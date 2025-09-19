import streamlit as st
from supabase import create_client, Client
import os
from typing import Optional

# Initialize Supabase client with service role key
@st.cache_resource
def init_service_client():
    url = st.secrets["SUPABASE_URL"]
    service_key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
    return create_client(url, service_key)

def get_user_by_email(email: str) -> Optional[dict]:
    """Get user by email using service role client"""
    supabase = init_service_client()
    try:
        # Get user from auth.users
        response = supabase.auth.admin.list_users()
        users = response.data.users if hasattr(response.data, 'users') else []
        
        for user in users:
            if user.email == email:
                return user
        return None
    except Exception as e:
        st.error(f"Error fetching user: {str(e)}")
        return None

def create_admin_user(email: str, password: str, full_name: str) -> bool:
    """Create a new admin user with service role privileges"""
    supabase = init_service_client()
    try:
        # Create user with auto-confirm
        response = supabase.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,  # Auto-confirm email
            "user_metadata": {
                "full_name": full_name,
                "role": "admin"
            }
        })
        
        if response.user:
            user_id = response.user.id
            
            # Insert into profiles table
            supabase.table("profiles").insert({
                "id": user_id,
                "full_name": full_name,
                "role": "admin"
            }).execute()
            
            # Insert into user_roles table
            supabase.table("user_roles").insert({
                "user_id": user_id,
                "role": "admin"
            }).execute()
            
            return True
    except Exception as e:
        st.error(f"Error creating admin user: {str(e)}")
        return False

def promote_user_to_admin(email: str) -> bool:
    """Promote existing user to admin role"""
    supabase = init_service_client()
    try:
        user = get_user_by_email(email)
        if not user:
            st.error("User not found")
            return False
            
        user_id = user.id
        
        # Update profiles table
        supabase.table("profiles").update({
            "role": "admin"
        }).eq("id", user_id).execute()
        
        # Insert or update user_roles table
        existing_role = supabase.table("user_roles").select("*").eq("user_id", user_id).execute()
        
        if existing_role.data:
            # Update existing role
            supabase.table("user_roles").update({
                "role": "admin"
            }).eq("user_id", user_id).execute()
        else:
            # Insert new role
            supabase.table("user_roles").insert({
                "user_id": user_id,
                "role": "admin"
            }).execute()
        
        # Update user metadata
        supabase.auth.admin.update_user_by_id(user_id, {
            "user_metadata": {
                **user.user_metadata,
                "role": "admin"
            }
        })
        
        return True
    except Exception as e:
        st.error(f"Error promoting user: {str(e)}")
        return False

def list_admin_users():
    """List all admin users"""
    supabase = init_service_client()
    try:
        # Get admin users from profiles table
        response = supabase.table("profiles").select("*").eq("role", "admin").execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching admin users: {str(e)}")
        return []

def main():
    st.set_page_config(page_title="Admin User Management", page_icon="👑")
    
    st.title("👑 Admin User Management")
    st.markdown("Manage admin users with service role privileges")
    
    # Check if service role key is configured
    if "SUPABASE_SERVICE_ROLE_KEY" not in st.secrets:
        st.error("⚠️ SUPABASE_SERVICE_ROLE_KEY not found in secrets.toml")
        st.code("""
# Add this to your secrets.toml file:
SUPABASE_SERVICE_ROLE_KEY = "your_service_role_key_here"
        """)
        return
    
    tab1, tab2, tab3 = st.tabs(["Create Admin", "Promote User", "List Admins"])
    
    with tab1:
        st.header("Create New Admin User")
        
        with st.form("create_admin"):
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            full_name = st.text_input("Full Name")
            
            if st.form_submit_button("Create Admin User"):
                if email and password and full_name:
                    if create_admin_user(email, password, full_name):
                        st.success(f"✅ Admin user created successfully: {email}")
                        st.rerun()
                    else:
                        st.error("❌ Failed to create admin user")
                else:
                    st.error("Please fill in all fields")
    
    with tab2:
        st.header("Promote Existing User to Admin")
        
        with st.form("promote_user"):
            email = st.text_input("User Email Address")
            
            if st.form_submit_button("Promote to Admin"):
                if email:
                    if promote_user_to_admin(email):
                        st.success(f"✅ User promoted to admin: {email}")
                        st.rerun()
                    else:
                        st.error("❌ Failed to promote user")
                else:
                    st.error("Please enter an email address")
    
    with tab3:
        st.header("Current Admin Users")
        
        admin_users = list_admin_users()
        
        if admin_users:
            for admin in admin_users:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{admin.get('full_name', 'N/A')}**")
                        st.write(f"ID: `{admin['id']}`")
                    with col2:
                        st.write("👑 Admin")
                    st.divider()
        else:
            st.info("No admin users found")
        
        if st.button("🔄 Refresh List"):
            st.rerun()

if __name__ == "__main__":
    main()
