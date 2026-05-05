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
        markdown_with_images,
    )
    from storyteller.modules.st.content_docx import create_docx
    from storyteller.modules.st.enums import ImageGeneratorEnum
    from storyteller.modules.st.files import get_filename_and_bytes
    from storyteller.modules.st.image_gen_calls import (
        generate_image,
    )
    from storyteller.modules.st.llm_calls import (
        describe_image,
        generate_story,
        load_characters,
    )
    from storyteller.modules.st.option_choices import (
        artistic_styles,
        eye_color_choices,
        hair_color_choices,
        identity_choices,
        reading_level_choices,
        skin_color_choices,
    )

    return (
        ImageGeneratorEnum,
        artistic_styles,
        as_url,
        clear_directory,
        create_docx,
        create_timestamp_directory,
        create_zip,
        describe_image,
        docx_to_pdf,
        download_images,
        eye_color_choices,
        generate_image,
        generate_story,
        get_filename_and_bytes,
        get_input_root_dir,
        get_output_root_dir,
        get_storage_client,
        hair_color_choices,
        identity_choices,
        load_characters,
        markdown_with_images,
        reading_level_choices,
        skin_color_choices,
    )


@app.cell
def _app_title(mo):
    mo.md("""# Storyteller""")
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
    # Now you can access the session from the request
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
# State
# -----------------------------------------------------------------------------


@app.cell
def _state(mo):
    get_characters, set_characters = mo.state(dict())
    return get_characters, set_characters


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
        output_dir_name = output_root_dir / user_email / url_path
        if not output_dir_name.exists():
            output_dir_name.mkdir(parents=True, exist_ok=True)
        _output_keep_file = output_dir_name / ".keep"
        if not _output_keep_file.exists():
            _output_keep_file.touch()

        _input_keep_file = input_dir_name / ".keep"
        if not _input_keep_file.exists():
            _input_keep_file.touch()
    else:
        output_dir_name = output_root_dir / "unauthenticated" / url_path
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
# File upload
# -----------------------------------------------------------------------------


@app.cell
def _character_file_upload_element(mo, output_dir_name):
    filetypes = [
        ".png",
        ".jpg",
        ".jpeg",
    ]

    # Create the data directory if it doesn't exist
    output_dir_name.mkdir(parents=True, exist_ok=True)

    character_file_uploads = mo.ui.file(filetypes=filetypes, multiple=False)
    return (character_file_uploads,)


# -----------------------------------------------------------------------------
# Step 1: Characters
# -----------------------------------------------------------------------------


@app.cell
def _add_character_form(
    mo,
    eye_color_choices,
    hair_color_choices,
    skin_color_choices,
    identity_choices,
    character_file_uploads,
    get_filename_and_bytes,
    logger,
):
    logger.info(type(character_file_uploads))
    logger.info(character_file_uploads)
    filename, file_content = get_filename_and_bytes(character_file_uploads)
    logger.info(f"filename: {filename}")
    logger.info(f"file_content: {file_content}")
    # Create UI elements for character input
    _character_layout = mo.md(
        """
        Name: {name}
        Age: {age}

        Eye color: {eye_color}
        Hair color: {hair_color}
        Skin color: {skin_color}

        Length: {length}
        Identity: {identity}

        Favourite animal: {favourite_animal}

        Image: {image}

        Interests: {interests}
        """
    )
    character_info = mo.ui.batch(
        _character_layout,
        {
            "name": mo.ui.text(value="Luna"),
            "interests": mo.ui.text_area(value="Adventures"),
            "favourite_animal": mo.ui.text(value="Cat"),
            "age": mo.ui.number(value=9),
            "eye_color": mo.ui.dropdown(options=eye_color_choices, value="green"),
            "hair_color": mo.ui.dropdown(options=hair_color_choices, value="brown"),
            "skin_color": mo.ui.dropdown(options=skin_color_choices, value="light"),
            "length": mo.ui.number(value=150),
            "identity": mo.ui.dropdown(options=identity_choices, value="girl"),
            "image": character_file_uploads,
        },
    )

    # Button to add character
    add_character_button = mo.ui.run_button(label="Add Character")

    # Display UI elements in a vertical stack
    character_info_container = mo.vstack(
        [
            character_info,
            add_character_button,
        ]
    )
    return character_info_container


@app.cell
def _add_character_action(
    Any,  # noqa
    get_characters,
    set_characters,
    add_character_button,
    character_info,
):
    # Function to add a character to the list
    def add_character(char_info: dict[str, Any]) -> None:
        _characters = get_characters()
        name = char_info.get("name")
        if name not in _characters:
            _characters[name] = char_info
        set_characters(_characters)

    # Add character when button is clicked
    if add_character_button.value:
        add_character(character_info.value)
    return


