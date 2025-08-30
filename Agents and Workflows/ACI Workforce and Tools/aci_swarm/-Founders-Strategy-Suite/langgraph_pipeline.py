from camel_agents import (
    idea_validator_agent,
    pitch_deck_agent,
    monetization_agent
)
from langgraph.graph import StateGraph, END

def validate_idea(state):
    query = state["input"]
    validated = idea_validator_agent(query)
    return {"validated_idea": validated}

def generate_pitch(state):
    validated_idea = state.get("validated_idea")
    pitch = pitch_deck_agent(validated_idea)
    return {"pitch": pitch}

def generate_monetization(state):
    pitch_content = state.get("pitch")
    monetization = monetization_agent(pitch_content)
    return {"monetization": monetization}

workflow = StateGraph()
workflow.add_node("Validate Idea", validate_idea)
workflow.add_node("Generate Pitch", generate_pitch)
workflow.add_node("Generate Monetization", generate_monetization)

workflow.set_entry_point("Validate Idea")
workflow.add_edge("Validate Idea", "Generate Pitch")
workflow.add_edge("Generate Pitch", "Generate Monetization")
workflow.add_edge("Generate Monetization", END)

graph_executor = workflow.compile()

def run_pipeline(startup_idea: str) -> dict:
    return graph_executor.invoke({"input": startup_idea})
