import json
import os
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType

from config import GEMINI_API_KEY


def create_llm_agent(system_prompt: str = None, temperature: float = 0.2) -> ChatAgent:
    """Creates and configures a ChatAgent with a Gemini model."""
    model = ModelFactory.create(
        model_platform=ModelPlatformType.GEMINI,
        model_type=ModelType.GEMINI_2_5_PRO,
        api_key=GEMINI_API_KEY,
        model_config_dict={"temperature": temperature},
    )
    
    system_message = BaseMessage.make_assistant_message(
        role_name="Assistant",
        content=system_prompt or "You are a helpful assistant.",
    )
    
    return ChatAgent(system_message=system_message, model=model)


def load_prompt(prompt_name: str) -> str:
    """Loads a specific prompt from prompts.txt file."""
    try:
        prompts_file = os.path.join(os.path.dirname(__file__), "prompts.txt")
        with open(prompts_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split prompts by the delimiter
        prompts = {}
        sections = content.split('\n\n')
        
        for section in sections:
            if '|' in section:
                lines = section.split('\n')
                if lines and '|' in lines[0]:
                    name, first_line = lines[0].split('|', 1)
                    prompt_content = first_line
                    if len(lines) > 1:
                        prompt_content += '\n' + '\n'.join(lines[1:])
                    prompts[name.strip()] = prompt_content.strip()
        
        return prompts.get(prompt_name, f"Prompt '{prompt_name}' not found. Available prompts: {list(prompts.keys())}")
        
    except FileNotFoundError:
        return f"prompts.txt file not found. Please ensure it exists in the project directory."
    except Exception as e:
        return f"Error loading prompt: {e}"


def parse_json_from_response(response: str) -> dict:
    """Extracts a JSON object from a string response."""
    try:
        # Find the start and end of the JSON block
        start_index = response.find("```json")
        end_index = response.rfind("```")
        
        if start_index != -1:
            # Extract the JSON string and load it
            json_str = response[start_index + 7:end_index].strip()
            return json.loads(json_str)
        else:
            # Try to parse the entire response as JSON
            return json.loads(response.strip())
            
    except (json.JSONDecodeError, IndexError):
        # Fallback for non-JSON or malformed responses
        pass
        
    return None
