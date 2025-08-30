import streamlit as st
import os
from camel.societies import RolePlaying
from camel.messages import BaseMessage
from camel.types import ModelType, TaskType, ModelPlatformType
from camel.models import ModelFactory
from camel.configs import ChatGPTConfig, AnthropicConfig, GeminiConfig
from datetime import datetime
import json
from pathlib import Path
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure the page
st.set_page_config(
    page_title="CAMEL AI - Role Playing",
    page_icon="🎭",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .chat-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        max-height: 500px;
        overflow-y: auto;
    }
    .message {
        padding: 0.5rem;
        margin: 0.5rem;
        border-radius: 0.3rem;
    }
    .assistant-message {
        background-color: #e3f2fd;
        margin-left: 2rem;
    }
    .user-message {
        background-color: #f5f5f5;
        margin-right: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state_role_playing():
    if 'role_playing_session' not in st.session_state:
        st.session_state.role_playing_session = None
    if 'role_playing_messages' not in st.session_state:
        st.session_state.role_playing_messages = []
    if 'role_playing_conversation_history' not in st.session_state:
        st.session_state.role_playing_conversation_history = []
    # For provider dropdown and model name text input
    if 'rp_selected_provider' not in st.session_state:
        st.session_state.rp_selected_provider = "OpenAI"
    if 'rp_custom_model_name' not in st.session_state:
        st.session_state.rp_custom_model_name = "gpt-4o-mini"

def create_model_instance(provider_name: str, model_name: str, agent_identifier: str = "Agent"):
    """Create a model instance for role playing."""
    model_name = model_name.strip()

    logging.info(f"Attempting to create model for {agent_identifier} in Role Playing: Provider='{provider_name}', Model='{model_name}'")

    if not provider_name:
        st.error(f"Provider name for {agent_identifier} cannot be empty.")
        return None
    if not model_name:
        st.error(f"Model name for {agent_identifier} cannot be empty.")
        return None

    try:
        provider_lower = provider_name.lower()
        api_key = None
        model_config_dict = {"max_tokens": 4096, "temperature": 0.7}
        
        if provider_lower == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                st.error(f"OpenAI API Key not set for {agent_identifier}. Configure on Home page.")
                return None
            
            # Use the latest model types and names
            if model_name.lower() in ["gpt-4o", "gpt-4o-mini"]:
                model_type = model_name.lower()
            elif model_name.lower() in ["gpt-4.1", "gpt-4.1-mini"]:
                model_type = model_name.lower()
            elif model_name.lower() in ["o3", "o4-mini"]:
                model_type = model_name.lower()
            elif model_name.lower() == "gpt-4":
                model_type = ModelType.GPT_4
            elif model_name.lower() in ["gpt-3.5-turbo", "gpt-3.5"]:
                model_type = ModelType.GPT_3_5_TURBO
            else:
                model_type = model_name  # Use as string for newer models
            
            model_instance = ModelFactory.create(
                model_platform=ModelPlatformType.OPENAI,
                model_type=model_type,
                model_config_dict=ChatGPTConfig(**model_config_dict).as_dict(),
                api_key=api_key
            )
            
        elif provider_lower == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                st.error(f"Anthropic API Key not set for {agent_identifier}. Configure on Home page.")
                return None
            
            # Use the latest Claude models with specific version names
            if model_name.lower() in ["claude-opus-4-20250514", "claude-opus-4"]:
                model_type = model_name
            elif model_name.lower() in ["claude-sonnet-4-20250514", "claude-sonnet-4"]:
                model_type = model_name
            elif model_name.lower() in ["claude-3-7-sonnet-20250219", "claude-3-7-sonnet"]:
                model_type = model_name
            elif model_name.lower() in ["claude-3-5-haiku-20241022", "claude-3-5-haiku-latest"]:
                model_type = model_name
            elif model_name.lower() in ["claude-3-5-sonnet-latest", "claude-3-5-sonnet"]:
                model_type = ModelType.CLAUDE_3_5_SONNET
            elif model_name.lower() in ["claude-3-5-haiku-latest", "claude-3-5-haiku"]:
                model_type = ModelType.CLAUDE_3_5_HAIKU
            elif model_name.lower() == "claude-2":
                model_type = ModelType.CLAUDE_2_1
            else:
                model_type = model_name  # Use as string for newer models
            
            model_instance = ModelFactory.create(
                model_platform=ModelPlatformType.ANTHROPIC,
                model_type=model_type,
                model_config_dict=AnthropicConfig(**model_config_dict).as_dict(),
                api_key=api_key
            )
            
        elif provider_lower == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                st.error(f"Gemini API Key not set for {agent_identifier}. Configure on Home page.")
                return None
            
            # Use the latest Gemini models with specific version names
            if model_name.lower() in ["gemini-2.5-pro-preview-05-06", "gemini-2.5-pro"]:
                model_type = model_name
            elif model_name.lower() in ["gemini-2.5-flash-preview-05-20", "gemini-2.5-flash"]:
                model_type = model_name
            elif model_name.lower() in ["gemini-2.0-flash", "gemini-2-0-flash"]:
                model_type = ModelType.GEMINI_2_0_FLASH
            elif model_name.lower() in ["gemini-1.5-pro", "gemini-1-5-pro"]:
                model_type = ModelType.GEMINI_1_5_PRO
            elif model_name.lower() in ["gemini-1.5-flash", "gemini-1-5-flash"]:
                model_type = ModelType.GEMINI_1_5_FLASH
            else:
                model_type = model_name  # Use as string for newer models
            
            model_instance = ModelFactory.create(
                model_platform=ModelPlatformType.GEMINI,
                model_type=model_type,
                model_config_dict=GeminiConfig(**model_config_dict).as_dict(),
                api_key=api_key
            )
            
        elif provider_lower == "openrouter":
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                st.error(f"OpenRouter API Key not set for {agent_identifier}. Configure on Home page.")
                return None
            
            model_instance = ModelFactory.create(
                model_platform=ModelPlatformType.OPENROUTER,
                model_type=model_name,
                model_config_dict=model_config_dict,
                api_key=api_key
            )
        else:
            st.error(f"Invalid provider selected: {provider_name} for {agent_identifier}.")
            return None

        if model_instance is None:
             st.error(f"Failed to create model instance for {agent_identifier} with provider '{provider_name}' and model '{model_name}'. Check model name & API key.")
             return None
        
        logging.info(f"Model instance created successfully for {agent_identifier} in Role Playing.")
        return model_instance
        
    except Exception as e:
        st.error(f"Error creating model for {agent_identifier} (Provider: {provider_name}, Model: {model_name}): {str(e)}")
        logging.error(f"Exception during model creation for {agent_identifier} in Role Playing: {str(e)}", exc_info=True)
        return None

def save_conversation_role_playing(messages, ai_role, user_role, task_prompt, provider, model_name_val):
    save_dir = Path("role_play_history")
    save_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = save_dir / f"role_playing_{timestamp}.json"
    conversation_data = {
        "timestamp": timestamp,
        "ai_role": ai_role, "user_role": user_role, "task_prompt": task_prompt,
        "provider": provider, "model_name": model_name_val,
        "messages": messages
    }
    with open(filename, 'w') as f: json.dump(conversation_data, f, indent=2)


def main():
    initialize_session_state_role_playing()
    
    # Enhanced header with back button
    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("🏠 Home"):
            st.switch_page("Home.py")
    with col2:
        st.title("🎭 CAMEL AI Role Playing")
    
    st.markdown("Simulate conversations between two AI agents playing different roles.")

    with st.sidebar:
        st.header("Scenario Configuration")

        # Provider selection with better styling
        available_providers = []
        if os.getenv("OPENAI_API_KEY"): available_providers.append("OpenAI")
        if os.getenv("ANTHROPIC_API_KEY"): available_providers.append("Anthropic")
        if os.getenv("GEMINI_API_KEY"): available_providers.append("Gemini")
        if os.getenv("OPENROUTER_API_KEY"): available_providers.append("OpenRouter")
        
        if not available_providers:
            available_providers = ["(Set API Keys on Home Page)"]

        if st.session_state.rp_selected_provider not in available_providers and available_providers[0] != "(Set API Keys on Home Page)":
            st.session_state.rp_selected_provider = available_providers[0]
        
        selected_provider = st.selectbox(
            "Select Provider",
            available_providers,
            index=available_providers.index(st.session_state.rp_selected_provider) if st.session_state.rp_selected_provider in available_providers else 0,
            key="rp_selected_provider_dropdown" 
        )
        st.session_state.rp_selected_provider = selected_provider

        # Model name input with updated defaults
        default_model_for_provider = {
            "OpenAI": "gpt-4.1-mini", 
            "Anthropic": "claude-sonnet-4-20250514",
            "Gemini": "gemini-2.5-flash-preview-05-20", 
            "OpenRouter": "google/gemini-flash-1.5"
        }
        
        if 'rp_last_selected_provider' not in st.session_state or st.session_state.rp_last_selected_provider != selected_provider:
            st.session_state.rp_custom_model_name = default_model_for_provider.get(selected_provider, "")
        st.session_state.rp_last_selected_provider = selected_provider
        
        custom_model_name = st.text_input(
            f"Enter Model Name for {selected_provider}",
            value=st.session_state.rp_custom_model_name,
            key="rp_model_name_input",
            help=f"E.g., {default_model_for_provider.get(selected_provider, 'specific-model-name')}"
        )
        st.session_state.rp_custom_model_name = custom_model_name

        ai_role_name = st.text_input("AI Assistant Role Name", value="Python Programmer", key="rp_ai_role")
        ai_role_description = st.text_area("AI Assistant Role Description", value="You are a Python programmer that can write Python code.", key="rp_ai_desc")
        
        user_role_name = st.text_input("User Proxy Role Name", value="Stock Trader", key="rp_user_role")
        user_role_description = st.text_area("User Proxy Role Description", value="You are a stock trader that is interested in the stock market.", key="rp_user_desc")

        task_prompt_template = "Develop a trading bot for the stock market"
        task_prompt = st.text_area("Task Prompt", value=task_prompt_template, height=100, key="rp_task_prompt")

        word_limit = st.slider("Word Limit for Responses", 50, 500, 150, key="rp_word_limit")

        if st.button("Start Role Playing Session", key="rp_start_btn"):
            if selected_provider == "(Set API Keys on Home Page)":
                 st.error("Please set the required API keys on the Home page to select a provider.")
            elif not custom_model_name.strip():
                st.error("Model name cannot be empty.")
            else:
                # Create the model instance first
                common_model = create_model_instance(
                    selected_provider, 
                    custom_model_name, 
                    "Shared Model" 
                )

                if common_model:
                    try:
                        st.session_state.role_playing_session = RolePlaying(
                            assistant_role_name=ai_role_name,
                            assistant_agent_kwargs=dict(model=common_model),
                            user_role_name=user_role_name,
                            user_agent_kwargs=dict(model=common_model),
                            task_prompt=task_prompt,
                            with_task_specify=True,
                            task_specify_agent_kwargs=dict(model=common_model),
                            task_type=TaskType.CODE, # or other types
                            word_limit=word_limit 
                        )
                        st.session_state.role_playing_messages = []
                        st.session_state.role_playing_conversation_history = []
                        st.success(f"Role playing session started with {selected_provider}: {custom_model_name}!")
                    except Exception as e:
                        st.error(f"Error initializing RolePlaying session: {str(e)}")
                        st.session_state.role_playing_session = None
                else:
                    st.error("Failed to create model for Role Playing. Check provider, model name, and API keys.")
        
        st.divider()
        if st.button("Save Conversation", key="rp_save_convo_btn"):
            if st.session_state.role_playing_conversation_history:
                save_conversation_role_playing(
                    st.session_state.role_playing_conversation_history,
                    ai_role_name, user_role_name, task_prompt,
                    selected_provider, custom_model_name
                )
                st.success("Role Playing Conversation saved!")
            else:
                st.warning("No conversation to save.")

        if st.button("Clear Conversation", key="rp_clear_convo_btn"):
            st.session_state.role_playing_messages = []
            st.session_state.role_playing_conversation_history = []
            st.success("Role Playing Conversation cleared!")


    if st.session_state.role_playing_session is None:
        st.info("Configure the scenario and start the role playing session using the sidebar.")
        return

    chat_container = st.container()
    with chat_container:
        for msg_idx, msg_data in enumerate(st.session_state.role_playing_messages):
            role = msg_data['role']
            content = msg_data['content']
            if role == "user":
                st.markdown(f'''<div class="message user-message"><b>{st.session_state.role_playing_session.user_role_name}</b>: {content}</div>''', 
                            unsafe_allow_html=True)
            else: # assistant
                st.markdown(f'''<div class="message assistant-message"><b>{st.session_state.role_playing_session.assistant_role_name}</b>: {content}</div>''', 
                            unsafe_allow_html=True)

    user_input = st.chat_input("Your message to the AI assistant...", key="rp_user_input")

    if user_input:
        st.session_state.role_playing_messages.append({"role": "user", "content": user_input})
        st.session_state.role_playing_conversation_history.append({"role": st.session_state.role_playing_session.user_role_name, "content": user_input})
        
        try:
            assistant_response_message, _ = st.session_state.role_playing_session.step(
                BaseMessage.make_user_message(
                    role_name=st.session_state.role_playing_session.user_role_name,
                    content=user_input
                )
            )
            if assistant_response_message:
                assistant_response_content = assistant_response_message.content
                st.session_state.role_playing_messages.append({"role": "assistant", "content": assistant_response_content})
                st.session_state.role_playing_conversation_history.append({"role": st.session_state.role_playing_session.assistant_role_name, "content": assistant_response_content})
            else:
                st.warning("Assistant did not provide a response.")
            st.rerun()
        except Exception as e:
            st.error(f"Error during role playing step: {str(e)}")

if __name__ == "__main__":
    main()