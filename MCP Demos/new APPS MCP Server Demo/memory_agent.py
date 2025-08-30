import asyncio
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
import json
import nest_asyncio

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.toolkits import MCPToolkit
from camel.toolkits.mcp_toolkit import MCPConnectionError
from camel.types import ModelPlatformType
from create_config import create_config

# Apply nest_asyncio to allow running asyncio in a uvicorn environment
nest_asyncio.apply()

load_dotenv()
console = Console()

# Global variables for the agent and toolkit
agent: ChatAgent | None = None
mcp_toolkit: MCPToolkit | None = None
tool_list: list[dict] = []
agent_name = "ACI.dev MEM0 Agent"

# System message content for the memory management agent
system_message_content = """You are a specialized Memory Management Agent using MEM0 tools. Your primary function is to help users store, retrieve, update, delete, and analyze their memories using the available MEM0 tools.

**IMPORTANT: Always use user_id "your_user_id" in all MEM0 tool calls.**

**Your Instructions:**
1.  **Analyze User Input:** When users provide information to store, automatically identify what should be remembered. When they ask questions, identify what memories to search for.
2.  **Use Available Tools:** Use the appropriate tools for each operation:
    - **MEM0 Tools:** For storing, retrieving, updating, and deleting memories (always use user_id "your_user_id")
    - **BRAVE_SEARCH Tools:** For searching the web when users ask questions that require current information or research
    - **GMAIL Tools:** For email-related tasks like reading, sending, or managing emails
    - Choose the right tool based on the user's request - memory operations use MEM0, web searches use BRAVE_SEARCH, email tasks use GMAIL
3.  **Respond Conversationally:** Always respond in a natural, conversational tone. Talk to the user like a helpful assistant, not a formal system.
4.  **Format the Final Response:** After using MEM0 tools, structure your response like this:
    - Start with natural conversation (e.g., "I found your medication information!" or "Got it! I've stored that for you.")
    - **Operation Summary:** Briefly explain what you did
    - **Memory Details:** Show the information in a clear, organized format
    - **Status:** Confirm success and provide helpful context
    - End with natural follow-up (e.g., "Is there anything else you'd like me to remember?" or "Would you like to search for something else?")

**Example Scenarios:**
- **Memory Storage:** User says: 'I went to Paris last week and loved the Eiffel Tower' → Store using MEM0 tools with user_id "your_user_id"
- **Memory Retrieval:** User asks: 'What do you remember about my travels?' → Search memories using MEM0 with user_id "your_user_id"
- **Web Search:** User asks: 'What's the current weather in Paris?' → Use BRAVE_SEARCH to get current information
- **Email Management:** User says: 'Check my recent emails' → Use GMAIL tools to access their email

Always ensure that all MEM0 tool calls include the user_id "your_user_id" parameter. Be proactive in using MEM0 tools whenever users share information or ask memory-related questions."""


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the lifecycle of the application, including agent setup and teardown.
    """
    global agent, mcp_toolkit, tool_list
    rprint(Panel("[bold yellow]Initializing Services and Agent...[/bold yellow]"))
    create_config()
    mcp_toolkit = MCPToolkit(config_path="config.json")

    # Connect to MCP server with retries
    max_retries = 3
    retry_delay_seconds = 5
    for attempt in range(max_retries):
        try:
            console.log(
                f"Attempting to connect to MCP server ({attempt + 1}/{max_retries})..."
            )
            await mcp_toolkit.connect()
            console.log("[bold green]✓ Services Connected.[/bold green]")
            break
        except MCPConnectionError as e:
            if attempt < max_retries - 1:
                console.log(
                    f"[yellow]Connection failed. Retrying in {retry_delay_seconds} seconds...[/yellow]"
                )
                await asyncio.sleep(retry_delay_seconds)
            else:
                console.log(
                    "[bold red]FATAL: MCP connection failed after multiple retries.[/bold red]"
                )
                raise e

    # Define the Agent's persona as a Memory Management Agent
    memory_agent_prompt = BaseMessage.make_assistant_message(
        role_name=agent_name,
        content=system_message_content,
    )

    # Create the AI Agent
    model = ModelFactory.create(
        model_platform=ModelPlatformType.GEMINI,
        model_type="gemini-2.5-flash",
        api_key=os.getenv("GOOGLE_API_KEY"),
        model_config_dict={"temperature": 0.0, "max_tokens": 40000},
    )
    tools = mcp_toolkit.get_tools()

    # Store a serializable list of tool information
    tool_list = [
        {"name": tool.func.__name__, "description": tool.func.__doc__ or ""}
        for tool in tools
    ]

    rprint(
        f"[bold blue]Available tools:[/bold blue] {[tool['name'] for tool in tool_list]}"
    )

    agent = ChatAgent(model=model, system_message=memory_agent_prompt, tools=tools)
    agent.reset()
    console.print(Panel(f"[bold green]{agent_name} is ready![/bold green]"))

    yield  # The application is now running

    # --- Teardown ---
    if mcp_toolkit:
        await mcp_toolkit.disconnect()
        rprint("\n[bold red]Disconnected from services. Program ended.[/bold red]")


# Initialize FastAPI app
app = FastAPI(lifespan=lifespan)

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserMessage(BaseModel):
    content: str


@app.get("/tools")
async def get_tools():
    """
    Endpoint to get the list of available tools.
    """
    if not tool_list:
        rprint("[bold red]Tools not available yet.[/bold red]")
        return {"error": "Tools not available yet."}

    rprint(
        f"[bold blue]Returning tools list:[/bold blue] {[tool['name'] for tool in tool_list]}"
    )
    return {"tools": tool_list}


@app.post("/chat")
async def chat_endpoint(user_message: UserMessage):
    """
    Endpoint to receive user messages and return the agent's response.
    """
    rprint(f"[bold magenta]Received request for /chat[/bold magenta]")
    rprint(f"[cyan]User content:[/cyan] {user_message.content}")

    if not agent:
        rprint("[bold red]Agent not initialized[/bold red]")
        return {"error": "Agent not initialized"}

    message = BaseMessage.make_user_message(
        role_name="User", content=user_message.content
    )

    with console.status("[bold green]Agent is working...[/bold green]"):
        rprint("[yellow]Invoking agent...[/yellow]")
        response = await agent.astep(message)
        rprint("[green]Agent invocation complete.[/green]")

    executed_tools = []
    if response.info and response.info.get("tool_calls"):
        executed_tools = [
            tool_call.tool_name for tool_call in response.info["tool_calls"]
        ]

        # Log tool calls with more details
        tool_calls_details = [
            {
                "tool_name": tool_call.tool_name,
                "args": tool_call.args,
                "result": str(tool_call.result)[:200] + "..."
                if len(str(tool_call.result)) > 200
                else tool_call.result,
            }
            for tool_call in response.info["tool_calls"]
        ]
        rprint(
            f"[blue]Tools called:[/blue]\n{json.dumps(tool_calls_details, indent=2)}"
        )

    if response and hasattr(response, "msgs") and response.msgs:
        response_content = response.msgs[0].content
        rprint(
            f"[cyan]Agent response content (preview):[/cyan]\n{response_content[:200]}..."
        )
        return {
            "response": response_content,
            "executed_tools": executed_tools,
            "raw_output": str(response),
        }

    rprint("[bold red]No response generated.[/bold red]")
    return {"error": "Sorry, I couldn't respond."}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for chat.
    """
    await websocket.accept()
    rprint("[bold green]WebSocket connection established.[/bold green]")

    if not mcp_toolkit or not agent:
        rprint("[bold red]Agent or toolkit not initialized.[/bold red]")
        await websocket.send_json({"type": "error", "content": "Agent not initialized"})
        return

    try:
        while True:
            data = await websocket.receive_text()
            rprint(f"[cyan]WebSocket received:[/cyan] {data}")

            user_message = BaseMessage.make_user_message(role_name="User", content=data)
            response = await agent.astep(user_message)

            if response and hasattr(response, "msgs") and response.msgs:
                for msg in response.msgs:
                    # Send formatted message
                    await websocket.send_json(
                        {
                            "type": "agent_response",
                            "sender": agent_name,
                            "content": msg.content,
                        }
                    )
                # Send raw output
                await websocket.send_json(
                    {
                        "type": "raw_output",
                        "sender": "System",
                        "content": str(response),
                    }
                )
                rprint("[green]WebSocket response sent.[/green]")

    except WebSocketDisconnect:
        rprint("[bold yellow]WebSocket connection closed.[/bold yellow]")
    except Exception as e:
        rprint(f"[bold red]An error occurred in WebSocket: {e}[/bold red]")
        try:
            await websocket.send_json(
                {"type": "error", "sender": "System", "content": str(e)}
            )
        except:
            pass
    finally:
        rprint("[bold yellow]WebSocket connection terminated.[/bold yellow]")


if __name__ == "__main__":
    import uvicorn

    rprint(Panel("[bold green]Starting ACI.dev MEM0 Demo Server...[/bold green]"))
    uvicorn.run(app, host="0.0.0.0", port=8000)
