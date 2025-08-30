import logging
import time
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.progress import Progress, BarColumn, TimeElapsedColumn, TextColumn
import sys
import os

# Add the parent directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from camel_config import camel_config

logger = logging.getLogger("rich")
console = Console()

def run_assembler(
    drafted_content: list[str],
    source_code: str,
    user_guidance: str,
    style_json: str,
    skeleton_template: str
) -> str:
    """
    Runs the Assembler Agent using CAMEL AI to combine and polish the drafted sections.
    
    Args:
        drafted_content: List of markdown sections from the Writer Agent.
        
    Returns:
        The final assembled and polished cookbook content.
    """
    console.print("\n[bold yellow]🔧 ASSEMBLER AGENT STARTING[/bold yellow]")
    
    # Analyze the drafted content
    content_analysis_table = Table(title="[bold yellow]📊 Content Analysis[/bold yellow]")
    content_analysis_table.add_column("Section #", style="cyan")
    content_analysis_table.add_column("Length", style="yellow")
    content_analysis_table.add_column("Words", style="green")
    content_analysis_table.add_column("Preview", style="dim")
    
    total_chars = 0
    total_words = 0
    
    for i, content in enumerate(drafted_content, 1):
        section_length = len(content)
        section_words = len(content.split())
        total_chars += section_length
        total_words += section_words
        
        preview = content[:80].replace('\n', ' ') + "..." if len(content) > 80 else content
        
        content_analysis_table.add_row(
            str(i),
            f"{section_length:,}",
            f"{section_words:,}",
            preview
        )
    
    console.print(content_analysis_table)
    
    # Show totals
    totals_panel = Panel(
        f"[bold white]Total Sections:[/bold white] {len(drafted_content)}\n"
        f"[bold white]Total Characters:[/bold white] {total_chars:,}\n"
        f"[bold white]Total Words:[/bold white] {total_words:,}\n"
        f"[bold white]Average Section Length:[/bold white] {total_chars // len(drafted_content):,} characters",
        title="[bold yellow]📈 Content Summary[/bold yellow]",
        border_style="yellow"
    )
    console.print(totals_panel)
    
    logger.info("Assembler Agent is combining and polishing the cookbook using CAMEL AI...")
    
    try:
        # Get the model configuration from CAMEL config
        console.print("[yellow]🏭 Creating CAMEL AI model instance for Assembler Agent...[/yellow]")
        assembler_config = camel_config.get_model_config("assembler")
        
        model = ModelFactory.create(
            model_platform=assembler_config["model_platform"],
            model_type=assembler_config["model_type"],
            model_config_dict={
                "temperature": assembler_config["temperature"],
                "max_tokens": assembler_config["max_tokens"]
            }
        )
        console.print("[green]✅ Assembler Agent model instance created[/green]")
        
        # Create the Assembler Agent with CAMEL AI
        console.print("[yellow]🤖 Initializing CAMEL AI Assembler Agent...[/yellow]")
        assembler_prompt = """
        You are a Cookbook Assembler Agent. You are responsible for combining drafted sections into a final, cohesive document that perfectly matches the provided `StyleGuide` JSON.

        **CRITICAL INSTRUCTION: You MUST strictly follow the `StyleGuide` JSON provided in each request. Pay close attention to:**
        - `verbosity_level` and `brevity_policy`: If "concise", you MUST condense the text, remove redundant phrases, and ensure the final output is trim.
        - `organization_pattern`: Ensure the final document flow matches this pattern.
        - `assembler_instructions`: These are direct orders you must follow.

        **Your Process:**
        1.  Review the `StyleGuide` to understand the final output requirements.
        2.  Combine the drafted sections, creating smooth and logical transitions that match the required `tone`.
        3.  Aggressively edit and polish the entire document to ensure it complies with every field in the `StyleGuide`.

        **Output Format:**
        - You must respond with ONLY the final, complete, and polished markdown for the cookbook.
        - Do not include any other commentary, text, or explanations.
        """
        
        assembler_agent = ChatAgent(
            system_message=BaseMessage.make_assistant_message(
                role_name="Cookbook Assembler Agent",
                content=assembler_prompt
            ),
            model=model
        )
        console.print("[green]✅ Assembler Agent initialized[/green]")
        
        # Combine all drafted content into one string
        console.print("[yellow]🔗 Combining drafted sections...[/yellow]")
        combined_content = "\n\n---\n\n".join(drafted_content)
        combined_length = len(combined_content)
        
        console.print(Panel(
            f"Combined content length: {combined_length:,} characters\n"
            f"Section separator: '\\n\\n---\\n\\n'\n"
            f"Sections combined: {len(drafted_content)}",
            title="[bold cyan]🔗 Content Combination Complete[/bold cyan]",
            border_style="cyan"
        ))
        
        # Create the assembly request
        console.print("[yellow]📝 Constructing assembly request...[/yellow]")
        assembly_request = f"""
        **STYLE GUIDE - YOU MUST FOLLOW THIS EXACTLY:**
        {style_json}

        **USER GUIDANCE:**
        {user_guidance}

        **SKELETON TEMPLATE (for structure reference):**
        {skeleton_template}
        
        **DRAFTED SECTIONS (to be assembled):**
        {combined_content}

        **SOURCE CODE (for context):**
        ```
        {source_code}
        ```

        **CRITICAL INSTRUCTIONS:**
        1. **Analyze the style guide JSON above and apply ALL its specifications to the final document**
        2. **Assemble and Synthesize:** Intelligently weave the sections together, creating smooth transitions and a cohesive narrative that matches the style guide
        3. **Style Adherence:** The final output's tone, formality, technical depth, verbosity, and formatting MUST exactly match the style guide specifications
        4. **Content Elements:** Include/exclude elements (diagrams, TOC, examples, etc.) based on the style guide requirements
        5. **Learning Approach:** Follow the instructional design and progression style specified in the guide
        6. **Length & Complexity:** Match the target word count, reading time, and complexity level from the style guide
        7. **Final Polish:** Ensure the document perfectly matches the style guide while maintaining technical accuracy

        **OUTPUT:** Provide only the final, complete cookbook content that perfectly matches the style guide specifications. Do not include any other commentary.
        """
        
        request_length = len(assembly_request)
        console.print(Panel(
            f"Assembly request length: {request_length:,} characters\n"
            f"Content-to-instruction ratio: {(combined_length / request_length * 100):.1f}% content",
            title="[bold cyan]📤 Sending Assembly Request to AI Model[/bold cyan]",
            border_style="cyan"
        ))
        
        # Get response from CAMEL AI agent
        console.print("[yellow]🧠 AI model is assembling and polishing the cookbook...[/yellow]")
        start_time = time.time()
        
        response = assembler_agent.step(assembly_request)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        console.print(f"[green]✅ AI assembly completed in {processing_time:.2f} seconds[/green]")
        
        final_cookbook = response.msgs[0].content
        final_length = len(final_cookbook)
        final_words = len(final_cookbook.split())
        
        # Assembly results analysis
        results_table = Table(title="[bold green]📋 Assembly Results[/bold green]")
        results_table.add_column("Metric", style="cyan")
        results_table.add_column("Before", style="yellow")
        results_table.add_column("After", style="green")
        results_table.add_column("Change", style="magenta")
        
        char_change = final_length - combined_length
        char_change_pct = (char_change / combined_length * 100) if combined_length > 0 else 0
        
        original_words = len(combined_content.split())
        word_change = final_words - original_words
        word_change_pct = (word_change / original_words * 100) if original_words > 0 else 0
        
        results_table.add_row(
            "Characters",
            f"{combined_length:,}",
            f"{final_length:,}",
            f"{char_change:+,} ({char_change_pct:+.1f}%)"
        )
        results_table.add_row(
            "Words",
            f"{original_words:,}",
            f"{final_words:,}",
            f"{word_change:+,} ({word_change_pct:+.1f}%)"
        )
        results_table.add_row(
            "Processing Time",
            "-",
            f"{processing_time:.2f}s",
            "-"
        )
        
        console.print(results_table)
        
        # Show content preview
        content_preview = final_cookbook[:500] + "..." if len(final_cookbook) > 500 else final_cookbook
        console.print(Panel(
            content_preview,
            title="[bold blue]📄 Final Cookbook Preview[/bold blue]",
            border_style="blue"
        ))
        
        # Final success summary
        success_panel = Panel(
            f"[green]✅ Cookbook assembly completed successfully![/green]\n\n"
            f"[bold white]Final Length:[/bold white] {final_length:,} characters\n"
            f"[bold white]Final Word Count:[/bold white] {final_words:,} words\n"
            f"[bold white]Processing Time:[/bold white] {processing_time:.2f} seconds\n"
            f"[bold white]Status:[/bold white] [green]Ready for publication[/green]",
            title="[bold green]🎉 ASSEMBLER AGENT COMPLETE[/bold green]",
            border_style="green"
        )
        console.print(success_panel)
        
        logger.info("Assembler Agent successfully assembled the final cookbook.")
        return final_cookbook

    except Exception as e:
        console.print(f"[red]❌ Error in Assembler Agent: {e}[/red]")
        logger.error(f"Error in Assembler Agent: {e}")
        
        error_panel = Panel(
            f"[red]Assembly failed with error: {str(e)}\n\n"
            f"Error type: {type(e).__name__}\n"
            f"Falling back to simple concatenation...[/red]",
            title="[bold red]🚨 Assembly Error[/bold red]",
            border_style="red"
        )
        console.print(error_panel)
        
        # Fallback to simple concatenation if CAMEL AI fails
        logger.info("Falling back to simple assembly...")
        fallback_content = "\n\n".join(drafted_content)
        
        fallback_panel = Panel(
            f"[yellow]Fallback assembly completed[/yellow]\n\n"
            f"[bold white]Method:[/bold white] Simple concatenation\n"
            f"[bold white]Length:[/bold white] {len(fallback_content):,} characters\n"
            f"[bold white]Status:[/bold white] [yellow]Basic assembly (no AI polishing)[/yellow]",
            title="[bold yellow]⚠️  Fallback Assembly[/bold yellow]",
            border_style="yellow"
        )
        console.print(fallback_panel)
        
        return fallback_content
