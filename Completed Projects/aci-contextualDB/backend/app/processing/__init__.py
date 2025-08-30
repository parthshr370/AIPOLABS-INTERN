"""
Processing Package - HTML Content Processing Pipeline

This package provides a complete pipeline for processing HTML content:
1. Clean HTML and extract metadata (HTMLCleaner)
2. Split content into chunks (TextChunker)
3. Generate vector embeddings (TextEmbedder)

Main entry point: ProcessingPipeline
"""

# Core pipeline components
from .pipeline import ProcessingPipeline, ProcessingInput, ProcessingResult, SourceType
from .cleaners import HTMLCleaner
from .chunkers import TextChunker
from .embedders import TextEmbedder

# Version information
__version__ = "0.1.0"
__author__ = "Your Project"
__description__ = "HTML content processing pipeline with vector storage"

# Define public API
__all__ = [
    # Core pipeline
    "ProcessingPipeline",
    "ProcessingInput", 
    "ProcessingResult",
    "SourceType",
    
    # Individual components
    "HTMLCleaner",
    "TextChunker",
    "TextEmbedder",
    
    # Metadata
    "__version__",
]

# Convenience imports for common usage patterns
def create_pipeline():
    """Create a new processing pipeline with default configuration"""
    return ProcessingPipeline()

def create_cleaner():
    """Create a new HTML cleaner"""
    return HTMLCleaner()

def create_chunker(chunk_size: int = 2000, chunk_overlap: int = 300):
    """Create a new text chunker with specified parameters"""
    return TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

def create_embedder(model_name: str = "text-embedding-3-small"):
    """Create a new text embedder with specified model"""
    return TextEmbedder(model_name=model_name)


# Add convenience functions to __all__
__all__.extend([
    "create_pipeline",
    "create_cleaner", 
    "create_chunker",
    "create_embedder"
])