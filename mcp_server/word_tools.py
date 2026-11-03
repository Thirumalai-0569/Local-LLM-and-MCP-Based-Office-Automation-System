from pathlib import Path
from docx import Document

def word_read(file_path):
    path = Path(file_path)
    if not path.is_file():
        return f"File not found: {path}"
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

def word_create(title, content, output_path="output/word/mcp_created.docx"):
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = Document()
    doc.add_heading(title or "Office Document", level=1)
    for line in (content or "").splitlines():
        doc.add_paragraph(line)
    doc.save(path)
    return f"Created Word document: {path.resolve()}"
