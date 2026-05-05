# /// script
# [tool.marimo.runtime]
# auto_instantiate = false
# ///

import marimo

app = marimo.App(width="medium")


@app.cell
def _std_imports():
    import json
    import logging
    import os
    import random
    from copy import copy, deepcopy
    from functools import partial
    from pathlib import Path
    from typing import Any

    return (
        Any,
        Path,
        copy,
        deepcopy,
        json,
        logging,
        os,
        random,
        partial,
    )


@app.cell
def _third_party_imports():
    import marimo as mo
    import pandas as pd

    return (
        mo,
        pd,
    )


@app.cell
def _app_imports():
    from storyteller.modules.common.data_export import (
        clear_directory,
        create_zip,
    )
    from storyteller.modules.common.media import as_url
    from storyteller.modules.common.storage import (
        get_input_root_dir,
        get_output_root_dir,
        get_storage_client,
    )
    from storyteller.modules.st.content import (
        create_timestamp_directory,
        docx_to_pdf,
        download_images,
    )
    from storyteller.modules.st.content_docx import create_docx
    from storyteller.modules.st.enums import ImageGeneratorEnum
    from storyteller.modules.st.image_gen_calls import (
        generate_image,
    )

    # This is a new, hypothetical function that would need to be created.
    # It takes a story and extracts image prompts from it.
    from storyteller.modules.st.llm_calls import (
        extract_characters_from_story,
        extract_prompts_from_story,
        generate_existing_story_parts,
    )
    from storyteller.modules.st.option_choices import (
        artistic_styles,
    )

    return (
        ImageGeneratorEnum,
        artistic_styles,
        as_url,
        clear_directory,
        create_docx,
        create_timestamp_directory,
        create_zip,
        docx_to_pdf,
        download_images,
        extract_characters_from_story,
        extract_prompts_from_story,
        generate_existing_story_parts,
        generate_image,
        get_input_root_dir,
        get_output_root_dir,
        get_storage_client,
    )


@app.cell
def _app_title(mo):
    mo.md("""# Story Illustrator""")
    return


# -----------------------------------------------------------------------------
# Auth
# -----------------------------------------------------------------------------


@app.cell(hide_code=True)
def _add_request(mo):
    request = mo.app_meta().request
    return (request,)


@app.cell(hide_code=True)
def _check_session(mo, request):
    """Check session."""
    if request and request.user and request.user["is_authenticated"]:
        user_block = mo.vstack(
            [
                mo.md(f"Welcome {request.user['username']}!"),
            ]
        )
        is_authenticated = True
        user_email = request.user["email"]
        url_path = request.meta["url_path"]
    else:
        user_block = mo.md("Please [log in](/login)")
        is_authenticated = False
        user_email = None
        url_path = "unauthenticated"

    return (
        user_block,
        is_authenticated,
        user_email,
        url_path,
    )


# -----------------------------------------------------------------------------
# Definitions, functions and classes
# -----------------------------------------------------------------------------


@app.cell(hide_code=True)
def _logger(logging):
    logger = logging.getLogger(__name__)
    return (logger,)


@app.cell(hide_code=True)
def _storage_credentials(get_storage_client):
    input_storage_client = get_storage_client()
    output_storage_client = get_storage_client()
    return (
        input_storage_client,
        output_storage_client,
    )


@app.cell(hide_code=True)
def _paths(
    get_input_root_dir,
    get_output_root_dir,
    input_storage_client,
    output_storage_client,
):
    input_root_dir = get_input_root_dir(input_storage_client)
    output_root_dir = get_output_root_dir(output_storage_client)
    return (
        input_root_dir,
        output_root_dir,
    )


@app.cell(hide_code=True)
def _definitions(
    os,
    user_email,
    url_path,
    input_root_dir,
    output_root_dir,
    is_authenticated,
):
    input_dir_name = input_root_dir / "input" / url_path
    if not input_dir_name.exists():
        input_dir_name.mkdir(parents=True, exist_ok=True)
    _input_keep_file = input_dir_name / ".keep"
    if not _input_keep_file.exists():
        _input_keep_file.touch()

    if is_authenticated:
        output_dir_name = output_root_dir / "output" / user_email / url_path
        if not output_dir_name.exists():
            output_dir_name.mkdir(parents=True, exist_ok=True)
        _output_keep_file = output_dir_name / ".keep"
        if not _output_keep_file.exists():
            _output_keep_file.touch()
    else:
        output_dir_name = output_root_dir / "output" / "unauthenticated" / url_path
        if not output_dir_name.exists():
            output_dir_name.mkdir(parents=True, exist_ok=True)
        _output_keep_file = output_dir_name / ".keep"
        if not _output_keep_file.exists():
            _output_keep_file.touch()

    debug = os.environ.get("DEBUG", False)
    model_name = os.environ.get("MODEL_NAME", None)

    return (
        input_dir_name,
        output_dir_name,
        debug,
        model_name,
    )


