import os

import fal_client

from storyteller.modules.st.option_choices import artistic_styles
from storyteller.settings import FAL_TEXT_TO_IMAGE_MODEL_NAME

__all__ = ("generate_fal_text_to_image",)


# STORYTELLER_FAL_TEXT_TO_IMAGE_MODEL_NAME = os.getenv(
#     "STORYTELLER_FAL_TEXT_TO_IMAGE_MODEL_NAME",
#     "fal-ai/nano-banana",  # "fal-ai/flux-pro/v1.1-ultra"
# )


def generate_fal_text_to_image(
    prompt: str,
    prompt_prefix: str | None = None,
    prompt_suffix: str | None = None,
    artistic_style: str | None = None,
    guidance_scale: float = 9.5,
    num_inference_steps: int = 40,
    text_to_image_model: str | None = FAL_TEXT_TO_IMAGE_MODEL_NAME,
) -> tuple[str, str, bool]:
    """Generate a FAL text image."""
    artistic_style_prompt = artistic_styles.get(artistic_style, None)
    if not text_to_image_model:
        text_to_image_model = FAL_TEXT_TO_IMAGE_MODEL_NAME

    if artistic_style_prompt:
        final_prompt = f"""{prompt}
        Create an image in the style of {artistic_style}: {artistic_style_prompt}
        """
    else:
        final_prompt = prompt

    if prompt_prefix:
        final_prompt = f"{prompt_prefix}{final_prompt}"
    if prompt_suffix:
        final_prompt = f"{final_prompt}{prompt_suffix}"

    def on_queue_update(update):
        if isinstance(update, fal_client.InProgress):
            for log in update.logs:
                print(log["message"])

    response = fal_client.subscribe(
        text_to_image_model,
        arguments={
            "prompt": final_prompt,
            "guidance_scale": guidance_scale,
            "num_inference_steps": num_inference_steps,
            "seed": 1_000_000,
        },
        with_logs=True,
        on_queue_update=on_queue_update,
    )

    if response:
        return response["images"][0]["url"], final_prompt, True
    else:
        return "Error generating image", final_prompt, False
