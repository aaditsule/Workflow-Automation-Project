import os
import pandas as pd
import docx
import fitz  # PyMuPDF
import datetime as datetime
import re

def extract_text_from_docx(path):
    doc = docx.Document(path)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip() != ""])

def extract_text_from_pdf(path):
    doc = fitz.open(path)
    return "\n".join([page.get_text() for page in doc])

def extract_text_from_excel(path):
    try:
        xl = pd.ExcelFile(path)
        full_text = ""

        for sheet in xl.sheet_names:
            df = xl.parse(sheet, header=None, dtype=str)

            # Remove completely empty rows and columns
            df.dropna(how='all', inplace=True)
            df.dropna(axis=1, how='all', inplace=True)

            if df.empty:
                continue

            full_text += f"\n\n### Sheet: {sheet}\n\n"

            df = df.fillna("").astype(str)

            # Detect if sheet looks like KPI/metrics
            is_kpi = any(
                df.apply(lambda row: row.astype(str).str.contains(
                    r"(KPI|Metric|Target|Actual|Achieved|Revenue|Growth|%)", 
                    case=False, regex=True).any(), axis=1)
            )

            if is_kpi:
                full_text += "**(This sheet appears to contain KPI / Metrics data)**\n\n"

            # Convert every row into a markdown-style row
            for idx, row in df.iterrows():
                row_text = " | ".join(format_cell(cell) for cell in row)
                full_text += row_text + "\n"

        return full_text.strip() or "No readable data found in Excel file."

    except Exception as e:
        return f"Failed to parse Excel file: {e}"
    
def format_cell(cell):
    """Format individual cell values for readability."""
    cell = str(cell).strip()

    # Handle empty cells
    if cell.lower() in ["nan", "none", ""]:
        return ""

    # Detect and format dates
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%b-%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(cell, fmt).strftime("%d-%b-%Y")
        except Exception:
            pass

    # Detect currency / numbers
    if re.match(r"^\$?\d+(\.\d+)?$", cell.replace(",", "")):
        # Normalize to include commas for thousands
        try:
            value = float(cell.replace("$", "").replace(",", ""))
            return f"${value:,.2f}" if "$" in cell else f"{value:,.2f}"
        except:
            return cell

    return cell
    
def process_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.docx':
        return extract_text_from_docx(path)
    elif ext == '.pdf':
        return extract_text_from_pdf(path)
    elif ext == '.xlsx':
        return extract_text_from_excel(path)
    else:
        raise ValueError("Unsupported file type.")

 