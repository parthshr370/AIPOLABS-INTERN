import os
import json
import logging
from typing import List
from pydantic import BaseModel, Field, ValidationError
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from prompts.planner_prompt import PLANNER_PROMPT
from camel_config import camel_config
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.progress import track
import time

logger = logging.getLogger("rich")
console = Console()

# --- Pydantic Validation Model ---
class SectionPlan(BaseModel):
    section_title: str = Field(..., description="The markdown heading of the section.")
    goal: str = Field(..., description="The instruction for the Writer Agent.")
    relevant_code_snippets: List[str] = Field(..., description="List of code snippets.")

def run_planner(user_guidance: str, source_code: str, skeleton: str, style_json: str) -> list:
    """
    Runs the Planner Agent using CAMEL AI to generate and validate a cookbook plan.
    """
    console.print("\n[bold blue]🧠 PLANNER AGENT STARTING[/bold blue]")
    
    # Log inputs summary
    inputs_table = Table(title="[bold blue]📥 Planner Agent Inputs[/bold blue]")
    inputs_table.add_column("Input Type", style="cyan")
    inputs_table.add_column("Length", style="yellow")
    inputs_table.add_column("Preview", style="dim")
    
    inputs_table.add_row(
        "User Guidance",
        f"{len(user_guidance)} chars",
        user_guidance[:100].replace('\n', ' ') + "..." if len(user_guidance) > 100 else user_guidance
    )
    inputs_table.add_row(
        "Source Code",
        f"{len(source_code)} chars",
        source_code[:100].replace('\n', ' ') + "..." if len(source_code) > 100 else source_code
    )
    inputs_table.add_row(
        "Skeleton Template",
        f"{len(skeleton)} chars",
        skeleton[:100].replace('\n', ' ') + "..." if len(skeleton) > 100 else skeleton
    )
    
    console.print(inputs_table)
    
    logger.info("Planner Agent is analyzing the inputs via CAMEL AI...")
    
    try:
        # Validate environment
        console.print("[yellow]🔍 Validating CAMEL AI environment...[/yellow]")
        camel_config.validate_environment()
        console.print("[green]✅ Environment validation successful[/green]")
        
        # Get configuration for planner agent
        console.print("[yellow]⚙️  Loading planner agent configuration...[/yellow]")
        config = camel_config.get_model_config("planner")
        
        config_panel = Panel(
            f"[bold white]Model Platform:[/bold white] {config['model_platform']}\n"
            f"[bold white]Model Type:[/bold white] {config['model_type']}\n"
            f"[bold white]Temperature:[/bold white] {config['temperature']}\n"
            f"[bold white]Max Tokens:[/bold white] {config['max_tokens']}",
            title="[bold cyan]🤖 Model Configuration[/bold cyan]",
            border_style="cyan"
        )
        console.print(config_panel)
        
        # Create the model using CAMEL AI's ModelFactory
        console.print("[yellow]🏭 Creating CAMEL AI model instance...[/yellow]")
        model = ModelFactory.create(
            model_platform=config["model_platform"],
            model_type=config["model_type"],
            model_config_dict={
                "temperature": config["temperature"],
                "max_tokens": config["max_tokens"]
            }
        )
        console.print("[green]✅ Model instance created successfully[/green]")
        
        # Create the Planner Agent with CAMEL AI
        console.print("[yellow]🤖 Initializing CAMEL AI Planner Agent...[/yellow]")
        planner_agent = ChatAgent(
            system_message=BaseMessage.make_assistant_message(
                role_name="Cookbook Planner Agent",
                content=PLANNER_PROMPT
            ),
            model=model
        )
        console.print("[green]✅ Planner Agent initialized[/green]")
        
        # Construct the planning prompt
        console.print("[yellow]📝 Constructing planning request...[/yellow]")
        planning_request = f"""
        **STYLE GUIDE - YOU MUST FOLLOW THIS EXACTLY:**
        {style_json}

        **USER GUIDANCE:**
        {user_guidance}

        **SOURCE CODE:**
        {source_code}

        **SKELETON TEMPLATE (for structure reference):**
        {skeleton}

        **CRITICAL INSTRUCTIONS:**
        1. **Analyze the style guide JSON above and apply ALL its specifications to your planning**
        2. **Create a plan that matches the style guide specifications:**
           - Follow the specified organization pattern and content structure
           - Plan sections that match the target audience and technical depth
           - Include the number of sections and examples as specified in output_specifications
           - Consider the learning approach and progression style from instructional_design
           - Plan for the specified length preference and detail level from customization_options
        3. **Each section plan must include style guide requirements in the goal**

        **OUTPUT FORMAT:**
        Generate a JSON array of section plans. Each plan should have:
        - section_title: The markdown heading for the section (no ## formatting)
        - goal: Clear instruction for the Writer Agent that includes style guide requirements
        - relevant_code_snippets: Array of relevant code snippets for this section

        Return ONLY valid JSON array format.
        """
        
        console.print(Panel(
            f"Request length: {len(planning_request)} characters",
            title="[bold cyan]📤 Sending Request to AI Model[/bold cyan]",
            border_style="cyan"
        ))
        
        # Get response from CAMEL AI agent
        console.print("[yellow]🧠 AI model is processing the request...[/yellow]")
        start_time = time.time()
        
        response = planner_agent.step(planning_request)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        console.print(f"[green]✅ AI response received in {processing_time:.2f} seconds[/green]")
        
        plan_text = response.msgs[0].content
        
        console.print(Panel(
            f"Response length: {len(plan_text)} characters",
            title="[bold green]📨 Raw AI Response[/bold green]",
            border_style="green"
        ))
        
        # Show raw response (truncated for readability)
        console.print(Panel(
            plan_text[:500] + "..." if len(plan_text) > 500 else plan_text,
            title="[bold blue]📄 Response Preview[/bold blue]",
            border_style="blue"
        ))
        
        # Extract JSON from response if it's wrapped in markdown
        console.print("[yellow]🔍 Extracting JSON from response...[/yellow]")
        original_text = plan_text
        
        if "```json" in plan_text:
            start = plan_text.find("```json") + 7
            end = plan_text.find("```", start)
            plan_text = plan_text[start:end].strip()
            console.print("[green]✅ JSON extracted from markdown code block[/green]")
        elif "```" in plan_text:
            start = plan_text.find("```") + 3
            end = plan_text.rfind("```")
            plan_text = plan_text[start:end].strip()
            console.print("[green]✅ JSON extracted from generic code block[/green]")
        else:
            console.print("[blue]ℹ️  No code blocks found, using raw response[/blue]")
        
        # Show extracted JSON
        if plan_text != original_text:
            console.print(Panel(
                Syntax(plan_text[:1000] + "..." if len(plan_text) > 1000 else plan_text, "json", theme="monokai"),
                title="[bold green]🔧 Extracted JSON[/bold green]",
                border_style="green"
            ))
        
        # Parse and validate the plan
        console.print("[yellow]📊 Parsing and validating JSON structure...[/yellow]")
        plan_data = json.loads(plan_text)
        console.print(f"[green]✅ JSON parsed successfully - found {len(plan_data)} sections[/green]")
        
        console.print("[yellow]🔍 Validating section data with Pydantic...[/yellow]")
        validated_plan_obj = []
        
        for i, item in enumerate(plan_data):
            try:
                validated_section = SectionPlan(**item)
                validated_plan_obj.append(validated_section)
                console.print(f"[green]✅ Section {i+1} validated: '{validated_section.section_title}'[/green]")
            except ValidationError as ve:
                console.print(f"[red]❌ Section {i+1} validation failed: {ve}[/red]")
                raise ve
        
        plan = [item.dict() for item in validated_plan_obj]
        
        # Display final validated plan
        final_table = Table(title="[bold green]📋 Final Validated Plan[/bold green]")
        final_table.add_column("#", style="cyan")
        final_table.add_column("Section Title", style="bold white")
        final_table.add_column("Goal Preview", style="yellow")
        final_table.add_column("Code Snippets", style="green")
        
        for i, section in enumerate(plan, 1):
            goal_preview = section['goal'][:50] + "..." if len(section['goal']) > 50 else section['goal']
            final_table.add_row(
                str(i),
                section['section_title'],
                goal_preview,
                str(len(section['relevant_code_snippets']))
            )
        
        console.print(final_table)

        console.print(f"\n[bold green]🎉 Planner Agent successfully generated and validated a plan with {len(plan)} sections.[/bold green]")
        return plan

    except json.JSONDecodeError as e:
        console.print(f"[red]❌ JSON Decode Error: {e}[/red]")
        logger.error(f"Error decoding JSON from Planner Agent: {e}")
        
        if 'plan_text' in locals():
            console.print(Panel(
                plan_text,
                title="[bold red]🚨 Raw Response Content (Failed to Parse)[/bold red]",
                border_style="red"
            ))
            logger.error(f"Raw response content was:\n{plan_text}")
        else:
            console.print("[red]❌ No response content available[/red]")
            logger.error("No response content available.")
        return None
        
    except ValidationError as e:
        console.print(f"[red]❌ Pydantic Validation Error: {e}[/red]")
        logger.error(f"Pydantic validation failed for the plan: {e}")
        
        if 'plan_text' in locals():
            console.print(Panel(
                plan_text,
                title="[bold red]🚨 Raw Response Content (Failed Validation)[/bold red]",
                border_style="red"
            ))
            logger.error(f"Raw response content was:\n{plan_text}")
        else:
            console.print("[red]❌ No response content available[/red]")
            logger.error("No response content available.")
        return None
        
    except Exception as e:
        console.print(f"[red]❌ Unexpected Error: {e}[/red]")
        logger.error(f"An unexpected error occurred in the Planner Agent: {e}")
        
        if 'plan_text' in locals():
            console.print(Panel(
                plan_text,
                title="[bold red]🚨 Raw Response Content (Unexpected Error)[/bold red]",
                border_style="red"
            ))
            logger.error(f"Raw response content was:\n{plan_text}")
        else:
            console.print("[red]❌ No response content available[/red]")
            logger.error("No response content available.")
        return None
