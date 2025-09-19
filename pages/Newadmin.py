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

# Custom CSS for light blue theme and card layouts
def load_custom_css():
    st.markdown("""
    <style>
    /* Main theme colors */
    .main {
        background: linear-gradient(135deg, #e3f2fd 0%, #f8f9fa 100%);
    }
    
    .stApp {
        background: linear-gradient(135deg, #e3f2fd 0%, #f8f9fa 100%);
    }
    
    /* Card styling */
    .user-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #2196f3;
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
    
    .pending-card {
        border-left-color: #f44336;
        background: linear-gradient(135deg, #ffebee 0%, #ffffff 100%);
    }
    
    .stats-card {
        background: linear-gradient(135deg, #bbdefb 0%, #ffffff 100%);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1976d2;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 5px;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
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
        background: linear-gradient(180deg, #bbdefb 0%, #e3f2fd 100%);
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
        border: 2px solid #e0e0e0;
        transition: border-color 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2196f3;
        box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #e3f2fd 0%, #ffffff 100%);
        border-radius: 8px;
        padding: 8px 16px;
        border: 1px solid #e0e0e0;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
        color: white;
    }
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

def get_all_users(supabase: Client) -> List[Dict]:
    """Get all users with profiles, roles, and additional metadata"""
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
        
        # Get profiles from the actual profiles table
        profiles_response = supabase.table("profiles").select("*").execute()
        profiles = {p['id']: p for p in profiles_response.data} if profiles_response.data else {}
        
        # Get user roles
        roles_response = supabase.table("user_roles").select("*").execute()
        user_roles = {r['user_id']: r['role'] for r in roles_response.data} if roles_response.data else {}
        
        # Get user profiles (additional table)
        user_profiles_response = supabase.table("user_profiles").select("*").execute()
        user_profiles = {up['user_id']: up for up in user_profiles_response.data} if user_profiles_response.data else {}
        
        # Get pending signups for approval workflow
        try:
            pending_signups_response = supabase.table("pending_signups").select("*").execute()
            pending_signups = {ps['email']: ps for ps in pending_signups_response.data} if pending_signups_response.data else {}
        except:
            pending_signups = {}
        
        # Get users table data for additional info
        try:
            users_table_response = supabase.table("users").select("*").execute()
            users_table = {u['id']: u for u in users_table_response.data} if users_table_response.data else {}
        except:
            users_table = {}
        
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
                
                # Calculate user activity score
                activity_score = calculate_activity_score(user_last_sign_in_at)
                
                # Determine if user is pending approval
                is_pending = pending_signup.get('status') == 'pending' or user_profile.get('status') == 'pending'
                
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
                    'tokens_used': user_table_data.get('tokens_used_this_month', 0),
                    'total_cost': float(user_table_data.get('total_cost', 0)),
                    'last_login': user_table_data.get('last_login', user_last_sign_in_at)
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
        last_login = datetime.fromisoformat(last_sign_in.replace('Z', '+00:00'))
        now = datetime.now(last_login.tzinfo)
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

def render_user_card(user: Dict, key_suffix: str = ""):
    """Render a user card with all information and action buttons"""
    card_class = "user-card"
    if user['role'] == 'admin':
        card_class += " admin-card"
    elif user['pending_approval']:
        card_class += " pending-card"
    
    with st.container():
        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns([3, 2, 2, 3])
        
        with col1:
            # User basic info
            display_name = user['full_name'] or user['username'] or 'No Name'
            st.markdown(f"**👤 {display_name}**")
            st.markdown(f"📧 {user['email']}")
            if user['website']:
                st.markdown(f"🌐 [Website]({user['website']})")
            
            # Subscription info
            tier_emoji = {"free": "🆓", "pro": "⭐", "enterprise": "💎"}.get(user['subscription_tier'], "🆓")
            st.markdown(f"{tier_emoji} {user['subscription_tier'].title()}")
        
        with col2:
            # Role and status
            role_emoji = "👑" if user['role'] == 'admin' else "🛡️" if user['role'] == 'moderator' else "👤"
            st.markdown(f"{role_emoji} **{user['role'].title()}**")
            
            status_emoji = "✅" if user['is_active'] else "❌"
            status_text = "Active" if user['is_active'] else "Inactive"
            st.markdown(f"{status_emoji} {status_text}")
            
            if user['email_confirmed_at']:
                st.markdown("✉️ Email Verified")
            else:
                st.markdown("⚠️ Email Unverified")
        
        with col3:
            # Activity and usage
            st.markdown(f"🕒 **Last Active:** {user['activity_score']}")
            created_date = datetime.fromisoformat(user['created_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d')
            st.markdown(f"📅 **Joined:** {created_date}")
            
            if user['tokens_used'] > 0:
                st.markdown(f"🎯 **Tokens Used:** {user['tokens_used']:,}")
            
            if user['pending_approval']:
                st.markdown(f"⏳ **Status:** {user['approval_status']}")
        
        with col4:
            # Action buttons
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
                if st.button("✏️ Edit", key=f"edit_{user['id']}_{key_suffix}", help="Edit user details"):
                    st.session_state[f'editing_user_{user["id"]}'] = True
                    st.rerun()
        
        # Expandable details section
        with st.expander(f"📋 Details for {user['email']}", expanded=False):
            detail_col1, detail_col2 = st.columns(2)
            
            with detail_col1:
                st.markdown("**Profile Information:**")
                st.write(f"• **User ID:** {user['id']}")
                st.write(f"• **Username:** {user['username'] or 'Not set'}")
                st.write(f"• **Subscription:** {user['subscription_tier'].title()}")
                if user['avatar_url']:
                    st.write(f"• **Avatar:** [View]({user['avatar_url']})")
                st.write(f"• **Total Cost:** ${user['total_cost']:.4f}")
            
            with detail_col2:
                st.markdown("**Account Information:**")
                if user['updated_at']:
                    try:
                        updated_date = datetime.fromisoformat(user['updated_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
                        st.write(f"• **Last Updated:** {updated_date}")
                    except:
                        st.write(f"• **Last Updated:** {user['updated_at']}")
                
                if user['metadata']:
                    st.write("• **Metadata:**")
                    for key, value in user['metadata'].items():
                        st.write(f"  - {key}: {value}")
                
                if user['last_login'] and user['last_login'] != user['last_sign_in_at']:
                    try:
                        login_date = datetime.fromisoformat(user['last_login'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
                        st.write(f"• **Last Login:** {login_date}")
                    except:
                        st.write(f"• **Last Login:** {user['last_login']}")
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_stats_dashboard(users: List[Dict]):
    """Render statistics dashboard with cards"""
    st.markdown("## 📊 User Analytics Dashboard")
    
    # Calculate statistics
    total_users = len(users)
    admin_users = len([u for u in users if u['role'] == 'admin'])
    active_users = len([u for u in users if u['is_active']])
    verified_users = len([u for u in users if u['email_confirmed_at']])
    pending_approvals = len([u for u in users if u['pending_approval']])
    
    # Subscription stats
    pro_users = len([u for u in users if u['subscription_tier'] == 'pro'])
    enterprise_users = len([u for u in users if u['subscription_tier'] == 'enterprise'])
    
    # Recent activity (last 7 days)
    recent_active = len([u for u in users if u['activity_score'] in ['Today', 'Yesterday'] or 'days ago' in u['activity_score']])
    
    # Stats cards
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
            <div class="metric-value">{recent_active}</div>
            <div class="metric-label">Recent Active</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Additional stats row
    st.markdown("### 💰 Subscription Analytics")
    col7, col8, col9, col10 = st.columns(4)
    
    with col7:
        free_users = total_users - pro_users - enterprise_users
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
        total_revenue = sum([u['total_cost'] for u in users])
        st.markdown(f"""
        <div class="stats-card">
            <div class="metric-value">${total_revenue:.0f}</div>
            <div class="metric-label">Total Revenue</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    if users:
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
                color_discrete_sequence=['#2196f3', '#ff9800', '#4caf50', '#f44336']
            )
            fig_roles.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333')
            )
            st.plotly_chart(fig_roles, use_container_width=True)
        
        with chart_col2:
            # Subscription tier distribution
            tier_counts = {}
            for user in users:
                tier = user['subscription_tier']
                tier_counts[tier] = tier_counts.get(tier, 0) + 1
            
            fig_tiers = px.bar(
                x=list(tier_counts.keys()),
                y=list(tier_counts.values()),
                title="Subscription Tier Distribution",
                color=list(tier_counts.keys()),
                color_discrete_sequence=['#2196f3', '#ff9800', '#4caf50']
            )
            fig_tiers.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333'),
                xaxis_title="Subscription Tier",
                yaxis_title="Number of Users"
            )
            st.plotly_chart(fig_tiers, use_container_width=True)

