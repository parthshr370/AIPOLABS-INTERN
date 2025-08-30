import os
import warnings
from dotenv import load_dotenv
from mem0 import MemoryClient
from rich.console import Console
from rich.panel import Panel

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType

# Suppress noisy deprecation warnings from underlying libraries
warnings.filterwarnings("ignore", category=DeprecationWarning)


load_dotenv()

# api keys and stuff
USER_ID = "inventory_reporter"
MEM0_API_KEY = os.getenv("MEM0_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

console = Console()
if not MEM0_API_KEY or not GEMINI_API_KEY:
    console.print("[red]Error: Missing API keys in environment variables[/red]")
    exit(1)

# init memory in mem0
mem0 = MemoryClient()

# init llm inside camel
model = ModelFactory.create(
    model_platform=ModelPlatformType.GEMINI,
    model_type=ModelType.GEMINI_2_5_PRO,
    api_key=GEMINI_API_KEY,
    model_config_dict={"temperature": 0.2},
)

def main():
    """Simple, LLM-driven chat interface for inventory management."""
    console.print(Panel(
        "[bold blue]TAHAKOM Smart Inventory Agent[/bold blue]\n\n"
        "Just talk to me. I'll understand and remember everything.\n\n"
        "📝 [bold]To add items:[/bold] 'We just received 100 units of Part A for Warehouse 2.'\n"
        "❓ [bold]To ask questions:[/bold] 'What's the stock level of Part A?' or 'Summarize all inventory.'\n\n"
        "Type 'exit' to quit. To start fresh, type 'reset'.",
        title="🏭 Smart City Inventory System",
        border_style="green"
    ))
    # the loop that runs the agent
    while True:
        try:
            user_input = console.input("\n[bold cyan]You:[/bold cyan] ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                console.print("[yellow]Goodbye![/yellow]")
                break

            if user_input.lower() == 'reset':
                console.print("[bold yellow]Clearing all memories for this user...[/bold yellow]")
                mem0.delete_all(user_id=USER_ID)
                console.print("[green]Memories cleared. Ready for a fresh start.[/green]")
                continue
                
            if not user_input:
                continue

            # 1. Search for relevant memories
            relevant_memories = mem0.search(query=user_input, user_id=USER_ID, limit=5)
            
            memory_context = ""
            if relevant_memories:
                memory_list = [mem['memory'] for mem in relevant_memories]
                memory_context = "Here is some relevant information from your memory:\n- " + "\n- ".join(memory_list)

            # 2. Create agent with context via a powerful system prompt
            system_prompt = f"""You are a smart inventory management assistant for Tahakom's smart cities.

Your tasks:
1.  **Parse & Acknowledge**: When the user gives an inventory update (e.g., 'received 50 widgets'), understand it and provide a brief confirmation of the details you've captured.
2.  **Answer Queries**: When the user asks a question, use the provided memories to give a clear, concise answer. If helpful, format the data into a markdown table.
3.  **Conversational Memory**: You remember this entire conversation. Use past interactions to inform your current response.

**Relevant Memories:**
{memory_context if memory_context else "No relevant memories found."}

Now, respond to the user's latest message.
"""
            # system message is the agent's instructions
            system_message = BaseMessage.make_assistant_message(
                role_name="InventoryAgent",
                content=system_prompt,
            )

            agent = ChatAgent(system_message=system_message, model=model)

            # fetch agents response from the json response
            user_message = BaseMessage.make_user_message(role_name="User", content=user_input)
            response = agent.step(user_message)
            response_content = response.msg.content
            
            console.print(Panel(response_content, title="🤖 Smart Agent", border_style="blue"))

            # memory
            conversation = [
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": response_content}
            ]
            mem0.add(messages=conversation, user_id=USER_ID)
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    main() 