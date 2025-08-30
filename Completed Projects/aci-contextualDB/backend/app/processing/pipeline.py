# Processing pipeline module
import json
import logging
from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from .cleaners import HTMLCleaner
from .chunkers import TextChunker
from .embedders import TextEmbedder

logger = logging.getLogger(__name__)

class SourceType(Enum):
      URL = "url"
      HTML = "html"

@dataclass
class ProcessingResult:
    """Result of the processing pipeline"""
    success: bool
    source: SourceType
    chunks: List[str]
    chunks_embeddings: List[List[float]]
    chunks_count: int
    metadata: Dict[str, Any]
    metadata_embeddings: List[List[float]]
    metadata_count: int
    error: Optional[str] = None

@dataclass
class ProcessingInput:
    """Input for the processing pipeline"""
    html_content: str
    url: Optional[str] = None

class ProcessingPipeline:
    """Main processing pipeline orchestrator"""
    
    def __init__(self):
        self.cleaner = HTMLCleaner()
        self.chunker = TextChunker()
        self.embedder = TextEmbedder()
        
    async def process(self, input_data: ProcessingInput) -> ProcessingResult:
        """
        Process HTML content through the complete pipeline
        
        Args:
            input_data: ProcessingInput containing HTML and metadata
            
        Returns:
            ProcessingResult with chunks, embeddings, and metadata
            
        Raises:
            Exception: If any stage of processing fails
        """
        # Stage 1: Clean HTML file: extract metadata and clean text
        logger.info("Starting HTML cleaning stage")
        cleaned_text, extracted_metadata, cleaning_stats = self.cleaner.clean(
            html_content=input_data.html_content,
            url=input_data.url
        )
        
        # Stage 2: Chunk the cleaned text
        logger.info("Starting text chunking stage")
        chunks, chunks_stats = self.chunker.chunk(
            text=cleaned_text
        )
        
        # Stage 3: Generate embeddings for chunks
        logger.info("Starting embedding generation stage")
        chunks_embeddings = await self.embedder.embed(chunks)
        
        # Convert metadata dict to text for embedding
        metadata_text = json.dumps(extracted_metadata, ensure_ascii=False, separators=(',', ':'))
        metadata_embeddings = await self.embedder.embed([metadata_text]) if metadata_text.strip() else []

        
        logger.info(f"Pipeline completed successfully. Generated {len(chunks)} chunks")
        
        return ProcessingResult(
            success=True,
            chunks=chunks,
            chunks_embeddings=chunks_embeddings,
            chunks_count=chunks_stats["count"],
            metadata=extracted_metadata,
            metadata_embeddings=metadata_embeddings,
            metadata_count=cleaning_stats["metadata_count"],
            source=SourceType.HTML
        )
