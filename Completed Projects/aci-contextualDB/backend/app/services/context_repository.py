from app.core.supabase_client import supabase


class ContextRepository:
    """Repository for context-related database operations"""
    
    def __init__(self):
        self.supabase = supabase
    
    def get_context_by_id(self, context_id: str):
        """Get a specific context by ID"""
        return self.supabase.table("contexts").select("*").eq("id", context_id).execute()
    
    def get_all_contexts(self, user_id: str = None):
        """Get all contexts, optionally filtered by user_id"""
        query = self.supabase.table("contexts").select("*")
        if user_id:
            query = query.eq("user_id", user_id)
        return query.execute()
    
    def create_context(self, context: dict):
        """Create a new context entry"""
        return self.supabase.table("contexts").insert(context).execute()
    
    def delete_context(self, context_id: str):
        """Delete a context and all related chunks and metadata (CASCADE)"""
        return self.supabase.table("contexts").delete().eq("id", context_id).execute()
    
    def update_context(self, context_id: str, updates: dict):
        """Update context fields like success status, error message, etc."""
        updates['updated_at'] = 'NOW()'
        return self.supabase.table("contexts").update(updates).eq("id", context_id).execute()


class ChunkRepository:
    """Repository for chunk-related database operations"""
    
    def __init__(self):
        self.supabase = supabase
    
    def create_chunks(self, chunks: list):
        """Create multiple chunks for a context"""
        return self.supabase.table("context_chunks").insert(chunks).execute()
    
    def get_chunks_by_context(self, context_id: str):
        """Get all chunks for a specific context"""
        return self.supabase.table("context_chunks").select("*").eq("context_id", context_id).order("chunk_index").execute()
        
    def delete_chunks_by_context(self, context_id: str):
        """Delete all chunks for a specific context"""
        return self.supabase.table("context_chunks").delete().eq("context_id", context_id).execute()


class MetadataRepository:
    """Repository for metadata-related database operations"""
    
    def __init__(self):
        self.supabase = supabase
    
    def create_metadata(self, metadata: dict):
        """Create metadata entry for a context"""
        return self.supabase.table("context_metadata").insert(metadata).execute()
    
    def get_metadata_by_context(self, context_id: str):
        """Get metadata for a specific context"""
        return self.supabase.table("context_metadata").select("*").eq("context_id", context_id).execute()
        
    def delete_metadata_by_context(self, context_id: str):
        """Delete metadata for a specific context"""
        return self.supabase.table("context_metadata").delete().eq("context_id", context_id).execute()