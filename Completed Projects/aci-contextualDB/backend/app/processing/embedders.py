# Text embedding utilities
from typing import List
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class TextEmbedder:
    """Text embedding utility for generating vector representations"""
    
    def __init__(self, 
                 model_name: str = "text-embedding-3-small",
                 max_tokens: int = 8000,
                 batch_size: int = 100):
        """
        Initialize embedder with configuration
        
        Args:
            model_name: Embedding model to use
            max_tokens: Maximum tokens per text chunk
            batch_size: Number of chunks to process in each batch
        """
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.batch_size = batch_size
        self.client = OpenAI()
        
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for text chunks using OpenAI API
        
        Args:
            texts: List of text chunks to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            if not texts:
                logger.warning("No texts provided for embedding")
                return []
            
            logger.info(f"Generating embeddings for {len(texts)} text chunks using {self.model_name}")
            
            embeddings = []
            
            # Process in batches to avoid API limits
            for i in range(0, len(texts), self.batch_size):
                batch = texts[i:i + self.batch_size]
                logger.info(f"Processing batch {i//self.batch_size + 1}/{(len(texts) + self.batch_size - 1)//self.batch_size}")
                
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.model_name
                )
                
                # Extract embeddings from response
                batch_embeddings = [data.embedding for data in response.data]
                embeddings.extend(batch_embeddings)
            
            logger.info(f"Successfully generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise
    
    

# Test and batch processing
if __name__ == "__main__":
    import json
    import asyncio
    from pathlib import Path
    
    async def test():
        """Simple test"""
        embedder = TextEmbedder(batch_size=2)
        texts = ["Hello world", "This is a test", "Another text chunk"]
        
        embeddings = await embedder.embed(texts)
        print(f"texts: {texts}")
        print(f"Generated {len(embeddings)} embeddings")
        print(f"Dimension: {len(embeddings[0]) if embeddings else 0}")
    
    async def process_directory():
        """Process chunks directory"""
        script_dir = Path(__file__).parent
        chunks_dir = script_dir / "data" / "chunks"
        meta_dir = script_dir / "data" / "html_extract_meta"
        output_dir = script_dir / "data" / "embeddings"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        embedder = TextEmbedder(batch_size=50)
        
        for chunk_file in chunks_dir.glob("*.json"):
            try:
                with open(chunk_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract texts from different formats
                texts = []
                if 'chunks' in data:
                    texts = data['chunks']
                else:
                    texts = None
                
                embeddings = await embedder.embed(texts)
                meta_file = meta_dir / f"{chunk_file.stem}.txt"
                with open(meta_file, 'r', encoding='utf-8') as f:
                    metadata = json.dumps(json.loads(f.read()), separators=(',', ':'), ensure_ascii=False)
                
                # Generate embedding for metadata
                metadata_embedding = await embedder.embed([metadata.strip()]) if metadata.strip() else []
                    
                output_data = {
                    "source": chunk_file.name,
                    "model": embedder.model_name,
                    "embeddings": embeddings,
                    "metadata": metadata,
                    "metadata_embedding": metadata_embedding[0] if metadata_embedding else None
                }
                
                output_file = output_dir / f"{chunk_file.stem}.json"
                with open(output_file, 'w') as f:
                    json.dump(output_data, f)
                
                print(f"Processed {chunk_file.name} -> {len(embeddings)} embeddings with metadata")
                    
            except Exception as e:
                print(f"Error processing {chunk_file.name}: {e}")
    
    # Run test
    asyncio.run(test())
    print("\n" + "="*30 + "\n")
    
    # Run batch processing
    asyncio.run(process_directory())