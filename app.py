import streamlit as st
from supabase import create_client, Client
import hashlib
import re
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, Dict, Any, List
import time

# -------------------------
# Hide Streamlit Settings & Styling
# -------------------------
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display:none;}
.stDecoration {display:none;}
</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# -------------------------
# Supabase Setup
# -------------------------
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_ANON_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Failed to initialize Supabase: {e}")
        return None

@st.cache_resource
def init_service_client():
    try:
        url = st.secrets["SUPABASE_URL"]
        service_key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
        return create_client(url, service_key)
    except Exception as e:
        st.error(f"Failed to initialize service client: {e}")
        return None

supabase_client = init_supabase()
service_client = init_service_client()

# -------------------------
# Session State
# -------------------------
if "user" not in st.session_state:
    st.session_state.user = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None

# -------------------------
# Password Validator
# -------------------------
def is_strong_password(password: str) -> bool:
    """Password must be at least 6 chars"""
    return len(password) >= 6

# -------------------------
# Signup Function
# -------------------------
def signup_user(email: str, full_name: str, password: str) -> Dict[str, Any]:
    """Create a pending signup request that requires admin approval"""
    try:
        # Hash password for storage
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Insert into pending_signups table
        result = supabase_client.table("pending_signups").insert({
            "email": email,
            "full_name": full_name,
            "password_hash": password_hash,
            "status": "pending"
        }).execute()
        
        if result.data:
            return {"success": True, "message": "Signup request submitted! Please wait for admin approval."}
        else:
            return {"success": False, "message": "Failed to submit signup request"}
            
    except Exception as e:
        return {"success": False, "message": f"Signup error: {str(e)}"}

# -------------------------
# Login Function
# -------------------------
def login_user(email: str, password: str) -> Dict[str, Any]:
    """Login user with approval status check"""
    try:
        # First check if user has been approved
        pending_check = supabase_client.table("pending_signups").select("*").eq("email", email).eq("status", "approved").execute()
        
        if not pending_check.data:
            # Check if user has a pending request
            pending_request = supabase_client.table("pending_signups").select("*").eq("email", email).execute()
            if pending_request.data:
                status = pending_request.data[0]["status"]
                if status == "pending":
                    return {"success": False, "message": "Your account is pending admin approval"}
                elif status == "rejected":
                    return {"success": False, "message": "Your signup request was rejected"}
            else:
                return {"success": False, "message": "Please sign up first"}
        
        # Try to sign in with Supabase
        response = supabase_client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            return {"success": True, "user": response.user, "message": "Login successful"}
        else:
            return {"success": False, "message": "Invalid credentials"}
            
    except Exception as e:
        return {"success": False, "message": f"Login error: {str(e)}"}

