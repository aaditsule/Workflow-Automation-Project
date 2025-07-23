import os
import pandas as pd
import docx
import fitz  # PyMuPDF

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

            # Convert every row into a markdown-style row
            for idx, row in df.iterrows():
                row_text = " | ".join(cell.strip() for cell in row)
                full_text += row_text + "\n"

        return full_text.strip() or "No readable data found in Excel file."

    except Exception as e:
        return f"Failed to parse Excel file: {e}"
    
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

 