def render_user_editor(user: Dict, supabase: Client):
    """Render user editing form"""
    st.markdown(f"## ✏️ Editing User: {user['email']}")
    
    with st.form(f"edit_user_{user['id']}"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Basic Information**")
            new_email = st.text_input("Email", value=user['email'])
            new_full_name = st.text_input("Full Name", value=user['full_name'])
            new_username = st.text_input("Username", value=user['username'])
            new_website = st.text_input("Website", value=user['website'])
            new_avatar_url = st.text_input("Avatar URL", value=user['avatar_url'])
        
        with col2:
            st.markdown("**Settings & Permissions**")
            new_role = st.selectbox("Role", options=['user', 'admin', 'moderator'], index=['user', 'admin', 'moderator'].index(user['role']) if user['role'] in ['user', 'admin', 'moderator'] else 0)
            new_subscription_tier = st.selectbox("Subscription Tier", options=['free', 'pro', 'enterprise'], index=['free', 'pro', 'enterprise'].index(user['subscription_tier']) if user['subscription_tier'] in ['free', 'pro', 'enterprise'] else 0)
            new_active = st.checkbox("Account Active", value=user['is_active'])
            new_verified = st.checkbox("Email Verified", value=bool(user['email_confirmed_at']))
        
        st.markdown("**Actions**")
        col_save, col_cancel, col_reset_pwd, col_delete = st.columns(4)
        
        with col_save:
            save_changes = st.form_submit_button("💾 Save Changes", type="primary")
        
        with col_cancel:
            cancel_edit = st.form_submit_button("❌ Cancel")
        
        with col_reset_pwd:
            reset_password = st.form_submit_button("🔑 Reset Password")
        
        with col_delete:
            delete_user = st.form_submit_button("🗑️ Delete User")
        
        if save_changes:
            success = update_user_profile(
                supabase, user['id'], new_email, new_full_name, new_username,
                new_website, new_avatar_url, new_role, new_subscription_tier,
                new_active, new_verified
            )
            if success:
                st.success("✅ User updated successfully!")
                del st.session_state[f'editing_user_{user["id"]}']
                st.rerun()
            else:
                st.error("❌ Failed to update user")
        
        if cancel_edit:
            del st.session_state[f'editing_user_{user["id"]}']
            st.rerun()
        
        if reset_password:
            new_password = generate_secure_password()
            if reset_user_password(supabase, user['id'], new_password):
                st.success(f"✅ Password reset successfully! New password: `{new_password}`")
            else:
                st.error("❌ Failed to reset password")
        
        if delete_user:
            st.warning("⚠️ Are you sure you want to delete this user? This action cannot be undone!")
            if st.button("🗑️ Confirm Delete", key=f"confirm_delete_{user['id']}"):
                if delete_user_account(supabase, user['id']):
                    st.success("✅ User deleted successfully!")
                    del st.session_state[f'editing_user_{user["id"]}']
                    st.rerun()
                else:
                    st.error("❌ Failed to delete user")

def update_user_profile(supabase: Client, user_id: str, email: str, full_name: str, 
                       username: str, website: str, avatar_url: str, role: str,
                       subscription_tier: str, is_active: bool, email_verified: bool) -> bool:
    """Update user profile and settings"""
    try:
        # Update auth user email if changed
        current_user_response = supabase.auth.admin.get_user_by_id(user_id)
        current_user = current_user_response.user if hasattr(current_user_response, 'user') else current_user_response
        
        current_email = getattr(current_user, 'email', '')
        if current_email != email:
            supabase.auth.admin.update_user_by_id(user_id, {"email": email})
        
        # Update email verification status
        current_email_confirmed = getattr(current_user, 'email_confirmed_at', None)
        if email_verified and not current_email_confirmed:
            supabase.auth.admin.update_user_by_id(user_id, {"email_confirm": True})
        
        # Update user active status
        if not is_active:
            supabase.auth.admin.update_user_by_id(user_id, {"ban_duration": "876000h"})  # 100 years
        else:
            supabase.auth.admin.update_user_by_id(user_id, {"ban_duration": "none"})
        
        # Update profiles table
        supabase.table("profiles").upsert({
            "id": user_id,
            "full_name": full_name,
            "username": username,
            "website": website,
            "avatar_url": avatar_url,
            "role": role,
            "updated_at": datetime.now().isoformat()
        }).execute()
        
        # Update user_roles table
        supabase.table("user_roles").upsert({
            "user_id": user_id,
            "role": role
        }).execute()
        
        # Update users table
        supabase.table("users").upsert({
            "id": user_id,
            "email": email,
            "subscription_tier": subscription_tier,
            "is_active": is_active,
            "updated_at": datetime.now().isoformat()
        }).execute()
        
        # Update user_profiles table
        supabase.table("user_profiles").upsert({
            "user_id": user_id,
            "email": email,
            "full_name": full_name,
            "role": role,
            "status": "approved" if is_active else "suspended"
        }).execute()
        
        return True
        
    except Exception as e:
        st.error(f"Error updating user: {str(e)}")
        return False

def generate_secure_password(length: int = 12) -> str:
    """Generate a secure random password"""
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

def reset_user_password(supabase: Client, user_id: str, new_password: str) -> bool:
    """Reset user password"""
    try:
        supabase.auth.admin.update_user_by_id(user_id, {"password": new_password})
        return True
    except Exception as e:
        st.error(f"Error resetting password: {str(e)}")
        return False

def delete_user_account(supabase: Client, user_id: str) -> bool:
    """Delete user account and related data"""
    try:
        # Delete from all related tables
        tables_to_clean = [
            "profiles", "user_roles", "user_profiles", "users",
            "user_preferences", "user_activity_logs", "user_sessions",
            "api_usage", "chat_threads", "file_uploads", "custom_assistants"
        ]
        
        for table in tables_to_clean:
            try:
                if table == "users":
                    supabase.table(table).delete().eq("id", user_id).execute()
                else:
                    supabase.table(table).delete().eq("user_id", user_id).execute()
            except:
                continue  # Some tables might not exist or have different structures
        
        # Delete auth user
        supabase.auth.admin.delete_user(user_id)
        
        return True
    except Exception as e:
        st.error(f"Error deleting user: {str(e)}")
        return False

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

def create_admin_user(supabase: Client, email: str, password: str, full_name: str = "") -> Tuple[bool, str]:
    """Create a new admin user"""
    try:
        user_response = supabase.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True
        })
        
        if user_response.user:
            user_id = user_response.user.id
            
            # Create profile
            supabase.table("profiles").insert({
                "id": user_id,
                "full_name": full_name,
                "role": "admin"
            }).execute()
            
            # Create user role entry
            supabase.table("user_roles").insert({
                "user_id": user_id,
                "role": "admin"
            }).execute()
            
            # Create user profile entry
            supabase.table("user_profiles").insert({
                "user_id": user_id,
                "email": email,
                "full_name": full_name,
                "role": "admin",
                "status": "approved"
            }).execute()
            
            # Create users table entry
            supabase.table("users").insert({
                "id": user_id,
                "email": email,
                "subscription_tier": "enterprise",
                "is_active": True
            }).execute()
            
            return True, f"Admin user created successfully: {email}"
        else:
            return False, "Failed to create user"
            
    except Exception as e:
        return False, f"Error creating admin user: {str(e)}"

