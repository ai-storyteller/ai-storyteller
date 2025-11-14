import logging
import typing

if typing.TYPE_CHECKING:
    from marimo import ui

__all__ = ("get_filename_and_bytes",)

LOGGER = logging.getLogger(name=__name__)


def get_filename_and_bytes(
    uploaded_file: "ui.file",
) -> tuple[str, bytes] | tuple[None, bytes]:
    LOGGER.info(uploaded_file.value)
    if uploaded_file.value:
        return uploaded_file.value[0]
    return None, b""
