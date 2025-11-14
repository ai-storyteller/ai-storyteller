import logging
import os
from pathlib import Path

from dotenv import load_dotenv

__all__ = (
    "OUTPUT_ROOT",
    "MEDIA_ROOT",
    "MEDIA_URL_BASE",
    "OUTPUT_MEDIA_URL_BASE",
    "TOOL_MODEL_PROVIDER",
    "TOOL_MODEL_NAME",
    "DRAW_THINGS_API_ROOT",
    "FAL_TEXT_TO_IMAGE_MODEL_NAME",
    "IMAGE_DESCRIPTOR_MODEL_NAME",
    "STORY_MODEL_NAME",
    "STORAGE_INPUT_PATH",
    "STORAGE_OUTPUT_PATH",
    "STORAGE_SERVICE_ACCOUNT",
    "STORAGE_SERVICE_ACCOUNT_B64",
)

load_dotenv()

LOGGER = logging.getLogger(__name__)

# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------

# Output root
OUTPUT_ROOT = os.getenv("STORYTELLER_OUTPUT_PATH", "output")
LOGGER.info(f"OUTPUT_ROOT: {OUTPUT_ROOT}")

# Media root
MEDIA_ROOT = Path(os.getenv("STORYTELLER_MEDIA_PATH", "media")).resolve()
LOGGER.info(f"MEDIA_ROOT: {MEDIA_ROOT}")

# Media URL base
MEDIA_URL_BASE = os.getenv(
    "STORYTELLER_MEDIA_URL", "/media/"
)  # can be "/media/" or "https://host/media/"
if not MEDIA_URL_BASE.endswith("/"):
    MEDIA_URL_BASE += "/"
LOGGER.info(f"MEDIA_URL_BASE: {MEDIA_URL_BASE}")

# Output media URL base
OUTPUT_MEDIA_URL_BASE = os.getenv(
    "STORYTELLER_OUTPUT_MEDIA_URL", "/media/output/"
)  # can be "/media/" or "https://host/media/"
if not OUTPUT_MEDIA_URL_BASE.endswith("/"):
    OUTPUT_MEDIA_URL_BASE += "/"
LOGGER.info(f"OUTPUT_MEDIA_URL_BASE: {OUTPUT_MEDIA_URL_BASE}")

# ----------------------------------------------------------------------------
# Storages
# ----------------------------------------------------------------------------

# Storage input path
STORAGE_INPUT_PATH = os.getenv("STORYTELLER_STORAGE_INPUT_PATH", "")
LOGGER.info(f"STORAGE_INPUT_PATH: {STORAGE_INPUT_PATH}")

# Storage output path
STORAGE_OUTPUT_PATH = os.getenv("STORYTELLER_STORAGE_OUTPUT_PATH", "")
LOGGER.info(f"STORAGE_OUTPUT_PATH: {STORAGE_OUTPUT_PATH}")

STORAGE_SERVICE_ACCOUNT = os.getenv("STORYTELLER_STORAGE_SERVICE_ACCOUNT")
LOGGER.info(f"STORAGE_SERVICE_ACCOUNT: {STORAGE_SERVICE_ACCOUNT}")

STORAGE_SERVICE_ACCOUNT_B64 = os.getenv("STORYTELLER_STORAGE_SERVICE_ACCOUNT_B64")
LOGGER.info(f"STORAGE_SERVICE_ACCOUNT_B64: {STORAGE_SERVICE_ACCOUNT_B64}")

# ----------------------------------------------------------------------------
# LLMs
# ----------------------------------------------------------------------------

# Tool model provider
TOOL_MODEL_PROVIDER = os.getenv("STORYTELLER_TOOL_MODEL_PROVIDER", "openai")
LOGGER.info(f"TOOL_MODEL_PROVIDER: {TOOL_MODEL_PROVIDER}")

# Tool model name
TOOL_MODEL_NAME = os.getenv("STORYTELLER_TOOL_MODEL_NAME", "gpt-5-mini")
LOGGER.info(f"TOOL_MODEL_NAME: {TOOL_MODEL_NAME}")

# Story model name
STORY_MODEL_NAME = os.getenv("STORYTELLER_STORY_MODEL_NAME", "o4-mini")
LOGGER.info(f"STORY_MODEL_NAME: {STORY_MODEL_NAME}")

# Image descriptor model name
IMAGE_DESCRIPTOR_MODEL_NAME = os.getenv(
    "STORYTELLER_IMAGE_DESCRIPTOR_MODEL_NAME", "gpt-4.1-mini"
)
LOGGER.info(f"IMAGE_DESCRIPTOR_MODEL_NAME: {IMAGE_DESCRIPTOR_MODEL_NAME}")

# ----------------------------------------------------------------------------
# Integrations
# ----------------------------------------------------------------------------
# The base URL for the DrawThings API server.
DRAW_THINGS_API_ROOT = os.getenv(
    "STORYTELLER_DRAW_THINGS_API_ROOT", "http://localhost:7860"
)
LOGGER.info(f"DRAW_THINGS_API_ROOT: {DRAW_THINGS_API_ROOT}")

# FAL text-to-image model name
FAL_TEXT_TO_IMAGE_MODEL_NAME = os.getenv(
    "STORYTELLER_FAL_TEXT_TO_IMAGE_MODEL_NAME",
    "fal-ai/nano-banana",  # "fal-ai/flux-pro/v1.1-ultra"
)
LOGGER.info(f"FAL_TEXT_TO_IMAGE_MODEL_NAME: {FAL_TEXT_TO_IMAGE_MODEL_NAME}")
