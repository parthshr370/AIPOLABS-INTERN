from env_config import load_environment
load_environment()

import streamlit as st
from camel_agents import (
    idea_validator_agent,
    business_model_agent,
    pitch_deck_agent,
    ui_design_agent,
    growth_strategy_agent,
    monetization_agent,
)
import re
import time

def clean_text(text):
    text = text.replace("’", "'").replace("“", '"').replace("”", '"')  
    text = text.replace("\u2014", "-").replace("\u2013", "-")  
    emoji_pattern = re.compile("[" 
                               u"\U0001F600-\U0001F64F" 
                               u"\U0001F300-\U0001F5FF" 
                               u"\U0001F680-\U0001F6FF" 
                               u"\U0001F1E0-\U0001F1FF" 
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)  

# Streamlit Config
st.set_page_config(
    page_title="🏆 Startup Incubator - Powered by Camel AI, Mistral & LangGraph",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
.glass-container { 
    background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(12px); border-radius: 15px;
    padding: 20px; box-shadow: 0 6px 14px rgba(59,130,246,0.4);
}
.stTextInput>div>div>input {
    width: 100%; padding: 16px; font-size: 18px; font-weight: 500; color: #f9fafb;
    background: rgba(31,41,55, 0.85); border: 2px solid #374151; border-radius: 16px;
    transition: all 0.3s ease-in-out;
}
.stTextInput>div>div>input:focus {
    outline: none; border-color: #3b82f6; background: rgba(17,24,39, 0.95); transform: scale(1.03);
}
.stButton>button {
    display: block; margin: 30px auto; background: linear-gradient(135deg, #4f46e5, #3b82f6);
    color: white; font-weight: 700; font-size: 20px; padding: 16px 52px; border-radius: 30px;
    border: none; cursor: pointer; box-shadow: 0 6px 15px rgba(59,130,246,0.4); transition: all 0.3s ease-in-out;
}
.stButton>button:hover { box-shadow: 0 8px 25px rgba(59,130,246,0.65); transform: scale(1.05); }
a {
    color: #3b82f6;
    text-decoration: none;
}
a:hover {
    text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)


with st.sidebar:
    st.header("💡 Founders' Strategy Suite")
    st.markdown("""
    ### 🚀 About This App
    **Founders' Strategy Suite** is your all-in-one AI-powered startup incubator built using cutting-edge tools:
    - <a href="https://www.camel-ai.org/" target="_blank" rel="noopener noreferrer">Camel AI</a> for intelligent multi-agent collaboration  
    - <a href="https://mistral.ai/" target="_blank" rel="noopener noreferrer">Mistral</a> for powerful language models  
    - <a href="https://www.langchain.com/langgraph" target="_blank" rel="noopener noreferrer">LangGraph</a> for seamless AI workflow orchestration  

    This app transforms your raw startup ideas into comprehensive business plans by generating:  
    - ✅ Validated Idea Insights  
    - 💰 Robust Business Models  
    - 📊 Persuasive Pitch Decks  
    - 🎨 Modern UI/UX Design Concepts  
    - 📈 Effective Growth Strategies  
    - 💲 Monetization Blueprints  

    **Designed for founders who want to innovate faster and smarter.**

    ---
    📚 Explore each section to unlock expert guidance tailored for your startup journey.
    """, unsafe_allow_html=True)
    st.markdown("---")


col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    st.markdown("<h1 style='text-align: center; color: #f9fafb;'>💡 Founders' Strategy Suite</h1>", unsafe_allow_html=True)
    idea = st.text_input("Describe your startup idea:", placeholder="What can I help you with today?", key="idea_input")


if "conversations" not in st.session_state:
    st.session_state["conversations"] = []


tasks = [
    ("Idea Validation", idea_validator_agent),
    ("Business Model", business_model_agent),
    ("Pitch Deck", pitch_deck_agent),
    ("UI Design", ui_design_agent),
    ("Growth Strategy", growth_strategy_agent),
    ("Monetization", monetization_agent),
]

if st.button("✨ Generate Business Plan"):
    if not idea.strip():
        st.warning("Please enter your idea first")
    else:
        progress_bar = st.progress(0)
        plan = {}

        for idx, (section, func) in enumerate(tasks):
            progress = int((idx + 1) / len(tasks) * 100)
            progress_bar.progress(progress, text=f"Generating {section}...")
            answer = func(idea)
            with st.container():
                st.markdown(f'<div class="glass-container"><h2>{section}</h2><p>{answer}</p></div>', unsafe_allow_html=True)
            plan[section] = answer
        
        progress_bar.empty()
        st.success("Business plan generated successfully!")
        st.session_state["conversations"].insert(0, {"idea": idea, "plan": plan})  # Save history

if st.session_state.conversations:
    st.markdown("## 📚 Previous Analyses")
for idx, convo in enumerate(st.session_state.conversations):
    with st.expander(f"💡 Idea: {clean_text(convo['idea'])}", expanded=(idx == 0)):
        for section, content in convo["plan"].items():
            st.markdown(f"### {section}")
            st.write(content)
            st.markdown("---")







