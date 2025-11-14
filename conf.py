# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "The AI Storyteller"
copyright = "2025, Artur Barseghyan & Dale Richardson"
author = "Artur Barseghyan & Dale Richardson"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_design",
    "sphinx_revealjs",
    "sphinx_revealjs.ext.footnotes",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# -- jsphinx configuration ---------------------------------------------------
# https://github.com/barseghyanartur/jsphinx
prismjs_base = "//cdnjs.cloudflare.com/ajax/libs/prism/1.29.0"

html_css_files = [
    f"{prismjs_base}/themes/prism.min.css",
    f"{prismjs_base}/plugins/toolbar/prism-toolbar.min.css",
    "https://cdn.jsdelivr.net/gh/barseghyanartur/jsphinx/src/css/sphinx_rtd_theme.css",  # noqa
    "https://unpkg.com/tailwindcss@2.2.19/dist/tailwind.min.css",
]

html_js_files = [
    f"{prismjs_base}/prism.min.js",
    f"{prismjs_base}/plugins/autoloader/prism-autoloader.min.js",
    f"{prismjs_base}/plugins/toolbar/prism-toolbar.min.js",
    f"{prismjs_base}/plugins/copy-to-clipboard/prism-copy-to-clipboard.min.js",
    "https://cdn.jsdelivr.net/gh/barseghyanartur/jsphinx/src/js/download_adapter.js",  # noqa
    # "https://cdn.jsdelivr.net/gh/barseghyanartur/jsphinx@feature/Improve-eye-icon-functionality/src/js/download_adapter.js",  # noqa
    # "download_adapter.js",
]

# -- sphinx-no-pragma configuration ------------------------------------------

user_ignore_comments_endings = [
    "# [start]",
]

# -- sphinx-revealjs configuration -------------------------------------------
revealjs_script_plugins = [
    {
        "src": "revealjs/plugin/highlight/highlight.js",
        "name": "RevealHighlight",
    },
    {
        "src": "revealjs/plugin/notes/notes.js",
        "name": "RevealNotes",
    },
]

revealjs_css_files = html_css_files + [
    "revealjs/plugin/highlight/monokai.css",
    "custom.css",
]

revealjs_js_files = list(html_js_files)

revealjs_script_conf = """
{
  // The "normal" size of the presentation, aspect ratio will
  // be preserved when the presentation is scaled to fit different
  // resolutions. Can be specified using percentage units.
  // Original resolution: 960 x 700
  // For large screen: 1920 x 900
  width: 1920,
  height: 900,

  // Factor of the display size that should remain empty around
  // the content
  margin: 0.04,

  // Bounds for smallest/largest possible scale to apply to content
  minScale: 0.2,
  maxScale: 2.0,
}
"""
