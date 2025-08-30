"""
Simple iterative agent that searches mem0 until it finds answers
Uses short queries like simple_react_agent.py
"""

import os
import sys
import json

from dotenv import load_dotenv

load_dotenv()

from mem0.client.main import MemoryClient
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType

# Config
USER_ID = "doctor_memory"
MEM0_API_KEY = os.getenv("MEM0_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not MEM0_API_KEY or not GEMINI_API_KEY:
    print("Missing API keys!")
    exit(1)


class SimpleLoopAgent:
    def __init__(self):
        self.mem0 = MemoryClient(api_key=MEM0_API_KEY)

        # Simple model setup like camel_mem0_agent.py
        self.model = ModelFactory.create(
            model_platform=ModelPlatformType.GEMINI,
            model_type=ModelType.GEMINI_2_5_PRO,
            api_key=GEMINI_API_KEY,
            model_config_dict={"temperature": 0.2},
        )

    def search_and_think(self, query):
        """Simple search + think cycle"""
        print(f"\n🔍 Searching: {query}")

        # Search mem0 with simple params
        results = self.mem0.search(
            query=query,
            user_id=USER_ID,
            limit=5,  # Small limit
            threshold=0.5,  # Lower threshold to get more results
        )

        print(f"Found {len(results)} results")

        if not results:
            return [], "No results found"

        # Show raw results
        print(results)

        # Format for agent
        context = ""
        for i, result in enumerate(results, 1):
            memory = result.get("memory", "")
            metadata = result.get("metadata") or {}  # Handle None metadata
            patient = metadata.get("patient_name", "Unknown")
            context += f"{i}. [{patient}] {memory}\n"

        return results, context

    def decide_next_step(self, original_question, all_context, iteration, raw_results):
        """Agent decides what to do next"""

        # Extract key info from raw results for JSON summary
        json_summary = []
        for result in raw_results:
            metadata = result.get('metadata') or {}  # Handle None metadata
            json_summary.append({
                "patient_name": metadata.get('patient_name', 'Unknown'),
                "memory": result.get('memory', ''),
                "score": result.get('score', 0)
            })

        prompt = f"""You are helping answer: {original_question}

Information found so far:
{all_context}

This is iteration {iteration}. You need to decide:
1. Do we have enough info to answer the question? (YES/NO)
2. If NO, what SHORT search term should we try next? (2-3 words only)

Respond in this format:
ENOUGH_INFO: YES or NO
NEXT_SEARCH: short search term (only if ENOUGH_INFO is NO)
REASONING: brief explanation
FOUND_DATA: {json.dumps(json_summary, indent=2)}
"""

        # Create simple agent
        agent = ChatAgent(
            system_message=BaseMessage.make_assistant_message(
                role_name="Decider",
                content="You analyze medical information and decide search strategy. Keep searches SHORT and SIMPLE.",
            ),
            model=self.model,
        )

        response = agent.step(
            BaseMessage.make_user_message(role_name="User", content=prompt)
        )
        return response.msg.content

    def answer_question(self, question, all_context):
        """Generate final answer from all context"""

        prompt = f"""Question: {question}

All information gathered:
{all_context}

Provide a comprehensive answer based on this information."""

        agent = ChatAgent(
            system_message=BaseMessage.make_assistant_message(
                role_name="Answerer",
                content="You provide clear, helpful answers based on medical data.",
            ),
            model=self.model,
        )

        response = agent.step(
            BaseMessage.make_user_message(role_name="User", content=prompt)
        )
        return response.msg.content

    def refine_query(self, user_question):
        """Convert user question into mem0-friendly search terms"""

        prompt = f"""User asked: {user_question}

Convert this into a SHORT search term (1-3 words) that would find relevant medical records.

Examples:
"What is the average age of diabetic patients?" → "diabetes patients"
"How many people have heart disease?" → "heart disease"
"What treatments work for pain?" → "pain treatment"

Respond with just the search term, nothing else."""

        agent = ChatAgent(
            system_message=BaseMessage.make_assistant_message(
                role_name="QueryRefiner",
                content="You convert user questions into short, effective search terms for medical databases.",
            ),
            model=self.model,
        )

        response = agent.step(
            BaseMessage.make_user_message(role_name="User", content=prompt)
        )
        refined = response.msg.content.strip()
        print(f"🔧 Refined query: '{user_question}' → '{refined}'")
        return refined

    def research_loop(self, question):
        """Main research loop - simple and effective"""
        print(f"\n=== Researching: {question} ===")

        all_context = ""
        max_iterations = 4

        # Start with refined query instead of raw user input
        current_search = self.refine_query(question)

        for iteration in range(1, max_iterations + 1):
            print(f"\n--- Iteration {iteration} ---")

            # Search and get results
            results, context = self.search_and_think(current_search)

            # Add to accumulated context
            if context != "No results found":
                all_context += f"\nIteration {iteration} - Searched '{current_search}':\n{context}\n"

            # If no results, try simpler search
            if not results and iteration < max_iterations:
                words = current_search.split()
                if len(words) > 1:
                    current_search = words[0]  # Just use first word
                    print(f"No results, trying simpler: {current_search}")
                    continue
                else:
                    print("No results with simple search either")
                    break

            # Decide next step
            if iteration < max_iterations:
                decision = self.decide_next_step(question, all_context, iteration, results)
                print(f"\n🤔 Decision: {decision}")

                # Parse decision
                if "ENOUGH_INFO: YES" in decision:
                    print("✅ Enough information gathered!")
                    break

                # Extract next search
                next_search = None
                for line in decision.split("\n"):
                    if "NEXT_SEARCH:" in line:
                        next_search = line.split("NEXT_SEARCH:")[1].strip()
                        break

                if next_search:
                    current_search = next_search
                else:
                    print("No next search found, stopping")
                    break

        # Generate final answer
        print(f"\n🎯 Generating final answer...")
        if all_context.strip():
            final_answer = self.answer_question(question, all_context)
        else:
            final_answer = "I couldn't find relevant information in the database to answer your question."

        return final_answer


def main():
    """Simple main loop"""
    print("Simple Loop Agent - Medical Research")
    print("Ask questions and I'll search iteratively until I find answers")
    print("Type 'exit' to quit\n")

    agent = SimpleLoopAgent()

    while True:
        try:
            question = input("\nYour question: ").strip()

            if question.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            if not question:
                continue

            # Do the research
            answer = agent.research_loop(question)

            print(f"\n{'=' * 60}")
            print("FINAL ANSWER:")
            print(f"{'=' * 60}")
            print(answer)
            print(f"{'=' * 60}")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
