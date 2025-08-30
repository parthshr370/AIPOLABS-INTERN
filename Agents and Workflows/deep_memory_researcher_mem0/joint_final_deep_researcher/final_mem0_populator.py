# a way for anyone to populate their mem0 storage with synthetic medical data : )
# not recommended for real stuff obv

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
DOCTOR_MEMORY_ID = "doctor_memory"  # set user id constant as if one doctor examining multiple patients and mem0 is his personal memory silo
mem0 = MemoryClient()
model = ModelFactory.create(
    model_platform=ModelPlatformType.GEMINI,
    model_type="gemini-2.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY"),
    model_config_dict={"temperature": 0.3, "max_tokens": 40000},
)


def create_patient_disease_combo():
    """Generate unique patient-disease combo using LLM structured output"""

    # Force uniqueness with random seed in prompt
    import time

    random_seed = random.randint(1000, 9999)
    timestamp = int(time.time() * 1000) % 10000  # last 4 digits of milliseconds

    system_message = BaseMessage.make_assistant_message(
        role_name="MedicalGenerator",
        content=f"""Generate COMPLETELY UNIQUE patient with realistic medical condition. RANDOMIZATION SEED: {random_seed}-{timestamp}

CRITICAL: Generate ENTIRELY NEW names - NEVER use these common names:
- NO: John, Mary, Sarah, Michael, David, Jennifer, Lisa, Robert, Maria, James
- NO: Smith, Johnson, Williams, Brown, Jones, Garcia, Miller, Davis, Rodriguez, Martinez

MANDATORY UNIQUENESS REQUIREMENTS:
- Use uncommon first names from diverse cultures be different each time
- Use uncommon last names
- Vary age ranges (25-75), occupations, conditions completely
- Each generation must be COMPLETELY different from any previous one
- All of them need to have some sorts of chronic diseases and some associated diseases .

Return ONLY raw JSON - no markdown, no code blocks, no ```json formatting:
{{
    "patient_name": "[Full Name]",
    "age": "[25-75]",
    "gender": "[gender]",
    "occupation": "[occupation]",
    "condition": {{
        "name": "[Medical condition]",
        "icd10": "[code]",
        "symptoms": "[specific symptoms]",
        "vitals": "[vital signs with values]",
        "medications": "[medications with dosages]",
        "family_history": "[relevant history]"
    }}
}}

Use realistic medical data, actual drug names with mg/mcg dosages, real BP/HR/lab values.""",
    )

    agent = ChatAgent(system_message=system_message, model=model)
    response = agent.step(
        BaseMessage.make_user_message("User", "Generate unique patient-disease data")
    )

    output = response.msg.content.strip()
    unique_id = f"patient_{random.randint(10000, 99999)}"

    return {"raw_output": output, "unique_id": unique_id}


