import streamlit as st
from supabase import create_client, Client
import os
from typing import Optional, List
import pandas as pd
from datetime import datetime

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

def get_user_by_id(user_id: str) -> Optional[dict]:
    """Get user by ID using service role client"""
    supabase = init_service_client()
    try:
        response = supabase.auth.admin.get_user_by_id(user_id)
        return response.user if response.user else None
    except Exception as e:
        st.error(f"Error fetching user by ID: {str(e)}")
        return None

def get_all_users() -> List[dict]:
    """Get all users with their profile information"""
    supabase = init_service_client()
    try:
        # Get all users from auth
        auth_response = supabase.auth.admin.list_users()
        auth_users = auth_response.data.users if hasattr(auth_response.data, 'users') else []
        
        # Get all profiles
        profiles_response = supabase.table("profiles").select("*").execute()
        profiles = {profile['id']: profile for profile in profiles_response.data}
        
        # Get all user roles
        roles_response = supabase.table("user_roles").select("*").execute()
        roles = {role['user_id']: role['role'] for role in roles_response.data}
        
        # Combine the data
        combined_users = []
        for user in auth_users:
            profile = profiles.get(user.id, {})
            role = roles.get(user.id, profile.get('role', 'user'))
            
            combined_users.append({
                'id': user.id,
                'email': user.email,
                'full_name': profile.get('full_name', user.user_metadata.get('full_name', 'N/A')),
                'role': role,
                'created_at': user.created_at,
                'last_sign_in_at': user.last_sign_in_at,
                'email_confirmed_at': user.email_confirmed_at,
                'phone': user.phone,
                'user_metadata': user.user_metadata,
                'app_metadata': user.app_metadata
            })
        
        return combined_users
    except Exception as e:
        st.error(f"Error fetching all users: {str(e)}")
        return []

def update_user_profile(user_id: str, full_name: str, role: str) -> bool:
    """Update user profile and role"""
    supabase = init_service_client()
    try:
        # Update profiles table
        supabase.table("profiles").upsert({
            "id": user_id,
            "full_name": full_name,
            "role": role
        }).execute()
        
        # Update user_roles table
        existing_role = supabase.table("user_roles").select("*").eq("user_id", user_id).execute()
        
        if existing_role.data:
            supabase.table("user_roles").update({"role": role}).eq("user_id", user_id).execute()
        else:
            supabase.table("user_roles").insert({"user_id": user_id, "role": role}).execute()
        
        # Update user metadata
        supabase.auth.admin.update_user_by_id(user_id, {
            "user_metadata": {
                "full_name": full_name,
                "role": role
            }
        })
        
        return True
    except Exception as e:
        st.error(f"Error updating user profile: {str(e)}")
        return False

def delete_user(user_id: str) -> bool:
    """Delete user (soft delete by updating metadata)"""
    supabase = init_service_client()
    try:
        # Note: Supabase doesn't support hard delete via admin API
        # We'll disable the user instead
        supabase.auth.admin.update_user_by_id(user_id, {
            "app_metadata": {
                "disabled": True,
                "disabled_at": datetime.utcnow().isoformat()
            }
        })
        return True
    except Exception as e:
        st.error(f"Error disabling user: {str(e)}")
        return False

def enable_user(user_id: str) -> bool:
    """Enable previously disabled user"""
    supabase = init_service_client()
    try:
        supabase.auth.admin.update_user_by_id(user_id, {
            "app_metadata": {
                "disabled": False
            }
        })
        return True
    except Exception as e:
        st.error(f"Error enabling user: {str(e)}")
        return False

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

def format_datetime(dt_string):
    """Format datetime string for display"""
    if not dt_string:
        return "Never"
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return dt_string

