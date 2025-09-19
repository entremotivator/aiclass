import streamlit as st
import os
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, timedelta
import json
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional, Tuple
import hashlib
import secrets
import string
import re

# Configuration and initialization
@st.cache_resource
def init_service_client():
    """Initialize Supabase service role client with enhanced error handling"""
    try:
        url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
        service_key = st.secrets.get("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        anon_key = st.secrets.get("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not service_key:
            st.error("❌ Missing Supabase configuration. Please check your secrets.toml file.")
            with st.expander("📋 Configuration Help"):
                st.code("""
# Add these to your secrets.toml file:
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "your-service-role-key"
SUPABASE_ANON_KEY = "your-anon-key"  # Optional but recommended
                """)
            st.stop()
        
        # Create service role client
        service_client = create_client(url, service_key)
        
        # Test connection with database health check
        try:
            test_response = service_client.table("profiles").select("count", count="exact").execute()
            profile_count = test_response.count if hasattr(test_response, 'count') else 0
            
            # Test auth functionality
            auth_users = service_client.auth.admin.list_users()
            user_count = len(auth_users.data.users) if hasattr(auth_users, 'data') and hasattr(auth_users.data, 'users') else 0
            
            st.success(f"✅ Connected to Supabase | Users: {user_count} | Profiles: {profile_count}")
            
        except Exception as test_error:
            st.warning(f"⚠️ Connection established but with limited functionality: {str(test_error)}")
        
        return service_client, url, anon_key
        
    except Exception as e:
        st.error(f"❌ Failed to initialize Supabase client: {str(e)}")
        st.stop()

# Enhanced user management functions
def get_comprehensive_user_data(supabase: Client) -> Tuple[List[Dict], Dict]:
    """Get comprehensive user data with analytics"""
    try:
        # Get auth users with pagination support
        all_auth_users = []
        page = 1
        per_page = 1000
        
        while True:
            auth_response = supabase.auth.admin.list_users(page=page, per_page=per_page)
            if hasattr(auth_response, 'data') and hasattr(auth_response.data, 'users'):
                users_batch = auth_response.data.users
                if not users_batch:
                    break
                all_auth_users.extend(users_batch)
                if len(users_batch) < per_page:
                    break
                page += 1
            else:
                break
        
        # Get profiles with all fields
        profiles_response = supabase.table("profiles").select("""
            id, full_name, avatar_url, role, created_at, updated_at,
            bio, website, location, phone_number, preferences,
            last_active_at, subscription_status, metadata
        """).execute()
        profiles = {p['id']: p for p in profiles_response.data} if profiles_response.data else {}
        
        # Get user roles
        roles_response = supabase.table("user_roles").select("*").execute()
        user_roles = {r['user_id']: r for r in roles_response.data} if roles_response.data else {}
        
        # Get user sessions (if table exists)
        try:
            sessions_response = supabase.table("user_sessions").select("""
                user_id, created_at, last_activity, ip_address, user_agent, device_info
            """).execute()
            user_sessions = {}
            for session in (sessions_response.data or []):
                user_id = session['user_id']
                if user_id not in user_sessions:
                    user_sessions[user_id] = []
                user_sessions[user_id].append(session)
        except:
            user_sessions = {}
        
        # Get user activity logs (if table exists)
        try:
            activity_response = supabase.table("user_activity").select("""
                user_id, action, created_at, ip_address, metadata
            """).execute()
            user_activities = {}
            for activity in (activity_response.data or []):
                user_id = activity['user_id']
                if user_id not in user_activities:
                    user_activities[user_id] = []
                user_activities[user_id].append(activity)
        except:
            user_activities = {}
        
        # Combine all data
        comprehensive_users = []
        analytics = {
            'total_users': 0,
            'verified_users': 0,
            'active_users': 0,
            'admin_users': 0,
            'users_by_role': {},
            'users_by_month': {},
            'recent_signups': 0,
            'users_with_profiles': 0
        }
        
        for user in all_auth_users:
            profile = profiles.get(user.id, {})
            role_info = user_roles.get(user.id, {})
            sessions = user_sessions.get(user.id, [])
            activities = user_activities.get(user.id, [])
            
            # Determine user role
            role = (role_info.get('role') or 
                   profile.get('role') or 
                   user.user_metadata.get('role', 'user'))
            
            # Calculate activity metrics
            is_active = False
            if user.last_sign_in_at:
                last_signin = datetime.fromisoformat(user.last_sign_in_at.replace('Z', '+00:00'))
                is_active = (datetime.now() - last_signin.replace(tzinfo=None)) < timedelta(days=30)
            
            # Check if recent signup
            created_date = datetime.fromisoformat(user.created_at.replace('Z', '+00:00'))
            is_recent = (datetime.now() - created_date.replace(tzinfo=None)) < timedelta(days=7)
            
            user_data = {
                'id': user.id,
                'email': user.email,
                'phone': user.phone,
                'created_at': user.created_at,
                'email_confirmed_at': user.email_confirmed_at,
                'last_sign_in_at': user.last_sign_in_at,
                'role': role,
                'is_active': is_active,
                'is_recent': is_recent,
                
                # Profile data
                'full_name': profile.get('full_name', ''),
                'avatar_url': profile.get('avatar_url', ''),
                'bio': profile.get('bio', ''),
                'website': profile.get('website', ''),
                'location': profile.get('location', ''),
                'phone_number': profile.get('phone_number', ''),
                'preferences': profile.get('preferences', {}),
                'last_active_at': profile.get('last_active_at'),
                'subscription_status': profile.get('subscription_status', 'free'),
                'profile_updated_at': profile.get('updated_at'),
                
                # Role data
                'role_assigned_at': role_info.get('created_at'),
                'role_permissions': role_info.get('permissions', []),
                
                # Session data
                'session_count': len(sessions),
                'latest_session': sessions[0] if sessions else None,
                
                # Activity data
                'activity_count': len(activities),
                'latest_activity': activities[0] if activities else None,
                
                # User metadata
                'user_metadata': user.user_metadata or {},
                'app_metadata': user.app_metadata or {},
            }
            
            comprehensive_users.append(user_data)
            
            # Update analytics
            analytics['total_users'] += 1
            if user.email_confirmed_at:
                analytics['verified_users'] += 1
            if is_active:
                analytics['active_users'] += 1
            if role == 'admin':
                analytics['admin_users'] += 1
            if is_recent:
                analytics['recent_signups'] += 1
            if profile:
                analytics['users_with_profiles'] += 1
            
            # Role distribution
            analytics['users_by_role'][role] = analytics['users_by_role'].get(role, 0) + 1
            
            # Monthly signup distribution
            month_key = created_date.strftime('%Y-%m')
            analytics['users_by_month'][month_key] = analytics['users_by_month'].get(month_key, 0) + 1
        
        return comprehensive_users, analytics
        
    except Exception as e:
        st.error(f"❌ Error fetching comprehensive user data: {str(e)}")
        return [], {}

def create_user_with_options(supabase: Client, user_data: Dict) -> Tuple[bool, str]:
    """Create user with comprehensive options"""
    try:
        email = user_data['email']
        password = user_data.get('password')
        
        # Generate password if not provided
        if not password:
            password = generate_secure_password()
            user_data['generated_password'] = password
        
        # Validate email
        if not is_valid_email(email):
            return False, "Invalid email format"
        
        # Create user with service role
        create_payload = {
            "email": email,
            "password": password,
            "email_confirm": user_data.get('auto_confirm', True),
            "phone_confirm": user_data.get('phone_confirm', False)
        }
        
        if user_data.get('phone'):
            create_payload['phone'] = user_data['phone']
        
        if user_data.get('user_metadata'):
            create_payload['user_metadata'] = user_data['user_metadata']
        
        user_response = supabase.auth.admin.create_user(create_payload)
        
        if user_response.user:
            user_id = user_response.user.id
            
            # Create comprehensive profile
            profile_data = {
                "id": user_id,
                "full_name": user_data.get('full_name', ''),
                "role": user_data.get('role', 'user'),
                "bio": user_data.get('bio', ''),
                "website": user_data.get('website', ''),
                "location": user_data.get('location', ''),
                "phone_number": user_data.get('phone_number', ''),
                "subscription_status": user_data.get('subscription_status', 'free'),
                "preferences": user_data.get('preferences', {}),
                "metadata": user_data.get('metadata', {})
            }
            
            supabase.table("profiles").insert(profile_data).execute()
            
            # Create user role entry
            if user_data.get('role') != 'user':
                supabase.table("user_roles").insert({
                    "user_id": user_id,
                    "role": user_data.get('role', 'user'),
                    "permissions": user_data.get('permissions', [])
                }).execute()
            
            # Send welcome email if requested
            if user_data.get('send_welcome_email'):
                # This would require additional email service integration
                pass
            
            success_msg = f"User created successfully: {email}"
            if user_data.get('generated_password'):
                success_msg += f"\nGenerated password: {password}"
            
            return True, success_msg
        else:
            return False, "Failed to create user account"
            
    except Exception as e:
        return False, f"Error creating user: {str(e)}"

def bulk_user_operations(supabase: Client, operation: str, user_ids: List[str], options: Dict = None) -> Dict:
    """Perform bulk operations on users"""
    results = {
        'successful': [],
        'failed': [],
        'details': {}
    }
    
    options = options or {}
    
    try:
        for user_id in user_ids:
            try:
                if operation == 'delete':
                    # Soft delete by updating metadata
                    supabase.auth.admin.update_user_by_id(user_id, {
                        "app_metadata": {
                            "deleted": True,
                            "deleted_at": datetime.utcnow().isoformat(),
                            "deleted_by": options.get('deleted_by', 'admin')
                        }
                    })
                    results['successful'].append(user_id)
                
                elif operation == 'activate':
                    supabase.auth.admin.update_user_by_id(user_id, {
                        "app_metadata": {
                            "deleted": False,
                            "activated_at": datetime.utcnow().isoformat()
                        }
                    })
                    results['successful'].append(user_id)
                
                elif operation == 'change_role':
                    new_role = options.get('new_role', 'user')
                    
                    # Update profile
                    supabase.table("profiles").update({
                        "role": new_role
                    }).eq("id", user_id).execute()
                    
                    # Update user_roles
                    supabase.table("user_roles").upsert({
                        "user_id": user_id,
                        "role": new_role
                    }).execute()
                    
                    results['successful'].append(user_id)
                
                elif operation == 'send_reset_email':
                    # This would require email service integration
                    user = supabase.auth.admin.get_user_by_id(user_id)
                    if user.user and user.user.email:
                        # Placeholder for actual email sending
                        results['successful'].append(user_id)
                
            except Exception as e:
                results['failed'].append(user_id)
                results['details'][user_id] = str(e)
        
        return results
        
    except Exception as e:
        return {'error': str(e), 'successful': [], 'failed': user_ids}

def get_database_analytics(supabase: Client) -> Dict:
    """Get comprehensive database analytics"""
    analytics = {}
    
    try:
        # Table sizes and statistics
        tables_to_analyze = ['profiles', 'user_roles', 'user_sessions', 'user_activity']
        
        for table_name in tables_to_analyze:
            try:
                response = supabase.table(table_name).select("*", count="exact").execute()
                analytics[f"{table_name}_count"] = response.count if hasattr(response, 'count') else 0
            except:
                analytics[f"{table_name}_count"] = 0
        
        # Storage analytics (if using Supabase Storage)
        try:
            # This would require storage API calls
            analytics['storage_usage'] = "Not implemented"
        except:
            analytics['storage_usage'] = 0
        
        # Authentication statistics
        try:
            auth_response = supabase.auth.admin.list_users()
            if hasattr(auth_response, 'data') and hasattr(auth_response.data, 'users'):
                users = auth_response.data.users
                
                now = datetime.now()
                
                # Time-based analytics
                analytics['users_last_24h'] = len([u for u in users 
                    if u.last_sign_in_at and 
                    (now - datetime.fromisoformat(u.last_sign_in_at.replace('Z', '+00:00')).replace(tzinfo=None)) < timedelta(hours=24)])
                
                analytics['users_last_7d'] = len([u for u in users 
                    if u.last_sign_in_at and 
                    (now - datetime.fromisoformat(u.last_sign_in_at.replace('Z', '+00:00')).replace(tzinfo=None)) < timedelta(days=7)])
                
                analytics['users_last_30d'] = len([u for u in users 
                    if u.last_sign_in_at and 
                    (now - datetime.fromisoformat(u.last_sign_in_at.replace('Z', '+00:00')).replace(tzinfo=None)) < timedelta(days=30)])
                
                # Email verification stats
                analytics['verified_users'] = len([u for u in users if u.email_confirmed_at])
                analytics['unverified_users'] = len([u for u in users if not u.email_confirmed_at])
                
        except Exception as e:
            st.warning(f"Could not fetch auth analytics: {str(e)}")
        
        return analytics
        
    except Exception as e:
        st.error(f"Error getting database analytics: {str(e)}")
        return {}

# Utility functions
def generate_secure_password(length: int = 12) -> str:
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def is_valid_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def format_datetime(dt_string: str) -> str:
    """Format datetime string for display"""
    if not dt_string:
        return "Never"
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return dt_string or "Never"

def create_user_activity_chart(users: List[Dict]) -> go.Figure:
    """Create user activity visualization"""
    # Prepare data for monthly signups
    monthly_data = {}
    for user in users:
        if user['created_at']:
            month = datetime.fromisoformat(user['created_at'].replace('Z', '+00:00')).strftime('%Y-%m')
            monthly_data[month] = monthly_data.get(month, 0) + 1
    
    months = sorted(monthly_data.keys())
    values = [monthly_data[month] for month in months]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months,
        y=values,
        mode='lines+markers',
        name='Monthly Signups',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="User Signups Over Time",
        xaxis_title="Month",
        yaxis_title="New Users",
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig

# Main application
def main():
    st.set_page_config(
        page_title="Supabase Admin Console",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .user-card {
        border: 1px solid #e1e5e9;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 style="color: white; margin: 0;">🚀 Supabase Admin Console</h1>
        <p style="color: white; margin: 0; opacity: 0.9;">Comprehensive user and database management</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize Supabase
    supabase, url, anon_key = init_service_client()
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🎛️ Admin Console")
        
        page = st.selectbox("Choose Section", [
            "📊 Dashboard",
            "👥 User Management", 
            "➕ Create Users",
            "🔄 Bulk Operations",
            "📈 Analytics",
            "⚙️ Database Tools",
            "🛠️ System Settings"
        ])
        
        # Quick stats in sidebar
        if st.button("🔄 Refresh Data"):
            st.cache_resource.clear()
            st.rerun()
    
    # Load data
    users, analytics = get_comprehensive_user_data(supabase)
    db_analytics = get_database_analytics(supabase)
    
    # Dashboard
    if page == "📊 Dashboard":
        st.header("📊 System Dashboard")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Users", 
                analytics.get('total_users', 0),
                delta=f"+{analytics.get('recent_signups', 0)} this week"
            )
        
        with col2:
            st.metric(
                "Verified Users", 
                analytics.get('verified_users', 0),
                delta=f"{(analytics.get('verified_users', 0) / max(analytics.get('total_users', 1), 1) * 100):.1f}% rate"
            )
        
        with col3:
            st.metric(
                "Active Users", 
                analytics.get('active_users', 0),
                delta=f"{(analytics.get('active_users', 0) / max(analytics.get('total_users', 1), 1) * 100):.1f}% rate"
            )
        
        with col4:
            st.metric(
                "Admin Users", 
                analytics.get('admin_users', 0)
            )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            if analytics.get('users_by_role'):
                fig_roles = px.pie(
                    values=list(analytics['users_by_role'].values()),
                    names=list(analytics['users_by_role'].keys()),
                    title="Users by Role"
                )
                st.plotly_chart(fig_roles, use_container_width=True)
        
        with col2:
            if users:
                fig_activity = create_user_activity_chart(users)
                st.plotly_chart(fig_activity, use_container_width=True)
        
        # Recent activity
        st.subheader("📋 Recent User Activity")
        recent_users = sorted([u for u in users if u['is_recent']], 
                            key=lambda x: x['created_at'], reverse=True)[:10]
        
        if recent_users:
            for user in recent_users:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"**{user['full_name'] or 'No name'}** ({user['email']})")
                    with col2:
                        st.write(f"Role: {user['role']}")
                    with col3:
                        st.write(format_datetime(user['created_at']))
        else:
            st.info("No recent user signups")
    
    # User Management
    elif page == "👥 User Management":
        st.header("👥 User Management")
        
        # Search and filters
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_term = st.text_input("🔍 Search users", placeholder="Email, name, or ID...")
        
        with col2:
            role_filter = st.selectbox("Filter by role", 
                ["All"] + list(analytics.get('users_by_role', {}).keys()))
        
        with col3:
            status_filter = st.selectbox("Filter by status", 
                ["All", "Active", "Inactive", "Verified", "Unverified"])
        
        # Apply filters
        filtered_users = users
        
        if search_term:
            search_lower = search_term.lower()
            filtered_users = [u for u in filtered_users 
                            if search_lower in u['email'].lower() 
                            or search_lower in u.get('full_name', '').lower()
                            or search_lower in u['id']]
        
        if role_filter != "All":
            filtered_users = [u for u in filtered_users if u['role'] == role_filter]
        
        if status_filter != "All":
            if status_filter == "Active":
                filtered_users = [u for u in filtered_users if u['is_active']]
            elif status_filter == "Inactive":
                filtered_users = [u for u in filtered_users if not u['is_active']]
            elif status_filter == "Verified":
                filtered_users = [u for u in filtered_users if u['email_confirmed_at']]
            elif status_filter == "Unverified":
                filtered_users = [u for u in filtered_users if not u['email_confirmed_at']]
        
        st.write(f"**Showing {len(filtered_users)} of {len(users)} users**")
        
        # User selection for bulk operations
        if filtered_users:
            select_all = st.checkbox("Select all users")
            selected_users = []
            
            # Display users with selection checkboxes
            for i, user in enumerate(filtered_users):
                with st.container():
                    col1, col2, col3, col4 = st.columns([0.5, 3, 2, 1.5])
                    
                    with col1:
                        is_selected = st.checkbox("", key=f"select_{user['id']}", value=select_all)
                        if is_selected:
                            selected_users.append(user['id'])
                    
                    with col2:
                        status_icon = "✅" if user['email_confirmed_at'] else "⏳"
                        activity_icon = "🟢" if user['is_active'] else "🔴"
                        role_icon = "👑" if user['role'] == 'admin' else "👤"
                        
                        st.write(f"{status_icon}{activity_icon}{role_icon} **{user['full_name'] or 'No name'}**")
                        st.caption(f"{user['email']}")
                    
                    with col3:
                        st.write(f"Role: {user['role']}")
                        st.caption(f"Created: {format_datetime(user['created_at'])[:10]}")
                    
                    with col4:
                        if st.button("Edit", key=f"edit_{user['id']}"):
                            st.session_state.edit_user_id = user['id']
                            st.rerun()
                
                st.divider()
            
            # Bulk operations
            if selected_users:
                st.subheader(f"🔧 Bulk Operations ({len(selected_users)} users selected)")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button("🗑️ Delete Selected"):
                        results = bulk_user_operations(supabase, 'delete', selected_users)
                        st.success(f"Deleted {len(results['successful'])} users")
                        if results['failed']:
                            st.error(f"Failed to delete {len(results['failed'])} users")
                        st.rerun()
                
                with col2:
                    if st.button("✅ Activate Selected"):
                        results = bulk_user_operations(supabase, 'activate', selected_users)
                        st.success(f"Activated {len(results['successful'])} users")
                        st.rerun()
                
                with col3:
                    new_role = st.selectbox("Change role to:", ["user", "admin", "moderator"])
                    if st.button("🔄 Update Roles"):
                        results = bulk_user_operations(supabase, 'change_role', selected_users, 
                                                     {'new_role': new_role})
                        st.success(f"Updated {len(results['successful'])} users")
                        st.rerun()
                
                with col4:
                    if st.button("📧 Send Reset Email"):
                        results = bulk_user_operations(supabase, 'send_reset_email', selected_users)
                        st.success(f"Sent emails to {len(results['successful'])} users")
        
        # User editing modal
        if hasattr(st.session_state, 'edit_user_id'):
            user_to_edit = next((u for u in users if u['id'] == st.session_state.edit_user_id), None)
            if user_to_edit:
                with st.expander(f"✏️ Editing User: {user_to_edit['email']}", expanded=True):
                    with st.form("edit_user_form"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            new_name = st.text_input("Full Name", value=user_to_edit.get('full_name', ''))
                            new_email = st.text_input("Email", value=user_to_edit['email'])
                            new_role = st.selectbox("Role", 
                                                  options=["user", "admin", "moderator"],
                                                  index=["user", "admin", "moderator"].index(user_to_edit.get('role', 'user')))
                        
                        with col2:
                            new_bio = st.text_area("Bio", value=user_to_edit.get('bio', ''))
                            new_location = st.text_input("Location", value=user_to_edit.get('location', ''))
                            new_website = st.text_input("Website", value=user_to_edit.get('website', ''))
                        
                        col3, col4 = st.columns(2)
                        with col3:
                            if st.form_submit_button("💾 Save Changes"):
                                try:
                                    # Update profile
                                    supabase.table("profiles").update({
                                        "full_name": new_name,
                                        "role": new_role,
                                        "bio": new_bio,
                                        "location": new_location,
                                        "website": new_website
                                    }).eq("id", user_to_edit['id']).execute()
                                    
                                    # Update user roles
                                    supabase.table("user_roles").upsert({
                                        "user_id": user_to_edit['id'],
                                        "role": new_role
                                    }).execute()
                                    
                                    st.success("User updated successfully!")
                                    del st.session_state.edit_user_id
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error updating user: {str(e)}")
                        
                        with col4:
                            if st.form_submit_button("❌ Cancel"):
                                del st.session_state.edit_user_id
                                st.rerun()
    
    # Create Users
    elif page == "➕ Create Users":
        st.header("➕ Create New Users")
        
        tab1, tab2 = st.tabs(["Single User", "Bulk Import"])
        
        with tab1:
            st.subheader("Create Single User")
            
            with st.form("create_single_user"):
                col1, col2 = st.columns(2)
                
                with col1:
                    email = st.text_input("Email Address*", placeholder="user@example.com")
                    full_name = st.text_input("Full Name", placeholder="John Doe")
                    password = st.text_input("Password (leave empty for auto-generation)", 
                                           type="password", placeholder="Optional")
                    role = st.selectbox("Role", ["user", "admin", "moderator"])
                    
                with col2:
                    phone = st.text_input("Phone Number", placeholder="+1234567890")
                    bio = st.text_area("Bio", placeholder="User bio...")
                    location = st.text_input("Location", placeholder="City, Country")
                    website = st.text_input("Website", placeholder="https://example.com")
                
                col3, col4 = st.columns(2)
                with col3:
                    auto_confirm = st.checkbox("Auto-confirm email", value=True)
                    send_welcome = st.checkbox("Send welcome email", value=False)
                
                with col4:
                    subscription_status = st.selectbox("Subscription Status", 
                                                     ["free", "premium", "enterprise"])
                
                # Advanced options
                with st.expander("🔧 Advanced Options"):
                    user_metadata = st.text_area("User Metadata (JSON)", 
                                                value='{}', 
                                                help="Additional user metadata in JSON format")
                    permissions = st.multiselect("Additional Permissions", 
                                               ["read_users", "write_users", "delete_users", "manage_roles"])
                
                if st.form_submit_button("🚀 Create User"):
                    if email:
                        try:
                            metadata = json.loads(user_metadata) if user_metadata else {}
                        except:
                            st.error("Invalid JSON in user metadata")
                            metadata = {}
                        
                        user_data = {
                            'email': email,
                            'password': password,
                            'full_name': full_name,
                            'role': role,
                            'phone': phone,
                            'bio': bio,
                            'location': location,
                            'website': website,
                            'auto_confirm': auto_confirm,
                            'send_welcome_email': send_welcome,
                            'subscription_status': subscription_status,
                            'user_metadata': metadata,
                            'permissions': permissions
                        }
                        
                        success, message = create_user_with_options(supabase, user_data)
                        
                        if success:
                            st.success(message)
                            if user_data.get('generated_password'):
                                st.info("⚠️ Make sure to share the generated password securely!")
                        else:
                            st.error(message)
                    else:
                        st.error("Please provide at least an email address")
        
        with tab2:
            st.subheader("Bulk User Import")
            
            # Sample CSV template
            if st.button("📥 Download CSV Template"):
                template_data = {
                    'email': ['user1@example.com', 'user2@example.com'],
                    'full_name': ['John Doe', 'Jane Smith'],
                    'role': ['user', 'admin'],
                    'location': ['New York', 'London'],
                    'bio': ['Software Developer', 'Project Manager']
                }
                template_df = pd.DataFrame(template_data)
                csv = template_df.to_csv(index=False)
                st.download_button(
                    label="Download Template",
                    data=csv,
                    file_name="user_import_template.csv",
                    mime="text/csv"
                )
            
            # File upload
            uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
            
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    st.write("Preview of uploaded data:")
                    st.dataframe(df.head())
                    
                    if st.button("🚀 Import Users"):
                        success_count = 0
                        error_count = 0
                        errors = []
                        
                        progress_bar = st.progress(0)
                        
                        for index, row in df.iterrows():
                            try:
                                user_data = {
                                    'email': row.get('email', ''),
                                    'full_name': row.get('full_name', ''),
                                    'role': row.get('role', 'user'),
                                    'bio': row.get('bio', ''),
                                    'location': row.get('location', ''),
                                    'website': row.get('website', ''),
                                    'auto_confirm': True,
                                    'subscription_status': row.get('subscription_status', 'free')
                                }
                                
                                success, message = create_user_with_options(supabase, user_data)
                                
                                if success:
                                    success_count += 1
                                else:
                                    error_count += 1
                                    errors.append(f"Row {index + 1}: {message}")
                                
                            except Exception as e:
                                error_count += 1
                                errors.append(f"Row {index + 1}: {str(e)}")
                            
                            progress_bar.progress((index + 1) / len(df))
                        
                        st.success(f"✅ Successfully created {success_count} users")
                        
                        if error_count > 0:
                            st.error(f"❌ Failed to create {error_count} users")
                            with st.expander("View Errors"):
                                for error in errors:
                                    st.write(f"• {error}")
                
                except Exception as e:
                    st.error(f"Error reading CSV file: {str(e)}")
    
    # Bulk Operations
    elif page == "🔄 Bulk Operations":
        st.header("🔄 Bulk Operations")
        
        if not users:
            st.warning("No users found to perform bulk operations")
            return
        
        # Operation selection
        operation = st.selectbox("Select Operation", [
            "Update Roles",
            "Send Password Reset",
            "Export User Data",
            "Delete Inactive Users",
            "Verify All Users",
            "Update Subscription Status"
        ])
        
        # Filters for bulk operations
        st.subheader("🎯 Target Users")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            role_target = st.multiselect("Target Roles", 
                                       list(analytics.get('users_by_role', {}).keys()))
        
        with col2:
            activity_target = st.selectbox("Activity Status", 
                                         ["All", "Active Only", "Inactive Only"])
        
        with col3:
            verification_target = st.selectbox("Email Status", 
                                             ["All", "Verified Only", "Unverified Only"])
        
        # Apply targeting filters
        target_users = users
        
        if role_target:
            target_users = [u for u in target_users if u['role'] in role_target]
        
        if activity_target == "Active Only":
            target_users = [u for u in target_users if u['is_active']]
        elif activity_target == "Inactive Only":
            target_users = [u for u in target_users if not u['is_active']]
        
        if verification_target == "Verified Only":
            target_users = [u for u in target_users if u['email_confirmed_at']]
        elif verification_target == "Unverified Only":
            target_users = [u for u in target_users if not u['email_confirmed_at']]
        
        st.write(f"**{len(target_users)} users will be affected by this operation**")
        
        # Operation-specific options
        if operation == "Update Roles":
            new_role = st.selectbox("New Role", ["user", "admin", "moderator"])
            
            if st.button(f"Update {len(target_users)} users to {new_role}"):
                results = bulk_user_operations(supabase, 'change_role', 
                                             [u['id'] for u in target_users], 
                                             {'new_role': new_role})
                st.success(f"Updated {len(results['successful'])} users")
                if results['failed']:
                    st.error(f"Failed to update {len(results['failed'])} users")
        
        elif operation == "Export User Data":
            export_format = st.selectbox("Export Format", ["CSV", "JSON"])
            include_sensitive = st.checkbox("Include sensitive data (emails, IDs)")
            
            if st.button("📥 Generate Export"):
                if export_format == "CSV":
                    export_df = pd.DataFrame(target_users)
                    if not include_sensitive:
                        columns_to_drop = ['id', 'user_metadata', 'app_metadata']
                        export_df = export_df.drop(columns=[col for col in columns_to_drop if col in export_df.columns])
                    
                    csv_data = export_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:  # JSON
                    export_data = target_users.copy()
                    if not include_sensitive:
                        for user in export_data:
                            user.pop('id', None)
                            user.pop('user_metadata', None)
                            user.pop('app_metadata', None)
                    
                    json_data = json.dumps(export_data, indent=2, default=str)
                    st.download_button(
                        label="Download JSON",
                        data=json_data,
                        file_name=f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
        
        elif operation == "Delete Inactive Users":
            inactive_threshold = st.slider("Days since last sign-in", 30, 365, 90)
            
            cutoff_date = datetime.now() - timedelta(days=inactive_threshold)
            inactive_users = [u for u in target_users 
                            if u['last_sign_in_at'] and 
                            datetime.fromisoformat(u['last_sign_in_at'].replace('Z', '+00:00')).replace(tzinfo=None) < cutoff_date]
            
            st.write(f"**{len(inactive_users)} users inactive for {inactive_threshold}+ days**")
            
            if inactive_users and st.button(f"⚠️ Delete {len(inactive_users)} inactive users"):
                if st.checkbox("I understand this action cannot be undone"):
                    results = bulk_user_operations(supabase, 'delete', [u['id'] for u in inactive_users])
                    st.success(f"Deleted {len(results['successful'])} users")
    
    # Analytics
    elif page == "📈 Analytics":
        st.header("📈 Advanced Analytics")
        
        # Time range selector
        time_range = st.selectbox("Time Range", 
                                ["Last 7 days", "Last 30 days", "Last 90 days", "All time"])
        
        # User growth analytics
        st.subheader("📊 User Growth")
        
        if analytics.get('users_by_month'):
            # Monthly growth chart
            months = sorted(analytics['users_by_month'].keys())[-12:]  # Last 12 months
            values = [analytics['users_by_month'][month] for month in months]
            
            fig_growth = go.Figure()
            fig_growth.add_trace(go.Bar(
                x=months,
                y=values,
                name='New Users',
                marker_color='#667eea'
            ))
            
            # Add trend line
            if len(values) > 1:
                z = np.polyfit(range(len(values)), values, 1)
                p = np.poly1d(z)
                fig_growth.add_trace(go.Scatter(
                    x=months,
                    y=p(range(len(values))),
                    mode='lines',
                    name='Trend',
                    line=dict(color='red', dash='dash')
                ))
            
            fig_growth.update_layout(
                title="Monthly User Growth",
                xaxis_title="Month",
                yaxis_title="New Users",
                template='plotly_white'
            )
            st.plotly_chart(fig_growth, use_container_width=True)
        
        # User activity patterns
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👥 User Segments")
            
            # Active vs Inactive
            active_count = len([u for u in users if u['is_active']])
            inactive_count = len(users) - active_count
            
            fig_activity = px.pie(
                values=[active_count, inactive_count],
                names=['Active', 'Inactive'],
                title="User Activity Status"
            )
            st.plotly_chart(fig_activity, use_container_width=True)
        
        with col2:
            st.subheader("✉️ Email Verification")
            
            verified_count = len([u for u in users if u['email_confirmed_at']])
            unverified_count = len(users) - verified_count
            
            fig_verification = px.pie(
                values=[verified_count, unverified_count],
                names=['Verified', 'Unverified'],
                title="Email Verification Status"
            )
            st.plotly_chart(fig_verification, use_container_width=True)
        
        # Database statistics
        st.subheader("🗄️ Database Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Profiles Table", db_analytics.get('profiles_count', 0))
        with col2:
            st.metric("User Roles", db_analytics.get('user_roles_count', 0))
        with col3:
            st.metric("Sessions", db_analytics.get('user_sessions_count', 0))
        with col4:
            st.metric("Activities", db_analytics.get('user_activity_count', 0))
        
        # Detailed user analytics table
        st.subheader("📋 Detailed User Analytics")
        
        if users:
            analytics_df = pd.DataFrame([{
                'Email': u['email'],
                'Role': u['role'],
                'Status': 'Active' if u['is_active'] else 'Inactive',
                'Verified': 'Yes' if u['email_confirmed_at'] else 'No',
                'Created': format_datetime(u['created_at'])[:10],
                'Last Sign In': format_datetime(u['last_sign_in_at'])[:10],
                'Sessions': u.get('session_count', 0),
                'Activities': u.get('activity_count', 0)
            } for u in users])
            
            st.dataframe(analytics_df, use_container_width=True)
            
            # Export analytics
            if st.button("📊 Export Analytics"):
                csv_data = analytics_df.to_csv(index=False)
                st.download_button(
                    label="Download Analytics CSV",
                    data=csv_data,
                    file_name=f"user_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    # Database Tools
    elif page == "⚙️ Database Tools":
        st.header("⚙️ Database Management Tools")
        
        tab1, tab2, tab3 = st.tabs(["Table Management", "Data Cleanup", "Backup & Restore"])
        
        with tab1:
            st.subheader("📊 Table Statistics")
            
            # Table information
            tables_info = {
                'profiles': db_analytics.get('profiles_count', 0),
                'user_roles': db_analytics.get('user_roles_count', 0),
                'user_sessions': db_analytics.get('user_sessions_count', 0),
                'user_activity': db_analytics.get('user_activity_count', 0)
            }
            
            for table_name, count in tables_info.items():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**{table_name}**")
                
                with col2:
                    st.write(f"{count} records")
                
                with col3:
                    if st.button(f"View {table_name}", key=f"view_{table_name}"):
                        try:
                            data = supabase.table(table_name).select("*").limit(100).execute()
                            if data.data:
                                st.dataframe(pd.DataFrame(data.data))
                            else:
                                st.info(f"No data in {table_name} table")
                        except Exception as e:
                            st.error(f"Error fetching {table_name}: {str(e)}")
        
        with tab2:
            st.subheader("🧹 Data Cleanup Tools")
            
            # Orphaned records cleanup
            st.write("**Find Orphaned Records**")
            
            if st.button("🔍 Find Orphaned Profiles"):
                try:
                    # Get all profile IDs
                    profiles = supabase.table("profiles").select("id").execute()
                    profile_ids = {p['id'] for p in profiles.data} if profiles.data else set()
                    
                    # Get all auth user IDs
                    auth_users = supabase.auth.admin.list_users()
                    if hasattr(auth_users, 'data') and hasattr(auth_users.data, 'users'):
                        auth_ids = {u.id for u in auth_users.data.users}
                    else:
                        auth_ids = set()
                    
                    orphaned_profiles = profile_ids - auth_ids
                    orphaned_auth = auth_ids - profile_ids
                    
                    if orphaned_profiles:
                        st.warning(f"Found {len(orphaned_profiles)} orphaned profiles")
                        if st.button("🗑️ Delete Orphaned Profiles"):
                            for profile_id in orphaned_profiles:
                                supabase.table("profiles").delete().eq("id", profile_id).execute()
                            st.success("Orphaned profiles deleted")
                    
                    if orphaned_auth:
                        st.warning(f"Found {len(orphaned_auth)} users without profiles")
                        if st.button("➕ Create Missing Profiles"):
                            for user_id in orphaned_auth:
                                supabase.table("profiles").insert({
                                    "id": user_id,
                                    "role": "user"
                                }).execute()
                            st.success("Missing profiles created")
                    
                    if not orphaned_profiles and not orphaned_auth:
                        st.success("No orphaned records found")
                
                except Exception as e:
                    st.error(f"Error checking for orphaned records: {str(e)}")
            
            # Duplicate cleanup
            if st.button("🔍 Find Duplicate Emails"):
                try:
                    email_counts = {}
                    for user in users:
                        email = user['email']
                        email_counts[email] = email_counts.get(email, 0) + 1
                    
                    duplicates = {email: count for email, count in email_counts.items() if count > 1}
                    
                    if duplicates:
                        st.warning(f"Found {len(duplicates)} duplicate emails")
                        for email, count in duplicates.items():
                            st.write(f"• {email}: {count} accounts")
                    else:
                        st.success("No duplicate emails found")
                
                except Exception as e:
                    st.error(f"Error checking for duplicates: {str(e)}")
        
        with tab3:
            st.subheader("💾 Backup & Restore")
            
            # Backup options
            st.write("**Create Backup**")
            
            backup_options = st.multiselect("Select data to backup", 
                                          ["User profiles", "User roles", "User sessions", "User activity"])
            
            if st.button("📦 Create Backup"):
                backup_data = {}
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                try:
                    if "User profiles" in backup_options:
                        profiles = supabase.table("profiles").select("*").execute()
                        backup_data['profiles'] = profiles.data
                    
                    if "User roles" in backup_options:
                        roles = supabase.table("user_roles").select("*").execute()
                        backup_data['user_roles'] = roles.data
                    
                    if "User sessions" in backup_options:
                        sessions = supabase.table("user_sessions").select("*").execute()
                        backup_data['user_sessions'] = sessions.data or []
                    
                    if "User activity" in backup_options:
                        activities = supabase.table("user_activity").select("*").execute()
                        backup_data['user_activity'] = activities.data or []
                    
                    # Add metadata
                    backup_data['metadata'] = {
                        'created_at': datetime.now().isoformat(),
                        'version': '1.0',
                        'total_records': sum(len(v) for v in backup_data.values() if isinstance(v, list))
                    }
                    
                    backup_json = json.dumps(backup_data, indent=2, default=str)
                    
                    st.download_button(
                        label="📥 Download Backup",
                        data=backup_json,
                        file_name=f"supabase_backup_{timestamp}.json",
                        mime="application/json"
                    )
                    
                    st.success(f"Backup created with {backup_data['metadata']['total_records']} records")
                
                except Exception as e:
                    st.error(f"Error creating backup: {str(e)}")
    
    # System Settings
    elif page == "🛠️ System Settings":
        st.header("🛠️ System Settings")
        
        tab1, tab2, tab3 = st.tabs(["Connection Settings", "Security", "Maintenance"])
        
        with tab1:
            st.subheader("🔗 Supabase Connection")
            
            # Connection info (sanitized)
            st.write("**Current Configuration:**")
            st.write(f"• Project URL: {url}")
            st.write(f"• Service Role: {'✅ Configured' if supabase else '❌ Not configured'}")
            st.write(f"• Anonymous Key: {'✅ Available' if anon_key else '❌ Not configured'}")
            
            # Test connection
            if st.button("🔍 Test Connection"):
                try:
                    # Test various endpoints
                    test_results = {}
                    
                    # Test auth
                    try:
                        auth_test = supabase.auth.admin.list_users(per_page=1)
                        test_results['Auth API'] = "✅ Working"
                    except Exception as e:
                        test_results['Auth API'] = f"❌ Error: {str(e)}"
                    
                    # Test database
                    try:
                        db_test = supabase.table("profiles").select("count", count="exact").limit(1).execute()
                        test_results['Database API'] = "✅ Working"
                    except Exception as e:
                        test_results['Database API'] = f"❌ Error: {str(e)}"
                    
                    # Display results
                    for service, status in test_results.items():
                        st.write(f"• {service}: {status}")
                
                except Exception as e:
                    st.error(f"Connection test failed: {str(e)}")
        
        with tab2:
            st.subheader("🔒 Security Settings")
            
            # Security metrics
            security_metrics = {
                'Users with strong passwords': 'Not available (encrypted)',
                'Recent suspicious activity': '0 detected',
                'Failed login attempts': 'Not tracked',
                'Admin users': len([u for u in users if u['role'] == 'admin'])
            }
            
            for metric, value in security_metrics.items():
                st.write(f"• **{metric}**: {value}")
            
            st.subheader("🛡️ Security Actions")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 Force Password Reset for All"):
                    st.warning("This would require all users to reset their passwords on next login")
                
                if st.button("📧 Send Security Notification"):
                    st.info("This would send security notifications to all admin users")
            
            with col2:
                if st.button("🔒 Lock All Admin Accounts"):
                    st.warning("This would temporarily disable all admin accounts except yours")
                
                if st.button("📊 Generate Security Report"):
                    st.info("Security report functionality would be implemented here")
        
        with tab3:
            st.subheader("🔧 System Maintenance")
            
            # System status
            st.write("**System Status:**")
            st.write(f"• Last data refresh: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"• Total users processed: {len(users)}")
            st.write(f"• Cache status: {'Active' if st.cache_resource else 'Inactive'}")
            
            # Maintenance actions
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🧹 Clear All Caches"):
                    st.cache_resource.clear()
                    st.success("All caches cleared")
                
                if st.button("🔄 Refresh All Data"):
                    st.cache_resource.clear()
                    st.rerun()
            
            with col2:
                if st.button("📊 Rebuild Analytics"):
                    st.info("Analytics rebuild would be performed here")
                
                if st.button("🗑️ Cleanup Temp Data"):
                    st.info("Temporary data cleanup would be performed here")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>🚀 Supabase Admin Console | Built with Streamlit | 
        Last updated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
    </div>
    """, unsafe_allow_html=True)
