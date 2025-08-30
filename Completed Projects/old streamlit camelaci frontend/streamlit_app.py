#!/usr/bin/env python3
import asyncio
import os
import streamlit as st
from dotenv import load_dotenv
import traceback
from datetime import datetime
import nest_asyncio

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.toolkits import MCPToolkit
from camel.types import ModelPlatformType
from create_config import create_config

# Allow nested event loops for Streamlit compatibility
nest_asyncio.apply()

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="CAMEL-AI & ACI.dev MCP Chat",
    page_icon="🐪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container improvements - Better space utilization */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
        max-width: 100%;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 1rem;
        font-style: italic;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        max-width: 80%;
        word-wrap: break-word;
        clear: both;
        display: block;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: auto;
        margin-right: 0;
        float: right;
        clear: both;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        color: #333;
        border-left: 4px solid #1f77b4;
        margin-left: 0;
        margin-right: auto;
        float: left;
        clear: both;
    }
    
    .system-message {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        color: #856404;
        border-left: 4px solid #ffc107;
        margin: 0.5rem auto;
        max-width: 90%;
        text-align: center;
        font-style: italic;
        float: none;
        clear: both;
    }
    
    /* IMPROVED Chat container - Much larger! */
    .chat-container {
        height: 60vh;
        min-height: 500px;
        max-height: 70vh;
        overflow-y: auto;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 1rem;
        background-color: #f8f9fa;
        margin-bottom: 1rem;
    }
    
    /* Clear floats after chat messages */
    .chat-container::after {
        content: "";
        display: table;
        clear: both;
    }
    
    /* Tools summary */
    .tools-summary {
        background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%);
        color: #155724;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #28a745;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize session state variables"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    
    if 'mcp_toolkit' not in st.session_state:
        st.session_state.mcp_toolkit = None
    
    if 'tools' not in st.session_state:
        st.session_state.tools = []
    
    if 'agent_initialized' not in st.session_state:
        st.session_state.agent_initialized = False
    
    if 'input_key' not in st.session_state:
        st.session_state.input_key = 0

async def initialize_agent(google_api_key, aci_api_key, linked_account_id, model_type, temperature, max_tokens):
    """Initialize the CAMEL agent with MCP toolkit - following the working CLI pattern"""
    
    # Set environment variables for create_config
    os.environ["GOOGLE_API_KEY"] = google_api_key
    os.environ["ACI_API_KEY"] = aci_api_key
    os.environ["LINKED_ACCOUNT_OWNER_ID"] = linked_account_id
    
    # Create config using the working function
    create_config(linked_account_id)
    
    # Connect to MCP toolkit with error handling
    mcp_toolkit = None
    tools = []
    
    try:
        mcp_toolkit = MCPToolkit(config_path='config.json')
        await mcp_toolkit.connect()
        
        # Try to get tools with error handling for the unhashable type issue
        try:
            tools = mcp_toolkit.get_tools()
        except TypeError as e:
            if "unhashable type" in str(e):
                st.warning("⚠️ Tool parameter parsing issue detected. This is a known compatibility issue with some MCP tools.")
                st.info("💡 Continuing without external tools. The agent will still work for general conversations.")
                tools = []
                # Don't disconnect here, keep the toolkit for potential future use
            else:
                raise e
                
    except Exception as e:
        st.error(f"❌ MCP connection failed: {str(e)}")
        st.info("💡 Continuing without external tools. The agent will still work for general conversations.")
        mcp_toolkit = None
        tools = []
    
    # Create model
    model = ModelFactory.create(
        model_platform=ModelPlatformType.GEMINI,
        model_type=model_type,
        api_key=google_api_key,
        model_config_dict={
            "temperature": temperature, 
            "max_tokens": max_tokens
        }
    )
    
    # Create system message
    if tools:
        sys_content = "You are a helpful assistant with access to search, GitHub, arXiv, and Gmail tools. You can have ongoing conversations and remember the context of our discussion."
    else:
        sys_content = "You are a helpful assistant. While external tools are not currently available, you can still help with general questions, explanations, and conversations."
    
    sys_msg = BaseMessage.make_assistant_message(
        role_name="Assistant",
        content=sys_content
    )
    
    # Create agent
    agent = ChatAgent(
        model=model,
        system_message=sys_msg,
        tools=tools,
        memory=None
    )
    
    return agent, mcp_toolkit, tools

