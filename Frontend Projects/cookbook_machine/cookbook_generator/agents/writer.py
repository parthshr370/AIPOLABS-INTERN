import logging
import json
import time
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from prompts.writer_prompt import WRITER_PROMPT
from camel_config import camel_config
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TimeElapsedColumn, TextColumn
from rich.live import Live
from rich.syntax import Syntax

logger = logging.getLogger("rich")
console = Console()

def create_writer_agent():
    """Initializes and returns the Writer Agent using CAMEL AI."""
    console.print("\n[bold green]✍️  INITIALIZING WRITER AGENT[/bold green]")
    
    # Get configuration for writer agent
    console.print("[yellow]⚙️  Loading writer agent configuration...[/yellow]")
    config = camel_config.get_model_config("writer")
    
    config_panel = Panel(
        f"[bold white]Model Platform:[/bold white] {config['model_platform']}\n"
        f"[bold white]Model Type:[/bold white] {config['model_type']}\n"
        f"[bold white]Temperature:[/bold white] {config['temperature']}\n"
        f"[bold white]Max Tokens:[/bold white] {config['max_tokens']}",
        title="[bold green]🤖 Writer Agent Configuration[/bold green]",
        border_style="green"
    )
    console.print(config_panel)
    
    console.print("[yellow]🏭 Creating CAMEL AI model instance for Writer Agent...[/yellow]")
    model = ModelFactory.create(
        model_platform=config["model_platform"],
        model_type=config["model_type"],
        model_config_dict={
            "temperature": config["temperature"],
            "max_tokens": config["max_tokens"]
        }
    )
    console.print("[green]✅ Writer Agent model instance created successfully[/green]")
    
    console.print("[yellow]🤖 Initializing CAMEL AI Writer Agent...[/yellow]")
    writer_agent = ChatAgent(
        system_message=BaseMessage.make_assistant_message(
            role_name="Cookbook Writer Agent",
            content=WRITER_PROMPT
        ),
        model=model
    )
    console.print("[green]✅ Writer Agent initialized and ready[/green]")
    
    return writer_agent

def run_writer(
    agent: ChatAgent,
    plan: list,
    source_code: str,
    user_guidance: str,
    style_json: str,
    progress_bar=None,
) -> list:
    """
    Runs the Writer Agent using CAMEL AI to generate content for each section in the plan.

    Args:
        agent: The CAMEL AI Writer Agent instance.
        plan: The cookbook plan from the Planner Agent (can be full plan or single section).
        source_code: The full source code for context.
        user_guidance: The original user guidance for context.
        progress_bar: A progress bar to update (optional).

    Returns:
        A list of strings, where each string is the markdown for a section.
    """
    console.print("\n[bold green]✍️  WRITER AGENT PROCESSING[/bold green]")
    
    # Show writing overview
    overview_table = Table(title="[bold green]📝 Writing Overview[/bold green]")
    overview_table.add_column("Metric", style="cyan")
    overview_table.add_column("Value", style="yellow")
    
    overview_table.add_row("Sections to Write", str(len(plan)))
    overview_table.add_row("Source Code Length", f"{len(source_code):,} characters")
    overview_table.add_row("User Guidance Length", f"{len(user_guidance):,} characters")
    
    console.print(overview_table)
    
    logger.info("Writer Agent is drafting content using CAMEL AI...")
    drafted_sections = []
    total_sections = len(plan)
    total_start_time = time.time()

    for i, section in enumerate(plan, 1):
        section_start_time = time.time()
        
        # Create section-specific prompt
        section_prompt = f"""
        **STYLE GUIDE - YOU MUST FOLLOW THIS EXACTLY:**
        {style_json}

        **SECTION REQUIREMENTS:**
        Section Title: {section['section_title']}
        Section Goal: {section['goal']}

        **RELEVANT CODE SNIPPETS:**
        ```python
        {chr(10).join(section['relevant_code_snippets'])}
        ```

        **USER GUIDANCE CONTEXT:**
        {user_guidance}

        **INSTRUCTIONS:**
        1. Analyze the style guide JSON above and apply ALL its specifications to your writing
        2. Match the tone, formality level, technical depth, and verbosity specified in the style guide
        3. Follow the formatting preferences and content structure requirements
        4. Include/exclude elements based on the style guide specifications
        5. Write content that achieves the section goal while strictly adhering to the style guide
        6. Use the learning approach and progression style specified in the guide

        Write content that perfectly matches the style guide specifications while achieving the section goal.
        """

        try:
            # Get response from CAMEL AI agent
            response = agent.step(section_prompt)
            section_content = response.msgs[0].content
            
            # Process and validate content
            if not section_content:
                raise ValueError("Empty content received from AI model")
            
            # Add to drafted sections
            drafted_sections.append(section_content)
            
            # Calculate metrics
            section_time = time.time() - section_start_time
            section_chars = len(section_content)
            section_words = len(section_content.split())
            
            # Log section completion
            section_table = Table(title=f"[bold green]✅ Section {i} Completed[/bold green]")
            section_table.add_column("Metric", style="cyan")
            section_table.add_column("Value", style="yellow")
            
            section_table.add_row("Content Length", f"{section_chars:,} characters")
            section_table.add_row("AI Processing Time", f"{section_time:.2f} seconds")
            section_table.add_row("Total Section Time", f"{section_time:.2f} seconds")
            section_table.add_row("Words Estimated", f"{section_words:,}")
            
            console.print(section_table)
            
            # Preview content
            console.print(Panel(
                section_content[:200] + "..." if len(section_content) > 200 else section_content,
                title="[bold blue]📄 Section Content Preview[/bold blue]",
                border_style="blue"
            ))
            
        except Exception as e:
            logger.error(f"Error writing section {i}: {e}")
            # Add placeholder for failed section
            drafted_sections.append(f"Error generating content for {section['section_title']}: {str(e)}")
    
    # Final summary
    total_time = time.time() - total_start_time
    total_chars = sum(len(s) for s in drafted_sections)
    total_words = sum(len(s.split()) for s in drafted_sections)
    
    summary_table = Table(title="[bold green]📝 WRITER AGENT SUMMARY[/bold green]")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="yellow")
    
    summary_table.add_row("Total Sections", str(total_sections))
    summary_table.add_row("Total Content", f"{total_chars:,} characters")
    summary_table.add_row("Total Time", f"{total_time:.2f} seconds")
    summary_table.add_row("Average per Section", f"{total_time/total_sections:.2f} seconds")
    summary_table.add_row("Estimated Words", str(total_words))
    
    console.print(summary_table)
    
    return drafted_sections

def generate_progress_table(current: int, total: int, status: str) -> Table:
    """Generate a progress table for live updates."""
    table = Table(title="[bold green]✍️  Writer Agent Progress[/bold green]")
    table.add_column("Progress", style="cyan")
    table.add_column("Status", style="yellow")
    
    progress_bar = "█" * (current * 20 // total) + "░" * (20 - (current * 20 // total))
    percentage = (current / total * 100) if total > 0 else 0
    
    table.add_row(
        f"[{current}/{total}] {progress_bar} {percentage:.1f}%",
        status
    )
    
    return table
