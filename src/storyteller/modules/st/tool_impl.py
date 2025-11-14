# /// script
# requires-python = ">=3.12"
# ///

from __future__ import annotations

import json
import os
import logging
from pathlib import Path
from typing import Any, Optional

from storyteller.modules.common.storage import (
    get_storage_client,
    get_input_root_dir,
    get_output_root_dir,
)
from storyteller.modules.common.media import as_url
from storyteller.modules.st.enums import ImageGeneratorEnum
from storyteller.modules.st.llm_calls import (
    generate_story_from_basic_prompt,
)
from storyteller.modules.st.image_gen_calls import generate_image
from storyteller.modules.st.content import (
    create_timestamp_directory,
    download_images,
    docx_to_pdf,
)
from storyteller.modules.st.content_docx import create_docx
from storyteller.modules.st.option_choices import artistic_styles, reading_level_choices
from storyteller.settings import (
    OUTPUT_ROOT,
    MEDIA_ROOT,
    MEDIA_URL_BASE,
    OUTPUT_MEDIA_URL_BASE,
)

logger = logging.getLogger(__name__)


def _safe_image_generator(image_generator: Optional[str]) -> str:
    """Pick a valid ImageGeneratorEnum.value."""
    valid_values = [_o.value for _o in ImageGeneratorEnum]

    if not image_generator:
        return valid_values[0]

    for valid_value in valid_values:
        if image_generator in valid_value:
            return valid_value
    return valid_values[0]


def _infer_reading_level_hint(
    story_request: str,
    explicit_reading_level: Optional[str],
) -> str:
    """
    Try to pick an appropriate reading_level from reading_level_choices.

    Priority:
    1. explicit_reading_level if caller passed it and we can match.
    2. Heuristics from the request text (e.g. mentions '6 year old', 'toddler', 'young adult').
    3. Fallback: last element from reading_level_choices (usually simplest).
    """
    # 1. Respect explicit hint if supplied
    if explicit_reading_level:
        for choice in reading_level_choices:
            if explicit_reading_level.lower() in choice.lower():
                return choice

    req_lower = story_request.lower()

    # 2. Heuristic for age cues
    #    We'll keep it intentionally dumb but predictable. You can refine later.
    #    We just scan digits and some keywords.
    if "toddler" in req_lower or "2 year" in req_lower or "3 year" in req_lower:
        # Assume youngest if we have it
        return reading_level_choices[0]

    if "4 year" in req_lower or "5 year" in req_lower or "6 year" in req_lower:
        # Aim for early reading levels
        for choice in reading_level_choices:
            if "4" in choice or "5" in choice or "6" in choice:
                return choice

    if "7 year" in req_lower or "8 year" in req_lower or "9 year" in req_lower:
        for choice in reading_level_choices:
            if "7" in choice or "8" in choice or "9" in choice:
                return choice

    if "teen" in req_lower or "young adult" in req_lower or "ya " in req_lower:
        for choice in reading_level_choices:
            if "teen" in choice.lower() or "young adult" in choice.lower():
                return choice

    # 3. Fallback
    return reading_level_choices[-1]


