"""
Main coordinator for deep memory research pipeline
Flows: metadata_ingestion -> rewoo_research_planner -> user query processing
"""

import sys
import json
import os

# Add parent directory and required modules to Python path
sys.path.append('..')
sys.path.append('../mem0')
sys.path.append('../camel')

from rich import print as rprint
from metadata_ingestion import get_database_metadata, get_filtered_memory
from test_react import decompose_plan_to_searches
from rewoo_research_planner import ReWOOResearchPlanner


def main():
    rprint("Deep Memory Research Pipeline")

    # Step 1: Inspect filtered memory from mem0
    filtered = get_filtered_memory()
    rprint("Filtered memory (truncated to first 5 items):")
    rprint(filtered[:5])

    # Step 2: Generate metadata JSON from filtered memory
    metadata_json = get_database_metadata(filtered_memory=filtered)
    if not metadata_json:
        rprint("Error: could not get database metadata")
        return
    rprint("Metadata JSON:")
    try:
        parsed = json.loads(metadata_json)
        rprint(json.dumps(parsed, indent=2))
    except json.JSONDecodeError:
        rprint(metadata_json)

    # Step 3: Initialize planner
    planner = ReWOOResearchPlanner()
    rprint("Planner ready")

    # Interactive loop
    while True:
        try:
            user_query = input("\nQuery: ").strip()

            if user_query.lower() in ["exit", "quit"]:
                rprint("Bye")
                break

            if not user_query:
                continue

            # Step 4: Build plan for the query
            research_plan = planner.create_research_plan(user_query, metadata_json)
            rprint("Research plan:")
            rprint(research_plan)

            # Step 5: Decompose plan into actionable mem0.search calls
            rprint("Actionable mem0.search calls:")
            actions = decompose_plan_to_searches(research_plan)
            rprint(actions)

        except KeyboardInterrupt:
            rprint("Interrupted. Bye")
            break
        except Exception as e:
            rprint(f"Error: {e}")


if __name__ == "__main__":
    main()