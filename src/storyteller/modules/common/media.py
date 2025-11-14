import logging
from pathlib import Path
from urllib.parse import quote

from storyteller.settings import OUTPUT_ROOT, OUTPUT_MEDIA_URL_BASE

__all__ = ("as_url",)

LOGGER = logging.getLogger(__name__)


def as_url(
    p: Path,
    media_root: str = OUTPUT_ROOT,
    media_url_base: str = OUTPUT_MEDIA_URL_BASE,
) -> str:
    LOGGER.info(f"p: {p}")
    LOGGER.info(f"media_root: {media_root}")
    LOGGER.info(f"media_url_base: {media_url_base}")
    rel_path = p.relative_to(media_root)
    return f"{media_url_base}{quote(rel_path.as_posix())}"
