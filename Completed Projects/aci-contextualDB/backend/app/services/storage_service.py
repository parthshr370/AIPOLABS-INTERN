from app.core.supabase_client import supabase
import logging
import re


class StorageService:
    """Service for managing HTML file storage operations in Supabase Storage"""
    
    def __init__(self):
        self.supabase = supabase

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize filename to be storage-safe"""
        if not name:
            return "content.html"
        base = name
        base = re.sub(r"https?://", "", base)
        base = re.sub(r"[^a-zA-Z0-9\s._-]", "-", base)
        base = re.sub(r"[\s/\\]+", "-", base)
        base = re.sub(r"-+", "-", base).strip("-")
        if not base:
            base = "content"
        if len(base) > 80:
            base = base[:80]
        if not base.lower().endswith('.html'):
            base += '.html'
        return base

    def upload_html_file(self, file, user_id: str, file_name: str = None):
        """Upload HTML file to storage and return detailed information"""
        if hasattr(file, 'filename') and hasattr(file, 'file'):
            original_filename = file.filename
            file.file.seek(0)
            file_content = file.file.read()
            file_size = len(file_content)
            
            target_filename = self._sanitize_filename(file_name or original_filename)
            storage_path = f"{user_id}/{target_filename}"
            
            supabase_result = self.supabase.storage.from_('raw_html_contexts').upload(
                path=storage_path,
                file=file_content
            )
            
            # UploadResponse doesn't have error attribute - if we get here, upload succeeded
            # Check if upload was successful by looking for path in response
            if not hasattr(supabase_result, 'path') or not supabase_result.path:
                raise Exception("Storage upload failed: No path returned")
            
            # Return enhanced information for asset creation
            return {
                'original_filename': original_filename,
                'uploaded_filename': target_filename,
                'storage_path': storage_path,
                'storage_bucket': 'raw_html_contexts',
                'file_size': file_size,
                'mime_type': getattr(file, 'content_type', 'text/html')
            }
        else:
            raise ValueError("Invalid file object provided")

    def get_html_file(self, storage_path: str):
        """Download HTML file from storage and return raw bytes.

        Handles different return shapes from the client (bytes, Response-like, or dict).
        """
        logger = logging.getLogger(__name__)
        logger.info(f"Downloading from storage: path={storage_path}")
        result = self.supabase.storage.from_("raw_html_contexts").download(storage_path)

        # Direct bytes
        if isinstance(result, (bytes, bytearray)):
            logger.info(f"Downloaded {len(result)} bytes from storage")
            return bytes(result)

        # Response-like object with .content or .data
        content = None
        try:
            if hasattr(result, 'content') and result.content is not None:
                content = result.content
            elif hasattr(result, 'data') and result.data is not None:
                content = result.data
        except Exception:
            content = None

        if content is not None:
            try:
                size = len(content)
            except Exception:
                size = -1
            logger.info(f"Downloaded response-like content from storage (size={size})")
            return bytes(content)

        # Dict response shape { 'data': bytes, ... }
        if isinstance(result, dict):
            data = result.get('data')
            if isinstance(data, (bytes, bytearray)):
                logger.info(f"Downloaded dict data from storage ({len(data)} bytes)")
                return bytes(data)

        logger.warning("Storage download returned unsupported type; returning empty bytes")
        return b""
    
    def list_user_files(self, user_id: str):
        """List all files for a specific user"""
        return self.supabase.storage.from_("raw_html_contexts").list(path=user_id)
    
    def delete_html_file(self, file_name: str, user_id: str):
        """Delete a file for a specific user"""
        storage_path = f"{user_id}/{file_name}"
        return self.supabase.storage.from_("raw_html_contexts").remove([storage_path])