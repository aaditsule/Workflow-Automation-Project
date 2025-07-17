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
        all_text = ""

        for sheet in xl.sheet_names:
            df = xl.parse(sheet, header=None)  # no header initially

            # Drop fully empty rows
            df.dropna(how='all', inplace=True)

            if df.empty:
                continue

            # Attempt to identify the first non-empty header row (assumes 2D structure)
            header_row_idx = None
            for i, row in df.iterrows():
                if row.notna().sum() >= 2:  # at least 2 non-NaNs to consider as header
                    header_row_idx = i
                    break

            if header_row_idx is not None:
                df.columns = df.iloc[header_row_idx]
                df = df.iloc[header_row_idx + 1:]

            # Clean up: drop mostly empty columns
            df.dropna(axis=1, thresh=2, inplace=True)

            # Convert to text
            preview = df.head(10).fillna("").astype(str).to_string(index=False)

            all_text += f"\n\n--- Sheet: {sheet} ---\n"
            all_text += "Columns: " + ", ".join(df.columns.astype(str)) + "\n"
            all_text += "\nSample Data:\n" + preview

        if not all_text.strip():
            return "No meaningful data found in the Excel file."

        return all_text

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

 