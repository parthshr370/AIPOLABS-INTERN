#!/usr/bin/env python3
"""
Test script for IngestionService

This script tests the complete ingestion workflow using sample HTML files.
"""

import asyncio
import sys
import logging
from pathlib import Path
from typing import BinaryIO
import uuid

# Add the parent directory to the path to import from app
sys.path.append(str(Path(__file__).parent.parent))

from app.services.ingestion_service import IngestionService
from app.core.supabase_client import supabase


class MockUploadFile:
    """Mock file upload object to simulate FastAPI UploadFile"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.filename = file_path.name
        self.content_type = "text/html"
        
    @property
    def file(self) -> BinaryIO:
        """Return file-like object"""
        return open(self.file_path, 'rb')


async def test_single_file(ingestion_service: IngestionService, file_path: Path, user_id: str):
    """Test ingestion of a single HTML file"""
    print(f"\n📄 Testing: {file_path.name}")
    print("-" * 60)
    
    try:
        # Create mock upload file
        mock_file = MockUploadFile(file_path)
        
        # Test ingestion
        result = await ingestion_service.ingest_html_content(
            contenthtml=mock_file,
            user_id=user_id,
            file_name=None  # Use original filename
        )
        
        if result["success"]:
            print(f"✅ Successfully ingested: {file_path.name}")
            print(f"   📝 Context ID: {result['context_id']}")
            print(f"   📊 Chunks: {result['chunks_count']}")
            print(f"   🏷️  Metadata: {result['metadata_count']}")
            
            # Test status retrieval
            status = ingestion_service.get_ingestion_status(result["context_id"])
            print(f"   📈 Status: {status['status']}")
            
            if status.get('error'):
                print(f"   ⚠️  Error: {status['error']}")
                
        else:
            print(f"❌ Failed to ingest: {file_path.name}")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            
        return result["success"] if result else False
        
    except Exception as e:
        print(f"❌ Exception during ingestion of {file_path.name}: {str(e)}")
        return False
    finally:
        # Clean up file handle
        try:
            mock_file.file.close()
        except:
            pass


async def test_user_contexts(ingestion_service: IngestionService, user_id: str):
    """Test retrieval of all contexts for a user"""
    print(f"\n📋 Testing user contexts retrieval for user: {user_id}")
    print("-" * 60)
    
    try:
        contexts = ingestion_service.get_user_contexts(user_id)
        print(f"✅ Found {len(contexts)} contexts for user")
        
        for i, context in enumerate(contexts[:3]):  # Show first 3
            print(f"   {i+1}. Context {context.get('id', 'N/A')[:8]}... - Status: {context.get('processing_status', 'unknown')}")
            
        if len(contexts) > 3:
            print(f"   ... and {len(contexts) - 3} more contexts")
            
        return True
        
    except Exception as e:
        print(f"❌ Exception during context retrieval: {str(e)}")
        return False


async def get_test_user() -> str:
    """Get the specified test user ID"""
    # Use the specified user ID
    test_user_id = "6890cf8d-7699-4eb8-a06e-391209b89ade"
    print(f"🧪 Using specified test user ID: {test_user_id}")
    return test_user_id


async def main():
    """Main test function"""
    print("🚀 IngestionService Test Script")
    print("=" * 60)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize service
    ingestion_service = IngestionService()
    
    # Get test user ID
    test_user_id = await get_test_user()
    
    # Find input files
    script_dir = Path(__file__).parent
    input_dir = script_dir.parent / "app" / "processing" / "test_end_to_end" / "input"
    
    if not input_dir.exists():
        print(f"❌ Input directory not found: {input_dir}")
        return False
    
    html_files = list(input_dir.glob("*.html"))
    
    if not html_files:
        print(f"❌ No HTML files found in: {input_dir}")
        return False
    
    print(f"📁 Found {len(html_files)} HTML files in: {input_dir}")
    
    # Test each file (limit to first 2 for demo)
    successful_count = 0
    failed_count = 0
    test_files = html_files[:2]  # Test first 2 files
    
    print(f"\n🎯 Testing {len(test_files)} files:")
    
    for html_file in test_files:
        success = await test_single_file(ingestion_service, html_file, test_user_id)
        if success:
            successful_count += 1
        else:
            failed_count += 1
    
    # Test user contexts retrieval
    await test_user_contexts(ingestion_service, test_user_id)
    
    # Summary
    print(f"\n📊 Test Summary:")
    print("-" * 60)
    print(f"✅ Successful ingestions: {successful_count}")
    print(f"❌ Failed ingestions: {failed_count}")
    print(f"🎯 Total tested: {len(test_files)}")
    
    if failed_count == 0:
        print(f"\n🎉 All tests passed!")
        return True
    else:
        print(f"\n⚠️  Some tests failed. Check logs for details.")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Test script failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Usage:
# cd backend
# source .venv/bin/activate  # or activate your virtual environment
# python scripts/test_ingestion_service.py