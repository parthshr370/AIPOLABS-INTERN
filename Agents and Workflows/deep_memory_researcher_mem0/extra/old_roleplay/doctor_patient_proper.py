#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from rich import print as rprint
from camel.societies import RolePlaying
from camel.models import ModelFactory
from camel.types import ModelPlatformType, TaskType

load_dotenv()

# Create Gemini model
model = ModelFactory.create(
    model_platform=ModelPlatformType.GEMINI,
    model_type="gemini-2.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY"),
    model_config_dict={"temperature": 0.0, "max_tokens": 4096},
)

# Method 1: Using extend_sys_msg_meta_dicts with CORRECT KEYS
# Valid keys: {'assistant_role', 'user_role', 'criteria', 'critic_role', 'role', 'task', 'action_space'}

medical_meta_dict_doctor = {
    "assistant_role": "Dr. Sarah Chen (Internal Medicine Physician)",
    "user_role": "Alex Thompson (45-year-old office worker patient)",
    "task": """Conduct medical consultation with specific requirements:
    Doctor should: Ask questions with severity scales (1-10), provide actual medical values like "BP 140/90 mmHg", 
    give diagnoses with ICD-10 codes like "Hypertension, I10", recommend medications with dosages like "Lisinopril 10mg daily".
    Patient should: Give specific symptoms like "Chest pain 7/10, started 3 days ago", mention actual medications like "Metformin 500mg twice daily", 
    share realistic vitals like "HR 78 bpm, weight 180 lbs", include family history and lifestyle factors."""
}

medical_meta_dict_patient = {
    "assistant_role": "Dr. Sarah Chen (Internal Medicine Physician)", 
    "user_role": "Alex Thompson (45-year-old office worker patient)",
    "task": """Medical consultation where patient provides specific symptom details with real values and doctor gives actual medical diagnoses, 
    lab results, and treatment recommendations using real medical terminology and reference ranges."""
}

# Set up kwargs for medical consultation using proper CAMEL pattern
task_kwargs = {
    "task_prompt": "Conduct a comprehensive medical consultation for diagnosis and treatment planning with real medical data",
    "with_task_specify": True,
    "task_specify_agent_kwargs": {"model": model},
}

user_role_kwargs = {
    "user_role_name": "Patient (Alex Thompson)",
    "user_agent_kwargs": {"model": model},
}

assistant_role_kwargs = {
    "assistant_role_name": "Doctor (Dr. Sarah Chen)", 
    "assistant_agent_kwargs": {"model": model},
}

# The magic: extend_sys_msg_meta_dicts to inject medical context
society = RolePlaying(
    **task_kwargs,
    **user_role_kwargs, 
    **assistant_role_kwargs,
    extend_sys_msg_meta_dicts=[medical_meta_dict_doctor, medical_meta_dict_patient]  # One for each agent
)

def is_terminated(response):
    if response.terminated:
        role = response.msg.role_type.name
        reason = response.info["termination_reasons"]
        rprint(f"[red]AI {role} terminated due to {reason}[/red]")
    return response.terminated

def run(society, round_limit: int = 6):
    rprint("[bold green]🏥 Medical Consultation Session Started[/bold green]")
    rprint("[dim]Using extend_sys_msg_meta_dicts method[/dim]\n")
    
    input_msg = society.init_chat()

    for round_num in range(round_limit):
        rprint(f"[bold cyan]--- Round {round_num + 1} ---[/bold cyan]")
        
        assistant_response, user_response = society.step(input_msg)

        if is_terminated(assistant_response) or is_terminated(user_response):
            break
            
        rprint(f"[blue]👤 [Patient]:[/blue] {user_response.msg.content}\n")
        
        if "CAMEL_TASK_DONE" in user_response.msg.content:
            rprint("[green]✅ Consultation completed![/green]")
            break
            
        rprint(f"[red]👨‍⚕️ [Dr. Chen]:[/red] {assistant_response.msg.content}\n")
        input_msg = assistant_response.msg
    
    rprint("[bold yellow]📋 End of consultation[/bold yellow]")

# Run the medical consultation
run(society, round_limit=6)