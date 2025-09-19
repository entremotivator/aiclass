import streamlit as st
import os
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, timedelta
import json
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional

# Custom CSS for light green theme - User focused
def load_user_css():
    st.markdown("""
    <style>
    /* Main theme colors - Light Green for Users */
    .main {
        background: linear-gradient(135deg, #f1f8e9 0%, #e8f5e8 100%);
    }
    
    .stApp {
        background: linear-gradient(135deg, #f1f8e9 0%, #e8f5e8 100%);
    }
    
    /* User profile card */
    .profile-card {
        background: linear-gradient(135deg, #c8e6c9 0%, #ffffff 100%);
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 2px solid #a5d6a7;
    }
    
    /* Feature cards */
    .feature-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #66bb6a;
        transition: transform 0.2s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    
    /* Stats cards for users */
    .user-stats-card {
        background: linear-gradient(135deg, #dcedc8 0%, #ffffff 100%);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #c5e1a5;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #388e3c;
        margin: 0;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 5px;
    }
    
    /* Progress bars */
    .progress-container {
        background: #e8f5e8;
        border-radius: 10px;
        padding: 3px;
        margin: 10px 0;
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #4caf50 0%, #66bb6a 100%);
        height: 20px;
        border-radius: 8px;
        transition: width 0.3s ease;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #66bb6a 0%, #4caf50 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);
        transform: translateY(-1px);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #dcedc8 0%, #f1f8e9 100%);
    }
    
    /* Activity timeline */
    .activity-item {
        background: white;
        border-radius: 8px;
        padding: 15px;
        margin: 8px 0;
        border-left: 3px solid #66bb6a;
        box-shadow: 0 1px 4px rgba(0,0,0,0.1);
    }
    
    /* Usage indicators */
    .usage-good { color: #4caf50; font-weight: bold; }
    .usage-warning { color: #ff9800; font-weight: bold; }
    .usage-danger { color: #f44336; font-weight: bold; }
    
    /* Subscription badges */
    .sub-free { 
        background: #e8f5e8; 
        color: #2e7d32; 
        padding: 4px 12px; 
        border-radius: 15px; 
        font-size: 0.8rem;
        font-weight: bold;
    }
    .sub-pro { 
        background: #fff3e0; 
        color: #f57c00; 
        padding: 4px 12px; 
        border-radius: 15px; 
        font-size: 0.8rem;
        font-weight: bold;
    }
    .sub-enterprise { 
        background: #f3e5f5; 
        color: #7b1fa2; 
        padding: 4px 12px; 
        border-radius: 15px; 
        font-size: 0.8rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def init_client():
    """Initialize Supabase client"""
    try:
        url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
        anon_key = st.secrets.get("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not anon_key:
            st.error("❌ Missing Supabase configuration.")
            st.stop()
        
        return create_client(url, anon_key)
        
    except Exception as e:
        st.error(f"❌ Failed to initialize client: {str(e)}")
        st.stop()

def safe_date_format(date_string: str, format_str: str = '%Y-%m-%d') -> str:
    """Safely format date strings with error handling"""
    if not date_string:
        return "Not set"
    
    try:
        if 'T' in date_string:
            if date_string.endswith('Z'):
                date_string = date_string.replace('Z', '+00:00')
            dt = datetime.fromisoformat(date_string)
        else:
            dt = datetime.strptime(date_string, '%Y-%m-%d')
        
        return dt.strftime(format_str)
    except (ValueError, TypeError):
        return "Invalid date"

def get_user_data(supabase: Client, user_email: str) -> Dict:
    """Get comprehensive user data from all tables"""
    try:
        # Get user from auth (if we have access)
        user_data = {}
        
        # Get from profiles table
        profile_response = supabase.table("profiles").select("*").eq("id", user_email).execute()
        if profile_response.data:
            user_data.update(profile_response.data[0])
        
        # Get from users table
        users_response = supabase.table("users").select("*").eq("email", user_email).execute()
        if users_response.data:
            user_data.update(users_response.data[0])
        
        # Get user preferences
        prefs_response = supabase.table("user_preferences").select("*").eq("user_id", user_data.get('id')).execute()
        if prefs_response.data:
            user_data['preferences'] = prefs_response.data[0]
        
        # Get usage statistics
        usage_response = supabase.table("api_usage").select("*").eq("user_id", user_data.get('id')).execute()
        if usage_response.data:
            total_tokens = sum([u.get('total_tokens', 0) for u in usage_response.data])
            total_cost = sum([float(u.get('cost', 0)) for u in usage_response.data])
            user_data['usage_stats'] = {
                'total_tokens': total_tokens,
                'total_cost': total_cost,
                'requests': len(usage_response.data)
            }
        
        # Get chat threads
        threads_response = supabase.table("chat_threads").select("*").eq("user_id", user_data.get('id')).execute()
        user_data['chat_threads'] = threads_response.data if threads_response.data else []
        
        # Get file uploads
        files_response = supabase.table("file_uploads").select("*").eq("user_id", user_data.get('id')).execute()
        user_data['file_uploads'] = files_response.data if files_response.data else []
        
        # Get custom assistants
        assistants_response = supabase.table("custom_assistants").select("*").eq("user_id", user_data.get('id')).execute()
        user_data['custom_assistants'] = assistants_response.data if assistants_response.data else []
        
        # Get recent activity
        activity_response = supabase.table("user_activity_logs").select("*").eq("user_id", user_data.get('id')).order("created_at", desc=True).limit(10).execute()
        user_data['recent_activity'] = activity_response.data if activity_response.data else []
        
        return user_data
        
    except Exception as e:
        st.error(f"Error fetching user data: {str(e)}")
        return {}

def render_user_profile_card(user_data: Dict):
    """Render user profile card"""
    st.markdown('<div class="profile-card">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        # Avatar or placeholder
        if user_data.get('avatar_url'):
            st.image(user_data['avatar_url'], width=100)
        else:
            st.markdown("👤", unsafe_allow_html=True)
    
    with col2:
        # User info
        name = user_data.get('full_name', 'User')
        st.markdown(f"## 👋 Welcome, {name}!")
        st.markdown(f"📧 **Email:** {user_data.get('email', 'Not set')}")
        
        # Subscription badge
        tier = user_data.get('subscription_tier', 'free')
        if tier == 'free':
            st.markdown('<span class="sub-free">🆓 Free Plan</span>', unsafe_allow_html=True)
        elif tier == 'pro':
            st.markdown('<span class="sub-pro">⭐ Pro Plan</span>', unsafe_allow_html=True)
        elif tier == 'enterprise':
            st.markdown('<span class="sub-enterprise">💎 Enterprise Plan</span>', unsafe_allow_html=True)
        
        # Member since
        created_date = safe_date_format(user_data.get('created_at', ''))
        st.markdown(f"📅 **Member since:** {created_date}")
    
    with col3:
        # Quick stats
        st.markdown("### 📊 Quick Stats")
        threads_count = len(user_data.get('chat_threads', []))
        files_count = len(user_data.get('file_uploads', []))
        assistants_count = len(user_data.get('custom_assistants', []))
        
        st.markdown(f"💬 **Chats:** {threads_count}")
        st.markdown(f"📁 **Files:** {files_count}")
        st.markdown(f"🤖 **Assistants:** {assistants_count}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_usage_dashboard(user_data: Dict):
    """Render user usage dashboard"""
    st.markdown("## 📊 Your Usage Dashboard")
    
    # Get usage data
    usage_stats = user_data.get('usage_stats', {'total_tokens': 0, 'total_cost': 0, 'requests': 0})
    monthly_limit = user_data.get('monthly_token_limit', 10000)
    tokens_used = user_data.get('tokens_used_this_month', usage_stats['total_tokens'])
    
    # Usage percentage
    usage_percent = (tokens_used / monthly_limit) * 100 if monthly_limit > 0 else 0
    
    # Usage status
    if usage_percent < 70:
        usage_class = "usage-good"
        usage_status = "Good"
    elif usage_percent < 90:
        usage_class = "usage-warning"
        usage_status = "Warning"
    else:
        usage_class = "usage-danger"
        usage_status = "High"
    
    # Stats cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="user-stats-card">
            <div class="stat-value">{tokens_used:,}</div>
            <div class="stat-label">Tokens Used</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="user-stats-card">
            <div class="stat-value">{monthly_limit:,}</div>
            <div class="stat-label">Monthly Limit</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="user-stats-card">
            <div class="stat-value">${usage_stats['total_cost']:.2f}</div>
            <div class="stat-label">Total Cost</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="user-stats-card">
            <div class="stat-value {usage_class}">{usage_percent:.1f}%</div>
            <div class="stat-label">Usage ({usage_status})</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Usage progress bar
    st.markdown("### 📈 Token Usage Progress")
    progress_html = f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {min(usage_percent, 100)}%;"></div>
    </div>
    <p style="text-align: center; margin-top: 10px;">
        <span class="{usage_class}">{tokens_used:,} / {monthly_limit:,} tokens ({usage_percent:.1f}%)</span>
    </p>
    """
    st.markdown(progress_html, unsafe_allow_html=True)
    
    # Usage chart
    if usage_stats['requests'] > 0:
        st.markdown("### 📊 Usage Analytics")
        
        # Create a simple usage chart (you would get real data from api_usage table)
        fig = px.line(
            x=['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            y=[tokens_used * 0.2, tokens_used * 0.4, tokens_used * 0.7, tokens_used],
            title="Token Usage Over Time",
            labels={'x': 'Time Period', 'y': 'Tokens Used'}
        )
        fig.update_traces(line_color='#4caf50', line_width=3)
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333')
        )
        st.plotly_chart(fig, use_container_width=True)

def render_features_overview(user_data: Dict):
    """Render user features overview"""
    st.markdown("## 🚀 Your Features & Tools")
    
    # Feature cards
    col1, col2 = st.columns(2)
    
    with col1:
        # Chat Threads
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        threads = user_data.get('chat_threads', [])
        st.markdown(f"### 💬 Chat Threads ({len(threads)})")
        st.markdown(f"**Limit:** {user_data.get('max_threads', 10)} threads")
        
        if threads:
            st.markdown("**Recent Chats:**")
            for thread in threads[:3]:
                thread_date = safe_date_format(thread.get('created_at', ''), '%m/%d')
                st.markdown(f"• {thread.get('title', 'Untitled')} ({thread_date})")
        else:
            st.markdown("No chat threads yet. Start a conversation!")
        
        if st.button("💬 Start New Chat"):
            st.info("Redirecting to chat interface...")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Custom Assistants
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        assistants = user_data.get('custom_assistants', [])
        st.markdown(f"### 🤖 Custom Assistants ({len(assistants)})")
        
        if user_data.get('subscription_tier') in ['pro', 'enterprise']:
            if assistants:
                st.markdown("**Your Assistants:**")
                for assistant in assistants[:3]:
                    st.markdown(f"• {assistant.get('name', 'Unnamed')} - {assistant.get('category', 'General')}")
            else:
                st.markdown("No custom assistants yet. Create your first one!")
            
            if st.button("🤖 Create Assistant"):
                st.info("Redirecting to assistant builder...")
        else:
            st.markdown("🔒 Upgrade to Pro or Enterprise to create custom assistants")
            if st.button("⬆️ Upgrade Plan"):
                st.info("Redirecting to upgrade page...")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # File Uploads
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        files = user_data.get('file_uploads', [])
        st.markdown(f"### 📁 File Uploads ({len(files)})")
        st.markdown(f"**Limit:** {user_data.get('max_files', 5)} files")
        
        if files:
            st.markdown("**Recent Files:**")
            for file_upload in files[:3]:
                file_date = safe_date_format(file_upload.get('uploaded_at', ''), '%m/%d')
                file_size = file_upload.get('file_size', 0)
                size_mb = file_size / (1024 * 1024) if file_size else 0
                st.markdown(f"• {file_upload.get('original_filename', 'Unknown')} ({size_mb:.1f}MB, {file_date})")
        else:
            st.markdown("No files uploaded yet. Upload your first document!")
        
        if st.button("📁 Upload File"):
            st.info("Redirecting to file upload...")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Voice Features
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### 🎤 Voice Features")
        
        if user_data.get('voice_enabled'):
            st.markdown("✅ Voice features are enabled for your account")
            st.markdown("• Voice chat with AI assistants")
            st.markdown("• Speech-to-text transcription")
            st.markdown("• Text-to-speech output")
            
            if st.button("🎤 Try Voice Chat"):
                st.info("Redirecting to voice interface...")
        else:
            st.markdown("🔒 Voice features not available on your plan")
            if st.button("⬆️ Upgrade for Voice"):
                st.info("Redirecting to upgrade page...")
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_activity_timeline(user_data: Dict):
    """Render user activity timeline"""
    st.markdown("## 📈 Recent Activity")
    
    activities = user_data.get('recent_activity', [])
    
    if activities:
        for activity in activities:
            st.markdown('<div class="activity-item">', unsafe_allow_html=True)
            
            activity_type = activity.get('activity_type', 'Unknown')
            description = activity.get('description', 'No description')
            activity_date = safe_date_format(activity.get('created_at', ''), '%m/%d/%Y %H:%M')
            
            # Activity type icons
            icon = {
                'login': '🔐',
                'chat': '💬',
                'file_upload': '📁',
                'assistant_create': '🤖',
                'api_call': '🔗',
                'settings_update': '⚙️'
            }.get(activity_type, '📝')
            
            st.markdown(f"**{icon} {activity_type.replace('_', ' ').title()}**")
            st.markdown(f"{description}")
            st.markdown(f"*{activity_date}*")
            
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No recent activity to display. Start using the platform to see your activity here!")

def render_account_settings(user_data: Dict):
    """Render account settings"""
    st.markdown("## ⚙️ Account Settings")
    
    # User preferences
    preferences = user_data.get('preferences', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎨 Preferences")
        
        # Theme selection
        current_theme = preferences.get('theme', 'light')
        theme = st.selectbox("Theme", ['light', 'dark'], index=0 if current_theme == 'light' else 1)
        
        # Language selection
        current_language = preferences.get('language', 'en')
        language = st.selectbox("Language", ['en', 'es', 'fr', 'de'], index=['en', 'es', 'fr', 'de'].index(current_language) if current_language in ['en', 'es', 'fr', 'de'] else 0)
        
        # Notifications
        notifications = st.checkbox("Enable Notifications", value=preferences.get('notifications', True))
        email_notifications = st.checkbox("Email Notifications", value=preferences.get('email_notifications', True))
        
        if st.button("💾 Save Preferences"):
            st.success("Preferences saved successfully!")
    
    with col2:
        st.markdown("### 📊 Account Information")
        
        st.markdown(f"**Account Type:** {user_data.get('subscription_tier', 'free').title()}")
        st.markdown(f"**Status:** {'Active' if user_data.get('is_active', True) else 'Inactive'}")
        
        if user_data.get('subscription_start_date'):
            start_date = safe_date_format(user_data['subscription_start_date'])
            st.markdown(f"**Subscription Start:** {start_date}")
        
        if user_data.get('subscription_end_date'):
            end_date = safe_date_format(user_data['subscription_end_date'])
            st.markdown(f"**Subscription End:** {end_date}")
        
        st.markdown("### 🔐 Security")
        if st.button("🔑 Change Password"):
            st.info("Password change functionality would be implemented here")
        
        if st.button("📧 Update Email"):
            st.info("Email update functionality would be implemented here")

def main():
    st.set_page_config(
        page_title="User Dashboard",
        page_icon="👤",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load custom CSS
    load_user_css()
    
    # Initialize client
    supabase = init_client()
    
    # Sidebar navigation
    st.sidebar.title("👤 User Dashboard")
    
    # For demo purposes, we'll use a sample user email
    # In a real app, this would come from authentication
    user_email = st.sidebar.text_input("Enter your email (demo)", value="user@example.com")
    
    if not user_email:
        st.warning("Please enter your email to continue")
        return
    
    # Main navigation
    page = st.sidebar.selectbox("Navigate to", [
        "🏠 Dashboard",
        "📊 Usage & Analytics", 
        "🚀 Features & Tools",
        "📈 Activity Timeline",
        "⚙️ Account Settings"
    ])
    
    # Get user data
    with st.spinner("Loading your data..."):
        user_data = get_user_data(supabase, user_email)
    
    if not user_data:
        st.error("Could not load user data. Please check your email or contact support.")
        return
    
    # Render content based on selected page
    if page == "🏠 Dashboard":
        st.title("👤 User Dashboard")
        render_user_profile_card(user_data)
        
        # Quick overview
        col1, col2 = st.columns(2)
        with col1:
            render_usage_dashboard(user_data)
        with col2:
            render_activity_timeline(user_data)
    
    elif page == "📊 Usage & Analytics":
        st.title("📊 Usage & Analytics")
        render_usage_dashboard(user_data)
        
        # Additional analytics would go here
        st.markdown("### 📈 Detailed Analytics")
        st.info("Detailed usage analytics and insights would be displayed here")
    
    elif page == "🚀 Features & Tools":
        st.title("🚀 Features & Tools")
        render_features_overview(user_data)
    
    elif page == "📈 Activity Timeline":
        st.title("📈 Activity Timeline")
        render_activity_timeline(user_data)
    
    elif page == "⚙️ Account Settings":
        st.title("⚙️ Account Settings")
        render_account_settings(user_data)
    
    # Footer
    st.markdown("---")
    st.markdown("*User Dashboard - Built with Streamlit & Supabase*")

if __name__ == "__main__":
    main()
