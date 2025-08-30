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
    "conducting comprehensive research and information discovery across multiple sources. "
    "You have access to Exa AI for advanced web search and content discovery, ArXiv for "
    "academic papers and research publications, and Google Maps for location-based information "
    "and geographical data. You excel at finding relevant information, synthesizing research "
    "from multiple sources, identifying credible academic sources, discovering trending topics, "
    "and providing comprehensive background research for any topic or question."
)

async def get_search_agent():
    """
    Creates and connects a Research Specialist agent with its dedicated MCP tools.

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
        role_name="Research Specialist",
        content=specialization,
    )

    agent = ChatAgent(system_message=system_message, model=model, tools=tools)

    return agent, mcp_toolkit
