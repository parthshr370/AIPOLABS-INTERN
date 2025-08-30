#!/usr/bin/env python3
import asyncio
import os
from dotenv import load_dotenv
from rich import print as rprint
import nest_asyncio

from camel.societies.workforce import Workforce
from camel.tasks import Task

# Import the existing agents
from agents.hr_agent.agent import get_hr_agent
from agents.search_agent.agent import get_search_agent
from agents.slack_agent.agent import get_slack_agent

load_dotenv()

# Enable nested event loops for Jupyter-like environments
nest_asyncio.apply()


class WorkforceOrchestrator:
    def __init__(self):
        self.workforce = None
        self.toolkits = []

    async def initialize(self):
        """Initialize the workforce with existing specialized agents"""
        rprint("[green]🚀 Initializing ACI Workforce...[/green]")

        # Create workforce with description
        self.workforce = Workforce("ACI Multi-Agent Workforce")

        # Load HR Manager Agent
        rprint("[yellow]📋 Loading HR Manager Agent...[/yellow]")
        hr_agent, hr_toolkit = await get_hr_agent()
        self.workforce.add_single_agent_worker(
            "HR Manager - Handles recruitment, scheduling, documentation, and employee communications using Gmail, Google Sheets, Calendar, Notion, and Google Docs",
            worker=hr_agent,
        )
        self.toolkits.append(hr_toolkit)

        # Load Research Specialist Agent
        rprint("[yellow]🔍 Loading Research Specialist Agent...[/yellow]")
        research_agent, research_toolkit = await get_search_agent()
        self.workforce.add_single_agent_worker(
            "Research Specialist - Conducts comprehensive research using Exa AI, ArXiv, and Google Maps for information discovery and analysis",
            worker=research_agent,
        )
        self.toolkits.append(research_toolkit)

        # Load Slack Manager Agent
        rprint("[yellow]💬 Loading Slack Manager Agent...[/yellow]")
        slack_agent, slack_toolkit = await get_slack_agent()
        self.workforce.add_single_agent_worker(
            "Slack Manager - Manages team communications, channels, and workflow automation using Slack tools",
            worker=slack_agent,
        )
        self.toolkits.append(slack_toolkit)

        rprint("[green]✅ Workforce initialized with 3 specialized agents![/green]")

    async def process_task(self, task_description, additional_info=None):
        """Process a task using the workforce coordination system"""
        rprint(f"[blue]📋 Processing Task: {task_description}[/blue]")

        # Create task with unique ID
        task = Task(
            content=task_description,
            additional_info=additional_info,
            id=f"task_{len(str(asyncio.get_event_loop().time()).replace('.', ''))}",
        )

        # Process through workforce - this handles task planning, coordination, and execution
        result = self.workforce.process_task(task)

        rprint(f"[green]✅ Task Completed![/green]")
        return result

    async def cleanup(self):
        """Cleanup all MCP toolkit connections"""
        rprint("[yellow]🧹 Cleaning up connections...[/yellow]")

        for toolkit in self.toolkits:
            try:
                await toolkit.disconnect()
            except Exception as e:
                rprint(f"[red]Warning: Error disconnecting toolkit: {e}[/red]")

        rprint("[green]✅ Cleanup completed![/green]")


async def run_demo():
    """Run demonstration of workforce capabilities"""
    orchestrator = WorkforceOrchestrator()

    try:
        await orchestrator.initialize()

        # Demo tasks showcasing multi-agent coordination
        demo_tasks = [
            {
                "description": "Research the latest AI trends in healthcare for 2024, create a comprehensive report, and share the findings with our team on Slack",
                "context": "We need to understand AI applications in healthcare for our quarterly strategic planning meeting",
            },
            {
                "description": "Find contact information for senior Python developers in San Francisco, send personalized recruitment emails, and schedule initial screening interviews",
                "context": "We're expanding our engineering team and need 2 senior Python developers with AI/ML experience",
            },
            {
                "description": "Research our top 3 competitors in the AI automation space, document their key features and pricing, and notify the product team via Slack",
                "context": "Competitive analysis for our product roadmap and pricing strategy",
            },
        ]

        for i, task in enumerate(demo_tasks, 1):
            rprint(f"\n[bold cyan]🎯 Demo Task {i}[/bold cyan]")
            rprint(f"[dim]Context: {task['context']}[/dim]")

            result = await orchestrator.process_task(
                task["description"], task["context"]
            )

            rprint(f"[green]Result:[/green] {result.result}")
            rprint("-" * 80)

            # Brief pause between tasks
            await asyncio.sleep(1)

    except Exception as e:
        rprint(f"[red]Error during demo: {e}[/red]")
        import traceback

        rprint(f"[dim]{traceback.format_exc()}[/dim]")

    finally:
        await orchestrator.cleanup()


async def interactive_mode():
    """Interactive mode for custom task processing"""
    orchestrator = WorkforceOrchestrator()

    try:
        await orchestrator.initialize()

        rprint("[bold green]🎯 ACI Workforce Interactive Mode[/bold green]")
        rprint("Your workforce includes:")
        rprint(
            "• [cyan]HR Manager[/cyan]: Gmail, Google Sheets, Calendar, Notion, Google Docs"
        )
        rprint("• [cyan]Research Specialist[/cyan]: Exa AI, ArXiv, Google Maps")
        rprint("• [cyan]Slack Manager[/cyan]: Slack communications and automation")
        rprint("\nType 'exit' to quit, 'demo' to run demo tasks")
        rprint("-" * 70)

        while True:
            try:
                user_input = input("\n🎯 Enter your task: ").strip()

                if user_input.lower() in ["exit", "quit"]:
                    break
                elif user_input.lower() == "demo":
                    await run_demo()
                    continue
                elif not user_input:
                    continue

                # Process user task
                result = await orchestrator.process_task(user_input)
                rprint(f"[green]✅ Result:[/green] {result.result}")

            except KeyboardInterrupt:
                break
            except Exception as e:
                rprint(f"[red]Error: {e}[/red]")

    finally:
        await orchestrator.cleanup()
        rprint("[green]👋 Goodbye![/green]")


def main():
    """Main function with mode selection"""
    rprint("[bold]🌟 ACI Workforce Orchestrator[/bold]")
    rprint("Choose mode:")
    rprint("1. [yellow]Demo Mode[/yellow] - Run predefined demo tasks")
    rprint("2. [yellow]Interactive Mode[/yellow] - Enter custom tasks")

    try:
        choice = input("\nSelect mode (1 or 2): ").strip()

        if choice == "1":
            asyncio.run(run_demo())
        elif choice == "2":
            asyncio.run(interactive_mode())
        else:
            rprint("[red]Invalid choice. Running interactive mode...[/red]")
            asyncio.run(interactive_mode())

    except KeyboardInterrupt:
        rprint("\n[yellow]Exiting...[/yellow]")


if __name__ == "__main__":
    main()
