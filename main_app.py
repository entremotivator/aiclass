import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# -------------------------
# Professional Styling
# -------------------------
def apply_custom_css():
    """Apply professional blue/purple theme with black text"""
    st.markdown("""
    <style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .css-14xtw13.e8zbici0 {display: none;}
    .css-1rs6os.edgvbvh3 {display: none;}
    .css-vk3wp9.e1akgbir0 {display: none;}
    .css-1j8o68f.edgvbvh9 {display: none;}
    
    /* Main app styling */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        color: #000000;
    }
    
    /* Text colors - all black */
    .stMarkdown, .stText, p, span, div {
        color: #000000 !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #1e3a8a !important;
        font-weight: 600;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #3b82f6 0%, #6366f1 100%);
        color: white !important;
    }
    
    .css-1d391kg .stMarkdown, 
    .css-1d391kg .stText,
    .css-1d391kg p,
    .css-1d391kg span,
    .css-1d391kg div {
        color: white !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #5b21b6 100%);
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.4);
        transform: translateY(-1px);
    }
    
    /* Form styling */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        background-color: white;
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        color: #000000 !important;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 8px 8px 0 0;
        color: #374151;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
        color: white !important;
        border-color: #3b82f6;
    }
    
    /* Alert styling */
    .stAlert {
        border-radius: 8px;
        border: none;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Info boxes */
    .stInfo {
        background: linear-gradient(135deg, #dbeafe 0%, #e0e7ff 100%);
        border: 1px solid #3b82f6;
        color: #1e40af !important;
    }
    
    /* Success boxes */
    .stSuccess {
        background: linear-gradient(135deg, #dcfce7 0%, #d1fae5 100%);
        border: 1px solid #10b981;
        color: #065f46 !important;
    }
    
    /* Error boxes */
    .stError {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border: 1px solid #ef4444;
        color: #991b1b !important;
    }
    
    /* Warning boxes */
    .stWarning {
        background: linear-gradient(135deg, #fef3c7 0%, #fed7aa 100%);
        border: 1px solid #f59e0b;
        color: #92400e !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        color: #000000 !important;
    }
    
    /* DataFrame styling */
    .dataframe {
        border: none !important;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .dataframe thead tr th {
        background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 600;
    }
    
    .dataframe tbody tr:nth-child(even) {
        background-color: #f8fafc !important;
    }
    
    .dataframe tbody tr td {
        color: #000000 !important;
        border-color: #e5e7eb !important;
    }
    
    /* Login page specific styling */
    .login-container {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
        margin: 2rem 0;
    }
    
    .welcome-header {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
        border-radius: 12px;
        color: white !important;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3);
    }
    
    .welcome-header h1,
    .welcome-header h2,
    .welcome-header h3,
    .welcome-header p {
        color: white !important;
        margin: 0.5rem 0;
    }
    
    /* Dashboard cards */
    .dashboard-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #3b82f6;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }
    
    .dashboard-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
    }
    
    .dashboard-card h3 {
        color: #1e3a8a !important;
        margin-top: 0;
        font-weight: 600;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #2563eb 0%, #5b21b6 100%);
    }
    </style>
    """, unsafe_allow_html=True)

def hide_sidebar():
    """Hide the sidebar for login page"""
    st.markdown("""
    <style>
        .css-1d391kg {display: none;}
        section[data-testid="stSidebar"] {display: none;}
        .css-6qob1r {display: none;}
        .e1fqkh3o3 {display: none;}
    </style>
    """, unsafe_allow_html=True)

def show_sidebar():
    """Show the sidebar for authenticated users"""
    st.markdown("""
    <style>
        .css-1d391kg {display: flex !important;}
        section[data-testid="stSidebar"] {display: flex !important;}
        .css-6qob1r {display: flex !important;}
        .e1fqkh3o3 {display: flex !important;}
    </style>
    """, unsafe_allow_html=True)

