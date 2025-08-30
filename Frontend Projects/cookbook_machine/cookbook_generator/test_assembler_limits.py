#!/usr/bin/env python3
"""
Test script for the Assembler Agent to identify token limit issues.
This script creates test content of increasing size to determine at what point
the assembler agent hits token limits.
"""

import sys
import os
import time
from agents.assembler import run_assembler
from rich.console import Console
from rich.panel import Panel

console = Console()

def generate_test_content(size_per_section, num_sections):
    """Generate test content with the specified size."""
    sections = []
    
    for i in range(num_sections):
        # Create a section with approximately size_per_section characters
        section_title = f"# Section {i+1}\n\n"
        
        # Add some markdown content
        content = f"This is test content for section {i+1}.\n\n"
        
        # Add a code block
        code_block = "```python\n"
        code_block += "def test_function():\n"
        code_block += "    # This is a comment\n"
        code_block += "    print('This is a test function')\n"
        code_block += "    return True\n"
        code_block += "```\n\n"
        
        # Calculate how much filler text we need
        filler_size = size_per_section - len(section_title) - len(content) - len(code_block)
        filler = "Lorem ipsum dolor sit amet. " * (filler_size // 30)
        
        # Combine everything
        section = section_title + content + code_block + filler
        sections.append(section)
    
    return sections

def main():
    """Run tests with increasing content size to find token limits."""
    console.print("[bold yellow]🧪 ASSEMBLER AGENT TOKEN LIMIT TEST[/bold yellow]")
    
    # Start with small content and gradually increase
    section_sizes = [1000, 2000, 5000]  # Characters per section
    section_counts = [2, 4, 6]          # Number of sections
    
    for size in section_sizes:
        for count in section_counts:
            total_size = size * count
            console.print(f"\n[bold cyan]Testing with {count} sections of {size} characters each (total: {total_size})[/bold cyan]")
            
            # Generate test content
            test_sections = generate_test_content(size, count)
            actual_size = sum(len(s) for s in test_sections)
            
            console.print(Panel(
                f"[bold white]Sections:[/bold white] {count}\n"
                f"[bold white]Target size per section:[/bold white] {size} characters\n"
                f"[bold white]Actual total size:[/bold white] {actual_size} characters",
                title="[bold yellow]📊 Test Configuration[/bold yellow]",
                border_style="yellow"
            ))
            
            # Run the assembler
            try:
                start_time = time.time()
                result = run_assembler(test_sections)
                end_time = time.time()
                
                console.print("[bold green]✅ Test completed successfully![/bold green]")
                console.print(f"[bold cyan]Processing time: {end_time - start_time:.2f} seconds[/bold cyan]")
                console.print(f"[bold cyan]Result length: {len(result)} characters[/bold cyan]")
            except Exception as e:
                console.print(f"[bold red]❌ Test failed with error: {e}[/bold red]")
                console.print(f"[bold red]This indicates the token limit is likely between {total_size/1000:.1f}K and {total_size/1000:.1f}K characters[/bold red]")
                return 1
    
    console.print("\n[bold green]🎉 All tests completed successfully![/bold green]")
    console.print("[bold yellow]The assembler can handle at least up to the largest tested size.[/bold yellow]")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 