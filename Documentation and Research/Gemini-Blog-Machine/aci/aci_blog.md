# From Chaos to Control: How ACI.dev Redefines Context Engineering for Tool-Using Agents

You’ve built an AI agent. It’s clever, it’s promising, and it works perfectly on your local machine.

As developers, we've gotten pretty good at creating context silos for our agents' knowledge, feeding them our entire codebase or a library's documentation so they can answer questions accurately. But the moment you need your agent to _act_ on that knowledge by connecting to a real-world tool, everything changes.

Suddenly, you’re not writing agent logic anymore. You’re wrestling with OAuth libraries, parsing inconsistent API schemas, and drowning in boilerplate code just to get your agent to talk to Google Calendar or Slack. Your agent's brilliant core is lost in a sea of infrastructure.

The developer pain point has shifted. We've gotten good at giving agents knowledge, but we're still struggling with the infrastructure required to let them _act_. This is where Context Engineering comes in, not as a buzzword, but as the discipline of building a stable, secure, and observable environment for your agent to use tools. And it’s a discipline that has been sorely lacking a platform.

This is why we built [ACI.dev](https://aci.dev/). It’s an open-source platform designed to handle the messy, frustrating infrastructure of tool use, so you can get back to building what matters: your agent's intelligence.

## Redefining Context Engineering: It's About the `Search-Execute` Loop

If you've followed AI development, you've heard of "prompt engineering." Context Engineering is the next evolution. While prompting is about giving the LLM a good _initial instruction_, context engineering is the practice of creating the right environment for your agent, continuously feeding its short-term memory with the right information so it can call the right tools and do the right things.

![Untitled diagram _ Mermaid Chart-2025-08-05-074534.png](attachment:f189ac6a-e68e-4ea2-bde8-78d1a5dc6f81:Untitled_diagram___Mermaid_Chart-2025-08-05-074534.png)

This context can include many things: chat history, user data, and retrieved documents. But for tool-using agents, the most critical and failure-prone part of the context is the tools themselves. That's why we believe true context engineering for agents boils down to perfecting two phases:

1. **Search (The "What"):** How does an agent find the _right_ tool for the job from a sea of possibilities?
2. **Execute (The "How"):** Once found, how does the agent use that tool _correctly_ and _securely_, with the right data and permissions?

Vanilla agent frameworks dump this entire burden on you and the LLM. The result is predictable: slow, unreliable agents that fail in confusing ways.

## The 'Search' Problem: How ACI.dev Tames Tool Overload

An agent with 100+ tools is like a developer with 100+ browser tabs open, and it's quickly overwhelmed. The LLM’s context window gets flooded, its responses slow to a crawl, and it inevitably picks the wrong tool.

You've seen this solved elegantly in tools like **Cursor**. When you ask it to "fix a bug," it doesn't blindly guess. It intelligently searches your codebase, references relevant files with `@` symbols, and might even consult documentation. It's selecting from a huge number of possible actions but only presents the most relevant ones to its underlying model. It's performing a "search" to narrow down the context.

ACI.dev solves this with its [**Unified MCP Server**](https://docs.aci.dev/mcp-servers/unified-mcp-server). Instead of flooding the context, the server exposes just two powerful meta-functions to your agent: `ACI_SEARCH_FUNCTIONS` and `ACI_EXECUTE_FUNCTION`. When a user asks, "Plan my trip to London," the agent first uses the search function. The server understands the intent and returns only the most relevant tools, like `search_flights`, `book_hotel`, and `find_restaurants`. The agent then uses the execute function to call the chosen tool.

![aci](https://raw.githubusercontent.com/aipotheosis-labs/aci/main/frontend/public/aci-architecture-intro.svg)

The LLM gets a clean, minimal context, and you get an agent that makes the right choice, fast.

## The 'Execute' Problem: Secure and Reliable Tool Calls

But finding the right tool is just the first step. The real challenge is executing it reliably, which involves three problems developers know all too well: authentication, permissions, and debugging.

### 1. Managed Authentication

If you've ever had to implement an OAuth2 flow from scratch, you know the pain. It's that multi-step dance of redirects, tokens, and refresh logic required for your app to "Sign in with Google." Now imagine making your agent do that.

ACI.dev handles the entire OAuth2 flow for the 600+ tools in its catalog. You connect your account once, and ACI.dev manages the token lifecycle securely, keeping sensitive credentials out of your agent's hands. Your tool definition becomes blissfully simple because the authentication nightmare is handled for you.

### 2. Natural Language Permissions

You wouldn't give a junior developer root access to your production database. So why give your agent unlimited permissions to your APIs? Instead of wrestling with complex IAM roles, ACI.dev lets you define what your agent is allowed to do in plain English. A simple configuration like `can use gmail_send only for sending messages to internal domains` gives you powerful, intuitive control.

## ACI.dev in Action

So how does this look in practice? You don't run a complex local server. You use the ACI.dev platform as a central hub to configure your apps and authentication, and then point your agent to it.

![Screenshot 2025-08-05 at 13-18-08 ACI.DEV Platform.png](attachment:aa39e14b-5f12-40d5-8ce0-403227bda985:Screenshot_2025-08-05_at_13-18-08_ACI.DEV_Platform.png)

For an agent running in a tool like Claude Desktop, you simply add this to your `config.json` to connect to the Unified MCP server:

```json
{
  "mcpServers": {
    "aci-mcp-unified": {
      "command": "uvx",
      "args": [
        "aci-mcp@latest",
        "unified-server",
        "--linked-account-owner-id",
        "<LINKED_ACCOUNT_OWNER_ID>"
      ],
      "env": {
        "ACI_API_KEY": "<YOUR_ACI_API_KEY>"
      }
    }
  }
}
```

And in your agent's code, using the [ACI Python SDK](https://docs.aci.dev/sdk/introduction) is straightforward. You can easily integrate it into any agentic framework, like LangChain. Notice how you just get the function definition from ACI and then handle the call, with all the complex logic abstracted away.

```python
from aci import ACI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage

# 1. Initialize ACI and get the function definitions you need
aci = ACI()
search_func = aci.functions.get_definition("BRAVE_SEARCH__WEB_SEARCH")
star_repo_func = aci.functions.get_definition("GITHUB__STAR_REPOSITORY")

# 2. Bind these tools to your LLM (e.g., with LangChain)
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools([search_func, star_repo_func])

# 3. In your agent loop, handle the function call via ACI
#    (The LLM will generate the tool_call object)
messages = [HumanMessage("Star the aipotheosis-labs/aci repo on GitHub.")]
ai_message = llm_with_tools.invoke(messages)
messages.append(ai_message)

for tool_call in ai_message.tool_calls:
    result = aci.handle_function_call(
        tool_call["name"],
        tool_call["args"],
        linked_account_owner_id="YOUR_USER_ID" # The user you're acting for
    )
    messages.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))

```

## The Payoff: From Infrastructure to Intelligence

Look at that Python snippet again. Notice what isn't there: no `requests-oauthlib`, no token storage, no refresh logic. So where did the authentication happen?

It happened once, on the [ACI.dev platform](https://platform.aci.dev/). You link your Google, Slack, or GitHub account through their standard, secure consent screen, and ACI.dev handles the entire token lifecycle on its servers. The storage, the refreshing, the secure injection into the final API call—it's all managed for you. Your agent simply says "use this tool for this user," and ACI.dev takes care of the rest.

This abstraction is the key. By offloading this entire class of problems, you're no longer worried about writing compatible API clients. You can now focus on the truly interesting challenges, like agentic memory and workflows.

## Build Agents, Not Boilerplate

Of course, tool-calling is one critical piece of a much larger puzzle. Robust agents also need well-managed memory, the ability to reason over structured data from knowledge bases, and thoughtful workflow engineering to handle complex, multi-step tasks.

But by handling the tool integration and auth layer, ACI.dev gives you the solid foundation you need to tackle those other challenges, like agentic memory and workflows. Stop wrestling with infrastructure and start building truly intelligent agents.

- [**Get started with ACI.dev for free**](https://aci.dev/)
- [**Check out the project on GitHub and give us a star!**](https://github.com/aipolabs/aci)
