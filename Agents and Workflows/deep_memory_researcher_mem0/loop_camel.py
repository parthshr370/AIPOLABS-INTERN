import asyncio
import os
from dotenv import load_dotenv
from rich import print as rprint

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.toolkits import MCPToolkit
from camel.types import ModelPlatformType
from create_config import create_config
from camel.toolkits import ACIToolkit

load_dotenv()


async def main():
    """
    Main function to run the Image Analysis Agent.
    """
    create_config()
    mcp_toolkit = MCPToolkit(config_path="config.json")
    await mcp_toolkit.connect()

    agent_name = "ImageAnalysisAgent"
    system_message_content = (
        "You are a specialized Image Analysis Agent. Your sole purpose is to perform object detection using the `REPLICATE.run` tool. "
        "The user will provide a prompt containing an image URL and what to find in the image. "
        "Your task is to identify the image URL and the query object(s) from the user's text and immediately call the tool. "
        "You must not ask for clarification. If the query object is not perfectly clear, make a reasonable inference. For example, if the user asks for 'bounding boxes', assume they want to find 'object'. "
        "The `input` for the tool must be a dictionary with two keys: `image` (the URL) and `query` (a string of the object(s) to find, e.g., 'box, boxes'). "
        "After the tool runs, output the complete, raw JSON response. Do not interpret or format it."
        "Whenever i give you a link trigger the tool call , extract its outputs and links and present me in a proper markdown format with detailed analysis from the tool call in natural language"
    )

    tools = mcp_toolkit.get_tools()

    model = ModelFactory.create(
        model_platform=ModelPlatformType.GEMINI,
        model_type="gemini-2.5-pro",
        api_key=os.getenv("GOOGLE_API_KEY"),
        model_config_dict={"temperature": 0.0, "max_tokens": 4096},
    )

    sys_msg = BaseMessage.make_assistant_message(
        role_name=agent_name,
        content=system_message_content,
    )

    agent = ChatAgent(model=model, system_message=sys_msg, tools=tools, memory=None)

    rprint(
        f"[bold green]Started {agent_name}. Enter your request or type 'exit' to quit.[/bold green]"
    )
    try:
        while True:
            user_input = input("\nYou: ").strip()

            if user_input.lower() in ["exit", "quit", "bye"]:
                rprint("[bold yellow]Exiting...[/bold yellow]")
                break

            if not user_input:
                continue

            user_message = BaseMessage.make_user_message(
                role_name="User", content=user_input
            )

            response = await agent.astep(user_message)

            if response and hasattr(response, "msgs") and response.msgs:
                for msg in response.msgs:
                    rprint(f"[bold blue]{agent_name}:[/bold blue]\n{msg.content}")

    except KeyboardInterrupt:
        rprint(f"[bold yellow]\nExiting due to KeyboardInterrupt...[/bold yellow]")
    finally:
        await mcp_toolkit.disconnect()
        rprint("[bold red]MCP Toolkit disconnected. Program ended.[/bold red]")


if __name__ == "__main__":
    asyncio.run(main())
