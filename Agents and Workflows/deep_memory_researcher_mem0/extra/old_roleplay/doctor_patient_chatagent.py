#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from rich import print as rprint
from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.types import ModelPlatformType
from camel.messages import BaseMessage

load_dotenv()

model = ModelFactory.create(
    model_platform=ModelPlatformType.GEMINI,
    model_type="gemini-2.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY"),
    model_config_dict={"temperature": 0.0, "max_tokens": 4096},
)

# Method 3: Direct ChatAgent approach with BaseMessage (Most Control)
doctor_sys_msg = BaseMessage.make_assistant_message(
    role_name="Dr. Sarah Chen",
    content="""You are Dr. Sarah Chen, an experienced internal medicine physician conducting a medical consultation.
    - Ask specific questions about symptoms with severity scales (1-10)
    - Provide actual medical values: "Your blood pressure is 140/90 mmHg (Stage 1 hypertension)"
    - Give specific diagnoses with ICD-10 codes: "Hypertension, I10"
    - Recommend actual medications with dosages: "Lisinopril 10mg once daily"
    - Use real medical terminology and reference ranges, never placeholders
    - Keep responses concise but medically accurate
    """
)

patient_sys_msg = BaseMessage.make_user_message(
    role_name="Alex Thompson",
    content="""You are Alex Thompson, a 45-year-old office worker seeking medical consultation.
    - Provide specific symptom details: "Chest pain started 3 days ago, rates 7/10 severity"
    - Mention actual medications: "I take Metformin 500mg twice daily for diabetes"
    - Share realistic vital signs: "My resting heart rate is usually 78 bpm, weight 180 lbs"
    - Include relevant family history: "My father had heart disease at age 60"
    - Express genuine concerns but don't self-diagnose
    """
)

# Create ChatAgents directly with BaseMessage system messages
doctor_agent = ChatAgent(
    system_message=doctor_sys_msg,
    model=model
)

patient_agent = ChatAgent(
    system_message=patient_sys_msg,
    model=model
)

def run_manual_conversation(rounds: int = 6):
    rprint("[bold green]🏥 Medical Consultation Session Started[/bold green]")
    rprint("[dim]Using direct ChatAgent with BaseMessage approach[/dim]\n")
    
    # Initial patient message
    patient_msg = BaseMessage.make_user_message(
        role_name="Alex Thompson",
        content="Doctor, I've been having some concerning symptoms lately and wanted to get checked out."
    )
    
    for round_num in range(rounds):
        rprint(f"[bold cyan]--- Round {round_num + 1} ---[/bold cyan]")
        
        # Patient speaks first
        rprint(f"[blue]👤 [Patient]:[/blue] {patient_msg.content}\n")
        
        # Doctor responds
        doctor_response = doctor_agent.step(patient_msg)
        if doctor_response.terminated:
            rprint("[red]Doctor terminated conversation[/red]")
            break
            
        doctor_msg = doctor_response.msgs[0]
        rprint(f"[red]👨‍⚕️ [Dr. Chen]:[/red] {doctor_msg.content}\n")
        
        # Patient responds to doctor
        patient_response = patient_agent.step(doctor_msg)
        if patient_response.terminated:
            rprint("[red]Patient terminated conversation[/red]")
            break
        
        patient_msg = patient_response.msgs[0]
        
        # Check for completion
        if "CAMEL_TASK_DONE" in patient_msg.content or "consultation complete" in patient_msg.content.lower():
            rprint("[green]✅ Consultation completed![/green]")
            break
    
    rprint("[bold yellow]📋 End of consultation[/bold yellow]")

# Run the manual conversation
run_manual_conversation(rounds=6)