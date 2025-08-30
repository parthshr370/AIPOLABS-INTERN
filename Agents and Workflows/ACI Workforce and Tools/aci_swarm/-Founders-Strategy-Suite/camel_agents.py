from camel.models import ModelFactory
from camel.types import ModelType, ModelPlatformType
from camel.configs import MistralConfig
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.toolkits.search_toolkit import SearchToolkit
from prompts import *


mistral_model = ModelFactory.create(
    model_platform=ModelPlatformType.MISTRAL,
    model_type=ModelType.MISTRAL_LARGE,
    model_config_dict=MistralConfig(temperature=0.7).as_dict(),
)


search_tools = SearchToolkit().get_tools()

def run_agent(system_prompt, user_query):
    agent = ChatAgent(
        system_message=system_prompt,
        message_window_size=10,
        model=mistral_model,
        tools=search_tools  
    )
    user_msg = BaseMessage.make_user_message(role_name="user", content=user_query)
    response = agent.step(user_msg).msg.content
    return response

def idea_validator_agent(query):
    return run_agent(idea_system_prompt, query)

def business_model_agent(query):
    return run_agent(business_model_prompt, query)

def pitch_deck_agent(query):
    return run_agent(pitch_deck_prompt, query)

def ui_design_agent(query):
    return run_agent(ui_design_prompt, query)

def growth_strategy_agent(query):
    return run_agent(growth_prompt, query)

def monetization_agent(query):
    return run_agent(monetization_prompt, query)

def market_research_agent(query):
    return run_agent(market_research_prompt, query) 