# -------------------------
# Admin Dashboard
# -------------------------
def show_admin_dashboard():
    """Admin dashboard with pending signup management"""
    st.title("👨‍💼 Admin Dashboard")
    
    # Sidebar for navigation
    with st.sidebar:
        st.write(f"Welcome, Admin!")
        if st.button("Logout"):
            st.session_state.user = None
            st.session_state.user_role = None
            st.rerun()
    
    tab1, tab2, tab3 = st.tabs(["Pending Approvals", "User Management", "Analytics"])
    
    with tab1:
        st.subheader("📋 Pending Signup Approvals")
        
        pending_signups = get_pending_signups()
        
        if pending_signups:
            for signup in pending_signups:
                with st.expander(f"📧 {signup['email']} - {signup['full_name']}"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**Name:** {signup['full_name']}")
                        st.write(f"**Email:** {signup['email']}")
                        st.write(f"**Requested:** {signup['created_at'][:10]}")
                    
                    with col2:
                        if st.button("✅ Approve", key=f"approve_{signup['id']}"):
                            result = approve_signup(signup['id'], st.session_state.user.id)
                            if result["success"]:
                                st.success(result["message"])
                                st.rerun()
                            else:
                                st.error(result["message"])
                    
                    with col3:
                        if st.button("❌ Reject", key=f"reject_{signup['id']}"):
                            reason = st.text_input("Rejection reason (optional)", key=f"reason_{signup['id']}")
                            result = reject_signup(signup['id'], st.session_state.user.id, reason)
                            if result["success"]:
                                st.success(result["message"])
                                st.rerun()
                            else:
                                st.error(result["message"])
        else:
            st.info("No pending signup requests")
    
    with tab2:
        st.subheader("👥 User Management")
        # ... existing user management code ...
    
    with tab3:
        st.subheader("📊 Analytics")
        # ... existing analytics code ...

# -------------------------
# User Dashboard
# -------------------------
def show_user_dashboard():
    """Regular user dashboard"""
    st.title("👤 User Dashboard")
    
    with st.sidebar:
        st.write(f"Welcome, {st.session_state.user.email}!")
        if st.button("Logout"):
            st.session_state.user = None
            st.session_state.user_role = None
            st.rerun()
    
    st.info("Welcome to your dashboard!")

# -------------------------
# Admin Functions
# -------------------------
def get_pending_signups():
    """Get all pending signup requests"""
    try:
        result = service_client.table("pending_signups").select("*").eq("status", "pending").order("created_at", desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        st.error(f"Error fetching pending signups: {e}")
        return []

def approve_signup(signup_id: str, admin_id: str):
    """Approve a pending signup and create the actual user account"""
    try:
        # Get the pending signup details
        signup_result = service_client.table("pending_signups").select("*").eq("id", signup_id).single().execute()
        
        if not signup_result.data:
            return {"success": False, "message": "Signup request not found"}
        
        signup_data = signup_result.data
        
        # Create the actual user account using service role
        user_result = service_client.auth.admin.create_user({
            "email": signup_data["email"],
            "password": "temp_password_123",  # User will need to reset
            "email_confirm": True,
            "user_metadata": {
                "full_name": signup_data["full_name"]
            }
        })
        
        if user_result.user:
            # Create profile for the new user
            profile_result = service_client.table("profiles").insert({
                "id": user_result.user.id,
                "email": signup_data["email"],
                "full_name": signup_data["full_name"],
                "role": "user",
                "created_at": datetime.now().isoformat()
            }).execute()
            
            # Update pending signup status
            service_client.table("pending_signups").update({
                "status": "approved",
                "approved_by": admin_id,
                "approved_at": datetime.now().isoformat()
            }).eq("id", signup_id).execute()
            
            return {"success": True, "message": f"User {signup_data['email']} approved successfully"}
        else:
            return {"success": False, "message": "Failed to create user account"}
            
    except Exception as e:
        return {"success": False, "message": f"Error approving signup: {str(e)}"}

def reject_signup(signup_id: str, admin_id: str, reason: str = ""):
    """Reject a pending signup"""
    try:
        result = service_client.table("pending_signups").update({
            "status": "rejected",
            "approved_by": admin_id,
            "approved_at": datetime.now().isoformat(),
            "rejection_reason": reason
        }).eq("id", signup_id).execute()
        
        if result.data:
            return {"success": True, "message": "Signup request rejected"}
        else:
            return {"success": False, "message": "Failed to reject signup"}
            
    except Exception as e:
        return {"success": False, "message": f"Error rejecting signup: {str(e)}"}

# -------------------------
# Main App
# -------------------------
def main():
    if not supabase_client:
        st.error("Unable to connect to database. Please check configuration.")
        return
    
    # Authentication UI
    if not st.session_state.user:
        st.title("🔐 Admin Portal")
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            st.subheader("Login")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", type="primary"):
                if email and password:
                    result = login_user(email, password)
                    if result["success"]:
                        st.session_state.user = result["user"]
                        # Get user role
                        profile = supabase_client.table("profiles").select("role").eq("id", result["user"].id).single().execute()
                        if profile.data:
                            st.session_state.user_role = profile.data["role"]
                        st.success(result["message"])
                        st.rerun()
                    else:
                        st.error(result["message"])
                else:
                    st.warning("Please fill in all fields")
        
        with tab2:
            st.subheader("Sign Up")
            st.info("New user registrations require admin approval")
            
            full_name = st.text_input("Full Name", key="signup_name")
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
            
            if st.button("Sign Up", type="primary"):
                if full_name and email and password and confirm_password:
                    if password != confirm_password:
                        st.error("Passwords don't match")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        result = signup_user(email, full_name, password)
                        if result["success"]:
                            st.success(result["message"])
                        else:
                            st.error(result["message"])
                else:
                    st.warning("Please fill in all fields")
    
    else:
        # User is logged in
        if st.session_state.user_role == "admin":
            show_admin_dashboard()
        else:
            show_user_dashboard()

if __name__ == "__main__":
    main()
