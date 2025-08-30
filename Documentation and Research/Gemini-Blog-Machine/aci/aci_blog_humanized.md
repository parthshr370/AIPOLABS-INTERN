# How ACI.dev Solves Tool Overload in Context Engineering

You've built an AI agent. It's clever, it's promising, and it works perfectly on your local machine.

As developers, we've gotten pretty good at creating context silos for our agents' knowledge, feeding them our entire codebase or a library's documentation so they can answer questions accurately. But the moment you need your agent to _act_ on that knowledge by connecting to a real-world tool, everything changes.

Suddenly, your agent's context window is flooded with tool definitions, authentication details, and API schemas. What used to be clean, focused context becomes a mess of boilerplate that drowns out the important stuff. Your agent's brilliant core gets lost in context pollution, not infrastructure complexity.

This is a context engineering problem. Most developers are solving it badly.

## What Context Engineering Actually Is

If you've followed AI development, you've heard of "prompt engineering." Context engineering is the next step, but it's not about better prompts. It's the filling of an LLM's context window with exactly the right information for each step of a task.

Recent research shows context in AI systems includes nine components:

- System prompts and instructions
- User input and chat history
- Short and long-term memory
- Retrieved knowledge base information
- Tool definitions and their schemas
- Tool responses and feedback
- Structured outputs and data formats
- Global state across agent interactions

The challenge is to incorporate these components while balancing them within strict context window limits. Models start degrading around 32,000 tokens, and smaller models hit limits much earlier. Every token counts.

Here's where most developers run into trouble: tools are context hogs.

## The Tool Context Problem

An agent with 100+ tools is like a developer with 100+ browser tabs open. But instead of just being overwhelmed, your agent's context window gets flooded with verbose API schemas, authentication requirements, and parameter definitions. The important stuff (your actual task context, memory, and retrieved knowledge) gets squeezed out.

![Untitled diagram _ Mermaid Chart-2025-08-05-074534.png](attachment:f189ac6a-e68e-4ea2-bde8-78d1a5dc6f81:Untitled_diagram___Mermaid_Chart-2025-08-05-074534.png)

You've seen this solved elegantly in tools like **Cursor**. When you ask it to "fix a bug," it doesn't blindly guess from every possible file in your codebase. It smartly searches, references relevant files with `@` symbols, and presents only what matters to the model. Smart context curation.

This is where [ACI.dev](https://aci.dev/) fits into your context engineering strategy. We built it to solve the tool context optimization problem, freeing up context window space for the stuff that really matters: your agent's reasoning, memory, and task-specific knowledge.

ACI.dev offers two approaches: a **Unified MCP Server** for MCP-compatible environments, and a **Python SDK** for custom integrations. Both solve the same core problem—optimizing how tools consume your context budget.

## Smart Context Optimization: The Search-Execute Pattern

Instead of cramming hundreds of tool schemas into your context window, ACI.dev's Unified MCP Server exposes just two meta-functions: `ACI_SEARCH_FUNCTIONS` and `ACI_EXECUTE_FUNCTION`.

When a user asks, "Plan my trip to London," your agent doesn't wade through 600+ tool definitions. It uses the search function first. The server understands the intent and returns only the relevant tools: `search_flights`, `book_hotel`, `find_restaurants`. Clean, minimal context.

![aci](https://raw.githubusercontent.com/aipotheosis-labs/aci/main/frontend/public/aci-architecture-intro.svg)

Then the agent uses the execute function to call the chosen tool. No verbose schemas, no authentication boilerplate cluttering your context. Just the information needed for the task.

## MCP Integration: Plug and Play Context Optimization

For environments that support MCP (like Claude Desktop), the integration is straightforward. Add this to your `config.json`:

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

That's it. Your agent now has access to 600+ tools through two clean functions instead of 600+ bloated schemas eating your context budget.

## SDK Integration: Custom Context Control

For custom implementations, the [ACI Python SDK](https://www.aci.dev/docs/sdk/intro) gives you the same context optimization benefits with more control:

```python
from aci import ACI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage

# 1. Get clean, minimal tool definitions
aci = ACI()
search_func = aci.functions.get_definition("BRAVE_SEARCH__WEB_SEARCH")
star_repo_func = aci.functions.get_definition("GITHUB__STAR_REPOSITORY")

# 2. Your context stays focused on what matters
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools([search_func, star_repo_func])

# 3. Clean execution without context pollution
messages = [HumanMessage("Star the aipotheosis-labs/aci repo on GitHub.")]
ai_message = llm_with_tools.invoke(messages)
messages.append(ai_message)

for tool_call in ai_message.tool_calls:
    result = aci.handle_function_call(
        tool_call["name"],
        tool_call["args"],
        linked_account_owner_id="YOUR_USER_ID"
    )
    messages.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
```

## The Authentication Context Problem

Tool schemas aren't the only context polluters. Authentication is worse.

If you've ever implemented OAuth2 from scratch, you know it's complex and verbose. All that redirect logic, token management, and refresh handling? It either lives in your codebase (eating development time) or gets crammed into your agent's context (eating tokens).

ACI.dev handles the entire OAuth2 flow for 600+ tools. You connect your account once through standard consent screens, and we manage the token lifecycle on our servers. Your tool definitions stay clean because the authentication nightmare never touches your context window.

You can even set permissions in plain English: `can use gmail_send only for sending messages to internal domains`. No complex IAM schemas cluttering your agent's context.

## The Context Budget Payoff

Look at that Python snippet again. Notice what isn't polluting your context window: no verbose OAuth documentation, no complex API schemas, no token refresh boilerplate.

![Screenshot 2025-08-05 at 13-18-08 ACI.DEV Platform.png](attachment:aa39e14b-5f12-40d5-8ce0-403227bda985:Screenshot_2025-08-05_at_13-18-08_ACI.DEV_Platform.png)

The authentication happened once, on the [ACI.dev platform](https://platform.aci.dev/). The complex schemas got abstracted into simple function calls. Your agent's context budget gets spent on reasoning, memory, and task-specific knowledge instead of infrastructure boilerplate.

By optimizing how tools consume context, you free up space for the other eight components of context engineering that actually make your agent intelligent.

## Context Engineering, Not Just Tool Calling

Tool context is just one piece of the context engineering puzzle. Robust agents also need well-managed memory, smart knowledge retrieval, structured data processing, and thoughtful workflow engineering to handle complex, multi-step tasks.

But tool context optimization is often the lowest-hanging fruit for massive context window savings. By solving this piece cleanly, ACI.dev gives you the breathing room to tackle those other context engineering challenges properly.

Stop letting tool boilerplate eat your context budget. Start building agents that can actually think.

- [**Get started with ACI.dev for free**](https://aci.dev/)
- [**Check out the project on GitHub and give us a star!**](https://github.com/aipolabs/aci)
