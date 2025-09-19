import streamlit as st
from supabase import create_client, Client
import re
import pandas as pd

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
    st.title("👑 Admin Dashboard")
    
    try:
        users = supabase.table("user_profiles").select("*").execute()
        auth_users = supabase.auth.admin.list_users()  # requires service role

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

        total_users = len(user_data)
        admin_count = len([u for u in user_data if u["role"] == "admin"])
        unconfirmed = len([u for u in user_data if not u["confirmed"]])

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Users", total_users)
        col2.metric("Admins", admin_count)
        col3.metric("Unconfirmed", unconfirmed)

        st.subheader("📋 User Management")
        search = st.text_input("🔍 Search by email")
        filtered = [u for u in user_data if search.lower() in u["email"].lower()] if search else user_data

        if st.button("⬇️ Export CSV"):
            df = pd.DataFrame(filtered)
            st.download_button("Download Users CSV", df.to_csv(index=False), "users.csv", "text/csv")

        if filtered:
            for i, user in enumerate(filtered):
                with st.expander(f"👤 {user['email']} ({user['role'].title()})"):
                    st.write(f"**User ID:** {user['id']}")
                    st.write(f"**Created At:** {user['created_at']}")
                    st.write(f"**Last Sign In:** {user['last_sign_in']}")
                    st.write(f"**Confirmed:** {user['confirmed']}")

                    # Update role
                    new_role = st.selectbox("Change Role", ["user", "admin"], 
                                            index=0 if user["role"] == "user" else 1,
                                            key=f"role_{i}")
                    if st.button("Update Role", key=f"update_{i}"):
                        supabase.table("user_profiles").update({"role": new_role}).eq("id", user["id"]).execute()
                        st.success(f"Updated {user['email']} to {new_role}")
                        st.rerun()

                    # Reset password
                    if st.button("Reset Password", key=f"reset_{i}"):
                        reset_password(user["email"])
                        st.success(f"Password reset email sent to {user['email']}")

                    # Delete user
                    if st.button("❌ Delete User", key=f"delete_{i}"):
                        try:
                            supabase.table("user_profiles").delete().eq("id", user["id"]).execute()
                            supabase.auth.admin.delete_user(user["id"])
                            st.warning(f"Deleted {user['email']}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to delete: {e}")

        else:
            st.info("No users found.")

    except Exception as e:
        st.error(f"Error loading users: {e}")

    st.divider()
    if st.button("🚪 Logout", type="primary"):
        logout()

# -------------------------
# User Dashboard
# -------------------------
def user_dashboard():
    st.title("🙋 User Dashboard")
    user_email = st.session_state.user.email if st.session_state.user else "Unknown"
    st.write(f"Welcome, **{user_email}** 👋")
    st.info(f"Role: {st.session_state.role.title()}")
    if st.button("🚪 Logout", type="primary"):
        logout()

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
    st.set_page_config(page_title="Supabase Auth App", page_icon="🔐", layout="wide")

    if not st.session_state.authenticated:
        st.title("🔐 Supabase Authentication")

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
