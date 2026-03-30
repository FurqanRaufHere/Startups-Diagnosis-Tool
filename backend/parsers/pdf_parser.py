import fitz  # pymupdf
from pathlib import Path


def parse_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    pages = []
    for page in doc:
        text = page.get_text("text")
        if text.strip():
            pages.append(text.strip())
    doc.close()

    full_text = "\n\n".join(pages)

    # Truncate to ~12k chars to stay within Llama context
    if len(full_text) > 12000:
        full_text = full_text[:12000] + "\n\n[TRUNCATED]"

    return full_text