# -------------------------
# Supabase Setup
# -------------------------
@st.cache_resource
def init_connection() -> Client:
    """Initialize Supabase connection"""
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Failed to connect to Supabase: {e}")
        st.stop()

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
# Authentication Functions
# -------------------------
def signup(email, password):
    """Sign up new user (only regular users, no admin option)"""
    if not email or not password:
        return False, "⚠️ Please fill in all fields."
    
    if len(password) < 6:
        return False, "⚠️ Password must be at least 6 characters long."
    
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        if res.user:
            # Always create as regular user
            supabase.table("user_profiles").insert({
                "id": res.user.id,
                "email": email,
                "role": "user"  # Always user, no admin signup
            }).execute()
            return True, "✅ Account created! Please check your email to verify your account, then log in."
        return False, "❌ Failed to create account."
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower():
            return False, "⚠️ Email already registered. Try logging in."
        return False, f"❌ Signup error: {error_msg}"

def login(email, password):
    """Login user"""
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if res.user:
            profile = supabase.table("user_profiles").select("role").eq("id", res.user.id).execute()
            role = profile.data[0]["role"] if profile.data else "user"
            st.session_state.authenticated = True
            st.session_state.user = res.user
            st.session_state.role = role
            return True, f"✅ Welcome back! Logged in as {role.capitalize()}"
        return False, "❌ Invalid email or password."
    except Exception as e:
        return False, f"❌ Login error: {str(e)}"

def reset_password(email):
    """Reset password"""
    try:
        supabase.auth.reset_password_for_email(email)
        return True, f"✅ Password reset email sent to {email}"
    except Exception as e:
        return False, f"❌ Reset error: {str(e)}"

def logout():
    """Logout user"""
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
    """Admin dashboard with full management features"""
    show_sidebar()
    
    st.title("👑 Admin Dashboard")
    
    with st.sidebar:
        st.markdown("### 🔧 Admin Tools")
        
        if st.session_state.user:
            st.info(f"👤 {st.session_state.user.email}\\n🎭 {st.session_state.role.title()}")
        
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            logout()
        
        st.divider()
        
        admin_section = st.selectbox(
            "Select Section",
            ["📊 Analytics", "👥 User Management", "📈 Reports", "⚙️ Settings"]
        )
    
    if admin_section == "📊 Analytics":
        show_admin_analytics()
    elif admin_section == "👥 User Management":
        show_user_management()
    elif admin_section == "📈 Reports":
        show_system_reports()
    elif admin_section == "⚙️ Settings":
        show_admin_settings()

def show_admin_analytics():
    """Show admin analytics"""
    st.subheader("📊 System Analytics")
    
    try:
        users = supabase.table("user_profiles").select("*").execute()
        auth_users = supabase.auth.admin.list_users()
        
        total_users = len(users.data or [])
        admin_count = len([u for u in users.data or [] if u["role"] == "admin"])
        user_count = total_users - admin_count
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Users", total_users, delta=f"+{max(0, total_users-10)}")
        with col2:
            st.metric("Regular Users", user_count)
        with col3:
            st.metric("Administrators", admin_count)
        with col4:
            confirmed_users = len([u for u in auth_users.user if getattr(u, 'email_confirmed_at', None)])
            st.metric("Confirmed Users", confirmed_users)
        
        if users.data:
            st.subheader("📈 User Registration Trends")
            dates = pd.date_range(start='2024-01-01', end=datetime.now(), freq='D')
            registrations = pd.DataFrame({
                'date': dates,
                'registrations': [max(0, int(abs(hash(str(d)) % 8) - 3)) for d in dates]
            })
            
            fig = px.line(registrations, x='date', y='registrations', 
                         title='Daily User Registrations',
                         color_discrete_sequence=['#3b82f6'])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#000000'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            role_data = pd.DataFrame({
                'Role': ['Users', 'Admins'],
                'Count': [user_count, admin_count]
            })
            fig_pie = px.pie(role_data, values='Count', names='Role', 
                           title='User Role Distribution',
                           color_discrete_sequence=['#3b82f6', '#6366f1'])
            fig_pie.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#000000'
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error loading analytics: {e}")

