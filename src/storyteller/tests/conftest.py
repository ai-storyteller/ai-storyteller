import os
import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def output_dir(tmp_path_factory):
    """Create a temporary output directory for tests."""
    return tmp_path_factory.mktemp("test_output")


@pytest.fixture(scope="session")
def check_ollama():
    """Check if Ollama is running and accessible."""
    import httpx

    base_url = os.getenv("OPENAI_BASE_URL", "http://127.0.0.1:11434/v1")
    try:
        response = httpx.get(base_url.replace("/v1", "/api/version"), timeout=5)
        if response.status_code == 200:
            return True
    except Exception:
        pass
    pytest.skip("Ollama is not running or not accessible")


@pytest.fixture(scope="session")
def check_drawthings():
    """Check if DrawThings is running and accessible."""
    import httpx

    drawthings_url = os.getenv("STORYTELLER_DRAW_THINGS_API_ROOT", "http://localhost:7860")
    try:
        response = httpx.get(drawthings_url, timeout=5)
        if response.status_code in (200, 404):
            return True
    except Exception:
        pass
    pytest.skip("DrawThings is not running or not accessible")