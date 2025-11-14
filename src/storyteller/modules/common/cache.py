import os
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

__all__ = ("CachePath",)

# Grab the concrete Path class (PosixPath on Unix, WindowsPath on Win)
_BasePath = type(Path())


class CachePathMixin:
    """
    Mixin that appends the current YYYY-MM-DD-HH-MM timestamp
    to the `base_path` each time it's converted to a filesystem path.
    """

    base_path: str
    pattern: str

    def __str__(self) -> str:
        ts = datetime.now().strftime(self.pattern)
        return os.path.join(self.base_path, ts)

    __fspath__ = __str__  # used by os.fspath() and Path()

    def __repr__(self) -> str:
        return str(self)

    def __iter__(self) -> Iterator[str]:
        return iter(str(self))

    def __getitem__(self, idx):
        return str(self)[idx]


class CachePath(CachePathMixin, _BasePath):
    """Lazy-evaluated cache path subclassing the concrete `pathlib.Path`.
    Each time you do `str(cache_path)` or `os.fspath(cache_path)`,
    you get `base_path`/"YYYY-MM-DD-HH-MM".

    Example values for the `pattern` include:
    - `%Y-%m-%d-%H-%M`  # Minute based 2025-05-14-17-15
    - `%Y-%m-%d-%H`  # Hour based 2025-05-14-17
    - `%Y-%m-%d`  # Day based 2025-05-14

    Usage example:

    .. code-block:: python

        from time import sleep
        from joblib import Memory
        from playground.modules.common.cache import CachePath

        # Hourly cache path
        CACHE_PATH = CachePath(".joblib_cache", pattern="%Y-%m-%d-%H-%M")
        print(CACHE_PATH)  # 2025-05-14-17-15

        # Joblib memory
        MEMORY = Memory(location=CACHE_PATH, verbose=0)

        @MEMORY.cache
        def expensive_func():
            print("Running expensive function")
            sleep(10)
            return "OK"

        expensive_func()  # First run, takes 10 seconds
        expensive_func()  # Second run, takes 0 seconds
    """

    def __new__(cls, base_path: str, pattern: str = "%Y-%m-%d-%H"):
        """
        :param base_path: Base path of the cache.
        :param pattern: Date pattern for suffix.
        """
        # Construct the real Path object
        obj = super().__new__(cls, base_path)
        # Remember the raw base path
        obj.base_path = base_path
        obj.pattern = pattern
        return obj
