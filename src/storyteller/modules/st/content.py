import datetime
import json
import logging
import re
import os
import subprocess
from typing import Union
from pathlib import Path
from io import BytesIO

import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER



__all__ = (
    "break_text_into_paragraphs",
    "create_story_pdf",
    "create_timestamp_directory",
    "docx_to_pdf",
    "download_images",
    "markdown_with_images",
)

LOGGER = logging.getLogger(__name__)


def create_story_pdf(
    title: str,
    text: str,
    image_urls: list[str],
    cover_image_url: str,
    back_cover_image_url: str,
    output_path: str,
):
    width, height = A4
    c = canvas.Canvas(output_path, pagesize=A4)
    current_year = datetime.datetime.now().year

    # --- Styles ---
    styles = getSampleStyleSheet()
    # Define a new style for justified body text with increased leading
    body_style = ParagraphStyle(
        "BodyJustified",
        parent=styles["Normal"],  # Start with defaults from 'Normal'
        alignment=TA_JUSTIFY,
        fontSize=12,  # You can adjust this
        leading=30,
        # Increased line height (default for 12pt font might be 14.4pt,
        # iText default is 1.5*font_size [[1]])
        spaceBefore=20,  # Space before a paragraph
        spaceAfter=12,  # Space after a paragraph (more space)
        leftIndent=0,  # We'll control overall margins via x, y,
        # and available_width
        rightIndent=0,
        fontName="Helvetica",  # Or 'Times-Roman' for a more classic book feel
    )
    title_style = ParagraphStyle(
        "TitleCentered",
        parent=styles["h1"],
        alignment=TA_CENTER,
        fontSize=24,
        leading=28,
        fontName="Helvetica-Bold",
        spaceAfter=0.5 * inch,
    )
    credits_style = ParagraphStyle(
        "CreditsCentered",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=12,  # Smaller than body text
        leading=16,
        fontName="Helvetica",
        spaceAfter=3,
    )
    the_end_style = ParagraphStyle(
        "TheEndCentered",
        parent=styles["h2"],
        alignment=TA_CENTER,
        fontSize=20,
        leading=24,
        fontName="Helvetica-Bold",
        spaceAfter=0.5 * inch,
    )
    footer_style = ParagraphStyle(
        "FooterCentered",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        fontName="Helvetica",
    )

    def draw_image_on_canvas(
        canvas_obj,
        img_path_or_url,
        x,
        y,
        fit_width,
        available_height,
        scale=1.0,
        center_x=True,
    ):
        try:
            if img_path_or_url.startswith("http"):
                response = requests.get(img_path_or_url, timeout=20)
                response.raise_for_status()
                img_data_bytes = response.content
                img_reader = ImageReader(BytesIO(img_data_bytes))
            else:
                img_reader = ImageReader(img_path_or_url)
        except Exception as e:
            LOGGER.info(f"Error loading image: {img_path_or_url}, {e}")
            # Optionally draw a placeholder or error message on canvas
            p_err = Paragraph(f"Error loading image: {img_path_or_url}", styles["Normal"])
            p_err.wrapOn(canvas_obj, fit_width, available_height)
            p_err.drawOn(
                canvas_obj,
                x,
                y - p_err.height if y else height - inch - p_err.height,
            )
            return

        iw, ih = img_reader.getSize()
        aspect = ih / float(iw) if iw > 0 else 1

        new_width = fit_width
        new_height = new_width * aspect

        if (
            new_height > available_height * scale
        ):  # If scaled height is too much, scale by height
            new_height = available_height * scale
            new_width = new_height / aspect if aspect > 0 else 0

        if center_x:
            draw_x = x + (fit_width - new_width) / 2
        else:
            draw_x = x

        # Center vertically within available_height (simple centering for
        # full page image).
        # For images after text, y is usually the starting point from top.
        # If you want to center an image on a blank page:
        # draw_y = y + (available_height - new_height) / 2
        # But for sequential drawing, y is the top baseline.
        draw_y = y - new_height  # Image draws upwards from its bottom-left corner

        if new_width > 0 and new_height > 0:
            canvas_obj.drawImage(
                img_reader,
                draw_x,
                draw_y,
                width=new_width,
                height=new_height,
                preserveAspectRatio=True,
            )
        else:
            LOGGER.info(f"Calculated zero dimension for image: {img_path_or_url}")

    # --- Page Drawing Functions ---

    # Cover page
    # 1. Create & wrap
    p_header = Paragraph(title, title_style)
    available_width = width - 2 * inch
    # Reserve, say, 0.75*inch of height for your header
    p_header.wrapOn(c, available_width, 0.75 * inch)
    # 2. Compute Y so that it's, e.g., 0.5" down from the top edge
    y_header = height - 0.5 * inch - p_header.height
    # 3. Draw it
    p_header.drawOn(c, inch, y_header)

    # For full page image, centered:
    draw_image_on_canvas(
        c,
        cover_image_url,
        0,
        height / 2 + (height / 2 - 2 * inch),
        width,
        height - 3 * inch,
        scale=1.0,
        center_x=True,
    )
    c.showPage()

    # Credits page
    credits_margin = 1.5 * inch
    available_width_credits = width - 2 * credits_margin
    current_y = height - 2 * inch  # Start from top

    lines = [
        "Created by:",
        "Artur Barseghyan",
        "Dale Richardson",
        "",  # For spacing
        "Publisher: AI Storyteller",
        f"Year: {current_year}",
    ]
    # To center this block vertically, calculate total height first or use
    # vfill like logic. For simplicity, drawing from top with some spacing.
    for line_text in lines:
        if not line_text:  # Handle blank line for spacing
            current_y -= credits_style.leading * 0.5  # Half line space
            continue
        p_line = Paragraph(line_text, credits_style)
        p_line.wrapOn(c, available_width_credits, credits_style.leading * 2)
        p_line.drawOn(c, credits_margin, current_y - p_line.height)
        current_y -= p_line.height + credits_style.spaceAfter
    c.showPage()

    # Content pages
    text_margin = 1.5 * inch  # Increased margin for more padding
    available_text_width = width - 2 * text_margin
    images_iter = iter(image_urls)

    paragraphs_text = [p.strip() for p in text.strip().split("\n\n") if p.strip()]

    for paragraph_content in paragraphs_text:
        current_y = height - text_margin  # Reset Y for each new page starting with text

        # Draw the paragraph
        p = Paragraph(paragraph_content, body_style)
        p_width, p_height = p.wrapOn(
            c, available_text_width, height
        )  # Get actual height after wrapping

        # Check if paragraph fits, if not, new page (simple check, for complex
        # flowables use Platypus).
        if current_y - p_height < text_margin:
            c.showPage()
            current_y = height - text_margin

        p.drawOn(c, text_margin, current_y - p_height)
        current_y -= p_height + body_style.spaceAfter  # Move Y down

        # Try to add an image after the paragraph on the same page if space,
        # or new page.
        try:
            image_url = next(images_iter)
            # Space between text and image
            current_y -= 0.5 * inch  # Or body_style.leading or a fixed value

            # Estimate image height to see if it fits (this is tricky without
            # drawing it).
            # For simplicity, let's assume images are roughly half page height
            # or less.
            # A more robust way is to draw image, check position, and then
            # decide on new page.

            # If not enough space for a reasonably sized image, start a new
            # page for the image.
            if current_y < height * 0.4:  # If less than 40% of page height remains
                c.showPage()
                current_y = height - text_margin  # Reset Y for image on new page

            # Draw image on current page (either after text or top of new page)
            # Image width can be, e.g., 75% of available_text_width
            img_display_width = available_text_width * 0.95
            # Available height for image is from current_y down to bottom
            # margin.
            img_available_height = current_y - text_margin

            draw_image_on_canvas(
                c,
                image_url,
                text_margin,
                current_y,
                img_display_width,
                img_available_height,
                scale=1.0,
                center_x=True,
            )

        except StopIteration:
            pass  # No more images

        c.showPage()  # New page after each paragraph + optional image combo

    # The End page
    p_the_end = Paragraph("The End", the_end_style)
    p_the_end.wrapOn(c, width - 2 * inch, height)
    # Center "The End" vertically and horizontally
    p_the_end.drawOn(
        c, inch, (height / 2) + p_the_end.height / 2
    )  # Adjust y for vertical center

    if image_urls:  # Draw last image small and centered below "The End"
        # Position image below "The End" text
        img_y_start = (
            (height / 2) - p_the_end.height / 2 - (0.2 * inch)
        )  # Start below text
        img_available_h_end = img_y_start - inch  # Available height down to bottom margin

        draw_image_on_canvas(
            c,
            image_urls[-1],
            0,
            img_y_start,
            width,
            img_available_h_end,
            scale=0.3,
            center_x=True,
        )
    c.showPage()

    # Back cover
    # Full page image, centered
    draw_image_on_canvas(
        c,
        back_cover_image_url,
        0,
        height,
        width,
        height,
        scale=0.8,
        center_x=True,
    )

    p_footer = Paragraph(
        f"AI Storyteller {current_year}",
        footer_style,
    )
    p_footer.wrapOn(c, width - 2 * inch, inch)
    p_footer.drawOn(c, inch, 0.5 * inch)  # Position at bottom
    c.showPage()

    c.save()

