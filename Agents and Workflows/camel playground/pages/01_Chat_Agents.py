import streamlit as st
import os
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.types import ModelType, ModelPlatformType
from camel.models import ModelFactory
from camel.configs import ChatGPTConfig, AnthropicConfig, GeminiConfig
import plotly.graph_objects as go
from datetime import datetime
import json
from pathlib import Path
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure the page
st.set_page_config(
    page_title="CAMEL AI - Chat Agents",
    page_icon="💬",
    layout="wide"
)

# Enhanced Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 1rem 2rem;
    }
    .chat-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        max-height: 600px;
        overflow-y: auto;
        border: 1px solid #e1e5e9;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .message {
        padding: 1rem;
        margin: 0.75rem 0;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        animation: fadeIn 0.3s ease-in;
    }
    .agent-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 1rem;
        margin-right: 3rem;
    }
    .user-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        margin-left: 3rem;
        margin-right: 1rem;
    }
    .agent-config {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .status-indicator {
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 600;
        text-align: center;
        margin: 0.5rem 0;
    }
    .status-ready {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        color: white;
    }
    .status-not-ready {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: white;
    }
    .stButton>button {
        width: 100%;
        height: 3rem;
        font-size: 16px;
        font-weight: 600;
        border-radius: 10px;
        border: none;
        transition: all 0.3s ease;
        margin: 0.5rem 0;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .header-stats {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .compact-title {
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'selected_provider' not in st.session_state:
        st.session_state.selected_provider = "OpenAI"
    if 'custom_model_name' not in st.session_state:
        st.session_state.custom_model_name = "gpt-4o-mini" 
    if 'last_agent_raw_output' not in st.session_state:
        st.session_state.last_agent_raw_output = None

def create_agent(provider_name: str, model_name: str, role: str, role_description: str, agent_identifier: str = "Agent"): 
    model_instance = None
    model_name = model_name.strip()

    logging.info(f"Attempting to create {agent_identifier}: Provider='{provider_name}', Model='{model_name}', Role='{role}'")

    if not provider_name:
        st.error(f"Provider name for {agent_identifier} cannot be empty.")
        logging.error(f"Validation failed for {agent_identifier}: Provider name empty.")
        return None
    if not model_name:
        st.error(f"Model name for {agent_identifier} cannot be empty.")
        logging.error(f"Validation failed for {agent_identifier}: Model name empty (Provider: {provider_name}).")
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
            logging.error(f"Invalid provider for {agent_identifier}: '{provider_name}'")
            return None

        if model_instance is None:
             st.error(f"Failed to create model instance for {agent_identifier} with provider '{provider_name}' and model '{model_name}'. Check model name & API key.")
             logging.error(f"ModelFactory.create returned None for {agent_identifier}. Provider='{provider_name}', Model='{model_name}'")
             return None
        
        logging.info(f"Model instance created successfully for {agent_identifier}. Now creating ChatAgent.")
        
        # Create system message using the latest API
        system_message = BaseMessage.make_assistant_message(
            role_name=role,
            content=f"You are a {role}. {role_description}"
        )
        
        agent = ChatAgent(system_message=system_message, model=model_instance)
        logging.info(f"ChatAgent (type: {type(agent)}) created for {agent_identifier}.")
        return agent
        
    except Exception as e:
        st.error(f"Error creating {agent_identifier} (Provider: {provider_name}, Model: {model_name}): {str(e)}")
        logging.error(f"Exception during {agent_identifier} creation: {str(e)}. Provider='{provider_name}', Model='{model_name}'", exc_info=True)
        return None

def save_conversation(messages, role, provider, model_name_val):
    save_dir = Path("conversation_history")
    save_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = save_dir / f"conversation_{timestamp}.json"
    conversation_data = {
        "timestamp": timestamp, "role": role,
        "provider": provider, "model_name": model_name_val,
        "messages": messages
    }
    with open(filename, 'w') as f: json.dump(conversation_data, f, indent=2)

def main():
    initialize_session_state()
    
    # Enhanced header with back button
    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("🏠 Home"):
            st.switch_page("Home.py")
    with col2:
        st.markdown('<h1 class="compact-title">💬 Chat Agents</h1>', unsafe_allow_html=True)
    
    st.markdown("Create and interact with CAMEL AI agents using custom roles and personalities")
    
    # Agent status indicator
    if st.session_state.agent:
        st.markdown('<div class="status-indicator status-ready">🤖 Agent Ready - Start Chatting!</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-indicator status-not-ready">⚙️ Configure your agent in the sidebar first</div>', unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### 🛠️ Agent Configuration")
        
        # Provider selection with better styling
        available_providers = []
        if os.getenv("OPENAI_API_KEY"): available_providers.append("OpenAI")
        if os.getenv("ANTHROPIC_API_KEY"): available_providers.append("Anthropic")
        if os.getenv("GEMINI_API_KEY"): available_providers.append("Gemini")
        if os.getenv("OPENROUTER_API_KEY"): available_providers.append("OpenRouter")
        
        if not available_providers:
            available_providers = ["(Set API Keys on Home Page)"]
        
        if st.session_state.selected_provider not in available_providers and available_providers[0] != "(Set API Keys on Home Page)":
            st.session_state.selected_provider = available_providers[0]

        selected_provider = st.selectbox(
            "🔧 Select Provider",
            available_providers,
            index=available_providers.index(st.session_state.selected_provider) if st.session_state.selected_provider in available_providers else 0,
            key="selected_provider_chat_agent"
        )
        st.session_state.selected_provider = selected_provider

        # Model name input with updated defaults
        default_model_for_provider = {
            "OpenAI": "gpt-4.1-mini", 
            "Anthropic": "claude-sonnet-4-20250514",
            "Gemini": "gemini-2.5-flash-preview-05-20", 
            "OpenRouter": "google/gemini-flash-1.5"
        }
        
        if 'last_selected_provider_chat' not in st.session_state or st.session_state.last_selected_provider_chat != selected_provider:
            st.session_state.custom_model_name = default_model_for_provider.get(selected_provider, "")
        st.session_state.last_selected_provider_chat = selected_provider

        custom_model_name = st.text_input(
            f"🧠 Model Name for {selected_provider}",
            value=st.session_state.custom_model_name,
            key="model_name_chat_agent",
            help=f"E.g., {default_model_for_provider.get(selected_provider, 'specific-model-name')}"
        )
        st.session_state.custom_model_name = custom_model_name

        role = st.text_input("🎭 Agent Role", value="AI Assistant", key="role_chat_agent")
        role_description = st.text_area("📋 Role Description", value="You are a helpful assistant.", key="desc_chat_agent", height=100)
        
        if st.button("🚀 Create/Update Agent", key="create_chat_agent_btn"):
            if selected_provider == "(Set API Keys on Home Page)":
                 st.error("Please set the required API keys on the Home page to select a provider.")
            else:
                with st.spinner("Creating your agent..."):
                    st.session_state.agent = create_agent(
                        selected_provider, 
                        custom_model_name, 
                        role, role_description, 
                        "Chat Agent"
                    )
                    if st.session_state.agent:
                        st.success(f"✅ Agent created successfully!")
                        st.balloons()

        st.divider()
        
        # Conversation management
        st.markdown("### 💾 Conversation")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat", key="clear_chat_btn"):
                st.session_state.messages = []
                st.rerun()
        with col2:
            if st.button("💾 Save Chat", key="save_chat_btn"):
                if st.session_state.messages:
                    save_conversation(
                        st.session_state.messages, 
                        role, 
                        selected_provider, 
                        custom_model_name
                    )
                    st.success("Conversation saved!")
                else:
                    st.warning("No messages to save!")

    # Main chat interface
    if st.session_state.agent:
        # Chat history
        if st.session_state.messages:
            st.markdown("### 💬 Conversation")
            with st.container():
                st.markdown('<div class="chat-container">', unsafe_allow_html=True)
                for message in st.session_state.messages:
                    if message["role"] == "user":
                        st.markdown(f'<div class="message user-message"><strong>You:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="message agent-message"><strong>{role}:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        # Chat input
        user_input = st.chat_input("Type your message here...")
        
        if user_input:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Get agent response
            try:
                with st.spinner(f"{role} is thinking..."):
                    user_msg = BaseMessage.make_user_message(role_name="User", content=user_input)
                    response = st.session_state.agent.step(user_msg)
                    
                    if response and hasattr(response, 'msg') and response.msg:
                        agent_response = response.msg.content
                        st.session_state.messages.append({"role": "assistant", "content": agent_response})
                        st.session_state.last_agent_raw_output = response
                    else:
                        st.error("No valid response from agent.")
                        
            except Exception as e:
                st.error(f"Error getting response: {str(e)}")
                logging.error(f"Chat error: {str(e)}", exc_info=True)
            
            st.rerun()
    else:
        # No agent configured
        st.markdown("### 🎯 Getting Started")
        st.markdown("""
        <div class="agent-config">
        <h4>Configure Your Agent</h4>
        <p>To start chatting, you need to:</p>
        <ol>
        <li>🔧 Select a provider in the sidebar</li>
        <li>🧠 Choose a model name</li>
        <li>🎭 Define the agent's role and description</li>
        <li>🚀 Click "Create/Update Agent"</li>
        </ol>
        <p><strong>Tip:</strong> Try different roles like "Python Expert", "Creative Writer", or "Data Scientist" for specialized responses!</p>
        </div>
        """, unsafe_allow_html=True)

    # Display conversation stats
    if st.session_state.messages:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💬 Messages", len(st.session_state.messages))
        with col2:
            user_msgs = len([m for m in st.session_state.messages if m["role"] == "user"])
            st.metric("👤 Your Messages", user_msgs)
        with col3:
            agent_msgs = len([m for m in st.session_state.messages if m["role"] == "assistant"])
            st.metric("🤖 Agent Messages", agent_msgs)

if __name__ == "__main__":
    main()