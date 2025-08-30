import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="CAMEL AI Playground",
    page_icon="🐫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 1rem 2rem;
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
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    .feature-card h4 {
        margin: 0 0 0.5rem 0;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .feature-card p {
        margin: 0;
        opacity: 0.9;
        font-size: 0.95rem;
    }
    .chat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .role-card { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    .task-card { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    .viz-card { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
    
    .compact-title {
        margin-bottom: 0.5rem;
        padding-bottom: 0;
    }
    .compact-subtitle {
        margin-top: 0;
        margin-bottom: 1rem;
        color: #666;
        font-size: 1.1rem;
    }
    .quick-start {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .api-status {
        font-size: 0.9rem;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
    }
    .header-stats {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    # Compact header
    st.markdown('<h1 class="compact-title">🐫 CAMEL AI Playground</h1>', unsafe_allow_html=True)
    st.markdown('<p class="compact-subtitle">Experiment with autonomous and communicative AI agents</p>', unsafe_allow_html=True)

    # Sidebar configuration (keeping the existing API key management)
    st.sidebar.title("⚙️ Configuration")
    
    # API Key Management
    with st.sidebar.expander("🔑 API Key Management", expanded=True):
        # Define providers and their corresponding environment variable names
        providers = {
            "OpenAI": "OPENAI_API_KEY",
            "Anthropic": "ANTHROPIC_API_KEY",
            "Gemini": "GEMINI_API_KEY",
            "OpenRouter": "OPENROUTER_API_KEY"
        }
        provider_names = list(providers.keys())

        # Helper to get index of primary provider or default to 0
        def get_primary_provider_index():
            primary_provider_name = os.getenv("PRIMARY_CAMEL_PROVIDER")
            if primary_provider_name:
                try:
                    return provider_names.index(primary_provider_name.replace("_API_KEY","").replace("_"," ").title().replace("Ai","AI").replace("Api","API"))
                except ValueError:
                    # If PRIMARY_CAMEL_PROVIDER is set to a value not in our list (e.g. "OPENAI"), try to match it.
                    # This is a bit of a heuristic and might need refinement based on actual env var values.
                    for i, name in enumerate(provider_names):
                        if primary_provider_name.startswith(name.upper()):
                            return i
            return 0

        if 'selected_provider_index' not in st.session_state:
            st.session_state.selected_provider_index = get_primary_provider_index()

        selected_provider_name = st.selectbox(
            "Select API Provider",
            provider_names,
            index=st.session_state.selected_provider_index,
            key="selected_api_provider_selectbox"
        )
        
        # Update session state if selectbox changes
        if provider_names[st.session_state.selected_provider_index] != selected_provider_name:
            st.session_state.selected_provider_index = provider_names.index(selected_provider_name)

        selected_env_var_name = providers[selected_provider_name]
        
        current_api_key = st.text_input(
            f"{selected_provider_name} API Key",
            type="password",
            value=os.getenv(selected_env_var_name, ""),
            key=f"{selected_provider_name.lower()}_api_key_input",
            help=f"Enter your {selected_provider_name} API key"
        )
        
        if st.button(f"💾 Save {selected_provider_name} Key"):
            env_path = Path('.env')
            
            existing_env = {}
            if env_path.exists():
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if '=' in line:
                            key, value = line.split('=', 1)
                            # Preserve quotes if they exist, otherwise handle normally
                            if value.startswith('"') and value.endswith('"'):
                                existing_env[key] = value[1:-1]
                            elif value.startswith("'") and value.endswith("'"):
                                existing_env[key] = value[1:-1]
                            else:
                                existing_env[key] = value

            # Update the specific key for the selected provider
            if current_api_key:
                existing_env[selected_env_var_name] = current_api_key
            elif selected_env_var_name in existing_env: # Allow clearing the key
                 del existing_env[selected_env_var_name]

            # Set the primary provider
            existing_env["PRIMARY_CAMEL_PROVIDER"] = selected_provider_name.upper().replace(" ", "_")

            # Reconstruct .env content
            env_content = ""
            if "PRIMARY_CAMEL_PROVIDER" in existing_env:
                 env_content += f'PRIMARY_CAMEL_PROVIDER="{existing_env["PRIMARY_CAMEL_PROVIDER"]}"\n'
            
            for p_name, env_var in providers.items():
                if env_var in existing_env:
                    env_content += f'{env_var}="{existing_env[env_var]}"\n'
            
            # Add any other keys
            other_known_vars = list(providers.values()) + ["PRIMARY_CAMEL_PROVIDER"]
            for key, value in existing_env.items():
                if key not in other_known_vars:
                    env_content += f'{key}="{value}"\n'

            env_path.write_text(env_content.strip())
            load_dotenv(override=True)
            st.session_state.selected_provider_index = provider_names.index(selected_provider_name)
            st.success(f"✅ {selected_provider_name} API key saved!")
            st.rerun()

    # Compact API Key Status
    st.sidebar.markdown("### 📊 API Status")
    primary_provider_env_val = os.getenv("PRIMARY_CAMEL_PROVIDER")

    for provider_name, env_var_name in providers.items():
        is_set = bool(os.getenv(env_var_name))
        if is_set:
            icon = "✅" if primary_provider_env_val and provider_name.upper().replace(" ", "_") == primary_provider_env_val else "✔️"
            st.sidebar.success(f"{icon} {provider_name}")
        else:
            icon = "🚨" if primary_provider_env_val and provider_name.upper().replace(" ", "_") == primary_provider_env_val else "⚠️"
            st.sidebar.warning(f"{icon} {provider_name}")

    # Quick Start Guide (Compact)
    with st.expander("🚀 Quick Start", expanded=False):
        st.markdown("""
        **Ready in 3 steps:**
        1. 🔑 Configure API keys in the sidebar
        2. 🎯 Choose a feature below to get started
        3. 🚀 Start experimenting with AI agents!
        
        **Need help?** Check out our [Setup Guide](SETUP_GUIDE.md) or [Repository Index](REPOSITORY_INDEX.md)
        """)

    # Main Feature Cards - Prominently displayed
    st.markdown("## 🎯 Choose Your Adventure")
    
    # Create 2x2 grid for feature cards
    col1, col2 = st.columns(2)
    
    with col1:
        # Chat Agents Card
        st.markdown("""
        <div class="feature-card chat-card">
            <h4>💬 Chat Agents</h4>
            <p>Create and interact with AI agents using custom roles and personalities</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 Start Chatting", key="chat_btn"):
            st.switch_page("pages/01_Chat_Agents.py")
            
        # Task Automation Card
        st.markdown("""
        <div class="feature-card task-card">
            <h4>🎯 Task Automation</h4>
            <p>Set up autonomous task completion with progress tracking</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("⚡ Automate Tasks", key="task_btn"):
            st.switch_page("pages/03_Task_Automation.py")

    with col2:
        # Role Playing Card
        st.markdown("""
        <div class="feature-card role-card">
            <h4>🎭 Role Playing</h4>
            <p>Create scenarios with multiple agents in different roles</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🎪 Start Role Play", key="role_btn"):
            st.switch_page("pages/02_Role_Playing.py")
            
        # Visualization Card
        st.markdown("""
        <div class="feature-card viz-card">
            <h4>📊 Visualization</h4>
            <p>Analyze and visualize your agent interactions and performance</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📈 View Analytics", key="viz_btn"):
            st.switch_page("pages/04_Visualization.py")

    # Stats Summary (if there's data)
    col1, col2, col3, col4 = st.columns(4)
    
    # Check for existing data
    conv_count = len(list(Path("conversation_history").glob("*.json"))) if Path("conversation_history").exists() else 0
    role_count = len(list(Path("role_play_history").glob("*.json"))) if Path("role_play_history").exists() else 0
    task_count = len(list(Path("task_history").glob("*.json"))) if Path("task_history").exists() else 0
    
    with col1:
        st.metric("💬 Conversations", conv_count)
    with col2:
        st.metric("🎭 Role Plays", role_count)
    with col3:
        st.metric("🎯 Tasks", task_count)
    with col4:
        api_count = sum(1 for env_var in providers.values() if os.getenv(env_var))
        st.metric("🔑 APIs Ready", f"{api_count}/4")

if __name__ == "__main__":
    main()