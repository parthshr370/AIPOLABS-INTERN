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
    Main function to run the Memory Agent with MEM0.
    """
    create_config()
    mcp_toolkit = MCPToolkit(config_path="config.json")
    await mcp_toolkit.connect()

    agent_name = "MemoryAgent"
    system_message_content = (
        "You are a specialized Memory Management Agent using MEM0 tools. "
        "Use the available MEM0 tools to store, retrieve, update, delete, and analyze memories based on user requests. "
        "When users provide information, use the appropriate MEM0 tool to handle their request. "
        "For storing new information, use MEM0 store tools. For searching memories, use MEM0 retrieve tools. "
        "Always provide clear, detailed responses in markdown format explaining what memory operations were performed. "
        "If users ask about their memories or want to search for something, automatically use the MEM0 tools to help them."
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
                rprint("[bold yellow]👋 Goodbye! Your memories are safely stored.[/bold yellow]")
                break

            if not user_input:
                rprint("[dim]Please enter some information or a memory request...[/dim]")
                continue

            rprint(f"[dim]🔄 Processing your request...[/dim]")
            
            user_message = BaseMessage.make_user_message(
                role_name="User", content=user_input
            )

            response = await agent.astep(user_message)

            # Debug: Show structured response
            rprint("[bold magenta]🔍 Agent Response Structure:[/bold magenta]")
            rprint(f"[dim]Response Type: {type(response)}[/dim]")
            if hasattr(response, '__dict__'):
                rprint(f"[dim]Response Attributes: {list(response.__dict__.keys())}[/dim]")
            
            if response and hasattr(response, "msgs") and response.msgs:
                rprint(f"[dim]Number of messages: {len(response.msgs)}[/dim]")
                for i, msg in enumerate(response.msgs):
                    rprint(f"[bold blue]🧠 {agent_name} (Message {i+1}):[/bold blue]")
                    rprint(f"[dim]Message Type: {type(msg)}[/dim]")
                    if hasattr(msg, '__dict__'):
                        rprint(f"[dim]Message Attributes: {list(msg.__dict__.keys())}[/dim]")
                    if hasattr(msg, 'role_name'):
                        rprint(f"[dim]Role: {msg.role_name}[/dim]")
                    rprint(f"{msg.content}")
                    rprint("[dim]─" * 50 + "[/dim]")
            
            # Show tool calls if any
            if hasattr(response, 'info') and response.info:
                rprint("[bold cyan]🛠️  Tool Calls Information:[/bold cyan]")
                rprint(f"[dim]{response.info}[/dim]")
            
            # Show any function calls
            if response and hasattr(response, 'msgs'):
                for msg in response.msgs:
                    if hasattr(msg, 'function_call') and msg.function_call:
                        rprint("[bold green]📞 Function Call Detected:[/bold green]")
                        rprint(f"[dim]{msg.function_call}[/dim]")
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        rprint("[bold green]🔧 Tool Calls Detected:[/bold green]")
                        for tool_call in msg.tool_calls:
                            rprint(f"[dim]Tool: {tool_call}[/dim]")
            
            if not response or not hasattr(response, "msgs") or not response.msgs:
                rprint("[bold red]❌ No response received. Please try again.[/bold red]")
                rprint(f"[dim]Raw response: {response}[/dim]")

    except KeyboardInterrupt:
        rprint(f"[bold yellow]\n⏹️  Interrupted by user. Exiting gracefully...[/bold yellow]")
    except Exception as e:
        rprint(f"[bold red]❌ An error occurred: {str(e)}[/bold red]")
    finally:
        await mcp_toolkit.disconnect()
        rprint("[bold magenta]🔌 MCP Toolkit disconnected. Memory session ended.[/bold magenta]")
        rprint("[dim]Thank you for using the Memory Agent![/dim]")


if __name__ == "__main__":
    asyncio.run(main())
