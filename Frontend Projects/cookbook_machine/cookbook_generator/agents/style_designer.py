"""
CAMEL AI Style Designer Agent

This agent is responsible for analyzing an example cookbook and user guidance
to generate a structured IntentStyle JSON object. This object defines the
style, tone, structure, and other characteristics for the new cookbook.
"""

import os
import json
import logging
import time
from pydantic import ValidationError
from camel.models import ModelFactory
from camel.agents import ChatAgent
from camel.messages import BaseMessage

# Assuming the following files will be created or are accessible
from prompts.style_prompt import STYLE_PROMPT
from camel_config import camel_config
from style_schema import StyleGuide

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

logger = logging.getLogger("rich")
console = Console()

def run_style_designer(user_guidance: str, example_cookbook: str) -> StyleGuide:
    """
    Runs the Style Designer Agent to generate and validate a cookbook style guide.
    """
    console.print("\n[bold magenta]🎨 STYLE DESIGNER AGENT STARTING[/bold magenta]")

    # Log inputs summary
    inputs_table = Table(title="[bold magenta]📥 Style Designer Inputs[/bold magenta]")
    inputs_table.add_column("Input Type", style="cyan")
    inputs_table.add_column("Length", style="yellow")
    inputs_table.add_column("Preview", style="dim")

    inputs_table.add_row(
        "User Guidance",
        f"{len(user_guidance)} chars",
        user_guidance[:100].replace('\\n', ' ') + "..."
    )
    inputs_table.add_row(
        "Example Cookbook",
        f"{len(example_cookbook)} chars",
        example_cookbook[:100].replace('\\n', ' ') + "..."
    )
    console.print(inputs_table)

    try:
        # Get configuration for style designer agent
        config = camel_config.get_model_config("style_designer")
        
        config_panel = Panel(
            f"[bold white]Model Platform:[/bold white] {config['model_platform']}\n"
            f"[bold white]Model Type:[/bold white] {config['model_type']}\n"
            f"[bold white]Temperature:[/bold white] {config['temperature']}\n"
            f"[bold white]Max Tokens:[/bold white] {config['max_tokens']}",
            title="[bold magenta]🤖 Model Configuration[/bold magenta]",
            border_style="magenta"
        )
        console.print(config_panel)

        # Create the model
        model = ModelFactory.create(
            model_platform=config["model_platform"],
            model_type=config["model_type"],
            model_config_dict={
                "temperature": config["temperature"],
                "max_tokens": config["max_tokens"]
            }
        )

        # Create the Style Designer Agent
        style_agent = ChatAgent(
            system_message=BaseMessage.make_assistant_message(
                role_name="Cookbook Style Analyst",
                content=STYLE_PROMPT
            ),
            model=model
        )

        # Construct the request
        style_request = f"""
        Here is the user's guidance on the desired cookbook:
        ---
        {user_guidance}
        ---
        Here is an example cookbook to analyze for style, tone, and structure:
        ---
        {example_cookbook}
        ---
        Based on the guidance and the example, please generate the IntentStyle JSON object.
        """
        
        console.print(f"[yellow]🧠 AI model is analyzing the style...[/yellow]")
        start_time = time.time()
        
        response = style_agent.step(style_request)
        
        end_time = time.time()
        console.print(f"[green]✅ AI response received in {end_time - start_time:.2f} seconds[/green]")

        style_text = response.msgs[0].content

        # Extract JSON from response
        if "```json" in style_text:
            start = style_text.find("```json") + 7
            end = style_text.find("```", start)
            style_text = style_text[start:end].strip()
        
        # Parse and validate the style JSON
        console.print("[yellow]📊 Parsing and validating style JSON...[/yellow]")
        style_data = json.loads(style_text)
        
        validated_style = StyleGuide(**style_data)
        console.print("[green]✅ Style JSON validated successfully with Pydantic![/green]")
        
        # Log key inferred style parameters for debugging verbosity
        console.print(Panel(
            f"[bold]Verbosity Level:[/bold] {validated_style.verbosity_level}\n"
            f"[bold]Content Density:[/bold] {validated_style.content_density}\n"
            f"[bold]Brevity Policy:[/bold] {validated_style.brevity_policy}",
            title="[bold blue]📝 Key Style Parameters[/bold blue]",
            border_style="blue"
        ))

        console.print(Panel(
            Syntax(json.dumps(validated_style.model_dump(), indent=2), "json", theme="monokai"),
            title="[bold green]🎨 Validated Style Object[/bold green]",
            border_style="green"
        ))
        
        return validated_style

    except ValidationError as ve:
        logger.error(f"Style JSON validation failed: {ve}")
        console.print(Panel(str(ve), title="[bold red]❌ Pydantic Validation Error[/bold red]", border_style="red"))
        raise
    except Exception as e:
        logger.error(f"An error occurred in the Style Designer Agent: {e}")
        # Fallback to a default concise style to prevent pipeline failure
        console.print(Panel(f"{str(e)}\n\n[bold yellow]Falling back to default concise style.[/bold yellow]", title="[bold red]❌ Agent Error[/bold red]", border_style="red"))
        return StyleGuide(
            core_intent_summary="Default: Create a concise technical guide.",
            target_audience="technical experts",
            technology_stack=[],
            tone="formal",
            verbosity_level="concise",
            content_density="scan-friendly",
            organization_pattern="step-by-step-tutorial",
            section_length_guideline="short",
            example_usage="minimal and illustrative",
            formatting_preferences=["numbered-lists"],
            emoji_usage_policy="none",
            includes_diagrams=False,
            brevity_policy="Strictly adhere to conciseness. Keep explanations short and to the point.",
            planner_instructions=["Create a minimal plan with 2-3 essential sections."],
            writer_instructions=["Write very concise content for each section. Use short sentences and paragraphs."],
            assembler_instructions=["Assemble the content as is, with minimal transitions. Do not add extra content."]
        ) 