import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def generate_pdf_report(content, output_path="generated_report.pdf",
                        header_image="header.jpg", report_date=None):
    """
    Generate a styled PDF report with header image, title, subtitle, date, and summary text.
    """
    os.makedirs("generated_reports", exist_ok=True)
    output_dir = "generated_reports"

    # Base filename
    base_filename = f"Generate_report_{datetime.now().strftime('%Y-%m-%d_%H-%M')}"
    filename = f"{base_filename}.pdf"
    output_path = os.path.join(output_dir, filename)

    # Versioning
    version = 1
    while os.path.exists(output_path):
        version += 1
        filename = f"{base_filename}_v{version}.pdf"
        output_path = os.path.join(output_dir, filename)

    if report_date is None:
        report_date = datetime.now().strftime("%d-%b-%Y")

    json_string = content
    data = json.loads(json_string)


    title = data.get("title", "Report")
    subtitle = data.get("subtitle", "Summary")
    summary_text = data.get("summary", "")


    # Create document
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            leftMargin=40, rightMargin=40, topMargin=60, bottomMargin=40)

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(name="TitleStyle", fontSize=18, leading=22,
                                 alignment=TA_LEFT, spaceAfter=12, bold=True)
    subtitle_style = ParagraphStyle(name="SubtitleStyle", fontSize=14, leading=18,
                                    alignment=TA_LEFT, spaceAfter=12, bold=True)
    date_style = ParagraphStyle(name="DateStyle", fontSize=11, leading=14,
                                alignment=TA_LEFT, italic=True, spaceAfter=20)
    body_style = ParagraphStyle(name="BodyStyle", fontSize=11, leading=15,
                                alignment=TA_LEFT, spaceAfter=10)
    
    elements = []

    # Header image (logo)
    if header_image and os.path.exists(header_image):
        img = Image(header_image, width=A4[0]-80, height=60)  # width = page width - margins
        img.hAlign = "LEFT"
        elements.append(img)
        elements.append(Spacer(1, 12))

    # Title, subtitle, date
    elements.append(Paragraph(title, title_style))
    elements.append(Paragraph(subtitle, subtitle_style))
    elements.append(Paragraph("Date: " + report_date, date_style))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Dear Esteemed Colleagues,", body_style))
    elements.append(Spacer(1, 6))
    # Summary text (split into paragraphs)
    for para in summary_text.strip().split("\n\n"):
        elements.append(Paragraph(para.strip(), body_style))
        elements.append(Spacer(1, 6))

    elements.append(Paragraph("Sincerely,", body_style))
    elements.append(Paragraph("<br/>Mohamad El-Hage<br/>Executive Chair of the Board of Directors<br/>AMAD Rehabilitation and Long-Term Care", body_style))


    doc.build(elements)
    return output_path