def get_tool_name(tool):
    """Extract tool name from tool object"""
    if hasattr(tool, 'name') and tool.name:
        return tool.name
    elif hasattr(tool, 'func_json_schema') and isinstance(tool.func_json_schema, dict) and 'name' in tool.func_json_schema:
        return tool.func_json_schema['name']
    elif hasattr(tool, 'func') and hasattr(tool.func, '__name__'):
        return tool.func.__name__
    return "UnknownTool"

def display_tools_summary():
    """Display available tools"""
    if st.session_state.tools:
        tool_names = [get_tool_name(tool) for tool in st.session_state.tools]
        tools_text = ", ".join(tool_names[:4])
        if len(tool_names) > 4:
            tools_text += f" (+{len(tool_names)-4} more)"
        
        st.markdown(f"""
        <div class="tools-summary">
            🔧 <strong>{len(tool_names)} tools available:</strong> {tools_text}
        </div>
        """, unsafe_allow_html=True)

def display_chat_history():
    """Display the chat history"""
    if not st.session_state.chat_history:
        st.markdown('<div class="system-message">No messages yet. Start a conversation!</div>', unsafe_allow_html=True)
        return
    
    for message in st.session_state.chat_history:
        if message['type'] == 'user':
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong><br>
                {message['content']}
            </div>
            <div style="clear: both;"></div>
            """, unsafe_allow_html=True)
        elif message['type'] == 'assistant':
            tools_used = message.get('tools_used', [])
            tools_info = ""
            if tools_used:
                tool_names = [get_tool_name(tool) for tool in tools_used]
                tools_info = f"<br><small>🔧 <em>Used tools: {', '.join(tool_names)}</em></small>"
            
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>Assistant:</strong><br>
                {message['content']}{tools_info}
            </div>
            <div style="clear: both;"></div>
            """, unsafe_allow_html=True)
        elif message['type'] == 'system':
            st.markdown(f"""
            <div class="chat-message system-message">
                {message['content']}
            </div>
            <div style="clear: both;"></div>
            """, unsafe_allow_html=True)

async def process_message(message_content, agent):
    """Process a message - following the working CLI pattern"""
    user_message = BaseMessage.make_user_message(
        role_name="User",
        content=message_content
    )
    
    response = await agent.astep(user_message)
    
    # Extract response content
    response_content = ""
    if response and hasattr(response, "msgs") and response.msgs:
        response_content = "\n".join([msg.content for msg in response.msgs])
    
    # Extract tool usage info
    tools_used = []
    if hasattr(response, 'info') and response.info:
        raw_tool_calls = response.info.get('tool_calls', response.info.get('function_calls', []))
        if raw_tool_calls:
            tools_used = raw_tool_calls
    
    return response_content, tools_used

def reset_chat():
    """Reset the chat session"""
    if st.session_state.mcp_toolkit:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(st.session_state.mcp_toolkit.disconnect())
            loop.close()
        except Exception as e:
            st.warning(f"Warning during disconnect: {str(e)}")
    
    # Reset session state
    st.session_state.chat_history = []
    st.session_state.agent = None
    st.session_state.mcp_toolkit = None
    st.session_state.tools = []
    st.session_state.agent_initialized = False
    st.session_state.input_key += 1
    
    st.success("Chat session reset successfully!")
    st.rerun()

