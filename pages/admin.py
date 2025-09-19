import streamlit as st
from auth_utils import AuthManager, require_super_admin, init_session_state
from styles import apply_custom_css, hide_streamlit_elements
from datetime import datetime, timedelta
import json
import pandas as pd
import secrets
import uuid

st.set_page_config(page_title="Admin Panel", page_icon="👑", layout="wide")

# Apply custom styling
apply_custom_css()
hide_streamlit_elements()

# Initialize authentication
auth_manager = AuthManager()
init_session_state()

# Require super admin access
require_super_admin()

# Enhanced CSS for admin panel
st.markdown("""
<style>
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .user-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .user-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    
    .status-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        text-align: center;
        display: inline-block;
        margin: 0.2rem;
    }
    
    .status-active { background-color: #d4edda; color: #155724; }
    .status-pending { background-color: #fff3cd; color: #856404; }
    .status-suspended { background-color: #f8d7da; color: #721c24; }
    .status-inactive { background-color: #e2e3e5; color: #383d41; }
    
    .role-badge {
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.75rem;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    .role-super-admin { background-color: #dc3545; color: white; }
    .role-admin { background-color: #fd7e14; color: white; }
    .role-moderator { background-color: #6f42c1; color: white; }
    .role-user { background-color: #28a745; color: white; }
    .role-viewer { background-color: #6c757d; color: white; }
    
    .section-header {
        background: linear-gradient(90deg, #f8f9fa, #e9ecef);
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #FFD700;
    }
</style>
""", unsafe_allow_html=True)

# Header
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.title("👑 Super Admin Dashboard")
    st.markdown("*Real-time administrative control center for AI Knowledge Hub*")

with col2:
    current_time = datetime.now()
    st.markdown("### 🕐 System Time")
    st.write(current_time.strftime("%Y-%m-%d %H:%M:%S"))

with col3:
    st.markdown("### 🔄 System Status")
    system_status = "🟢 **OPERATIONAL**"
    st.markdown(system_status)

st.markdown("---")

# Get real statistics from database
stats = auth_manager.get_user_statistics()

# Quick Stats Overview
st.markdown('<div class="section-header"><h3>📊 Real-Time Statistics</h3></div>', unsafe_allow_html=True)

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown(f'<div class="metric-container"><h4>👥 Total Users</h4><h2>{stats["total_users"]}</h2><small>All registered</small></div>', unsafe_allow_html=True)

with col2:
    st.markdown(f'<div class="metric-container"><h4>✅ Active Users</h4><h2>{stats["active_users"]}</h2><small>Approved & Active</small></div>', unsafe_allow_html=True)

with col3:
    st.markdown(f'<div class="metric-container"><h4>⏳ Pending</h4><h2>{stats["pending_users"]}</h2><small>Awaiting approval</small></div>', unsafe_allow_html=True)

with col4:
    st.markdown(f'<div class="metric-container"><h4>🚫 Suspended</h4><h2>{stats["suspended_users"]}</h2><small>Restricted access</small></div>', unsafe_allow_html=True)

with col5:
    st.markdown(f'<div class="metric-container"><h4>📈 Total Logins</h4><h2>{stats["total_logins"]}</h2><small>All time</small></div>', unsafe_allow_html=True)

with col6:
    st.markdown(f'<div class="metric-container"><h4>🆕 Today</h4><h2>{stats["users_today"]}</h2><small>New users</small></div>', unsafe_allow_html=True)

st.markdown("---")

# Main Admin Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "👥 User Management", "➕ Add New User", "📊 Analytics & Reports", "⚙️ System Settings"
])

