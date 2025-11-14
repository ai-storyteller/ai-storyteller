import base64
import json
import logging
import os
from pathlib import Path

from cloudpathlib import AnyPath, CloudPath, GSClient
from google.oauth2 import service_account

from storyteller.settings import (
    STORAGE_INPUT_PATH,
    STORAGE_OUTPUT_PATH,
    STORAGE_SERVICE_ACCOUNT,
    STORAGE_SERVICE_ACCOUNT_B64,
)

__all__ = (
    "get_storage_client",
    "get_root_dir",
    "get_input_root_dir",
    "get_output_root_dir",
)

LOGGER = logging.getLogger(__name__)


def get_storage_client() -> GSClient | None:
    # -------------------------------------------------------------------------
    # Google Cloud Storage
    # -------------------------------------------------------------------------
    storage_service_account_b64 = STORAGE_SERVICE_ACCOUNT_B64
    storage_service_account_info = None

    if storage_service_account_b64:
        storage_service_account_str = base64.b64decode(
            storage_service_account_b64
        ).decode("utf-8")
        storage_service_account_info = json.loads(storage_service_account_str)

    storage_service_account_str = STORAGE_SERVICE_ACCOUNT

    if not storage_service_account_info and storage_service_account_str:
        storage_service_account_info = json.loads(storage_service_account_str)

    if storage_service_account_info:
        storage_credentials = service_account.Credentials.from_service_account_info(
            storage_service_account_info,
        )
        storage_client = GSClient(credentials=storage_credentials)
    else:
        storage_client = None

    return storage_client


def get_root_dir(path: str, storage_client: GSClient | None = None) -> Path | CloudPath:
    kwargs = {"client": storage_client} if storage_client else {}
    root_dir = AnyPath(path, **kwargs)
    return root_dir


def get_input_root_dir(
    storage_client: GSClient | None = None,
) -> Path | CloudPath:
    root_path = STORAGE_INPUT_PATH
    return get_root_dir(root_path, storage_client)


def get_output_root_dir(
    storage_client: GSClient | None = None,
) -> Path | CloudPath:
    root_path = STORAGE_OUTPUT_PATH
    return get_root_dir(root_path, storage_client)
