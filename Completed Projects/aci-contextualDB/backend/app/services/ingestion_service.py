import json
import logging
from typing import Optional
from app.processing import ProcessingPipeline, ProcessingInput
from app.services.storage_service import StorageService
from app.services.context_repository import ContextRepository, ChunkRepository, MetadataRepository
from app.services.asset_repository import AssetRepository

logger = logging.getLogger(__name__)


class IngestionService:
    """Service for handling content ingestion, processing, and storage"""
    
    def __init__(self):
        self.storage_service = StorageService()
        self.context_repo = ContextRepository()
        self.chunk_repo = ChunkRepository()
        self.metadata_repo = MetadataRepository()
        self.asset_repo = AssetRepository()
        self.processing_pipeline = ProcessingPipeline()
    
    async def ingest_html_content(self, 
                                contenthtml, 
                                user_id: str, 
                                file_name: Optional[str] = None) -> dict:
        """
        Complete ingestion workflow: upload, process, and store content
        
        Args:
            contenthtml: HTML file upload object
            user_id: User ID for context ownership
            file_name: Optional custom filename
            
        Returns:
            Dict with ingestion results and context information
        """
        context_id = None
        try:
            # Extract the actual filename used
            actual_filename = file_name or contenthtml.filename
            
            # Create initial context entry with pending status
            logger.info(f"Creating context entry for user {user_id} with pending status")
            initial_context_data = {
                "user_id": user_id,
                "source": "html",
                "processing_status": "pending"
            }
            context_result = self.context_repo.create_context(initial_context_data)
            
            # PostgREST APIResponse doesn't have error attribute - check for data instead
            if not hasattr(context_result, 'data') or not context_result.data:
                logger.error("Failed to create initial context entry: No data returned")
                raise Exception("Failed to create initial context entry: No data returned")
                
            context_id = context_result.data[0]['id']
            
            # 1. Upload raw HTML to storage
            logger.info(f"Uploading HTML file for user {user_id}")
            upload_result = self.storage_service.upload_html_file(
                contenthtml, user_id, file_name
            )
            logger.info("File uploaded successfully to storage")
            
            # Update status to processing after successful upload
            logger.info("Updating status to processing after file upload")
            processing_update_result = self.context_repo.update_context(context_id, {"processing_status": "processing"})
            if not hasattr(processing_update_result, 'data'):
                logger.error("Failed to update status to processing after upload: No response data")
                raise Exception("Failed to update status to processing after upload: No response data")
            
            # 2. Create asset record using upload result information
            logger.info("Creating asset record with upload information")
            asset_data = {
                "user_id": user_id,
                "context_id": context_id,
                "storage_bucket": upload_result['storage_bucket'],
                "storage_path": upload_result['storage_path'],
                "original_filename": upload_result['original_filename'],
                "uploaded_filename": upload_result['uploaded_filename'],
                "mime_type": upload_result['mime_type'],
                "size_bytes": upload_result['file_size']
            }
            
            asset_result = self.asset_repo.create_asset(asset_data)
            if not hasattr(asset_result, 'data') or not asset_result.data:
                logger.error("Failed to create asset record: No data returned")
                raise Exception("Failed to create asset record: No data returned")
            
            # Use the uploaded filename for subsequent operations
            actual_filename = upload_result['uploaded_filename']
            
            # 3. Retrieve and decode HTML content
            html_bytes = self.storage_service.get_html_file(upload_result['storage_path'])
            html_content = html_bytes.decode('utf-8')
            
            # 4. Process content through pipeline
            logger.info("Processing HTML content through pipeline")
            input_data = ProcessingInput(html_content=html_content)
            processing_result = await self.processing_pipeline.process(input_data)
            
            # 5. Store processing results in database
            logger.info("Storing processing results in database")
            await self._store_processing_results(processing_result, context_id)
            
            # Update status to success after successful completion
            logger.info("Updating status to success")
            success_update_result = self.context_repo.update_context(context_id, {
                "processing_status": "success",
                "chunks_count": getattr(processing_result, 'chunks_count', len(processing_result.chunks) if processing_result.chunks else 0),
                "metadata_count": getattr(processing_result, 'metadata_count', len(processing_result.metadata) if processing_result.metadata else 0)
            })
            if not hasattr(success_update_result, 'data'):
                logger.error("Failed to update context with success status: No response data")
                # Even if status update fails, processing was successful, so don't raise exception
            
            logger.info(f"Successfully ingested content with context_id: {context_id}")
            return {
                "success": True,
                "context_id": context_id,
                "chunks_count": processing_result.chunks_count,
                "metadata_count": processing_result.metadata_count,
            }
            
        except Exception as e:
            logger.error(f"Error in content ingestion: {str(e)}")
            # Update context status to failed if context was created
            if context_id:
                try:
                    final_update_result = self.context_repo.update_context(context_id, {
                        "processing_status": "failed",
                        "error": str(e)
                    })
                    if not hasattr(final_update_result, 'data'):
                        logger.error("Failed to update context status to failed: No response data")
                except Exception as update_error:
                    logger.error(f"Exception while updating context status: {str(update_error)}")
            raise
    
    async def _store_processing_results(self, processing_result, context_id: str):
        """Store processing results in database tables"""
        
        # 1. Create chunks if available
        if processing_result.chunks:
            chunks_data = []
            embeddings = processing_result.chunks_embeddings or []
            
            for i, chunk in enumerate(processing_result.chunks):
                chunk_data = {
                    "context_id": context_id,
                    "chunk_index": i,
                    "content": chunk,
                    "embedding": embeddings[i] if i < len(embeddings) else None
                }
                chunks_data.append(chunk_data)
            
            if chunks_data:
                chunks_result = self.chunk_repo.create_chunks(chunks_data)
                if not chunks_result.data:
                    logger.warning("Failed to create some chunk entries")
        
        # 2. Create single metadata entry if available (schema enforces UNIQUE constraint on context_id)
        if processing_result.metadata:
            metadata_embeddings = processing_result.metadata_embeddings or []
            
            # Convert metadata dict to readable text content
            metadata_content = json.dumps(processing_result.metadata, ensure_ascii=False, indent=2)
            
            metadata_data = {
                "context_id": context_id,
                "content": metadata_content,
                "metadata_json": processing_result.metadata,
                "embedding": metadata_embeddings[0] if metadata_embeddings else None
            }
            
            metadata_result = self.metadata_repo.create_metadata(metadata_data)
            if not hasattr(metadata_result, 'data') or not metadata_result.data:
                logger.error("Failed to create metadata entry: No data returned")
                raise Exception("Failed to create metadata entry: No data returned")
        
        return True
    
    def get_ingestion_status(self, context_id: str) -> dict:
        """Get the status of an ingestion operation"""
        context_result = self.context_repo.get_context_by_id(context_id)
        if not context_result.data:
            return {"error": "Context not found"}
            
        context = context_result.data[0]
        return {
            "context_id": context_id,
            "status": context.get('processing_status', 'unknown'),
            "chunks_count": context.get('chunks_count', 0),
            "metadata_count": context.get('metadata_count', 0),
            "error": context.get('error') if context.get('processing_status') == 'failed' else None,
            "created_at": context.get('created_at')
        }
    
    def get_user_contexts(self, user_id: str) -> list:
        """Get all contexts for a user"""
        result = self.context_repo.get_all_contexts(user_id)
        return result.data if result.data else []