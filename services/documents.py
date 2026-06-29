from db.connection import get_pool
import uuid
import os

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
    return dict(row)

async def list_documents() -> list[dict]:
    pool = get_pool()
    query = """
        SELECT id, filename, page_count, status, uploaded_at
        FROM documents
        ORDER BY uploaded_at DESC
    """
    rows = await pool.fetch(query)
    return [dict(row) for row in rows]