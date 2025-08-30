import asyncio
import os
import re
from dotenv import load_dotenv
from rich import print as rprint

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.toolkits import MCPToolkit
from camel.types import ModelPlatformType

load_dotenv()

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
    """
    for tool in tools:
        # The tool object is a FunctionTool, which has a 'parameters' attribute
        # containing the JSON schema for its arguments.
        if hasattr(tool, "parameters") and isinstance(tool.parameters, dict):
            _patch_tool_descriptions_recursive(tool.parameters)

async def main():
    agent_name = "web_crawler"
    config_path = f"configs/config_{agent_name}.json"

    if not os.path.exists(config_path):
        rprint(f"[bold red]Error: Config file '{config_path}' not found.[/bold red]")
        rprint("Please run `python create_configs.py` first.")
        return

    rprint(f"--- Testing Direct Tool Usage for '{agent_name}' ---")

    mcp_toolkit = MCPToolkit(config_path=config_path)
    await mcp_toolkit.connect()
    
    tools = mcp_toolkit.get_tools()
    
    # Find the Brave Search tool to inspect it
    brave_search_tool = next((t for t in tools if hasattr(t, 'name') and t.name == 'BRAVE_SEARCH_search'), None)

    if brave_search_tool:
        rprint("[bold magenta]--- SCHEMA BEFORE PATCHING ---[/bold magenta]")
        import json
        rprint(json.dumps(brave_search_tool.parameters, indent=2))

    rprint(f"\n[yellow]Applying recursive patch to {len(tools)} tools...[/yellow]\n")
    _patch_tool_descriptions(tools)
    
    if brave_search_tool:
        rprint("[bold magenta]--- SCHEMA AFTER PATCHING ---[/bold magenta]")
        import json
        rprint(json.dumps(brave_search_tool.parameters, indent=2))

    model = ModelFactory.create(
        model_platform=ModelPlatformType.OPENAI,
        model_type="gpt-4o",
        api_key=os.getenv("OPENAI_API_KEY"),
        model_config_dict={"temperature": 0.0},
    )

    system_message = BaseMessage.make_assistant_message(
        role_name="Web Data Analyst",
        content="You are a web crawler with access to Browserbase, Brave Search, and Steel tools. You MUST use these tools to perform web searches and data extraction. Use the tools available to you to search the web and provide real, current results."
    )

    agent = ChatAgent(
        system_message=system_message, model=model, tools=tools
    )
    
    query = "search for the best movies in 2025"
    rprint(f"\n[bold green]Query:[/bold green] {query}\n")

    user_message = BaseMessage.make_user_message(role_name="User", content=query)
    response = await agent.astep(user_message)

    rprint("[bold blue]Agent Response:[/bold blue]")
    if response and hasattr(response, "msgs") and response.msgs:
        final_msg = response.msgs[-1]
        rprint(final_msg.content)
        if final_msg.meta_dict and "tool_calls" in final_msg.meta_dict:
            rprint("\n[bold yellow]Tool Calls Made:[/bold yellow]")
            rprint(final_msg.meta_dict["tool_calls"])
    else:
        rprint("[red]No response from agent.[/red]")

    await mcp_toolkit.disconnect()
    rprint("\n--- Test Complete ---")

if __name__ == "__main__":
    asyncio.run(main()) 