import os
from dotenv import load_dotenv
from portia import Config, LLMProvider, McpToolRegistry, ToolRegistry, DefaultToolRegistry

load_dotenv() 

aci_api_key_value = os.getenv("ACI_API_KEY")
process_env = os.environ.copy()
if aci_api_key_value:
    process_env["ACI_API_KEY"] = aci_api_key_value
else:
    print("Warning: ACI_API_KEY was not found in the environment. The aci-mcp tool might fail.")

config = Config.from_default(
    llm_provider=LLMProvider.GOOGLE_GENERATIVE_AI,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    default_model="google/gemini-2.5-pro-preview-05-06",
)

mcp_registry = McpToolRegistry.from_stdio_connection(
    server_name="aci-apps-stdio",
    command="uvx",
    args=[
        "aci-mcp", "apps-server",
        "--apps=SLACK,GITHUB,BRAVE_SEARCH,OPEN_WEATHER_MAP,GMAIL",
        "--linked-account-owner-id=your_user_id",
    ],
    env=process_env
)

# Create a more selective tool registry
# Start with the MCP tools
selective_tool_list = list(mcp_registry.get_tools()) 

# Instantiate DefaultToolRegistry to selectively pick tools
default_registry_instance = DefaultToolRegistry(config)
for tool in default_registry_instance.get_tools():
    # Identify tools by their known names or class names if possible
    # The exact names/identifiers might need checking if this doesn't work
    # For example, LLMTool might have a specific `tool.name` like 'llm_tool'
    # or we can check `tool.__class__.__name__`
    if tool.__class__.__name__ == "LLMTool" or tool.__class__.__name__ == "CalculatorTool":
        selective_tool_list.append(tool)
    # Example of adding by specific tool name if known:
    # if tool.name in ["llm_tool", "calculator_tool"]:
    #     selective_tool_list.append(tool)

# Create the final tool registry from this selective list
tool_registry = ToolRegistry(tools=selective_tool_list)