def _maybe_pick_art_style(
    story_request: str,
    explicit_style: Optional[str],
) -> Optional[str]:
    """
    Choose artistic_style key for illustrations.
    Priority:
    1. explicit_style if provided and valid.
    2. Try to match style mentioned in request against artistic_styles keys.
    3. None if no match -> downstream means 'natural default'.
    """
    if explicit_style and explicit_style in artistic_styles:
        return explicit_style

    req_lower = story_request.lower()

    # Check if any artistic_styles key is mentioned in the request
    for style_key in artistic_styles:
        # Direct key match (case-insensitive)
        if style_key.lower() in req_lower:
            return style_key

        # Handle common variations
        # Extract main style word(s) from the key for partial matching
        key_words = style_key.lower().replace("-", " ").split()
        for word in key_words:
            # Skip common words that might cause false positives
            if word in ['art', 'the', 'and', 'or', 'painting', 'photography', 'shot']:
                continue
            # Check if significant style word appears in request
            if len(word) > 4 and word in req_lower:
                return style_key

    # Specific fuzzy matches for common variations
    style_aliases = {
        "surreal": "Surrealism",
        "impressionist": "Impressionism",
        "cubist": "Cubism",
        "deco": "Art Deco",
        "nouveau": "Art Nouveau",
        "abstract": "Abstract Expressionism",
        "realistic": "Realism",
        "romantic": "Romanticism",
        "minimal": "Minimalism",
        "street": "Contemporary Street Art",
        "graffiti": "Contemporary Street Art",
        "escher": "M.C. Escher",
        "klimt": "Gustav Klimt",
        "magritte": "Rene Magritte",
        "waterhouse": "J.W. Waterhouse",
    }

    for alias, style_key in style_aliases.items():
        if alias in req_lower and style_key in artistic_styles:
            return style_key

    return None


