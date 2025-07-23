import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

def generate_pdf_report(summary_text, output_dir="generated_reports"):
    os.makedirs(output_dir, exist_ok=True)

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

    # PDF styles
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    custom = ParagraphStyle(
        name="Body",
        parent=styles["Normal"],
        fontSize=11,
        leading=15
    )
    custom_bold = ParagraphStyle(
        name="Body",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15
    )

    # Content
    elements = []
    elements.append(Paragraph("AMAD – Chair Monthly Memo – " + datetime.now().strftime("%B-%Y"), styles["Title"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("AMAD Rehabilitation and Long-term Care (AMAD)", styles["Heading2"]))
    elements.append(Paragraph("To OSHCO Leadership and AMAD Board of Directors (BOD)", styles["Heading2"]))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("Date: " + datetime.now().strftime("%d-%b-%Y"), styles["Heading3"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Dear Esteemed Colleagues,", custom_bold))

    elements.append(Spacer(1, 12))

    for para in summary_text.strip().split("\n\n"):
        elements.append(Paragraph(para.strip(), custom))
        elements.append(Spacer(1, 8))

    # elements.append(Spacer(1, 24))
    elements.append(Paragraph("Sincerely,", custom))
    elements.append(Paragraph("<br/>Mohamad El-Hage<br/>Executive Chair of the Board of Directors<br/>AMAD Rehabilitation and Long-Term Care", custom))

    doc.build(elements)
    return output_path
