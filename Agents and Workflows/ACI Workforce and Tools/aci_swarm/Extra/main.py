import asyncio
import os
import sys
from dotenv import load_dotenv
from orchestrator import SimpleOrchestrator

load_dotenv()

async def main():
    """Simple main interface"""
    try:
        print("ACI Agent Swarm - Intent-Based Orchestrator")
        print("=" * 50)
        
        # Check for required environment variable
        if not os.getenv("OPENAI_API_KEY"):
            print("Error: OPENAI_API_KEY not found in environment")
            return
        
        # Initialize orchestrator
        orchestrator = SimpleOrchestrator()
        
        print("Ready! Enter your queries (type 'exit' to quit)")
        print("-" * 50)
        
        while True:
            try:
                # Get user input with explicit flushing
                sys.stdout.write("\nQuery: ")
                sys.stdout.flush()
                user_query = sys.stdin.readline().strip()
                
                if user_query.lower() in ['exit', 'quit', 'bye']:
                    print("Goodbye!")
                    break
                
                if not user_query:
                    continue
                
                print("Processing...")
                
                # Process through orchestrator
                result = await orchestrator.process_query(user_query)
                
                # Display result
                print(f"\nAgent: {result.get('selected_agent', 'unknown')}")
                print(f"Response: {result.get('agent_response', 'No response')}")
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except EOFError:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
        
        # Cleanup
        await orchestrator.cleanup()
        
    except Exception as e:
        print(f"Startup error: {e}")
        print("Make sure you've run 'python create_configs.py' first")

if __name__ == "__main__":
    asyncio.run(main())