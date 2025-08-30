"""
Iterative React Agent with mem0 search loop
Continuously searches and refines queries until finding satisfactory answers
"""

import os
import sys
import warnings
from typing import Dict, List, Any

from dotenv import load_dotenv

load_dotenv()

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from mem0.client.main import MemoryClient

# Suppress warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Configuration
USER_ID = "doctor_memory"
MEM0_API_KEY = os.getenv("MEM0_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

console = Console()

if not MEM0_API_KEY or not GEMINI_API_KEY:
    console.print("[red]Error: Missing API keys in environment variables[/red]")
    exit(1)


class IterativeReactAgent:
    """
    React Agent that iteratively searches mem0 data until finding satisfactory answers
    """

    def __init__(self, max_iterations: int = 5):
        self.mem0_client = MemoryClient(api_key=MEM0_API_KEY)
        self.max_iterations = max_iterations

        # Create CAMEL model
        self.model = ModelFactory.create(
            model_platform=ModelPlatformType.GEMINI,
            model_type=ModelType.GEMINI_2_5_PRO,
            api_key=GEMINI_API_KEY,
            model_config_dict={"temperature": 0.3, "max_tokens": 40000},
        )

        # System prompt for the React agent
        self.system_prompt = """You are an iterative research agent. Your job is to search through medical data to find comprehensive answers.

SEARCH LOOP PROCESS:
1. **ANALYZE** the current query and any previous search results
2. **DECIDE** if you have enough information to provide a complete answer
3. **SEARCH** with a new/refined query if more information is needed
4. **REPEAT** until you have comprehensive information

DECISION CRITERIA:
- CONTINUE searching if: Answer is incomplete, contradictory, or lacks important details
- STOP searching if: You have comprehensive, consistent information that fully answers the question

RESPONSE FORMAT:
- **DECISION**: [CONTINUE/STOP]
- **REASONING**: Why you decided to continue/stop
- **NEXT_SEARCH**: If continuing, what specific query to search next
- **ANSWER**: If stopping, provide the comprehensive final answer

You must be thorough - don't stop until you have complete information."""

        # Create React agent
        self.agent = ChatAgent(
            system_message=BaseMessage.make_assistant_message(
                role_name="IterativeResearcher",
                content=self.system_prompt,
            ),
            model=self.model,
        )

    def search_mem0(
        self, query: str, limit: int = 10, threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search mem0 database with given query"""
        try:
            results = self.mem0_client.search(
                query=query,
                user_id=USER_ID,
                limit=limit,
                threshold=threshold,
                metadata={"summary_fact": True},  # Focus on summary facts
            )
            return results
        except Exception as e:
            console.print(f"[red]Search error: {e}[/red]")
            return []

    def format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for agent consumption"""
        if not results:
            return "No relevant information found."

        formatted = "SEARCH RESULTS:\n"
        for i, result in enumerate(results, 1):
            memory = result.get("memory", "No content")
            metadata = result.get("metadata", {})
            patient_name = metadata.get("patient_name", "Unknown")
            formatted += f"{i}. [Patient: {patient_name}] {memory}\n"

        return formatted

    def iterative_search(self, initial_query: str) -> str:
        """
        Perform iterative search until finding satisfactory answer
        """
        console.print(
            f"[bold green]Starting iterative search for: {initial_query}[/bold green]\n"
        )

        accumulated_info = ""
        current_query = initial_query

        for iteration in range(1, self.max_iterations + 1):
            console.print(f"[bold yellow]--- ITERATION {iteration} ---[/bold yellow]")
            console.print(f"[blue]Searching for: {current_query}[/blue]")

            # Search mem0
            search_results = self.search_mem0(current_query)
            formatted_results = self.format_search_results(search_results)

            # Show search results
            console.print(f"[dim]Found {len(search_results)} results[/dim]")

            # Update accumulated information
            accumulated_info += (
                f"\n--- Search {iteration}: {current_query} ---\n{formatted_results}\n"
            )

            # Ask agent to analyze and decide next step
            analysis_prompt = f"""
ORIGINAL QUESTION: {initial_query}

ACCUMULATED INFORMATION SO FAR:
{accumulated_info}

Please analyze this information and decide whether to continue searching or provide the final answer.
"""

            user_message = BaseMessage.make_user_message(
                role_name="User", content=analysis_prompt
            )

            response = self.agent.step(user_message)
            agent_response = response.msg.content

            console.print(
                Panel(
                    agent_response,
                    title=f"🤖 Analysis - Iteration {iteration}",
                    border_style="blue",
                )
            )

            # Check if agent decided to stop
            if (
                "DECISION: STOP" in agent_response.upper()
                or "DECISION:**STOP" in agent_response.upper()
            ):
                console.print(
                    "[bold green]✅ Agent found satisfactory answer![/bold green]\n"
                )
                return agent_response

            # Extract next search query if continuing
            lines = agent_response.split("\n")
            next_search = None
            for line in lines:
                if "NEXT_SEARCH" in line.upper():
                    next_search = line.split(":", 1)[1].strip() if ":" in line else None
                    break

            if not next_search:
                console.print("[yellow]⚠️ No next search query found, stopping[/yellow]")
                break

            current_query = next_search
            console.print()

        console.print(f"[red]❌ Reached max iterations ({self.max_iterations})[/red]")
        return agent_response


def main():
    """Main interactive loop"""
    agent = IterativeReactAgent(max_iterations=5)

    console.print(
        Panel(
            "[bold blue]Iterative React Agent[/bold blue]\n\n"
            "🔍 I'll search through medical data iteratively until I find complete answers.\n"
            "🔄 I'll keep refining my searches based on what I discover.\n"
            "✅ I'll stop when I have comprehensive information.\n\n"
            "Type 'exit' to quit.",
            title="🧠 Medical Research Agent",
            border_style="green",
        )
    )

    while True:
        try:
            user_query = console.input(
                "\n[bold cyan]Your question:[/bold cyan] "
            ).strip()

            if user_query.lower() in ["exit", "quit"]:
                console.print("[yellow]Goodbye![/yellow]")
                break

            if not user_query:
                continue

            # Start iterative search
            final_answer = agent.iterative_search(user_query)

            console.print("\n" + "=" * 80)
            console.print(
                Panel(
                    final_answer,
                    title="🎯 Final Research Results",
                    border_style="green",
                )
            )
            console.print("=" * 80 + "\n")

        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    main()
