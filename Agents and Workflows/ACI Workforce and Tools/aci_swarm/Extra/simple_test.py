import asyncio
import os
from dotenv import load_dotenv
from orchestrator import SimpleOrchestrator

load_dotenv()

async def simple_test():
    """Simple test with minimal queries to avoid context length issues"""
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found")
        return
    
    print("🎯 Simple ACI Agent Test")
    print("=" * 30)
    
    orchestrator = SimpleOrchestrator()
    
    # Simple test queries
    simple_queries = [
        "Bitcoin price",
        "Hello world", 
        "Logo design"
    ]
    
    for i, query in enumerate(simple_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 20)
        
        try:
            result = await orchestrator.process_query(query)
            print(f"Agent: {result.get('selected_agent', 'unknown')}")
            response = result.get('agent_response', 'No response')
            # Show first 100 chars only
            if len(response) > 100:
                response = response[:100] + "..."
            print(f"Response: {response}")
            
        except Exception as e:
            print(f"Error: {e}")
    
    await orchestrator.cleanup()
    print("\n✅ Simple test completed!")

if __name__ == "__main__":
    asyncio.run(simple_test())