def promote_user_to_admin(supabase: Client, email: str) -> Tuple[bool, str]:
    """Promote existing user to admin"""
    try:
        users = get_all_users(supabase)
        user = next((u for u in users if u['email'] == email), None)
        
        if not user:
            return False, "User not found"
        
        user_id = user['id']
        
        # Update all relevant tables
        supabase.table("profiles").upsert({
            "id": user_id,
            "role": "admin"
        }).execute()
        
        supabase.table("user_roles").upsert({
            "user_id": user_id,
            "role": "admin"
        }).execute()
        
        supabase.table("user_profiles").upsert({
            "user_id": user_id,
            "role": "admin"
        }).execute()
        
        return True, f"User {email} promoted to admin successfully"
        
    except Exception as e:
        return False, f"Error promoting user: {str(e)}"

def bulk_user_operations(supabase: Client, user_ids: List[str], operation: str) -> bool:
    """Perform bulk operations on multiple users"""
    try:
        if operation == "delete":
            for user_id in user_ids:
                delete_user_account(supabase, user_id)
        elif operation == "activate":
            for user_id in user_ids:
                supabase.auth.admin.update_user_by_id(user_id, {"ban_duration": "none"})
                supabase.table("users").update({"is_active": True}).eq("id", user_id).execute()
        elif operation == "deactivate":
            for user_id in user_ids:
                supabase.auth.admin.update_user_by_id(user_id, {"ban_duration": "876000h"})
                supabase.table("users").update({"is_active": False}).eq("id", user_id).execute()
        elif operation == "verify_email":
            for user_id in user_ids:
                supabase.auth.admin.update_user_by_id(user_id, {"email_confirm": True})
        
        return True
    except Exception as e:
        st.error(f"Error in bulk operation: {str(e)}")
        return False