# -----------------------------------------------------------------------------
# Download all data
# -----------------------------------------------------------------------------


@app.cell
def _download_all_data_button(
    create_zip,
    mo,
    output_dir_name,
    partial,
):
    create_zip_partial = partial(create_zip, output_dir_name=output_dir_name)

    download_data_button = mo.download(
        data=create_zip_partial,
        filename=f"{output_dir_name.name}.zip",
        label="Download all data",
    )

    return (download_data_button,)


# -----------------------------------------------------------------------------
# Delete all data
# -----------------------------------------------------------------------------


@app.cell(hide_code=True)
def _delete_all_data_button(mo):
    delete_data_button = mo.ui.run_button(
        label=f"{mo.icon('lucide:trash-2')} Delete all data",
    )

    return (delete_data_button,)


@app.cell
def _delete_all_data_action(
    delete_data_button,
    clear_directory,
    mo,
    output_dir_name,
):
    if delete_data_button.value:
        clear_directory(dir_name=output_dir_name)


# -----------------------------------------------------------------------------
# Step 1: Story and Style
# -----------------------------------------------------------------------------


@app.cell
def _story_and_style_inputs(
    mo,
    artistic_styles,
    ImageGeneratorEnum,  # noqa
):
    # Text area for the user to input their full story
    story_title_input = mo.ui.text(
        value="Squeaky - adventures of a lousy squirrel",
        label="Your Story Title",
        full_width=True,
    )
    story_text_input = mo.ui.text_area(
        value=(
            # "Part 1: Squeaky’s Big Idea\n"
            "One bright morning, Squeaky the Squirrel woke up with a sparkle in his eyes."  # noqa
            "“I’m going to find the Golden Acorn!” he said, puffing up his tiny chest."  # noqa
            "Everyone in the forest whispered about the acorn that could grant one wish — just one!"  # noqa
            "Squeaky didn’t know what he’d wish for yet, but he knew it had to be something special. \n\n"  # noqa
            # "Part 2: Dorothy and the Map of Stars\n"
            "As Squeaky hopped down the path, a soft voice purred, “Going somewhere shiny, little nut chaser?”"  # noqa
            "It was Dorothy the Cat, her fur glowing like moonlight. She stretched lazily and smiled."  # noqa
            "Squeaky told her about his plan. Dorothy blinked and said, “Then you’ll need the Map of Stars. Only the owl keeps it.”"  # noqa
            "They set off together, their paws crunching leaves that smelled like cinnamon. \n\n"  # noqa
            # "Part 3: Ella and the Windy Hill\n"
            "At the top of the Windy Hill, they met Ella the Mouse, who was building a nest inside a teacup."  # noqa
            "“The owl flew that way!” Ella squeaked, pointing with her tail. “But be careful — the wind plays tricks!”"  # noqa
            "And oh, it did! It whooshed their hats away, flipped leaves, and giggled in the trees."  # noqa
            "But Ella was clever — she tied their tails together with a ribbon so no one would blow away. \n\n"  # noqa
            # "Part 4: Edward and the Golden Wish\n"
            "By the river, Edward the Duckling waddled up, his feathers still fluffy and soft."  # noqa
            "“I saw a glow at the tallest tree!” he quacked. “Maybe it’s your acorn!”"  # noqa
            "They hurried there — climbing, hopping, flapping — until Squeaky reached the very top."  # noqa
            "The Golden Acorn shimmered like sunrise."
            "Squeaky held it close and whispered, “I wish… for us all to stay friends forever.”"  # noqa
            "And the forest glowed back, as if it smiled too. \n\n"
        ),
        label="Your Story",
        full_width=True,
        rows=10,
    )

    # Dropdown for selecting the artistic style
    _artistic_style_options = list(artistic_styles.keys())
    artistic_style = mo.ui.dropdown(
        label="Artistic Style (Theme)",
        options=_artistic_style_options,
        value=None,
        allow_select_none=True,
    )

    # Dropdown for selecting the image generator
    _image_generator_options = [_o.value for _o in ImageGeneratorEnum]
    image_generator = mo.ui.dropdown(
        label="Image Generator",
        options=_image_generator_options,
        value=_image_generator_options[0],
    )

    # Button to start the illustration process
    generate_prompts_button = mo.ui.run_button(label="Generate Illustration Prompts")

    return (
        story_title_input,
        story_text_input,
        artistic_style,
        image_generator,
        generate_prompts_button,
    )


