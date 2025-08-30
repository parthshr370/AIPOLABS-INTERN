# Vector operations and storage utilities
from typing import List, Dict, Any, Optional, Tuple
import logging
import uuid

logger = logging.getLogger(__name__)

class VectorOperations:
    """Vector database operations for storing and retrieving embeddings"""
    
    def __init__(self, connection_config: Optional[Dict[str, Any]] = None):
        """
        Initialize vector operations
        
        Args:
            connection_config: Database connection configuration
        """
        self.connection_config = connection_config or {}
        self.table_name = "contexts"
        
    async def store_embeddings(self, 
                             chunks: List[str], 
                             embeddings: List[List[float]], 
                             metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store text chunks and their embeddings in the vector database
        
        Args:
            chunks: List of text chunks
            embeddings: Corresponding embedding vectors
            metadata: Metadata about the content
            
        Returns:
            Storage result with IDs and status
        """
        try:
            if len(chunks) != len(embeddings):
                raise ValueError(f"Chunks count ({len(chunks)}) doesn't match embeddings count ({len(embeddings)})")
            
            logger.info(f"Storing {len(chunks)} chunks with embeddings")
            
            # TODO: Implement actual database storage
            # This is a placeholder implementation
            stored_ids = []
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_id = str(uuid.uuid4())
                
                # Mock storage operation
                # In real implementation, this would insert into Supabase
                record = {
                    "id": chunk_id,
                    "content": chunk,
                    "embedding": embedding,
                    "url": metadata.get("url"),
                    "title": metadata.get("title"),
                    "user_id": metadata.get("user_id"),
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    **{k: v for k, v in metadata.items() if k not in ["url", "title", "user_id"]}
                }
                
                stored_ids.append(chunk_id)
                logger.debug(f"Stored chunk {i+1}/{len(chunks)} with ID {chunk_id}")
            
            result = {
                "success": True,
                "ids": stored_ids,
                "stored_count": len(stored_ids),
                "table": self.table_name
            }
            
            logger.info(f"Successfully stored {len(stored_ids)} chunks")
            return result
            
        except Exception as e:
            logger.error(f"Vector storage failed: {str(e)}")
            raise
    
    async def search_similar(self, 
                           query_embedding: List[float], 
                           limit: int = 5,
                           similarity_threshold: float = 0.7,
                           user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for similar content using vector similarity
        
        Args:
            query_embedding: Query vector
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            user_id: Filter by user ID if provided
            
        Returns:
            List of similar content with scores
        """
        try:
            logger.info(f"Searching for similar content (limit: {limit}, threshold: {similarity_threshold})")
            
            # TODO: Implement actual vector similarity search
            # This is a placeholder that returns mock results
            
            mock_results = [
                {
                    "id": str(uuid.uuid4()),
                    "content": "This is a mock search result matching your query",
                    "similarity_score": 0.85,
                    "url": "https://example.com/page1",
                    "title": "Example Page 1",
                    "metadata": {"chunk_index": 0}
                },
                {
                    "id": str(uuid.uuid4()),
                    "content": "Another relevant piece of content from your database",
                    "similarity_score": 0.78,
                    "url": "https://example.com/page2", 
                    "title": "Example Page 2",
                    "metadata": {"chunk_index": 1}
                }
            ]
            
            # Filter by user_id if provided
            if user_id:
                mock_results = [r for r in mock_results if r.get("user_id") == user_id]
            
            # Filter by similarity threshold
            filtered_results = [r for r in mock_results if r["similarity_score"] >= similarity_threshold]
            
            # Limit results
            limited_results = filtered_results[:limit]
            
            logger.info(f"Found {len(limited_results)} similar results")
            return limited_results
            
        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            raise
    
    def calculate_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Similarity score between 0 and 1
        """
        import math
        
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have the same dimension")
        
        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # Calculate magnitudes
        mag1 = math.sqrt(sum(a * a for a in vec1))
        mag2 = math.sqrt(sum(b * b for b in vec2))
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        # Calculate cosine similarity
        similarity = dot_product / (mag1 * mag2)
        
        # Normalize to [0, 1] range
        return (similarity + 1) / 2

# Test function
if __name__ == "__main__":
    import asyncio
    
    async def test():
        # Mock data for testing
        chunks = ["First chunk of text", "Second chunk of content"]
        embeddings = [[0.1, 0.2, 0.3] * 512, [0.2, 0.3, 0.4] * 512]  # Mock embeddings
        metadata = {
            "url": "https://example.com",
            "title": "Test Page",
            "user_id": "test-user"
        }
        
        vector_ops = VectorOperations()
        
        # Test storage
        storage_result = await vector_ops.store_embeddings(chunks, embeddings, metadata)
        print(f"Storage result: {storage_result}")
        
        # Test search
        query_embedding = [0.15, 0.25, 0.35] * 512  # Mock query embedding
        search_results = await vector_ops.search_similar(query_embedding, limit=3)
        print(f"Search results: {len(search_results)} items")
        
        # Test similarity calculation
        similarity = vector_ops.calculate_similarity(embeddings[0][:10], query_embedding[:10])
        print(f"Similarity score: {similarity}")
    
    asyncio.run(test())