def generate_conversation(patient_disease_combo, rounds=5):
    """Generate realistic doctor-patient conversation"""

    raw_data = patient_disease_combo["raw_output"]

    society = RolePlaying(
        assistant_role_name="Dr. Sarah Chen",
        user_role_name="Patient",
        task_prompt=f"Medical consultation based on: {raw_data}",
        with_task_specify=False,
        assistant_agent_kwargs={"model": model},
        user_agent_kwargs={"model": model},
        extend_sys_msg_meta_dicts=[
            {
                "assistant_role": "Dr. Sarah Chen",
                "user_role": "Patient",
                "task": f"You're Dr. Chen consulting a UNIQUE patient. Patient data: {raw_data}. ALWAYS address the patient by their exact full name from the data in EVERY response. Reference their name when discussing their condition, medications, or treatment.Act and talk like a normal person , short and to the point sentecnes convey necessary information ",
            },
            {
                "assistant_role": "Dr. Sarah Chen",
                "user_role": "Patient",
                "task": f"You are THIS SPECIFIC patient: {raw_data}. ALWAYS introduce yourself with your full name. When describing symptoms or answering questions, use phrases like 'I am [Full Name] and I...' to ensure your identity is clear in every response. Make sure that your answers are always short to the point and full of information , just talk like you just want to tell your condition ",
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
                "patient": user_response.msg.content,
                "doctor": assistant_response.msg.content,
            }
        )

        input_msg = assistant_response.msg

        if "CAMEL_TASK_DONE" in user_response.msg.content:
            break

    return conversations


def create_patient_summary(conversations, patient_data, patient_name):
    """Create a comprehensive patient summary with guaranteed name inclusion"""

    # Combine all conversations into one context
    full_conversation = ""
    for i, convo in enumerate(conversations):
        full_conversation += f"Round {i + 1}:\nPatient: {convo['patient']}\nDr. Sarah Chen: {convo['doctor']}\n\n"

    summary_prompt = f"""Create a comprehensive medical summary for {patient_name} based on this consultation.

Patient Data: {patient_data}
Conversation: {full_conversation}

Create 5-7 specific medical facts, each starting with "{patient_name}":
Example format:
- {patient_name} is 45 years old and works as a teacher
- {patient_name} has been diagnosed with hypertension
- {patient_name} is taking lisinopril 10mg daily
- {patient_name} reports chest pain and fatigue
- {patient_name} has a family history of heart disease

Return only the medical facts, one per line, each starting with the patient's full name."""

    try:
        # Use CAMEL agent like the rest of the code
        system_message = BaseMessage.make_assistant_message(
            role_name="MedicalSummarizer",
            content="You are a medical summarizer. Create specific medical facts from conversations.",
        )

        agent = ChatAgent(system_message=system_message, model=model)
        response = agent.step(BaseMessage.make_user_message("User", summary_prompt))

        # Split into individual facts and clean them
        facts = [
            fact.strip()
            for fact in response.msg.content.strip().split("\n")
            if fact.strip() and patient_name in fact
        ]
        return facts
    except Exception as e:
        rprint(f"[red]Error generating summary: {e}[/red]")
        return []


def store_patient_summary(conversations, patient_disease_combo):
    """Store patient summary directly without automatic fact extraction"""

    unique_id = patient_disease_combo["unique_id"]
    raw_data = patient_disease_combo["raw_output"]

    try:
        import json

        patient_data = json.loads(raw_data)
        patient_name = patient_data["patient_name"]
    except (json.JSONDecodeError, KeyError):
        rprint(f"[red]Error parsing patient data[/red]")
        return 0

    # Create summary
    summary_facts = create_patient_summary(conversations, raw_data, patient_name)

    stored = 0
    agent_id = f"patient_{unique_id}"

    for fact in summary_facts:
        if fact.strip() and patient_name in fact:
            try:
                mem0.add(
                    messages=[{"role": "assistant", "content": fact}],
                    user_id=DOCTOR_MEMORY_ID,
                    agent_id=agent_id,
                    metadata={
                        "patient_name": patient_name,
                        "patient_id": unique_id,
                        "summary_fact": True,
                        "session_type": f"consultation_with_{patient_name.replace(' ', '_').lower()}",
                    },
                )
                stored += 1
            except Exception as e:
                rprint(f"[red]Error storing fact: {e}[/red]")

    return stored


def process_single_patient(rounds=5):
    # some fancy rptint statmtnst for user to see live

    """Generate one patient case and store conversation"""
    rprint(Panel("[yellow]Starting new patient case[/yellow]"))
    combo = create_patient_disease_combo()

    # Display patient info
    try:
        import json

        patient_data = json.loads(combo["raw_output"])
        patient_name = patient_data["patient_name"]
        condition_name = patient_data["condition"]["name"]
        age = patient_data["age"]
        gender = patient_data["gender"]
        rprint(f"[green]Patient: {patient_name} ({age}y, {gender})[/green]")
        rprint(f"[blue]Condition: {condition_name}[/blue]")
    except (json.JSONDecodeError, KeyError) as e:
        rprint(f"[red]Error parsing patient data: {e}[/red]")
        rprint(f"[yellow]Raw output: {combo['raw_output'][:200]}...[/yellow]")

    rprint("\n[yellow]Creating conversation...[/yellow]")
    conversations = generate_conversation(combo, rounds)

    # Log each conversation round
    for i, convo in enumerate(conversations):
        rprint(f"\n[cyan]Round {i + 1}:[/cyan]")
        try:
            patient_name = patient_data["patient_name"]
            rprint(f"[magenta]{patient_name}:[/magenta] {convo['patient']}")
        except (NameError, KeyError):
            rprint(f"[magenta]Patient:[/magenta] {convo['patient']}")
        rprint(f"[green]Dr. Sarah Chen:[/green] {convo['doctor']}")

    rprint("\n[yellow]Creating patient summary and storing in memory...[/yellow]")
    stored = store_patient_summary(conversations, combo)
    rprint(f"[green]Stored {stored} medical facts[/green]\n")

    return stored


def get_memory_status():
    """Check memory database status from mem0"""
    rprint("[yellow]Checking memory status...[/yellow]")
    try:
        memories = mem0.search(
            query="Dr. Sarah Chen", user_id=DOCTOR_MEMORY_ID, limit=100
        )
        count = len(memories) if memories else 0
        rprint(f"[green]Found {count} memories in database[/green]")
        return count
    except Exception as e:
        rprint(f"[red]Error checking status: {e}[/red]")
        return 0


def clear_memory():
    """Clear all memories from database"""
    try:
        mem0.delete_all(
            user_id=DOCTOR_MEMORY_ID
        )  # you can use this but not relevant to this usecase of population anyways
        rprint("[green]Memory database cleared[/green]")
        return True
    except Exception as e:
        rprint(f"[red]Error clearing memory: {e}[/red]")
        return False


if __name__ == "__main__":
    # Uncomment the following line to clear all existing memories before starting
    # clear_memory()  # This will delete all stored memories for DOCTOR_MEMORY_ID

    stored = process_single_patient()  # loop for one patient
    rprint(f"[cyan]Stored {stored} conversations[/cyan]")

    # change value for how many unique patietts
    for i in range(10):
        process_single_patient()

    # end loop with memory status
    total_memories = get_memory_status()
    rprint(Panel(f"[green]Total memories in database: {total_memories}[/green]"))
