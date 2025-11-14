from collections.abc import Callable
from contextlib import suppress
from typing import TypeVar

T = TypeVar("T")

__all__ = ("parse_value",)


def parse_value(value: str, cast: Callable[[str], T], default: T) -> T:
    """Try to convert `value to type `cast`.
    On ValueError or TypeError, return `default`.

    :param value: The value to convert.
    :param cast: The type to convert to.
    :param default: The default value to return if `value` is not `cast`.
    :return: The converted value.

    Usage example:

    .. code-block:: python

        import os

        # `int` with `default=100`
        MAX_NB_DATASET_ITEMS = parse_value(os.getenv("MAX_NB_DATASET_ITEMS", ""), int, 100)

        # `float` with `default=0.3`
        TEMPERATURE = parse_value(os.getenv("TEMPERATURE", ""), float, 1.0)
    """
    with suppress(Exception):
        return cast(value)
    return default