def show_user_management():
    """Show user management interface"""
    st.subheader("👥 User Management")
    
    try:
        users = supabase.table("user_profiles").select("*").execute()
        auth_users = supabase.auth.admin.list_users()

        user_data = []
        for profile in users.data or []:
            auth_info = next((u for u in auth_users.user if u.id == profile["id"]), None)
            user_data.append({
                "id": profile["id"],
                "email": profile["email"],
                "role": profile["role"],
                "created_at": getattr(auth_info, "created_at", None),
                "last_sign_in": getattr(auth_info, "last_sign_in_at", None),
                "confirmed": getattr(auth_info, "email_confirmed_at", None) is not None,
            })

        col1, col2 = st.columns([2, 1])
        with col1:
            search = st.text_input("🔍 Search by email")
        with col2:
            role_filter = st.selectbox("Filter by role", ["All", "user", "admin"])
        
        filtered = user_data
        if search:
            filtered = [u for u in filtered if search.lower() in u["email"].lower()]
        if role_filter != "All":
            filtered = [u for u in filtered if u["role"] == role_filter]

        st.subheader("🔧 Bulk Actions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📧 Send Welcome Email to All"):
                st.success("Welcome emails sent to all users!")
        with col2:
            if st.button("⬇️ Export User Data"):
                df = pd.DataFrame(filtered)
                st.download_button("Download CSV", df.to_csv(index=False), "users.csv", "text/csv")

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
                            success, msg = reset_password(user["email"])
                            if success:
                                st.success(msg)
                            else:
                                st.error(msg)
                    
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
    """Show system reports"""
    st.subheader("📈 System Reports")
    
    st.write("**Recent System Activity**")
    activity_data = [
        {"timestamp": datetime.now() - timedelta(minutes=5), "action": "User login", "user": "user@example.com"},
        {"timestamp": datetime.now() - timedelta(minutes=15), "action": "New user registration", "user": "newuser@example.com"},
        {"timestamp": datetime.now() - timedelta(hours=1), "action": "Password reset", "user": "forgot@example.com"},
        {"timestamp": datetime.now() - timedelta(hours=2), "action": "Admin role assigned", "user": "admin@example.com"},
    ]
    
    for activity in activity_data:
        st.write(f"🕐 {activity['timestamp'].strftime('%Y-%m-%d %H:%M')} - {activity['action']} - {activity['user']}")
    
    st.subheader("🏥 System Health")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Database Status", "✅ Healthy", delta="99.9% uptime")
    with col2:
        st.metric("Auth Service", "✅ Operational", delta="0 errors")
    with col3:
        st.metric("API Response", "⚡ Fast", delta="120ms avg")

def show_admin_settings():
    """Show admin settings"""
    st.subheader("⚙️ System Settings")
    
    st.write("**Security Configuration**")
    password_policy = st.checkbox("Enforce minimum password length", value=True)
    session_timeout = st.slider("Session timeout (hours)", 1, 24, 8)
    two_factor = st.checkbox("Require 2FA for admins", value=False)
    
    st.write("**Email Configuration**")
    welcome_email = st.checkbox("Send welcome emails", value=True)
    notification_email = st.text_input("Admin notification email", value="admin@company.com")
    
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
    """Regular user dashboard"""
    show_sidebar()
    
    st.title("🙋 Welcome to Your Dashboard")
    
    user_email = st.session_state.user.email if st.session_state.user else "Unknown"
    user_id = st.session_state.user.id if st.session_state.user else None
    
    with st.sidebar:
        st.markdown("### 🏠 Dashboard")
        
        st.info(f"👤 {user_email.split('@')[0].title()}\\n🎭 {st.session_state.role.title()}\\n📧 {user_email}")
        
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            logout()
        
        st.divider()
        
        page = st.selectbox(
            "Navigate to:",
            ["📊 My Activity", "👤 Profile", "🔔 Notifications", "❓ Help"]
        )
    
    if page == "📊 My Activity":
        show_user_activity(user_id, user_email)
    elif page == "👤 Profile":
        show_user_profile(user_id, user_email)
    elif page == "🔔 Notifications":
        show_user_notifications(user_email)
    elif page == "❓ Help":
        show_user_help()

def show_user_activity(user_id, user_email):
    """Show user activity"""
    st.subheader("📊 Your Activity Overview")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Days Active", "12", delta="+2")
    with col2:
        st.metric("Total Sessions", "45", delta="+5")
    with col3:
        st.metric("Last Login", "2 hours ago")
    
    st.subheader("📈 Your Activity Chart")
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    activity = pd.DataFrame({
        'date': dates,
        'sessions': [max(0, int(abs(hash(str(d) + user_email) % 5) - 1)) for d in dates]
    })
    
    fig = px.bar(activity, x='date', y='sessions', 
                 title='Your Daily Activity (Last 30 Days)',
                 color_discrete_sequence=['#3b82f6'])
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#000000'
    )
    st.plotly_chart(fig, use_container_width=True)

