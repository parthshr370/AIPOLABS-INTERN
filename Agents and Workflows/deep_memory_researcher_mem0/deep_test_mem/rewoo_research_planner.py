import os
import sys
import json
import warnings

# Add parent directory and required modules to Python path
sys.path.append('..')
sys.path.append('../mem0')
sys.path.append('../camel')

from dotenv import load_dotenv
# Load environment variables FIRST
load_dotenv()

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from prompts import STRATEGIC_PLANNING_SYSTEM_PROMPT, STRATEGIC_PLANNING_USER_PROMPT

# Suppress warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in environment variables")

class ReWOOResearchPlanner:
    """
    Strategic Research Planner Agent
    Creates multi-phase investigation plans based on user intent and available data
    """
    
    def __init__(self):
        self.model = ModelFactory.create(
            model_platform=ModelPlatformType.GEMINI,
            model_type="gemini-2.5-flash-lite",
            api_key=GEMINI_API_KEY,
            model_config_dict={"temperature": 0.3, "max_tokens": 40000},
        )
        
        # Create strategic planner agent
        self.planner_agent = ChatAgent(
            system_message=BaseMessage.make_assistant_message(
                role_name="StrategicPlanner",
                content=STRATEGIC_PLANNING_SYSTEM_PROMPT,
            ),
            model=self.model,
        )
    
    def create_research_plan(self, user_query: str, metadata_json: str) -> str:
        """
        Create a strategic multi-phase research plan
        
        Args:
            user_query: The research question from user
            metadata_json: Database metadata as string from metadata_ingestion.py
            
        Returns:
            str: Strategic research plan as JSON string
        """
        
        # Simple prompt injection - let the LLM do all the strategic thinking
        planning_prompt = STRATEGIC_PLANNING_USER_PROMPT.format(
            user_query=user_query,
            metadata_json=metadata_json
        )
        
        # Get strategic research plan
        response = self.planner_agent.step(
            BaseMessage.make_user_message(role_name="User", content=planning_prompt)
        )
        
        # Return raw response without parsing
        return response.msg.content
