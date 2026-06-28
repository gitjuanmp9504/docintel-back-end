-- ============================================
-- DocIntel - Database schema
-- Postgres + pgvector
-- ============================================

-- Enable the pgvector extension (once per database)
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable gen_random_uuid() 
CREATE EXTENSION IF NOT EXISTS pgcrypto;


-- ============================================
-- TABLE 1: documents
-- Metadata for each uploaded PDF (not the file itself)
-- ============================================
CREATE TABLE documents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename        VARCHAR(255) NOT NULL,
    storage_path    VARCHAR(500) NOT NULL,
    page_count      INTEGER,
    status          VARCHAR(20) NOT NULL DEFAULT 'processing',
    uploaded_at     TIMESTAMP NOT NULL DEFAULT now()
);


-- ============================================
-- TABLE 2: document_chunks
-- Text fragments + their embedding (the "search index")
-- ============================================
CREATE TABLE document_chunks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text      TEXT NOT NULL,
    page            INTEGER,
    chunk_index     INTEGER NOT NULL,
    embedding       VECTOR(1536) NOT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT now()
);

-- Index for fast vector similarity search
CREATE INDEX ON document_chunks
    USING hnsw (embedding vector_cosine_ops);

-- Regular index for filtering by document
CREATE INDEX idx_chunks_document_id ON document_chunks(document_id);


-- ============================================
-- TABLE 3: conversations
-- 1 conversation = 1 document (design decision)
-- ============================================
CREATE TABLE conversations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title           VARCHAR(255),
    document_id     UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    created_at      TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_conversations_document_id ON conversations(document_id);


-- ============================================
-- TABLE 4: messages
-- Each user question and Claude's response
-- ============================================
CREATE TABLE messages (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id     UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role                VARCHAR(20) NOT NULL,
    content             TEXT NOT NULL,
    citations           JSONB,
    created_at          TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);