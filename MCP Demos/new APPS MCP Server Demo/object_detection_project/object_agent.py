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

load_dotenv()


async def main():
    """
    Main function to run the Object Detection Agent.
    """
    create_config()
    mcp_toolkit = MCPToolkit(config_path="config.json")
    await mcp_toolkit.connect()

    agent_name = "ACI.dev MEM0 Agent"
    system_message_content = (
        "You are a specialized Memory Management Agent using MEM0 tools. Your primary function is to help users store, retrieve, update, delete, and analyze their memories using the available MEM0 tools. "
        "IMPORTANT: Always use user_id 'your_user_id' in all MEM0 tool calls. "
        "When users provide information to store, automatically use the appropriate MEM0 store tools with user_id 'your_user_id' to save it. "
        "When users ask about their memories or want to search for something, automatically use the MEM0 retrieve tools with user_id 'your_user_id' to help them find relevant information. "
        "For updating or deleting memories, use the appropriate MEM0 update or delete tools with user_id 'your_user_id'. "
        "Always provide clear, detailed responses explaining what memory operations were performed. "
        "Format your responses as follows: "
        "- **Operation Summary:** Explain what memory operation was performed "
        "- **Memory Details:** Show the stored/retrieved information in a clear format "
        "- **Status:** Confirm the success of the operation "
        "Always ensure that all MEM0 tool calls include the user_id 'your_user_id' parameter. Be proactive in using MEM0 tools whenever users share information or ask memory-related questions."
    )

    tools = mcp_toolkit.get_tools()

    model = ModelFactory.create(
        model_platform=ModelPlatformType.GEMINI,
        model_type="gemini-1.5-flash",
        api_key=os.getenv("GOOGLE_API_KEY"),
        model_config_dict={"temperature": 0.0, "max_tokens": 4096},
    )

    sys_msg = BaseMessage.make_assistant_message(
        role_name=agent_name,
        content=system_message_content,
    )

    agent = ChatAgent(model=model, system_message=sys_msg, tools=tools, memory=None)

    rprint(
        f"[bold green]Started {agent_name}. Share information to store or ask about your memories. Type 'exit' to quit.[/bold green]"
    )
    rprint("[bold cyan]💾 Memory Operations Available:[/bold cyan]")
    rprint("[green]  • Store information by sharing it[/green]")
    rprint("[green]  • Search memories with natural language[/green]") 
    rprint("[green]  • Ask to update or delete specific memories[/green]")
    rprint("[green]  • Request memory analysis and insights[/green]")
    rprint("[dim]Example: 'I went to Paris last week' or 'What do you remember about my trips?'[/dim]")
    
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
