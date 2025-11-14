from enum import Enum

__all__ = ("ImageGeneratorEnum",)


class ImageGeneratorEnum(str, Enum):
    FAL_TEXT_TO_IMAGE = "FAL text to image"
    DRAW_THINGS_TEXT_TO_IMAGE = "DrawThings text to image"
    # DALL_E_3_TEXT_TO_IMAGE = "Dall-E 3 text to image"
    # GEMINI_TEXT_TO_IMAGE = "Gemini text to image"
    # FLUX_IMAGE_TO_IMAGE = "Flux image to image"
    # DALL_E_3_IMAGE_TO_IMAGE = "Dall-E 3 image to image"
    # GEMINI_IMAGE_TO_IMAGE = "Gemini image to image"
