import hashlib
import json
from typing import TypeVar

__all__ = (
    "hash_dict",
    "hash_list_of_dicts",
)


def hash_dict(data: dict) -> str:
    """Generate a stable hash for a dictionary."""
    # Convert dictionary to JSON string with sorted keys
    data_str = json.dumps(data, sort_keys=True, separators=(",", ":"))

    # Compute SHA-256 hash
    return hashlib.sha256(data_str.encode()).hexdigest()


def hash_list_of_dicts(data: list[dict]) -> str:
    """Generate a stable hash for a list of dictionaries.

    The function sorts the list by converting each dictionary to a JSON
    string, ensuring that the same content always produces the same hash
    regardless of order.
    """
    # Sort the list using the canonical JSON representation of each dictionary.
    sorted_data = sorted(
        data,
        key=lambda d: json.dumps(d, sort_keys=True, separators=(",", ":")),
    )

    # Convert the sorted list to a JSON string. Using sort_keys here ensures
    # that any nested dictionaries are also sorted.
    data_str = json.dumps(sorted_data, sort_keys=True, separators=(",", ":"))

    # Compute the SHA-256 hash of the resulting string.
    return hashlib.sha256(data_str.encode()).hexdigest()


T = TypeVar("T", dict, list, bool, str, int, float, None)
