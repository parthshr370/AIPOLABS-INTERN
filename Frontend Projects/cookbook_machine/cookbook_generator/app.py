from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv
import logging
from rich.logging import RichHandler
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.tree import Tree
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
import os
import json
import time

# --- CAMEL AI Agent Imports ---
from agents.planner import run_planner
from agents.writer import create_writer_agent, run_writer
from agents.assembler import run_assembler
from agents.style_designer import run_style_designer
from camel_config import camel_config
from style_schema import StyleGuide

# --- Basic Configuration ---
load_dotenv()

# --- Rich Console Setup ---
console = Console()

# --- Enhanced Logging Setup ---
class CookbookRichHandler(RichHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.console = console

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[CookbookRichHandler(rich_tracebacks=True, show_path=False)],
)
logger = logging.getLogger("rich")

def log_section_header(title: str, color: str = "blue"):
    """Log a beautiful section header."""
    console.print(Panel(
        Align.center(Text(title, style=f"bold {color}")),
        border_style=color,
        padding=(1, 2)
    ))

def log_agent_output(agent_name: str, content: str, style: str = "dim"):
    """Log agent output with nice formatting."""
    console.print(Panel(
        content,
        title=f"[bold cyan]{agent_name} Output[/bold cyan]",
        border_style="cyan",
        padding=(1, 2)
    ))

def log_step_progress(step: str, status: str, details: str = ""):
    """Log step progress with status indicators."""
    status_styles = {
        "starting": "[yellow]🚀 STARTING[/yellow]",
        "processing": "[blue]⚙️  PROCESSING[/blue]",
        "success": "[green]✅ SUCCESS[/green]",
        "error": "[red]❌ ERROR[/red]",
        "complete": "[green]🎉 COMPLETE[/green]"
    }
    
    status_text = status_styles.get(status, f"[white]{status}[/white]")
    
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Status", style="bold")
    table.add_column("Step")
    table.add_column("Details")
    
    table.add_row(status_text, f"[bold white]{step}[/bold white]", details)
    console.print(table)

def log_api_request(endpoint: str, data_summary: str):
    """Log incoming API requests."""
    console.print(Panel(
        f"[bold white]Endpoint:[/bold white] {endpoint}\n[bold white]Data:[/bold white] {data_summary}",
        title="[bold green]📥 Incoming Request[/bold green]",
        border_style="green"
    ))

# --- Function to load skeleton ---
def load_skeleton():
    try:
        with open("../cookbook-skeleton-template.mdx", "r") as f:
            return f.read()
    except FileNotFoundError:
        logger.error("Cookbook skeleton template not found.")
        return None

app = Flask(__name__)
CORS(app)

