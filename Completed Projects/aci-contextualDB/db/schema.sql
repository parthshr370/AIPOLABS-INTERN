-- =========================
-- Extensions
-- =========================
CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS vector;    -- for embeddings


-- =========================
-- Helpers (updated_at trigger)
-- =========================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS trigger AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- =========================
-- Main Tables
-- =========================

-- Contexts: basic context entries
DROP TABLE IF EXISTS context_metadata CASCADE;
DROP TABLE IF EXISTS context_chunks CASCADE;
DROP TABLE IF EXISTS contexts CASCADE;
DROP TABLE IF EXISTS context_assets CASCADE;

CREATE TABLE contexts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    source TEXT NOT NULL CHECK (source IN ('html', 'url')),
    processing_status TEXT CHECK (processing_status IN ('pending', 'processing', 'success', 'failed')),
    chunks_count INTEGER DEFAULT 0,
    metadata_count INTEGER DEFAULT 0,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT valid_user_id CHECK (user_id IS NOT NULL)
);

-- Assets: store file object information, bucket/path, optional metadata
CREATE TABLE context_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    context_id UUID REFERENCES contexts(id) ON DELETE CASCADE,
    storage_bucket TEXT NOT NULL,
    storage_path   TEXT NOT NULL,                     -- e.g. '<user_id>/<filename>'

    -- Optional metadata
    original_filename  TEXT,
    uploaded_filename  TEXT,
    mime_type          TEXT,
    size_bytes         BIGINT,
    content_sha256     TEXT,
    source_url         TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT context_assets_object_unique UNIQUE (storage_bucket, storage_path)
);

-- One-to-one: each context can only have one asset
ALTER TABLE context_assets
  ADD CONSTRAINT context_assets_context_unique UNIQUE (context_id);


-- Chunks: text chunk embeddings for high-frequency retrieval
CREATE TABLE context_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    context_id UUID REFERENCES contexts(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(context_id, chunk_index)
);

-- Metadata: supplementary embeddings
CREATE TABLE context_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    context_id UUID REFERENCES contexts(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    metadata_json JSONB,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(context_id)
);


-- =========================
-- Triggers (updated_at)
-- =========================
DROP TRIGGER IF EXISTS trg_contexts_set_updated_at ON contexts;
CREATE TRIGGER trg_contexts_set_updated_at
BEFORE UPDATE ON contexts
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_context_assets_set_updated_at ON context_assets;
CREATE TRIGGER trg_context_assets_set_updated_at
BEFORE UPDATE ON context_assets
FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- =========================
-- Row Level Security (RLS)
-- =========================
ALTER TABLE contexts ENABLE ROW LEVEL SECURITY;
ALTER TABLE context_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE context_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE context_metadata ENABLE ROW LEVEL SECURITY;

-- contexts RLS
DROP POLICY IF EXISTS "Users can insert their own contexts" ON contexts;
CREATE POLICY "Users can insert their own contexts" ON contexts
  FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can view their own contexts" ON contexts;
CREATE POLICY "Users can view their own contexts" ON contexts
  FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update their own contexts" ON contexts;
CREATE POLICY "Users can update their own contexts" ON contexts
  FOR UPDATE USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete their own contexts" ON contexts;
CREATE POLICY "Users can delete their own contexts" ON contexts
  FOR DELETE USING (auth.uid() = user_id);

-- context_assets RLS
DROP POLICY IF EXISTS "Users can insert their own assets" ON context_assets;
CREATE POLICY "Users can insert their own assets" ON context_assets
  FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can view their own assets" ON context_assets;
CREATE POLICY "Users can view their own assets" ON context_assets
  FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update their own assets" ON context_assets;
CREATE POLICY "Users can update their own assets" ON context_assets
  FOR UPDATE USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete their own assets" ON context_assets;
CREATE POLICY "Users can delete their own assets" ON context_assets
  FOR DELETE USING (auth.uid() = user_id);

-- context_chunks RLS
DROP POLICY IF EXISTS "Users can insert their own context chunks" ON context_chunks;
CREATE POLICY "Users can insert their own context chunks" ON context_chunks
  FOR INSERT WITH CHECK (EXISTS (
    SELECT 1 FROM contexts WHERE id = context_id AND user_id = auth.uid()
  ));

DROP POLICY IF EXISTS "Users can view their own context chunks" ON context_chunks;
CREATE POLICY "Users can view their own context chunks" ON context_chunks
  FOR SELECT USING (EXISTS (
    SELECT 1 FROM contexts WHERE id = context_id AND user_id = auth.uid()
  ));

DROP POLICY IF EXISTS "Users can update their own context chunks" ON context_chunks;
CREATE POLICY "Users can update their own context chunks" ON context_chunks
  FOR UPDATE USING (EXISTS (
    SELECT 1 FROM contexts WHERE id = context_id AND user_id = auth.uid()
  ));

DROP POLICY IF EXISTS "Users can delete their own context chunks" ON context_chunks;
CREATE POLICY "Users can delete their own context chunks" ON context_chunks
  FOR DELETE USING (EXISTS (
    SELECT 1 FROM contexts WHERE id = context_id AND user_id = auth.uid()
  ));

-- context_metadata RLS
DROP POLICY IF EXISTS "Users can insert their own context metadata" ON context_metadata;
CREATE POLICY "Users can insert their own context metadata" ON context_metadata
  FOR INSERT WITH CHECK (EXISTS (
    SELECT 1 FROM contexts WHERE id = context_id AND user_id = auth.uid()
  ));

DROP POLICY IF EXISTS "Users can view their own context metadata" ON context_metadata;
CREATE POLICY "Users can view their own context metadata" ON context_metadata
  FOR SELECT USING (EXISTS (
    SELECT 1 FROM contexts WHERE id = context_id AND user_id = auth.uid()
  ));

DROP POLICY IF EXISTS "Users can update their own context metadata" ON context_metadata;
CREATE POLICY "Users can update their own context metadata" ON context_metadata
  FOR UPDATE USING (EXISTS (
    SELECT 1 FROM contexts WHERE id = context_id AND user_id = auth.uid()
  ));

DROP POLICY IF EXISTS "Users can delete their own context metadata" ON context_metadata;
CREATE POLICY "Users can delete their own context metadata" ON context_metadata
  FOR DELETE USING (EXISTS (
    SELECT 1 FROM contexts WHERE id = context_id AND user_id = auth.uid()
  ));


-- =========================
-- Indexes
-- =========================
-- contexts
CREATE INDEX idx_contexts_user_id ON contexts(user_id);

-- context_assets
CREATE INDEX idx_context_assets_user_id ON context_assets(user_id);
CREATE INDEX idx_context_assets_context_id ON context_assets(context_id);
CREATE INDEX idx_context_assets_bucket_path ON context_assets(storage_bucket, storage_path);

-- context_chunks
CREATE INDEX idx_context_chunks_context_id ON context_chunks(context_id);
CREATE INDEX idx_context_chunks_embedding
  ON context_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 1000);

-- context_metadata
CREATE INDEX idx_context_metadata_context_id ON context_metadata(context_id);
CREATE INDEX idx_context_metadata_embedding
  ON context_metadata USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
