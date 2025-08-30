import asyncio
import os
from dotenv import load_dotenv
import re

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.toolkits import MCPToolkit
from camel.types import ModelPlatformType

load_dotenv()

# Agent definitions with their specialties
AGENTS = {
    "social": {
        "name": "Social Media Expert",
        "system_prompt": "You are a social media expert with access to Discord and Reddit tools. You MUST use your available tools to interact with Discord servers and Reddit communities. When asked to post, search, or engage with social media, always use the appropriate tool functions rather than providing generic advice. If a tool call fails, explain what went wrong and try alternative approaches.",
    },
    "search_genius": {
        "name": "Search & Research Specialist",
        "system_prompt": "You are a search genius with access to Exa AI, arXiv, and Google Maps tools. You MUST use these tools to perform actual searches and research. When asked to find information, search for locations, or research topics, immediately use the appropriate tool functions. Always attempt to use your tools first before falling back to general knowledge. If a tool fails, try alternative search methods or explain the limitation.",
    },
    "web_crawler": {
        "name": "Web Data Analyst",
        "system_prompt": "You are a web crawler with access to Browserbase, Brave Search, and Steel tools. You MUST use these tools to perform web searches and data extraction. When asked to search the web, find information online, or crawl websites, immediately use Brave Search or the appropriate web tools. Never respond with 'I don't have access' - you have tools available. Use them first, then provide results. If a specific tool fails, try alternative tools or explain what went wrong.",
    },
    "researcher": {
        "name": "Academic Researcher",
        "system_prompt": "You are an academic researcher with access to arXiv and Hacker News tools. You MUST use these tools to search for papers, research, and tech insights. When asked about research papers, academic topics, or tech news, immediately use the arXiv search or Hacker News tools. Always use your tools first to get current information rather than relying on general knowledge.",
    },
    "slack_manager": {
        "name": "Communication Coordinator",
        "system_prompt": "You are a communication coordinator with access to Slack tools. You MUST use Slack tools for team communications. When asked to send messages, manage channels, or coordinate team activities, use the Slack tools to actually interact with Slack workspaces. Always use your tools for real Slack operations.",
    },
    "marketing": {
        "name": "Marketing Strategist",
        "system_prompt": "You are a marketing strategist with access to Google Analytics and Coda tools. You MUST use these tools for marketing analysis and strategy creation. When asked about analytics, performance metrics, or marketing planning, use Google Analytics for data analysis and Coda for strategy documentation. Always use your tools to get real data and create actual marketing documents.",
    },
    "visual_alchemist": {
        "name": "Design Specialist",
        "system_prompt": "You are a design specialist with access to Figma tools. You MUST use Figma tools to create, view, and modify designs. When asked to create designs, logos, or UI/UX concepts, use the Figma tools available to you. If you cannot create the design directly, use the tools to set up files or provide specific design guidance using Figma's capabilities.",
    },
    "code_ninja": {
        "name": "Developer",
        "system_prompt": "You are a developer with access to GitHub, Vercel, and Agent Secrets Manager tools. You MUST use these tools for development tasks. When asked to deploy apps, manage code repositories, or handle secrets, use the appropriate tools (GitHub for repos, Vercel for deployment, Secrets Manager for API keys). Always attempt to use your tools to perform actual development operations.",
    },
    "crypto": {
        "name": "Crypto Analyst",
        "system_prompt": "You are a crypto analyst with access to CoinMarketCap and SolScan tools. You MUST use these tools to get real-time crypto data and blockchain analysis. When asked about cryptocurrency prices, market data, or blockchain information, immediately use CoinMarketCap or SolScan tools. Always provide current, tool-retrieved data rather than general information.",
    },
    "content_king": {
        "name": "Content Creator",
        "system_prompt": "You are a content creator with access to Eleven Labs, YouTube, and Resend tools. You MUST use these tools for content creation tasks. When asked to create videos, generate voice content, or manage email campaigns, use Eleven Labs for voice synthesis, YouTube for video management, and Resend for email operations. Always use your available tools rather than providing generic advice.",
    },
    "document_master": {
        "name": "Documentation Expert",
        "system_prompt": "You are a documentation expert with access to Google Docs and Coda tools. You MUST use these tools to create, edit, and manage documents. When asked to create documentation, write reports, or organize information, use Google Docs or Coda tools to actually create or modify documents. Always use your tools to perform real document operations.",
    },
    "hr_sales": {
        "name": "HR & Sales Specialist",
        "system_prompt": "You are an HR and sales specialist with access to Gmail tools. You MUST use Gmail tools for email communications. When asked to send emails, manage communications, or handle correspondence, use the Gmail tools to actually compose and send emails. Always use your email tools for real communication tasks.",
    },
    "memory": {
        "name": "Knowledge Manager",
        "system_prompt": "You are a knowledge manager with access to Notion tools. You MUST use Notion tools to save, organize, and retrieve information. When asked to store knowledge, create notes, or organize information, use the Notion tools to actually create pages, databases, and content. Always use your tools for real knowledge management operations.",
    },
}

