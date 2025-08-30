import json
import os
import sys
from typing import Any, Dict, List


from dotenv import load_dotenv
from rich import print as rprint

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType
from prompts import PLAN_DECOMPOSER_PROMPT


load_dotenv()


def decompose_plan_to_searches(plan: str) -> str:
    """
    Takes a research plan from the ReWOO planner and converts it into a
    simple list of mem0.search() parameter dictionaries.
    """
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("Missing GEMINI_API_KEY in environment variables")

    model = ModelFactory.create(
        model_platform=ModelPlatformType.GEMINI,
        model_type="gemini-2.5-pro",
        api_key=gemini_api_key,
        model_config_dict={"temperature": 0.1, "max_tokens": 40000},
    )

    decomposer_agent = ChatAgent(
        system_message=BaseMessage.make_assistant_message(
            role_name="PlanDecomposer",
            content=PLAN_DECOMPOSER_PROMPT,
        ),
        model=model,
    )

    user_prompt = f"""Here is the research plan to decompose:

{plan}

Analyze this plan and return the simple JSON list of mem0.search() calls as specified in your system prompt."""

    response = decomposer_agent.step(
        BaseMessage.make_user_message(role_name="User", content=user_prompt)
    )

    return response.msg.content


if __name__ == "__main__":
    from rewoo_research_planner import ReWOOResearchPlanner
    from metadata_ingestion import get_database_metadata, get_filtered_memory

    filtered_mem = get_filtered_memory()
    metadata_json = get_database_metadata(filtered_memory=filtered_mem)
    if not metadata_json:
        rprint("Error: could not get metadata")
        sys.exit(1)

    planner = ReWOOResearchPlanner()
    user_query = "how many patients have diabetes here and what are their names"
    research_plan = planner.create_research_plan(user_query, metadata_json)
    if "error" in research_plan:
        rprint("Error: could not create research plan")
        sys.exit(1)

    actionable_searches = decompose_plan_to_searches(research_plan)
    rprint(actionable_searches)
