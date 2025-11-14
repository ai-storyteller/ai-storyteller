# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "langchain-core",
#     "langchain-community",
#     "langchain",
#     "langgraph",
# ]
# ///

"""
Story Agent
===========

This module exposes a chat-style agent that focuses ONLY on story creation.

Key behavior:
- User can say: "Create a story about a little fish named Rody and a 6 year old
  girl named Ani. Generate images using DrawThings."
- The agent will decide to call the `create_story_bundle` tool.
- The tool (from story_tool.create_story_bundle_fn) will:
    * Extract characters and structure from the request
    * Write the story
    * Generate images
    * Build PDFs (3 variants)
    * Return file:// URLs
- The agent will reply with those PDF links.

Important details:
- We intentionally do not assume who the main character is.
- We do not assume reading level or style unless the tool infers it.

Usage:
    uv run story_agent.py -- chat

Then type your request.
"""

from __future__ import annotations

import argparse
import json
from typing import Annotated, TypedDict

from langchain.chat_models import init_chat_model
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import StructuredTool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from storyteller.modules.st.tool_impl import create_story_bundle_fn
from storyteller.settings import (
    TOOL_MODEL_PROVIDER as MODEL_PROVIDER,
    TOOL_MODEL_NAME as MODEL_NAME,
)

# -----------------------------------------------------------------------------
# 1. Tool definition
# -----------------------------------------------------------------------------
def _fallback_title_from_request(req: str) -> str:
    """Best-effort title if LLM didn't pass one."""
    # Very defensive: short, kid-book-ish, alphanumeric-ish.
    # We take first ~8 meaningful words, capitalize nicely.
    raw = req.strip().split()
    if not raw:
        return "My Storybook"
    draft = " ".join(raw[:8])
    # Capitalize first letter only, avoid screaming long prompts.
    draft = draft.strip().rstrip(".!?")
    if not draft:
        return "My Storybook"
    # Example: "Create a story about a little fish named Rody"
    # -> "Create a story about a little fish named Rody"
    # We can soften leading verbs like "Create a story about" -> "A Little Fish Named Rody"
    lower = draft.lower()
    if lower.startswith("create a story about"):
        draft = draft[len("create a story about"):].strip().strip(":,-")
    elif lower.startswith("make a story about"):
        draft = draft[len("make a story about"):].strip().strip(":,-")
    elif lower.startswith("tell a story about"):
        draft = draft[len("tell a story about"):].strip().strip(":,-")

    # Final tidy
    draft = draft[:60].strip()
    if not draft:
        draft = "My Storybook"
    # Title-case-ish for kid feel
    nice = draft[0].upper() + draft[1:]
    return nice


def _wrap_create_story_bundle_fn(
    story_request: str,
    story_title: str | None = None,
    artistic_style_key: str | None = None,
    reading_level: str | None = None,
    image_generator: str | None = None,
    user_email: str | None = None,
    url_path: str = "api",
) -> dict:
    """
    Thin wrapper around create_story_bundle_fn so we have a stable signature.

    We forward all arguments directly.

    :param story_request: Full natural language request from the user.
    :param artistic_style_key: Optional style hint.
    :param reading_level: Optional reading level hint.
    :param image_generator: Optional image generator backend ("DrawThings", etc.).
    :param user_email: Optional namespace for output dir.
    :param url_path: Optional subfolder name, default "api".
    :return: Result dict with 'public_urls' and PDF paths.
    :rtype: dict
    """
    _title = story_title if story_title and story_title.strip() else _fallback_title_from_request(story_request)

    return create_story_bundle_fn(
        story_request=story_request,
        story_title=_title,
        artistic_style_key=artistic_style_key,
        reading_level=reading_level,
        image_generator=image_generator,
        user_email=user_email,
        url_path=url_path,
    )


create_story_bundle_tool = StructuredTool.from_function(
    func=_wrap_create_story_bundle_fn,
    name="create_story_bundle",
    description=(
        "Generate a fully illustrated story PLUS export ready-to-download PDF and DOCX versions. "
        "Use this tool when the user is asking for a children's story, fairy tale, bedtime story, "
        "adventure story, fantasy, etc. and they also want illustrations and a final PDF/DOCX book.\n\n"
        "Arguments you MUST provide:\n"
        "- story_request: str. Pass the user's entire request, including character names, mood, age hints, "
        "  style instructions, safety/tone instructions, etc. Do NOT summarize; pass it verbatim.\n"
        "- story_title (str): a short, warm, kid-friendly book title you invent from the request. "
        "  Example: 'Ani and Rody and the Stormy Lake'. If the user already gave a title, reuse it.\n\n"
        "- story_text (str): A full story text you invent from the request. Be creative. Take reading_level into consideration.\n"
        "Optional:\n"
        "- artistic_style_key: Optional[str]. If the user specified a visual style that clearly maps to one of "
        "  known styles (like 'watercolor', 'storybook', etc.), include that exact key if you know it. Otherwise omit.\n"
        "- reading_level: Optional[str]. If the user says 'for a 6-year-old', pass '6-year-old' or similar. Otherwise omit.\n"
        "- image_generator: Optional[str]. If the user says 'Use DrawThings', pass 'DrawThings'. Otherwise omit.\n"
        "- user_email: Optional[str]. If you know the user's e-mail or account id for namespacing output, pass it. "
        "  Otherwise omit.\n"
        "- url_path: Optional[str]. Subfolder label (defaults to 'api').\n\n"
        "Return value: A dict with keys:\n"
        "- title: Story title.\n"
        "- public_urls: { 'method_1', 'method_2', 'method_3' } which are direct download links to PDF/DOCX.\n"
        "- pdf_paths: Local filesystem paths for debugging.\n"
        "- output_dir: Directory where all assets were written.\n\n"
        "AFTER calling this tool, you MUST reply to the user with the title and all PDF links in public_urls."
    ),
)


