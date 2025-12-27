# utils/help_pdf.py
import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    PageBreak,
    Table,
    TableStyle,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def _try_register_fonts():
    """
    Optionnel : si tu ajoutes des polices TTF dans assets/fonts/
    Ex: assets/fonts/DejaVuSans.ttf
    """
    font_dir = os.path.join("assets", "fonts")
    dejavu = os.path.join(font_dir, "DejaVuSans.ttf")
    dejavu_b = os.path.join(font_dir, "DejaVuSans-Bold.ttf")
    try:
        if os.path.exists(dejavu):
            pdfmetrics.registerFont(TTFont("DejaVuSans", dejavu))
        if os.path.exists(dejavu_b):
            pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", dejavu_b))
    except Exception:
        pass


def _styles():
    _try_register_fonts()
    styles = getSampleStyleSheet()

    base_font = "Helvetica"
    base_bold = "Helvetica-Bold"
    if "DejaVuSans" in pdfmetrics.getRegisteredFontNames():
        base_font = "DejaVuSans"
    if "DejaVuSans-Bold" in pdfmetrics.getRegisteredFontNames():
        base_bold = "DejaVuSans-Bold"

    title = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontName=base_bold,
        fontSize=20,
        leading=24,
        spaceAfter=14,
    )
    h1 = ParagraphStyle(
        "H1",
        parent=styles["Heading1"],
        fontName=base_bold,
        fontSize=14,
        leading=18,
        spaceBefore=14,
        spaceAfter=8,
    )
    h2 = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontName=base_bold,
        fontSize=12,
        leading=16,
        spaceBefore=10,
        spaceAfter=6,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName=base_font,
        fontSize=10.5,
        leading=14,
        spaceAfter=4,
    )
    small = ParagraphStyle(
        "Small",
        parent=styles["BodyText"],
        fontName=base_font,
        fontSize=9,
        leading=12,
        textColor=colors.grey,
        spaceAfter=6,
    )
    mono = ParagraphStyle(
        "Mono",
        parent=styles["BodyText"],
        fontName="Courier",
        fontSize=9.5,
        leading=12,
        backColor=colors.whitesmoke,
        borderColor=colors.lightgrey,
        borderWidth=0.5,
        borderPadding=6,
        spaceAfter=6,
    )
    return {
        "title": title,
        "h1": h1,
        "h2": h2,
        "body": body,
        "small": small,
        "mono": mono,
        "base_font": base_font,
        "base_bold": base_bold,
    }


def _escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _paragraphs_from_text(text: str, body_style, mono_style):
    """
    Convertit un texte simple en Paragraphs.
    Support léger :
    - lignes " - " => bullets
    - lignes en backticks ```...``` => bloc monospace
    - lignes vides => Spacer
    """
    flow = []
    lines = text.split("\n")
    in_code = False
    code_buf = []

    def flush_code():
        nonlocal code_buf
        if code_buf:
            code_text = "<br/>".join(_escape(x) for x in code_buf)
            flow.append(Paragraph(code_text, mono_style))
            code_buf = []

    bullet_buf = []

    def flush_bullets():
        nonlocal bullet_buf
        if bullet_buf:
            # Simple bullet list
            items = "".join(f"<li>{_escape(x)}</li>" for x in bullet_buf)
            flow.append(Paragraph(f"<ul>{items}</ul>", body_style))
            bullet_buf = []

    for raw in lines:
        line = raw.rstrip()

        if line.strip().startswith("```"):
            if not in_code:
                flush_bullets()
                in_code = True
                code_buf = []
            else:
                in_code = False
                flush_code()
            continue

        if in_code:
            code_buf.append(line)
            continue

        if line.strip() == "":
            flush_bullets()
            flow.append(Spacer(1, 6))
            continue

        if line.lstrip().startswith("- "):
            bullet_buf.append(line.lstrip()[2:])
            continue

        # Non-bullet line
        flush_bullets()
        flow.append(Paragraph(_escape(line), body_style))

    flush_bullets()
    flush_code()
    return flow


def _header_footer(canvas, doc, title_text: str):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.grey)

    # Footer line
    canvas.line(1.7 * cm, 1.6 * cm, A4[0] - 1.7 * cm, 1.6 * cm)

    # Left footer
    canvas.drawString(1.7 * cm, 1.1 * cm, title_text)

    # Right footer (page)
    canvas.drawRightString(A4[0] - 1.7 * cm, 1.1 * cm, f"Page {doc.page}")

    canvas.restoreState()