@app.route("/api/generate-cookbook", methods=['POST'])
def generate_cookbook():
    data = request.json
    source_code = data.get('source_code')
    user_guidance = data.get('user_guidance')
    example_cookbook = data.get('example_cookbook')
    style_json = data.get('style_json')

    log_api_request(
        "/api/generate-cookbook",
        f"Source code length: {len(source_code) if source_code else 0} chars, "
        f"Guidance length: {len(user_guidance) if user_guidance else 0} chars, "
        f"Example length: {len(example_cookbook) if example_cookbook else 0} chars, "
        f"Style JSON provided: {'Yes' if style_json else 'No'}"
    )

    if not user_guidance or (not example_cookbook and not style_json):
        console.print("[red]❌ Missing required fields: user_guidance and either example_cookbook or style_json are required.[/red]")
        return jsonify({"error": "user_guidance and either example_cookbook or style_json are required"}), 400

    try:
        camel_config.validate_environment()
        log_step_progress("Environment Validation", "success", "All API keys validated")
    except ValueError as e:
        log_step_progress("Environment Validation", "error", str(e))
        return jsonify({"error": f"API key validation failed: {str(e)}"}), 500

    def generate():
        nonlocal style_json
        skeleton_template = load_skeleton()
        if not skeleton_template:
            console.print("[red]❌ Could not load the cookbook skeleton template.[/red]")
            yield f"data: {json.dumps({'error': 'Could not load the cookbook skeleton template.'})}\n\n"
            return

        # --- Step 0: CAMEL AI Style Designer Agent ---
        if style_json:
            log_section_header("🎨 SKIPPING STYLE DESIGNER (Style Guide Provided)", "cyan")
            if isinstance(style_json, dict):
                # Ensure it's a valid StyleGuide object for consistency
                try:
                    style_object = StyleGuide(**style_json)
                    style_json = style_object.model_dump_json()
                except Exception as e:
                    logger.error(f"Provided style_json is invalid: {e}")
                    yield f"data: {json.dumps({'error': f'Provided style_json is invalid: {e}'})}\n\n"
                    return
        else:
            log_section_header("🎨 STEP 0: STYLE DESIGNER AGENT", "magenta")
            yield f"data: {json.dumps({'status': 'styling', 'message': 'The Style Designer Agent is analyzing for style and intent...'})}\n\n"
            
            try:
                if not example_cookbook:
                    raise ValueError("Example cookbook is required to generate a style guide.")
                style_object = run_style_designer(user_guidance, example_cookbook)
                style_data = style_object.model_dump()
                style_json = style_object.model_dump_json() # Use model_dump_json() for a string
                log_step_progress("Style Designer Agent", "success", "Generated and validated style guide")
                yield f"data: {json.dumps({'status': 'styling_complete', 'style_json': style_data})}\n\n"
            except Exception as e:
                log_step_progress("Style Designer Agent", "error", str(e))
                logger.error(f"Error in CAMEL AI Style Designer Agent: {e}")
                yield f"data: {json.dumps({'error': f'An error occurred during styling with CAMEL AI: {e}'})}\n\n"
                return

        # --- Ensure source code is present for the next steps ---
        if not source_code:
            logger.info("Styling complete. No source code provided, so ending stream.")
            return

        log_section_header("🚀 COOKBOOK GENERATION PROCESS STARTED", "magenta")
        
        start_time = time.time()
        
        yield f"data: {json.dumps({'status': 'planning', 'message': 'The CAMEL AI Planner Agent is creating the blueprint...'})}\n\n"

        # --- Step 1: CAMEL AI Planner Agent ---
        log_section_header("📋 STEP 1: PLANNER AGENT", "blue")
        log_step_progress("Planner Agent", "starting", "Analyzing inputs and creating cookbook structure")
        
        try:
            plan = run_planner(user_guidance, source_code, skeleton_template, style_json)
            if not plan:
                log_step_progress("Planner Agent", "error", "Failed to generate a plan")
                yield f"data: {json.dumps({'error': 'CAMEL AI Planner Agent failed to generate a plan.'})}\n\n"
                return
                
            log_step_progress("Planner Agent", "success", f"Generated plan with {len(plan)} sections")
            
            plan_tree = Tree("[bold blue]📋 Generated Plan Structure[/bold blue]")
            for i, section in enumerate(plan, 1):
                section_node = plan_tree.add(f"[cyan]Section {i}: {section.get('section_title', 'Untitled')}[/cyan]")
                section_node.add(f"[dim]Goal: {section.get('goal', 'No goal specified')[:100]}...[/dim]")
                section_node.add(f"[dim]Code snippets: {len(section.get('relevant_code_snippets', []))} found[/dim]")
            
            console.print(plan_tree)
            
            logger.info("CAMEL AI Planner Agent finished.")
            yield f"data: {json.dumps({'status': 'planning_complete', 'plan': plan})}\n\n"
        except Exception as e:
            log_step_progress("Planner Agent", "error", str(e))
            logger.error(f"Error in CAMEL AI Planner Agent: {e}")
            yield f"data: {json.dumps({'error': f'An error occurred during planning with CAMEL AI: {e}'})}\n\n"
            return

        # --- Step 2: CAMEL AI Writer Agent ---
        log_section_header("✍️  STEP 2: WRITER AGENT", "green")
        log_step_progress("Writer Agent", "starting", f"Drafting {len(plan)} sections")
        
        yield f"data: {json.dumps({'status': 'writing', 'message': 'The CAMEL AI Writer Agent is starting...', 'total_sections': len(plan), 'section_number': 0})}\n\n"
        try:
            writer_agent = create_writer_agent()
            drafted_content = []
            
            for i, section in enumerate(plan, 1):
                section_title = section.get("section_title", "Untitled")
                yield f"data: {json.dumps({'status': 'writing', 'message': f'Writing section {i}/{len(plan)}: {section_title}', 'section_number': i, 'total_sections': len(plan)})}\n\n"
                
                section_content = run_writer(writer_agent, [section], source_code, user_guidance, style_json, None)
                drafted_content.extend(section_content)
                
                log_step_progress("Writer Agent", "processing", f"Completed section {i}/{len(plan)}")
            
            log_step_progress("Writer Agent", "success", f"Drafted {len(drafted_content)} sections")
            
            content_table = Table(title="[bold green]📝 Drafted Content Summary[/bold green]")
            content_table.add_column("Section", style="cyan")
            content_table.add_column("Length", style="yellow")
            content_table.add_column("Preview", style="dim")
            
            for i, content in enumerate(drafted_content, 1):
                preview = content[:100].replace('\n', ' ') + "..." if len(content) > 100 else content
                content_table.add_row(
                    f"Section {i}",
                    f"{len(content)} chars",
                    preview
                )
            
            console.print(content_table)
            
            logger.info("CAMEL AI Writer Agent finished.")
            yield f"data: {json.dumps({'status': 'writing_complete', 'drafted_content': drafted_content})}\n\n"
        except Exception as e:
            log_step_progress("Writer Agent", "error", str(e))
            logger.error(f"Error in CAMEL AI Writer Agent: {e}")
            yield f"data: {json.dumps({'error': f'An error occurred during writing with CAMEL AI: {e}'})}\n\n"
            return
            
        # --- Step 3: CAMEL AI Assembler Agent ---
        log_section_header("🔧 STEP 3: ASSEMBLER AGENT", "yellow")
        log_step_progress("Assembler Agent", "starting", "Compiling final cookbook")

        yield f"data: {json.dumps({'status': 'assembling', 'message': 'The CAMEL AI Assembler Agent is compiling the cookbook...'})}\n\n"
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                task = progress.add_task("[yellow]Assembling...", total=None)
                final_cookbook = run_assembler(drafted_content, source_code, user_guidance, style_json, skeleton_template)
                progress.update(task, completed=True, description="[green]Assembly Complete!")

            log_step_progress("Assembler Agent", "success", "Final cookbook compiled")
            log_agent_output("Final Cookbook", final_cookbook[:500] + "...") 
            logger.info("CAMEL AI Assembler Agent finished.")
            yield f"data: {json.dumps({'status': 'complete', 'final_cookbook': final_cookbook})}\n\n"

        except Exception as e:
            log_step_progress("Assembler Agent", "error", str(e))
            logger.error(f"Error in CAMEL AI Assembler Agent: {e}")
            yield f"data: {json.dumps({'error': f'An error occurred during assembly with CAMEL AI: {e}'})}\n\n"
            return
            
        end_time = time.time()
        duration = end_time - start_time
        
        final_cookbook_len = len(final_cookbook) if final_cookbook else 0
        summary_panel = Panel(
            f"[bold green]Total Duration:[/bold green] {duration:.2f} seconds\n"
            f"[bold green]Final Cookbook Size:[/bold green] {final_cookbook_len} characters",
            title="[bold magenta]🎉 Generation Complete! 🎉[/bold magenta]",
            border_style="magenta"
        )
        console.print(summary_panel)

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, port=8080) 