def main():
    initialize_session_state()
    
    st.markdown('<h1 class="main-header">🐪 CAMEL-AI & ACI.dev MCP Chat</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Multi-turn conversation with CAMEL-AI agents enhanced by ACI.dev MCP tools</p>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Configuration inputs
        default_google_key = os.getenv("GOOGLE_API_KEY", "")
        default_aci_key = os.getenv("ACI_API_KEY", "")
        default_linked_id = os.getenv("LINKED_ACCOUNT_OWNER_ID", "")
        
        st.subheader("🔑 API Keys")
        google_api_key = st.text_input("Google API Key", value=default_google_key, type="password")
        aci_api_key = st.text_input("ACI API Key", value=default_aci_key, type="password")
        linked_account_id = st.text_input("Linked Account Owner ID", value=default_linked_id)
        
        st.subheader("🤖 Model Settings")
        model_options = {
            "gemini-2.0-flash": "⚡ Gemini 2.0 Flash (Latest & Fast)",
            "gemini-2.5-pro-preview-05-06": "🧠 Gemini 2.5 Pro Preview",
            "gemini-2.5-flash-preview-05-20": "🚀 Gemini 2.5 Flash Preview",
            "gemini-1.5-pro": "🔧 Gemini 1.5 Pro",
            "gemini-1.5-flash": "💨 Gemini 1.5 Flash"
        }
        model_type = st.selectbox("Model Type", options=list(model_options.keys()), format_func=lambda x: model_options[x], index=0)
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
        max_tokens = st.number_input("Max Tokens", 1000, 80000, 40000)
        
        config_valid = all([google_api_key, aci_api_key, linked_account_id])
        
        if not config_valid:
            st.error("⚠️ Please fill in all required fields")
        
        st.markdown("---")
        
        if st.session_state.agent_initialized:
            st.success(f"✅ Agent Ready - {len(st.session_state.chat_history)} messages")
            if st.button("🔄 Reset Chat", type="secondary"):
                reset_chat()
        else:
            st.warning("🟡 Agent not initialized")
    
    # Main interface
    if not config_valid:
        st.warning("Please configure your API keys in the sidebar to continue.")
        return
    
    # Initialize agent if needed
    if not st.session_state.agent_initialized:
        if st.button("🚀 Initialize Chat Agent", type="primary", use_container_width=True):
            try:
                with st.spinner("Initializing agent..."):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    agent, mcp_toolkit, tools = loop.run_until_complete(
                        initialize_agent(google_api_key, aci_api_key, linked_account_id, 
                                       model_type, temperature, max_tokens)
                    )
                    
                    st.session_state.agent = agent
                    st.session_state.mcp_toolkit = mcp_toolkit
                    st.session_state.tools = tools
                    st.session_state.agent_initialized = True
                    
                    # Add welcome message
                    st.session_state.chat_history.append({
                        'type': 'system',
                        'content': "Chat session initialized! I'm ready to help you with questions about current events, code, research papers, email management, and more.",
                        'timestamp': datetime.now()
                    })
                    
                    st.success("✅ Agent initialized successfully!")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Initialization failed: {str(e)}")
                with st.expander("🐛 Error Details"):
                    st.code(traceback.format_exc())
        return
    
    # Display tools and chat
    display_tools_summary()
    
    st.subheader("💬 Chat")
    
    # Chat display
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        display_chat_history()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    input_cols = st.columns([5, 1])
    with input_cols[0]:
        user_input = st.text_input(
            "Type your message:",
            placeholder="Ask me anything! I can search the web, find code on GitHub, look up research papers, manage emails...",
            key=f"chat_input_{st.session_state.input_key}",
            label_visibility="collapsed"
        )
    with input_cols[1]:
        send_button = st.button("📤 Send", type="primary", use_container_width=True)
    
    # Process message
    if send_button and user_input.strip():
        # Add user message
        st.session_state.chat_history.append({
            'type': 'user',
            'content': user_input,
            'timestamp': datetime.now()
        })
        
        try:
            with st.spinner("🤔 Thinking..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                response_content, tools_used = loop.run_until_complete(
                    process_message(user_input, st.session_state.agent)
                )
                
                # Add assistant response
                st.session_state.chat_history.append({
                    'type': 'assistant',
                    'content': response_content,
                    'timestamp': datetime.now(),
                    'tools_used': tools_used
                })
                
                st.session_state.input_key += 1
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            with st.expander("🐛 Error Details"):
                st.code(traceback.format_exc())
    
    # Example prompts
    if len(st.session_state.chat_history) <= 1:
        st.markdown("---")
        st.markdown("### 💡 Try these examples:")
        example_cols = st.columns(2)
        prompts = [
            ("🔍 Latest AI news", "What are the latest developments in AI? Search for recent news."),
            ("📚 ML research papers", "Find recent machine learning research papers on arXiv"),
            ("💻 Python frameworks", "Find popular Python web frameworks on GitHub"),
            ("📧 Gmail help", "What can you help me with regarding Gmail management?")
        ]
        for i, (btn_text, prompt_content) in enumerate(prompts):
            with example_cols[i % 2]:
                if st.button(btn_text, use_container_width=True, key=f"example_{i}"):
                    st.session_state.chat_history.append({
                        'type': 'user',
                        'content': prompt_content,
                        'timestamp': datetime.now()
                    })
                    st.session_state.input_key += 1
                    st.rerun()

if __name__ == "__main__":
    main()