#!/usr/bin/env python3
"""
Test script for the Assembler Agent using Gemini 2.5 Pro.
This script verifies that the assembler can work with the Gemini model.
"""

import sys
import os
import time
from camel.models import ModelFactory
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from rich.console import Console
from rich.panel import Panel

# Add the parent directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cookbook_generator.camel_config import camel_config

console = Console()

def test_gemini_assembler():
    """Test the assembler agent with Gemini 2.5 Pro."""
    console.print("[bold yellow]🧪 GEMINI ASSEMBLER TEST[/bold yellow]")
    
    # Create some simple test content
    test_sections = [
        """# Introduction
        
        This is a simple test section for the assembler agent.
        
        ```python
        def hello_world():
            print("Hello, world!")
        ```
        """,
        
        """# Setup
        
        This is another test section to verify the assembler works with Gemini.
        
        ```python
        def setup():
            # Initialize environment
            return True
        ```
        """
    ]
    
    # Get the model configuration
    console.print("[yellow]🏭 Creating Gemini model instance...[/yellow]")
    assembler_config = camel_config.get_model_config("assembler")
    
    console.print(Panel(
        f"[bold white]Model Platform:[/bold white] {assembler_config['model_platform']}\n"
        f"[bold white]Model Type:[/bold white] {assembler_config['model_type']}\n"
        f"[bold white]Temperature:[/bold white] {assembler_config['temperature']}\n"
        f"[bold white]Max Tokens:[/bold white] {assembler_config['max_tokens']}",
        title="[bold green]🤖 Assembler Configuration[/bold green]",
        border_style="green"
    ))
    
    # Create the model
    model = ModelFactory.create(
        model_platform=assembler_config["model_platform"],
        model_type=assembler_config["model_type"],
        model_config_dict={
            "temperature": assembler_config["temperature"],
            "max_tokens": assembler_config["max_tokens"]
        }
    )
    
    # Create the agent
    assembler_prompt = """
    You are a Cookbook Assembler Agent responsible for combining and polishing cookbook sections into a cohesive document.
    
    Your tasks:
    1. Combine sections into a logical flow
    2. Ensure consistent formatting and style
    3. Add smooth transitions between sections
    4. Fix any markdown formatting issues
    5. Ensure code blocks are properly formatted
    """
    
    assembler_agent = ChatAgent(
        system_message=BaseMessage.make_assistant_message(
            role_name="Cookbook Assembler Agent",
            content=assembler_prompt
        ),
        model=model
    )
    
    console.print("[green]✅ Gemini assembler agent created[/green]")
    
    # Combine the content
    combined_content = "\n\n---\n\n".join(test_sections)
    
    # Create the assembly request
    assembly_request = f"""
    Please assemble and polish the following cookbook sections into a cohesive document:

    {combined_content}

    Requirements:
    - Ensure smooth flow between sections
    - Fix any formatting inconsistencies
    - Make sure code blocks are properly formatted
    """
    
    # Process the content
    try:
        console.print("[yellow]🧠 Processing with Gemini 2.5 Pro...[/yellow]")
        start_time = time.time()
        
        response = assembler_agent.step(assembly_request)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        result = response.msgs[0].content
        
        console.print(f"[green]✅ Processing completed in {processing_time:.2f} seconds[/green]")
        console.print(f"[bold cyan]Result length: {len(result)} characters[/bold cyan]")
        
        # Show a preview of the result
        preview = result[:500] + "..." if len(result) > 500 else result
        console.print(Panel(
            preview,
            title="[bold blue]📄 Result Preview[/bold blue]",
            border_style="blue"
        ))
        
        return True
    except Exception as e:
        console.print(f"[bold red]❌ Test failed with error: {e}[/bold red]")
        return False

if __name__ == "__main__":
    success = test_gemini_assembler()
    sys.exit(0 if success else 1) 