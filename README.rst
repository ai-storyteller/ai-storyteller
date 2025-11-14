===========
Storyteller
===========
AI Storyteller - where your imagination meets state-of-the-art AI creativity.

MCP
===
Locally
-------
We need two instances:

- MCP server
- MEDIA server

ATM, the Marimo app has MEDIA server functionality. For local inference, we
can use that.

As a pre-requisite, both processed, need to be given this:

.. code-block:: sh

    export OPENAI_API_KEY='ollama'
    export MEDIA_ROOT='media'
    export MEDIA_URL='http://localhost:8000/media/'
    export DISABLE_HTTPS_ENFORCEMENT=1
    export OPENAI_BASE_URL='http://127.0.0.1:11434/v1'
    export OUTPUT_MEDIA_URL='media/output'
    export OUTPUT_PATH='output'

Then start the MEDIA server (FastAPI/Playground):

.. code-block:: sh

    make run

Then start the MCP server in HTTP mode (FastAPI):

.. code-block:: sh

    make mcp
