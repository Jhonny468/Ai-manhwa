from pathlib import Path
from pypdf import PdfReader
from docx import Document

SUPPORTED = {".txt", ".pdf", ".docx"}

def extract_text(path: str) -> str:
    file = Path(path)
    suffix = file.suffix.lower()
    if suffix == ".txt":
        return file.read_text(encoding="utf-8", errors="replace")
    if suffix == ".pdf":
        reader = PdfReader(str(file))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)
    if suffix == ".docx":
        doc = Document(str(file))
        return "\n".join(p.text for p in doc.paragraphs)
    raise ValueError("Unsupported file type. Use TXT, PDF or DOCX.")
