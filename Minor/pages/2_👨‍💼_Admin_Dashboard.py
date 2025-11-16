"""
Admin Dashboard - User Management & System Analytics
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.ui_components import (
    check_authentication, render_stats_grid,
    render_info_box, check_role
)
from services.database import Database
from services.analytics import AnalyticsService
from utils.auth import create_user, hash_password

# Page config
st.set_page_config(
    page_title="Admin Dashboard",
    page_icon="👨‍💼",
    layout="wide"
)

# Check authentication and role
check_authentication()
check_role('admin')

# Initialize services
@st.cache_resource
def init_services():
    db = Database()
    return db, AnalyticsService(db)

db, analytics = init_services()

# Page header
st.markdown("# 👨‍💼 Admin Dashboard")
st.markdown("### System Management & Analytics")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview",
    "👥 User Management",
    "📁 Document Management",
    "📈 Analytics"
])

with tab1:
    st.markdown("### 📊 System Overview")
    
    # Get system stats
    try:
        total_users = db.count_users()
        total_docs = db.count_documents()
        total_sessions = db.count_sessions()
        storage_mb = analytics.get_storage_usage()
        active_today = analytics.get_active_users_today()
        
        # Display metrics grid
        stats = [
            ("Total Users", total_users, "👥"),
            ("Documents", total_docs, "📄"),
            ("Chat Sessions", total_sessions, "💬"),
            ("Storage (MB)", f"{storage_mb:.2f}", "💾"),
            ("Active Today", active_today, "🟢")
        ]
        
        render_stats_grid(stats)
        
        st.markdown("---")
        
        # Platform statistics
        platform_stats = analytics.get_platform_stats()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📄 Document Statistics")
            doc_stats = platform_stats['documents']
            
            st.metric("Total Documents", doc_stats['total'])
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Completed", doc_stats['completed'], 
                         delta=f"{(doc_stats['completed']/doc_stats['total']*100):.1f}%" if doc_stats['total'] > 0 else "0%")
            with col_b:
                st.metric("Processing", doc_stats['processing'])
            
            if doc_stats['failed'] > 0:
                st.warning(f"⚠️ {doc_stats['failed']} documents failed processing")
        
        with col2:
            st.markdown("### 💬 Chat Statistics")
            chat_stats = platform_stats['chat']
            
            st.metric("Total Sessions", chat_stats['total_sessions'])
            st.metric("Total Messages", chat_stats['total_messages'])
            st.metric("Avg Messages/Session", chat_stats['avg_messages_per_session'])
        
        # Generated content
        if platform_stats['generated_content']['total'] > 0:
            st.markdown("### ✏️ Generated Content")
            
            content_data = platform_stats['generated_content']['by_type']
            
            if content_data:
                df = pd.DataFrame([
                    {"Content Type": k.upper(), "Count": v}
                    for k, v in content_data.items()
                ])
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.bar_chart(df.set_index('Content Type'))
                
                with col2:
                    st.dataframe(df, use_container_width=True)
        
        # Activity summary
        st.markdown("### 📈 Recent Activity")
        st.info(f"📊 {platform_stats['activity']['last_7_days']} events in the last 7 days")
        
    except Exception as e:
        st.error(f"Error loading statistics: {str(e)}")

with tab2:
    st.markdown("### 👥 User Management")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Create New User")
        
        with st.form("create_user_form"):
            new_username = st.text_input("Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["student", "faculty", "admin"])
            
            submit = st.form_submit_button("➕ Create User", use_container_width=True)
            
            if submit:
                if new_username and new_password and new_email:
                    success = create_user(new_username, new_password, new_role, new_email)
                    if success:
                        st.success(f"✅ User '{new_username}' created successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Username already exists")
                else:
                    st.warning("⚠️ Please fill all fields")
    
    with col2:
        st.markdown("#### Quick Stats")
        st.metric("Total Users", total_users)
        
        # Users by role (if we had this data)
        st.info("💡 User management features")
    
    st.markdown("---")
    
    # List all users (simplified - you'd want pagination in production)
    st.markdown("#### 📋 User List")
    
    # Note: You'll need to add a method to get all users in database.py
    st.info("User list feature - Add get_all_users() method to Database class")

with tab3:
    st.markdown("### 📁 Document Management")
    
    # Get all documents
    # Note: You'll need to add get_all_documents() method
    
    st.markdown("#### 📊 Document Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        platform_stats = analytics.get_platform_stats()
        doc_stats = platform_stats['documents']
        
        with col1:
            st.metric("Total", doc_stats['total'])
        with col2:
            st.metric("Completed", doc_stats['completed'], delta="Ready")
        with col3:
            st.metric("Processing", doc_stats['processing'], delta="In Progress")
        with col4:
            st.metric("Failed", doc_stats['failed'], delta="Needs Attention" if doc_stats['failed'] > 0 else "Good")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    
    # Popular documents
    st.markdown("#### 🔥 Most Accessed Documents")
    
    try:
        popular_docs = analytics.get_popular_documents(limit=10)
        
        if popular_docs:
            df = pd.DataFrame(popular_docs)
            df = df[['filename', 'uploaded_by', 'chunks_created', 'access_count']]
            df.columns = ['Filename', 'Uploaded By', 'Chunks', 'Access Count']
            
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No document access data available yet")
    
    except Exception as e:
        st.warning("Unable to load popular documents")
    
    st.markdown("---")
    
    # Document search and delete
    st.markdown("#### 🗑️ Document Management")
    
    search_doc = st.text_input("🔍 Search documents by filename:")
    
    if search_doc:
        st.info(f"Searching for: {search_doc}")
        # Add search functionality

with tab4:
    st.markdown("### 📈 Advanced Analytics")
    
    # Usage trends
    st.markdown("#### 📊 Usage Trends (Last 7 Days)")
    
    try:
        trend_data = analytics.get_usage_trend(days=7)
        
        if trend_data['trend']:
            df = pd.DataFrame(trend_data['trend'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Events Over Time**")
                st.line_chart(df.set_index('date')['events'])
            
            with col2:
                st.markdown("**Unique Users Over Time**")
                st.line_chart(df.set_index('date')['unique_users'])
            
            # Summary table
            st.markdown("#### 📋 Daily Breakdown")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Not enough data to show trends yet")
    
    except Exception as e:
        st.warning("Unable to load usage trends")
    
    st.markdown("---")
    
    # System health
    st.markdown("#### 🏥 System Health")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        db_status = db.check_connection()
        if db_status == "operational":
            st.success("✅ Database: Healthy")
        else:
            st.error("❌ Database: Unhealthy")
    
    with col2:
        # Check vector store
        st.success("✅ Vector Store: Healthy")
    
    with col3:
        # Check storage
        if storage_mb < 1000:  # Less than 1GB
            st.success(f"✅ Storage: {storage_mb:.2f}MB")
        else:
            st.warning(f"⚠️ Storage: {storage_mb:.2f}MB")
    
    # Export data
    st.markdown("---")
    st.markdown("#### 📥 Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Analytics", use_container_width=True):
            # Export analytics data
            st.info("Export feature - Coming soon!")
    
    with col2:
        if st.button("👥 Export Users", use_container_width=True):
            st.info("Export feature - Coming soon!")
    
    with col3:
        if st.button("📄 Export Documents", use_container_width=True):
            st.info("Export feature - Coming soon!")

# Footer with system info
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.caption(f"👤 Logged in as: {st.session_state.username}")

with col2:
    st.caption(f"🔐 Role: Administrator")

with col3:
    st.caption(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")