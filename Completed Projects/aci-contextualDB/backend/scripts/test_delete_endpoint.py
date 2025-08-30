#!/usr/bin/env python3
"""
Test script for the DELETE /context endpoint
"""

import sys
import os
import asyncio

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.context_repository import ContextRepository


async def test_delete_endpoint(context_id: str, user_id: str):
    """Test the DELETE /context endpoint functionality"""
    print("=" * 60)
    print("Testing DELETE /context endpoint")
    print("=" * 60)
    
    try:
        context_repo = ContextRepository()
        
        print(f"Context ID: {context_id}")
        print(f"User ID: {user_id}")
        print("-" * 40)
        
        # Check if context exists before deletion
        print("🔍 Checking if context exists...")
        context_result = context_repo.get_context_by_id(context_id)
        
        if not context_result.data:
            print("❌ Context not found (would return 404)")
            return
        
        context = context_result.data[0]
        print(f"✅ Context found: {context.get('id')}")
        
        # Check user ownership
        if context.get('user_id') != user_id:
            print("❌ Access denied - context belongs to different user (would return 403)")
            print(f"   Context owner: {context.get('user_id')}")
            print(f"   Requested by: {user_id}")
            return
        
        print("✅ User authorized to delete context")
        
        # Perform deletion
        print("🗑️  Deleting context...")
        delete_result = context_repo.delete_context(context_id)
        
        if not delete_result.data:
            print("❌ Failed to delete context (would return 500)")
            return
        
        print("✅ Context deleted successfully")
        
        # Verify deletion
        print("🔍 Verifying deletion...")
        verify_result = context_repo.get_context_by_id(context_id)
        
        if verify_result.data:
            print("❌ Context still exists after deletion")
        else:
            print("✅ Context successfully removed from database")
        
        print("\n🎉 DELETE endpoint test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    context_id = "21d004ca-d127-404a-83f6-d07225dbaa19"
    user_id = "6890cf8d-7699-4eb8-a06e-391209b89ade"
    
    await test_delete_endpoint(context_id, user_id)


if __name__ == "__main__":
    asyncio.run(main())