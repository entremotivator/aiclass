import streamlit as st
from supabase import create_client, Client
import re

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
            try:
                supabase.table("user_profiles").insert({
                    "id": res.user.id,
                    "email": email,
                    "role": role
                }).execute()
            except Exception as profile_error:
                return False, f"Account created but profile setup failed: {str(profile_error)}"
            
            return True, "✅ Account created! Please check your email to verify your account, then log in."
        else:
            return False, "❌ Failed to create account. Please try again."
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower():
            return False, "⚠️ This email is already registered. Try logging in instead."
        return False, f"❌ Signup error: {error_msg}"

# -------------------------
# Login Function
# -------------------------
def login(email, password):
    if not email or not password:
        return False, "⚠️ Please fill in all fields."
    
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if res.user:
            try:
                profile = supabase.table("user_profiles").select("role").eq("id", res.user.id).execute()
                role = profile.data[0]["role"] if profile.data else "user"
            except Exception:
                role = "user"  # Default role if profile lookup fails
            
            st.session_state.authenticated = True
            st.session_state.user = res.user
            st.session_state.role = role
            return True, f"✅ Welcome back! Logged in as {role.capitalize()}"
        else:
            return False, "❌ Login failed. Please check your credentials."
    except Exception as e:
        error_msg = str(e)
        if "invalid login credentials" in error_msg.lower():
            return False, "❌ Invalid email or password. Please try again."
        elif "email not confirmed" in error_msg.lower():
            return False, "⚠️ Please check your email and confirm your account first."
        return False, f"❌ Login error: {error_msg}"

# -------------------------
# Password Reset
# -------------------------
def reset_password(email):
    if not email:
        return False, "⚠️ Please enter your email address."
    
    try:
        supabase.auth.reset_password_for_email(email)
        return True, f"✅ Password reset email sent to {email}. Please check your inbox."
    except Exception as e:
        return False, f"❌ Reset error: {str(e)}"

# -------------------------
# Logout Function
# -------------------------
def logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass  # Continue with logout even if API call fails
    
    st.session_state.authenticated = False
    st.session_state.role = None
    st.session_state.user = None
    st.rerun()

# -------------------------
# Admin Dashboard
# -------------------------
def admin_dashboard():
    st.title("👑 Admin Dashboard")
    
    col1, col2 = st.columns(2)
    
    try:
        users = supabase.table("user_profiles").select("*").execute()
        total_users = len(users.data) if users.data else 0
        admin_count = len([u for u in users.data if u.get('role') == 'admin']) if users.data else 0
        
        with col1:
            st.metric("Total Users", total_users)
        with col2:
            st.metric("Admins", admin_count)
        
        st.subheader("📋 User Management")
        
        if users.data:
            for i, user in enumerate(users.data):
                with st.expander(f"👤 {user['email']} ({user['role'].title()})"):
                    st.write(f"**User ID:** {user['id']}")
                    st.write(f"**Email:** {user['email']}")
                    st.write(f"**Role:** {user['role'].title()}")
                    
                    # Role update functionality
                    new_role = st.selectbox(
                        "Change Role:", 
                        ["user", "admin"], 
                        index=0 if user['role'] == 'user' else 1,
                        key=f"role_{i}"
                    )
                    
                    if st.button(f"Update Role", key=f"update_{i}"):
                        try:
                            supabase.table("user_profiles").update({"role": new_role}).eq("id", user['id']).execute()
                            st.success(f"✅ Updated {user['email']} to {new_role}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Failed to update role: {str(e)}")
        else:
            st.info("No users found in the database.")
            
    except Exception as e:
        st.error(f"❌ Error loading users: {str(e)}")
    
    st.divider()
    if st.button("🚪 Logout", type="primary"):
        logout()

# -------------------------
# User Dashboard
# -------------------------
def user_dashboard():
    st.title("🙋 User Dashboard")
    
    user_email = st.session_state.user.email if st.session_state.user else "Unknown"
    st.write(f"**Welcome back, {user_email}!** 👋")
    
    # User info card
    with st.container():
        st.subheader("📊 Your Account")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Email:** {user_email}")
        with col2:
            st.info(f"**Role:** {st.session_state.role.title()}")
    
    st.subheader("🚀 Quick Actions")
    st.write("This is where you can add user-specific features and functionality.")
    
    # Example user actions
    if st.button("🔄 Refresh Profile"):
        st.success("Profile refreshed!")
    
    st.divider()
    if st.button("🚪 Logout", type="primary"):
        logout()

# -------------------------
# Redirect Logged-in Users
# -------------------------
def redirect_dashboard():
    if st.session_state.role == "admin":
        admin_dashboard()
    else:
        user_dashboard()

# -------------------------
# Main App UI
# -------------------------
def main():
    st.set_page_config(
        page_title="Supabase Auth App",
        page_icon="🔐",
        layout="wide"
    )
    
    if not st.session_state.authenticated:
        st.title("🔐 Supabase Authentication")
        st.write("Welcome! Please login or create an account to continue.")

        tab1, tab2, tab3 = st.tabs(["🔑 Login", "📝 Sign Up", "🔄 Reset Password"])

        # ----- LOGIN -----
        with tab1:
            st.subheader("Login to Your Account")
            
            with st.form("login_form"):
                login_email = st.text_input("📧 Email", placeholder="Enter your email")
                login_password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                login_submitted = st.form_submit_button("🔑 Login", type="primary")
                
                if login_submitted:
                    with st.spinner("Logging in..."):
                        success, msg = login(login_email, login_password)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

        # ----- SIGNUP -----
        with tab2:
            st.subheader("Create New Account")
            
            with st.form("signup_form"):
                signup_email = st.text_input("📧 Email", placeholder="Enter your email")
                signup_password = st.text_input("🔒 Password", type="password", placeholder="Create a strong password")
                
                st.caption("Password must be at least 12 characters with uppercase, lowercase, number, and special character.")
                
                role = st.selectbox("👤 Role", ["user", "admin"], help="Select your account type")
                signup_submitted = st.form_submit_button("📝 Create Account", type="primary")
                
                if signup_submitted:
                    with st.spinner("Creating account..."):
                        success, msg = signup(signup_email, signup_password, role)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)

        # ----- RESET PASSWORD -----
        with tab3:
            st.subheader("Reset Your Password")
            
            with st.form("reset_form"):
                reset_email = st.text_input("📧 Email", placeholder="Enter your registered email")
                reset_submitted = st.form_submit_button("📧 Send Reset Email", type="primary")
                
                if reset_submitted:
                    with st.spinner("Sending reset email..."):
                        success, msg = reset_password(reset_email)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)

    else:
        redirect_dashboard()

# -------------------------
# Run the App
# -------------------------
if __name__ == "__main__":
    main()
