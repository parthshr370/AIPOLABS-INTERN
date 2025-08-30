import asyncio
import os
import warnings
from pathlib import Path

from dotenv import load_dotenv
from rich import print as rprint

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.toolkits import MCPToolkit
from camel.types import ModelPlatformType

warnings.filterwarnings("ignore")
load_dotenv()

# Directory where config JSON files live
CONFIG_DIR = Path(__file__).resolve().parent.parent / "configs"

# Shared model configuration for all agents
MODEL_KWARGS = {
    "model_platform": ModelPlatformType.GEMINI,
    "model_type": "gemini-2.5-pro-preview-06-05",
    "api_key": os.getenv("GOOGLE_API_KEY"),
    "model_config_dict": {"temperature": 0.7, "max_tokens": 40000},
}

# (agent_key, config_filename, system_prompt, unique_query)
AGENT_TESTS = [
    (
        "social",
        "config_social.json",
        "You are a social media expert. Use Discord and Reddit tools to interact with communities.",
        "Post a welcome message to our Discord server about the upcoming launch.",
    ),
    (
        "search_genius",
        "config_search_genius.json",
        "You are a search & research specialist. Use Exa AI, arXiv and Google Maps to fetch data.",
        "Find highly-rated Italian restaurants near the Colosseum in Rome and give me the top 3 with map links.",
    ),
    (
        "web_crawler",
        "config_web_crawler.json",
        "You are a web data analyst. Use Brave Search and related tools to extract information from the web.",
        "Use Brave Search to list the top programming blogs to follow in 2024.",
    ),
    (
        "researcher",
        "config_researcher.json",
        "You are an academic researcher. Use arXiv and Hacker News tools to retrieve papers and tech news.",
        "Find the most recent arXiv papers on quantum computing published this month.",
    ),
    (
        "slack_manager",
        "config_slack_manager.json",
        "You are a communication coordinator. Use Slack tools for team communication.",
        "Send a reminder message to #general about the daily stand-up at 10 AM tomorrow.",
    ),
    (
        "marketing",
        "config_marketing.json",
        "You are a marketing strategist. Use Google Analytics and Coda tools for insights and planning.",
        "Show me last week's website traffic broken down by channel and suggest an optimization action.",
    ),
    (
        "visual_alchemist",
        "config_visual_alchemist.json",
        "You are a design specialist. Use Figma tools to create and edit UI/UX designs.",
        "Create a mobile-app login screen concept in Figma using our brand colors.",
    ),
    (
        "code_ninja",
        "config_code_ninja.json",
        "You are a developer. Use GitHub, Vercel, and Secrets Manager tools to manage code & deployments.",
        "Deploy the latest commit of the GitHub repo `my-app/frontend` to Vercel in the production environment.",
    ),
    (
        "crypto",
        "config_crypto.json",
        "You are a crypto analyst. Use CoinMarketCap and SolScan for real-time data and chain analysis.",
        "Give me the current price of Ethereum (ETH) and today's 24-hour percentage change.",
    ),
    (
        "content_king",
        "config_content_king.json",
        "You are a content creator. Use Eleven Labs, YouTube, and Resend tools for multimedia content.",
        "Draft a catchy YouTube video title and description for an AI-powered cooking tutorial.",
    ),
    (
        "document_master",
        "config_document_master.json",
        "You are a documentation expert. Use Google Docs and Coda to create and manage docs.",
        "Create a project proposal document titled 'Project Phoenix' with an outline of objectives and timelines.",
    ),
    (
        "hr_sales",
        "config_hr_sales.json",
        "You are an HR & sales specialist. Use Gmail tools to handle email communications.",
        "Draft and send a follow-up email to a potential client thanking them for yesterday's call.",
    ),
    (
        "memory",
        "config_memory.json",
        "You are a knowledge manager. Use Notion tools to store and retrieve information.",
        "Save these meeting notes in Notion: 'Budget approved for Q3 marketing campaign.'",
    ),
]


async def test_agent(agent_key: str, cfg_file: str, system_prompt: str, query: str):
    cfg_path = CONFIG_DIR / cfg_file
    if not cfg_path.exists():
        rprint(f"[red]Config file not found for {agent_key}: {cfg_path}")
        return

    toolkit = MCPToolkit(config_path=str(cfg_path))
    await toolkit.connect()
    tools = toolkit.get_tools()

    model = ModelFactory.create(**MODEL_KWARGS)

    system_msg = BaseMessage.make_assistant_message(role_name=agent_key, content=system_prompt)
    agent = ChatAgent(model=model, system_message=system_msg, tools=tools)

    user_msg = BaseMessage.make_user_message(role_name="User", content=query)

    rprint(f"\n[bold cyan]▶ Testing {agent_key}[/bold cyan]\n[dim]Query:[/dim] {query}")
    try:
        response = await agent.astep(user_msg)
        if response and response.msgs:
            final = response.msgs[-1]
            snippet = final.content if len(final.content) <= 600 else final.content[:600] + "…"
            rprint(f"[green]Response:[/green] {snippet}")
            if final.meta_dict and "tool_calls" in final.meta_dict:
                rprint("[yellow]Tool Calls:[/yellow]", final.meta_dict["tool_calls"])
        else:
            rprint("[yellow]No response received[/yellow]")
    except Exception as exc:
        rprint(f"[red]Error while testing {agent_key}: {exc}")
    finally:
        try:
            await toolkit.disconnect()
        except Exception:
            pass


async def main():
    rprint("[bold]🔧 ACI Agent Swarm — Batch Test[/bold]")

    if not os.getenv("GOOGLE_API_KEY"):
        rprint("[red]GOOGLE_API_KEY environment variable is missing.[/red]")
        return

    for agent_key, cfg_file, prompt, q in AGENT_TESTS:
        await test_agent(agent_key, cfg_file, prompt, q)
        await asyncio.sleep(1)  # gentle pause

    rprint("\n[bold green]✅ Batch testing complete.[/bold green]")


if __name__ == "__main__":
    asyncio.run(main()) 