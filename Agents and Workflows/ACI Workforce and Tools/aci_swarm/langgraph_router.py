import asyncio
import json
import os
import re
import warnings
from pathlib import Path

from dotenv import load_dotenv
from rich import print as rprint
from rich.syntax import Syntax
from rich.console import Console

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.toolkits import MCPToolkit
from camel.types import ModelPlatformType

from langgraph.graph import StateGraph, END

warnings.filterwarnings("ignore")
load_dotenv()

CONFIG_DIR = Path(__file__).resolve().parent / "configs"

MODEL_KWARGS = {
    "model_platform": ModelPlatformType.GEMINI,
    "model_type": "gemini-2.5-pro-preview-06-05",
    "api_key": os.getenv("GOOGLE_API_KEY"),
    "model_config_dict": {"temperature": 0.7, "max_tokens": 40000},
}


def _patch_tool_descriptions_recursive(schema: dict):
    if not isinstance(schema, dict):
        return
    if schema.get("type") == "object" and "properties" in schema:
        for prop_name, prop_schema in schema["properties"].items():
            if not prop_schema.get("description"):
                readable = re.sub(r"(?<!^)(?=[A-Z])", " ", prop_name).lower()
                prop_schema["description"] = f"The {readable} for the tool."
            _patch_tool_descriptions_recursive(prop_schema)
    elif schema.get("type") == "array" and "items" in schema:
        _patch_tool_descriptions_recursive(schema["items"])


def patch_tools(tools: list):
    for tool in tools:
        if hasattr(tool, "parameters") and isinstance(tool.parameters, dict):
            _patch_tool_descriptions_recursive(tool.parameters)


def select_agent(query: str) -> str:
    q = query.lower()
    if any(w in q for w in ["discord", "reddit", "social", "community", "post"]):
        return "social"
    if any(w in q for w in ["restaurant", "location", "map", "near", "address", "directions"]):
        return "search_genius"
    if any(w in q for w in ["search", "browse", "website", "crawl"]):
        return "web_crawler"
    if any(w in q for w in ["research", "paper", "study", "arxiv", "academic"]):
        return "researcher"
    if any(w in q for w in ["bitcoin", "crypto", "blockchain", "ethereum", "solana", "token"]):
        return "crypto"
    if any(w in q for w in ["design", "logo", "ui", "ux", "figma", "mockup", "visual"]):
        return "visual_alchemist"
    if any(w in q for w in ["code", "deploy", "github", "vercel", "development"]):
        return "code_ninja"
    if any(w in q for w in ["video", "content", "script", "youtube", "audio", "voice"]):
        return "content_king"
    if any(w in q for w in ["document", "docs", "write", "documentation"]):
        return "document_master"
    if any(w in q for w in ["email", "gmail", "send", "contact"]):
        return "hr_sales"
    if any(w in q for w in ["slack", "meeting", "team", "collaborate"]):
        return "slack_manager"
    if any(w in q for w in ["marketing", "analytics", "campaign", "metrics"]):
        return "marketing"
    if any(w in q for w in ["save", "remember", "note", "organize", "knowledge"]):
        return "memory"
    return "search_genius"


def route(state):
    query = state["query"]
    agent_key = select_agent(query)
    return {"agent_key": agent_key, "query": query}


