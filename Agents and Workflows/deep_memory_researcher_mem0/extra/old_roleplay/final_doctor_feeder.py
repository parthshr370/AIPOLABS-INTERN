#!/usr/bin/env python3

import os
import random
import warnings
from dotenv import load_dotenv
from mem0 import MemoryClient
from rich import print as rprint

from camel.societies import RolePlaying
from camel.models import ModelFactory
from camel.types import ModelPlatformType
from camel.agents import ChatAgent
from camel.messages import BaseMessage
import json

warnings.filterwarnings("ignore", category=DeprecationWarning)
load_dotenv()

# Configuration
DOCTOR_MEMORY_ID = "doctor_memory"
mem0 = MemoryClient()
model = ModelFactory.create(
    model_platform=ModelPlatformType.GEMINI,
    model_type="gemini-2.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY"),
    model_config_dict={"temperature": 0.3, "max_tokens": 4096},
)


def create_patient_disease_combo():
    """Generate unique patient-disease combo using LLM structured output"""

    system_message = BaseMessage.make_assistant_message(
        role_name="MedicalGenerator",
        content="""Generate unique patient with realistic medical condition. Return structured output:

Patient: [Unique name], [age 25-75], [gender], [occupation]
Condition: [Medical condition], [ICD-10], [specific symptoms], [vital signs with values], [medications with dosages], [family history]

Use diverse names, realistic medical data, actual drug names with mg/mcg dosages, real BP/HR/lab values.""",
    )

    agent = ChatAgent(system_message=system_message, model=model)
    response = agent.step(
        BaseMessage.make_user_message("User", "Generate unique patient-disease data")
    )

    # raw llm output basically
    output = response.msg.content.strip()

    # unique id for patient-disease combo
    unique_id = f"patient_{random.randint(10000, 99999)}"

    return {"raw_output": output, "unique_id": unique_id}


def generate_conversation(patient_disease_combo, rounds=5):
    """Generate realistic doctor-patient conversation"""

    raw_data = patient_disease_combo["raw_output"]

    # Simple RolePlaying setup - let LLM use the raw patient data
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
                "task": f"You're Dr. Chen consulting about: {raw_data}. Talk in first person.",
            },
            {
                "assistant_role": "Dr. Sarah Chen",
                "user_role": "Patient",
                "task": f"You're the patient with: {raw_data}. Talk in first person about your symptoms.",
            },
        ],
    )

    # Generate conversation
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

        print(f"Round {i + 1}: Patient ↔ Dr. Chen")
        print(f"👤 Patient: {user_response.msg.content}")
        print(f"👨‍⚕️ Dr. Chen: {assistant_response.msg.content}")
        print()

        input_msg = assistant_response.msg

        if "CAMEL_TASK_DONE" in user_response.msg.content:
            break

    return conversations


def add_to_memory(conversations, patient_disease_combo):
    """Add conversations to mem0 with unique metadata to prevent overwriting"""

    stored = 0
    unique_id = patient_disease_combo["unique_id"]
    raw_data = patient_disease_combo["raw_output"]

    for i, convo in enumerate(conversations):
        try:
            messages = [
                {"role": "user", "content": convo["patient"]},
                {"role": "assistant", "content": convo["doctor"]},
            ]

            # Use mem0 with unique metadata for each patient case
            mem0.add(
                messages=messages,
                user_id=DOCTOR_MEMORY_ID,
                metadata={
                    "patient_id": unique_id,
                    "case_info": raw_data,
                    "conversation_round": i + 1,
                },
            )
            stored += 1
        except Exception as e:
            print(f"Error storing: {e}")

    return stored


def fill_doctor_database(n_patients=5):
    """Main function: Generate n different patient-disease combinations and feed to memory"""

    print(f"🏥 Filling doctor database with {n_patients} patients...")

    total_conversations = 0
    total_stored = 0

    for i in range(n_patients):
        print(f"\n--- Patient {i + 1}/{n_patients} ---")

        # Step 1: Create patient-disease combo
        combo = create_patient_disease_combo()
        unique_id = combo["unique_id"]
        raw_data = combo["raw_output"]

        # Extract key info from LLM output for clean display
        lines = raw_data.split("\n")
        patient_line = next(
            (line for line in lines if line.startswith("Patient:")), "Patient: Unknown"
        )
        condition_line = next(
            (line for line in lines if line.startswith("Condition:")),
            "Condition: Unknown",
        )

        print(patient_line)
        print(condition_line)

        # Step 2: Generate conversation
        conversations = generate_conversation(combo, rounds=4)

        if conversations:
            # Step 3: Add to memory
            stored = add_to_memory(conversations, combo)
            total_conversations += len(conversations)
            total_stored += stored

            print(f"✅ Generated {len(conversations)} rounds, stored {stored}")
        else:
            print("❌ No conversation generated")

    print(
        f"\n🎉 Database filled! Total: {total_conversations} conversations, {total_stored} stored"
    )


def main():
    """Simple main loop"""
    print("🩺 Doctor Database Feeder")

    while True:
        command = (
            input(
                "\nEnter number of patients to generate (or 'status'/'reset'/'exit'): "
            )
            .strip()
            .lower()
        )

        if command == "exit":
            print("Goodbye!")
            break
        elif command == "status":
            try:
                # Search across all patient memories (using wildcard approach)
                total_memories = 0
                print("📊 Checking memory status...")

                # Since we use unique patient IDs, we need to check differently
                # For now, just check the base doctor_memory
                memories = mem0.search(
                    query="Dr. Sarah Chen", user_id=DOCTOR_MEMORY_ID, limit=100
                )
                if memories:
                    total_memories += len(memories)

                print(f"📊 Memories in database: {total_memories}")
            except Exception as e:
                print(f"Error checking status: {e}")
        elif command == "reset":
            print("🗑️ Clearing all patient memories...")
            # Note: This only clears the base doctor_memory
            # Individual patient memories would need separate clearing
            mem0.delete_all(user_id=DOCTOR_MEMORY_ID)
            print("🗑️ Database cleared")
        else:
            try:
                n = int(command)
                if n > 0:
                    fill_doctor_database(n)
                else:
                    print("Please enter a positive number")
            except ValueError:
                print("Commands: [number], status, reset, exit")


if __name__ == "__main__":
    main()
