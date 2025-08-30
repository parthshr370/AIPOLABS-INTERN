#!/usr/bin/env python3
"""
🧠 Simple Mem0 + CAMEL AI Agent
===============================

A clean, simple implementation of a CAMEL AI agent with the enhanced Mem0CloudToolkit.
This agent has persistent memory capabilities with all 18+ memory management tools.

Usage:
    python simple_mem0_camel_agent.py

Requirements:
    - MEM0_API_KEY environment variable
    - OPENAI_API_KEY environment variable  
    - camel-ai and mem0ai packages installed
"""

import os
from rich.console import Console
from rich.panel import Panel

# CAMEL AI imports
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType

# Import our enhanced Mem0 toolkit
from mem_camel_toolkit import Mem0CloudToolkit

class SimpleMem0Agent:
    """A simple CAMEL AI agent with enhanced Mem0 memory capabilities."""
    
    def __init__(self, agent_id: str = "simple-agent", user_id: str = "user"):
        self.agent_id = agent_id
        self.user_id = user_id
        self.console = Console()
        
        # Initialize the enhanced Mem0 toolkit (18+ tools)
        self.toolkit = Mem0CloudToolkit(agent_id=self.agent_id, user_id=self.user_id)
        tools = self.toolkit.get_tools()
        
        # Create the language model
        model = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_4O_MINI,
        )
        
        # Simple but effective system message
        system_message = """
You are a helpful AI assistant with advanced memory capabilities. You can:

- Store and retrieve memories with rich metadata
- Search through memories using semantic search
- Update and manage existing memories
- Perform batch operations for efficiency
- Track memory history and provide analytics
- Export memory data and provide insights

Always explain what memory operations you're performing and be helpful and conversational.
When users ask about your capabilities, mention that you have 18+ memory management tools available.
"""
        
        sys_msg = BaseMessage.make_assistant_message(
            role_name="Mem0 Assistant",
            content=system_message,
        )
        
        # Create the agent with all memory tools
        self.agent = ChatAgent(sys_msg, model=model, tools=tools)
        
        self.console.print(Panel.fit(
            f"[bold green]🧠 Mem0 Agent Ready![/bold green]\n"
            f"[dim]Agent ID: {self.agent_id} | User ID: {self.user_id}[/dim]\n"
            f"[dim]Available Tools: {len(tools)}[/dim]",
            border_style="green"
        ))
    
    def chat(self):
        """Start interactive chat with the agent."""
        self.console.print("\n[bold cyan]💬 Start chatting with your Mem0-enabled agent![/bold cyan]")
        self.console.print("[dim]Type 'exit' or 'quit' to end the conversation.[/dim]\n")
        
        while True:
            try:
                # Get user input
                user_input = input("\n🤔 You: ")
                
                if user_input.lower().strip() in ["exit", "quit", "bye"]:
                    self.console.print("[yellow]👋 Goodbye! Your memories are safely stored.[/yellow]")
                    break
                
                if not user_input.strip():
                    continue
                
                # Process with agent
                user_msg = BaseMessage.make_user_message(role_name="User", content=user_input)
                
                # Show thinking indicator
                with self.console.status("[bold green]🧠 Thinking...[/bold green]"):
                    response = self.agent.step(user_msg)
                
                # Display response
                self.console.print(f"\n🤖 [bold green]Agent:[/bold green] {response.msg.content}")
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]👋 Chat interrupted. Goodbye![/yellow]")
                break
            except Exception as e:
                self.console.print(f"\n[red]❌ Error: {e}[/red]")
                continue


def check_environment():
    """Check if required environment variables are set."""
    console = Console()
    
    required_vars = ["MEM0_API_KEY", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        console.print(f"[red]❌ Missing environment variables: {', '.join(missing_vars)}[/red]")
        console.print("\n[yellow]Please set:[/yellow]")
        for var in missing_vars:
            if var == "MEM0_API_KEY":
                console.print(f"  export {var}='your-key-here'  # Get from https://app.mem0.ai")
            else:
                console.print(f"  export {var}='your-key-here'")
        return False
    
    return True


def main():
    """Main function."""
    console = Console()
    
    # Show header
    console.print("""
[bold blue]🧠 Simple Mem0 + CAMEL AI Agent[/bold blue]
[dim]Enhanced memory capabilities with 18+ tools[/dim]
    """)
    
    # Check environment
    if not check_environment():
        return
    
    # Create and run agent
    try:
        agent = SimpleMem0Agent()
        agent.chat()
    except Exception as e:
        console.print(f"[red]❌ Failed to create agent: {e}[/red]")


if __name__ == "__main__":
    main()