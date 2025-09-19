import streamlit as st
from supabase import create_client, Client
import os
from datetime import datetime
import pandas as pd

# Initialize Supabase client with service role key
def init_service_client():
    """Initialize Supabase client with service role key for admin operations"""
    url = st.secrets["SUPABASE_URL"]
    service_key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]  # Service role key bypasses RLS
    return create_client(url, service_key)

def create_admin_user(email: str, password: str, full_name: str = None):
    """Create an admin user with elevated privileges"""
    supabase = init_service_client()
    
    try:
        # Create user with service role (bypasses email confirmation)
        auth_response = supabase.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,  # Auto-confirm email
            "user_metadata": {
                "full_name": full_name or email.split("@")[0],
                "role": "admin",
                "created_by": "system_admin"
            }
        })
        
        if auth_response.user:
            user_id = auth_response.user.id
            
            # Insert user profile with admin role
            profile_data = {
                "id": user_id,
                "email": email,
                "full_name": full_name or email.split("@")[0],
                "role": "admin",
                "created_at": datetime.now().isoformat(),
                "is_active": True
            }
            
            # Insert into profiles table
            supabase.table("profiles").insert(profile_data).execute()
            
            return True, f"Admin user {email} created successfully"
        else:
            return False, "Failed to create user"
            
    except Exception as e:
        return False, f"Error creating admin user: {str(e)}"

def promote_user_to_admin(email: str):
    """Promote an existing user to admin role"""
    supabase = init_service_client()
    
    try:
        # Find user by email
        user_response = supabase.table("profiles").select("*").eq("email", email).execute()
        
        if not user_response.data:
            return False, f"User {email} not found"
        
        user = user_response.data[0]
        user_id = user["id"]
        
        # Update user role to admin
        supabase.table("profiles").update({
            "role": "admin",
            "updated_at": datetime.now().isoformat()
        }).eq("id", user_id).execute()
        
        # Update user metadata
        supabase.auth.admin.update_user_by_id(user_id, {
            "user_metadata": {
                **user.get("user_metadata", {}),
                "role": "admin"
            }
        })
        
        return True, f"User {email} promoted to admin successfully"
        
    except Exception as e:
        return False, f"Error promoting user: {str(e)}"

def list_all_users():
    """List all users with their roles"""
    supabase = init_service_client()
    
    try:
        response = supabase.table("profiles").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching users: {str(e)}")
        return []

def main():
    st.set_page_config(page_title="Admin User Management", page_icon="👑")
    
    st.title("👑 Admin User Management")
    st.markdown("---")
    
    # Check if service role key is configured
    if "SUPABASE_SERVICE_ROLE_KEY" not in st.secrets:
        st.error("⚠️ SUPABASE_SERVICE_ROLE_KEY not found in secrets.toml")
        st.info("Add your Supabase service role key to secrets.toml to use admin functions")
        return
    
    tab1, tab2, tab3 = st.tabs(["Create Admin", "Promote User", "User List"])
    
    with tab1:
        st.header("Create New Admin User")
        
        with st.form("create_admin"):
            email = st.text_input("Email Address", placeholder="admin@example.com")
            password = st.text_input("Password", type="password", placeholder="Strong password")
            full_name = st.text_input("Full Name (Optional)", placeholder="Admin User")
            
            if st.form_submit_button("Create Admin User", type="primary"):
                if email and password:
                    success, message = create_admin_user(email, password, full_name)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("Please provide both email and password")
    
    with tab2:
        st.header("Promote Existing User to Admin")
        
        with st.form("promote_user"):
            email = st.text_input("User Email", placeholder="user@example.com")
            
            if st.form_submit_button("Promote to Admin", type="primary"):
                if email:
                    success, message = promote_user_to_admin(email)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("Please provide user email")
    
    with tab3:
        st.header("All Users")
        
        if st.button("Refresh User List"):
            st.rerun()
        
        users = list_all_users()
        
        if users:
            df = pd.DataFrame(users)
            
            # Display user statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Users", len(users))
            with col2:
                admin_count = len([u for u in users if u.get("role") == "admin"])
                st.metric("Admin Users", admin_count)
            with col3:
                active_count = len([u for u in users if u.get("is_active", True)])
                st.metric("Active Users", active_count)
            
            # Display users table
            st.dataframe(
                df[["email", "full_name", "role", "created_at", "is_active"]],
                use_container_width=True
            )
        else:
            st.info("No users found")

if __name__ == "__main__":
    main()
