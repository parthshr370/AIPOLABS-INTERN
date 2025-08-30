import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

# Configure the page
st.set_page_config(
    page_title="CAMEL AI - Visualization",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .visualization-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .chart-container {
        background-color: #fff;
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

def load_conversation_history():
    history_dir = Path("conversation_history")
    if not history_dir.exists():
        return []
    
    conversations = []
    for file in history_dir.glob("*.json"):
        with open(file, 'r') as f:
            conversations.append(json.load(f))
    return conversations

def load_role_play_history():
    history_dir = Path("role_play_history")
    if not history_dir.exists():
        return []
    
    sessions = []
    for file in history_dir.glob("*.json"):
        with open(file, 'r') as f:
            sessions.append(json.load(f))
    return sessions

def load_task_history():
    history_dir = Path("task_history")
    if not history_dir.exists():
        return []
    
    tasks = []
    for file in history_dir.glob("*.json"):
        with open(file, 'r') as f:
            tasks.append(json.load(f))
    return tasks

def analyze_conversation_stats(conversations):
    if not conversations:
        return pd.DataFrame()
    
    stats = []
    for conv in conversations:
        message_count = len(conv.get('messages', []))
        avg_length = np.mean([len(str(m.get('content', ''))) for m in conv.get('messages', [])])
        stats.append({
            'timestamp': conv.get('timestamp'),
            'model': conv.get('model'),
            'messages': message_count,
            'avg_length': avg_length
        })
    return pd.DataFrame(stats)

def analyze_role_play_stats(sessions):
    if not sessions:
        return pd.DataFrame()
    
    stats = []
    for session in sessions:
        conversation = session.get('conversation', [])
        agent1_messages = len([m for m in conversation if m.get('role') == 'agent1'])
        agent2_messages = len([m for m in conversation if m.get('role') == 'agent2'])
        stats.append({
            'timestamp': session.get('timestamp'),
            'agent1_role': session.get('agent1_role'),
            'agent2_role': session.get('agent2_role'),
            'agent1_messages': agent1_messages,
            'agent2_messages': agent2_messages,
            'total_messages': len(conversation)
        })
    return pd.DataFrame(stats)

def analyze_task_stats(tasks):
    if not tasks:
        return pd.DataFrame()
    
    stats = []
    for task_set in tasks:
        completed = len([s for s in task_set.get('status', {}).values() if s == 'completed'])
        failed = len([s for s in task_set.get('status', {}).values() if s == 'failed'])
        stats.append({
            'timestamp': task_set.get('timestamp'),
            'total_tasks': len(task_set.get('tasks', [])),
            'completed_tasks': completed,
            'failed_tasks': failed
        })
    return pd.DataFrame(stats)

def main():
    st.title("📊 Visualization")
    st.markdown("""
    Analyze and visualize data from your CAMEL AI interactions, including conversation patterns,
    role-playing statistics, and task completion metrics.
    """)
    
    # Load historical data
    conversations = load_conversation_history()
    role_play_sessions = load_role_play_history()
    tasks = load_task_history()
    
    # Data analysis
    conv_stats = analyze_conversation_stats(conversations)
    role_stats = analyze_role_play_stats(role_play_sessions)
    task_stats = analyze_task_stats(tasks)
    
    # Visualization sections
    tab1, tab2, tab3 = st.tabs(["Conversations", "Role Playing", "Tasks"])
    
    with tab1:
        st.header("Conversation Analysis")
        if not conv_stats.empty:
            # Message count over time
            fig1 = px.line(conv_stats, x='timestamp', y='messages',
                          title='Message Count Over Time')
            st.plotly_chart(fig1)
            
            # Average message length by model
            fig2 = px.box(conv_stats, x='model', y='avg_length',
                         title='Message Length Distribution by Model')
            st.plotly_chart(fig2)
            
            # Statistics summary
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Conversations", len(conversations))
            col2.metric("Avg Messages/Conversation", conv_stats['messages'].mean().round(2))
            col3.metric("Avg Message Length", conv_stats['avg_length'].mean().round(2))
        else:
            st.info("No conversation data available. Start some conversations to see analytics!")
    
    with tab2:
        st.header("Role Playing Analysis")
        if not role_stats.empty:
            # Message distribution between agents
            fig3 = go.Figure(data=[
                go.Bar(name='Agent 1', x=role_stats['timestamp'], y=role_stats['agent1_messages']),
                go.Bar(name='Agent 2', x=role_stats['timestamp'], y=role_stats['agent2_messages'])
            ])
            fig3.update_layout(title='Message Distribution Between Agents', barmode='stack')
            st.plotly_chart(fig3)
            
            # Role combinations
            role_combinations = pd.DataFrame({
                'Roles': role_stats['agent1_role'] + ' & ' + role_stats['agent2_role'],
                'Count': 1
            }).groupby('Roles').count()
            fig4 = px.pie(role_combinations, values='Count', names=role_combinations.index,
                         title='Popular Role Combinations')
            st.plotly_chart(fig4)
            
            # Statistics summary
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Sessions", len(role_play_sessions))
            col2.metric("Avg Messages/Session", role_stats['total_messages'].mean().round(2))
            col3.metric("Unique Role Combinations", len(role_combinations))
        else:
            st.info("No role-playing data available. Try some role-playing sessions to see analytics!")
    
    with tab3:
        st.header("Task Analysis")
        if not task_stats.empty:
            # Task completion rates over time
            fig5 = px.line(task_stats, x='timestamp', y=['completed_tasks', 'failed_tasks'],
                          title='Task Completion Rates Over Time')
            st.plotly_chart(fig5)
            
            # Success rate distribution
            success_rates = (task_stats['completed_tasks'] / task_stats['total_tasks'] * 100)
            fig6 = px.histogram(success_rates, nbins=10,
                              title='Distribution of Task Success Rates (%)',
                              labels={'value': 'Success Rate (%)', 'count': 'Frequency'})
            st.plotly_chart(fig6)
            
            # Statistics summary
            col1, col2, col3 = st.columns(3)
            total_tasks = task_stats['total_tasks'].sum()
            total_completed = task_stats['completed_tasks'].sum()
            col1.metric("Total Tasks", total_tasks)
            col2.metric("Tasks Completed", total_completed)
            col3.metric("Success Rate", f"{(total_completed/total_tasks*100):.1f}%")
        else:
            st.info("No task data available. Complete some tasks to see analytics!")
    
    # Export functionality
    st.sidebar.header("Export Data")
    export_format = st.sidebar.selectbox("Choose format:", ["CSV", "JSON"])
    
    if st.sidebar.button("Export All Data"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if export_format == "CSV":
            # Export to CSV
            with pd.ExcelWriter(f"camel_analytics_{timestamp}.xlsx") as writer:
                if not conv_stats.empty:
                    conv_stats.to_excel(writer, sheet_name="Conversations", index=False)
                if not role_stats.empty:
                    role_stats.to_excel(writer, sheet_name="Role_Playing", index=False)
                if not task_stats.empty:
                    task_stats.to_excel(writer, sheet_name="Tasks", index=False)
            st.sidebar.success("Data exported to Excel file!")
        else:
            # Export to JSON
            export_data = {
                "conversations": conv_stats.to_dict('records') if not conv_stats.empty else [],
                "role_playing": role_stats.to_dict('records') if not role_stats.empty else [],
                "tasks": task_stats.to_dict('records') if not task_stats.empty else []
            }
            with open(f"camel_analytics_{timestamp}.json", 'w') as f:
                json.dump(export_data, f, indent=2)
            st.sidebar.success("Data exported to JSON file!")

if __name__ == "__main__":
    main()