# Add this helper near your other utilities
def _normalize_story_whitespace(text: str) -> str:
    """Normalize story text whitespace:
    - Preserve double newlines (paragraph breaks).
    - Convert single newlines to spaces.
    - Ensure a space after sentence/phrase punctuation when missing.
    - Collapse multiple spaces/tabs.
    """
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Protect paragraph breaks by temporarily marking them
    PARA = "\n\n"
    SENTINEL = "\uFFFF"  # uncommon char as placeholder
    text = text.replace(PARA, SENTINEL)

    # Convert single newlines to spaces
    text = re.sub(r"\n", " ", text)

    # Restore paragraph breaks
    text = text.replace(SENTINEL, PARA)

    # Ensure a space after end punctuation if the next char is non-space
    text = re.sub(r"([.!?])(?=\S)", r"\1 ", text)
    # Ensure a space after comma/semicolon/colon if the next char is non-space
    text = re.sub(r"([,:;])(?=\S)", r"\1 ", text)

    # Collapse runs of spaces/tabs
    text = re.sub(r"[ \t]{2,}", " ", text)

    # Trim whitespace around paragraph boundaries
    text = re.sub(r"[ \t]*\n\n[ \t]*", "\n\n", text)

    return text.strip()


def break_text_into_paragraphs(text: str, nb_paragraphs: int) -> str:
    """
    Ensure the given text is split into exactly nb_paragraphs paragraphs.
    If it already has >= nb_paragraphs (by counting blank-line separators),
    return as-is. Otherwise, split the entire text into sentences and re-chunk
    into nb_paragraphs of roughly equal size.

    :param text: Full text with paragraphs separated by one or more blank lines.
    :param nb_paragraphs: Desired minimum number of paragraphs.
    :return: A string with exactly nb_paragraphs paragraphs (separated by two
        newlines).
    """
    # Normalize whitespace (preserve blank lines; fix missing spaces)
    text = _normalize_story_whitespace(text)

    # 1) Count existing paragraphs
    orig_paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    if len(orig_paras) >= nb_paragraphs:
        return text

    # 2) Flatten into sentences
    #    Split on sentence enders (., !, ?) followed by whitespace
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    total = len(sentences)
    if total == 0:
        return "\n\n".join([""] * nb_paragraphs)

    # 3) Compute how many sentences per paragraph
    base, rem = divmod(total, nb_paragraphs)
    paragraphs: list[str] = []
    idx = 0
    for i in range(nb_paragraphs):
        cnt = base + (1 if i < rem else 0)
        if cnt > 0:
            chunk = sentences[idx : idx + cnt]
            paragraphs.append(" ".join(chunk).strip())
            idx += cnt
        else:
            # no sentences left → empty paragraph
            paragraphs.append("")
    return "\n\n".join(paragraphs)