def build_help_pdf_bytes(
    *,
    lang_code: str,
    app_name: str,
    subtitle: str,
    sections: list,
    faq: list,
    screenshots_dir: str = "assets/help_screens",
    logo_path: str = "assets/logo.png",
):
    """
    sections: list of dict { "title": str, "body": str, "image": optional filename, "caption": optional str }
    faq: list of dict { "q": str, "a": str }
    """
    st = _styles()

    buffer_path = None
    from io import BytesIO
    bio = BytesIO()

    doc = SimpleDocTemplate(
        bio,
        pagesize=A4,
        leftMargin=1.7 * cm,
        rightMargin=1.7 * cm,
        topMargin=1.6 * cm,
        bottomMargin=2.0 * cm,
        title=f"{app_name} - Help",
        author=app_name,
    )

    story = []

    # Cover / Header
    if os.path.exists(logo_path):
        try:
            story.append(Image(logo_path, width=3.2 * cm, height=3.2 * cm))
            story.append(Spacer(1, 10))
        except Exception:
            pass

    story.append(Paragraph(_escape(app_name), st["title"]))
    story.append(Paragraph(_escape(subtitle), st["body"]))
    story.append(Spacer(1, 8))

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    story.append(Paragraph(_escape(f"{'Version' if lang_code=='EN' else 'Version'} : {now}"), st["small"]))
    story.append(Spacer(1, 10))

    # Quick table
    story.append(Paragraph(_escape("Sommaire" if lang_code == "FR" else "Contents"), st["h1"]))

    toc_data = [[_escape("Section" if lang_code == "FR" else "Section"), _escape("Description" if lang_code == "FR" else "Description")]]
    for s in sections:
        toc_data.append([_escape(s.get("title", "")), _escape(s.get("toc", ""))])

    toc_table = Table(toc_data, colWidths=[7.5 * cm, 8.0 * cm])
    toc_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F2F2")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("FONTNAME", (0, 0), (-1, 0), st["base_bold"]),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 1), (-1, -1), 9.5),
        ("FONTNAME", (0, 1), (-1, -1), st["base_font"]),
    ]))
    story.append(toc_table)
    story.append(PageBreak())

    # Sections
    for s in sections:
        story.append(Paragraph(_escape(s.get("title", "")), st["h1"]))
        story.append(Spacer(1, 4))

        body = s.get("body", "")
        story.extend(_paragraphs_from_text(body, st["body"], st["mono"]))
        story.append(Spacer(1, 10))

        # Image if any
        img_name = s.get("image")
        if img_name:
            img_path = os.path.join(screenshots_dir, img_name)
            if os.path.exists(img_path):
                try:
                    story.append(Paragraph(_escape(s.get("caption", "")), st["small"]))
                    story.append(Image(img_path, width=16.0 * cm, height=9.0 * cm))
                    story.append(Spacer(1, 10))
                except Exception:
                    story.append(Paragraph(_escape("Capture non lisible (format/poids)."), st["small"]))
            else:
                # graceful note
                note = (
                    f"Capture attendue mais introuvable : {img_path}"
                    if lang_code == "FR"
                    else f"Expected screenshot not found: {img_path}"
                )
                story.append(Paragraph(_escape(note), st["small"]))

        story.append(Spacer(1, 6))

    # FAQ
    story.append(PageBreak())
    story.append(Paragraph(_escape("FAQ – Questions fréquentes" if lang_code == "FR" else "FAQ – Common questions"), st["h1"]))
    story.append(Spacer(1, 6))

    for item in faq:
        story.append(Paragraph(_escape("Q: " + item["q"]), st["h2"]))
        story.extend(_paragraphs_from_text(item["a"], st["body"], st["mono"]))
        story.append(Spacer(1, 8))

    # Build
    title_footer = f"{app_name} – {'Aide' if lang_code=='FR' else 'Help'}"
    doc.build(
        story,
        onFirstPage=lambda c, d: _header_footer(c, d, title_footer),
        onLaterPages=lambda c, d: _header_footer(c, d, title_footer),
    )

    bio.seek(0)
    return bio.getvalue()