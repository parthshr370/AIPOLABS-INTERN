#!/bin/bash

# Create the main project directory
mkdir -p object_detection_project
cd object_detection_project

# Create the object_agent.py file
cat << 'EOF' > object_agent.py
import asyncio
import os
from dotenv import load_dotenv
from rich import print as rprint

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.toolkits import MCPToolkit
from camel.types import ModelPlatformType
from create_config import create_config

load_dotenv()


async def main():
    """
    Main function to run the Object Detection Agent.
    """
    create_config()
    mcp_toolkit = MCPToolkit(config_path="config.json")
    await mcp_toolkit.connect()

    agent_name = "ObjectDetectionAgent"
    system_message_content = (
        "You are a specialized Object Detection Agent. Your primary function is to use the `REPLICATE.run` tool for object detection and present the findings in a user-friendly format. "
        "The user will provide a text prompt containing an image URL and a query. You must extract the `image` URL and the `query` object(s). "
        "Immediately call the `REPLICATE.run` tool. The `input` must be a dictionary with two keys: `image` (the URL) and `query` (a string of the object(s)). "
        "Do not ask for clarification; make a reasonable inference if the query is ambiguous. "
        "After receiving the tool's output, format your response as follows: "
        "- **Natural Language Summary:** Start with a detailed friendly, insightful analysis of the detection results in plain English. "
        "- **Markdown Table:** Create a markdown table with columns: 'Object', 'Confidence Score', and 'Bounding Box Coordinates'. "
        "- **Result Image:** If the tool provides a URL for an image with bounding boxes, display it using markdown: `![Detected Objects](URL_HERE)`. "
        "Whenever I give you a link, trigger the tool call, extract its outputs and links, and present me in a proper markdown format with detailed analysis from the tool call in natural language."
    )

    tools = mcp_toolkit.get_tools()

    model = ModelFactory.create(
        model_platform=ModelPlatformType.GEMINI,
        model_type="gemini-1.5-flash",
        api_key=os.getenv("GOOGLE_API_KEY"),
        model_config_dict={"temperature": 0.0, "max_tokens": 4096},
    )

    sys_msg = BaseMessage.make_assistant_message(
        role_name=agent_name,
        content=system_message_content,
    )

    agent = ChatAgent(model=model, system_message=sys_msg, tools=tools, memory=None)

    rprint(
        f"[bold green]Started {agent_name}. Enter your request or type 'exit' to quit.[/bold green]"
    )
    rprint("[dim]Example: 'Find cars in this image: https://example.com/image.jpg'[/dim]")

    try:
        while True:
            user_input = input("\nYou: ").strip()

            if user_input.lower() in ["exit", "quit", "bye"]:
                rprint("[bold yellow]Exiting...[/bold yellow]")
                break

            if not user_input:
                continue

            user_message = BaseMessage.make_user_message(
                role_name="User", content=user_input
            )

            response = await agent.astep(user_message)

            if response and hasattr(response, "msgs") and response.msgs:
                for msg in response.msgs:
                    rprint(f"[bold blue]{agent_name}:[/bold blue]\n{msg.content}")

    except KeyboardInterrupt:
        rprint(f"[bold yellow]\nExiting due to KeyboardInterrupt...[/bold yellow]")
    finally:
        await mcp_toolkit.disconnect()
        rprint("[bold red]MCP Toolkit disconnected. Program ended.[/bold red]")


if __name__ == "__main__":
    asyncio.run(main())
EOF

# Create the create_config.py file
cat << 'EOF' > create_config.py
import os
import json
from dotenv import load_dotenv


def create_config():
    """Create MCP config with proper environment variable substitution"""
    load_dotenv()

    aci_api_key = os.getenv("ACI_API_KEY")
    if not aci_api_key:
        raise ValueError("ACI_API_KEY environment variable is required")

    config = {
        "mcpServers": {
            "aci_apps": {
                "command": "aci-mcp",
                "args": [
                    "apps-server",
                    "--apps=REPLICATE",
                    "--linked-account-owner-id",
                    "your_user_id",
                ],
                "env": {"ACI_API_KEY": aci_api_key},
            }
        }
    }

    # Write to config.json
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)

    print("✓ Config created successfully with API key")
    return config


if __name__ == "__main__":
    create_config()
EOF

# Create the example .env file
cat << 'EOF' > examples.env
# Rename this file to .env and fill in your API keys.

# Get your ACI_API_KEY from Another Cloud Inc.
ACI_API_KEY="your_aci_api_key_here"

# Get your Google API Key from Google AI Studio.
GOOGLE_API_KEY="your_google_api_key_here"
EOF

# Create the README.md file
cat << 'EOF' > README.md
# Object Detection Agent

This project contains a Python agent that uses AI to detect objects in images by leveraging the CAMEL AI framework and external tools.

## Prerequisites

- Python 3.8 or higher
- `pip` for package installation

## Setup Instructions

1.  **Save the Script:**
    Save the bash script above as `setup_project.sh`.

2.  **Make it Executable:**
    Open your terminal and run the following command to make the script executable:
    ```bash
    chmod +x setup_project.sh
    ```

3.  **Run the Script:**
    Execute the script to create the project directory and files.
    ```bash
    ./setup_project.sh
    ```

4.  **Navigate to the Project Directory:**
    ```bash
    cd object_detection_project
    ```

5.  **Create and Activate a Virtual Environment:**
    It is highly recommended to use a virtual environment to manage dependencies.
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
    On Windows, use `venv\Scripts\activate`.

6.  **Install Dependencies:**
    Install the necessary Python packages using pip.
    ```bash
    pip install python-dotenv rich camel-ai another-cloud-io
    ```

7.  **Configure Environment Variables:**
    Rename the `examples.env` file to `.env` and add your API keys.
    ```bash
    mv examples.env .env
    ```
    Now, edit the `.env` file and replace the placeholder values with your actual keys.

## How to Run

Once the setup is complete, you can start the agent with the following command:

```bash
python object_agent.py