def markdown_with_images(
    title: str,
    text: str,
    images: list[str],
    cover_image_url: str,
    back_cover_image_url: str,
) -> str:
    """
    Insert images after each paragraph in the given text, and
    append any remaining images at the end.

    :param title: Document title.
    :param text: A single string containing all paragraphs (separated by one
        or more blank lines).
    :param images: A list of image URLs to insert.
    :param cover_image_url: URL to the cover image.
    :param back_cover_image_url: URL to the back cover image.
    :return: A Markdown-formatted string where an image follows each
        paragraph (until images run out).

    Example usage:

    .. code-block:: python

        text = '''First paragraph here.

        Second paragraph here.

        Third paragraph here.
        '''

        imgs = [
            "https://example.com/img1.jpg",
            "https://example.com/img2.jpg"
        ]
        print(markdown_with_images(text, imgs))
    """
    updated_text = break_text_into_paragraphs(text, nb_paragraphs=len(images))

    # Split on one or more blank lines
    paragraphs = re.split(r"\n\s*\n", updated_text.strip())

    md_blocks = [f"# {title}", ""]  # title + blank line
    md_blocks.append(f"![Image {0}]({cover_image_url})")
    # md_blocks.append("\\newpage")

    # Interleave images with paragraphs
    for i, para in enumerate(paragraphs):
        md_blocks.append(para.strip())
        if i < len(images):
            md_blocks.append(f"![Image {i + 1}]({images[i]})")
        md_blocks.append("")  # blank line after each block

    # Append any leftover images
    for j in range(len(paragraphs), len(images)):
        md_blocks.append(f"![Image {j + 1}]({images[j]})")
        md_blocks.append("")

    # md_blocks.append("\\newpage")
    md_blocks.append("## The End")
    md_blocks.append("")
    md_blocks.append(f"![Image {0}]({back_cover_image_url})")

    return "\n".join(md_blocks)


