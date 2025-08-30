import asyncio
import os
from pathlib import Path
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
import json

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.toolkits import MCPToolkit
from camel.toolkits.mcp_toolkit import MCPConnectionError
from camel.types import ModelPlatformType
from create_config import create_config, CONFIG_PATH

load_dotenv()
console = Console()

# Global variables for the agent and toolkit
agent: ChatAgent | None = None
mcp_toolkit: MCPToolkit | None = None
tool_list: list[dict] = []
agent_name = "PlaygroundAgent"

# System message content for the agent
system_message_content = """You are a versatile autonomous agent. Your primary function is to analyse user prompts, call the appropriate MCP tools when needed, and present a clear, friendly answer. If an image-analysis tool called `REPLICATE.run` is available, prefer using it for detection tasks. When returning results, explain in plain language first, then (if relevant) include a markdown table of objects and an image rendered with bounding boxes.

**Your General Instructions:**
1. Extract the intent and parameters from the user's question.
2. If a tool call is required, call it immediately with the correct arguments (do not ask for confirmation unless absolutely necessary).
3. Summarise results in a user-friendly paragraph.
4. Include structured details (tables / code) afterwards when useful.
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan – sets up agent & toolkit, tears them down on shutdown."""
    global agent, mcp_toolkit, tool_list

    rprint(Panel("[bold yellow]Initializing Services and Agent...[/bold yellow]"))
    create_config()  # ensures CONFIG_PATH exists / is up to date

    mcp_toolkit = MCPToolkit(config_path=str(CONFIG_PATH))

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

    # Define the Agent's persona
    system_prompt_msg = BaseMessage.make_assistant_message(
        role_name=agent_name,
        content=system_message_content,
    )

    # Create the AI Agent
    model = ModelFactory.create(
        model_platform=ModelPlatformType.GEMINI,
        model_type="gemini-2.5-flash",
        api_key=os.getenv("GOOGLE_API_KEY"),
        model_config_dict={"temperature": 0.0, "max_tokens": 4096},
    )
    tools = mcp_toolkit.get_tools()

    # Store a serializable list of tool information
    tool_list = [
        {"name": tool.func.__name__, "description": tool.func.__doc__ or ""}
        for tool in tools
    ]

    rprint(f"[bold blue]Available tools:[/bold blue] {[tool['name'] for tool in tool_list]}")

    agent = ChatAgent(model=model, system_message=system_prompt_msg, tools=tools)
    agent.reset()
    console.print(Panel(f"[bold green]Agent {agent_name} is ready![/bold green]"))

    yield  # --- Application running ---

    # --- Teardown ---
    if mcp_toolkit:
        await mcp_toolkit.disconnect()
        rprint("\n[bold red]Disconnected from services. Program ended.[/bold red]")


# Initialize FastAPI app
app = FastAPI(lifespan=lifespan)

# CORS (allow everything for local dev – adjust in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserMessage(BaseModel):
    content: str


@app.get("/tools")
async def get_tools():
    """Return metadata about the currently loaded tools."""
    if not tool_list:
        rprint("[bold red]Tools not available yet.[/bold red]")
        return {"error": "Tools not available yet."}
    return {"tools": tool_list}


@app.post("/chat")
async def chat_endpoint(user_message: UserMessage):
    """Passes the user message to the agent and returns its response."""
    rprint(f"[bold magenta]User:[/bold magenta] {user_message.content}")

    if not agent:
        return {"error": "Agent not initialized"}

    message = BaseMessage.make_user_message(role_name="User", content=user_message.content)

    with console.status("[bold green]Agent is thinking...[/bold green]"):
        response = await agent.astep(message)

    executed_tools = []
    if response.info and response.info.get("tool_calls"):
        executed_tools = [tc.tool_name for tc in response.info["tool_calls"]]
        # Log details (trimmed)
        log = [
            {"tool": tc.tool_name, "args": tc.args, "result": str(tc.result)[:120] + "..."}
            for tc in response.info["tool_calls"]
        ]
        rprint(json.dumps(log, indent=2))

    if response and getattr(response, "msgs", None):
        content = response.msgs[0].content
        return {"response": content, "executed_tools": executed_tools}

    return {"error": "No response generated."}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    if not mcp_toolkit or not agent:
        await websocket.send_json({"type": "error", "content": "Agent not initialized"})
        return

    try:
        while True:
            data = await websocket.receive_text()
            user_msg = BaseMessage.make_user_message(role_name="User", content=data)
            response = await agent.astep(user_msg)
            if response and getattr(response, "msgs", None):
                for msg in response.msgs:
                    await websocket.send_json({"type": "agent_response", "content": msg.content})
    except WebSocketDisconnect:
        pass


if __name__ == "__main__":
    import uvicorn

    rprint(Panel("[bold green]Starting Agent MCP server...[/bold green]"))
    uvicorn.run("agent_server:app", host="0.0.0.0", port=8000, reload=True) 