@app.cell
def _characters_table(mo, pd, get_characters):
    # Display the list of characters in a table
    _characters = get_characters()
    if _characters:
        _characters_df = pd.DataFrame.from_dict(_characters, orient="index")
        characters_table = mo.ui.table(_characters_df)
    else:
        characters_table = mo.md("")

    # characters_table  # noqa
    return characters_table


# -----------------------------------------------------------------------------
# Step 2: Story
# -----------------------------------------------------------------------------


@app.cell
def _story_prompt(mo):
    # Create a text area for the general story prompt
    story_prompt = mo.ui.text_area(
        # value="""Craft a whimsical fantasy story set in an enchanted, glowing forest where ancient secrets are whispered by the wind and animals possess unique magical abilities. The characters discover a hidden map leading to a legendary artifact.
        # """,  # noqa
        value="""Write a 500-700 word children's story about [CHARACTERS]. Start with them waking up/discovering something absurdly wrong (be creative—no flying cows). The problem escalates fast: their first fix backfires, making things worse, then worse again. Include snappy dialogue (40% of the story), sound effects, and physical comedy. They solve it through teamwork, each using their unique trait. End upbeat with everyone laughing together.
TONE: Fast-paced and hilarious, not gentle. Open with action, not description.
        """,  # noqa
        label="Story Prompt",
        full_width=True,
    )
    return story_prompt


@app.cell
def _reading_level_selector(mo, reading_level_choices):
    _value = reading_level_choices[-1]
    reading_level_selector = mo.ui.dropdown(
        label="Reading Level",
        options=reading_level_choices,
        value=_value,
    )
    return reading_level_selector


@app.cell
def _create_story_button(mo):
    create_story_button = mo.ui.run_button(label="Create story")
    return create_story_button


@app.cell
def _generate_story(
    mo,
    create_story_button,
    story_prompt,
    get_characters,
    load_characters,
    generate_story,
    artistic_style,
    deepcopy,
    logger,
    reading_level_selector,
):
    if create_story_button.value:
        _characters = get_characters()
        with mo.status.progress_bar(
            total=len(_characters),
            remove_on_exit=True,
            title="Generating story",
        ) as _progress_bar:
            logger.info(f"Characters: {_characters}")
            characters = load_characters(
                data=list(_characters.values()),
                progress_bar=_progress_bar,
            )
            logger.info("characters")
            logger.info(characters)
            base_prompt = story_prompt.value

        with mo.status.progress_bar(
            total=1,
            remove_on_exit=True,
            title="Generating story",
        ) as _progress_bar:
            story_output = generate_story(
                base_prompt,
                characters,
                artistic_style=artistic_style.value,
                progress_bar=_progress_bar,
                reading_level=reading_level_selector.value,
            )

            # Display the generated stories
            generated_story = mo.ui.text_area(
                value=story_output.story,
                label="Generated story",
            )
            sd_prompts = deepcopy(story_output.key_sd_prompts)
            sd_prompts.append(story_output.cover_image_sd_prompt)
            sd_prompts.append(story_output.back_cover_image_sd_prompt)
            story_json = mo.json(story_output.model_dump_json())
    else:
        generated_story = mo.md("")
        story_output = None
        story_json = mo.md("")
        sd_prompts = []

    return (
        generated_story,
        story_output,
        story_json,
        sd_prompts,
    )


# -----------------------------------------------------------------------------
# Step 3: Images generation
# -----------------------------------------------------------------------------


@app.cell
def _image_generator_options_and_create_images_button(
    mo,
    artistic_styles,
    ImageGeneratorEnum,  # noqa
):
    _image_generator_options = [_o.value for _o in ImageGeneratorEnum]
    _image_generator_value = _image_generator_options[0]
    image_generator = mo.ui.dropdown(
        label="Image Generator",
        options=_image_generator_options,
        value=_image_generator_value,
    )

    _artistic_style_options = list(artistic_styles.keys())
    _artistic_style_value = None
    artistic_style = mo.ui.dropdown(
        label="Artistic Style",
        options=_artistic_style_options,
        value=_artistic_style_value,
        allow_select_none=True,
    )
    create_images_button = mo.ui.run_button(label="Create images")

    return (
        create_images_button,
        image_generator,
        artistic_style,
    )