def export_users_data(users: List[Dict]) -> pd.DataFrame:
    """Export users data to DataFrame for download"""
    export_data = []
    for user in users:
        export_data.append({
            'ID': user['id'],
            'Email': user['email'],
            'Full Name': user['full_name'],
            'Username': user['username'],
            'Role': user['role'],
            'Subscription Tier': user['subscription_tier'],
            'Active': user['is_active'],
            'Email Verified': bool(user['email_confirmed_at']),
            'Website': user['website'],
            'Created At': user['created_at'],
            'Last Sign In': user['last_sign_in_at'],
            'Activity Score': user['activity_score'],
            'Pending Approval': user['pending_approval'],
            'Approval Status': user['approval_status'],
            'Tokens Used': user['tokens_used'],
            'Total Cost': user['total_cost']
        })
    
    return pd.DataFrame(export_data)

def main():
    st.set_page_config(
        page_title="Advanced User Management System",
        page_icon="👑",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load custom CSS
    load_custom_css()
    
    st.title("👑 Advanced User Management System")
    st.markdown("Comprehensive user administration with card-based interface and approval workflows")
    
    # Initialize service client
    supabase = init_service_client()
    
    # Sidebar navigation
    st.sidebar.title("🎛️ Navigation")
    
    # Main tabs
    tab = st.sidebar.selectbox("Choose Section", [
        "📊 Dashboard & Analytics",
        "👥 User Management",
        "⏳ Pending Approvals", 
        "➕ Create Admin User",
        "⬆️ Promote User",
        "🔧 Bulk Operations",
        "📤 Export Data",
        "🔍 Advanced Search"
    ])
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_resource.clear()
        st.rerun()
    
    # Get users data
    users = get_all_users(supabase)
    
    # Main content based on selected tab
    if tab == "📊 Dashboard & Analytics":
        render_stats_dashboard(users)
        
        st.markdown("---")
        st.markdown("## 📈 Recent Activity")
        
        # Show recent users
        recent_users = sorted(users, key=lambda x: x['created_at'], reverse=True)[:5]
        st.markdown("### 🆕 Recently Registered Users")
        for user in recent_users:
            render_user_card(user, "recent")
    
    elif tab == "👥 User Management":
        st.markdown("## 👥 All Users")
        
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            role_filter = st.selectbox("Filter by Role", ["All", "admin", "user", "moderator"])
        with col2:
            status_filter = st.selectbox("Filter by Status", ["All", "Active", "Inactive"])
        with col3:
            tier_filter = st.selectbox("Subscription Tier", ["All", "free", "pro", "enterprise"])
        with col4:
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
        
        if search_term:
            filtered_users = [u for u in filtered_users 
                            if search_term.lower() in u['email'].lower() 
                            or search_term.lower() in u.get('full_name', '').lower()
                            or search_term.lower() in u.get('username', '').lower()]
        
        st.markdown(f"**Showing {len(filtered_users)} of {len(users)} users**")
        
        # Check for users being edited
        editing_users = [user for user in filtered_users if st.session_state.get(f'editing_user_{user["id"]}', False)]
        
        # Show editing forms first
        for user in editing_users:
            render_user_editor(user, supabase)
            st.markdown("---")
        
        # Show user cards
        for user in filtered_users:
            if not st.session_state.get(f'editing_user_{user["id"]}', False):
                render_user_card(user, "main")
    
    elif tab == "⏳ Pending Approvals":
        st.markdown("## ⏳ Pending Approvals")
        
        pending_users = [u for u in users if u['pending_approval']]
        
        if pending_users:
            st.markdown(f"**{len(pending_users)} users awaiting approval**")
            
            for user in pending_users:
                render_user_card(user, "pending")
        else:
            st.info("🎉 No pending approvals!")
    
    elif tab == "➕ Create Admin User":
        st.markdown("## ➕ Create New Admin User")
        
        with st.form("create_admin"):
            col1, col2 = st.columns(2)
            
            with col1:
                email = st.text_input("📧 Email Address")
                password = st.text_input("🔑 Password", type="password")
                
            with col2:
                full_name = st.text_input("👤 Full Name")
                auto_generate = st.checkbox("🎲 Auto-generate secure password")
            
            if auto_generate:
                password = generate_secure_password()
                st.info(f"🔑 Generated password: `{password}`")
            
            if st.form_submit_button("➕ Create Admin User", type="primary"):
                if email and password:
                    success, message = create_admin_user(supabase, email, password, full_name)
                    if success:
                        st.success(message)
                        st.balloons()
                    else:
                        st.error(message)
                else:
                    st.error("Please provide email and password")
    
    elif tab == "⬆️ Promote User":
        st.markdown("## ⬆️ Promote User to Admin")
        
        non_admin_users = [u for u in users if u['role'] != 'admin']
        
        if non_admin_users:
            # Show user cards for selection
            st.markdown("**Select a user to promote:**")
            
            for user in non_admin_users[:10]:  # Show first 10 for performance
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    display_name = user['full_name'] or user['username'] or 'No Name'
                    st.markdown(f"**{display_name}** ({user['email']})")
                    st.markdown(f"Role: {user['role']} | Tier: {user['subscription_tier']} | Active: {'Yes' if user['is_active'] else 'No'}")
                
                with col2:
                    if st.button("⬆️ Promote", key=f"promote_{user['id']}"):
                        success, message = promote_user_to_admin(supabase, user['email'])
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                
                st.markdown("---")
        else:
            st.info("No non-admin users found")
    
    elif tab == "🔧 Bulk Operations":
        st.markdown("## 🔧 Bulk Operations")
        
        if users:
            st.markdown("**Select users for bulk operations:**")
            
            # Select all checkbox
            select_all = st.checkbox("Select All Users")
            
            selected_users = []
            
            for user in users:
                if select_all:
                    selected = True
                else:
                    display_name = user['full_name'] or user['username'] or 'No Name'
                    selected = st.checkbox(f"{user['email']} ({display_name})", key=f"bulk_{user['id']}")
                
                if selected:
                    selected_users.append(user['id'])
            
            if selected_users:
                st.markdown(f"**{len(selected_users)} users selected**")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button("✅ Activate All"):
                        if bulk_user_operations(supabase, selected_users, "activate"):
                            st.success("Users activated successfully!")
                            st.rerun()
                
                with col2:
                    if st.button("❌ Deactivate All"):
                        if bulk_user_operations(supabase, selected_users, "deactivate"):
                            st.success("Users deactivated successfully!")
                            st.rerun()
                
                with col3:
                    if st.button("✉️ Verify Emails"):
                        if bulk_user_operations(supabase, selected_users, "verify_email"):
                            st.success("Emails verified successfully!")
                            st.rerun()
                
                with col4:
                    if st.button("🗑️ Delete All"):
                        st.warning("⚠️ This will permanently delete selected users!")
                        if st.button("Confirm Delete", key="confirm_bulk_delete"):
                            if bulk_user_operations(supabase, selected_users, "delete"):
                                st.success("Users deleted successfully!")
                                st.rerun()
        else:
            st.info("No users available for bulk operations")
    
    elif tab == "📤 Export Data":
        st.markdown("## 📤 Export User Data")
        
        if users:
            df = export_users_data(users)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Export Options:**")
                export_format = st.selectbox("Choose format", ["CSV", "Excel"])
                include_sensitive = st.checkbox("Include sensitive data (IDs, metadata)")
            
            with col2:
                st.markdown("**Preview:**")
                st.dataframe(df.head(), use_container_width=True)
            
            # Generate download
            if export_format == "CSV":
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("Excel export functionality would be implemented here")
        else:
            st.info("No user data to export")
    
    elif tab == "🔍 Advanced Search":
        st.markdown("## 🔍 Advanced Search & Analytics")
        
        # Advanced search form
        with st.expander("🔍 Search Filters", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                email_search = st.text_input("Email contains")
                name_search = st.text_input("Name contains")
                username_search = st.text_input("Username contains")
            
            with col2:
                date_from = st.date_input("Registered after")
                date_to = st.date_input("Registered before")
                activity_filter = st.selectbox("Activity", ["All", "Today", "This week", "This month", "Inactive"])
            
            with col3:
                role_search = st.multiselect("Roles", ["admin", "user", "moderator"])
                tier_search = st.multiselect("Subscription Tiers", ["free", "pro", "enterprise"])
                has_website = st.checkbox("Has website")
        
        # Apply advanced filters
        filtered_users = users
        
        if email_search:
            filtered_users = [u for u in filtered_users if email_search.lower() in u['email'].lower()]
        
        if name_search:
            filtered_users = [u for u in filtered_users if name_search.lower() in u.get('full_name', '').lower()]
        
        if username_search:
            filtered_users = [u for u in filtered_users if username_search.lower() in u.get('username', '').lower()]
        
        if role_search:
            filtered_users = [u for u in filtered_users if u['role'] in role_search]
        
        if tier_search:
            filtered_users = [u for u in filtered_users if u['subscription_tier'] in tier_search]
        
        if has_website:
            filtered_users = [u for u in filtered_users if u.get('website')]
        
        # Activity filter
        if activity_filter != "All":
            if activity_filter == "Today":
                filtered_users = [u for u in filtered_users if u['activity_score'] == "Today"]
            elif activity_filter == "This week":
                filtered_users = [u for u in filtered_users if "days ago" in u['activity_score'] or u['activity_score'] in ["Today", "Yesterday"]]
            elif activity_filter == "Inactive":
                filtered_users = [u for u in filtered_users if u['activity_score'] == "Never" or "months ago" in u['activity_score'] or "years ago" in u['activity_score']]
        
        st.markdown(f"**Found {len(filtered_users)} users matching criteria**")
        
        # Show results
        for user in filtered_users:
            render_user_card(user, "search")
    
    # Footer
    st.markdown("---")
    st.markdown("*Advanced User Management System - Built with Streamlit & Supabase*")

if __name__ == "__main__":
    main()
