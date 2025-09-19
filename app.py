import streamlit as st
from supabase import create_client, Client
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import requests

# -------------------------
# Supabase Setup
# -------------------------
def init_connection() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

def init_service_role_connection() -> Client:
    """Initialize Supabase client with service role key for admin operations"""
    url = st.secrets["supabase"]["url"]
    service_key = st.secrets["supabase"]["service_role_key"]  # Added service role key
    return create_client(url, service_key)

supabase = init_connection()
service_supabase = init_service_role_connection()  # Service role client for admin operations

# -------------------------
# Session State
# -------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "role" not in st.session_state:
    st.session_state.role = None
if "user" not in st.session_state:
    st.session_state.user = None

# -------------------------
# Password Validator
# -------------------------
def is_strong_password(password: str) -> bool:
    """Password must be at least 12 chars, with upper, lower, number, special"""
    return bool(re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{12,}$", password))

# -------------------------
# Signup Function
# -------------------------
def signup(email, password, role="user"):
    if not email or not password:
        return False, "⚠️ Please fill in all fields."
    if not is_strong_password(password):
        return False, "⚠️ Password must be at least 12 characters and include uppercase, lowercase, number, and special character."
    
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        if res.user:
            supabase.table("user_profiles").insert({
                "id": res.user.id,
                "email": email,
                "role": role
            }).execute()
            return True, "✅ Account created! Please check your email to verify your account, then log in."
        return False, "❌ Failed to create account."
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower():
            return False, "⚠️ Email already registered. Try logging in."
        return False, f"❌ Signup error: {error_msg}"

# -------------------------
# Login Function
# -------------------------
def login(email, password):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if res.user:
            profile = supabase.table("user_profiles").select("role").eq("id", res.user.id).execute()
            role = profile.data[0]["role"] if profile.data else "user"
            st.session_state.authenticated = True
            st.session_state.user = res.user
            st.session_state.role = role
            return True, f"✅ Logged in as {role.capitalize()}"
        return False, "❌ Invalid login."
    except Exception as e:
        return False, f"❌ Login error: {str(e)}"

# -------------------------
# Reset Password
# -------------------------
def reset_password(email):
    try:
        supabase.auth.reset_password_for_email(email)
        return True, f"✅ Password reset email sent to {email}"
    except Exception as e:
        return False, f"❌ Reset error: {str(e)}"

# -------------------------
# Logout
# -------------------------
def logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    st.session_state.authenticated = False
    st.session_state.role = None
    st.session_state.user = None
    st.rerun()

# -------------------------
# Admin Dashboard
# -------------------------
def admin_dashboard():
    st.title("👑 Admin Dashboard - Service Role Enabled")
    
    st.success("🔑 Service Role API Active - Full Administrative Access")
    
    # Sidebar navigation for admin features
    with st.sidebar:
        st.header("🔧 Admin Tools")
        admin_section = st.selectbox(
            "Select Section",
            ["📊 Analytics Overview", "👥 User Management", "🔧 Service Role Operations", "📈 System Reports", "⚙️ Settings"]
        )
    
    if admin_section == "📊 Analytics Overview":
        show_admin_analytics_enhanced()
    elif admin_section == "👥 User Management":
        show_user_management_enhanced()
    elif admin_section == "🔧 Service Role Operations":  # New service role section
        show_service_role_operations()
    elif admin_section == "📈 System Reports":
        show_system_reports()
    elif admin_section == "⚙️ Settings":
        show_admin_settings()

def show_admin_analytics_enhanced():
    """Enhanced analytics using service role API"""
    st.subheader("📊 System Analytics - Service Role Data")
    
    # Get comprehensive stats
    stats = get_system_stats_service_role()
    if not stats:
        st.error("Failed to load system statistics")
        return
    
    # Display enhanced metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Users", stats["total_users"])
    with col2:
        st.metric("Regular Users", stats["user_count"])
    with col3:
        st.metric("Administrators", stats["admin_count"])
    with col4:
        st.metric("Confirmed Users", stats["confirmed_count"])
    with col5:
        st.metric("Recent (24h)", stats["recent_registrations"], delta=f"+{stats['recent_registrations']}")
    
    # Enhanced user data visualization
    if stats["users_data"]:
        st.subheader("📈 User Analytics")
        
        # Role distribution
        role_data = pd.DataFrame({
            'Role': ['Users', 'Admins'],
            'Count': [stats["user_count"], stats["admin_count"]]
        })
        
        col1, col2 = st.columns(2)
        with col1:
            fig_pie = px.pie(role_data, values='Count', names='Role', 
                           title='User Role Distribution')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Registration timeline
            auth_users_df = pd.DataFrame([{
                'created_at': u.created_at,
                'confirmed': getattr(u, 'email_confirmed', False)
            } for u in stats["auth_users"]])
            
            if not auth_users_df.empty:
                auth_users_df['date'] = pd.to_datetime(auth_users_df['created_at']).dt.date
                daily_registrations = auth_users_df.groupby('date').size().reset_index(name='registrations')
                
                fig_line = px.line(daily_registrations, x='date', y='registrations',
                                 title='Daily User Registrations')
                st.plotly_chart(fig_line, use_container_width=True)

def show_user_management_enhanced():
    """Enhanced user management with service role capabilities"""
    st.subheader("👥 User Management - Service Role Powers")
    
    # Get all users using service role
    users_data = get_all_users_service_role()
    auth_users = service_supabase.auth.admin.list_users()
    
    # Enhanced user creation
    st.subheader("➕ Create New User (Service Role)")
    with st.form("create_user_service"):
        col1, col2 = st.columns(2)
        with col1:
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
        with col2:
            new_role = st.selectbox("Role", ["user", "admin"])
            auto_confirm = st.checkbox("Auto-confirm email", value=True)
        
        metadata = st.text_area("User Metadata (JSON)", value='{"created_by": "admin"}')
        
        if st.form_submit_button("🔧 Create User (Service Role)", type="primary"):
            try:
                metadata_dict = json.loads(metadata) if metadata else {}
                success, msg = create_user_service_role(new_email, new_password, new_role, metadata_dict)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
            except json.JSONDecodeError:
                st.error("Invalid JSON in metadata field")
    
    # Enhanced user list with service role data
    st.subheader("👥 All Users (Service Role View)")
    
    if users_data:
        # Merge auth and profile data
        enhanced_users = []
        for profile in users_data:
            auth_info = next((u for u in auth_users.user if u.id == profile["id"]), None)
            enhanced_users.append({
                **profile,
                "created_at": getattr(auth_info, "created_at", None),
                "last_sign_in": getattr(auth_info, "last_sign_in_at", None),
                "confirmed": getattr(auth_info, "email_confirmed", False),
                "phone": getattr(auth_info, "phone", None),
                "user_metadata": getattr(auth_info, "user_metadata", {}),
            })
        
        # Display users with enhanced controls
        for i, user in enumerate(enhanced_users):
            with st.expander(f"👤 {user['email']} ({user['role'].title()}) {'✅' if user['confirmed'] else '❌'}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**User ID:** {user['id']}")
                    st.write(f"**Created:** {user['created_at']}")
                    st.write(f"**Last Login:** {user['last_sign_in']}")
                    st.write(f"**Phone:** {user.get('phone', 'N/A')}")
                
                with col2:
                    st.write(f"**Status:** {'Confirmed' if user['confirmed'] else 'Pending'}")
                    st.write(f"**Role:** {user['role'].title()}")
                    st.write(f"**Created by Admin:** {user.get('created_by_admin', False)}")
                    
                with col3:
                    st.write("**User Metadata:**")
                    st.json(user.get('user_metadata', {}))
                
                # Service role actions
                st.write("**🔧 Service Role Actions:**")
                action_col1, action_col2, action_col3 = st.columns(3)
                
                with action_col1:
                    new_role = st.selectbox("Change Role", ["user", "admin"], 
                                          index=0 if user["role"] == "user" else 1,
                                          key=f"role_sr_{i}")
                    if st.button("🔧 Update Role (SR)", key=f"update_sr_{i}"):
                        success, msg = update_user_role_service_role(user["id"], new_role)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                
                with action_col2:
                    if st.button("🔄 Reset Password (SR)", key=f"reset_sr_{i}"):
                        try:
                            service_supabase.auth.admin.update_user_by_id(
                                user["id"], 
                                {"password": "TempPassword123!"}
                            )
                            st.success("Password reset to: TempPassword123!")
                        except Exception as e:
                            st.error(f"Reset failed: {e}")
                
                with action_col3:
                    if st.button("❌ Delete User (SR)", key=f"delete_sr_{i}", type="secondary"):
                        success, msg = delete_user_service_role(user["id"])
                        if success:
                            st.warning(msg)
                            st.rerun()
                        else:
                            st.error(msg)

def show_service_role_operations():
    """New section for service role specific operations"""
    st.subheader("🔧 Service Role Operations")
    st.info("These operations use the service role key and bypass Row Level Security (RLS)")
    
    # Bulk operations
    st.subheader("📦 Bulk Operations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Bulk User Creation**")
        uploaded_file = st.file_uploader("Upload CSV with users", type=['csv'])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write("Preview:")
            st.dataframe(df.head())
            
            if st.button("🔧 Create All Users (Service Role)"):
                success_count = 0
                for _, row in df.iterrows():
                    success, _ = create_user_service_role(
                        row['email'], 
                        row.get('password', 'TempPassword123!'),
                        row.get('role', 'user')
                    )
                    if success:
                        success_count += 1
                
                st.success(f"Created {success_count}/{len(df)} users successfully")
    
    with col2:
        st.write("**System Maintenance**")
        if st.button("🧹 Clean Unconfirmed Users (7+ days)"):
            try:
                cutoff_date = (datetime.now() - timedelta(days=7)).isoformat()
                auth_users = service_supabase.auth.admin.list_users()
                
                deleted_count = 0
                for user in auth_users.user:
                    if (not getattr(user, 'email_confirmed', False) and 
                        user.created_at < cutoff_date):
                        service_supabase.auth.admin.delete_user(user.id)
                        deleted_count += 1
                
                st.success(f"Cleaned up {deleted_count} unconfirmed users")
            except Exception as e:
                st.error(f"Cleanup failed: {e}")
        
        if st.button("📊 Generate Full System Report"):
            stats = get_system_stats_service_role()
            if stats:
                report = {
                    "timestamp": datetime.now().isoformat(),
                    "total_users": stats["total_users"],
                    "admin_count": stats["admin_count"],
                    "confirmed_count": stats["confirmed_count"],
                    "recent_registrations": stats["recent_registrations"]
                }
                
                st.download_button(
                    "📥 Download Report",
                    json.dumps(report, indent=2),
                    "system_report.json",
                    "application/json"
                )
    
    # Advanced queries
    st.subheader("🔍 Advanced Queries (Service Role)")
    
    query_type = st.selectbox("Query Type", [
        "Users by Role",
        "Recent Registrations",
        "Unconfirmed Users",
        "Users by Creation Date"
    ])
    
    if st.button("🔧 Execute Query"):
        try:
            if query_type == "Users by Role":
                users = get_all_users_service_role()
                role_counts = {}
                for user in users:
                    role = user.get('role', 'unknown')
                    role_counts[role] = role_counts.get(role, 0) + 1
                st.json(role_counts)
            
            elif query_type == "Recent Registrations":
                auth_users = service_supabase.auth.admin.list_users()
                recent = [u for u in auth_users.user 
                         if u.created_at > (datetime.now() - timedelta(days=7)).isoformat()]
                st.write(f"Found {len(recent)} users registered in the last 7 days")
                for user in recent[:10]:  # Show first 10
                    st.write(f"- {user.email} ({user.created_at})")
            
            elif query_type == "Unconfirmed Users":
                auth_users = service_supabase.auth.admin.list_users()
                unconfirmed = [u for u in auth_users.user 
                              if not getattr(u, 'email_confirmed', False)]
                st.write(f"Found {len(unconfirmed)} unconfirmed users")
                for user in unconfirmed[:10]:
                    st.write(f"- {user.email} (created: {user.created_at})")
        
        except Exception as e:
            st.error(f"Query failed: {e}")

def show_system_reports():
    st.subheader("📈 System Reports")
    
    # Activity logs
    st.write("**Recent System Activity**")
    activity_data = [
        {"timestamp": datetime.now() - timedelta(minutes=5), "action": "User login", "user": "user@example.com"},
        {"timestamp": datetime.now() - timedelta(minutes=15), "action": "New user registration", "user": "newuser@example.com"},
        {"timestamp": datetime.now() - timedelta(hours=1), "action": "Password reset", "user": "forgot@example.com"},
        {"timestamp": datetime.now() - timedelta(hours=2), "action": "Admin role assigned", "user": "admin@example.com"},
    ]
    
    for activity in activity_data:
        st.write(f"🕐 {activity['timestamp'].strftime('%Y-%m-%d %H:%M')} - {activity['action']} - {activity['user']}")
    
    # System health
    st.subheader("🏥 System Health")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Database Status", "✅ Healthy", delta="99.9% uptime")
    with col2:
        st.metric("Auth Service", "✅ Operational", delta="0 errors")
    with col3:
        st.metric("API Response", "⚡ Fast", delta="120ms avg")

def show_admin_settings():
    st.subheader("⚙️ System Settings")
    
    # Security settings
    st.write("**Security Configuration**")
    password_policy = st.checkbox("Enforce strong passwords", value=True)
    session_timeout = st.slider("Session timeout (hours)", 1, 24, 8)
    two_factor = st.checkbox("Require 2FA for admins", value=False)
    
    # Email settings
    st.write("**Email Configuration**")
    welcome_email = st.checkbox("Send welcome emails", value=True)
    notification_email = st.text_input("Admin notification email", value="admin@company.com")
    
    # System maintenance
    st.write("**System Maintenance**")
    if st.button("🧹 Clean up old sessions"):
        st.success("Old sessions cleaned up!")
    if st.button("📊 Generate system report"):
        st.success("System report generated!")
    
    if st.button("💾 Save Settings", type="primary"):
        st.success("Settings saved successfully!")

# -------------------------
# User Dashboard
# -------------------------
def user_dashboard():
    st.title("🙋 Welcome to Your Dashboard")
    
    user_email = st.session_state.user.email if st.session_state.user else "Unknown"
    user_id = st.session_state.user.id if st.session_state.user else None
    
    # Welcome section
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### Hello, **{user_email.split('@')[0].title()}**! 👋")
        st.info(f"🎭 Role: {st.session_state.role.title()} | 📧 Email: {user_email}")
    with col2:
        if st.button("🚪 Logout", type="primary"):
            logout()
    
    # User-specific content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 My Activity", "👤 Profile", "🔔 Notifications", "❓ Help"])
    
    with tab1:
        show_user_activity(user_id, user_email)
    
    with tab2:
        show_user_profile(user_id, user_email)
    
    with tab3:
        show_user_notifications(user_email)
    
    with tab4:
        show_user_help()

def show_user_activity(user_id, user_email):
    st.subheader("📊 Your Activity Overview")
    
    # Activity metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Days Active", "12", delta="2 this week")
    with col2:
        st.metric("Last Login", "Today", delta="2 hours ago")
    with col3:
        st.metric("Profile Updates", "3", delta="1 this month")
    
    # Recent activity timeline
    st.subheader("🕐 Recent Activity")
    activities = [
        {"time": "2 hours ago", "action": "Logged in", "icon": "🔐"},
        {"time": "1 day ago", "action": "Updated profile", "icon": "👤"},
        {"time": "3 days ago", "action": "Changed password", "icon": "🔒"},
        {"time": "1 week ago", "action": "First login", "icon": "🎉"},
    ]
    
    for activity in activities:
        st.write(f"{activity['icon']} **{activity['action']}** - {activity['time']}")
    
    # Usage chart
    st.subheader("📈 Your Usage Pattern")
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    usage_data = pd.DataFrame({
        'Date': dates,
        'Sessions': [max(0, int(abs(hash(str(d) + user_email) % 5))) for d in dates]
    })
    
    fig = px.bar(usage_data, x='Date', y='Sessions', title='Daily Sessions (Last 30 Days)')
    st.plotly_chart(fig, use_container_width=True)

def show_user_profile(user_id, user_email):
    st.subheader("👤 Your Profile")
    
    # Profile information
    with st.form("profile_form"):
        st.write("**Account Information**")
        display_name = st.text_input("Display Name", value=user_email.split('@')[0].title())
        bio = st.text_area("Bio", value="Tell us about yourself...")
        
        # Preferences
        st.write("**Preferences**")
        theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
        notifications = st.checkbox("Email notifications", value=True)
        newsletter = st.checkbox("Subscribe to newsletter", value=False)
        
        # Security
        st.write("**Security**")
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.form_submit_button("💾 Save Changes", type="primary"):
            if new_password and new_password == confirm_password:
                if is_strong_password(new_password):
                    st.success("Profile updated successfully!")
                else:
                    st.error("Password doesn't meet security requirements")
            else:
                st.success("Profile preferences updated!")

def show_user_notifications(user_email):
    st.subheader("🔔 Your Notifications")
    
    # Notification settings
    st.write("**Notification Preferences**")
    email_notifications = st.checkbox("Email notifications", value=True)
    security_alerts = st.checkbox("Security alerts", value=True)
    product_updates = st.checkbox("Product updates", value=False)
    
    # Recent notifications
    st.write("**Recent Notifications**")
    notifications = [
        {"time": "1 hour ago", "message": "Welcome to the platform!", "type": "info", "read": False},
        {"time": "1 day ago", "message": "Your profile was updated", "type": "success", "read": True},
        {"time": "3 days ago", "message": "Security: New login detected", "type": "warning", "read": True},
    ]
    
    for i, notif in enumerate(notifications):
        icon = "🔵" if not notif["read"] else "⚪"
        type_icon = {"info": "ℹ️", "success": "✅", "warning": "⚠️"}.get(notif["type"], "📢")
        st.write(f"{icon} {type_icon} **{notif['message']}** - {notif['time']}")
        if not notif["read"] and st.button(f"Mark as read", key=f"read_{i}"):
            st.success("Marked as read!")
    
    if st.button("🧹 Clear all notifications"):
        st.success("All notifications cleared!")

def show_user_help():
    st.subheader("❓ Help & Support")
    
    # FAQ
    st.write("**Frequently Asked Questions**")
    
    with st.expander("How do I change my password?"):
        st.write("Go to the Profile tab and enter your current password along with your new password.")
    
    with st.expander("How do I update my notification preferences?"):
        st.write("Visit the Notifications tab to customize which notifications you receive.")
    
    with st.expander("Who can I contact for support?"):
        st.write("You can reach out to our support team at support@company.com")
    
    # Contact form
    st.write("**Contact Support**")
    with st.form("support_form"):
        subject = st.selectbox("Subject", ["General Question", "Technical Issue", "Feature Request", "Bug Report"])
        message = st.text_area("Message", placeholder="Describe your question or issue...")
        
        if st.form_submit_button("📧 Send Message"):
            st.success("Your message has been sent! We'll get back to you soon.")
    
    # Quick actions
    st.write("**Quick Actions**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 View Documentation"):
            st.info("Opening documentation...")
    with col2:
        if st.button("💬 Live Chat"):
            st.info("Connecting to live chat...")

# -------------------------
# Service Role API Functions
# -------------------------
def get_all_users_service_role():
    """Get all users using service role - bypasses RLS"""
    try:
        response = service_supabase.table("user_profiles").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"Service role error: {e}")
        return []

