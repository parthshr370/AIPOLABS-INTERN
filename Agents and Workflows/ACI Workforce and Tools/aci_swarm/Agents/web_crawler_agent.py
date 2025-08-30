import asyncio
import os
import warnings
from dotenv import load_dotenv
from rich import print as rprint

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.toolkits import MCPToolkit
from camel.types import ModelPlatformType

# Suppress all warnings
warnings.filterwarnings("ignore")

load_dotenv()


async def main():
    # Initialize MCP toolkit
    mcp_toolkit = MCPToolkit(config_path="configs/config_web_crawler.json")
    await mcp_toolkit.connect()
    tools = mcp_toolkit.get_tools()

    # Create model
    model = ModelFactory.create(
        model_platform=ModelPlatformType.GEMINI,
        model_type="gemini-2.5-pro-preview-06-05",
        api_key=os.getenv("GOOGLE_API_KEY"),
        model_config_dict={"temperature": 0.7, "max_tokens": 40000},
    )

    # Create agent with minimal system message
    system_message = BaseMessage.make_assistant_message(
        role_name="user",
        content="You are a helpful assistant. Use the available tools to help users with web searches, scraping, and automation tasks.",
    )

    agent = ChatAgent(model=model, system_message=system_message, tools=tools)

    rprint(f"Ready! ({len(tools)} tools)")

    try:
        while True:
            user_input = input("\n🌐 You: ").strip()
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                break

            user_message = BaseMessage.make_user_message(role_name="human", content=user_input)
            
            rprint("Working...")
            response = await agent.astep(user_message)

            if response and response.msgs:
                for msg in response.msgs:
                    rprint(f"{msg.content}")
                
                # Always show raw response
                rprint(f"\n--- RAW ---\n{response}\n--- END ---")
            else:
                rprint("No response")

    except KeyboardInterrupt:
        pass

    finally:
        await mcp_toolkit.disconnect()


if __name__ == "__main__":
    asyncio.run(main())