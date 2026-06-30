from pypdf import PdfReader
import io


def extract_text_by_page(file_bytes: bytes) -> list[tuple[int, str]]:
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text.strip():  
            pages.append((i + 1, text))  
    return pages


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap  
    return chunks