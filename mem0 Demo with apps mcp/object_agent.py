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
        "You are a specialized Memory Management Agent with access to MEM0, BRAVE_SEARCH, and GMAIL tools. Your primary function is to help users store, retrieve, update, delete, and analyze their memories, while also providing web search and email capabilities. "
        "IMPORTANT: Always use user_id 'parthshr370' in all MEM0 tool calls. "
        "Always respond in a natural, conversational tone. Talk to the user like a helpful assistant, not a formal system. "
        "Choose the appropriate tools based on user requests: "
        "- **MEM0 Tools:** For memory operations (storing, retrieving, updating, deleting personal information) - always use user_id 'parthshr370' "
        "- **BRAVE_SEARCH Tools:** For web searches when users need current information, research, or answers not in their memories "
        "- **GMAIL Tools:** For email-related tasks like reading, sending, or managing emails "
        "When users provide information to store, use MEM0 tools. When they ask about current events or need research, use BRAVE_SEARCH. For email tasks, use GMAIL tools. "
        "Structure your responses like this: "
        "- Start with natural conversation (e.g., 'I found your information!' or 'Got it! I've saved that for you.') "
        "- **Operation Summary:** Briefly explain what you did "
        "- **Details:** Show the relevant information in a clear, organized format "
        "- **Status:** Confirm success and provide helpful context "
        "- End with natural follow-up (e.g., 'Is there anything else you'd like me to remember?' or 'Would you like to search for something else?') "
        "Always ensure that all MEM0 tool calls include the user_id 'parthshr370' parameter. Be proactive in using the right tools for each user request."
    )

    tools = mcp_toolkit.get_tools()

    model = ModelFactory.create(
        model_platform=ModelPlatformType.GEMINI,
        model_type="gemini-2.5-flash",
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