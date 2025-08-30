#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from rich import print as rprint
from camel.societies import RolePlaying
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.messages import BaseMessage

load_dotenv()

# Create Gemini model
model = ModelFactory.create(
    model_platform=ModelPlatformType.GEMINI,
    model_type="gemini-2.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY"),
    model_config_dict={"temperature": 0.0, "max_tokens": 4096},
)

# Enhanced system messages for medical consultation
doctor_sys_msg = """You are Dr. Sarah Chen, an experienced internal medicine physician conducting a thorough medical consultation.
- Ask specific questions about symptoms, duration, severity using 1-10 scales
- Provide actual medical values: "Your blood pressure is 140/90 mmHg (Stage 1 hypertension)"
- Give specific diagnoses with ICD-10 codes: "Hypertension, I10"
- Recommend actual medications with dosages: "Lisinopril 10mg once daily"
- Use real medical terminology and reference ranges, never placeholders like [medication] or [value]
- Keep responses concise but medically accurate
Example response: "Based on your symptoms and BP reading of 140/90, I'm diagnosing Stage 1 hypertension (I10). I'm prescribing Lisinopril 10mg daily."
"""

patient_sys_msg = """You are Alex Thompson, a 45-year-old office worker with health concerns.
- Provide specific symptom details: "Chest pain started 3 days ago, rates 7/10 severity, occurs after climbing stairs"
- Mention actual medications: "I take Metformin 500mg twice daily for diabetes"
- Share realistic vital signs: "My resting heart rate is usually 78 bps, weight 180 lbs"
- Include relevant family history: "My father had heart disease at age 60"
- Express genuine concerns but don't self-diagnose
- Be honest about lifestyle factors: "I smoke half a pack daily, drink 2-3 beers on weekends"
"""

# Set up kwargs for medical consultation
task_kwargs = {
    "task_prompt": "Conduct a comprehensive medical consultation for diagnosis and treatment planning.",
    "with_task_specify": False,  # Disable to avoid overriding our detailed system messages
}

user_role_kwargs = {
    "user_role_name": "Patient",
    "user_agent_kwargs": {
        "model": model,
        "system_message": patient_sys_msg
    },
}

assistant_role_kwargs = {
    "assistant_role_name": "Doctor", 
    "assistant_agent_kwargs": {
        "model": model,
        "system_message": doctor_sys_msg
    },
}

# This encapsulates all the keyword arguments.
society = RolePlaying(**task_kwargs, **user_role_kwargs, **assistant_role_kwargs)


def is_terminated(response):
    """
    Alert when the session should be terminated.
    """
    if response.terminated:
        role = response.msg.role_type.name
        reason = response.info["termination_reasons"]
        print(f"AI {role} terminated due to {reason}")
    return response.terminated


def run(society, round_limit: int = 6):
    rprint("[bold green]🏥 Medical Consultation Session Started[/bold green]")
    rprint("[dim]Dr. Sarah Chen consulting with patient Alex Thompson[/dim]\n")
    
    input_msg = society.init_chat()

    # Starting the medical consultation
    for round_num in range(round_limit):
        rprint(f"[bold cyan]--- Consultation Round {round_num + 1} ---[/bold cyan]")
        
        # Let the doctor and patient interact
        assistant_response, user_response = society.step(input_msg)

        # If termination is prompted, break out
        if is_terminated(assistant_response) or is_terminated(user_response):
            break
            
        # Display patient response
        rprint(f"[blue]👤 [Patient]:[/blue] {user_response.msg.content}\n")
        
        if "CAMEL_TASK_DONE" in user_response.msg.content:
            rprint("[green]✅ Consultation completed![/green]")
            break
            
        # Display doctor response
        rprint(f"[red]👨‍⚕️ [Dr. Chen]:[/red] {assistant_response.msg.content}\n")
        
        # Set up the next input message for the next round
        input_msg = assistant_response.msg
    
    rprint("[bold yellow]📋 End of medical consultation session[/bold yellow]")
    return None


# Run the medical consultation
run(society, round_limit=6)