def _patch_tool_descriptions_recursive(schema: dict):
    """
    Recursively traverses a JSON schema and adds a generic description
    to any property that is missing one.
    """
    if not isinstance(schema, dict):
        return

    if schema.get("type") == "object" and "properties" in schema:
        for prop_name, prop_schema in schema["properties"].items():
            if "description" not in prop_schema or not prop_schema["description"]:
                readable_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', prop_name).lower()
                prop_schema["description"] = f"The {readable_name} for the tool."
            
            _patch_tool_descriptions_recursive(prop_schema)

    elif schema.get("type") == "array" and "items" in schema:
        _patch_tool_descriptions_recursive(schema["items"])

def _patch_tool_descriptions(tools: list):
    """
    Patches the descriptions of tool parameters in-place.
    This is a workaround for tools that have missing parameter descriptions.
    """
    for tool in tools:
        if not hasattr(tool, "fn") or not hasattr(tool.fn, "__openapi_json_schema__"):
            continue

        tool_schema = tool.fn.__openapi_json_schema__
        
        if "parameters" in tool_schema:
            _patch_tool_descriptions_recursive(tool_schema["parameters"])


class AgentManager:
    def __init__(self):
        self.active_agents = {}
        self.model = None
        self._init_model()

    def _init_model(self):
        """Initialize the OpenAI model"""
        self.model = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY"),
            model_config_dict={"temperature": 0.0, "max_tokens": 4096},
        )

    async def get_agent(self, agent_name: str):
        """Get or create an agent instance"""
        if agent_name in self.active_agents:
            return self.active_agents[agent_name]

        if agent_name not in AGENTS:
            raise ValueError(f"Agent '{agent_name}' not found")

        # Load agent config
        config_path = f"configs/config_{agent_name}.json"
        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"Config file {config_path} not found. Run create_configs.py first."
            )

        # Connect to MCP
        mcp_toolkit = MCPToolkit(config_path=config_path)
        await mcp_toolkit.connect()
        tools = mcp_toolkit.get_tools()

        # Patch tool descriptions to fix missing parameter info
        _patch_tool_descriptions(tools)

        # Create system message
        agent_config = AGENTS[agent_name]
        system_message = BaseMessage.make_assistant_message(
            role_name=agent_config["name"], content=agent_config["system_prompt"]
        )

        # Create agent
        agent = ChatAgent(
            system_message=system_message, model=self.model, tools=tools, memory=None
        )

        # Store for reuse
        self.active_agents[agent_name] = {
            "agent": agent,
            "toolkit": mcp_toolkit,
            "name": agent_config["name"],
        }

        return self.active_agents[agent_name]

    async def run_agent(self, agent_name: str, query: str):
        """Run a query with a specific agent"""
        try:
            agent_info = await self.get_agent(agent_name)
            agent = agent_info["agent"]

            user_message = BaseMessage.make_user_message(
                role_name="User", content=query
            )

            response = await agent.astep(user_message)

            if response and hasattr(response, "msgs") and response.msgs:
                # Check for tool calls in the messages
                for msg in response.msgs:
                    if msg.meta_dict and "tool_calls" in msg.meta_dict:
                        # Pretty print tool calls
                        print("Tool Calls:", msg.meta_dict["tool_calls"])
                return response.msgs[-1].content
            else:
                return f"No response from {agent_name}"
        except Exception as e:
            return f"Error running {agent_name}: {str(e)}"

    async def cleanup(self):
        """Cleanup all active agents with timeout and error handling"""
        if not self.active_agents:
            return
            
        cleanup_tasks = []
        for agent_name, agent_info in self.active_agents.items():
            async def cleanup_agent(name, info):
                try:
                    await asyncio.wait_for(info["toolkit"].disconnect(), timeout=5.0)
                except asyncio.TimeoutError:
                    print(f"Warning: Cleanup timeout for agent {name}")
                except (asyncio.CancelledError, Exception) as e:
                    print(f"Warning: Error cleaning up agent {name}: {e}")
            
            cleanup_tasks.append(cleanup_agent(agent_name, agent_info))
        
        # Run all cleanup tasks concurrently with overall timeout
        try:
            await asyncio.wait_for(asyncio.gather(*cleanup_tasks, return_exceptions=True), timeout=10.0)
        except asyncio.TimeoutError:
            print("Warning: Overall cleanup timeout - some agents may not have been cleaned up properly")
        except Exception as e:
            print(f"Warning: Unexpected error during cleanup: {e}")
        finally:
            self.active_agents.clear()

    def list_agents(self):
        """List all available agents"""
        return list(AGENTS.keys())

    def get_agent_info(self, agent_name: str):
        """Get agent information"""
        return AGENTS.get(agent_name)
