#!/usr/bin/env python3
"""
Test script for a chunked approach to the Assembler Agent.
This script demonstrates how to handle large content by processing it in chunks.
"""

import sys
import os
import time
from camel.models import ModelFactory
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

# Add the parent directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cookbook_generator.camel_config import camel_config

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

def run_chunked_assembler(sections, max_chunk_size=15000):
    """
    Process large content by breaking it into manageable chunks.
    
    Args:
        sections: List of content sections
        max_chunk_size: Maximum size for each chunk in characters
        
    Returns:
        The final assembled content
    """
    console.print("\n[bold yellow]🔄 CHUNKED ASSEMBLER PROCESSING[/bold yellow]")
    
    # Create the model and agent
    console.print("[yellow]🏭 Creating CAMEL AI model instance...[/yellow]")
    assembler_config = camel_config.get_model_config("assembler")
    
    model = ModelFactory.create(
        model_platform=assembler_config["model_platform"],
        model_type=assembler_config["model_type"],
        model_config_dict={
            "temperature": assembler_config["temperature"],
            "max_tokens": assembler_config["max_tokens"]
        }
    )
    
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
    
    console.print("[green]✅ Agent created successfully[/green]")
    
    # Step 1: Group sections into chunks that don't exceed the token limit
    chunks = []
    current_chunk = []
    current_chunk_size = 0
    
    for section in sections:
        section_size = len(section)
        
        # If adding this section would exceed the chunk size, start a new chunk
        if current_chunk_size + section_size > max_chunk_size and current_chunk:
            chunks.append(current_chunk)
            current_chunk = [section]
            current_chunk_size = section_size
        else:
            current_chunk.append(section)
            current_chunk_size += section_size
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk)
    
    console.print(f"[bold cyan]Content divided into {len(chunks)} chunks[/bold cyan]")
    
    # Step 2: Process each chunk separately
    processed_chunks = []
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Processing chunks...", total=len(chunks))
        
        for i, chunk in enumerate(chunks):
            chunk_content = "\n\n---\n\n".join(chunk)
            chunk_size = len(chunk_content)
            
            console.print(f"[bold cyan]Processing chunk {i+1}/{len(chunks)} ({chunk_size} characters)[/bold cyan]")
            
            # Create the assembly request for this chunk
            assembly_request = f"""
            Please assemble and polish the following cookbook sections into a cohesive document:

            {chunk_content}

            Requirements:
            - Ensure smooth flow between sections
            - Fix any formatting inconsistencies
            - Make sure code blocks are properly formatted
            """
            
            # Process the chunk
            try:
                response = assembler_agent.step(assembly_request)
                processed_content = response.msgs[0].content
                processed_chunks.append(processed_content)
                console.print(f"[green]✅ Chunk {i+1} processed successfully[/green]")
            except Exception as e:
                console.print(f"[red]❌ Error processing chunk {i+1}: {e}[/red]")
                # Fall back to using the original content for this chunk
                processed_chunks.append(chunk_content)
            
            progress.update(task, advance=1)
    
    # Step 3: Final assembly of all processed chunks
    if len(processed_chunks) == 1:
        # If there's only one chunk, we're done
        return processed_chunks[0]
    else:
        # If there are multiple chunks, do a final assembly pass
        console.print("[bold yellow]🔄 Performing final assembly of all chunks...[/bold yellow]")
        
        # Create a summary of each chunk for the final assembly
        chunk_summaries = []
        for i, chunk in enumerate(processed_chunks):
            # Extract just the headings from each chunk to create a summary
            lines = chunk.split("\n")
            headings = [line for line in lines if line.startswith("#")]
            summary = "\n".join(headings[:5])  # Take up to 5 headings
            chunk_summaries.append(f"Chunk {i+1} contains:\n{summary}\n...")
        
        # Create the final assembly request
        final_request = f"""
        You have been given multiple chunks of a cookbook that need to be combined into a final document.
        
        Here's what each chunk contains:
        
        {chr(10).join(chunk_summaries)}
        
        Now, please combine these chunks into a single cohesive document:
        
        {chr(10).join(processed_chunks)}
        
        Ensure the final document has:
        1. A consistent style throughout
        2. Smooth transitions between the chunks
        3. No duplicate content or headings
        4. Proper formatting throughout
        """
        
        try:
            final_response = assembler_agent.step(final_request)
            final_content = final_response.msgs[0].content
            console.print("[green]✅ Final assembly completed successfully[/green]")
            return final_content
        except Exception as e:
            console.print(f"[red]❌ Error in final assembly: {e}[/red]")
            # Fall back to simple concatenation
            console.print("[yellow]⚠️ Falling back to simple concatenation of processed chunks[/yellow]")
            return "\n\n---\n\n".join(processed_chunks)

def main():
    """Test the chunked assembler approach."""
    console.print("[bold yellow]🧪 CHUNKED ASSEMBLER TEST[/bold yellow]")
    
    # Generate a large test content (30K characters total)
    section_size = 5000
    num_sections = 6
    console.print(f"[bold cyan]Generating {num_sections} sections of {section_size} characters each[/bold cyan]")
    
    test_sections = generate_test_content(section_size, num_sections)
    total_size = sum(len(s) for s in test_sections)
    
    console.print(Panel(
        f"[bold white]Sections:[/bold white] {num_sections}\n"
        f"[bold white]Size per section:[/bold white] {section_size} characters\n"
        f"[bold white]Total content size:[/bold white] {total_size} characters",
        title="[bold yellow]📊 Test Configuration[/bold yellow]",
        border_style="yellow"
    ))
    
    # Process the content using the chunked approach
    try:
        start_time = time.time()
        result = run_chunked_assembler(test_sections)
        end_time = time.time()
        
        console.print("[bold green]✅ Test completed successfully![/bold green]")
        console.print(f"[bold cyan]Processing time: {end_time - start_time:.2f} seconds[/bold cyan]")
        console.print(f"[bold cyan]Result length: {len(result)} characters[/bold cyan]")
        
        # Show a preview of the result
        preview = result[:500] + "..." if len(result) > 500 else result
        console.print(Panel(
            preview,
            title="[bold blue]📄 Result Preview[/bold blue]",
            border_style="blue"
        ))
        
        return 0
    except Exception as e:
        console.print(f"[bold red]❌ Test failed with error: {e}[/bold red]")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 