# -----------------------------------------------------------------------------
# Step 2: Generate Illustrations
# -----------------------------------------------------------------------------


@app.cell
def _extract_image_prompts(
    mo,
    generate_prompts_button,
    story_title_input,
    story_text_input,
    artistic_style,
    extract_prompts_from_story,
    extract_characters_from_story,
    generate_existing_story_parts,
    deepcopy,
    logger,
):
    if generate_prompts_button.value:
        with mo.status.progress_bar(
            total=1,
            remove_on_exit=True,
            title="Analyzing story and creating prompts",
        ) as _progress_bar:
            characters = extract_characters_from_story(
                story_text=story_text_input.value,
                progress_bar=_progress_bar,
            )
            story_output = generate_existing_story_parts(
                story_title=story_title_input.value,
                story_text=story_text_input.value,
                characters=characters.characters,
                artistic_style=artistic_style.value,
                progress_bar=_progress_bar,
            )
            logger.info("Extracted prompts from story.")

            # Prepare prompts for the next step
            sd_prompts = deepcopy(story_output.key_sd_prompts)
            sd_prompts.append(story_output.cover_image_sd_prompt)
            sd_prompts.append(story_output.back_cover_image_sd_prompt)
            story_json = mo.json(story_output.model_dump_json())
    else:
        story_output = None
        story_json = mo.md("")
        sd_prompts = []

    return (
        story_output,
        story_json,
        sd_prompts,
    )


@app.cell
def _create_images_button_and_prompts_display(mo, sd_prompts):
    create_images_button = mo.ui.run_button(label="Create Images")

    prompts_display = (
        mo.vstack([mo.md("### Generated Image Prompts"), mo.json(sd_prompts)])
        if sd_prompts
        else mo.md("")
    )

    return create_images_button, prompts_display


@app.cell
def _generate_images(
    mo,
    story_output,
    generate_image,
    create_images_button,
    image_generator,
    artistic_style,
    logger,
):
    image_urls = []
    mo_image_urls = []
    cover_image_url = None
    back_cover_image_url = None

    if create_images_button.value and story_output:
        all_prompts = story_output.key_sd_prompts + [
            story_output.cover_image_sd_prompt,
            story_output.back_cover_image_sd_prompt,
        ]
        with mo.status.progress_bar(
            total=len(all_prompts),
            remove_on_exit=True,
            title="Generating images",
        ) as _progress_bar:
            # Cover image
            _progress_bar.update(subtitle="Generating cover image")
            cover_image_url, _prompt, _success = generate_image(
                prompt=story_output.cover_image_sd_prompt,
                generator=image_generator.value,
                artistic_style=artistic_style.value,
            )
            if _success:
                mo_image_urls.append(
                    mo.image(src=cover_image_url, width=400, caption=f"Cover: {_prompt}")
                )
            else:
                logger.warning(f"Failed to generate cover image for {_prompt}")

            # Back cover image
            _progress_bar.update(subtitle="Generating back cover image")
            back_cover_image_url, _prompt, _success = generate_image(
                prompt=story_output.back_cover_image_sd_prompt,
                generator=image_generator.value,
                artistic_style=artistic_style.value,
            )
            if _success:
                mo_image_urls.append(
                    mo.image(
                        src=back_cover_image_url,
                        width=400,
                        caption=f"Back Cover: {_prompt}",
                    )
                )
            else:
                logger.warning(f"Failed to generate back cover image for {_prompt}")

            # Story images
            for sd_prompt in story_output.key_sd_prompts:
                _progress_bar.update(subtitle="Generating story images")
                _image_url, _prompt, _success = generate_image(
                    prompt=sd_prompt,
                    generator=image_generator.value,
                    artistic_style=artistic_style.value,
                )
                if _success:
                    image_urls.append(_image_url)
                    mo_image_urls.append(
                        mo.image(src=_image_url, width=300, caption=_prompt)
                    )
                else:
                    logger.warning(
                        f"Failed to generate image for {_prompt}: {_image_url}"
                    )

    return (
        mo_image_urls,
        cover_image_url,
        back_cover_image_url,
        image_urls,
    )