def create_story_bundle_fn(
    story_request: str,
    story_title: Optional[str] = None,
    story_text: Optional[str] = None,
    # Optional knobs. The LLM can set these, but none are required.
    artistic_style_key: Optional[str] = None,
    reading_level: Optional[str] = None,
    image_generator: Optional[str] = None,
    user_email: Optional[str] = None,
    url_path: str = "api",
    image_prompt_prefix: Optional[str] = None,
    image_prompt_suffix: Optional[str] = None,
) -> dict[str, Any]:
    """
    High-level autonomous story pipeline:
    - Parse the user's request for characters, tone, style, etc.
    - Generate story text, SDXL-style prompts for each scene.
    - Generate images with the chosen generator.
    - Assemble PDFs via all methods.
    - Return links.

    Caller (LLM) MUST pass the following required parameters:
      - story_request: natural language. Example:
        "Create a cozy bedtime story about a brave little fish named Rody
         and a kind 9-year-old girl named Luna who rescues him from a stormy lake.
         Make it sweet, safe, and comforting. Use DrawThings. Reading level age 6."

    Caller (LLM) MAY pass the following optional parameters:
      - story_title: title of the story.
      - story_text: text of the story.
      - artistic_style_key: key from artistic_styles, if known. Optional.
      - reading_level: human-readable hint ("4-6 years", "young adult"). Optional.
      - image_generator: string backend ("DrawThings", etc.). Optional.
      - user_email: which user bucket to store outputs under.
      - url_path: subfolder bucket (similar to request.meta['url_path'] in marimo).
      - image_prompt_prefix: to be added at the beginning of image_prompts.
      - image_prompt_suffix: to be added at the end of image_prompts.

    Returns:
        Dict with story metadata, filesystem paths, and "public_urls" that can be
        given back to the user.

    Note:
        The tool itself decides who is the main character. We do NOT enforce
        protagonist naming, age, etc. We pass the entire `story_request`
        to the story planning LLM calls.
    """
    # ------------------------------------------------------------------
    # Resolve storage roots (like in marimo apps)
    # ------------------------------------------------------------------
    input_storage_client = get_storage_client()
    output_storage_client = get_storage_client()

    input_root_dir = get_input_root_dir(input_storage_client)
    output_root_dir = get_output_root_dir(output_storage_client)

    # Decide which user's output dir to use
    if user_email:
        base_output_dir = output_root_dir /  user_email / url_path
    else:
        base_output_dir = output_root_dir / "unauthenticated" / url_path

    base_output_dir.mkdir(parents=True, exist_ok=True)
    (base_output_dir / ".keep").touch(exist_ok=True)

    # Timestamped subdir for this run
    run_dir = Path(create_timestamp_directory(base_output_dir))
    run_dir.mkdir(parents=True, exist_ok=True)

    # Derive style + reading level hints from request text if not given
    inferred_artistic_style = _maybe_pick_art_style(story_request, artistic_style_key)
    final_artistic_style = inferred_artistic_style

    inferred_reading_level = _infer_reading_level_hint(
        story_request,
        explicit_reading_level=reading_level,
    )
    final_reading_level = inferred_reading_level

    # Now create structured story parts (LLM writes full story etc.)
    story_output = generate_story_from_basic_prompt(
        base_prompt=story_request,  # Raw request becomes seed material
        artistic_style=final_artistic_style,
        progress_bar=None,
        reading_level=final_reading_level,
    )

    # Persist raw JSON dump for debugging / traceability
    story_json_path = run_dir / "story.json"
    story_json_path.write_text(story_output.model_dump_json())

    # ------------------------------------------------------------------
    # 2. Generate images for cover, back cover, and story scenes.
    # ------------------------------------------------------------------
    gen_backend = _safe_image_generator(image_generator)

    cover_image_url = None
    back_cover_image_url = None
    story_image_urls: list[str] = []

    # Cover
    cover_image_url, _cover_prompt_used, cover_success = generate_image(
        prompt=story_output.cover_image_sd_prompt,
        generator=gen_backend,
        artistic_style=final_artistic_style,
    )
    if cover_success:
        (run_dir / "cover_image.json").write_text(json.dumps(cover_image_url))

    # Back cover
    back_cover_image_url, _back_prompt_used, back_success = generate_image(
        prompt=story_output.back_cover_image_sd_prompt,
        generator=gen_backend,
        artistic_style=final_artistic_style,
        prompt_prefix=image_prompt_prefix,
        prompt_suffix=image_prompt_suffix,
    )
    if back_success:
        (run_dir / "back_cover_image.json").write_text(json.dumps(back_cover_image_url))

    # Inner illustrations
    for sd_prompt in story_output.key_sd_prompts:
        _image_url, _prompt_used, _ok = generate_image(
            prompt=sd_prompt,
            generator=gen_backend,
            artistic_style=final_artistic_style,
        )
        if _ok:
            story_image_urls.append(_image_url)

    (run_dir / "images.json").write_text(json.dumps(story_image_urls))

    # ------------------------------------------------------------------
    # 3. Download all remote image URLs to local disk in run_dir
    # ------------------------------------------------------------------
    if story_image_urls:
        download_images(story_image_urls, run_dir)
    if cover_image_url:
        download_images([cover_image_url], run_dir, suffix="cover")
    if back_cover_image_url:
        download_images([back_cover_image_url], run_dir, suffix="back_cover")

    # ------------------------------------------------------------------
    # 4. Produce PDFs via all 3 methods (same flow as UI apps)
    # ------------------------------------------------------------------
    pdf_path = run_dir / "story.pdf"
    docx_path = run_dir / "story.docx"

    # Method 1
    create_docx(
        title=story_output.title,
        text=story_output.story,
        cover_image_url=cover_image_url,
        back_cover_image_url=back_cover_image_url,
        images=story_image_urls,
        output_path=str(docx_path),
    )
    logger.info(f"docx_path: {docx_path}")
    logger.info(f"pdf_path: {pdf_path}")
    # TODO: Fix errors here
    docx_to_pdf(docx_path=docx_path, pdf_path=pdf_path)

    # ------------------------------------------------------------------
    # 5. Prepare response (links)
    # ------------------------------------------------------------------

    result = {
        "title": story_output.title,
        "story_text": story_output.story,
        "output_dir": str(run_dir),
        "document_paths": {
            "docx": str(docx_path),
            "pdf": str(pdf_path),
        },
        "public_urls": {
            "docx": as_url(docx_path),
            "pdf": as_url(pdf_path),
        },
    }

    (run_dir / "result.json").write_text(json.dumps(result, indent=2))

    logger.info("Story bundle created at %s", run_dir)
    return result
