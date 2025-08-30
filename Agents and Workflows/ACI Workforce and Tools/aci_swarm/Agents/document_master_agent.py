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

warnings.filterwarnings("ignore")
load_dotenv()


async def main():
    mcp_toolkit = MCPToolkit(config_path="configs/config_document_master.json")
    await mcp_toolkit.connect()
    tools = mcp_toolkit.get_tools()

    model = ModelFactory.create(
        model_platform=ModelPlatformType.GEMINI,
        model_type="gemini-2.5-pro-preview-06-05",
        api_key=os.getenv("GOOGLE_API_KEY"),
        model_config_dict={"temperature": 0.7, "max_tokens": 40000},
    )

    system_message = BaseMessage.make_assistant_message(
        role_name="Documentation Expert",
        content="You are a documentation expert. Use Google Docs and Coda tools to create, edit, and manage documents.",
    )

    agent = ChatAgent(model=model, system_message=system_message, tools=tools)

    rprint(f"Ready! (document_master agent) - {len(tools)} tools loaded")

    try:
        while True:
            user_input = input("\n📄 You: ").strip()
            if user_input.lower() in ["exit", "quit", "bye"]:
                break

            user_message = BaseMessage.make_user_message(role_name="User", content=user_input)
            rprint("Working...")
            response = await agent.astep(user_message)

            if response and response.msgs:
                for msg in response.msgs:
                    rprint(msg.content)
                rprint(f"\n--- RAW ---\n{response}\n--- END ---")
            else:
                rprint("No response")

    except KeyboardInterrupt:
        pass
    finally:
        await mcp_toolkit.disconnect()


if __name__ == "__main__":
    asyncio.run(main()) 