@app.cell
def _generate_images(
    mo,
    story_output,
    generate_image,
    create_images_button,
    sd_prompts,
    image_generator,
    artistic_style,
    logger,
):
    image_urls = []
    mo_image_urls = []
    cover_image_url = None
    back_cover_image_url = None

    if create_images_button.value and story_output:
        with mo.status.progress_bar(
            total=len(sd_prompts),
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
                # image_urls.append(_image_url)
                mo_image_urls.append(
                    mo.image(
                        src=cover_image_url,
                        width=400,
                        caption=_prompt,
                    )
                )
            else:
                logger.warning(
                    f"Failed to generate image for {_prompt}: {cover_image_url}"
                )

            # Back cover image
            _progress_bar.update(subtitle="Generating back cover image")
            back_cover_image_url, _prompt, _success = generate_image(
                prompt=story_output.back_cover_image_sd_prompt,
                generator=image_generator.value,
                artistic_style=artistic_style.value,
            )

            if _success:
                # image_urls.append(_image_url)
                mo_image_urls.append(
                    mo.image(
                        src=back_cover_image_url,
                        width=400,
                        caption=_prompt,
                    )
                )
            else:
                logger.warning(
                    f"Failed to generate image for {_prompt}: {back_cover_image_url}"
                )

            # Other images
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
                        mo.image(
                            src=_image_url,
                            width=300,
                            caption=_prompt,
                        )
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
    character_info_container,
    characters_table,
    story_prompt,
    create_story_button,
    create_images_button,
    mo_image_urls,
    cover_image_url,
    back_cover_image_url,
    image_urls,
    story_json,
    story_output,
    download_images,
    create_timestamp_directory,
    create_docx,
    docx_to_pdf,
    Path,  # noqa
    image_generator,
    artistic_style,
    sd_prompts,
    logger,
    output_dir_name,
    as_url,
    reading_level_selector,
):
    output_dir = create_timestamp_directory(output_dir_name)
    # Download images
    if image_urls:
        download_images(image_urls, output_dir)
    if cover_image_url:
        download_images([cover_image_url], output_dir, suffix="cover")
    if back_cover_image_url:
        download_images([back_cover_image_url], output_dir, suffix="back_cover")
    # Prepare paths
    story_json_path = Path(output_dir) / "story.json"
    cover_image_json_path = Path(output_dir) / "cover_image.json"
    back_cover_image_json_path = Path(output_dir) / "back_cover_image.json"
    images_json_path = Path(output_dir) / "images.json"
    docx_path = Path(output_dir) / "story.docx"
    pdf_path = Path(output_dir) / "story.pdf"
    if story_output and story_output.story:
        story_json_path.write_text(story_output.model_dump_json(indent=4))
    if image_urls:
        images_json_path.write_text(json.dumps(image_urls, indent=4))
    if cover_image_url:
        cover_image_json_path.write_text(json.dumps(cover_image_url, indent=4))
    if back_cover_image_url:
        back_cover_image_json_path.write_text(json.dumps(back_cover_image_url, indent=4))

    with mo.status.progress_bar(
        total=2,
        remove_on_exit=True,
        title="Assembling the final story",
        subtitle="Creating DOCX",
    ) as _progress_bar:
        if story_output and story_output.story and image_urls:
            create_docx(
                title=story_output.title,
                text=story_output.story,
                cover_image_url=cover_image_url,
                back_cover_image_url=back_cover_image_url,
                images=image_urls,
                output_path=str(docx_path),
            )
            _progress_bar.update(subtitle="Creating PDF")
            docx_to_pdf(docx_path=docx_path, pdf_path=pdf_path)
            docx_url = as_url(docx_path)
        else:
            story_md = ""
            docx_url = ""

    logger.info(story_output)
    logger.info(image_urls)

    tabs = mo.ui.tabs(
        {
            "Step 1. Characters": mo.vstack(
                [
                    character_info_container,
                    characters_table,
                ]
            ),
            "Step 2. Story": mo.vstack(
                [
                    story_prompt,
                    reading_level_selector,
                    artistic_style,
                    create_story_button,
                    story_json,
                ]
            ),
            "Step 3. Images": mo.vstack(
                [
                    mo.json(sd_prompts),
                    image_generator,
                    create_images_button,
                    mo.vstack(mo_image_urls),
                ]
            ),
            "Step 4. Documents": mo.vstack(
                [
                    mo.md("### Generated PDF"),
                    mo.pdf(pdf_path, width="600px", height="50vh")
                    if pdf_path.exists()
                    else mo.md(""),
                    mo.md("### Generated DOCX"),
                    mo.md(f"""
                    **Download the DOCX file:** [Download link]({docx_url})
                    """)
                    if docx_url
                    else mo.md(""),
                ]
            ),
        },
    )
    tabs  # noqa


if __name__ == "__main__":
    app.run()
