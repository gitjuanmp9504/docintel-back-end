from db.connection import get_pool
import uuid
import os
from services.chunking import extract_text_by_page, chunk_text
from services.embeddings import get_embedding, get_embeddings_batch


UPLOAD_DIR = "./uploads"

async def create_document(filename: str, file_bytes: bytes) -> dict:
    pool = get_pool()
    
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    #save file in local filesystem for the moment
    storage_path = f"{UPLOAD_DIR}/{uuid.uuid4()}_{filename}"
    with open(storage_path, "wb") as f:
        f.write(file_bytes)
    
    query = """
        INSERT INTO documents (filename, storage_path, status)
        VALUES ($1, $2, 'processing')
        RETURNING id, filename, status
    """
    row = await pool.fetchrow(query, filename, storage_path)
    document = dict(row)

    await process_document(document["id"], file_bytes)

    return document

async def process_document(document_id, file_bytes: bytes):
    pool = get_pool()

    pages = extract_text_by_page(file_bytes)
    
    all_chunks: list[str] = []
    chunk_pages: list[int] = []

    for page_number, page_text in pages:
        chunks = chunk_text(page_text)
        all_chunks.extend(chunks)
        chunk_pages.extend([page_number] * len(chunks))

    embeddings = await get_embeddings_batch(all_chunks)

    for index, (chunk, page, embedding) in enumerate(zip(all_chunks, chunk_pages, embeddings)):
        await pool.execute(
            """
            INSERT INTO document_chunks (document_id, chunk_text, page, chunk_index, embedding)
            VALUES ($1, $2, $3, $4, $5)
            """,
            document_id, chunk, page, index, embedding
        )

    await pool.execute(
        """
        UPDATE documents
        SET status = 'ready', page_count = $2
        WHERE id = $1
        """,
        document_id, len(pages)
    )

async def list_documents() -> list[dict]:
    pool = get_pool()
    query = """
        SELECT id, filename, page_count, status, uploaded_at
        FROM documents
        ORDER BY uploaded_at DESC
    """
    rows = await pool.fetch(query)
    return [dict(row) for row in rows]