def create_user_service_role(email, password, role="user", metadata=None):
    """Create user with service role privileges"""
    try:
        # Create auth user
        auth_response = service_supabase.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,  # Auto-confirm with service role
            "user_metadata": metadata or {}
        })
        
        if auth_response.user:
            # Create profile
            profile_response = service_supabase.table("user_profiles").insert({
                "id": auth_response.user.id,
                "email": email,
                "role": role,
                "created_by_admin": True
            }).execute()
            
            return True, f"User {email} created successfully with {role} role"
        return False, "Failed to create user"
    except Exception as e:
        return False, f"Service role creation error: {e}"

def update_user_role_service_role(user_id, new_role):
    """Update user role using service role"""
    try:
        response = service_supabase.table("user_profiles").update({
            "role": new_role,
            "updated_at": datetime.now().isoformat()
        }).eq("id", user_id).execute()
        
        return True, f"User role updated to {new_role}"
    except Exception as e:
        return False, f"Role update error: {e}"

def delete_user_service_role(user_id):
    """Delete user completely using service role"""
    try:
        # Delete from profiles first
        service_supabase.table("user_profiles").delete().eq("id", user_id).execute()
        
        # Delete from auth
        service_supabase.auth.admin.delete_user(user_id)
        
        return True, "User deleted successfully"
    except Exception as e:
        return False, f"Deletion error: {e}"

