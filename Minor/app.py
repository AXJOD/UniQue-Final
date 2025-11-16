"""
College AI Portal - Streamlit Application
Main entry point with authentication
"""

import streamlit as st
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="College AI Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        font-size: 1rem;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    .info-box {
        padding: 1.5rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin: 1rem 0;
    }
    .role-card {
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid #e0e0e0;
        text-align: center;
        transition: all 0.3s;
        cursor: pointer;
        background: white;
    }
    .role-card:hover {
        border-color: #667eea;
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
    }
</style>
""", unsafe_allow_html=True)

def show_landing_page():
    """Display landing page for non-authenticated users"""
    
    st.markdown('<h1 class="main-header">🎓 College AI Portal</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <h2 style="margin-top: 0;">Welcome to the Future of Education</h2>
        <p style="font-size: 1.1rem;">
            A comprehensive AI-powered platform for students, faculty, and administrators.
            Experience intelligent document processing, personalized learning, and advanced analytics.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🤖 AI-Powered Learning
        - Smart document analysis
        - Personalized study notes
        - Practice question generation
        - Interactive Q&A chatbot
        """)
    
    with col2:
        st.markdown("""
        ### 👨‍🏫 Faculty Tools
        - Easy document upload
        - Auto-generate assignments
        - Create MCQs & viva questions
        - Track student engagement
        """)
    
    with col3:
        st.markdown("""
        ### 📊 Admin Dashboard
        - User management
        - System analytics
        - Usage monitoring
        - Performance insights
        """)
    
    st.markdown("---")
    
    # Role selection and login
    st.markdown("### 🚀 Get Started")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("👈 Please use the sidebar to login or sign up")
    
    with col2:
        if st.button("📖 View Documentation", use_container_width=True):
            st.markdown("""
            ### Quick Guide:
            1. **Students**: Access AI chatbot, get study notes
            2. **Faculty**: Upload PDFs, generate questions
            3. **Admin**: Manage users, view analytics
            """)

def show_sidebar():
    """Display sidebar with authentication"""
    
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/education.png", width=80)
        st.title("College AI Portal")
        
        if not st.session_state.authenticated:
            st.markdown("### 🔐 Authentication")
            
            tab1, tab2 = st.tabs(["Login", "Sign Up"])
            
            with tab1:
                show_login_form()
            
            with tab2:
                show_signup_form()
        else:
            show_user_info()

def show_login_form():
    """Display login form"""
    from utils.auth import verify_user
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True)
        
        if submit:
            if username and password:
                user = verify_user(username, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.username = user['username']
                    st.session_state.user_role = user['role']
                    st.session_state.user_id = user['id']
                    st.success(f"Welcome back, {username}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.warning("Please fill in all fields")

def show_signup_form():
    """Display signup form"""
    from utils.auth import create_user
    
    with st.form("signup_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        role = st.selectbox("Role", ["student", "faculty"])
        submit = st.form_submit_button("Sign Up", use_container_width=True)
        
        if submit:
            if not all([username, email, password, confirm_password]):
                st.warning("Please fill in all fields")
            elif password != confirm_password:
                st.error("Passwords don't match")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                success = create_user(username, password, role, email)
                if success:
                    st.success("Account created! Please login.")
                else:
                    st.error("Username already exists")

def show_user_info():
    """Display logged-in user information"""
    st.success(f"✅ Logged in as **{st.session_state.username}**")
    st.info(f"Role: **{st.session_state.user_role.title()}**")
    
    st.markdown("---")
    
    # Navigation based on role
    if st.session_state.user_role == "admin":
        st.page_link("pages/2_👨‍💼_Admin_Dashboard.py", label="📊 Admin Dashboard", icon="👨‍💼")
    elif st.session_state.user_role == "faculty":
        st.page_link("pages/3_👨‍🏫_Faculty_Portal.py", label="📚 Faculty Portal", icon="👨‍🏫")
    elif st.session_state.user_role == "student":
        st.page_link("pages/4_👨‍🎓_Student_Portal.py", label="🤖 Student Portal", icon="👨‍🎓")
    
    st.markdown("---")
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.session_state.username = None
        st.session_state.user_id = None
        st.rerun()

# Main app logic
def main():
    show_sidebar()
    
    if st.session_state.authenticated:
        st.markdown(f"# Welcome, {st.session_state.username}! 👋")
        
        role = st.session_state.user_role
        
        if role == "admin":
            st.info("Navigate to **Admin Dashboard** using the sidebar →")
        elif role == "faculty":
            st.info("Navigate to **Faculty Portal** using the sidebar →")
        elif role == "student":
            st.info("Navigate to **Student Portal** using the sidebar →")
        
        # Quick stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Your Role", role.title(), "Active")
        
        with col2:
            st.metric("Status", "Online", "✓")
        
        with col3:
            st.metric("Session", "Active", "🟢")
    else:
        show_landing_page()

if __name__ == "__main__":
    # Verify Groq API key
    if not os.getenv("GROQ_API_KEY"):
        st.error("⚠️ GROQ_API_KEY not found in .env file!")
        st.stop()
    
    main()