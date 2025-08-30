# CAMEL AI Cookbook: Pairing AI Agents with 600+ MCP Tools via ACI.dev

You can also check this cookbook in [Google Colab](https://colab.research.google.com/drive/1ssaxacH4ahbFcv0fz6azy7hX9yjEXYro?usp=sharing).

<div className="align-center">
  ⭐ *Visit [ACI.dev](https://aci.dev), join our [Discord](https://discord.gg/nnqFSzq2ne) or check our [Documentation](https://www.aci.dev/docs/introduction/overview)*
</div>


## The Frameworks
### What is CAMEL AI?

**CAMEL AI** (Communicative Agents for "Mind" Exploration of Large Language Model Society) is the world's first multi-agent framework designed for building autonomous, communicative agents that can collaborate to solve complex tasks. 

Unlike traditional single-agent systems, CAMEL *enables multiple AI agents to work together*, *maintain stateful memory* , and *evolve through interactions with their environment*. 

The framework **supports scalable systems** with **millions of agents** and focuses on minimal human intervention, making it *ideal for sophisticated automation workflows* and *research into multi-agent behaviors*.

### What is ACI.dev

**ACI.dev** is a platform that enhances AI agent capabilities by seamlessly connecting them to over 600+ tools through an advanced implementation of the **MCP (Model Context Protocol)** framework. It simplifies tool integration, authentication, and management of AI agents.

This cookbook demonstrates how to supercharge your **CAMEL AI agents** by connecting them to 600+ MCP tools seamlessly through **ACI.dev**.

## Index

- Understanding the evolution from traditional tooling to MCP
- How ACI.dev enhances vanilla MCP with better tool management
- Setting up CAMEL AI agents with ACI's MCP server
- Creating practical demos like GitHub repository management
- Best practices for multi-app AI workflows

This approach focuses on using **CAMEL with ACI.dev's enhanced MCP servers** to create more powerful and flexible AI agents.

## 📦 Installation

First, install the required packages for this cookbook:

```bash
pip install "camel-ai[all]==0.2.62" python-dotenv uv
```

> **Note:** This method uses `uv`, a fast Python installer and toolchain, to run the ACI.dev MCP server directly from the command line, as defined in our configuration script.

## 🔑 Setting Up API Keys

This cookbook uses multiple services that require API keys:

1. **ACI.dev API Key**: Sign up at [ACI.dev](https://aci.dev) and get your API key from Project Settings
2. **Google Gemini API Key**: Get your API key from [Google's API Console](https://console.developers.google.com/)
3. **Linked Account Owner ID**: This is provided when you connect apps in ACI.dev

The scripts will load these from environment variables, so you'll need to create a `.env` file.

## 🤖 Introduction

LLMs have been in the AI landscape for some time now and so are the tools powering them.

On their own, LLMs can crank out essays, spark creative ideas, or break down tricky concepts which in itself is pretty impressive.

But let's be real: without the ability to connect to the world around them, _they're just fancy word machines_. What turns them into real problem-solvers, capable of grabbing fresh data or tackling tasks, is **tooling**.

## 🔧 Traditional Tooling

**Tooling** is essentially a set of directions that tells an LLM how to _kick off a specific action when you ask for it._

Imagine it as **handing your AI a bunch of tasks to do**, it wasn't built for like - 
- Pulling in the latest info
- Performing Mathematical calculations
- Editing code files
- Creating PPTs out of thin air

The catch? **Historically, tooling has been a walled garden**. Every provider think *OpenAI, Cursor*, or others, has their own implementation of tooling, which creates a mismatch of setups that don't play nice together. It's a hassle for users and vendors alike.

## 🌐 MCP: The Better Tooling

Which is what **MCP** solves. **MCP** is like a universal connector, a _straightforward protocol that lets any LLM, agent, or editor hook up with tools from any source._

It's built on a client-server setup: the **client** (your LLM or agent) talks to the server (where the tools live). When you need something beyond the LLM's cutoff knowledge, like up-to-date docs, it doesn't flounder. It pings the MCP server, grabs the right function's details, runs it, and delivers the answer in plain English.

### MCP Architecture Example

**Problem**:

- HR manager must send 100 unique onboarding emails to clients.
- Manual process is slow, error-prone, and takes hours.

**Solution with MCP**:

- AI agent instructed to: "Draft 100 Gmail onboarding emails using client data from a spreadsheet."
- MCP server connects AI to Gmail and Google Sheets.
- Retrieves client details, drafts personalized emails, and queues them for review or sending.
- Saves hours, ensures accuracy.

**Limitations**:

- MCP ties tools to single apps, requires manual setup, lacks auto-tool selection.
- Has no method to provide a unified Authentication flow

## 🚀 Outdoing Vanilla MCP

### Why ACI.dev Takes MCP to the Next Level

MCP lays a strong groundwork, but it's got some gaps. Let's break down where it stumbles and how ACI.dev steps up to fix it.

With standard MCP:

- **One server, one app**: You're stuck running separate servers for each tool — like one for GitHub, another for Gmail — which gets messy fast.
- **Setup takes effort**: Every tool needs its own configuration, and dealing with OAuth for a bunch of them is a headache for a normal or enterprise user
- **No smart tool picks**: MCP can't figure out the right tool for a task — you've got to spell it all out ahead of time in the prompt to let the LLM know what tool to use and execute.

With these headaches in mind, ACI.dev built something better. Our platform ties AI to third-party software through tool-calling APIs, making integration and automation a breeze.

It does this by introducing **two ways** to access MCP servers:

- The **Apps MCP Server** and the **Unified MCP Server** to give your AI a cleaner way to tap into tools and data.

This setup gives you access to 600+ MCP tools in the palm of your hand and make it easy for you to access any tool via both these methods.

### How ACI.dev Levels Up MCP

- **All Your Apps, One Server** — ACI Apps MCP Server lets you set up tools like GitHub, Vercel, Cloudflare, and Gmail in one spot. It's a single hub for your AI's toolkit, keeping things simple.
- **Tools That Find Themselves** - Forget predefining every tool. Unified MCP Server uses functions like ACI_SEARCH_FUNCTION and ACI_EXECUTE_FUNCTION to let your AI hunt down and run the perfect tool for the job.
- **Smarter Context Handling** — MCP can bog down your LLM by stuffing its context with tools you don't need. ACI.dev keeps it lean, loading only what's necessary, when it's necessary, so your LLM has enough memory for actual token prediction.
- **Smooth Cross-App Flows** — ACI.dev makes linking apps seamless without jumping between servers.
- **Easy Setup, and Authentication** - Configuring tools individually can be time-consuming, but ACI simplifies the process by centralizing everything. Manage accounts, API keys, and settings in one hub. Just add apps from the ACI App Store, enable them in Project Settings, and link them with a single linked-account-owner-id. Done.

## 🛠️ Tutorial: Two Ways to Integrate CAMEL AI with ACI

Alright, we've covered how MCP and ACI.dev make LLMs way more than just word generators. Now, let's get our hands dirty with practical demos using CAMEL AI.
### Step 1: Signing Up and Setting Up Your ACI.dev Project

First things first, head to [ACI.dev](https://aci.dev) and sign up if you don't have an account. Once you're in, create a new project or pick one you've already got. This is your control hub for managing apps and snagging your API key.

![ACI Dashboard](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*3LoS4_biV27QxxQHKl3kcw.png)

### Step 2: Adding Apps in the ACI App Store

1. Zip over to the ACI App Store.
2. Search for the apps you want your agent to use. For our HR Assistant demo, you'll need to add **Gmail, Google Sheets, Google Calendar, Resend, and Notion**.
3. For each app, hit "Add," and follow the prompts to link your account. During the OAuth flow, you'll set a `linked-account-owner-id` (usually your email or a unique ID from ACI). Jot this down—you'll need it for your `.env` file.

![OAuth Flow](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*DvD7N7oRehBSxTahxZkebQ.png)

### Step 3: Enabling Apps and Grabbing Your API Key

1. Go to **Project Settings** and check the "Allowed Apps" section. Make sure all the apps you added are toggled on. If one is missing, flip that switch.
2. Copy your **API key** from this page and keep it safe. It's the golden ticket for connecting CAMEL AI to ACI's services.

![Project Settings](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*V22RnZyPGxbn15xteIrjZw.png)

### Step 4: Environment Variables Setup

Create a `.env` file in your project folder with these variables:

```bash
GEMINI_API_KEY="your_gemini_api_key_here" 
ACI_API_KEY="your_aci_api_key_here" 
LINKED_ACCOUNT_OWNER_ID="your_linked_account_owner_id_here"
```

Replace:

- `your_gemini_api_key_here` with your GEMINI API key for the Gemini model (get it from Google's API console)
- `your_aci_api_key_here` with the API key from ACI.dev's Project Settings
- `your_linked_account_owner_id_here` with the ID from the aci.dev platform

## Using the Apps MCP Server Approach

This method uses CAMEL's `MCPToolkit` to connect to ACI's **Apps MCP Server**. It offers a straightforward way to give your AI agent access to a pre-selected suite of powerful tools—like Gmail, Notion, and Google Calendar—all managed through a single configuration.

For this project, you need to create two Python scripts in the same directory:
1.  **`create_config.py`**: To initiate, load, and run the server configuration for our agent's tools.
2.  **`simple.py`**: To define and run our HR Assistant agent.

### The Configuration Script (`create_config.py`)

This script is responsible for setting up the connection to the ACI.dev Apps MCP Server. It dynamically creates a `config.json` file that tells CAMEL's `MCPToolkit` how to launch the server and which tools to activate.

Here is the complete code:

```python
import os
import json
from dotenv import load_dotenv


def create_config():
    """Create MCP config with all required ACI apps for the HR agent"""
    load_dotenv()

    aci_api_key = os.getenv("ACI_API_KEY")
    if not aci_api_key:
        raise ValueError("ACI_API_KEY environment variable is required")

    linked_account_owner_id = os.getenv("LINKED_ACCOUNT_OWNER_ID", "default_id")

    config = {
        "mcpServers": {
            "aci_apps": {
                "command": "uvx",
                "args": [
                    "aci-mcp",
                    "apps-server",
                    "--apps=GMAIL,GOOGLE_SHEETS,GOOGLE_CALENDAR,RESEND,NOTION",
                    "--linked-account-owner-id",
                    linked_account_owner_id,
                ],
                "env": {"ACI_API_KEY": aci_api_key},
            }
        }
    }

    # Write to config.json
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)

    print("✓ Config created successfully for: GMAIL, GOOGLE_SHEETS, GOOGLE_CALENDAR, RESEND, NOTION")
    return config


if __name__ == "__main__":
    create_config()
```

**What's happening here?**
- **Imports & Setup**: It loads the necessary libraries and the environment variables from your `.env` file.
- **`create_config()` Function**:
    - It retrieves your `ACI_API_KEY` and `LINKED_ACCOUNT_OWNER_ID`.
    - It constructs a `config` dictionary that defines the server command. The key part is `"command": "uvx"` and the `args` list, which instructs the toolkit to run an `aci-mcp apps-server`.
    - The `--apps` flag specifies exactly which tools our agent can use. Here, we're activating tools for Gmail, Google Sheets, Google Calendar, Resend, and Notion.
    - Finally, it writes this configuration to a `config.json` file.

### The HR Assistant Agent (`simple.py`)

This script defines our AI agent. It uses the configuration from the previous step to connect to the ACI tools and then enters an interactive loop where you can give it tasks.

```python
import asyncio
import os
from dotenv import load_dotenv
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.toolkits import MCPToolkit
from camel.types import ModelPlatformType
from create_config import create_config

load_dotenv()

async def run_hr_assistant(mcp_toolkit: MCPToolkit):
    """
    Creates and runs a conversational HR Assistant agent.
    """
    # 1. Define the Agent's Persona and Capabilities
    hr_system_prompt = BaseMessage.make_assistant_message(
        role_name="HRAssistant",
        content="""You are a helpful and proactive HR Assistant. Your primary role is to help with recruitment and employee management tasks.

**Your Guiding Principles:**
1.  **Be Concise:** When using tools to search for information (like emails), provide a brief summary. For example, list email subjects and senders instead of the entire email body.
2.  **Clarify Ambiguity:** If a request is vague (e.g., "check my email"), ask for clarification. For example: "To narrow the search, could you provide a sender, keyword, or timeframe?"
3.  **Execute Directly:** Perform the requested actions using your tools without asking for confirmation.

**Your Tools:**
-   **Gmail**: Search emails by sender, subject, or keywords. *Remember to summarize.*
-   **Google Calendar**: Schedule meetings.
-   **Google Sheets**: Track data.
-   **Resend**: Send emails.
-   **Notion**: Manage records.

Your goal is to be an efficient and intelligent assistant. How can I help you today?""",
    )

    # 2. Create the AI Agent
    model = ModelFactory.create(
        model_platform=ModelPlatformType.GEMINI,
        model_type="gemini-2.5-pro-preview-05-06",
        api_key=os.getenv("GOOGLE_API_KEY"),
        model_config_dict={"temperature": 0.2, "max_tokens": 8000},
    )

    tools = mcp_toolkit.get_tools()

    agent = ChatAgent(
        model=model, system_message=hr_system_prompt, tools=tools, memory=None
    )
    agent.reset()

    print("\nHR Assistant is ready!")
    print("Type your requests below. Type 'exit' or 'quit' to end.\n")

    # 3. Start Interactive Conversation Loop
    try:
        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in ["exit", "quit", "bye"]:
                print("HR Assistant signing off. Goodbye!")
                break

            if not user_input:
                continue

            user_message = BaseMessage.make_user_message(
                role_name="User", content=user_input
            )

            print("\nAssistant is thinking...")
            response = await agent.astep(user_message)

            if response and hasattr(response, "msgs") and response.msgs:
                for msg in response.msgs:
                    print(f"HR Assistant: {msg.content}")
            else:
                print("Sorry, I couldn't respond.")

    except KeyboardInterrupt:
        print("\nSession ended by user.")


async def main():
    """
    Initializes the application and services.
    """
    print("Initializing Services...")
    create_config()
    mcp_toolkit = MCPToolkit(config_path="config.json")
    await mcp_toolkit.connect()
    print("Services Initialized.")

    try:
        await run_hr_assistant(mcp_toolkit)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        await mcp_toolkit.disconnect()
        print("\nDisconnected from services. Program ended.")


if __name__ == "__main__":
    asyncio.run(main())


## Example Queries

You can modify the user query to ask different questions, such as:

- "Did I receive any emails with 'job application' in the subject today? Please summarize them."
- "Check my calendar for any interviews scheduled for tomorrow."
- "Draft an email to 'candidate@email.com' with the subject 'Interview Availability' and a brief message asking for their schedule next week."

## 🎯 Conclusion

The world of AI agents and tooling is buzzing with potential, and MCP is a solid step toward making LLMs more than just clever chatbots.

In this cookbook, you've learned how to:
- Use ACI.dev's **Apps MCP Server** to easily provide tools to a CAMEL agent.
- Structure a project with a separate configuration script for clarity.
- Write a powerful system prompt to guide agent behavior effectively.
- Create a practical, interactive AI agent that can connect to and use external services like Gmail and Google Calendar.

As new ideas and implementations pop up in the agentic space, it's worth staying curious and watching for what's next. The future's wide open, and tools like these are just the start.

**Happy coding!**

---

That's everything! Got questions about ACI.dev? Join us on [Discord](https://discord.gg/nnqFSzq2ne)! Whether you want to share feedback, explore the latest in AI agent tooling, get support, or connect with others on exciting projects, we'd love to have you in the community! 🤝

Check out our documentation:
- 📚 [ACI.dev Documentation](https://www.aci.dev/docs/introduction/overview)
- 🚀 [Getting Started Guide](https://www.aci.dev/docs/introduction/overview)
- 🐪 [CAMEL-AI Org](https://www.camel-ai.org/)
- 🌵[CAMEL-AI Docs](https://docs.camel-ai.org)

Thanks from everyone at ACI.dev

<div className="align-center">
  <br/>
  ⭐ *Visit [ACI.dev](https://aci.dev), join our [Discord](https://discord.gg/nnqFSzq2ne) or check our [Documentation](https://www.aci.dev/docs/introduction/overview)*
</div>