from typing import Protocol

__all__ = ("ProgressBar",)


class ProgressBar(Protocol):
    """ProgressBar type."""

    def update(self, **kwargs) -> None: ...
