import os
import pickle
from typing import Any

from storyteller.modules.st.enums import ImageGeneratorEnum

__all__ = (
    "dump_pickle",
    "get_enum_value",
    "load_pickle",
)


def get_enum_value(value: str | ImageGeneratorEnum):
    if isinstance(value, str):
        return value
    return value.value


def dump_pickle(obj: Any, filename: str, output_dir: str = "output") -> str:
    """
    Serialize `obj` to a pickle file in `output_dir` under the project root.

    :param obj: Any picklable Python object.
    :param filename: Desired filename (with or without “.pkl” extension).
    :param output_dir: Directory (relative to cwd) to write the file into.
        Defaults to "output".
    :return: The full filesystem path to the written pickle file.
    :raises:
        OSError: If the directory cannot be created or the file cannot be
            written.
        pickle.PicklingError: If the object cannot be pickled.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Guarantee .pkl extension
    if not filename.lower().endswith(".pkl"):
        filename = f"{filename}.pkl"

    full_path = os.path.join(output_dir, filename)

    # Write the pickle
    with open(full_path, "wb") as f:
        pickle.dump(obj, f)

    return full_path


def load_pickle(filename: str, output_dir: str = "output") -> Any:
    """
    Load and return a Python object from a pickle file in `output_dir`.

    :param filename: The name of the pickle file (with or without “.pkl”
        extension).
    :param output_dir: Directory (relative to cwd) where the file is located.
        Defaults to "output".
    :return: The unpickled Python object.
    :raises:
        FileNotFoundError: If the specified file does not exist.
        pickle.UnpicklingError: If the file cannot be unpickled.
        OSError: If there’s an I/O error reading the file.
    """
    # Guarantee .pkl extension
    if not filename.lower().endswith(".pkl"):
        filename = f"{filename}.pkl"

    full_path = os.path.join(output_dir, filename)

    # Read and return the pickle
    with open(full_path, "rb") as f:
        return pickle.load(f)
