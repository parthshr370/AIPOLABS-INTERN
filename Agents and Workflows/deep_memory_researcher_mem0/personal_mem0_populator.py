# a way to populate mem0 storage with personal memories about Dr. Parth Sharma
# creates mundane personal and professional memories

import os
import random
import warnings
from dotenv import load_dotenv
from mem0 import MemoryClient
from rich import print as rprint
from rich.panel import Panel

from camel.societies import RolePlaying
from camel.models import ModelFactory
from camel.types import ModelPlatformType
from camel.agents import ChatAgent
from camel.messages import BaseMessage

warnings.filterwarnings("ignore", category=DeprecationWarning)
load_dotenv()

# Configuration
PARTH_MEMORY_ID = "doctor_memory"  # personal memory silo for Dr. Parth Sharma
mem0 = MemoryClient()
model = ModelFactory.create(
    model_platform=ModelPlatformType.GEMINI,
    model_type="gemini-2.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY"),
    model_config_dict={"temperature": 0.3, "max_tokens": 40000},
)


def create_personal_memory_scenario():
    """Generate unique personal memory scenario using LLM structured output"""
    
    import time
    
    random_seed = random.randint(1000, 9999)
    timestamp = int(time.time() * 1000) % 10000
    
    system_message = BaseMessage.make_assistant_message(
        role_name="PersonalMemoryGenerator",
        content=f"""Generate a COMPLETELY UNIQUE personal memory scenario about Dr. Parth Sharma. RANDOMIZATION SEED: {random_seed}-{timestamp}

CONTEXT: Dr. Parth Sharma is a medical doctor with:
- Wife and daughter
- Professional medical practice
- Personal hobbies and interests
- Daily routines and preferences
- Relationships with colleagues and friends

MANDATORY UNIQUENESS REQUIREMENTS:
- Generate different scenarios each time (family moments, professional situations, hobbies, preferences, memories)
- Include diverse aspects: medical work, family time, personal interests, food preferences, travel, childhood memories
- Vary the type of memory: recent events, habits, preferences, relationships, professional experiences
- Each generation must be COMPLETELY different from any previous one

Memory categories to choose from:
- Family moments with wife and daughter
- Professional medical experiences
- Personal hobbies and interests  
- Food and restaurant preferences
- Travel experiences
- Childhood or past memories
- Daily routines and habits
- Relationships with colleagues/friends
- Personal achievements or milestones

Return ONLY raw JSON - no markdown, no code blocks, no ```json formatting:
{{
    "memory_type": "[category from above list]",
    "scenario_context": "[detailed context of the memory/preference/habit]",
    "key_details": "[specific details that make this memorable]",
    "people_involved": "[family, colleagues, friends mentioned]",
    "location": "[where this takes place/took place]",
    "emotional_context": "[how Parth feels about this]",
    "frequency": "[how often this happens/happened - daily, weekly, once, etc.]"
}}

Make it realistic, mundane but memorable. Focus on the kind of personal details that make someone human.""",
    )
    
    agent = ChatAgent(system_message=system_message, model=model)
    response = agent.step(
        BaseMessage.make_user_message("User", "Generate unique personal memory scenario for Dr. Parth Sharma")
    )
    
    output = response.msg.content.strip()
    unique_id = f"memory_{random.randint(10000, 99999)}"
    
    return {"raw_output": output, "unique_id": unique_id}


def generate_memory_conversation(memory_scenario, rounds=3):
    """Generate conversation about personal memories"""
    
    raw_data = memory_scenario["raw_output"]
    
    society = RolePlaying(
        assistant_role_name="Memory Narrator",
        user_role_name="Dr. Parth Sharma",
        task_prompt=f"Personal memory discussion based on: {raw_data}",
        with_task_specify=False,
        assistant_agent_kwargs={"model": model},
        user_agent_kwargs={"model": model},
        extend_sys_msg_meta_dicts=[
            {
                "assistant_role": "Memory Narrator",
                "user_role": "Dr. Parth Sharma",
                "task": f"You're asking Dr. Parth Sharma about his personal memories/preferences. Memory context: {raw_data}. Ask thoughtful questions about his experiences, feelings, and details. Keep responses conversational and natural.",
            },
            {
                "assistant_role": "Memory Narrator", 
                "user_role": "Dr. Parth Sharma",
                "task": f"You are Dr. Parth Sharma reflecting on your personal life. Memory context: {raw_data}. Share personal details naturally, using 'I like to...', 'I remember when...', 'My daughter always...', 'My wife and I...'. Be authentic and share specific personal details about your life, preferences, and experiences.",
            },
        ],
    )
    
    conversations = []
    input_msg = society.init_chat()
    
    for i in range(rounds):
        assistant_response, user_response = society.step(input_msg)
        
        if assistant_response.terminated or user_response.terminated:
            break
            
        conversations.append(
            {
                "narrator": assistant_response.msg.content,
                "parth": user_response.msg.content,
            }
        )
        
        input_msg = assistant_response.msg
        
        if "CAMEL_TASK_DONE" in user_response.msg.content:
            break
            
    return conversations


