import os
import json
from dotenv import load_dotenv


def create_config(linked_account_owner_id: str | None = None):
    """Create MCP config with proper environment variable substitution"""
    load_dotenv()

    aci_api_key = os.getenv("ACI_API_KEY")
    if not aci_api_key:
        raise ValueError("ACI_API_KEY environment variable is required")

    # Prioritize argument, then environment variable, then error
    final_linked_account_id = linked_account_owner_id or os.getenv("LINKED_ACCOUNT_OWNER_ID")
    
    if not final_linked_account_id:
        raise ValueError(
            "LINKED_ACCOUNT_OWNER_ID is required. "
            "Pass it as an argument or set it as an environment variable."
        )
    
    # The placeholder in the original file was <YOUR_LINKED_ACCOUNT_ID>
    # We should check against that specific string if it's a concern for copy-paste.
    # For now, we assume any value that is not None is potentially valid,
    # but a more specific placeholder check might be "<YOUR_LINKED_ACCOUNT_ID>"
    if final_linked_account_id == "<YOUR_LINKED_ACCOUNT_ID>" or final_linked_account_id == "<YOUR_LINKED_ACCOUNT_OWNER_ID>":
        raise ValueError(
            "Placeholder value detected for LINKED_ACCOUNT_OWNER_ID. "
            "Please provide your actual Linked Account Owner ID."
        )

    config = {
        "mcpServers": {
            "aci_apps": {
                "command": "uvx",
                "args": [
                    "aci-mcp",
                    "apps-server",
                    "--apps=BRAVE_SEARCH,GITHUB,ARXIV",
                    "--linked-account-owner-id",
                    final_linked_account_id,  # Use the resolved ID
                ],
                "env": {"ACI_API_KEY": aci_api_key},
            }
        }
    }

    # Write to config.json
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)

    print(f"✓ Config created successfully with API key and Linked Account Owner ID: {final_linked_account_id}")
    return config


if __name__ == "__main__":
    try:
        # Attempt to create config using LINKED_ACCOUNT_OWNER_ID from .env
        create_config() 
    except ValueError as e:
        print(f"Error during direct execution: {e}")
        print("If running directly, ensure LINKED_ACCOUNT_OWNER_ID is set in your .env file.")
