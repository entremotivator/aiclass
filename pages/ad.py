import streamlit as st
import os
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, timedelta
import json
import re
import hashlib
import uuid
from typing import Dict, List, Optional, Tuple
import plotly.express as px
import plotly.graph_objects as go

# Custom CSS for light green theme and card layouts
def load_custom_css():
    st.markdown("""
    <style>
    /* Main theme colors - Light Green */
    .main {
        background: linear-gradient(135deg, #e8f5e8 0%, #f1f8e9 100%);
    }
    
    .stApp {
        background: linear-gradient(135deg, #e8f5e8 0%, #f1f8e9 100%);
    }
    
    /* Card styling */
    .user-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #4caf50;
        transition: transform 0.2s ease;
    }
    
    .user-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    
    .admin-card {
        border-left-color: #ff9800;
        background: linear-gradient(135deg, #fff3e0 0%, #ffffff 100%);
    }
    
    .moderator-card {
        border-left-color: #9c27b0;
        background: linear-gradient(135deg, #f3e5f5 0%, #ffffff 100%);
    }
    
    .pending-card {
        border-left-color: #f44336;
        background: linear-gradient(135deg, #ffebee 0%, #ffffff 100%);
    }
    
    .premium-card {
        border-left-color: #ffc107;
        background: linear-gradient(135deg, #fffde7 0%, #ffffff 100%);
    }
    
    .stats-card {
        background: linear-gradient(135deg, #c8e6c9 0%, #ffffff 100%);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #a5d6a7;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2e7d32;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 5px;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #388e3c 0%, #2e7d32 100%);
        transform: translateY(-1px);
    }
    
    /* Approval buttons */
    .approve-btn {
        background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%) !important;
    }
    
    .reject-btn {
        background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%) !important;
    }
    
    .warning-btn {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%) !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #c8e6c9 0%, #e8f5e8 100%);
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: linear-gradient(135deg, #e8f5e8 0%, #ffffff 100%);
        border-left: 4px solid #4caf50;
    }
    
    .stError {
        background: linear-gradient(135deg, #ffebee 0%, #ffffff 100%);
        border-left: 4px solid #f44336;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #fff3e0 0%, #ffffff 100%);
        border-left: 4px solid #ff9800;
    }
    
    /* Form styling */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #c8e6c9;
        transition: border-color 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4caf50;
        box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #e8f5e8 0%, #ffffff 100%);
        border-radius: 8px;
        padding: 8px 16px;
        border: 1px solid #c8e6c9;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);
        color: white;
    }
    
    /* Feature cards */
    .feature-card {
        background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%);
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid #c8e6c9;
    }
    
    /* Activity indicators */
    .activity-high { color: #4caf50; font-weight: bold; }
    .activity-medium { color: #ff9800; font-weight: bold; }
    .activity-low { color: #f44336; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def init_service_client():
    """Initialize Supabase service role client with caching"""
    try:
        url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
        service_key = st.secrets.get("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not service_key:
            st.error("❌ Missing Supabase configuration. Please check your secrets.toml file.")
            st.stop()
        
        client = create_client(url, service_key)
        # Test connection with a simple query
        test_response = client.table("profiles").select("id").limit(1).execute()
        
        return client
        
    except Exception as e:
        st.error(f"❌ Failed to initialize service client: {str(e)}")
        st.stop()

def safe_date_format(date_string: str, format_str: str = '%Y-%m-%d') -> str:
    """Safely format date strings with error handling"""
    if not date_string:
        return "Not set"
    
    try:
        # Handle different date formats
        if 'T' in date_string:
            # ISO format with time
            if date_string.endswith('Z'):
                date_string = date_string.replace('Z', '+00:00')
            dt = datetime.fromisoformat(date_string)
        else:
            # Simple date format
            dt = datetime.strptime(date_string, '%Y-%m-%d')
        
        return dt.strftime(format_str)
    except (ValueError, TypeError) as e:
        return "Invalid date"

def get_all_users(supabase: Client) -> List[Dict]:
    """Get all users with comprehensive data from multiple tables"""
    try:
        # Get auth users with better error handling
        auth_response = supabase.auth.admin.list_users()
        
        # Handle different response formats from Supabase
        auth_users = []
        if hasattr(auth_response, 'data') and hasattr(auth_response.data, 'users'):
            auth_users = auth_response.data.users
        elif hasattr(auth_response, 'users'):
            auth_users = auth_response.users
        elif isinstance(auth_response, list):
            auth_users = auth_response
        else:
            st.warning("Unexpected auth response format. Please check your Supabase configuration.")
            return []
        
        # Get data from all user-related tables
        tables_data = {}
        
        # Core tables
        for table_name in ['profiles', 'user_roles', 'user_profiles', 'users', 'pending_signups']:
            try:
                response = supabase.table(table_name).select("*").execute()
                tables_data[table_name] = response.data if response.data else []
            except Exception as e:
                st.warning(f"Could not fetch {table_name}: {str(e)}")
                tables_data[table_name] = []
        
        # Additional feature tables
        for table_name in ['user_preferences', 'user_activity_logs', 'api_usage', 'chat_threads', 'file_uploads', 'custom_assistants']:
            try:
                response = supabase.table(table_name).select("*").execute()
                tables_data[table_name] = response.data if response.data else []
            except:
                tables_data[table_name] = []
        
        # Create lookup dictionaries
        profiles = {p['id']: p for p in tables_data['profiles']}
        user_roles = {r['user_id']: r['role'] for r in tables_data['user_roles']}
        user_profiles = {up['user_id']: up for up in tables_data['user_profiles']}
        users_table = {u['id']: u for u in tables_data['users']}
        pending_signups = {ps['email']: ps for ps in tables_data['pending_signups']}
        user_preferences = {up['user_id']: up for up in tables_data['user_preferences']}
        
        # Activity and usage data
        user_activity = {}
        for activity in tables_data['user_activity_logs']:
            user_id = activity['user_id']
            if user_id not in user_activity:
                user_activity[user_id] = []
            user_activity[user_id].append(activity)
        
        api_usage = {}
        for usage in tables_data['api_usage']:
            user_id = usage['user_id']
            if user_id not in api_usage:
                api_usage[user_id] = {'total_tokens': 0, 'total_cost': 0, 'requests': 0}
            api_usage[user_id]['total_tokens'] += usage.get('total_tokens', 0)
            api_usage[user_id]['total_cost'] += float(usage.get('cost', 0))
            api_usage[user_id]['requests'] += 1
        
        chat_threads_count = {}
        for thread in tables_data['chat_threads']:
            user_id = thread['user_id']
            chat_threads_count[user_id] = chat_threads_count.get(user_id, 0) + 1
        
        file_uploads_count = {}
        for file_upload in tables_data['file_uploads']:
            user_id = file_upload['user_id']
            file_uploads_count[user_id] = file_uploads_count.get(user_id, 0) + 1
        
        custom_assistants_count = {}
        for assistant in tables_data['custom_assistants']:
            user_id = assistant['user_id']
            custom_assistants_count[user_id] = custom_assistants_count.get(user_id, 0) + 1
        
        # Combine data with safer attribute access
        users = []
        for user in auth_users:
            try:
                # Safely get user attributes
                user_id = getattr(user, 'id', '')
                user_email = getattr(user, 'email', '')
                user_created_at = getattr(user, 'created_at', '')
                user_email_confirmed_at = getattr(user, 'email_confirmed_at', None)
                user_last_sign_in_at = getattr(user, 'last_sign_in_at', None)
                user_banned_until = getattr(user, 'banned_until', None)
                user_metadata = getattr(user, 'user_metadata', {}) or {}
                
                if not user_id or not user_email:
                    continue  # Skip invalid user records
                
                # Get data from various tables
                profile = profiles.get(user_id, {})
                user_profile = user_profiles.get(user_id, {})
                user_table_data = users_table.get(user_id, {})
                role = user_roles.get(user_id, profile.get('role', user_profile.get('role', 'user')))
                pending_signup = pending_signups.get(user_email, {})
                preferences = user_preferences.get(user_id, {})
                
                # Calculate user activity score
                activity_score = calculate_activity_score(user_last_sign_in_at)
                
                # Determine if user is pending approval
                is_pending = pending_signup.get('status') == 'pending' or user_profile.get('status') == 'pending'
                
                # Get usage statistics
                usage_stats = api_usage.get(user_id, {'total_tokens': 0, 'total_cost': 0, 'requests': 0})
                
                users.append({
                    'id': user_id,
                    'email': user_email,
                    'created_at': user_created_at,
                    'email_confirmed_at': user_email_confirmed_at,
                    'last_sign_in_at': user_last_sign_in_at,
                    'role': role,
                    'full_name': profile.get('full_name', user_profile.get('full_name', '')),
                    'avatar_url': profile.get('avatar_url', ''),
                    'website': profile.get('website', ''),
                    'username': profile.get('username', ''),
                    'updated_at': profile.get('updated_at', user_profile.get('created_at', '')),
                    'activity_score': activity_score,
                    'pending_approval': is_pending,
                    'approval_status': pending_signup.get('status', user_profile.get('status', 'approved')),
                    'is_active': not user_banned_until and user_table_data.get('is_active', True),
                    'metadata': user_metadata,
                    'subscription_tier': user_table_data.get('subscription_tier', 'free'),
                    'tokens_used': user_table_data.get('tokens_used_this_month', usage_stats['total_tokens']),
                    'total_cost': float(user_table_data.get('total_cost', usage_stats['total_cost'])),
                    'last_login': user_table_data.get('last_login', user_last_sign_in_at),
                    'monthly_token_limit': user_table_data.get('monthly_token_limit', 10000),
                    'max_files': user_table_data.get('max_files', 5),
                    'max_threads': user_table_data.get('max_threads', 10),
                    'voice_enabled': user_table_data.get('voice_enabled', False),
                    'advanced_features': user_table_data.get('advanced_features', False),
                    'stripe_customer_id': user_table_data.get('stripe_customer_id', ''),
                    'subscription_status': user_table_data.get('subscription_status', 'active'),
                    'subscription_start_date': user_table_data.get('subscription_start_date', ''),
                    'subscription_end_date': user_table_data.get('subscription_end_date', ''),
                    # Preferences
                    'theme': preferences.get('theme', 'light'),
                    'language': preferences.get('language', 'en'),
                    'notifications': preferences.get('notifications', True),
                    'email_notifications': preferences.get('email_notifications', True),
                    # Activity and usage
                    'activity_logs_count': len(user_activity.get(user_id, [])),
                    'api_requests': usage_stats['requests'],
                    'chat_threads_count': chat_threads_count.get(user_id, 0),
                    'file_uploads_count': file_uploads_count.get(user_id, 0),
                    'custom_assistants_count': custom_assistants_count.get(user_id, 0),
                    # Recent activity
                    'recent_activities': user_activity.get(user_id, [])[-5:] if user_activity.get(user_id) else []
                })
            except Exception as user_error:
                st.warning(f"Skipping user due to error: {str(user_error)}")
                continue
        
        return users
        
    except Exception as e:
        st.error(f"❌ Error fetching users: {str(e)}")
        return []

def calculate_activity_score(last_sign_in: str) -> str:
    """Calculate user activity score based on last sign in"""
    if not last_sign_in:
        return "Never"
    
    try:
        if 'T' in last_sign_in:
            if last_sign_in.endswith('Z'):
                last_sign_in = last_sign_in.replace('Z', '+00:00')
            last_login = datetime.fromisoformat(last_sign_in)
        else:
            last_login = datetime.strptime(last_sign_in, '%Y-%m-%d')
        
        now = datetime.now(last_login.tzinfo) if last_login.tzinfo else datetime.now()
        days_ago = (now - last_login).days
        
        if days_ago == 0:
            return "Today"
        elif days_ago == 1:
            return "Yesterday"
        elif days_ago <= 7:
            return f"{days_ago} days ago"
        elif days_ago <= 30:
            return f"{days_ago // 7} weeks ago"
        elif days_ago <= 365:
            return f"{days_ago // 30} months ago"
        else:
            return f"{days_ago // 365} years ago"
    except:
        return "Unknown"

def get_activity_class(activity_score: str) -> str:
    """Get CSS class for activity level"""
    if activity_score in ["Today", "Yesterday"]:
        return "activity-high"
    elif "days ago" in activity_score or "1 weeks ago" in activity_score:
        return "activity-medium"
    else:
        return "activity-low"

def render_user_card(user: Dict, key_suffix: str = ""):
    """Render a comprehensive user card with all information and action buttons"""
    # Determine card class based on user type
    card_class = "user-card"
    if user['role'] == 'admin':
        card_class += " admin-card"
    elif user['role'] == 'moderator':
        card_class += " moderator-card"
    elif user['pending_approval']:
        card_class += " pending-card"
    elif user['subscription_tier'] in ['pro', 'enterprise']:
        card_class += " premium-card"
    
    with st.container():
        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
        
        # Main card content
        col1, col2, col3, col4 = st.columns([3, 2, 2, 3])
        
        with col1:
            # User basic info
            display_name = user['full_name'] or user['username'] or 'No Name'
            st.markdown(f"**👤 {display_name}**")
            st.markdown(f"📧 {user['email']}")
            
            if user['website']:
                st.markdown(f"🌐 [Website]({user['website']})")
            
            # Subscription info with enhanced details
            tier_emoji = {"free": "🆓", "pro": "⭐", "enterprise": "💎"}.get(user['subscription_tier'], "🆓")
            st.markdown(f"{tier_emoji} **{user['subscription_tier'].title()}**")
            
            # Subscription status
            if user['subscription_status'] != 'active':
                st.markdown(f"⚠️ Status: {user['subscription_status']}")
        
        with col2:
            # Role and permissions
            role_emoji = "👑" if user['role'] == 'admin' else "🛡️" if user['role'] == 'moderator' else "👤"
            st.markdown(f"{role_emoji} **{user['role'].title()}**")
            
            # Account status
            status_emoji = "✅" if user['is_active'] else "❌"
            status_text = "Active" if user['is_active'] else "Inactive"
            st.markdown(f"{status_emoji} {status_text}")
            
            # Email verification
            if user['email_confirmed_at']:
                st.markdown("✉️ Email Verified")
            else:
                st.markdown("⚠️ Email Unverified")
            
            # Feature flags
            if user['voice_enabled']:
                st.markdown("🎤 Voice Enabled")
            if user['advanced_features']:
                st.markdown("🚀 Advanced Features")
        
        with col3:
            # Activity and usage with enhanced styling
            activity_class = get_activity_class(user['activity_score'])
            st.markdown(f"🕒 **Last Active:** <span class='{activity_class}'>{user['activity_score']}</span>", unsafe_allow_html=True)
            
            created_date = safe_date_format(user['created_at'])
            st.markdown(f"📅 **Joined:** {created_date}")
            
            # Usage statistics
            if user['tokens_used'] > 0:
                usage_percent = (user['tokens_used'] / user['monthly_token_limit']) * 100
                st.markdown(f"🎯 **Tokens:** {user['tokens_used']:,}/{user['monthly_token_limit']:,} ({usage_percent:.1f}%)")
            
            if user['total_cost'] > 0:
                st.markdown(f"💰 **Cost:** ${user['total_cost']:.4f}")
            
            if user['pending_approval']:
                st.markdown(f"⏳ **Status:** {user['approval_status']}")
        
        with col4:
            # Enhanced action buttons
            if user['pending_approval']:
                col4a, col4b = st.columns(2)
                with col4a:
                    if st.button("✅ Approve", key=f"approve_{user['id']}_{key_suffix}", help="Approve pending request"):
                        approve_user_request(user['id'], user['email'])
                        st.rerun()
                with col4b:
                    if st.button("❌ Reject", key=f"reject_{user['id']}_{key_suffix}", help="Reject pending request"):
                        reject_user_request(user['id'], user['email'])
                        st.rerun()
            else:
                col4a, col4b = st.columns(2)
                with col4a:
                    if st.button("✏️ Edit", key=f"edit_{user['id']}_{key_suffix}", help="Edit user details"):
                        st.session_state[f'editing_user_{user["id"]}'] = True
                        st.rerun()
                with col4b:
                    if st.button("📊 Details", key=f"details_{user['id']}_{key_suffix}", help="View detailed analytics"):
                        st.session_state[f'viewing_details_{user["id"]}'] = True
                        st.rerun()
        
        # Enhanced expandable details section
        with st.expander(f"📋 Comprehensive Details for {user['email']}", expanded=False):
            detail_tab1, detail_tab2, detail_tab3, detail_tab4 = st.tabs(["👤 Profile", "📊 Usage", "🎛️ Settings", "📈 Activity"])
            
            with detail_tab1:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Basic Information:**")
                    st.write(f"• **User ID:** {user['id']}")
                    st.write(f"• **Username:** {user['username'] or 'Not set'}")
                    st.write(f"• **Full Name:** {user['full_name'] or 'Not set'}")
                    st.write(f"• **Email:** {user['email']}")
                    if user['avatar_url']:
                        st.write(f"• **Avatar:** [View]({user['avatar_url']})")
                
                with col2:
                    st.markdown("**Account Details:**")
                    st.write(f"• **Role:** {user['role']}")
                    st.write(f"• **Subscription:** {user['subscription_tier']}")
                    st.write(f"• **Status:** {user['subscription_status']}")
                    if user['stripe_customer_id']:
                        st.write(f"• **Stripe ID:** {user['stripe_customer_id']}")
                    
                    updated_date = safe_date_format(user['updated_at'], '%Y-%m-%d %H:%M')
                    st.write(f"• **Last Updated:** {updated_date}")
            
            with detail_tab2:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Usage Statistics:**")
                    st.write(f"• **Tokens Used:** {user['tokens_used']:,}")
                    st.write(f"• **Monthly Limit:** {user['monthly_token_limit']:,}")
                    st.write(f"• **Total Cost:** ${user['total_cost']:.4f}")
                    st.write(f"• **API Requests:** {user['api_requests']:,}")
                
                with col2:
                    st.markdown("**Content & Features:**")
                    st.write(f"• **Chat Threads:** {user['chat_threads_count']}")
                    st.write(f"• **File Uploads:** {user['file_uploads_count']}")
                    st.write(f"• **Custom Assistants:** {user['custom_assistants_count']}")
                    st.write(f"• **Activity Logs:** {user['activity_logs_count']}")
            
            with detail_tab3:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Preferences:**")
                    st.write(f"• **Theme:** {user['theme']}")
                    st.write(f"• **Language:** {user['language']}")
                    st.write(f"• **Notifications:** {'Enabled' if user['notifications'] else 'Disabled'}")
                    st.write(f"• **Email Notifications:** {'Enabled' if user['email_notifications'] else 'Disabled'}")
                
                with col2:
                    st.markdown("**Limits & Features:**")
                    st.write(f"• **Max Files:** {user['max_files']}")
                    st.write(f"• **Max Threads:** {user['max_threads']}")
                    st.write(f"• **Voice Enabled:** {'Yes' if user['voice_enabled'] else 'No'}")
                    st.write(f"• **Advanced Features:** {'Yes' if user['advanced_features'] else 'No'}")
            
            with detail_tab4:
                st.markdown("**Recent Activity:**")
                if user['recent_activities']:
                    for activity in user['recent_activities']:
                        activity_date = safe_date_format(activity.get('created_at', ''), '%Y-%m-%d %H:%M')
                        st.write(f"• **{activity.get('activity_type', 'Unknown')}** - {activity.get('description', 'No description')} ({activity_date})")
                else:
                    st.write("No recent activity recorded")
                
                if user['metadata']:
                    st.markdown("**User Metadata:**")
                    for key, value in user['metadata'].items():
                        st.write(f"• **{key}:** {value}")
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_stats_dashboard(users: List[Dict]):
    """Render comprehensive statistics dashboard with enhanced analytics"""
    st.markdown("## 📊 Comprehensive User Analytics Dashboard")
    
    # Calculate comprehensive statistics
    total_users = len(users)
    admin_users = len([u for u in users if u['role'] == 'admin'])
    moderator_users = len([u for u in users if u['role'] == 'moderator'])
    active_users = len([u for u in users if u['is_active']])
    verified_users = len([u for u in users if u['email_confirmed_at']])
    pending_approvals = len([u for u in users if u['pending_approval']])
    
    # Subscription stats
    free_users = len([u for u in users if u['subscription_tier'] == 'free'])
    pro_users = len([u for u in users if u['subscription_tier'] == 'pro'])
    enterprise_users = len([u for u in users if u['subscription_tier'] == 'enterprise'])
    
    # Feature usage stats
    voice_enabled_users = len([u for u in users if u['voice_enabled']])
    advanced_features_users = len([u for u in users if u['advanced_features']])
    
    # Activity stats
    active_today = len([u for u in users if u['activity_score'] == "Today"])
    active_week = len([u for u in users if u['activity_score'] in ["Today", "Yesterday"] or "days ago" in u['activity_score']])
    
    # Revenue and usage
    total_revenue = sum([u['total_cost'] for u in users])
    total_tokens = sum([u['tokens_used'] for u in users])
    total_api_requests = sum([u['api_requests'] for u in users])
    
    # Main stats cards
    st.markdown("### 📈 Key Metrics")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <div class="metric-value">{total_users}</div>
            <div class="metric-label">Total Users</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stats-card">
            <div class="metric-value">{admin_users}</div>
            <div class="metric-label">Admins</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stats-card">
            <div class="metric-value">{active_users}</div>
            <div class="metric-label">Active</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stats-card">
            <div class="metric-value">{verified_users}</div>
            <div class="metric-label">Verified</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="stats-card">
            <div class="metric-value">{pending_approvals}</div>
            <div class="metric-label">Pending</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown(f"""
        <div class="stats-card">
            <div class="metric-value">{active_today}</div>
            <div class="metric-label">Active Today</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Subscription and revenue stats
    st.markdown("### 💰 Subscription & Revenue Analytics")
    col7, col8, col9, col10, col11, col12 = st.columns(6)
    
    with col7:
        st.markdown(f"""
        <div class="stats-card">
            <div class="metric-value">{free_users}</div>
            <div class="metric-label">Free Users</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col8:
        st.markdown(f"""
        <div class="stats-card">
            <div class="metric-value">{pro_users}</div>
            <div class="metric-label">Pro Users</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col9:
        st.markdown(f"""
        <div class="stats-card">
            <div class="metric-value">{enterprise_users}</div>
            <div class="metric-label">Enterprise</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col10:
        st.markdown(f"""
        <div class="stats-card">
            <div class="metric-value">${total_revenue:.0f}</div>
            <div class="metric-label">Total Revenue</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col11:
        st.markdown(f"""
        <div class="stats-card">
            <div class="metric-value">{total_tokens:,}</div>
            <div class="metric-label">Total Tokens</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col12:
        st.markdown(f"""
        <div class="stats-card">
            <div class="metric-value">{total_api_requests:,}</div>
            <div class="metric-label">API Requests</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Feature usage stats
    st.markdown("### 🚀 Feature Usage")
    col13, col14, col15, col16 = st.columns(4)
    
    with col13:
        st.markdown(f"""
        <div class="stats-card">
            <div class="metric-value">{voice_enabled_users}</div>
            <div class="metric-label">Voice Enabled</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col14:
        st.markdown(f"""
        <div class="stats-card">
            <div class="metric-value">{advanced_features_users}</div>
            <div class="metric-label">Advanced Features</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col15:
        total_chat_threads = sum([u['chat_threads_count'] for u in users])
        st.markdown(f"""
        <div class="stats-card">
            <div class="metric-value">{total_chat_threads}</div>
            <div class="metric-label">Chat Threads</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col16:
        total_file_uploads = sum([u['file_uploads_count'] for u in users])
        st.markdown(f"""
        <div class="stats-card">
            <div class="metric-value">{total_file_uploads}</div>
            <div class="metric-label">File Uploads</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts section
    if users:
        st.markdown("### 📊 Visual Analytics")
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Role distribution pie chart
            role_counts = {}
            for user in users:
                role = user['role']
                role_counts[role] = role_counts.get(role, 0) + 1
            
            fig_roles = px.pie(
                values=list(role_counts.values()),
                names=list(role_counts.keys()),
                title="User Role Distribution",
                color_discrete_sequence=['#4caf50', '#ff9800', '#9c27b0', '#f44336']
            )
            fig_roles.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333')
            )
            st.plotly_chart(fig_roles, use_container_width=True)
        
        with chart_col2:
            # Subscription tier distribution
            tier_counts = {'free': free_users, 'pro': pro_users, 'enterprise': enterprise_users}
            
            fig_tiers = px.bar(
                x=list(tier_counts.keys()),
                y=list(tier_counts.values()),
                title="Subscription Tier Distribution",
                color=list(tier_counts.keys()),
                color_discrete_sequence=['#4caf50', '#ff9800', '#9c27b0']
            )
            fig_tiers.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333'),
                xaxis_title="Subscription Tier",
                yaxis_title="Number of Users"
            )
            st.plotly_chart(fig_tiers, use_container_width=True)
        
        # Activity and usage charts
        chart_col3, chart_col4 = st.columns(2)
        
        with chart_col3:
            # Activity distribution
            activity_counts = {}
            for user in users:
                activity = user['activity_score']
                if activity == "Today":
                    activity_counts['Today'] = activity_counts.get('Today', 0) + 1
                elif activity == "Yesterday":
                    activity_counts['Yesterday'] = activity_counts.get('Yesterday', 0) + 1
                elif "days ago" in activity:
                    activity_counts['This Week'] = activity_counts.get('This Week', 0) + 1
                elif "weeks ago" in activity:
                    activity_counts['This Month'] = activity_counts.get('This Month', 0) + 1
                else:
                    activity_counts['Inactive'] = activity_counts.get('Inactive', 0) + 1
            
            fig_activity = px.bar(
                x=list(activity_counts.keys()),
                y=list(activity_counts.values()),
                title="User Activity Distribution",
                color=list(activity_counts.values()),
                color_continuous_scale='Greens'
            )
            fig_activity.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333'),
                xaxis_title="Activity Period",
                yaxis_title="Number of Users"
            )
            st.plotly_chart(fig_activity, use_container_width=True)
        
        with chart_col4:
            # Token usage distribution
            usage_ranges = {'0': 0, '1-1000': 0, '1001-5000': 0, '5001-10000': 0, '10000+': 0}
            for user in users:
                tokens = user['tokens_used']
                if tokens == 0:
                    usage_ranges['0'] += 1
                elif tokens <= 1000:
                    usage_ranges['1-1000'] += 1
                elif tokens <= 5000:
                    usage_ranges['1001-5000'] += 1
                elif tokens <= 10000:
                    usage_ranges['5001-10000'] += 1
                else:
                    usage_ranges['10000+'] += 1
            
            fig_usage = px.bar(
                x=list(usage_ranges.keys()),
                y=list(usage_ranges.values()),
                title="Token Usage Distribution",
                color=list(usage_ranges.values()),
                color_continuous_scale='Greens'
            )
            fig_usage.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333'),
                xaxis_title="Token Usage Range",
                yaxis_title="Number of Users"
            )
            st.plotly_chart(fig_usage, use_container_width=True)

# Additional functions for user management operations
def approve_user_request(user_id: str, email: str):
    """Approve a pending user request"""
    try:
        supabase = init_service_client()
        
        # Update pending_signups table
        supabase.table("pending_signups").update({
            "status": "approved",
            "updated_at": datetime.now().isoformat()
        }).eq("email", email).execute()
        
        # Update user_profiles table
        supabase.table("user_profiles").update({
            "status": "approved"
        }).eq("user_id", user_id).execute()
        
        st.success(f"✅ Approved user request for {email}")
    except Exception as e:
        st.error(f"Error approving user: {str(e)}")

def reject_user_request(user_id: str, email: str):
    """Reject a pending user request"""
    try:
        supabase = init_service_client()
        
        # Update pending_signups table
        supabase.table("pending_signups").update({
            "status": "rejected",
            "updated_at": datetime.now().isoformat()
        }).eq("email", email).execute()
        
        # Update user_profiles table
        supabase.table("user_profiles").update({
            "status": "rejected"
        }).eq("user_id", user_id).execute()
        
        st.success(f"❌ Rejected user request for {email}")
    except Exception as e:
        st.error(f"Error rejecting user: {str(e)}")

def main():
    st.set_page_config(
        page_title="Admin Dashboard - User Management",
        page_icon="👑",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load custom CSS
    load_custom_css()
    
    st.title("👑 Admin Dashboard - Advanced User Management")
    st.markdown("Comprehensive user administration with enhanced analytics and card-based interface")
    
    # Initialize service client
    supabase = init_service_client()
    
    # Sidebar navigation
    st.sidebar.title("🎛️ Admin Navigation")
    
    # Main tabs
    tab = st.sidebar.selectbox("Choose Section", [
        "📊 Dashboard & Analytics",
        "👥 User Management",
        "⏳ Pending Approvals", 
        "➕ Create Admin User",
        "⬆️ Promote User",
        "🔧 Bulk Operations",
        "📤 Export Data",
        "🔍 Advanced Search",
        "⚙️ System Settings"
    ])
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_resource.clear()
        st.rerun()
    
    # Get users data with progress indicator
    with st.spinner("Loading user data..."):
        users = get_all_users(supabase)
    
    if not users:
        st.warning("No users found or error loading data. Please check your database connection.")
        return
    
    # Main content based on selected tab
    if tab == "📊 Dashboard & Analytics":
        render_stats_dashboard(users)
        
        st.markdown("---")
        st.markdown("## 📈 Recent Activity & Top Users")
        
        # Show recent users and top users
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🆕 Recently Registered Users")
            recent_users = sorted(users, key=lambda x: x['created_at'], reverse=True)[:3]
            for user in recent_users:
                render_user_card(user, "recent")
        
        with col2:
            st.markdown("### 💎 Top Users by Usage")
            top_users = sorted(users, key=lambda x: x['total_cost'], reverse=True)[:3]
            for user in top_users:
                render_user_card(user, "top")
    
    elif tab == "👥 User Management":
        st.markdown("## 👥 Comprehensive User Management")
        
        # Enhanced filters
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            role_filter = st.selectbox("Filter by Role", ["All", "admin", "user", "moderator"])
        with col2:
            status_filter = st.selectbox("Filter by Status", ["All", "Active", "Inactive"])
        with col3:
            tier_filter = st.selectbox("Subscription Tier", ["All", "free", "pro", "enterprise"])
        with col4:
            activity_filter = st.selectbox("Activity Level", ["All", "Active Today", "Active This Week", "Inactive"])
        with col5:
            search_term = st.text_input("🔍 Search users...")
        
        # Apply filters
        filtered_users = users
        
        if role_filter != "All":
            filtered_users = [u for u in filtered_users if u['role'] == role_filter]
        
        if status_filter != "All":
            is_active = status_filter == "Active"
            filtered_users = [u for u in filtered_users if u['is_active'] == is_active]
        
        if tier_filter != "All":
            filtered_users = [u for u in filtered_users if u['subscription_tier'] == tier_filter]
        
        if activity_filter != "All":
            if activity_filter == "Active Today":
                filtered_users = [u for u in filtered_users if u['activity_score'] == "Today"]
            elif activity_filter == "Active This Week":
                filtered_users = [u for u in filtered_users if u['activity_score'] in ["Today", "Yesterday"] or "days ago" in u['activity_score']]
            elif activity_filter == "Inactive":
                filtered_users = [u for u in filtered_users if u['activity_score'] in ["Never"] or "months ago" in u['activity_score'] or "years ago" in u['activity_score']]
        
        if search_term:
            filtered_users = [u for u in filtered_users 
                            if search_term.lower() in u['email'].lower() 
                            or search_term.lower() in u.get('full_name', '').lower()
                            or search_term.lower() in u.get('username', '').lower()]
        
        st.markdown(f"**Showing {len(filtered_users)} of {len(users)} users**")
        
        # Pagination for large datasets
        users_per_page = 10
        total_pages = (len(filtered_users) + users_per_page - 1) // users_per_page
        
        if total_pages > 1:
            page = st.selectbox("Page", range(1, total_pages + 1))
            start_idx = (page - 1) * users_per_page
            end_idx = start_idx + users_per_page
            paginated_users = filtered_users[start_idx:end_idx]
        else:
            paginated_users = filtered_users
        
        # Show user cards
        for user in paginated_users:
            render_user_card(user, "main")
    
    elif tab == "⏳ Pending Approvals":
        st.markdown("## ⏳ Pending Approvals Management")
        
        pending_users = [u for u in users if u['pending_approval']]
        
        if pending_users:
            st.markdown(f"**{len(pending_users)} users awaiting approval**")
            
            for user in pending_users:
                render_user_card(user, "pending")
        else:
            st.success("🎉 No pending approvals!")
    
    # Additional tabs would be implemented here...
    
    # Footer
    st.markdown("---")
    st.markdown("*Advanced User Management System - Admin Dashboard - Built with Streamlit & Supabase*")

if __name__ == "__main__":
    main()
