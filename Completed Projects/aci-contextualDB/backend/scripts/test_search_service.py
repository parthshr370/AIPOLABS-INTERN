#!/usr/bin/env python3
"""
Test script for SearchService
Similar to the test function in retrieval.py but using the new SearchService
"""

import sys
import os
import asyncio

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.search_service import SearchService


async def test_search_service():
    """Test the SearchService semantic search functionality"""
    print("=" * 60)
    print("Testing SearchService.semantic_search()")
    print("=" * 60)
    
    try:
        # Initialize the search service
        search_service = SearchService()
        print("✅ SearchService initialized successfully")
        
        # Test parameters
        test_query = "How to start a project with supabase?"
        test_user_id = "6890cf8d-7699-4eb8-a06e-391209b89ade"
        top_k = 5
        similarity_threshold = 0.3
        
        print(f"\nTest Parameters:")
        print(f"  Query: '{test_query}'")
        print(f"  User ID: {test_user_id}")
        print(f"  Top K: {top_k}")
        print(f"  Similarity Threshold: {similarity_threshold}")
        print("\n" + "-" * 40)
        
        # Perform semantic search
        print("🔍 Performing semantic search...")
        results = await search_service.semantic_search(
            query=test_query,
            user_id=test_user_id,
            top_k=top_k,
            similarity_threshold=similarity_threshold
        )
        
        # Display results
        print(f"\n✅ Search completed successfully!")
        print(f"📊 Found {len(results)} contexts:")
        
        if not results:
            print("⚠️  No results found. This could mean:")
            print("   - No contexts exist for this user")
            print("   - No contexts meet the similarity threshold")
            print("   - Database connection issues")
            print("   - Embedding generation failed")
        else:
            print("\n" + "=" * 60)
            for i, ctx in enumerate(results, 1):
                print(f"\n🎯 Result #{i}")
                print(f"   Context ID: {ctx['context_id'][:8]}...")
                print(f"   Asset ID: {ctx['asset_id'][:8] if ctx['asset_id'] else 'None'}...")
                print(f"   Relevance Score: {ctx.get('relevance_score', 0):.4f}")
                print(f"   Max Chunk Similarity: {ctx.get('max_chunk_similarity', 0):.4f}")
                print(f"   Avg Chunk Similarity: {ctx.get('avg_chunk_similarity', 0):.4f}")
                print(f"   Metadata Similarity: {ctx.get('metadata_similarity', 0):.4f}")
                print(f"   Matching Chunks: {ctx.get('matching_chunks_count', 0)}")
                print(f"   Has Metadata Match: {ctx.get('has_metadata_match', False)}")
        
        print("\n" + "=" * 60)
        print("🎉 Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error:")
        print(f"   Error Type: {type(e).__name__}")
        print(f"   Error Message: {str(e)}")
        
        # Print more detailed error info for debugging
        import traceback
        print(f"\n📋 Full Traceback:")
        traceback.print_exc()


async def test_different_queries():
    """Test with different types of queries"""
    print("\n" + "=" * 60)
    print("Testing with Different Query Types")
    print("=" * 60)
    
    search_service = SearchService()
    test_user_id = "6890cf8d-7699-4eb8-a06e-391209b89ade"
    
    test_queries = [
        "How to start a project with supabase?",
        "How to build a web search engine with neural embeddings?", 
        "What are text embeddings and how do they work?",
        "How to set up local development environment with CLI?",
        "Research on African language models and cultural alignment",
        "Donald Trump meeting with European leaders and security talks"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        try:
            results = await search_service.semantic_search(
                query=query,
                user_id=test_user_id,
                top_k=3,
                similarity_threshold=0.25
            )
            print(f"   Found {len(results)} results")
            if results:
                best_score = max(r.get('relevance_score', 0) for r in results)
                print(f"   Best relevance score: {best_score:.4f}")
        except Exception as e:
            print(f"   ❌ Failed: {str(e)}")


async def main():
    """Main test function"""
    print("🚀 Starting SearchService Tests")
    print("=" * 60)
    
    # Test basic functionality
    await test_search_service()
    
    # Test with different queries
    await test_different_queries()
    
    print("\n🏁 All tests completed!")


if __name__ == "__main__":
    # Run the async test
    asyncio.run(main())