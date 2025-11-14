import io
import typing
import zipfile
from typing import Any, Union

from src.storyteller.modules.common.structured_outputs import BaseModel

if typing.TYPE_CHECKING:
    from pathlib import Path

    from cloudpathlib import CloudPath

__all__ = (
    "clear_directory",
    "create_zip",
    "schema_to_dict",
)


def schema_to_dict(
    schema: type[BaseModel] | dict[str, Any] | None = None,
) -> dict | None:
    if not schema:
        return None

    if isinstance(schema, dict):
        return schema

    return schema.model_json_schema()


def create_zip(output_dir_name: Union["Path", "CloudPath"]) -> io.BytesIO:
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in output_dir_name.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(output_dir_name)
                # Read the file bytes (works for both local and cloud storage)
                file_bytes = file_path.read_bytes()
                zf.writestr(str(arcname), file_bytes)
    memory_file.seek(0)
    return memory_file


def clear_directory(dir_name: Union["Path", "CloudPath"]) -> None:
    """Remove all contents from the given directory (files and subdirectories).

    Does not remove the given directory itself. Works with `pathlib.Path` and
    `cloudpathlib.CloudPath` objects.

    :param dir_name: The directory to clear.
    """
    for item in dir_name.iterdir():
        if item.is_dir():
            # Recursively clear the directory and remove it.
            clear_directory(item)
            item.rmdir()
        else:
            # Remove the file.
            item.unlink()
