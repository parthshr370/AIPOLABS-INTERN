# Data cleaning utilities
from typing import Dict, Any, Tuple, Optional
import trafilatura
import logging

logger = logging.getLogger(__name__)

def _filter_metadata(metadata) -> Tuple[Dict[str, Any], int]:
    """
    Filter metadata to keep only specified attributes
    
    Args:
        metadata: Metadata object from trafilatura
        
    Returns:
        Tuple of (filtered_metadata_dict, count_of_extracted_fields)
    """
    extracted_metadata = {}
    count = 0
    if metadata:
        # Only keep specified attributes
        desired_attrs = {'title', 'description', 'tags', 'author', 'sitename'}
        for attr in desired_attrs:
            if hasattr(metadata, attr):
                value = getattr(metadata, attr, None)
                # Skip None values, empty lists, empty dicts, and XML Element objects
                if (value is not None and 
                    value != [] and 
                    value != {} and 
                    not str(type(value)).startswith("<class 'lxml.etree.")):
                    extracted_metadata[attr] = value
                    count += 1
    
    return extracted_metadata, count

class HTMLCleaner:
    """HTML content cleaner using trafilatura"""
    
    def __init__(self):
        self.config = trafilatura.settings.use_config()
        
    def clean(self, html_content: str, url: Optional[str] = None) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
        """
        Clean HTML content and extract metadata
        
        Args:
            html_content: Raw HTML content
            url: Source URL
            
        Returns:
            Tuple of (cleaned_text, metadata)
        """
        if url is not None:
            """
            if url is provided, we will check it and use it to extract metadata, just skip it in V0.
            """  
        else:        
            try:
                # Check if HTML content is a fragment and wrap it if needed
                if not html_content.strip().startswith('<!DOCTYPE') and not html_content.strip().startswith('<html'):
                    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Document</title>
</head>
<body>
{html_content}
</body>
</html>"""
                
                # Extract clean text from html file
                cleaned_text = trafilatura.extract(
                    html_content,
                    output_format="markdown",
                    config=self.config,
                    include_comments=True,
                    include_tables=True,
                    include_links=True,
                    include_images=False
                )
                
                if not cleaned_text:
                    raise ValueError("Failed to extract content from HTML")

                logger.info(f"Successfully cleaned HTML from {url}, extracted {len(cleaned_text)} characters")
                
                # Extract metadata
                metadata = trafilatura.metadata.extract_metadata(html_content)
                logger.info(f"Successfully extracted metadata from {url}")
                
                # Clean and filter metadata
                extracted_metadata, count = _filter_metadata(metadata)
                
                # Add processing stats
                cleaning_stats = {
                    "metadata_count": count,
                    "content_length": len(cleaned_text),
                    "extraction_method": "trafilatura"
                }
                
                return cleaned_text, extracted_metadata, cleaning_stats
                
            except Exception as e:
                logger.error(f"HTML cleaning failed: {str(e)}")
                raise

# Test function
if __name__ == "__main__":
    from pathlib import Path
    import json
    
    def batch_process_html_files():
        """Process all HTML files in html_samples directory"""
        # Get the directory where this script is located
        script_dir = Path(__file__).parent
        input_dir = script_dir / "data" / "html_samples"
        output_text_dir = script_dir / "data" / "html_extract_text"
        output_meta_dir = script_dir / "data" / "html_extract_meta"
        output_text_dir.mkdir(parents=True, exist_ok=True)
        output_meta_dir.mkdir(parents=True, exist_ok=True)
        
        # Get all HTML files
        html_files = list(input_dir.glob("*.html"))
        
        if not html_files:
            print("No HTML files found in html_samples directory")
            return
        
        cleaner = HTMLCleaner()
        processed_count = 0
        failed_count = 0
        
        print(f"Found {len(html_files)} HTML files to process")
        print("=" * 80)
        
        for html_file in html_files:
            try:
                print(f"\nProcessing: {html_file.name}")
                
                # Read HTML file
                with open(html_file, "r", encoding="utf-8") as f:
                    html_content = f.read()
                
                # Clean HTML
                cleaned_text, metadata, cleaning_stats = cleaner.clean(html_content)
                
                # Generate output filename for extracted text
                output_text_file = output_text_dir / f"{html_file.stem}.txt"
                
                # Save extracted text
                with open(output_text_file, "w", encoding="utf-8") as f:
                    f.write(cleaned_text)
                
                print(f"  ✅ Saved to: {output_text_file}")
                print(f"  📏 Text length: {len(cleaned_text)} characters")
                
                # Generate output filename for extracted metadata
                output_meta_file = output_meta_dir / f"{html_file.stem}.txt"

                # Save extracted metadata
                with open(output_meta_file, "w", encoding="utf-8") as f:
                    f.write(json.dumps(metadata, indent=4))
                
                print(f"  ✅ Saved to: {output_meta_file}")
                print(f"  📏 Metadata length: {len(metadata)} characters")

                # print cleaning stats
                print(f"  📏 Cleaning stats: {cleaning_stats}")
                processed_count += 1        
            except Exception as e:
                print(f"  ❌ Error processing {html_file.name}: {str(e)}")
                failed_count += 1
        
        print("\n" + "=" * 80)
        print(f"Processing complete!")
        print(f"✅ Successfully processed: {processed_count} files")
        print(f"❌ Failed: {failed_count} files")
        print(f"📁 Output directory: {output_text_dir}")
        print(f"📁 Output metadata directory: {output_meta_dir}")
    
    batch_process_html_files()