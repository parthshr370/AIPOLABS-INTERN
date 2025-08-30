#!/usr/bin/env python3
"""
Test script for StorageService
Tests HTML file upload, download, list, and delete operations using test files
"""

import sys
import os
import asyncio
from io import BytesIO
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.storage_service import StorageService


class MockUploadFile:
    """Mock UploadFile object for testing"""
    def __init__(self, content: bytes, filename: str):
        self.filename = filename
        self.file = BytesIO(content)
        self.content_type = "text/html"


def get_test_files():
    """Get test HTML files from the test_end_to_end/input directory"""
    input_dir = Path(__file__).parent.parent / "app" / "processing" / "test_end_to_end" / "input"
    
    if not input_dir.exists():
        print(f"❌ Test input directory not found: {input_dir}")
        return []
    
    html_files = list(input_dir.glob("*.html"))
    print(f"📁 Found {len(html_files)} test HTML files")
    
    return html_files


def test_storage_service():
    """Test the StorageService operations"""
    print("🚀 StorageService Tests")
    
    try:
        # Initialize the storage service
        storage_service = StorageService()
        print("✅ StorageService initialized")
        
        # Test parameters
        test_user_id = "6890cf8d-7699-4eb8-a06e-391209b89ade"
        
        # Get test files
        test_files = get_test_files()
        if not test_files:
            print("❌ No test files found")
            return
        
        # Use the first few files for testing
        files_to_test = test_files[:3]
        uploaded_files = []
        
        print(f"\n📤 Testing file uploads...")
        
        # Test file uploads
        for file_path in files_to_test:
            try:
                print(f"📄 Testing: {file_path.name}")
                
                # Read the file content
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                
                # Create mock upload file
                mock_file = MockUploadFile(file_content, file_path.name)
                
                # Upload the file
                result = storage_service.upload_html_file(
                    file=mock_file,
                    user_id=test_user_id,
                    file_name=file_path.name
                )
                
                # Check if upload was successful
                # Supabase storage returns different structures, but no exception means success
                if result is not None:
                    print(f"   ✅ Uploaded successfully")
                    uploaded_files.append(file_path.name)
                    # Show some details if available
                    if hasattr(result, 'data') and result.data:
                        print(f"      Details: {result.data}")
                else:
                    print(f"   ⚠️  Upload returned None")
                
            except Exception as e:
                print(f"   ❌ Upload failed: {str(e)}")
        
        print(f"\n📋 Testing file listing...")
        
        # Test file listing
        try:
            file_list = storage_service.list_user_files(test_user_id)
            
            # Handle different return types from Supabase storage
            files_data = None
            if isinstance(file_list, list):
                files_data = file_list
            elif hasattr(file_list, 'data'):
                files_data = file_list.data
            
            if files_data and len(files_data) > 0:
                print(f"   ✅ Found {len(files_data)} files")
                for file_info in files_data[:3]:  # Show first 3 files
                    if isinstance(file_info, dict):
                        name = file_info.get('name', 'Unknown')
                        # Get size from metadata
                        size = file_info.get('metadata', {}).get('size', 0)
                        created_at = file_info.get('created_at', 'N/A')
                        # Convert bytes to KB/MB for readability
                        if size > 1024 * 1024:
                            size_str = f"{size / (1024*1024):.1f} MB"
                        elif size > 1024:
                            size_str = f"{size / 1024:.1f} KB"
                        else:
                            size_str = f"{size} bytes"
                        print(f"      - {name} ({size_str}) - {created_at}")
                    else:
                        print(f"      - {file_info}")
            else:
                print("   ⚠️  No files found")
                if hasattr(file_list, 'error'):
                    print(f"      Error: {file_list.error}")
        except Exception as e:
            print(f"   ❌ Listing failed: {str(e)}")
        
        print(f"\n📥 Testing file downloads...")
        
        # Test file downloads
        for filename in uploaded_files[:2]:  # Test first 2 uploaded files
            try:
                print(f"📄 Downloading: {filename}")
                
                # Sanitize filename (same logic as StorageService)
                sanitized_name = storage_service._sanitize_filename(filename)
                
                # Download the file
                file_content = storage_service.get_html_file(sanitized_name, test_user_id)
                
                if file_content and len(file_content) > 0:
                    content_size = len(file_content)
                    content_preview = file_content[:100].decode('utf-8', errors='ignore')
                    print(f"   ✅ Downloaded {content_size} bytes")
                    print(f"   Preview: {content_preview[:50]}...")
                else:
                    print(f"   ⚠️  Download returned empty content")
                
            except Exception as e:
                print(f"   ❌ Download failed: {str(e)}")
        
        print(f"\n🗑️  Testing file deletion...")
        
        # Test file deletion
        for filename in uploaded_files[:1]:  # Delete first uploaded file
            try:
                print(f"🗑️  Deleting: {filename}")
                
                # Sanitize filename
                sanitized_name = storage_service._sanitize_filename(filename)
                
                # Delete the file
                result = storage_service.delete_html_file(sanitized_name, test_user_id)
                
                # Check deletion result - no exception means success
                if result is not None:
                    print(f"   ✅ Deleted successfully")
                    if hasattr(result, 'data') and result.data:
                        print(f"      Details: {result.data}")
                else:
                    print(f"   ⚠️  Deletion returned None")
                
            except Exception as e:
                print(f"   ❌ Deletion failed: {str(e)}")
        
        print(f"\n🧪 Testing filename sanitization...")
        
        # Test filename sanitization
        test_filenames = [
            "https://example.com/file.html",
            "file with spaces.html",
            "file/with\\slashes.html",
            "file@#$%with&*special()chars.html",
            "very-long-filename-that-exceeds-the-normal-length-limit-and-should-be-truncated-properly.html",
            ""
        ]
        
        for original_name in test_filenames:
            sanitized = storage_service._sanitize_filename(original_name)
            print(f"   '{original_name}' → '{sanitized}'")
        
        print("\n🎉 Tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")


def test_error_conditions():
    """Test error conditions and edge cases"""
    print("\n🔍 Testing Error Conditions")
    
    storage_service = StorageService()
    test_user_id = "test-user-errors"
    
    # Test invalid file object
    try:
        print("🧪 Testing invalid file object...")
        result = storage_service.upload_html_file("not a file", test_user_id, "test.html")
        print("   ⚠️  Expected error but got success")
    except ValueError as e:
        print(f"   ✅ Caught expected error: {str(e)}")
    except Exception as e:
        print(f"   ⚠️  Caught unexpected error: {str(e)}")
    
    # Test downloading non-existent file
    try:
        print("🧪 Testing non-existent file download...")
        result = storage_service.get_html_file("nonexistent.html", test_user_id)
        print("   ⚠️  Expected error but got success")
    except Exception as e:
        print(f"   ✅ Caught expected error: {type(e).__name__}")


def main():
    """Main test function"""
    # Test basic functionality
    test_storage_service()
    
    # Test error conditions
    test_error_conditions()
    
    print("\n🏁 All tests completed!")


if __name__ == "__main__":
    main()