# -----------------------------------------------------------------------------
# Tabbed interface
# -----------------------------------------------------------------------------


@app.cell
def _tabs(
    mo,
    json,
    Path,  # noqa
    logger,
    output_dir_name,
    # Step 1 inputs
    story_title_input,
    story_text_input,
    artistic_style,
    image_generator,
    generate_prompts_button,
    # Step 2 inputs & outputs
    story_output,
    story_json,
    prompts_display,
    create_images_button,
    mo_image_urls,
    cover_image_url,
    back_cover_image_url,
    image_urls,
    # PDF creation functions
    create_timestamp_directory,
    download_images,
    create_docx,
    docx_to_pdf,
    as_url,
):
    # This block runs when images are generated to prepare files
    if create_images_button.value and story_output and image_urls:
        output_dir = create_timestamp_directory(output_dir_name)
        # Download all generated images
        download_images(image_urls, output_dir)
        if cover_image_url:
            download_images([cover_image_url], output_dir, suffix="cover")
        if back_cover_image_url:
            download_images([back_cover_image_url], output_dir, suffix="back_cover")

        # Prepare paths and save JSON data
        story_json_path = Path(output_dir) / "story.json"
        story_json_path.write_text(story_output.model_dump_json(indent=4))
        cover_image_json_path = Path(output_dir) / "cover_image.json"
        back_cover_image_json_path = Path(output_dir) / "back_cover_image.json"
        images_json_path = Path(output_dir) / "images.json"
        if image_urls:
            images_json_path.write_text(json.dumps(image_urls, indent=4))
        if cover_image_url:
            cover_image_json_path.write_text(json.dumps(cover_image_url, indent=4))
        if back_cover_image_url:
            back_cover_image_json_path.write_text(
                json.dumps(back_cover_image_url, indent=4)
            )

        docx_path = Path(output_dir) / "story.docx"
        pdf_path = Path(output_dir) / "story.pdf"

        with mo.status.progress_bar(
            total=2, remove_on_exit=True, title="Assembling the final story PDF"
        ) as _progress_bar:
            _progress_bar.update(subtitle="Creating DOCX")
            create_docx(
                title=story_title_input.value,
                text=story_text_input.value,
                cover_image_url=cover_image_url,
                back_cover_image_url=back_cover_image_url,
                images=image_urls,
                output_path=str(docx_path),
            )
            _progress_bar.update(subtitle="Creating PDF")
            docx_to_pdf(docx_path=docx_path, pdf_path=pdf_path)
            docx_url = as_url(
                docx_path,
            )
        pdf_viewer = mo.vstack(
            [
                mo.md("### Generated PDF"),
                mo.pdf(pdf_path, width="100%", height="60vh")
                if pdf_path.exists()
                else mo.md(""),  # PDF generation failed or not yet generated
            ]
        )
        docx_viewer = mo.vstack(
            [
                mo.md("### Generated DOCX"),
                mo.md(f"""
                **Download the DOCX file:** [Download link]({docx_url})
                """)
                if docx_url
                else mo.md(""),
            ]
        )
    else:
        pdf_viewer = mo.md("Complete the steps above to generate a PDF.")
        docx_viewer = mo.md("")

    tabs = mo.ui.tabs(
        {
            "Step 1: Story & Style": mo.vstack(
                [
                    story_title_input,
                    story_text_input,
                    artistic_style,
                    image_generator,
                    generate_prompts_button,
                    story_json,  # Shows the output from the LLM prompt extraction
                ]
            ),
            "Step 2: Illustrations": mo.vstack(
                [
                    prompts_display,
                    create_images_button,
                    mo.vstack(mo_image_urls),
                ]
            ),
            "Step 3: Documents": mo.vstack(
                [
                    pdf_viewer,
                    docx_viewer,
                ],
                justify="center",
            ),
        },
    )
    tabs  # noqa
    return


if __name__ == "__main__":
    app.run()