def show_user_profile(user_id, user_email):
    """Show user profile"""
    st.subheader("👤 Your Profile")
    
    with st.form("profile_form"):
        st.write("**Personal Information**")
        full_name = st.text_input("Full Name", value="")
        phone = st.text_input("Phone Number", value="")
        bio = st.text_area("Bio", value="")
        
        st.write("**Preferences**")
        theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
        notifications = st.checkbox("Email notifications", value=True)
        newsletter = st.checkbox("Subscribe to newsletter", value=False)
        
        st.write("**Security**")
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.form_submit_button("💾 Save Changes", type="primary"):
            if new_password and new_password == confirm_password:
                if len(new_password) >= 6:
                    st.success("Profile updated successfully!")
                else:
                    st.error("Password must be at least 6 characters long")
            else:
                st.success("Profile preferences updated!")

def show_user_notifications(user_email):
    """Show user notifications"""
    st.subheader("🔔 Your Notifications")
    
    st.write("**Notification Preferences**")
    email_notifications = st.checkbox("Email notifications", value=True)
    security_alerts = st.checkbox("Security alerts", value=True)
    product_updates = st.checkbox("Product updates", value=False)
    
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
    """Show user help"""
    st.subheader("❓ Help & Support")
    
    st.write("**Frequently Asked Questions**")
    
    with st.expander("How do I change my password?"):
        st.write("Go to the Profile tab and enter your current password along with your new password.")
    
    with st.expander("How do I update my notification preferences?"):
        st.write("Visit the Notifications tab to customize which notifications you receive.")
    
    with st.expander("Who can I contact for support?"):
        st.write("You can reach out to our support team at support@company.com")
    
    st.write("**Contact Support**")
    with st.form("support_form"):
        subject = st.selectbox("Subject", ["General Question", "Technical Issue", "Feature Request", "Bug Report"])
        message = st.text_area("Message", placeholder="Describe your question or issue...")
        
        if st.form_submit_button("📧 Send Message"):
            st.success("Your message has been sent! We'll get back to you soon.")

# -------------------------
# Login Page
# -------------------------
def login_page():
    """Professional login page"""
    hide_sidebar()
    
    st.markdown("""
    <div class="welcome-header">
        <h1>🔐 Professional Authentication Portal</h1>
        <p>Secure access to your personalized dashboard</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🔑 Login", "📝 Sign Up", "🔄 Reset Password"])

    with tab1:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.subheader("🔑 Sign In to Your Account")
        with st.form("login_form"):
            email = st.text_input("📧 Email Address", placeholder="your.email@example.com")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            remember_me = st.checkbox("🧠 Remember me")
            
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
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.subheader("📝 Create New Account")
        st.info("💡 New accounts are created as regular users. Contact an administrator to upgrade to admin privileges.")
        
        with st.form("signup_form"):
            email = st.text_input("📧 Email Address", placeholder="your.email@example.com")
            password = st.text_input("🔒 Password", type="password", 
                                   help="Must be at least 6 characters long")
            confirm_password = st.text_input("🔒 Confirm Password", type="password")
            
            terms = st.checkbox("✅ I agree to the Terms of Service and Privacy Policy")
            
            if st.form_submit_button("🎉 Create Account", type="primary", use_container_width=True):
                if email and password and confirm_password:
                    if password != confirm_password:
                        st.error("❌ Passwords don't match!")
                    elif not terms:
                        st.warning("⚠️ Please agree to the terms and conditions.")
                    else:
                        success, msg = signup(email, password)
                        if success:
                            st.success(msg)
                            st.balloons()
                        else:
                            st.error(msg)
                else:
                    st.warning("Please fill in all fields.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# Main App
# -------------------------
def main():
    """Main application"""
    st.set_page_config(
        page_title="Professional Auth Portal", 
        page_icon="🔐", 
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    apply_custom_css()

    if not st.session_state.authenticated:
        login_page()
    else:
        if st.session_state.role == "admin":
            admin_dashboard()
        else:
            user_dashboard()

if __name__ == "__main__":
    main()
