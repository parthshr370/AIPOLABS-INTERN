import os
import json
from dotenv import load_dotenv

# Agent configurations with their tools and API key environment variables
AGENT_CONFIGS = {
    "social": {
        "tools": ["DISCORD", "REDDIT"],
        "api_key_env": "SOCIAL_API_KEY"
    },
    "search_genius": {
        "tools": ["EXA_AI", "ARXIV", "GOOGLE_MAPS"],
        "api_key_env": "SEARCH_GENIUS_API_KEY"
    },
    "web_crawler": {
        "tools": ["BROWSERBASE", "BRAVE_SEARCH", "STEEL"],
        "api_key_env": "WEB_CRAWLER_API_KEY"
    },
    "researcher": {
        "tools": ["ARXIV", "HACKERNEWS"],
        "api_key_env": "RESEARCHER_API_KEY"
    },
    "slack_manager": {
        "tools": ["SLACK"],
        "api_key_env": "SLACK_MANAGER_API_KEY"
    },
    "marketing": {
        "tools": ["GOOGLE_ANALYTICS_ADMIN", "CODA"],
        "api_key_env": "MARKETING_API_KEY"
    },
    "visual_alchemist": {
        "tools": ["FIGMA"],
        "api_key_env": "VISUAL_ALCHEMIST_API_KEY"
    },
    "code_ninja": {
        "tools": ["GITHUB", "VERCEL", "AGENT_SECRETS_MANAGER"],
        "api_key_env": "CODE_NINJA_API_KEY"
    },
    "crypto": {
        "tools": ["COINMARKETCAP", "SOLSCAN"],
        "api_key_env": "CRYPTO_API_KEY"
    },
    "content_king": {
        "tools": ["ELEVEN_LABS", "YOUTUBE", "RESEND"],
        "api_key_env": "CONTENT_KING_API_KEY"
    },
    "document_master": {
        "tools": ["GOOGLE_DOCS", "CODA"],
        "api_key_env": "DOCUMENT_MASTER_API_KEY"
    },
    "hr_sales": {
        "tools": ["GMAIL"],
        "api_key_env": "HR_SALES_API_KEY"
    },
    "memory": {
        "tools": ["NOTION"],
        "api_key_env": "MEMORY_API_KEY"
    }
}

def create_agent_config(agent_name: str):
    """Create individual config file for an agent"""
    load_dotenv()
    
    if agent_name not in AGENT_CONFIGS:
        print(f"Error: Agent '{agent_name}' not found")
        return False
    
    agent_config = AGENT_CONFIGS[agent_name]
    api_key = os.getenv(agent_config["api_key_env"])
    
    if not api_key:
        print(f"Error: {agent_config['api_key_env']} not found in environment")
        return False
    
    tools_string = ",".join(agent_config["tools"])
    
    config = {
        "mcpServers": {
            "aci_apps": {
                "command": "uvx",
                "args": [
                    "aci-mcp",
                    "apps-server",
                    f"--apps={tools_string}",
                    "--linked-account-owner-id",
                    "your_user_id"
                ],
                "env": {
                    "ACI_API_KEY": api_key
                }
            }
        }
    }
    
    config_filename = f"configs/config_{agent_name}.json"
    with open(config_filename, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Created {config_filename}")
    return True

def create_all_configs():
    """Create config files for all agents"""
    print("Creating agent configurations...")
    
    success_count = 0
    for agent_name in AGENT_CONFIGS:
        if create_agent_config(agent_name):
            success_count += 1
    
    print(f"Created {success_count}/{len(AGENT_CONFIGS)} configurations")
    
    if success_count < len(AGENT_CONFIGS):
        print("Some configurations failed. Check your .env file for missing API keys.")

if __name__ == "__main__":
    create_all_configs() 