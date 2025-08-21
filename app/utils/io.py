
from pypdf import PdfReader
from docx import Document
from io import BytesIO

def save_to_file(filename: str, content: str):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def load_from_file(filename: str) -> str:
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def pdf_to_text(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def docx_to_text(file_bytes: bytes) -> str:
    doc = Document(BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs)

def any_to_text(filename: str, file_bytes: bytes) -> str:
    fn = filename.lower()
    if fn.endswith(".pdf"):
        return pdf_to_text(file_bytes)
    if fn.endswith(".docx"):
        return docx_to_text(file_bytes)
    # txt / autres
    try:
        return file_bytes.decode("utf-8")
    except Exception:
        return file_bytes.decode("latin-1", errors="ignore")
