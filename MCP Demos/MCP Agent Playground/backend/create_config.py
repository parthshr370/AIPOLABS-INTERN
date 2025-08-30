import os
import json
from pathlib import Path
from dotenv import load_dotenv


CONFIG_PATH = Path(__file__).resolve().parent / "config.json"


def create_config() -> dict:
    """Create an MCP config.json file if it doesn't exist.

    The file will be written next to this script (i.e. inside the *backend* folder).
    Environment variable `ACI_API_KEY` must be set.
    """
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

    # Only write if file doesn't exist or contents differ
    if not CONFIG_PATH.exists() or json.loads(CONFIG_PATH.read_text()) != config:
        CONFIG_PATH.write_text(json.dumps(config, indent=2))
        print(f"✓ Config written to {CONFIG_PATH.relative_to(Path.cwd())}")
    else:
        print("✓ Config already up to date")

    return config


if __name__ == "__main__":
    create_config() 