from app.core.supabase_client import supabase


class AssetRepository:
    """Repository for context_assets related database operations"""
    
    def __init__(self):
        self.supabase = supabase
    
    def create_asset(self, asset_data: dict):
        """Create a new context asset entry"""
        return self.supabase.table("context_assets").insert(asset_data).execute()
    
    def get_asset_by_context_id(self, context_id: str):
        """Get asset for a specific context"""
        return self.supabase.table("context_assets").select("*").eq("context_id", context_id).execute()
    
    def get_asset_by_id(self, asset_id: str):
        """Get a specific asset by ID"""
        return self.supabase.table("context_assets").select("*").eq("id", asset_id).execute()
    
    def get_asset_by_storage_path(self, storage_bucket: str, storage_path: str):
        """Get asset by storage bucket and path"""
        return self.supabase.table("context_assets").select("*")\
            .eq("storage_bucket", storage_bucket)\
            .eq("storage_path", storage_path)\
            .execute()
    
    def get_assets_by_user(self, user_id: str):
        """Get all assets for a specific user"""
        return self.supabase.table("context_assets").select("*").eq("user_id", user_id).execute()
    
    def update_asset(self, asset_id: str, updates: dict):
        """Update asset fields"""
        return self.supabase.table("context_assets").update(updates).eq("id", asset_id).execute()
    
    def update_asset_by_context(self, context_id: str, updates: dict):
        """Update asset by context_id"""
        return self.supabase.table("context_assets").update(updates).eq("context_id", context_id).execute()
    
    def delete_asset(self, asset_id: str):
        """Delete a specific asset"""
        return self.supabase.table("context_assets").delete().eq("id", asset_id).execute()
    
    def delete_asset_by_context(self, context_id: str):
        """Delete asset for a specific context"""
        return self.supabase.table("context_assets").delete().eq("context_id", context_id).execute()