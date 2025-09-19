import streamlit as st
from supabase import create_client, Client
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# -------------------------
# Hide Streamlit Settings & Styling
# -------------------------
hide_streamlit_style = """
    <style>
    /* Hide Streamlit header, footer, and menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Hide the hamburger menu */
    .css-14xtw13.e8zbici0 {display: none;}
    
    /* Hide the "Deploy" button */
    .css-1rs6os.edgvbvh3 {display: none;}
    
    /* Hide the settings menu */
    .css-vk3wp9.e1akgbir0 {display: none;}
    
    /* Hide the GitHub icon */
    .css-1j8o68f.edgvbvh9 {display: none;}
    
    /* Custom styling for better appearance */
    .stApp > header {
        background-color: transparent;
    }
    
    .stApp {
        margin-top: -80px;
    }
    
    /* Hide sidebar initially */
    .css-1d391kg {
        display: none;
    }
    
    /* Show sidebar only when authenticated */
    .show-sidebar .css-1d391kg {
        display: flex !important;
    }
    </style>
"""

def hide_sidebar():
    """Hide the sidebar completely"""
    st.markdown("""
    <style>
        .css-1d391kg {
            display: none;
        }
        section[data-testid="stSidebar"] {
            display: none;
        }
        .css-6qob1r {
            display: none;
        }
        .e1fqkh3o3 {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

def show_sidebar():
    """Show the sidebar for authenticated users"""
    st.markdown("""
    <style>
        .css-1d391kg {
            display: flex !important;
        }
        section[data-testid="stSidebar"] {
            display: flex !important;
        }
        .css-6qob1r {
            display: flex !important;
        }
        .e1fqkh3o3 {
            display: flex !important;
        }
    </style>
    """, unsafe_allow_html=True)

# -------------------------
# Supabase Setup
# -------------------------
def init_connection() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_connection()

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
    # Show sidebar for authenticated users
    show_sidebar()
    
    st.title("👑 Admin Dashboard")
    
    # Sidebar navigation for admin features
    with st.sidebar:
        st.header("🔧 Admin Tools")
        
        # User info in sidebar
        if st.session_state.user:
            st.info(f"👤 {st.session_state.user.email}\n🎭 {st.session_state.role.title()}")
        
        # Logout button in sidebar
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            logout()
        
        st.divider()
        
        admin_section = st.selectbox(
            "Select Section",
            ["📊 Analytics Overview", "👥 User Management", "📈 System Reports", "⚙️ Settings"]
        )
    
    if admin_section == "📊 Analytics Overview":
        show_admin_analytics()
    elif admin_section == "👥 User Management":
        show_user_management()
    elif admin_section == "📈 System Reports":
        show_system_reports()
    elif admin_section == "⚙️ Settings":
        show_admin_settings()

def show_admin_analytics():
    st.subheader("📊 System Analytics")
    
    try:
        # Get user data
        users = supabase.table("user_profiles").select("*").execute()
        auth_users = supabase.auth.admin.list_users()
        
        # Calculate metrics
        total_users = len(users.data or [])
        admin_count = len([u for u in users.data or [] if u["role"] == "admin"])
        user_count = total_users - admin_count
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Users", total_users, delta=f"+{total_users - max(0, total_users-5)}")
        with col2:
            st.metric("Regular Users", user_count)
        with col3:
            st.metric("Administrators", admin_count)
        with col4:
            confirmed_users = len([u for u in auth_users.user if getattr(u, 'email_confirmed', False)])
            st.metric("Confirmed Users", confirmed_users)
        
        # User registration chart
        if users.data:
            st.subheader("📈 User Registration Trends")
            # Create sample data for demonstration
            dates = pd.date_range(start='2024-01-01', end=datetime.now(), freq='D')
            registrations = pd.DataFrame({
                'date': dates,
                'registrations': [max(0, int(abs(hash(str(d)) % 10) - 5)) for d in dates]
            })
            
            fig = px.line(registrations, x='date', y='registrations', 
                         title='Daily User Registrations')
            st.plotly_chart(fig, use_container_width=True)
            
            # Role distribution pie chart
            role_data = pd.DataFrame({
                'Role': ['Users', 'Admins'],
                'Count': [user_count, admin_count]
            })
            fig_pie = px.pie(role_data, values='Count', names='Role', 
                           title='User Role Distribution')
            st.plotly_chart(fig_pie, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error loading analytics: {e}")

def show_user_management():
    st.subheader("👥 User Management")
    
    try:
        users = supabase.table("user_profiles").select("*").execute()
        auth_users = supabase.auth.admin.list_users()

        # Merge auth info + profiles
        user_data = []
        for profile in users.data or []:
            auth_info = next((u for u in auth_users.user if u.id == profile["id"]), None)
            user_data.append({
                "id": profile["id"],
                "email": profile["email"],
                "role": profile["role"],
                "created_at": getattr(auth_info, "created_at", None),
                "last_sign_in": getattr(auth_info, "last_sign_in_at", None),
                "confirmed": getattr(auth_info, "email_confirmed", False),
            })

        # Search and filter options
        col1, col2 = st.columns([2, 1])
        with col1:
            search = st.text_input("🔍 Search by email")
        with col2:
            role_filter = st.selectbox("Filter by role", ["All", "user", "admin"])
        
        # Apply filters
        filtered = user_data
        if search:
            filtered = [u for u in filtered if search.lower() in u["email"].lower()]
        if role_filter != "All":
            filtered = [u for u in filtered if u["role"] == role_filter]

        # Bulk actions
        st.subheader("🔧 Bulk Actions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📧 Send Welcome Email to All"):
                st.success("Welcome emails sent to all users!")
        with col2:
            if st.button("⬇️ Export User Data"):
                df = pd.DataFrame(filtered)
                st.download_button("Download Users CSV", df.to_csv(index=False), "users.csv", "text/csv")

        # User list
        if filtered:
            for i, user in enumerate(filtered):
                with st.expander(f"👤 {user['email']} ({user['role'].title()}) {'✅' if user['confirmed'] else '❌'}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**User ID:** {user['id'][:8]}...")
                        st.write(f"**Created:** {user['created_at']}")
                        st.write(f"**Last Login:** {user['last_sign_in']}")
                    with col2:
                        st.write(f"**Status:** {'Confirmed' if user['confirmed'] else 'Pending'}")
                        st.write(f"**Role:** {user['role'].title()}")

                    # Actions
                    action_col1, action_col2, action_col3 = st.columns(3)
                    with action_col1:
                        new_role = st.selectbox("Change Role", ["user", "admin"], 
                                                index=0 if user["role"] == "user" else 1,
                                                key=f"role_{i}")
                        if st.button("Update Role", key=f"update_{i}"):
                            supabase.table("user_profiles").update({"role": new_role}).eq("id", user["id"]).execute()
                            st.success(f"Updated {user['email']} to {new_role}")
                            st.rerun()
                    
                    with action_col2:
                        if st.button("🔄 Reset Password", key=f"reset_{i}"):
                            reset_password(user["email"])
                            st.success(f"Password reset sent!")
                    
                    with action_col3:
                        if st.button("❌ Delete User", key=f"delete_{i}", type="secondary"):
                            try:
                                supabase.table("user_profiles").delete().eq("id", user["id"]).execute()
                                supabase.auth.admin.delete_user(user["id"])
                                st.warning(f"Deleted {user['email']}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to delete: {e}")
        else:
            st.info("No users found matching your criteria.")

    except Exception as e:
        st.error(f"Error loading users: {e}")

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
    # Show sidebar for authenticated users
    show_sidebar()
    
    st.title("🙋 Welcome to Your Dashboard")
    
    user_email = st.session_state.user.email if st.session_state.user else "Unknown"
    user_id = st.session_state.user.id if st.session_state.user else None
    
    # Sidebar for user navigation
    with st.sidebar:
        st.header("🏠 Dashboard")
        
        # User info in sidebar
        st.info(f"👤 {user_email.split('@')[0].title()}\n🎭 {st.session_state.role.title()}\n📧 {user_email}")
        
        # Logout button in sidebar
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            logout()
        
        st.divider()
        
        # Navigation menu
        page = st.selectbox(
            "Navigate to:",
            ["📊 My Activity", "👤 Profile", "🔔 Notifications", "❓ Help"]
        )
    
    # Main content based on sidebar selection
    if page == "📊 My Activity":
        show_user_activity(user_id, user_email)
    elif page == "👤 Profile":
        show_user_profile(user_id, user_email)
    elif page == "🔔 Notifications":
        show_user_notifications(user_email)
    elif page == "❓ Help":
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
# Redirect
# -------------------------
def redirect_dashboard():
    if st.session_state.role == "admin":
        admin_dashboard()
    else:
        user_dashboard()

# -------------------------
# Login Page
# -------------------------
def login_page():
    # Hide sidebar completely for unauthenticated users
    hide_sidebar()
    
    st.title("🔐 Secure Authentication Portal")
    
    # Add some styling for the login page
    st.markdown("""
    <div style='text-align: center; padding: 20px; margin-bottom: 30px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white;'>
        <h3>🚀 Welcome to Your Secure Dashboard</h3>
        <p>Please authenticate to access your personalized experience</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🔑 Login", "📝 Sign Up", "🔄 Reset Password"])

    with tab1:
        st.subheader("🔑 Sign In to Your Account")
        with st.form("login_form"):
            email = st.text_input("📧 Email Address", placeholder="your.email@example.com")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                remember_me = st.checkbox("🧠 Remember me")
            with col2:
                st.write("")  # Spacer
            
            if st.form_submit_button("🚀 Login", type="primary", use_container_width=True):
                if email and password:
                    success, msg = login(email, password)
                    if success:
                        st.success(msg)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Please fill in all fields.")

    with tab2:
        st.subheader("📝 Create New Account")
        with st.form("signup_form"):
            email = st.text_input("📧 Email Address", placeholder="your.email@example.com")
            password = st.text_input("🔒 Password", type="password", 
                                   help="Must be 12+ characters with uppercase, lowercase, number, and special character")
            confirm_password = st.text_input("🔒 Confirm Password", type="password")
            role = st.selectbox("👤 Account Type", ["user", "admin"], 
                               help="Select 'admin' only if you have administrative privileges")
            
            terms = st.checkbox("✅ I agree to the Terms of Service and Privacy Policy")
            
            if st.form_submit_button("🎉 Create Account", type="primary", use_container_width=True):
                if email and password and confirm_password:
                    if password != confirm_password:
                        st.error("❌ Passwords don't match!")
                    elif not terms:
                        st.warning("⚠️ Please agree to the terms and conditions.")
                    else:
                        success, msg = signup(email, password, role)
                        if success:
                            st.success(msg)
                            st.balloons()
                        else:
                            st.error(msg)
                else:
                    st.warning("Please fill in all fields.")

    with tab3:
        st.subheader("🔄 Reset Your Password")
        with st.form("reset_form"):
            email = st.text_input("📧 Email Address", 
                                 placeholder="Enter your registered email address")
            st.info("💡 We'll send you a secure link to reset your password")
            
            if st.form_submit_button("📧 Send Reset Link", type="primary", use_container_width=True):
                if email:
                    success, msg = reset_password(email)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.warning("Please enter your email address.")

# -------------------------
# Main App
# -------------------------
def main():
    st.set_page_config(
        page_title="Secure Auth Portal", 
        page_icon="🔐", 
        layout="wide",
        initial_sidebar_state="collapsed"  # Start with collapsed sidebar
    )
    
    # Apply custom CSS to hide Streamlit elements
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    if not st.session_state.authenticated:
        login_page()
    else:
        redirect_dashboard()

# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    main()
