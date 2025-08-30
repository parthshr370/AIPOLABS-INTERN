import warnings
from rich.console import Console
from rich.panel import Panel

from config import USER_ID, GEMINI_API_KEY, MEM0_API_KEY
from deep_research_agent import DeepResearchAgent

warnings.filterwarnings("ignore", category=DeprecationWarning)

console = Console()

# Check API keys
if not MEM0_API_KEY or not GEMINI_API_KEY:
    console.print("[red]Error: Missing API keys in environment variables[/red]")
    console.print("[yellow]Please set GEMINI_API_KEY and MEM0_API_KEY[/yellow]")
    exit(1)


def main():
    """CLI interface for Deep Memory Researcher"""
    
    console.print(Panel(
        "[bold blue]🧠 Deep Memory Researcher System (Refactored)[/bold blue]\n\n"
        "A simplified, agent-based medical research system.\n\n"
        "💡 [bold]Example queries:[/bold]\n"
        "• 'Find all diabetic patients and their treatment outcomes'\n"
        "• 'What are the most effective pain management approaches?'\n"
        "• 'Analyze hypertension treatment patterns across patients'\n\n"
        "Type 'exit' to quit.",
        title="🔬 Medical Research Interface",
        border_style="cyan"
    ))
    
    # Initialize the agent
    agent = DeepResearchAgent(user_id=USER_ID)
    
    while True:
        try:
            user_input = console.input("\n[bold cyan]Research Query:[/bold cyan] ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                console.print("[yellow]Research session ended. Goodbye![/yellow]")
                break
                
            if not user_input:
                continue
            
            # Run the agent's research process
            agent.run(user_input)
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Research interrupted. Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")


if __name__ == "__main__":
    main()