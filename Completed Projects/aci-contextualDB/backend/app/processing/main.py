import asyncio
import json
import logging
import sys
from pathlib import Path
from .pipeline import ProcessingPipeline, ProcessingInput

# Logger for this module (no global configuration)
logger = logging.getLogger(__name__)

async def process_single_file(pipeline: ProcessingPipeline, input_file: Path, output_dir: Path) -> bool:
    """Process a single HTML file and save result as JSON"""
    print(f"📄 Processing: {input_file.name}")
    
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            html_content = f.read()
    except Exception as e:
        print(f"❌ Failed to read {input_file.name}: {e}")
        return False

    # Create processing input
    input_data = ProcessingInput(html_content=html_content)
    
    # Generate output filename (same name but with .json extension)
    output_file = output_dir / f"{input_file.stem}.json"
    
    try:
        # Process the file
        result = await pipeline.process(input_data)
        
        # Convert ProcessingResult to dictionary for JSON serialization
        result_data = {
            "source_file": input_file.name,
            "success": result.success,
            "source": result.source.value if result.source else None,
            "chunks": result.chunks,
            "chunks_embeddings": result.chunks_embeddings,
            "chunks_count": result.chunks_count,
            "metadata": result.metadata,
            "metadata_embeddings": result.metadata_embeddings,
            "metadata_count": result.metadata_count,
            "error": None
        }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {input_file.name} → {output_file.name}")
        return True
            
    except Exception as e:
        # Handle processing errors
        error_result_data = {
            "source_file": input_file.name,
            "success": False,
            "source": None,
            "chunks": [],
            "chunks_embeddings": [],
            "chunks_count": 0,
            "metadata": {},
            "metadata_embeddings": [],
            "metadata_count": 0,
            "error": str(e)
        }
        
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(error_result_data, f, ensure_ascii=False, indent=2)
            print(f"⚠️  {input_file.name} processed with errors → {output_file.name}")
            print(f"   Error: {str(e)}")
        except Exception as save_error:
            print(f"❌ Failed to save error result for {input_file.name}: {save_error}")
        
        return False

async def batch_process_files() -> bool:
    """Process all HTML files in input directory and save results to output directory"""
    logger.info("Starting batch file processing")
    
    # Setup directories
    base_dir = Path(__file__).parent / "test_end_to_end"
    input_dir = base_dir / "input"
    output_dir = base_dir / "output"
    
    # Create output directory if it doesn't exist, clear if it has content
    if output_dir.exists():
        # Clear existing files in output directory
        existing_files = list(output_dir.glob("*"))
        if existing_files:
            print(f"🧹 Clearing {len(existing_files)} existing file(s) from output directory")
            for file in existing_files:
                try:
                    if file.is_file():
                        file.unlink()
                    elif file.is_dir():
                        import shutil
                        shutil.rmtree(file)
                except Exception as e:
                    print(f"⚠️  Warning: Could not remove {file.name}: {e}")
            print("✅ Output directory cleared")
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if input directory exists
    if not input_dir.exists():
        print(f"❌ Input directory not found: {input_dir}")
        return False
    
    # Find all HTML files in input directory
    html_files = list(input_dir.glob("*.html"))
    
    if not html_files:
        print(f"⚠️  No HTML files found in {input_dir}")
        return True
    
    print(f"🚀 Found {len(html_files)} HTML file(s) to process")
    print(f"📁 Input: {input_dir}")
    print(f"📁 Output: {output_dir}")
    print("-" * 50)
    
    # Initialize processing pipeline
    pipeline = ProcessingPipeline()
    
    # Process files
    successful_count = 0
    failed_count = 0
    
    for html_file in sorted(html_files):
        success = await process_single_file(pipeline, html_file, output_dir)
        if success:
            successful_count += 1
        else:
            failed_count += 1
    
    print("-" * 50)
    print(f"📊 Processing Summary:")
    print(f"   ✅ Successful: {successful_count}")
    print(f"   ❌ Failed: {failed_count}")
    print(f"   📁 Results saved in: {output_dir}")
    
    return failed_count == 0


if __name__ == "__main__":
    # Configure logging only when running as standalone
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the batch processing
    try:
        success = asyncio.run(batch_process_files())
        if success:
            print("🎉 Batch processing completed successfully!")
            sys.exit(0)
        else:
            print("⚠️  Batch processing completed with some failures!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Processing interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Batch processing failed with exception: {e}")
        print(f"❌ Batch processing failed: {e}")
        sys.exit(1)

# cd backend
# source .venv/bin/activate
# uv run --active -m app.processing.main