def create_personal_summary(conversations, memory_data):
    """Create personal memory facts starting with 'Parth Sharma likes to' or similar"""
    
    # Combine all conversations into one context
    full_conversation = ""
    for i, convo in enumerate(conversations):
        full_conversation += f"Round {i + 1}:\nNarrator: {convo['narrator']}\nDr. Parth Sharma: {convo['parth']}\n\n"
    
    summary_prompt = f"""Create personal memory facts about Dr. Parth Sharma based on this conversation.

Memory Context: {memory_data}
Conversation: {full_conversation}

Create 4-6 specific personal facts, each starting with "Parth Sharma" in these formats:
- Parth Sharma likes to...
- Parth Sharma enjoys...
- Parth Sharma prefers...
- Parth Sharma often...
- Parth Sharma remembers...
- Parth Sharma has a habit of...
- Parth Sharma's daughter...
- Parth Sharma's wife...

Examples:
- Parth Sharma likes to have coffee every morning at 7 AM
- Parth Sharma enjoys playing chess with his daughter on weekends
- Parth Sharma prefers Indian cuisine over continental food
- Parth Sharma often works late on Tuesdays due to his clinic schedule
- Parth Sharma remembers his first day as a resident doctor fondly

Return only the personal facts, one per line, each starting with "Parth Sharma"."""
    
    try:
        system_message = BaseMessage.make_assistant_message(
            role_name="PersonalMemorySummarizer",
            content="You are creating personal memory facts about Dr. Parth Sharma from conversations.",
        )
        
        agent = ChatAgent(system_message=system_message, model=model)
        response = agent.step(BaseMessage.make_user_message("User", summary_prompt))
        
        # Split into individual facts and clean them
        facts = [
            fact.strip()
            for fact in response.msg.content.strip().split("\n")
            if fact.strip() and "Parth Sharma" in fact
        ]
        return facts
    except Exception as e:
        rprint(f"[red]Error generating personal summary: {e}[/red]")
        return []


def store_personal_memories(conversations, memory_scenario):
    """Store personal memory facts in mem0"""
    
    unique_id = memory_scenario["unique_id"]
    raw_data = memory_scenario["raw_output"]
    
    try:
        import json
        memory_data = json.loads(raw_data)
        memory_type = memory_data["memory_type"]
    except (json.JSONDecodeError, KeyError):
        rprint(f"[red]Error parsing memory data[/red]")
        return 0
    
    # Create summary
    summary_facts = create_personal_summary(conversations, raw_data)
    
    stored = 0
    agent_id = f"personal_memory_{unique_id}"
    
    for fact in summary_facts:
        if fact.strip() and "Parth Sharma" in fact:
            try:
                mem0.add(
                    messages=[{"role": "assistant", "content": fact}],
                    user_id=PARTH_MEMORY_ID,
                    agent_id=agent_id,
                    metadata={
                        "memory_type": memory_type,
                        "memory_id": unique_id,
                        "personal_fact": True,
                        "session_type": f"personal_memory_{memory_type.replace(' ', '_').lower()}",
                    },
                )
                stored += 1
            except Exception as e:
                rprint(f"[red]Error storing personal fact: {e}[/red]")
    
    return stored


def process_single_memory(rounds=3):
    """Generate one personal memory scenario and store it"""
    rprint(Panel("[yellow]Creating new personal memory[/yellow]"))
    scenario = create_personal_memory_scenario()
    
    # Display memory info
    try:
        import json
        memory_data = json.loads(scenario["raw_output"])
        memory_type = memory_data["memory_type"]
        context = memory_data["scenario_context"]
        rprint(f"[green]Memory Type: {memory_type}[/green]")
        rprint(f"[blue]Context: {context[:100]}...[/blue]")
    except (json.JSONDecodeError, KeyError) as e:
        rprint(f"[red]Error parsing memory data: {e}[/red]")
        rprint(f"[yellow]Raw output: {scenario['raw_output'][:200]}...[/yellow]")
    
    rprint("\n[yellow]Creating memory conversation...[/yellow]")
    conversations = generate_memory_conversation(scenario, rounds)
    
    # Log each conversation round
    for i, convo in enumerate(conversations):
        rprint(f"\n[cyan]Round {i + 1}:[/cyan]")
        rprint(f"[magenta]Narrator:[/magenta] {convo['narrator']}")
        rprint(f"[green]Dr. Parth Sharma:[/green] {convo['parth']}")
    
    rprint("\n[yellow]Creating personal facts and storing in memory...[/yellow]")
    stored = store_personal_memories(conversations, scenario)
    rprint(f"[green]Stored {stored} personal facts[/green]\n")
    
    return stored


def get_personal_memory_status():
    """Check personal memory database status"""
    rprint("[yellow]Checking personal memory status...[/yellow]")
    try:
        memories = mem0.search(
            query="Parth Sharma", user_id=PARTH_MEMORY_ID, limit=100
        )
        count = len(memories) if memories else 0
        rprint(f"[green]Found {count} personal memories in database[/green]")
        return count
    except Exception as e:
        rprint(f"[red]Error checking status: {e}[/red]")
        return 0


def clear_personal_memory():
    """Clear all personal memories from database"""
    try:
        mem0.delete_all(user_id=PARTH_MEMORY_ID)
        rprint("[green]Personal memory database cleared[/green]")
        return True
    except Exception as e:
        rprint(f"[red]Error clearing memory: {e}[/red]")
        return False


if __name__ == "__main__":
    # Uncomment the following line to clear all existing memories before starting
    # clear_personal_memory()  # This will delete all stored memories for PARTH_MEMORY_ID
    
    stored = process_single_memory()  # process one memory scenario
    rprint(f"[cyan]Stored {stored} personal facts[/cyan]")
    
    # Generate multiple personal memories
    for i in range(15):
        process_single_memory()
    
    # Display final status
    total_memories = get_personal_memory_status()
    rprint(Panel(f"[green]Total personal memories in database: {total_memories}[/green]"))