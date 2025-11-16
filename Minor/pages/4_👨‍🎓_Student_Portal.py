"""
Student Portal - AI Chatbot & Study Tools
"""

import streamlit as st
import asyncio
from datetime import datetime
import uuid
from utils.ui_components import (
    check_authentication, render_chat_message, 
    render_info_box
)
from services.rag_engine import RAGEngine
from services.analytics import AnalyticsService
from services.database import Database

# Page config
st.set_page_config(
    page_title="Student Portal",
    page_icon="👨‍🎓",
    layout="wide"
)

# Check authentication
check_authentication()

# Initialize services
@st.cache_resource
def init_services():
    db = Database()
    return RAGEngine(), AnalyticsService(db), db

rag_engine, analytics, db = init_services()

# Async helper function for Streamlit context
@st.cache_resource
def get_event_loop():
    """Get or create event loop for async operations"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop

def run_async(coro):
    """Helper to run async functions in Streamlit"""
    loop = get_event_loop()
    return loop.run_until_complete(coro)

# Initialize chat history and session ID in session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_session_id' not in st.session_state:
    st.session_state.current_session_id = str(uuid.uuid4())

# Page header
st.markdown("# 👨‍🎓 Student Portal")
st.markdown("### AI-Powered Learning Assistant")

# Sidebar - Session management
with st.sidebar:
    st.markdown("### 💾 Session")
    if st.button("🔄 New Chat Session", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.current_session_id = str(uuid.uuid4())
        st.success("Started new session!")
    
    if st.button("📥 Download Chat History", use_container_width=True):
        if st.session_state.chat_history:
            chat_text = "\n\n".join([
                f"{'You' if msg['is_user'] else 'AI'}: {msg['content']}"
                for msg in st.session_state.chat_history
            ])
            st.download_button(
                "Download",
                chat_text,
                file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

# Main content area
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 My Stats", "ℹ️ How to Use"])

with tab1:
    render_info_box(
        "Q&A Mode",
        "Ask any question and get instant answers from your course materials. Your conversation is saved, so you can ask follow-up questions!",
        "💬"
    )
    
    # Chat interface
    st.markdown("### 💬 Chat Interface")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            render_chat_message(message['content'], message['is_user'])
    
    # Chat input
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_area(
            "Your message:",
            height=100,
            placeholder="Type your question here... (e.g., 'Explain neural networks' or 'What is machine learning?')",
            key="chat_input"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        send_button = st.button("🚀 Send", use_container_width=True, type="primary")
    
    # Handle send
    if send_button and user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            'content': user_input,
            'is_user': True,
            'timestamp': datetime.now()
        })
        
        # Show processing
        with st.spinner("🤔 AI is thinking..."):
            try:
                # Get AI response using the conversational RAG engine
                result = run_async(rag_engine.answer_query(user_input, st.session_state.current_session_id))
                
                # Format response
                response = result['answer']
                sources = result.get('sources', [])
                
                if sources:
                    response += f"\n\n📚 **Sources:** {', '.join(sources)}"
                
                # Add AI response to history
                st.session_state.chat_history.append({
                    'content': response,
                    'is_user': False,
                    'timestamp': datetime.now()
                })
                
                # Log analytics
                analytics.log_chat_interaction(
                    st.session_state.user_id,
                    "qa"  # Mode is now fixed to qa
                )
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("💡 Tip: Make sure documents are uploaded and processed by faculty. You may also need to set your GROQ_API_KEY environment variable.")
    
    # Clear chat button
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()

with tab2:
    st.markdown("### 📊 Your Learning Statistics")
    # This part remains unchanged
    # ...

with tab3:
    st.markdown("""
    ### 📖 How to Use the Student Portal
    
    This portal allows you to have a conversation with an AI assistant that has access to your course materials.
    
    #### 💡 Tips for Best Results
    
    1. **Be Specific**: Instead of "Tell me about AI", try "Explain the difference between supervised and unsupervised learning".
    
    2. **Ask Follow-up Questions**: The AI remembers your conversation. You can ask for more details or clarifications.
    
    3. **Start a New Session**: If you want to talk about a completely different topic, use the "New Chat Session" button in the sidebar.
    
    4. **Save Important Answers**: Download your chat history for later review.
    
    #### 🚀 Getting Started
    
    1. Type your question in the input box.
    2. Click "Send" and wait for the AI response.
    3. Continue the conversation or start a new one!
    
    #### ⚠️ Important Notes
    
    - Responses are based on documents uploaded by faculty.
    - If you get generic answers, faculty may need to upload more materials.
    - Your chat history is saved during your session.
    """)

# Footer
st.markdown("---")
st.caption(f"Logged in as: {st.session_state.username} | Role: Student | Session ID: {st.session_state.current_session_id[:8]}...")