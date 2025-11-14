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

    export DISABLE_HTTPS_ENFORCEMENT=1
    export DISABLE_AUTHENTICATION=1
    export OPENAI_API_KEY='ollama'
    export OPENAI_BASE_URL='http://127.0.0.1:11434/v1'

    export STORYTELLER_MEDIA_PATH='/Users/me/repos/ai-storyteller/media'
    export STORYTELLER_MEDIA_URL='http://localhost:8000/media/'

    export STORYTELLER_OUTPUT_PATH='/Users/me/repos/ai-storyteller/output'
    export STORYTELLER_OUTPUT_MEDIA_URL='http://localhost:8000/media/output/'

    export STORYTELLER_TOOL_MODEL_PROVIDER='openai'
    export STORYTELLER_TOOL_MODEL_NAME='gpt-5-mini'
    export STORYTELLER_STORY_MODEL_NAME='o4-mini'
    export STORYTELLER_IMAGE_DESCRIPTOR_MODEL_NAME='gpt-4.1-mini'

Then start the MEDIA server (FastAPI/Playground):

.. code-block:: sh

    make run

Then start the MCP server in HTTP mode (FastAPI):

.. code-block:: sh

    make mcp

To start the AI chat (with storyteller tool), type:

.. code-block:: sh

    make chat

License
=======

MIT

Authors
=======

- Artur Barseghyan
- Dale Richardson
