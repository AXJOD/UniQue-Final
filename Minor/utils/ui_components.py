"""
Reusable UI components for Streamlit app
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from typing import List, Dict

def render_metric_card(title, value, delta=None, icon="📊"):
    """Render a metric card"""
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(f"<div style='font-size: 3rem;'>{icon}</div>", unsafe_allow_html=True)
    with col2:
        st.metric(title, value, delta)

def render_status_badge(status):
    """Render a status badge"""
    colors = {
        "completed": "green",
        "processing": "orange",
        "queued": "blue",
        "failed": "red"
    }
    color = colors.get(status, "gray")
    
    return f'<span style="background-color: {color}; color: white; padding: 0.2rem 0.8rem; border-radius: 12px; font-size: 0.8rem; font-weight: bold;">{status.upper()}</span>'

def render_progress_bar(current, total, label="Progress"):
    """Render a progress bar with label"""
    percentage = int((current / total) * 100) if total > 0 else 0
    st.markdown(f"**{label}:** {current}/{total}")
    st.progress(percentage / 100)
    return percentage

def render_document_card(doc, on_view=None, on_delete=None):
    """Render a document card"""
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"### 📄 {doc['filename']}")
            st.caption(f"Uploaded: {doc['created_at']}")
            st.markdown(render_status_badge(doc['status']), unsafe_allow_html=True)
        
        with col2:
            if doc['chunks_created']:
                st.metric("Chunks", doc['chunks_created'])
        
        with col3:
            if on_view and st.button("👁️ View", key=f"view_{doc['id']}"):
                on_view(doc)
            if on_delete and st.button("🗑️ Delete", key=f"del_{doc['id']}"):
                on_delete(doc)

def render_chat_message(message, is_user=True):
    """Render a chat message bubble"""
    if is_user:
        st.markdown(f"""
        <div style="background-color: #667eea; color: white; padding: 1rem; border-radius: 15px; margin: 0.5rem 0; margin-left: 20%;">
            <strong>You:</strong><br>{message}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background-color: #f0f2f6; color: #000000; padding: 1rem; border-radius: 15px; margin: 0.5rem 0; margin-right: 20%;">
            <strong>🤖 AI Assistant:</strong><br>{message}
        </div>
        """, unsafe_allow_html=True)

def render_analytics_chart(data, chart_type="line", title="Analytics"):
    """Render analytics chart using Plotly"""
    if chart_type == "line":
        fig = px.line(data, x='date', y='value', title=title)
    elif chart_type == "bar":
        fig = px.bar(data, x='category', y='value', title=title)
    elif chart_type == "pie":
        fig = px.pie(data, values='value', names='category', title=title)
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_stats_grid(stats):
    """Render a grid of statistics"""
    cols = st.columns(len(stats))
    for col, (label, value, icon) in zip(cols, stats):
        with col:
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white;">
                <div style="font-size: 2rem;">{icon}</div>
                <div style="font-size: 2rem; font-weight: bold;">{value}</div>
                <div style="font-size: 0.9rem;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

def render_loading_spinner(text="Processing..."):
    """Render a loading spinner"""
    with st.spinner(text):
        return True

def render_success_message(message):
    """Render a success message with animation"""
    st.success(f"✅ {message}")

def render_error_message(message):
    """Render an error message"""
    st.error(f"❌ {message}")

def render_info_box(title, content, icon="ℹ️"):
    """Render an info box"""
    st.markdown(f"""
    <div style="background-color: #e9eafc; border-left: 4px solid #667eea; padding: 1rem; border-radius: 5px; margin: 1rem 0; color: #000000;">
        <div style="font-size: 1.5rem;">{icon} <strong>{title}</strong></div>
        <div style="margin-top: 0.5rem;">{content}</div>
    </div>
    """, unsafe_allow_html=True)

def render_question_card(question, index):
    """Render a generated question card"""
    with st.expander(f"Question {index + 1}: {question.get('type', 'Question').title()}", expanded=True):
        st.markdown(f"**Question:** {question['question']}")
        
        if 'options' in question:
            st.markdown("**Options:**")
            for key, value in question['options'].items():
                st.markdown(f"- {key}) {value}")
            st.success(f"✓ Correct Answer: {question.get('correct_answer', 'N/A')}")
        
        if 'marking_scheme' in question:
            st.info(f"**Marks:** {question.get('marks', 'N/A')}")
            st.markdown("**Marking Scheme:**")
            st.markdown(question['marking_scheme'])
        
        if 'explanation' in question:
            st.markdown("**Explanation:**")
            st.markdown(question['explanation'])

def check_authentication():
    """Check if user is authenticated, redirect if not"""
    if not st.session_state.get('authenticated', False):
        st.error("🔒 Please login to access this page")
        st.stop()

def check_role(required_role):
    """Check if user has required role"""
    if st.session_state.get('user_role') != required_role:
        st.error(f"⛔ This page is only accessible to {required_role}s")
        st.stop()

def format_questions_for_txt(questions: List[Dict], content_type: str) -> str:
    """Formats a list of generated questions into a human-readable string for TXT download."""
    output = [f"Generated {content_type.upper()} Questions"]
    output.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("=" * 40)
    
    for q in questions:
        output.append(f"\nQuestion {q.get('question_number', '')}: {q.get('question', 'N/A')}")
        
        if 'type' in q:
            output.append(f"Type: {q['type'].title()}")
        if 'marks' in q:
            output.append(f"Marks: {q['marks']}")
        
        if 'options' in q and isinstance(q['options'], dict):
            output.append("\nOptions:")
            for key, value in q['options'].items():
                output.append(f"  {key}) {value}")
        
        if 'correct_answer' in q:
            output.append(f"\nCorrect Answer: {q['correct_answer']}")
        
        if 'explanation' in q:
            output.append(f"Explanation: {q['explanation']}")
            
        if 'marking_scheme' in q:
            output.append(f"Marking Scheme: {q['marking_scheme']}")
            
        if 'sample_answer' in q:
            output.append(f"Sample Answer: {q['sample_answer']}")
            
        if 'key_points' in q and isinstance(q['key_points'], list):
            output.append("Key Points for Answer:")
            for point in q['key_points']:
                output.append(f"  - {point}")

        output.append("-" * 40)
        
    return "\n".join(output)