def create_timestamp_directory(base_dir: str = "output") -> str:
    """
    Create a timestamped directory under the base directory in
    format YYYY-MM-DD--HH-MM-SS.
    Returns the path to the new directory.
    """
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d--%H-%M-%S")
    target_dir = os.path.join(base_dir, timestamp)
    os.makedirs(target_dir, exist_ok=True)
    return target_dir


def download_images(
    image_urls: list[str], dest_folder: str, suffix: str = ""
) -> list[str]:
    """
    Download images from the list of URLs into dest_folder.
    Returns a list of local file paths for the downloaded images.
    """
    local_paths = []
    for idx, url in enumerate(image_urls, start=1):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            ext = os.path.splitext(url)[1] or ".jpg"
            filename = f"image_{idx}_{suffix}{ext}"
            filepath = os.path.join(dest_folder, filename)
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            local_paths.append(filepath)
        except Exception as e:
            LOGGER.info(f"Failed to download {url}: {e}")
    return local_paths


def dump_json(data: dict, json_path: str) -> None:
    """
    Dump the provided data dict into a JSON file at json_path.
    """
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def docx_to_pdf(docx_path: Union[str, Path], pdf_path: Union[str, Path]) -> None:
    """
    Convert a DOCX file to PDF using LibreOffice (soffice --headless).
    Supports both string and pathlib.Path objects for input and output paths.
    Preserves page breaks and layout.
    """
    # Ensure both paths are Path objects for consistent handling
    docx_path = Path(docx_path)
    pdf_path = Path(pdf_path)

    out_dir = pdf_path.parent.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            "soffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(out_dir),
            str(docx_path),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    produced = out_dir / docx_path.with_suffix(".pdf").name
    if produced != pdf_path:
        if pdf_path.exists():
            pdf_path.unlink()
        produced.replace(pdf_path)


CURRENT_YEAR = datetime.datetime.now().year


# Basic LaTeX escaping for user-provided text content
def escape_latex(text: str) -> str:
    # This is a basic escaper. For truly arbitrary input, a more
    # comprehensive LaTeX escaping library or function would be safer.
    chars_to_escape = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
        "\\": r"\textbackslash{}",
    }
    # Order matters for backslash: escape it first.
    if "\\" in text:  # Check if backslash exists to avoid error if not
        text = text.replace("\\", chars_to_escape["\\"])
    for char, escaped_char in chars_to_escape.items():
        if char != "\\":  # Avoid re-processing backslash
            text = text.replace(char, escaped_char)
    return text

