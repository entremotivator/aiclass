import os
import streamlit as st
from datetime import date
from supabase import create_client, Client

st.set_page_config(page_title="Manage User Plans", page_icon="📝")

if not st.session_state.get("authenticated", False):
    st.warning("Please log in to access this page.")
    st.stop()

st.title("Manage User Plans")
st.write("Manually add or update user subscription plans.")

# ✅ Load Supabase credentials safely
def get_supabase_credentials():
    # Try nested secrets first
    if "supabase" in st.secrets:
        url = st.secrets["supabase"].get("url")
        key = st.secrets["supabase"].get("anon_key")
    else:  # fallback to flat structure
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_ANON_KEY")

    if not url or not key:
        st.stop()
        raise ValueError("❌ Supabase credentials are missing. Check your secrets.toml.")
    return url, key

SUPABASE_URL, SUPABASE_ANON_KEY = get_supabase_credentials()

@st.cache_resource
def init_supabase_client():
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

supabase: Client = init_supabase_client()

# ------------------ Add Plan Form ------------------ #
with st.form("add_user_plan_form"):
    st.subheader("Add New User Plan")
    user_id = st.text_input("User ID (UUID from Supabase auth.users)")
    plan_name = st.selectbox("Plan Name", ["Free", "Basic", "Premium", "Enterprise"])
    start_date = st.date_input("Start Date", value=date.today())
    end_date = st.date_input("End Date", value=date.today().replace(year=date.today().year + 1))

    submitted = st.form_submit_button("Add Plan")

    if submitted:
        if user_id and plan_name and start_date and end_date:
            try:
                data = supabase.table("user_plans").insert({
                    "user_id": user_id,
                    "plan_name": plan_name,
                    "start_date": str(start_date),
                    "end_date": str(end_date)
                }).execute()
                st.success(f"Plan '{plan_name}' added for user {user_id}!")
            except Exception as e:
                st.error(f"Error adding plan: {e}")
        else:
            st.error("Please fill in all fields.")

# ------------------ Show Current User Plans ------------------ #
st.subheader("Existing User Plans")
if st.session_state.get("authenticated", False):
    try:
        current_user_id = st.session_state.get("user_id")
        if current_user_id:
            response = supabase.table("user_plans").select("*").eq("user_id", current_user_id).execute()
            plans = response.data
            if plans:
                st.write("Your current plans:")
                for plan in plans:
                    st.json(plan)
            else:
                st.info("No plans found for your account.")
        else:
            st.warning("Could not retrieve user ID for displaying plans.")
    except Exception as e:
        st.error(f"Error fetching plans: {e}")