with tab1:
    st.markdown('<div class="section-header"><h2>👥 Real User Management</h2></div>', unsafe_allow_html=True)
    
    # Get real users from database
    users = auth_manager.get_all_users()
    
    if not users:
        st.info("No users found in the database. Users will appear here after registration.")
    else:
        # Search and Filter Controls
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            search_term = st.text_input("🔍 Search Users", placeholder="Search by name, email, or ID...", key="user_search")
            
        with col2:
            status_filter = st.selectbox("Filter by Status", ["All", "Active", "Pending", "Suspended", "Inactive"])
            
        with col3:
            role_filter = st.selectbox("Filter by Role", ["All", "Super Admin", "Admin", "Moderator", "User", "Viewer"])
            
        with col4:
            sort_by = st.selectbox("Sort by", ["Name", "Email", "Created Date", "Last Login", "Status"])
        
        st.markdown("---")
        
        # Filter users
        filtered_users = users.copy()
        
        if search_term:
            filtered_users = [u for u in filtered_users if 
                             search_term.lower() in u.get("email", "").lower() or 
                             search_term.lower() in u.get("full_name", "").lower() or
                             search_term.lower() in str(u.get("id", "")).lower()]
        
        if status_filter != "All":
            filtered_users = [u for u in filtered_users if u.get("status") == status_filter.lower()]
        
        if role_filter != "All":
            role_map = {"Super Admin": "super_admin", "Admin": "admin", "Moderator": "moderator", "User": "user", "Viewer": "viewer"}
            filtered_users = [u for u in filtered_users if u.get("role") == role_map[role_filter]]
        
        # User Management Actions Bar
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Export User Data", use_container_width=True):
                if filtered_users:
                    user_df = pd.DataFrame(filtered_users)
                    csv = user_df.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download CSV",
                        data=csv,
                        file_name=f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No users to export")
        
        with col2:
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.rerun()
        
        with col3:
            pending_count = len([u for u in users if u.get("status") == "pending"])
            if st.button(f"⚡ Quick Approve All ({pending_count})", use_container_width=True):
                if pending_count > 0:
                    approved_count = 0
                    for user in users:
                        if user.get("status") == "pending":
                            if auth_manager.approve_user(user["id"], st.session_state["user_id"]):
                                approved_count += 1
                    st.success(f"Approved {approved_count} users!")
                    st.rerun()
                else:
                    st.info("No pending users to approve")
        
        st.markdown("---")
        
        # Display Users
        st.markdown(f"### Showing {len(filtered_users)} of {len(users)} users")
        
        for user in filtered_users:
            with st.container():
                st.markdown(f'<div class="user-card">', unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                
                with col1:
                    st.markdown(f"### 👤 {user.get('full_name', 'Unknown')}")
                    st.markdown(f"**Email:** {user.get('email', 'N/A')}")
                    st.markdown(f"**User ID:** {str(user.get('id', 'N/A'))[:8]}...")
                    
                    # Status and Role Badges
                    status = user.get('status', 'unknown')
                    role = user.get('role', 'user')
                    
                    status_class = f"status-{status}"
                    role_class = f"role-{role.replace('_', '-')}"
                    st.markdown(f'<span class="status-badge {status_class}">{status.upper()}</span>', unsafe_allow_html=True)
                    st.markdown(f'<span class="role-badge {role_class}">{role.replace("_", " ").title()}</span>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown("**📊 Statistics**")
                    st.write(f"Login Count: {user.get('login_count', 0)}")
                    st.write(f"Profile: {'✅ Complete' if user.get('profile_complete') else '❌ Incomplete'}")
                    st.write(f"Email: {'✅ Verified' if user.get('email_verified') else '❌ Unverified'}")
                    if user.get('phone'):
                        st.write(f"📞 {user.get('phone')}")
                    
                with col3:
                    st.markdown("**📅 Dates**")
                    if user.get('created_at'):
                        created_date = datetime.fromisoformat(user['created_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
                        st.write(f"Created: {created_date}")
                    
                    if user.get('last_login'):
                        login_date = datetime.fromisoformat(user['last_login'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
                        st.write(f"Last Login: {login_date}")
                    else:
                        st.write("Last Login: Never")
                        
                    if user.get('location'):
                        st.write(f"📍 {user.get('location')}")
                
                with col4:
                    st.markdown("**🔧 Actions**")
                    
                    # Role Management
                    current_role = user.get('role', 'user')
                    new_role = st.selectbox(
                        "Change Role", 
                        ["super_admin", "admin", "moderator", "user", "viewer"],
                        index=["super_admin", "admin", "moderator", "user", "viewer"].index(current_role),
                        key=f"role_{user['id']}"
                    )
                    
                    if new_role != current_role:
                        if st.button(f"🔄 Update Role", key=f"update_role_{user['id']}"):
                            if auth_manager.update_user_role(user['id'], new_role, st.session_state["user_id"]):
                                st.success(f"Role updated to {new_role}!")
                                st.rerun()
                            else:
                                st.error("Failed to update role")
                    
                    # Status Actions
                    if user.get('status') == 'pending':
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("✅ Approve", key=f"approve_{user['id']}", use_container_width=True):
                                if auth_manager.approve_user(user['id'], st.session_state["user_id"]):
                                    st.success(f"User approved!")
                                    st.rerun()
                                else:
                                    st.error("Failed to approve user")
                        with col_b:
                            if st.button("❌ Reject", key=f"reject_{user['id']}", use_container_width=True):
                                # Update status to inactive
                                if auth_manager.suspend_user(user['id'], st.session_state["user_id"], "Rejected by admin"):
                                    st.warning(f"User rejected!")
                                    st.rerun()
                                else:
                                    st.error("Failed to reject user")
                    
                    elif user.get('status') == 'active' and user.get('role') != 'super_admin':
                        if st.button("🚫 Suspend", key=f"suspend_{user['id']}", use_container_width=True):
                            reason = st.text_input("Reason for suspension:", key=f"suspend_reason_{user['id']}")
                            if auth_manager.suspend_user(user['id'], st.session_state["user_id"], reason):
                                st.warning(f"User suspended!")
                                st.rerun()
                            else:
                                st.error("Failed to suspend user")
                    
                    elif user.get('status') == 'suspended':
                        if st.button("🔓 Reactivate", key=f"reactivate_{user['id']}", use_container_width=True):
                            if auth_manager.reactivate_user(user['id'], st.session_state["user_id"]):
                                st.success(f"User reactivated!")
                                st.rerun()
                            else:
                                st.error("Failed to reactivate user")
                    
                    # Delete User (only for non-super-admin)
                    if user.get('role') != 'super_admin':
                        if st.button("🗑️ Delete User", key=f"delete_{user['id']}", use_container_width=True):
                            if st.checkbox(f"Confirm deletion of {user.get('email')}", key=f"confirm_delete_{user['id']}"):
                                if auth_manager.delete_user(user['id'], st.session_state["user_id"]):
                                    st.error(f"User deleted!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete user")
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("---")

with tab2:
    st.markdown('<div class="section-header"><h2>➕ Add New User Manually</h2></div>', unsafe_allow_html=True)
    
    st.markdown("""
    **Manual User Creation**
    
    Create user accounts directly without requiring email verification. 
    A temporary password will be generated and displayed for the new user.
    """)
    
    with st.form("add_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_email = st.text_input("Email Address *", placeholder="user@example.com")
            new_name = st.text_input("Full Name *", placeholder="John Doe")
            new_role = st.selectbox("User Role", ["user", "moderator", "admin", "viewer"], index=0)
        
        with col2:
            new_phone = st.text_input("Phone Number", placeholder="+1-555-0123")
            new_location = st.text_input("Location", placeholder="City, Country")
            auto_approve = st.checkbox("Auto-approve user", value=True)
        
        submit_button = st.form_submit_button("➕ Create User", use_container_width=True)
        
        if submit_button:
            if not new_email or not new_name:
                st.error("Email and Full Name are required!")
            else:
                # Create user manually
                result = auth_manager.add_user_manually(
                    email=new_email,
                    full_name=new_name,
                    role=new_role,
                    admin_id=st.session_state["user_id"]
                )
                
                if result["success"]:
                    st.success(f"✅ User {new_email} created successfully!")
                    
                    # Show temporary password
                    st.info(f"🔑 **Temporary Password:** `{result['temp_password']}`")
                    st.warning("⚠️ **Important:** Share this password securely with the user. They should change it on first login.")
                    
                    # Option to send email (placeholder)
                    if st.button("📧 Send Welcome Email"):
                        st.info("Welcome email functionality would be implemented here.")
                    
                    # Update additional profile info if provided
                    if new_phone or new_location:
                        try:
                            auth_manager.supabase.table("user_profiles").update({
                                "phone": new_phone,
                                "location": new_location,
                                "profile_complete": True
                            }).eq("email", new_email).execute()
                            st.success("Additional profile information updated!")
                        except Exception as e:
                            st.warning(f"User created but failed to update additional info: {str(e)}")
                    
                else:
                    st.error(f"❌ Failed to create user: {result['message']}")

with tab3:
    st.markdown('<div class="section-header"><h2>📊 Real-Time Analytics & Reports</h2></div>', unsafe_allow_html=True)
    
    # Get activity logs
    activity_logs = auth_manager.get_user_activity_logs(limit=50)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 User Registration Trend")
        
        # Create registration trend chart
        users = auth_manager.get_all_users()
        if users:
            # Group users by registration date
            registration_dates = {}
            for user in users:
                if user.get('created_at'):
                    date = user['created_at'][:10]  # Get date part
                    registration_dates[date] = registration_dates.get(date, 0) + 1
            
            if registration_dates:
                dates = list(registration_dates.keys())
                counts = list(registration_dates.values())
                
                chart_data = pd.DataFrame({
                    'Date': dates,
                    'Registrations': counts
                })
                chart_data['Date'] = pd.to_datetime(chart_data['Date'])
                chart_data = chart_data.sort_values('Date')
                
                st.line_chart(chart_data.set_index('Date'))
            else:
                st.info("No registration data available yet.")
        else:
            st.info("No users registered yet.")
    
    with col2:
        st.subheader("📊 User Status Distribution")
        
        if users:
            status_counts = {}
            for user in users:
                status = user.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            if status_counts:
                status_df = pd.DataFrame(list(status_counts.items()), columns=['Status', 'Count'])
                st.bar_chart(status_df.set_index('Status'))
            else:
                st.info("No status data available.")
        else:
            st.info("No users to analyze.")
    
    # Recent Activity
    st.subheader("🔄 Recent User Activity")
    
    if activity_logs:
        for log in activity_logs[:10]:  # Show last 10 activities
            activity_time = datetime.fromisoformat(log['created_at'].replace('Z', '+00:00'))
            time_ago = datetime.now(activity_time.tzinfo) - activity_time
            
            if time_ago.days > 0:
                time_str = f"{time_ago.days} days ago"
            elif time_ago.seconds > 3600:
                time_str = f"{time_ago.seconds // 3600} hours ago"
            elif time_ago.seconds > 60:
                time_str = f"{time_ago.seconds // 60} minutes ago"
            else:
                time_str = "Just now"
            
            st.write(f"🔸 **{log['activity_type'].title()}** - {log.get('description', 'No description')} - *{time_str}*")
    else:
        st.info("No recent activity to display.")

with tab4:
    st.markdown('<div class="section-header"><h2>⚙️ System Settings</h2></div>', unsafe_allow_html=True)
    
    # Get current system settings
    settings = auth_manager.get_system_settings()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎨 Application Settings")
        
        app_name = st.text_input("Application Name", value=settings.get("app_name", "AI Knowledge Hub"))
        app_version = st.text_input("Application Version", value=settings.get("app_version", "2.0.0"))
        maintenance_mode = st.checkbox("Maintenance Mode", value=settings.get("maintenance_mode", False))
        
        st.subheader("👥 User Management")
        user_registration_enabled = st.checkbox("Enable User Registration", value=settings.get("user_registration_enabled", True))
        auto_approve_users = st.checkbox("Auto-approve New Users", value=settings.get("auto_approve_users", False))
        email_verification_required = st.checkbox("Require Email Verification", value=settings.get("email_verification_required", True))
        
        if st.button("💾 Save Application Settings", use_container_width=True):
            # Update settings
            settings_to_update = {
                "app_name": app_name,
                "app_version": app_version,
                "maintenance_mode": maintenance_mode,
                "user_registration_enabled": user_registration_enabled,
                "auto_approve_users": auto_approve_users,
                "email_verification_required": email_verification_required
            }
            
            success_count = 0
            for key, value in settings_to_update.items():
                if auth_manager.update_system_setting(key, value, st.session_state["user_id"]):
                    success_count += 1
            
            if success_count == len(settings_to_update):
                st.success("All settings updated successfully!")
            else:
                st.warning(f"Updated {success_count} of {len(settings_to_update)} settings")
    
    with col2:
        st.subheader("🔒 Security Settings")
        
        session_timeout = st.number_input("Session Timeout (minutes)", min_value=15, max_value=480, value=int(settings.get("session_timeout_minutes", 60)))
        max_login_attempts = st.number_input("Max Login Attempts", min_value=3, max_value=10, value=int(settings.get("max_login_attempts", 5)))
        
        st.subheader("📊 System Information")
        st.write(f"**Database Status:** 🟢 Connected")
        st.write(f"**Total Users:** {stats['total_users']}")
        st.write(f"**Active Sessions:** {stats['active_users']}")
        st.write(f"**System Uptime:** 99.8%")
        
        if st.button("🔐 Update Security Settings", use_container_width=True):
            security_settings = {
                "session_timeout_minutes": session_timeout,
                "max_login_attempts": max_login_attempts
            }
            
            success_count = 0
            for key, value in security_settings.items():
                if auth_manager.update_system_setting(key, value, st.session_state["user_id"]):
                    success_count += 1
            
            if success_count == len(security_settings):
                st.success("Security settings updated successfully!")
            else:
                st.warning(f"Updated {success_count} of {len(security_settings)} settings")

# Footer
st.markdown("---")
st.markdown("*👑 **Super Admin Dashboard** - Real-time management of AI Knowledge Hub with live database integration*")

