import asyncio
import os
from dotenv import load_dotenv
from agents import AgentManager

load_dotenv()

async def test_brave_search():
    """Test Brave Search functionality specifically"""
    
    # Check if OPENAI_API_KEY exists
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment")
        return
    
    print("Testing Brave Search with Web Crawler Agent...")
    print("=" * 50)
    
    agent_manager = AgentManager()
    
    # Test queries specifically for Brave Search
    test_queries = [
        "Use Brave Search to find the best movies of 2024",
        "Search for recent news about artificial intelligence using Brave Search",
        "Find information about Python programming tutorials using Brave Search",
        "Search for the latest Tesla stock price and news using Brave Search",
        "Use Brave Search to find restaurants in New York City"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing: {query}")
        print("-" * 40)
        
        try:
            # Get the web_crawler agent specifically
            agent_info = await agent_manager.get_agent('web_crawler')
            agent = agent_info["agent"]
            
            # Create a more detailed prompt that explicitly requests tool usage
            detailed_prompt = f"""
            You have access to Brave Search and other web tools. 
            
            User request: {query}
            
            IMPORTANT: You MUST use your available tools, specifically Brave Search, to fulfill this request. 
            Do not respond with generic information or say you don't have access. 
            Use the tools available to you to search the web and provide real, current results.
            
            If a tool call fails, show me the error and try alternative approaches.
            """
            
            from camel.messages import BaseMessage
            user_message = BaseMessage.make_user_message(
                role_name="User", 
                content=detailed_prompt
            )
            
            print("Sending request to web_crawler agent...")
            response = await agent.astep(user_message)
            
            if response and hasattr(response, "msgs") and response.msgs:
                full_response = response.msgs[-1].content
                # Show first part of response
                if len(full_response) > 500:
                    print(f"Response: {full_response[:500]}...")
                else:
                    print(f"Response: {full_response}")
            else:
                print("No response received from agent")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("Brave Search test completed!")
    
    try:
        await agent_manager.cleanup()
        print("Cleanup completed successfully!")
    except Exception as e:
        print(f"Cleanup warning: {e}")

if __name__ == "__main__":
    asyncio.run(test_brave_search())