import argparse
import logging
import sys
from typing import Optional, Dict, List

from fastmcp import FastMCP

from storyteller.modules.st.tool_impl import create_story_bundle_fn

# ----------------------------------------------------------------------------
# Logging setup
# ----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------
# MCP Server instance
# ----------------------------------------------------------------------------
mcp = FastMCP("AI Storyteller: Story creation server")


# ----------------------------------------------------------------------------
# Helper: Type mapping
# ----------------------------------------------------------------------------

def _fallback_title_from_request(req: str) -> str:
    """Best-effort title if LLM didn't pass one."""
    raw = req.strip().split()
    if not raw:
        return "My Storybook"
    draft = " ".join(raw[:8])
    draft = draft.strip().rstrip(".!?")
    if not draft:
        return "My Storybook"
    lower = draft.lower()
    for prefix in [
        "create a story about", "make a story about", "tell a story about"
    ]:
        if lower.startswith(prefix):
            draft = draft[len(prefix):].strip().strip(":,-")
    draft = draft[:60].strip()
    if not draft:
        draft = "My Storybook"
    nice = draft[0].upper() + draft[1:]
    return nice


@mcp.tool(
    name="create_story_bundle",
    description="""
Generate a fully illustrated story and export a ready-to-download PDF and DOCX versions.
Use this tool when the user is asking for a children's story, fairy tale, bedtime story, adventure story, fantasy, etc., and they also want illustrations and a final PDF/DOCX book.

Arguments:
- story_request (str): The user's entire request, verbatim.
- story_title (str, optional): A short, warm, kid-friendly book title you invent from the request. If the user already gave a title, reuse it.
- artistic_style_key (str, optional): Visual style hint (e.g., 'watercolor', 'storybook').
- image_prompt_prefix (str, optional): Visual nuance to be added at the beginning of every image prompt.
- image_prompt_suffix (str, optional): Visual nuance to be added at the end of every image prompt.
- reading_level (str, optional): Age-appropriate reading level (e.g., '6-year-old').
- image_generator (str, optional): Backend for image generation (e.g., 'DrawThings').
- user_email (str, optional): User namespace for output.
- url_path (str, optional): Subfolder label (defaults to 'api').

Returns:
- title: Story title.
- public_urls: Dict of PDF download links.
- pdf_paths: Local filesystem paths.
- output_dir: Directory where assets were written.

After calling this tool, reply to the user with the title and all PDF links in public_urls.
"""
)
def create_story_bundle(
    story_request: str,
    story_title: Optional[str] = None,
    artistic_style_key: Optional[str] = None,
    reading_level: Optional[str] = None,
    image_generator: Optional[str] = None,
    user_email: Optional[str] = None,
    url_path: str = "api",
    image_prompt_prefix: str | None = None,
    image_prompt_suffix: str | None = None,
) -> Dict:
    """
    Generate a fully illustrated story and export multiple ready-to-download PDF versions.
    """
    _title = story_title.strip() if story_title and story_title.strip() else _fallback_title_from_request(story_request)
    return create_story_bundle_fn(
        story_request=story_request,
        story_title=_title,
        artistic_style_key=artistic_style_key,
        reading_level=reading_level,
        image_generator=image_generator,
        user_email=user_email,
        url_path=url_path,
        image_prompt_prefix=image_prompt_prefix,
        image_prompt_suffix=image_prompt_suffix,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI Storyteller - Story creation MCP Server — run in `stdio`, `http` or `sse` mode."
    )
    parser.add_argument(
        "mode",
        nargs="?",
        choices=["stdio", "http", "sse"],
        default="stdio",
        help="Transport mode: 'stdio' (default) or 'http'",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host for HTTP mode (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8005,
        help="Port for HTTP mode (default: 8005)",
    )
    args = parser.parse_args()

    if args.mode == "http":
        logger.info(f"Starting MCP server in HTTP mode on {args.host}:{args.port}")
        mcp.run(transport="http", host=args.host, port=args.port)
    elif args.mode == "sse":
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        logger.info("Starting MCP server in STDIO mode")
        mcp.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