def main():
    st.set_page_config(page_title="Admin User Management", page_icon="👑", layout="wide")
    
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
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Create Admin", "Promote User", "List Admins", "View All Users", "Edit User"])
    
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
        
        if st.button("🔄 Refresh Admin List"):
            st.rerun()
    
    with tab4:
        st.header("All Users")
        
        # Search and filter options
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search_term = st.text_input("🔍 Search by email or name", placeholder="Enter email or name...")
        with col2:
            role_filter = st.selectbox("Filter by role", ["All", "admin", "user", "moderator"])
        with col3:
            status_filter = st.selectbox("Filter by status", ["All", "Active", "Disabled"])
        
        all_users = get_all_users()
        
        # Apply filters
        filtered_users = all_users
        
        if search_term:
            filtered_users = [u for u in filtered_users 
                            if search_term.lower() in u['email'].lower() 
                            or search_term.lower() in u['full_name'].lower()]
        
        if role_filter != "All":
            filtered_users = [u for u in filtered_users if u['role'] == role_filter]
        
        if status_filter != "All":
            if status_filter == "Active":
                filtered_users = [u for u in filtered_users 
                                if not u.get('app_metadata', {}).get('disabled', False)]
            else:  # Disabled
                filtered_users = [u for u in filtered_users 
                                if u.get('app_metadata', {}).get('disabled', False)]
        
        st.write(f"**Total users: {len(filtered_users)}**")
        
        if filtered_users:
            # Create a dataframe for better display
            df_data = []
            for user in filtered_users:
                is_disabled = user.get('app_metadata', {}).get('disabled', False)
                status = "🔴 Disabled" if is_disabled else "🟢 Active"
                
                df_data.append({
                    'Email': user['email'],
                    'Name': user['full_name'],
                    'Role': f"{'👑' if user['role'] == 'admin' else '👤'} {user['role']}",
                    'Status': status,
                    'Created': format_datetime(user['created_at']),
                    'Last Sign In': format_datetime(user['last_sign_in_at']),
                    'ID': user['id'][:8] + '...'  # Shortened ID for display
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
            
            # Export functionality
            if st.button("📥 Export to CSV"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("No users found matching the criteria")
        
        if st.button("🔄 Refresh User List"):
            st.rerun()
    
    with tab5:
        st.header("Edit User")
        
        # User selection
        all_users = get_all_users()
        if all_users:
            user_options = {f"{user['email']} - {user['full_name']}": user['id'] for user in all_users}
            selected_user_key = st.selectbox("Select user to edit", [""] + list(user_options.keys()))
            
            if selected_user_key:
                selected_user_id = user_options[selected_user_key]
                selected_user = next((u for u in all_users if u['id'] == selected_user_id), None)
                
                if selected_user:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("User Information")
                        
                        # Display current user info
                        is_disabled = selected_user.get('app_metadata', {}).get('disabled', False)
                        status_color = "🔴" if is_disabled else "🟢"
                        st.write(f"**Status:** {status_color} {'Disabled' if is_disabled else 'Active'}")
                        st.write(f"**Email:** {selected_user['email']}")
                        st.write(f"**ID:** `{selected_user['id']}`")
                        st.write(f"**Created:** {format_datetime(selected_user['created_at'])}")
                        st.write(f"**Last Sign In:** {format_datetime(selected_user['last_sign_in_at'])}")
                        
                        # Status management
                        st.subheader("Status Management")
                        if is_disabled:
                            if st.button("✅ Enable User", type="primary"):
                                if enable_user(selected_user_id):
                                    st.success("User enabled successfully!")
                                    st.rerun()
                        else:
                            if st.button("❌ Disable User", type="secondary"):
                                if st.session_state.get('confirm_disable'):
                                    if delete_user(selected_user_id):
                                        st.success("User disabled successfully!")
                                        st.rerun()
                                else:
                                    st.session_state.confirm_disable = True
                                    st.rerun()
                            
                            if st.session_state.get('confirm_disable'):
                                st.warning("⚠️ Are you sure you want to disable this user?")
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    if st.button("Yes, Disable"):
                                        if delete_user(selected_user_id):
                                            st.success("User disabled successfully!")
                                            st.session_state.confirm_disable = False
                                            st.rerun()
                                with col_b:
                                    if st.button("Cancel"):
                                        st.session_state.confirm_disable = False
                                        st.rerun()
                    
                    with col2:
                        st.subheader("Edit Profile")
                        
                        with st.form("edit_user"):
                            new_full_name = st.text_input("Full Name", value=selected_user['full_name'])
                            new_role = st.selectbox("Role", 
                                                  options=["user", "admin", "moderator"], 
                                                  index=["user", "admin", "moderator"].index(selected_user['role']) 
                                                  if selected_user['role'] in ["user", "admin", "moderator"] else 0)
                            
                            if st.form_submit_button("💾 Update Profile"):
                                if update_user_profile(selected_user_id, new_full_name, new_role):
                                    st.success("User profile updated successfully!")
                                    st.rerun()
                                else:
                                    st.error("Failed to update user profile")
        else:
            st.info("No users found")

if __name__ == "__main__":
    main()
