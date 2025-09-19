import streamlit as st
import os
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import json

@st.cache_resource
def init_service_client():
    """Initialize Supabase service role client with caching"""
    try:
        url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
        service_key = st.secrets.get("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not service_key:
            st.error("❌ Missing Supabase configuration. Please check your secrets.toml file.")
            st.stop()
        
        # Test connection
        client = create_client(url, service_key)
        
        # Test with a simple query
        test_response = client.table("profiles").select("id").limit(1).execute()
        
        st.success("✅ Service role client initialized successfully")
        return client
        
    except Exception as e:
        st.error(f"❌ Failed to initialize service client: {str(e)}")
        st.stop()

def get_all_users(supabase: Client):
    """Get all users with profiles and roles"""
    try:
        # Get auth users
        auth_response = supabase.auth.admin.list_users()
        
        if hasattr(auth_response, 'data') and hasattr(auth_response.data, 'users'):
            auth_users = auth_response.data.users
        elif isinstance(auth_response, list):
            auth_users = auth_response
        else:
            auth_users = []
        
        # Get profiles
        profiles_response = supabase.table("profiles").select("*").execute()
        profiles = {p['id']: p for p in profiles_response.data} if profiles_response.data else {}
        
        # Get user roles
        roles_response = supabase.table("user_roles").select("*").execute()
        user_roles = {r['user_id']: r['role'] for r in roles_response.data} if roles_response.data else {}
        
        # Combine data
        users = []
        for user in auth_users:
            profile = profiles.get(user.id, {})
            role = user_roles.get(user.id, profile.get('role', 'user'))
            
            users.append({
                'id': user.id,
                'email': user.email,
                'created_at': user.created_at,
                'email_confirmed_at': user.email_confirmed_at,
                'last_sign_in_at': user.last_sign_in_at,
                'role': role,
                'full_name': profile.get('full_name', ''),
                'avatar_url': profile.get('avatar_url', ''),
                'updated_at': profile.get('updated_at', '')
            })
        
        return users
        
    except Exception as e:
        st.error(f"❌ Error fetching users: {str(e)}")
        return []

def create_admin_user(supabase: Client, email: str, password: str, full_name: str = ""):
    """Create a new admin user"""
    try:
        # Create user with service role (bypasses email confirmation)
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
            
            return True, f"Admin user created successfully: {email}"
        else:
            return False, "Failed to create user"
            
    except Exception as e:
        return False, f"Error creating admin user: {str(e)}"

def promote_user_to_admin(supabase: Client, email: str):
    """Promote existing user to admin"""
    try:
        # Find user by email
        users = get_all_users(supabase)
        user = next((u for u in users if u['email'] == email), None)
        
        if not user:
            return False, "User not found"
        
        user_id = user['id']
        
        # Update profile role
        supabase.table("profiles").upsert({
            "id": user_id,
            "role": "admin"
        }).execute()
        
        # Update user roles
        supabase.table("user_roles").upsert({
            "user_id": user_id,
            "role": "admin"
        }).execute()
        
        return True, f"User {email} promoted to admin successfully"
        
    except Exception as e:
        return False, f"Error promoting user: {str(e)}"

def main():
    st.set_page_config(
        page_title="Admin User Management",
        page_icon="👑",
        layout="wide"
    )
    
    st.title("👑 Admin User Management")
    st.markdown("Manage users with service role privileges")
    
    # Initialize service client
    supabase = init_service_client()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    tab = st.sidebar.selectbox("Choose Action", [
        "View All Users",
        "Create Admin User", 
        "Promote User to Admin",
        "User Search & Filter"
    ])
    
    if tab == "View All Users":
        st.header("📋 All Users")
        
        if st.button("🔄 Refresh Users"):
            st.cache_resource.clear()
        
        users = get_all_users(supabase)
        
        if users:
            df = pd.DataFrame(users)
            st.dataframe(df, use_container_width=True)
            
            # Summary stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Users", len(users))
            with col2:
                admin_count = len([u for u in users if u['role'] == 'admin'])
                st.metric("Admin Users", admin_count)
            with col3:
                confirmed_count = len([u for u in users if u['email_confirmed_at']])
                st.metric("Confirmed Users", confirmed_count)
        else:
            st.warning("No users found or error fetching users")
    
    elif tab == "Create Admin User":
        st.header("➕ Create New Admin User")
        
        with st.form("create_admin"):
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            full_name = st.text_input("Full Name (Optional)")
            
            if st.form_submit_button("Create Admin User"):
                if email and password:
                    success, message = create_admin_user(supabase, email, password, full_name)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("Please provide email and password")
    
    elif tab == "Promote User to Admin":
        st.header("⬆️ Promote User to Admin")
        
        users = get_all_users(supabase)
        non_admin_users = [u for u in users if u['role'] != 'admin']
        
        if non_admin_users:
            user_options = {f"{u['email']} ({u['full_name']})" if u['full_name'] else u['email']: u['email'] 
                          for u in non_admin_users}
            
            selected_user = st.selectbox("Select User to Promote", list(user_options.keys()))
            
            if st.button("Promote to Admin"):
                email = user_options[selected_user]
                success, message = promote_user_to_admin(supabase, email)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        else:
            st.info("No non-admin users found")
    
    elif tab == "User Search & Filter":
        st.header("🔍 Search & Filter Users")
        
        users = get_all_users(supabase)
        
        if users:
            # Search and filter options
            col1, col2 = st.columns(2)
            
            with col1:
                search_term = st.text_input("Search by email or name")
            
            with col2:
                role_filter = st.selectbox("Filter by role", ["All", "admin", "user"])
            
            # Apply filters
            filtered_users = users
            
            if search_term:
                filtered_users = [u for u in filtered_users 
                                if search_term.lower() in u['email'].lower() 
                                or search_term.lower() in u.get('full_name', '').lower()]
            
            if role_filter != "All":
                filtered_users = [u for u in filtered_users if u['role'] == role_filter]
            
            st.write(f"Found {len(filtered_users)} users")
            
            if filtered_users:
                df = pd.DataFrame(filtered_users)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No users match your search criteria")

if __name__ == "__main__":
    main()
