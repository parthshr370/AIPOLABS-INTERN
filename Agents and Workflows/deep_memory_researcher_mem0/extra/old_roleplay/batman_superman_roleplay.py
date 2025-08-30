#!/usr/bin/env python3
"""
Simple Batman and Superman Agent Conversation using CAMEL RolePlaying
"""

import os
from getpass import getpass
from camel.societies import RolePlaying
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType

def setup_gemini_model():
    """Setup Gemini model with API key"""
    # Get Gemini API key
    if "GEMINI_API_KEY" not in os.environ:
        gemini_api_key = getpass('Enter your Gemini API key: ')
        os.environ["GEMINI_API_KEY"] = gemini_api_key
    
    # Create Gemini model
    model = ModelFactory.create(
        model_platform=ModelPlatformType.GEMINI,
        model_type=ModelType.GEMINI_1_5_FLASH,
    )
    return model

def is_terminated(response):
    """Check if the conversation should be terminated"""
    if response.terminated:
        role = response.msg.role_type.name
        reason = response.info['termination_reasons']
        print(f'AI {role} terminated due to {reason}')
    return response.terminated

def run_batman_superman_conversation(society, round_limit: int = 5):
    """Run the Batman and Superman conversation"""
    print("🦇 Batman and Superman are discussing how to protect Metropolis 🦸")
    print("=" * 60)
    
    # Initialize the conversation
    input_msg = society.init_chat()
    
    for round_num in range(round_limit):
        print(f"\n--- Round {round_num + 1} ---")
        
        # Let the agents interact
        assistant_response, user_response = society.step(input_msg)
        
        # Check for termination
        if is_terminated(assistant_response) or is_terminated(user_response):
            break
            
        # Display Batman's response (user role)
        print(f"🦇 [Batman]: {user_response.msg.content}\n")
        
        # Check if task is completed
        if 'CAMEL_TASK_DONE' in user_response.msg.content:
            print("✅ Task completed!")
            break
            
        # Display Superman's response (assistant role)  
        print(f"🦸 [Superman]: {assistant_response.msg.content}\n")
        
        # Set up next round
        input_msg = assistant_response.msg
    
    print("\n🎬 Conversation ended!")

def main():
    """Main function to run the Batman-Superman roleplay"""
    print("Setting up Batman vs Superman Agent Conversation...")
    
    # Setup model
    model = setup_gemini_model()
    
    # Task configuration
    task_kwargs = {
        'task_prompt': 'Create a plan to protect Metropolis from a new villain threat',
        'with_task_specify': True,
        'task_specify_agent_kwargs': {'model': model}
    }
    
    # Batman setup (user role - gives instructions)
    user_role_kwargs = {
        'user_role_name': 'Batman',
        'user_agent_kwargs': {'model': model}
    }
    
    # Superman setup (assistant role - provides solutions)
    assistant_role_kwargs = {
        'assistant_role_name': 'Superman', 
        'assistant_agent_kwargs': {'model': model}
    }
    
    # Create the agent society
    society = RolePlaying(
        **task_kwargs,
        **user_role_kwargs,
        **assistant_role_kwargs
    )
    
    # Print system messages
    print("\n🔧 System Messages:")
    print(f"Batman System Message: {society.user_sys_msg}")
    print(f"Superman System Message: {society.assistant_sys_msg}")
    print(f"Task Prompt: {society.task_prompt}")
    
    # Run the conversation
    run_batman_superman_conversation(society, round_limit=5)

if __name__ == "__main__":
    main()