# -----------------------------------------------------------------------------
# 2. Agent state and nodes
# -----------------------------------------------------------------------------

class StoryState(TypedDict):
    """
    Conversation state carried through the LangGraph execution.

    :ivar messages: List of messages (HumanMessage, AIMessage, ToolMessage, etc.).
    :ivar trace: List of trace steps for debugging.
    :ivar story_mode: Bool-like flag. When True, means we already executed
        create_story_bundle OR we are mid-tool usage. We use this to prevent
        chaining more tools in the same turn.
    """
    messages: Annotated[list, add_messages]
    trace: list
    story_mode: bool


class BasicToolNode:
    """
    A node that actually runs the tools requested by the LLM in the previous step.

    We only expose `create_story_bundle` here, but this class is written in a way
    that would scale if you later add more storytelling-related tools.
    """

    def __init__(self, tools: list[StructuredTool]) -> None:
        # Map tool name -> tool instance
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict) -> dict:
        """
        Execute all tool calls that the last AIMessage requested.
        Turn each tool result into a ToolMessage so the LLM can see it.
        Also update trace and flip story_mode to True.
        """
        if messages := inputs.get("messages", []):
            last_msg = messages[-1]
        else:
            raise ValueError("No message found in input for tools node.")

        trace = list(inputs.get("trace", []))
        outputs = []
        story_mode = bool(inputs.get("story_mode", False))

        # LLM tool calls look like .tool_calls on the last AIMessage
        for tool_call in getattr(last_msg, "tool_calls", []) or []:
            _name = tool_call["name"]
            _args = tool_call.get("args") or {}

            print(f"\n====\n[tool-call] {_name} args={_args!r}")

            tool = self.tools_by_name.get(_name)
            if tool is None:
                result = {"error": f"Unknown tool: {_name}"}
            else:
                # Execute tool
                result = tool.invoke(_args)

            # Flip story_mode if we executed create_story_bundle
            if _name == "create_story_bundle":
                story_mode = True

            # Produce short preview for trace
            try:
                s = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False)
                preview = (s[:240] + "…") if len(s) > 240 else s
            except Exception:
                preview = f"<non-serializable {type(result).__name__}>"

            trace.append({
                "node": "tools",
                "event": "tool_executed",
                "tool": _name,
                "args": _args,
                "result_preview": preview,
            })

            # Return a ToolMessage back into the graph so chatbot can read it
            outputs.append(
                ToolMessage(
                    content=json.dumps(result, ensure_ascii=False),
                    name=_name,
                    tool_call_id=tool_call["id"],
                )
            )

        return {"messages": outputs, "trace": trace, "story_mode": story_mode}


# Instantiate the tool node with only our storytelling tool
tool_node = BasicToolNode(tools=[create_story_bundle_tool])


# -----------------------------------------------------------------------------
# 3. LLM node (chatbot)
# -----------------------------------------------------------------------------

# Initialize base chat model.
_llm = init_chat_model(
    model=MODEL_NAME,
    model_provider=MODEL_PROVIDER,
)
_llm_with_tools = _llm.bind_tools([create_story_bundle_tool])


CHATBOT_SYSTEM_PROMPT = (
    "Policy:\n"
    "- You are a story creation assistant.\n"
    "- If the user asks for an illustrated storybook, bedtime story, fairy tale, "
    "  or anything that sounds like 'generate a story and images / PDF/DOCX', you SHOULD "
    "  call the `create_story_bundle` tool with:\n"
    "    story_request = the user's exact request text (verbatim),\n"
    "    image_generator = whatever backend the user mentioned (e.g. 'DrawThings'),\n"
    "    reading_level = if they mention an age or reading level, otherwise omit,\n"
    "    artistic_style_key = if they mention a clear art style, otherwise omit,\n"
    "    user_email = if they provided an email or account identifier, otherwise omit.\n"
    "- After you call `create_story_bundle` in a turn, do NOT call any other tool in the same turn.\n"
    "- When `create_story_bundle` returns a result (in a ToolMessage), "
    "  you MUST answer by:\n"
    "    1) Stating the story title from the tool result,\n"
    "    2) Saying that the illustrated storybook is ready,\n"
    "    3) Listing all links in result.public_urls (method_1, method_2, method_3) as download links.\n"
    "- Never reveal internal filesystem paths except by presenting them as download links if they "
    "  appear in `public_urls`. Do not expose anything else from pdf_paths or output_dir.\n"
    "- If the user is just chatting about stories or asking questions without requesting full PDF "
    "  generation, you may answer directly without calling any tools.\n"
)


