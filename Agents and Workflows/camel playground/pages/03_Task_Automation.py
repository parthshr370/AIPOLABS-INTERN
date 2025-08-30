import streamlit as st
import os
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.types import ModelType, ModelPlatformType
from camel.models import ModelFactory
import plotly.graph_objects as go
from datetime import datetime
import json
from pathlib import Path
import time
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure the page
st.set_page_config(
    page_title="CAMEL AI - Task Automation",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .task-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .progress-container {
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .output-container {
        background-color: #fff;
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        margin: 1rem 0;
        max-height: 400px;
        overflow-y: auto;
    }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state():
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'tasks' not in st.session_state:
        st.session_state.tasks = []
    if 'task_outputs' not in st.session_state:
        st.session_state.task_outputs = {}
    if 'task_status' not in st.session_state:
        st.session_state.task_status = {}
    if 'model_name_input' not in st.session_state:
        st.session_state.model_name_input = "gpt-3.5-turbo"

def create_agent_for_task_automation(model_name_input: str, role: str, role_description: str, agent_identifier: str = "Task Agent"):
    model_instance = None
    model_name_input_stripped = model_name_input.strip()
    
    logging.info(f"Attempting to create {agent_identifier}: Input='{model_name_input_stripped}', Role='{role}'")

    if not model_name_input_stripped:
        st.error(f"Model input for {agent_identifier} cannot be empty.")
        logging.error(f"Validation failed for {agent_identifier}: Model input empty.")
        return None
    
    platform_to_pass = None
    model_spec_to_pass = model_name_input_stripped
    api_key_env_var = None
    api_key_name_for_user = "Selected Provider"
    provider_for_logging = "Unknown"
    model_config = {"max_tokens": 4096}

    try:
        if ":" in model_name_input_stripped:
            parts = model_name_input_stripped.split(":", 1)
            provider_from_input = parts[0].lower()
            model_name_from_input = parts[1]
            provider_for_logging = provider_from_input

            if not model_name_from_input:
                st.error(f"Model name missing after prefix '{provider_from_input}:' for {agent_identifier}.")
                logging.error(f"Validation failed for {agent_identifier}: Model name missing after prefix '{provider_from_input}:' (Input: '{model_name_input_stripped}')")
                return None
            model_spec_to_pass = model_name_from_input

            if provider_from_input == "openai":
                platform_to_pass = ModelPlatformType.OPENAI
                api_key_env_var = "OPENAI_API_KEY"; api_key_name_for_user = "OpenAI"
            elif provider_from_input == "anthropic":
                platform_to_pass = ModelPlatformType.ANTHROPIC
                api_key_env_var = "ANTHROPIC_API_KEY"; api_key_name_for_user = "Anthropic"
            elif provider_from_input == "gemini":
                platform_to_pass = ModelPlatformType.GEMINI
                api_key_env_var = "GEMINI_API_KEY"; api_key_name_for_user = "Gemini"
            elif provider_from_input == "openrouter":
                platform_to_pass = ModelPlatformType.OPENROUTER
                api_key_env_var = "OPENROUTER_API_KEY"; api_key_name_for_user = "OpenRouter"
            else:
                st.error(f"Unknown provider prefix '{provider_from_input}' in '{model_name_input_stripped}' for {agent_identifier}.")
                logging.error(f"Unknown provider prefix '{provider_from_input}' for {agent_identifier} (Input: '{model_name_input_stripped}')")
                return None
        else:
            provider_for_logging = "Inferred (OpenAI/Anthropic based on model name)"
            lower_input = model_name_input_stripped.lower()
            if lower_input == "gpt-4":
                model_spec_to_pass = ModelType.GPT_4
                platform_to_pass = ModelPlatformType.OPENAI
                api_key_env_var = "OPENAI_API_KEY"; api_key_name_for_user = "OpenAI"
            elif lower_input in ["gpt-3.5-turbo", "gpt-3.5"]:
                model_spec_to_pass = ModelType.GPT_35_TURBO
                platform_to_pass = ModelPlatformType.OPENAI
                api_key_env_var = "OPENAI_API_KEY"; api_key_name_for_user = "OpenAI"
            elif lower_input == "claude-2":
                model_spec_to_pass = ModelType.CLAUDE_2
                platform_to_pass = ModelPlatformType.ANTHROPIC
                api_key_env_var = "ANTHROPIC_API_KEY"; api_key_name_for_user = "Anthropic"
            else:
                st.error(f"Unknown model '{model_name_input_stripped}' for {agent_identifier}. No provider prefix found, and not a known short name (e.g., gpt-4, claude-2). Use format 'provider:model_name' like 'openrouter:google/gemini-flash-1.5'.")
                logging.error(f"Cannot infer provider for {agent_identifier} from model '{model_name_input_stripped}'. Needs prefix or known short name.")
                return None
            
        api_key_present = bool(os.getenv(api_key_env_var))
        logging.info(f"{agent_identifier} - Parsed Provider: {provider_for_logging}, Platform to pass: {platform_to_pass}, Model spec: {model_spec_to_pass}, API Key ({api_key_env_var}) Present: {api_key_present}, Model Config: {model_config}")

        if api_key_env_var and not api_key_present:
            st.error(f"{api_key_name_for_user} API Key not set for {agent_identifier}. Configure on Home page.")
            logging.error(f"{api_key_name_for_user} API Key not set for {agent_identifier} (Env Var: {api_key_env_var})")
            return None

        logging.info(f"Calling ModelFactory.create for {agent_identifier} with platform='{platform_to_pass}', type='{model_spec_to_pass}' (is ModelType: {isinstance(model_spec_to_pass, ModelType)}), config='{model_config}'")
        if platform_to_pass and not isinstance(model_spec_to_pass, ModelType):
            model_instance = ModelFactory.create(model_platform=platform_to_pass, model_type=model_spec_to_pass, api_key=os.getenv(api_key_env_var), model_config_dict=model_config)
        elif isinstance(model_spec_to_pass, ModelType):
            model_instance = ModelFactory.create(model_type=model_spec_to_pass, api_key=os.getenv(api_key_env_var), model_config_dict=model_config)
        else:
            st.error(f"Could not determine how to create model for {agent_identifier} with input '{model_name_input_stripped}'. Ambiguous configuration.")
            logging.error(f"Ambiguous model creation for {agent_identifier}: input='{model_name_input_stripped}', platform_to_pass='{platform_to_pass}', model_spec='{model_spec_to_pass}'")
            return None

        if model_instance is None:
            st.error(f"Failed to create model for {agent_identifier} with input \'{model_name_input_stripped}\'. Check format/name & API keys. See logs.")
            logging.error(f"ModelFactory.create returned None for {agent_identifier}. Input='{model_name_input_stripped}', Platform='{platform_to_pass}', ModelSpec='{model_spec_to_pass}'")
            return None
        
        logging.info(f"Model instance created successfully for {agent_identifier}. Now creating ChatAgent.")
        agent = ChatAgent(system_message=f"You are a {role}. {role_description}", model=model_instance)
        logging.info(f"ChatAgent (type: {type(agent)}) created for {agent_identifier}.")
        return agent

    except ValueError as ve:
        st.error(f"Configuration error creating {agent_identifier} with input '{model_name_input_stripped}': {str(ve)}. Check format and names. See logs.")
        logging.error(f"ValueError during {agent_identifier} creation: {str(ve)}. Input='{model_name_input_stripped}', Platform='{platform_to_pass}', ModelSpec='{model_spec_to_pass}'", exc_info=True)
        return None
    except Exception as e:
        st.error(f"Unexpected error creating {agent_identifier} with input '{model_name_input_stripped}': {str(e)}. See logs for details.")
        logging.error(f"Unexpected exception during {agent_identifier} creation: {str(e)}. Input='{model_name_input_stripped}', Platform='{platform_to_pass}', ModelSpec='{model_spec_to_pass}'", exc_info=True)
        return None

def save_task_results(tasks, outputs, status, model_name_input_val):
    save_dir = Path("task_history")
    save_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = save_dir / f"tasks_{timestamp}.json"
    task_data = {
        "timestamp": timestamp,
        "model_name_input": model_name_input_val,
        "tasks": tasks,
        "outputs": outputs,
        "status": status
    }
    with open(filename, 'w') as f:
        json.dump(task_data, f, indent=2)

def main():
    initialize_session_state()
    st.title("🎯 Task Automation")
    st.markdown("""
    Set up automated tasks for CAMEL AI agents. Define a sequence of tasks and let the agent
    work through them autonomously.
    """)
    
    with st.sidebar:
        st.header("Agent Configuration")
        model_name_input_val = st.text_input(
            "Enter Model Name",
            value=st.session_state.model_name_input,
            key="task_agent_model_name_input",
            help="Examples: 'gpt-4', 'gemini:gemini-pro'"
        )
        st.session_state.model_name_input = model_name_input_val
        role = st.text_input("Agent Role", value="Task Executor", key="task_agent_role_input")
        role_description = st.text_area("Role Description", value="You are an efficient task executor capable of breaking down and completing complex tasks.", key="task_agent_role_desc_input")
        
        if st.button("Create/Update Agent"):
            st.session_state.agent = create_agent_for_task_automation(
                st.session_state.model_name_input, 
                role, 
                role_description, 
                "Task Automation Agent"
            )
            if st.session_state.agent:
                st.success(f"Agent ({st.session_state.model_name_input}) created successfully as a {role}!")
            else:
                st.error("Agent creation failed. Check model name and API keys.")
        
        st.divider()
        if st.button("Save Results"):
            if st.session_state.tasks:
                save_task_results(
                    st.session_state.tasks, st.session_state.task_outputs,
                    st.session_state.task_status, st.session_state.model_name_input
                )
                st.success("Task results saved!")
            else: st.warning("No tasks to save!")
        
        if st.button("Clear All"):
            st.session_state.tasks = []
            st.session_state.task_outputs = {}
            st.session_state.task_status = {}
            st.success("All tasks cleared!")
    
    if st.session_state.agent is None:
        st.warning("Please create an agent using the sidebar configuration first!")
        return
    
    with st.expander("Add New Task", expanded=True):
        new_task_description = st.text_area("Task Description", key="new_task_desc_input")
        if st.button("Add Task"):
            if new_task_description:
                st.session_state.tasks.append(new_task_description)
                st.session_state.task_status[new_task_description] = "pending"
                st.success("Task added successfully!")
                st.rerun() 
            else:
                st.error("Please enter a task description!")
    
    if st.session_state.tasks:
        st.subheader("Tasks Overview")
        for task_item in list(st.session_state.tasks): 
            with st.container():
                col1, col2, col3 = st.columns([3,1,1])
                with col1: st.markdown(f"**Task:** {task_item}")
                with col2:
                    status = st.session_state.task_status.get(task_item, "pending")
                    if status == "pending": st.warning("Pending")
                    elif status == "in_progress": st.info("In Progress")
                    elif status == "completed": st.success("Completed")
                    else: st.error(f"Failed ({status})") 
                with col3:
                    if status == "pending":
                        if st.button("Execute", key=f"exec_task_{task_item}"):
                            task_input_content = f"Please complete this task: {task_item}"
                            logging.info(f"Executing task: '{task_item}'. Agent input: '{task_input_content}'")
                            try:
                                st.session_state.task_status[task_item] = "in_progress"
                                st.rerun()
                                
                                logging.info(f"Sending message to agent (type: {type(st.session_state.agent)}). Content: '{task_input_content}'")
                                user_message = BaseMessage.make_user_message(role_name="User", content=task_input_content)
                                logging.info(f"Prepared BaseMessage for task: {user_message}")

                                agent_response = st.session_state.agent.step(user_message)
                                logging.info(f"Raw agent response for task '{task_item}': {agent_response}")
                                
                                if agent_response and agent_response.msgs:
                                    response_content = agent_response.msgs[0].content
                                    logging.info(f"Extracted response content for task '{task_item}': '{response_content}'")
                                    st.session_state.task_outputs[task_item] = response_content
                                    st.session_state.task_status[task_item] = "completed"
                                elif agent_response and not agent_response.msgs:
                                    logging.warning(f"Agent response for task '{task_item}' received, but no messages.")
                                    st.session_state.task_outputs[task_item] = "Agent processed task but returned no message content."
                                    st.session_state.task_status[task_item] = "completed_no_output"
                                else:
                                    logging.warning(f"Agent did not return a valid response for task '{task_item}'.")
                                    st.session_state.task_outputs[task_item] = "Agent did not provide a response."
                                    st.session_state.task_status[task_item] = "error_no_response"
                                
                                st.rerun()
                            except AttributeError as ae:
                                error_msg = f"Method not found on agent: {str(ae)}. Task: '{task_item}'"
                                st.error(error_msg)
                                logging.error(f"AttributeError for task '{task_item}': {str(ae)}. Agent type: {type(st.session_state.agent)}", exc_info=True)
                                st.session_state.task_status[task_item] = "error_attribute"
                                st.session_state.task_outputs[task_item] = error_msg
                                st.rerun()
                            except Exception as e:
                                error_msg = f"Error executing task '{task_item[:30]}...': {str(e)}"
                                st.error(error_msg)
                                logging.error(f"Exception executing task '{task_item}': {str(e)}. Agent type: {type(st.session_state.agent)}", exc_info=True)
                                st.session_state.task_status[task_item] = "error_execution"
                                st.session_state.task_outputs[task_item] = error_msg
                                st.rerun()

        if st.session_state.task_outputs:
            st.subheader("Task Outputs")
            for task_key, output in st.session_state.task_outputs.items(): 
                with st.expander(f"Output for: {task_key[:50]}..."):
                    st.markdown(output)
        
        st.subheader("Task Statistics")
        total_tasks = len(st.session_state.tasks)
        completed_tasks = list(st.session_state.task_status.values()).count("completed")
        failed_tasks = sum(1 for s in st.session_state.task_status.values() if s not in ["pending", "in_progress", "completed"])
        pending_tasks = list(st.session_state.task_status.values()).count("pending")
        in_progress_tasks = list(st.session_state.task_status.values()).count("in_progress")

        stat_cols = st.columns(5)
        stat_cols[0].metric("Total", total_tasks)
        stat_cols[1].metric("Completed", completed_tasks)
        stat_cols[2].metric("Pending", pending_tasks)
        stat_cols[3].metric("In Progress", in_progress_tasks)
        stat_cols[4].metric("Failed/Error", failed_tasks)
        
        if total_tasks > 0:
            fig = go.Figure(data=[
                go.Bar(
                    x=['Completed', 'Pending', 'In Progress', 'Failed/Error'],
                    y=[completed_tasks, pending_tasks, in_progress_tasks, failed_tasks],
                    marker_color=['#00cc96', '#636efa', '#ffa15a', '#ef553b']
                )
            ])
            fig.update_layout(
                title="Task Status Distribution",
                xaxis_title="Status",
                yaxis_title="Number of Tasks"
            )
            st.plotly_chart(fig)

if __name__ == "__main__":
    main()