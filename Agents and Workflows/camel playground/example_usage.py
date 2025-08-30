#!/usr/bin/env python3
"""
Example usage of CAMEL AI integration.
This script demonstrates how to create and use CAMEL AI agents programmatically.
"""

import os
from dotenv import load_dotenv
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.types import ModelType, ModelPlatformType
from camel.models import ModelFactory
from camel.configs import ChatGPTConfig

# Load environment variables
load_dotenv()

def create_simple_agent():
    """Create a simple CAMEL AI agent."""
    
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.")
        return None
    
    try:
        # Create model instance
        model = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type="gpt-4.1-mini",  # Using latest balanced model
            model_config_dict=ChatGPTConfig(temperature=0.7, max_tokens=1000).as_dict(),
            api_key=api_key
        )
        
        # Create system message
        system_message = BaseMessage.make_assistant_message(
            role_name="Python Expert",
            content="You are a helpful Python programming expert. You provide clear, concise, and practical Python code examples and explanations."
        )
        
        # Create agent
        agent = ChatAgent(system_message=system_message, model=model)
        
        print("✅ Agent created successfully!")
        return agent
        
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        return None

def chat_with_agent(agent, message):
    """Send a message to the agent and get a response."""
    
    try:
        # Create user message
        user_msg = BaseMessage.make_user_message(role_name="User", content=message)
        
        # Get response from agent
        response = agent.step(user_msg)
        
        if response and hasattr(response, 'msg') and response.msg:
            return response.msg.content
        else:
            return "No response received from agent."
            
    except Exception as e:
        return f"Error getting response: {e}"

def main():
    """Main function demonstrating CAMEL AI usage."""
    
    print("🐫 CAMEL AI Integration Example")
    print("=" * 40)
    
    # Create agent
    agent = create_simple_agent()
    if not agent:
        return
    
    # Example conversations
    examples = [
        "Write a simple Python function to calculate the factorial of a number.",
        "How do I read a CSV file using pandas?",
        "What's the difference between a list and a tuple in Python?",
        "Show me how to create a simple web scraper with requests and BeautifulSoup."
    ]
    
    print("\n🤖 Starting conversation with Python Expert agent...\n")
    
    for i, question in enumerate(examples, 1):
        print(f"👤 Question {i}: {question}")
        print("🤖 Agent Response:")
        
        response = chat_with_agent(agent, question)
        print(response)
        print("-" * 60)
    
    print("\n✨ Example completed! You can now use this pattern in your own applications.")

if __name__ == "__main__":
    main() 