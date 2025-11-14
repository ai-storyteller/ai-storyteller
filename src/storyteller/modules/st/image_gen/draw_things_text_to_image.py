import base64
import os
import pathlib
import requests
from uuid import uuid4
from pathlib import Path
import urllib.parse

# Assuming this is the correct import path from your project structure
from storyteller.modules.st.option_choices import artistic_styles
from storyteller.settings import (
    OUTPUT_ROOT,
    MEDIA_ROOT,
    MEDIA_URL_BASE,
    DRAW_THINGS_API_ROOT as SERVER_URL,
)
__all__ = ("generate_draw_things_text_to_image",)

# --- Configuration for the local DrawThings API ---
# The base URL for the DrawThings API server.
# SERVER_URL = os.getenv(
#     "STORYTELLER_DRAW_THINGS_API_ROOT", "http://localhost:7860"
# )
# The local folder where generated images will be saved.
# OUTPUT_ROOT = os.getenv("STORYTELLER_OUTPUT_PATH", "./drawthings_output")
# OUTPUT_FOLDER = "/Users/me/repos/storyteller-dev/output"


def generate_draw_things_text_to_image(
    prompt: str,
    prompt_prefix: str | None = None,
    prompt_suffix: str | None = None,
    artistic_style: str | None = None,
    guidance_scale: float = 5.5,
    num_inference_steps: int = 16,
    width: int = 1024,
    height: int = 1024,
    negative_prompt: str = "ugly, bad anatomy, deformed, disfigured, poorly drawn face, poorly drawn eyes, extra arms, extra legs, mutated hands, malformed limbs, missing limb, blurry, low resolution, error, cropped, worst quality, low quality, jpeg artifacts, signature, watermark, username, artist name, border, frame, extra limbs, distorted",
    seed: int = 1_000_000,
    output_dir: str | Path | None = None,
) -> tuple[str, str, bool]:
    """
    Generate an image using a local DrawThings API instance.

    This function constructs a prompt, sends it to the local API,
    saves the resulting image to a local folder, and returns the file path.

    :param prompt: The base prompt for image generation.
    :param prompt_prefix: Optional prefix for prompt.
    :param prompt_suffix: Optional suffix for prompt.
    :param artistic_style: The artistic style to apply to the prompt.
    :param guidance_scale: How closely the model should follow the prompt (cfg_scale).
    :param num_inference_steps: The number of steps for the diffusion process.
    :param width: The width of the generated image.
    :param height: The height of the generated image.
    :param negative_prompt: The negative prompt to guide the model away from certain features.
    :param seed: The seed for reproducibility. -1 means random.
    :param output_dir: The output directory to save the generated image.
    :return: A tuple containing the image file path (or error message),
             the final prompt used, and a boolean indicating success.
    """
    # 1. Construct the final prompt with the specified artistic style
    artistic_style_prompt = artistic_styles.get(artistic_style, None)
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

    # Resolve media config
    media_root = MEDIA_ROOT
    media_url_base = MEDIA_URL_BASE
    # media_url_base = os.getenv(
    #     "STORYTELLER_MEDIA_URL", "/media/"
    # )  # can be "/media/" or "https://host/media/"
    # if not media_url_base.endswith("/"):
    #     media_url_base += "/"

    # 2. Prepare the API request payload
    endpoint = f"{SERVER_URL.rstrip('/')}/sdapi/v1/txt2img"
    payload = {
        "prompt": final_prompt,
        "negative_prompt": negative_prompt,
        "width": width,
        "height": height,
        "seed": seed,
        "steps": num_inference_steps,  # Standard A1111/DrawThings API uses 'steps'
        "cfg_scale": guidance_scale,  # Standard A1111/DrawThings API uses 'cfg_scale'
    }

    try:
        # 3. Send the request to the DrawThings API
        print("Sending request to local DrawThings API...")
        response = requests.post(endpoint, json=payload, timeout=300)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        data = response.json()
        images_b64 = data.get("images", [])

        if not images_b64:
            return "Error: DrawThings API returned no images", final_prompt, False

        # 4. Decode the base64 image data and save it to a file
        img_data = base64.b64decode(images_b64[0])

        filename_prefix: str = ("sdxl",)

        # Ensure the output directory exists
        pathlib.Path(media_root).mkdir(parents=True, exist_ok=True)

        # Create a unique filename and save the image
        fname = f"drawthings_{uuid4()}.png"
        file_path = media_root / fname
        file_path.write_bytes(img_data)
        print(f"Image successfully saved to {file_path}")

        image_url = urllib.parse.urljoin(media_url_base, fname)
        # 5. Return the local file path as the 'URL'
        return image_url, final_prompt, True

    except requests.exceptions.ConnectionError as e:
        error_message = f"Connection Error: Could not connect to DrawThings API at {SERVER_URL}. Is it running?"
        print(error_message)
        return error_message, final_prompt, False
    except requests.exceptions.RequestException as e:
        error_message = f"API Request Error: {e}"
        print(error_message)
        return error_message, final_prompt, False
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        print(error_message)
        return error_message, final_prompt, False
