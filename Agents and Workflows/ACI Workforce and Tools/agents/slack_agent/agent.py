import asyncio
import os
from dotenv import load_dotenv

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.toolkits import MCPToolkit
from camel.types import ModelPlatformType

load_dotenv()

specialization = (
    "managing Slack communications, team collaboration, and workspace administration. "
    "You have access to comprehensive Slack tools including sending messages, creating "
    "channels, managing users, posting announcements, setting reminders, sharing files, "
    "and automating workflows. You excel at facilitating team communication, organizing "
    "discussions, coordinating project updates, managing Slack workspaces, creating "
    "automated notifications, and maintaining effective team collaboration through "
    "structured messaging and channel organization."
)

async def get_slack_agent():
    """
    Creates and connects a Slack Manager agent with its dedicated MCP tools.

    Returns:
        tuple[ChatAgent, MCPToolkit]: A tuple containing the configured
                                       ChatAgent and its connected MCPToolkit.
    """
    current_dir = os.path.dirname(__file__)
    mcp_config_path = os.path.join(current_dir, "mcp_config.json")

    mcp_toolkit = MCPToolkit(config_path=mcp_config_path)
    await mcp_toolkit.connect()
    tools = mcp_toolkit.get_tools()

    model = ModelFactory.create(
        model_platform=ModelPlatformType.OPENAI,
        model_type="gpt-4o",
        api_key=os.getenv("OPENAI_API_KEY"),
        model_config_dict={"temperature": 0.2, "max_tokens": 4096},
    )

    system_message = BaseMessage.make_assistant_message(
        role_name="Slack Manager",
        content=specialization,
    )

    agent = ChatAgent(system_message=system_message, model=model, tools=tools)

    return agent, mcp_toolkit
