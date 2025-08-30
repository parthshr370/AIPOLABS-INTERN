#!/usr/bin/env python3

import os
import warnings
from dotenv import load_dotenv
from mem0 import MemoryClient
from rich import print as rprint

from camel.societies import RolePlaying
from camel.models import ModelFactory
from camel.types import ModelPlatformType

warnings.filterwarnings("ignore", category=DeprecationWarning)
load_dotenv()

# Simple configuration
DOCTOR_MEMORY_ID = "doctor_memory"
MEM0_API_KEY = os.getenv("MEM0_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not MEM0_API_KEY or not GOOGLE_API_KEY:
    rprint("[red]Missing API keys in environment[/red]")
    exit(1)

# Initialize
mem0 = MemoryClient()
model = ModelFactory.create(
    model_platform=ModelPlatformType.GEMINI,
    model_type="gemini-2.5-flash",
    api_key=GOOGLE_API_KEY,
    model_config_dict={"temperature": 0.2, "max_tokens": 4096},
)


def generate_medical_data(rounds=6):
    """Generate medical conversation data - raw and detailed"""
    rprint("[green]🏥 Generating medical consultation data...[/green]")

    # Medical context for detailed conversations
    medical_context = """
    Generate DETAILED medical consultation with:
    - Specific vital signs: BP 142/88 mmHg, HR 76 bpm, Temp 98.6°F
    - Lab values: Glucose 156 mg/dL, HbA1c 7.2%, Cholesterol 245 mg/dL
    - Precise medications: Metformin 1000mg BID, Lisinopril 20mg daily
    - ICD-10 diagnoses: Type 2 Diabetes E11.9, Hypertension I10
    - Detailed symptoms: Chest pain 8/10 severity, radiating to left arm
    - Family history: Father MI age 58, mother diabetes
    - Social history: Smokes 1 PPD x 20 years, drinks 3 beers daily
    """

    # Simple RolePlaying setup
    society = RolePlaying(
        assistant_role_name="Dr. Sarah Chen",
        user_role_name="Patient Alex Thompson",
        task_prompt="Conduct detailed medical consultation with comprehensive clinical data",
        with_task_specify=False,
        assistant_agent_kwargs={"model": model},
        user_agent_kwargs={"model": model},
        extend_sys_msg_meta_dicts=[
            {
                "assistant_role": "Dr. Sarah Chen",
                "user_role": "Patient Alex Thompson",
                "task": medical_context,
            },
            {
                "assistant_role": "Dr. Sarah Chen",
                "user_role": "Patient Alex Thompson",
                "task": medical_context,
            },
        ],
    )

    # Generate conversation rounds
    conversations = []
    input_msg = society.init_chat()

    for i in range(rounds):
        assistant_response, user_response = society.step(input_msg)

        if assistant_response.terminated or user_response.terminated:
            break

        conversations.append(
            {
                "patient": user_response.msg.content,
                "doctor": assistant_response.msg.content,
            }
        )

        # VERBOSE LOGGING - Show all conversation details
        rprint(f"\n[bold cyan]═══ ROUND {i + 1} DETAILS ═══[/bold cyan]")
        rprint(f"[blue]👤 PATIENT:[/blue] {user_response.msg.content}")
        rprint(f"[red]👨‍⚕️ DOCTOR:[/red] {assistant_response.msg.content}")
        rprint(f"[dim]─── End Round {i + 1} ───[/dim]\n")

        input_msg = assistant_response.msg

        if "CAMEL_TASK_DONE" in user_response.msg.content:
            break

    rprint(f"[green]✅ Generated {len(conversations)} conversation rounds[/green]")
    return conversations


def add_to_memory(conversations):
    """Add raw conversation data to mem0 - let mem0 handle extraction"""
    rprint("\n[bold yellow]💾 ADDING DATA TO MEM0 - VERBOSE MODE[/bold yellow]")

    stored = 0
    for i, convo in enumerate(conversations):
        try:
            # Simple format - let mem0 do the magic
            messages = [
                {"role": "user", "content": f"Patient: {convo['patient']}"},
                {"role": "assistant", "content": f"Doctor: {convo['doctor']}"},
            ]

            rprint(
                f"\n[bold magenta]📤 SENDING TO MEM0 - Round {i + 1}:[/bold magenta]"
            )
            rprint(f"[dim]User ID: {DOCTOR_MEMORY_ID}[/dim]")
            rprint(f"[dim]Messages format: {messages}[/dim]")

            # Call mem0.add and show response
            result = mem0.add(messages=messages, user_id=DOCTOR_MEMORY_ID)
            rprint(f"[green]✅ MEM0 Response: {result}[/green]")

            stored += 1
        except Exception as e:
            rprint(f"[red]❌ Error storing round {i + 1}: {e}[/red]")

    rprint(
        f"\n[bold green]🎉 FINAL RESULT: Added {stored}/{len(conversations)} conversations to memory[/bold green]"
    )
    return stored


def main():
    """Main loop: Generate data → Add to memory → Repeat"""
    rprint("[bold blue]🩺 Simple Medical Memory Feeder[/bold blue]\n")

    while True:
        try:
            command = (
                input(
                    "Enter 'generate' to create data, 'status' to check, 'reset' to clear, 'exit' to quit: "
                )
                .strip()
                .lower()
            )

            if command == "exit":
                rprint("[yellow]Goodbye![/yellow]")
                break

            elif command == "generate":
                rprint(
                    "\n[bold blue]🚀 STARTING MEDICAL DATA GENERATION & STORAGE PROCESS[/bold blue]"
                )
                rprint(
                    "[dim]═══════════════════════════════════════════════════════[/dim]"
                )

                # Step 1: Generate medical data with full logging
                rprint(
                    "[bold cyan]STEP 1: GENERATING MEDICAL CONVERSATIONS[/bold cyan]"
                )
                conversations = generate_medical_data(rounds=6)

                if conversations:
                    rprint(
                        "\n[bold cyan]STEP 2: FEEDING TO MEM0 MEMORY STORE[/bold cyan]"
                    )
                    # Step 2: Add to memory with verbose logging
                    stored_count = add_to_memory(conversations)

                    rprint("\n[bold blue]═══ PROCESS COMPLETE ═══[/bold blue]")
                    rprint(
                        f"[bold green]🎉 Generated: {len(conversations)} conversation rounds[/bold green]"
                    )
                    rprint(
                        f"[bold green]🎉 Stored: {stored_count} in mem0[/bold green]"
                    )
                    rprint(
                        f"[bold green]🎉 Success Rate: {stored_count}/{len(conversations)} ({100 * stored_count / len(conversations):.1f}%)[/bold green]"
                    )
                else:
                    rprint("[red]❌ No data generated[/red]")

            elif command == "status":
                try:
                    memories = mem0.search(
                        query="medical", user_id=DOCTOR_MEMORY_ID, limit=50
                    )
                    count = len(memories) if memories else 0
                    rprint(f"[blue]📊 Current memories in store: {count}[/blue]")
                except:
                    rprint("[red]Error checking status[/red]")

            elif command == "reset":
                mem0.delete_all(user_id=DOCTOR_MEMORY_ID)
                rprint("[yellow]🗑️ Memory cleared[/yellow]")

            else:
                rprint("[yellow]Commands: generate, status, reset, exit[/yellow]")

        except KeyboardInterrupt:
            rprint("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            rprint(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    main()