def get_system_stats_service_role():
    """Get comprehensive system statistics using service role"""
    try:
        # Get all users
        users = service_supabase.table("user_profiles").select("*").execute()
        auth_users = service_supabase.auth.admin.list_users()
        
        # Calculate stats
        total_users = len(users.data or [])
        admin_count = len([u for u in users.data or [] if u["role"] == "admin"])
        confirmed_count = len([u for u in auth_users.user if getattr(u, 'email_confirmed', False)])
        
        # Get recent activity (last 24 hours)
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        recent_users = [u for u in auth_users.user if u.created_at > yesterday]
        
        return {
            "total_users": total_users,
            "admin_count": admin_count,
            "user_count": total_users - admin_count,
            "confirmed_count": confirmed_count,
            "recent_registrations": len(recent_users),
            "users_data": users.data,
            "auth_users": auth_users.user
        }
    except Exception as e:
        st.error(f"Stats error: {e}")
        return None

# -------------------------
# Redirect
# -------------------------
def redirect_dashboard():
    if st.session_state.role == "admin":
        admin_dashboard()
    else:
        user_dashboard()

# -------------------------
# Main App
# -------------------------
def main():
    st.set_page_config(page_title="Enhanced Auth App - Service Role", page_icon="🔐", layout="wide")

    if not st.session_state.authenticated:
        st.title("🔐 Supabase Authentication - Service Role Enabled")
        st.info("🔑 This application includes service role API capabilities for administrative operations")

        tab1, tab2, tab3 = st.tabs(["🔑 Login", "📝 Sign Up", "🔄 Reset Password"])

        with tab1:
            with st.form("login_form"):
                email = st.text_input("📧 Email")
                password = st.text_input("🔒 Password", type="password")
                if st.form_submit_button("Login", type="primary"):
                    success, msg = login(email, password)
                    st.success(msg) if success else st.error(msg)
                    if success: st.rerun()

        with tab2:
            with st.form("signup_form"):
                email = st.text_input("📧 Email")
                password = st.text_input("🔒 Password", type="password")
                role = st.selectbox("👤 Role", ["user", "admin"])
                if st.form_submit_button("Sign Up", type="primary"):
                    success, msg = signup(email, password, role)
                    st.success(msg) if success else st.error(msg)

        with tab3:
            with st.form("reset_form"):
                email = st.text_input("📧 Email")
                if st.form_submit_button("Send Reset", type="primary"):
                    success, msg = reset_password(email)
                    st.success(msg) if success else st.error(msg)
    else:
        redirect_dashboard()

# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    main()
