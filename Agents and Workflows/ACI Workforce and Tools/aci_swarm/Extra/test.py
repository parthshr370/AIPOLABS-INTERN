import asyncio
import os
from dotenv import load_dotenv
from orchestrator import SimpleOrchestrator

load_dotenv()

async def test_agents():
    """Test script to verify agents work"""
    
    # Check if OPENAI_API_KEY exists
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment")
        return
    
    print("Testing ACI Agent Swarm...")
    print("=" * 40)
    
    orchestrator = SimpleOrchestrator()
    
    # Test queries for different agents
    test_queries = [
        "What's the current Bitcoin price?",  # Should route to crypto
        "Find research papers about AI",      # Should route to researcher  
        "Create a logo design",              # Should route to visual_alchemist
        "Search for restaurants in London",  # Should route to search_genius
        "Deploy my React app",               # Should route to code_ninja
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing: {query}")
        print("-" * 30)
        
        try:
            result = await orchestrator.process_query(query)
            print(f"Agent: {result.get('selected_agent', 'unknown')}")
            response = result.get('agent_response', 'No response')
            # Truncate long responses
            if len(response) > 200:
                response = response[:200] + "..."
            print(f"Response: {response}")
            
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 40)
    print("Test completed!")
    
    # Allow a moment for any ongoing operations to complete
    await asyncio.sleep(1)
    
    try:
        await orchestrator.cleanup()
        print("Cleanup completed successfully!")
    except Exception as e:
        print(f"Cleanup warning: {e}")

if __name__ == "__main__":
    asyncio.run(test_agents())