# Text chunking utilities
from typing import List, Dict, Any, Optional, Tuple
import logging
import re

logger = logging.getLogger(__name__)

class TextChunker:
    """Text chunking utility for breaking down content into manageable pieces"""
    
    def __init__(self, 
                 chunk_size: int = 2000,
                 chunk_overlap: int = 300,
                 min_chunk_size: int = 100):
        """
        Initialize chunker with configuration
        
        Args:
            chunk_size: Target size for each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
            min_chunk_size: Minimum chunk size to avoid tiny fragments
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        
    def _find_table_boundaries(self, text: str) -> List[tuple]:
        """
        Find table start and end positions in markdown text
        
        Returns:
            List of (start, end) tuples for table boundaries
        """
        table_boundaries = []
        lines = text.split('\n')
        table_start = None
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Check if this is a valid table row
            is_table_row = False
            if line_stripped.startswith('|') and line_stripped.endswith('|'):
                # Count pipe characters to ensure it's a proper table row
                pipe_count = line_stripped.count('|')
                if pipe_count >= 3:  # At least |col1|col2| format
                    is_table_row = True
            elif line_stripped.startswith('|') and '|' in line_stripped[1:]:
                # Handle cases where line doesn't end with | but has multiple |
                pipe_count = line_stripped.count('|')
                if pipe_count >= 2:  # At least |col1|col2 format
                    is_table_row = True
            elif '|' in line_stripped and not line_stripped.startswith('|'):
                # Handle table rows that don't start with | (some markdown formats)
                parts = line_stripped.split('|')
                if len(parts) >= 3 and any(part.strip() for part in parts):
                    is_table_row = True
            
            # Check for table header separator (|---|---|)
            if re.match(r'^\s*\|[\s\-\|:]+\|\s*$', line_stripped):
                is_table_row = True
            
            if is_table_row:
                if table_start is None:
                    table_start = i
            else:
                # Not a table row - but check if it's just an empty line within a table
                if table_start is not None and line_stripped == '':
                    # Empty line - could be within table, continue
                    continue
                elif table_start is not None and line_stripped == '|':
                    # Single pipe - likely table continuation, continue
                    continue
                elif table_start is not None:
                    # End of table found
                    table_end = i - 1
                    # Skip back over any trailing empty lines or single pipes
                    while table_end >= table_start and (lines[table_end].strip() == '' or lines[table_end].strip() == '|'):
                        table_end -= 1
                    
                    if table_end >= table_start:
                        # Convert line numbers to character positions
                        start_pos = sum(len(lines[j]) + 1 for j in range(table_start))
                        end_pos = sum(len(lines[j]) + 1 for j in range(table_end + 1))
                        table_boundaries.append((start_pos, end_pos))
                    table_start = None
        
        # Handle case where text ends with a table
        if table_start is not None:
            table_end = len(lines) - 1
            # Skip back over any trailing empty lines or single pipes
            while table_end >= table_start and (lines[table_end].strip() == '' or lines[table_end].strip() == '|'):
                table_end -= 1
            
            if table_end >= table_start:
                start_pos = sum(len(lines[j]) + 1 for j in range(table_start))
                end_pos = sum(len(lines[j]) + 1 for j in range(table_end + 1))
                table_boundaries.append((start_pos, end_pos))
        
        return table_boundaries
    
    def _get_chunk_stats(self, chunks: List[str]) -> Dict[str, Any]:
        """Get statistics about chunks"""
        if not chunks:
            return {"count": 0, "total_length": 0, "avg_length": 0}
        
        total_length = sum(len(chunk) for chunk in chunks)
        return {
            "count": len(chunks),
            "total_length": total_length,
            "avg_length": total_length // len(chunks),
            "min_length": min(len(chunk) for chunk in chunks),
            "max_length": max(len(chunk) for chunk in chunks)
        }

    def chunk(self, text: str) -> Tuple[List[str], Dict[str, Any]]:
        """
        Split text into chunks
        
        Args:
            text: Text content to chunk
            
        Returns:
            List of text chunks
        """
        try:
            if not text or len(text) < self.min_chunk_size:
                logger.warning(f"Text too short for chunking: {len(text) if text else 0} characters")
                return [text] if text else []
            
            # Find table boundaries
            table_boundaries = self._find_table_boundaries(text)
            
            chunks = []
            start = 0
            
            while start < len(text):
                # Check if current position is inside a table
                in_table = False
                table_start = None
                table_end = None
                
                for tb_start, tb_end in table_boundaries:
                    if start >= tb_start and start < tb_end:
                        in_table = True
                        table_start = tb_start
                        table_end = tb_end
                        break
                
                if in_table:
                    # Include the entire table as one chunk
                    table_chunk = text[table_start:table_end].strip()
                    if table_chunk:
                        chunks.append(table_chunk)
                    start = table_end
                    continue
                
                # Check if chunk would cross into a table
                end = start + self.chunk_size
                chunk_crosses_table = False
                
                for tb_start, tb_end in table_boundaries:
                    if start < tb_start and end > tb_start:
                        # Chunk would cross into table, stop before table
                        end = tb_start
                        chunk_crosses_table = True
                        break
                
                if end >= len(text):
                    # Last chunk
                    final_chunk = text[start:].strip()
                    if final_chunk:
                        chunks.append(final_chunk)
                    break
                
                # Find good breaking point (sentence boundary)
                chunk_text = text[start:end]
                
                # Try to break at sentence end
                sentence_breaks = ['.', '!', '?', '\n\n']
                best_break = -1
                
                if not chunk_crosses_table:  # Only look for sentence breaks if not crossing table
                    for i in range(len(chunk_text) - 1, -1, -1):
                        if chunk_text[i] in sentence_breaks:
                            # Check if there's enough content after the break
                            if i > self.min_chunk_size:
                                best_break = i + 1
                                break
                
                if best_break > 0:
                    chunk_text = text[start:start + best_break].strip()
                    if chunk_text:  # Only add non-empty chunks
                        chunks.append(chunk_text)
                    start = start + best_break - self.chunk_overlap
                else:
                    # No good break found or crossing table, use end position
                    chunk_text = text[start:end].strip()
                    if chunk_text:  # Only add non-empty chunks
                        chunks.append(chunk_text)
                    if chunk_crosses_table:
                        start = end  # No overlap when approaching table
                    else:
                        start = end - self.chunk_overlap
                
                # Ensure we're making progress
                if start <= 0:
                    start = end
            
            # Filter out chunks that are too small (already stripped above)
            filtered_chunks = [chunk for chunk in chunks if len(chunk) >= self.min_chunk_size]
            
            logger.info(f"Successfully chunked text into {len(filtered_chunks)} pieces")
            return filtered_chunks, self._get_chunk_stats(filtered_chunks)
            
        except Exception as e:
            logger.error(f"Text chunking failed: {str(e)}")
            raise
    
if __name__ == "__main__":
    import json
    from pathlib import Path
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    def batch_process_html_text_files():
        """Process all files in html_extract_text directory and save chunks to chunks directory"""                
        # Get script directory and construct absolute paths
        script_dir = Path(__file__).parent
        html_extract_text_dir = script_dir / "data" / "html_extract_text"
        chunks_dir = script_dir / "data" / "chunks"
        
        # Ensure chunks directory exists
        chunks_dir.mkdir(parents=True, exist_ok=True)
        
        if not html_extract_text_dir.exists():
            logger.error(f"Directory {html_extract_text_dir} does not exist")
            return
        
        chunker = TextChunker()
        
        # Process all .txt files in the html_extract_text directory
        for file_path in html_extract_text_dir.glob("*.txt"):
            try:
                logger.info(f"Processing {file_path.name}")
                
                # Read the text file
                with open(file_path, "r", encoding="utf-8") as f:
                    text_content = f.read()
                
                if not text_content.strip():
                    logger.warning(f"File {file_path.name} is empty, skipping")
                    continue
                
                # Chunk the text
                chunks, chunk_stats = chunker.chunk(text_content)
                
                if not chunks:
                    logger.warning(f"No chunks created for {file_path.name}")
                    continue
                
                # Prepare output data
                output_data = {
                    "source_file": file_path.name,
                    "original_length": len(text_content),
                    "chunk_stats": chunk_stats,
                    "chunks": chunks
                }
                
                # Save chunks to JSON file
                output_file = chunks_dir / f"{file_path.stem}.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(output_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Saved {len(chunks)} chunks to {output_file.name}")
                
            except Exception as e:
                logger.error(f"Error processing {file_path.name}: {str(e)}")
        
        logger.info("Finished processing all HTML text files")
    
    batch_process_html_text_files()