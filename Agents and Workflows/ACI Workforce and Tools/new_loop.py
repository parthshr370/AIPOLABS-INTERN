import asyncio
import os

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.toolkits import MCPToolkit
from camel.types import ModelPlatformType
from create_config import create_config
from dotenv import load_dotenv
from rich import print as rprint


async def main():
    """A continuous chat loop with a single, tool-enabled AI agent."""
    load_dotenv()

    # --- 1. Configuration ---
    AGENT_NAME = "Research Assistant"
    SYSTEM_PROMPT = """You are a meticulous Research Assistant.
    Your goal is to provide accurate, up-to-date information by using the tools available to you.
    You have access to the following tools:
    - BRAVE_SEARCH: For general web searches and finding current events.
    - ARXIV: For searching academic papers and preprints.
    - GITHUB: For searching code, repositories, and developer trends.
    Always state which tool you are using when you perform an action.
    """

    # --- 2. MCP and Tool Initialization ---
    rprint("[cyan]🔧 Setting up ACI MCP connection...[/cyan]")
    create_config()
    mcp_toolkit = MCPToolkit(config_path="config.json")
    await mcp_toolkit.connect()
    tools = mcp_toolkit.get_tools()
    rprint(f"[green]✅ Connected! Found {len(tools)} ACI tools.[/green]\n")

    try:
        # --- 3. Agent and Model Initialization ---
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY is required in .env")

        model = ModelFactory.create(
            model_platform=ModelPlatformType.GEMINI,
            model_type="gemini-2.5-pro",
            api_key=google_api_key,
            model_config_dict={"temperature": 0.7},
        )
        system_message = BaseMessage.make_assistant_message(
            role_name=AGENT_NAME, content=SYSTEM_PROMPT
        )
        # Pass the tools to the agent during initialization
        agent = ChatAgent(system_message=system_message, model=model, tools=tools)

        rprint(f"[bold green]🤖 Starting chat with {AGENT_NAME}.[/bold green]")
        rprint("[dim]Available tools: BRAVE_SEARCH, GITHUB, ARXIV[/dim]")
        rprint("[dim]Type 'exit', 'quit', or 'bye' to end.[/dim]")

        # --- 4. The Continuous Chat Loop ---
        while True:
            user_input = input("\nYou: ").strip()

            if user_input.lower() in ["exit", "quit", "bye"]:
                rprint(f"[bold yellow]👋 Goodbye![/bold yellow]")
                break

            user_message = BaseMessage.make_user_message(
                role_name="User", content=user_input
            )

            rprint(f"[dim]{AGENT_NAME} is thinking...[/dim]")
            response = await agent.astep(user_message)

            if response.msgs:
                rprint(f"[cyan]{AGENT_NAME}:[/cyan] {response.msgs[0].content}")

    except KeyboardInterrupt:
        rprint(f"\n[bold yellow]👋 Goodbye![/bold yellow]")
    finally:
        # --- 5. Cleanup ---
        await mcp_toolkit.disconnect()
        rprint("[bold green]🔌 MCP Toolkit disconnected.[/bold green]")


if __name__ == "__main__":
    asyncio.run(main())