def chatbot_node(state: StoryState) -> dict:
    """
    Chatbot node:
    - Prep messages = system prompt + conversation so far.
    - Ask the LLM to respond.
    - The LLM MAY request a tool call (create_story_bundle).
    - We append a trace entry describing what it asked for.
    """
    msgs = [SystemMessage(content=CHATBOT_SYSTEM_PROMPT)] + state["messages"]

    ai = _llm_with_tools.invoke(msgs)

    trace = list(state.get("trace", []))
    tool_calls = getattr(ai, "tool_calls", []) or []
    trace.append({
        "node": "chatbot",
        "event": "llm_invoked",
        "requested_tools": [
            {"name": tc.get("name"), "args": tc.get("args")} for tc in tool_calls
        ],
    })

    # Keep story_mode flag from state (we might already be in story_mode)
    return {
        "messages": [ai],
        "trace": trace,
        "story_mode": state.get("story_mode", False),
    }


# -----------------------------------------------------------------------------
# 4. Graph wiring
# -----------------------------------------------------------------------------

graph_builder = StateGraph(StoryState)

graph_builder.add_node("chatbot", chatbot_node)
graph_builder.add_node("tools", tool_node)


def guarded_condition(state: StoryState):
    """
    Conditional edge routing.

    Rules:
    - If story_mode is True, that means we already executed create_story_bundle this turn,
      OR we are returning after it. We should end the turn (no more tools).
    - Otherwise, check if the last AIMessage has any tool_calls.
      If yes, go to 'tools', else END.
    """
    if state.get("story_mode"):
        return END

    last_msg = state.get("messages", [])[-1]
    requested = getattr(last_msg, "tool_calls", []) or []
    return "tools" if requested else END


# Edges:
# Start -> chatbot
graph_builder.add_edge(START, "chatbot")
# chatbot -> conditional -> tools or END
graph_builder.add_conditional_edges(
    "chatbot",
    guarded_condition,
    {
        "tools": "tools",
        END: END,
    },
)
# tools -> chatbot (so after executing tool(s), we let the LLM produce the final reply)
graph_builder.add_edge("tools", "chatbot")

# Compile final graph
story_graph = graph_builder.compile()


# -----------------------------------------------------------------------------
# 5. Tiny driver / CLI
# -----------------------------------------------------------------------------

def run_query(user_input: str) -> None:
    """
    Run a single user message through the graph and print the conversation + trace.

    This simulates what your service / API layer would do per user turn.
    """
    print("\n" + "=" * 20)
    # Initialize base state: one HumanMessage
    state = {
        "messages": [HumanMessage(content=user_input)],
        "trace": [],
        "story_mode": False,
    }

    final_state = None

    # Stream lets us observe node-by-node execution.
    for event in story_graph.stream(state):
        for node_name, value in event.items():
            print(f"[node] {node_name}")
            msgs = value.get("messages", [])
            # Print assistant content if available
            if msgs and hasattr(msgs[-1], "content"):
                print("Assistant:", msgs[-1].content)
            final_state = value

    # Print trace for debugging
    print("\n--- Trace ---")
    if final_state and "trace" in final_state:
        for i, step in enumerate(final_state["trace"], 1):
            ev = step.get("event")
            if ev == "llm_invoked":
                requested = step.get("requested_tools", [])
                print(f"{i}. [chatbot] requested_tools={requested}")
            elif ev == "tool_executed":
                print(
                    f"{i}. [tools] {step['tool']} "
                    f"args={step['args']} -> {step['result_preview']}"
                )
            else:
                print(f"{i}. {step}")
    else:
        print("(no trace)")
    print("=" * 20 + "\n")


def main() -> None:
    """
    CLI entry point.

    Modes:
      - chat : Interactive chat loop with the story agent.
      - test : Send a single prompt from CLI right away.
    """
    parser = argparse.ArgumentParser(
        description="Storytelling LangGraph agent"
    )
    parser.add_argument(
        "mode",
        choices=["chat", "test"],
        nargs="?",
        default="chat",
        help="Run interactive chat (default) or run once and exit.",
    )
    parser.add_argument(
        "--prompt",
        help="Prompt to run in 'test' mode.",
        required=False,
    )
    args = parser.parse_args()

    if args.mode == "test":
        if not args.prompt:
            run_query(
                "Create a story about a little fish named Rody and a 9 year "
                "old girl named Luna. They are sweet troublemakers eventually "
                "everything ends fine. Make it really funny. Add a couple of "
                "new characters - talking animals. It's an ode to friendship "
                "and team-work. Artistic style - cubism."
            )
        else:
            run_query(args.prompt)
        return

    # Interactive chat loop
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            run_query(user_input)

        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
