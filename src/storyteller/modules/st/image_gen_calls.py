from storyteller.modules.st.enums import ImageGeneratorEnum
from storyteller.modules.st.helpers import get_enum_value
from storyteller.modules.st.image_gen.fal_text_to_image import (
    generate_fal_text_to_image,
)
from storyteller.modules.st.image_gen.draw_things_text_to_image import (
    generate_draw_things_text_to_image,
)

__all__ = ("generate_image",)


def generate_image(
    prompt: str,
    generator: ImageGeneratorEnum | str,
    artistic_style: str | None = None,
    file=None,  # type: ignore
    prompt_prefix: str | None = None,
    prompt_suffix: str | None = None,
) -> tuple[str, str, bool]:
    """Generate image from prompt.

    :param prompt: The prompt to generate image from.
    :param generator: The image generator to use.
    :param artistic_style: The artistic style to use.
    :param file: The file to use.
    :param prompt_prefix: The prefix to use.
    :param prompt_suffix: The suffix to use.
    :return: An image URL and boolean indicating if the image was generated
        on success. An error string and a boolean False on failure.
    """
    generator = get_enum_value(generator)

    try:
        if generator == ImageGeneratorEnum.FAL_TEXT_TO_IMAGE.value:
            return generate_fal_text_to_image(
                prompt,
                artistic_style=artistic_style,
                prompt_prefix=prompt_prefix,
                prompt_suffix=prompt_suffix,
            )
        elif generator == ImageGeneratorEnum.DRAW_THINGS_TEXT_TO_IMAGE.value:
            return generate_draw_things_text_to_image(
                prompt,
                artistic_style=artistic_style,
                prompt_prefix=prompt_prefix,
                prompt_suffix=prompt_suffix,
            )
    except Exception as err:
        return str(err), prompt, False

    return "", prompt, False
