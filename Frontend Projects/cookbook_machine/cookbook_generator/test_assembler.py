#!/usr/bin/env python3
"""
Test script for the Assembler Agent to verify it works independently.
This script creates a simple test with minimal content to ensure the assembler
can process and combine sections without hitting token limits.
"""

import sys
import os
from agents.assembler import run_assembler
from rich.console import Console

console = Console()

def main():
    """Run a simple test of the assembler agent with minimal content."""
    console.print("[bold yellow]🧪 ASSEMBLER AGENT TEST[/bold yellow]")
    
    # Create some simple test content - much smaller than real content
    test_sections = [
        """# Introduction
        
        This is a simple test section for the assembler agent.
        
        ```python
        def hello_world():
            print("Hello, world!")
        ```
        """,
        
        """# Setup
        
        This is another test section to verify the assembler works.
        
        ```python
        def setup():
            # Initialize environment
            return True
        ```
        """
    ]
    
    console.print(f"[bold cyan]Test sections created: {len(test_sections)}[/bold cyan]")
    console.print(f"[bold cyan]Total test content size: {sum(len(s) for s in test_sections)} characters[/bold cyan]")
    
    # Run the assembler with minimal content
    try:
        result = run_assembler(test_sections)
        console.print("[bold green]✅ Test completed successfully![/bold green]")
        console.print(f"[bold cyan]Result length: {len(result)} characters[/bold cyan]")
    except Exception as e:
        console.print(f"[bold red]❌ Test failed with error: {e}[/bold red]")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 