async def run_single_query(agent_key: str, query: str):
    """Run a single query with the specified agent - isolated async function"""
    cfg = CONFIG_DIR / f"config_{agent_key}.json"
    if not cfg.exists():
        return [], f"No config for {agent_key}.", False

    toolkit = None
    try:
        toolkit = MCPToolkit(config_path=str(cfg))
        await toolkit.connect()
        tools = toolkit.get_tools()
        patch_tools(tools)
        
        # Extract tool names properly
        tool_names = []
        for i, tool in enumerate(tools):
            name = None
            
            # Try various ways to get the tool name
            if hasattr(tool, 'name') and tool.name:
                name = tool.name
            elif hasattr(tool, '_name') and tool._name:
                name = tool._name
            elif hasattr(tool, 'tool_name') and tool.tool_name:
                name = tool.tool_name
            elif hasattr(tool, 'function') and hasattr(tool.function, 'name'):
                name = tool.function.name
            elif hasattr(tool, 'fn') and hasattr(tool.fn, '__name__'):
                name = tool.fn.__name__
            elif hasattr(tool, 'fn') and hasattr(tool.fn, 'name'):
                name = tool.fn.name
            
            # If still no name, try to get it from the function schema
            if not name and hasattr(tool, 'fn') and hasattr(tool.fn, '__openapi_json_schema__'):
                schema = tool.fn.__openapi_json_schema__
                if isinstance(schema, dict) and 'title' in schema:
                    name = schema['title']
            
            # Fallback: try to get any string that might be the name
            if not name:
                for attr in ['openapi_schema', 'schema', '__name__']:
                    if hasattr(tool, attr):
                        try:
                            val = getattr(tool, attr)
                            if isinstance(val, str):
                                name = val
                                break
                        except:
                            continue
            
            tool_names.append(name if name else f"Tool_{i+1}")
        
        model = ModelFactory.create(**MODEL_KWARGS)
        system_msg = BaseMessage.make_assistant_message(
            role_name=agent_key,
            content=f"You are the {agent_key} agent. Use your available tools to help the user."
        )
        
        agent = ChatAgent(
            model=model,
            system_message=system_msg,
            tools=tools,
            memory=None
        )
        
        user_msg = BaseMessage.make_user_message(role_name="User", content=query)
        
        # KEY FIX: Use async step like in reference code
        response = await agent.astep(user_msg)
        
        if response and hasattr(response, "msgs") and response.msgs:
            content = response.msgs[-1].content
            
            # Extract tool calls safely for display
            tool_call_details = []
            used_tools = False
            
            for msg in response.msgs:
                if msg.meta_dict and "tool_calls" in msg.meta_dict:
                    used_tools = True
                    try:
                        # Convert tool calls to safe format
                        calls = msg.meta_dict["tool_calls"]
                        if calls:
                            # Convert to string representation to avoid pickling issues
                            safe_calls = []
                            for call in calls:
                                try:
                                    if hasattr(call, '__dict__'):
                                        call_dict = {}
                                        for attr in ['id', 'function', 'type']:
                                            if hasattr(call, attr):
                                                val = getattr(call, attr)
                                                if hasattr(val, '__dict__'):
                                                    call_dict[attr] = str(val.__dict__)
                                                else:
                                                    call_dict[attr] = str(val)
                                        safe_calls.append(call_dict)
                                    else:
                                        safe_calls.append(str(call))
                                except Exception as e:
                                    safe_calls.append(f"[Call conversion error: {e}]")
                            tool_call_details.extend(safe_calls)
                    except Exception as e:
                        tool_call_details.append(f"[Tool call extraction error: {e}]")
            
            # Also try to get tool responses if available
            tool_responses = []
            for msg in response.msgs:
                if msg.meta_dict and "tool_responses" in msg.meta_dict:
                    try:
                        responses = msg.meta_dict["tool_responses"]
                        for resp in responses:
                            try:
                                if hasattr(resp, '__dict__'):
                                    resp_dict = {}
                                    for attr in ['tool_call_id', 'content', 'name']:
                                        if hasattr(resp, attr):
                                            resp_dict[attr] = str(getattr(resp, attr))
                                    tool_responses.append(resp_dict)
                                else:
                                    tool_responses.append(str(resp))
                            except Exception as e:
                                tool_responses.append(f"[Response conversion error: {e}]")
                    except Exception as e:
                        tool_responses.append(f"[Tool response extraction error: {e}]")
        else:
            content = "No response received"
            used_tools = False
            tool_call_details = []
            tool_responses = []
        
        return tool_names, content, used_tools, tool_call_details, tool_responses
        
    except Exception as e:
        return [], f"Error: {str(e)}", False, [], []
    finally:
        if toolkit:
            try:
                await toolkit.disconnect()
            except Exception:
                pass


def exec_agent(state):
    query = state["query"]
    agent_key = state["agent_key"]
    
    # Run async function in isolated event loop
    try:
        tool_names, content, used_tools, tool_call_details, tool_responses = asyncio.run(run_single_query(agent_key, query))
    except Exception as e:
        return {
            "agent_key": agent_key,
            "tools": [],
            "response": f"Execution error: {str(e)}",
            "used_tools": False,
            "tool_calls": [],
            "tool_responses": [],
        }

    return {
        "agent_key": agent_key,
        "tools": tool_names,
        "response": content,
        "used_tools": used_tools,
        "tool_calls": tool_call_details,
        "tool_responses": tool_responses,
    }


workflow = StateGraph(dict)
workflow.add_node("Route", route)
workflow.add_node("Exec", exec_agent)
workflow.set_entry_point("Route")
workflow.add_edge("Route", "Exec")
workflow.add_edge("Exec", END)

graph = workflow.compile()


def main():
    if not os.getenv("GOOGLE_API_KEY"):
        rprint("[red]GOOGLE_API_KEY missing.[/red]")
        return

    rprint("[bold]✨ LangGraph Router (Fixed)[/bold] (type 'exit' to quit)")
    while True:
        try:
            q = input("\n🌐 Query: ").strip()
            if q.lower() in {"exit", "quit", "bye"}:
                break
            if not q:
                continue
                
            result = graph.invoke({"query": q})
            rprint(f"\n[cyan]Agent:[/cyan] {result['agent_key']}")
            rprint(f"[magenta]Tools:[/magenta] {', '.join(result['tools']) if result['tools'] else 'None'}")
            rprint(f"[yellow]Used Tools:[/yellow] {'Yes' if result.get('used_tools') else 'No'}")
            rprint(f"[green]Response:[/green] {result['response']}")
            
            # Display tool calls and responses if any
            if result.get('tool_calls'):
                rprint(f"\n[bold blue]🔧 Tool Calls:[/bold blue]")
                for i, call in enumerate(result['tool_calls'], 1):
                    try:
                        # Try to format as JSON if it's a dict
                        if isinstance(call, dict):
                            formatted_json = json.dumps(call, indent=2)
                            syntax = Syntax(formatted_json, "json", theme="monokai", line_numbers=False)
                            Console().print(f"  {i}.", end=" ")
                            Console().print(syntax)
                        else:
                            rprint(f"  {i}. {call}")
                    except:
                        rprint(f"  {i}. {call}")
            
            if result.get('tool_responses'):
                rprint(f"\n[bold magenta]📋 Tool Responses:[/bold magenta]")
                for i, resp in enumerate(result['tool_responses'], 1):
                    try:
                        # Try to format as JSON if it's a dict
                        if isinstance(resp, dict):
                            formatted_json = json.dumps(resp, indent=2)
                            syntax = Syntax(formatted_json, "json", theme="monokai", line_numbers=False)
                            Console().print(f"  {i}.", end=" ")
                            Console().print(syntax)
                        else:
                            rprint(f"  {i}. {resp}")
                    except:
                        rprint(f"  {i}. {resp}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            rprint(f"[red]Error:[/red] {e}")


if __name__ == "__main__":
    main() 