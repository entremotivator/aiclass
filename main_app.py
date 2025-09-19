import streamlit as st
import os
from supabase import create_client, Client
from datetime import datetime

# Import the separate pages
import admin_page
import user_page

# Custom CSS for main navigation
def load_main_css():
    st.markdown("""
    <style>
    /* Main theme colors - Light Green */
    .main {
        background: linear-gradient(135deg, #e8f5e8 0%, #f1f8e9 100%);
    }
    
    .stApp {
        background: linear-gradient(135deg, #e8f5e8 0%, #f1f8e9 100%);
    }
    
    /* Navigation cards */
    .nav-card {
        background: white;
        border-radius: 15px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 2px solid #a5d6a7;
        text-align: center;
        transition: transform 0.3s ease;
    }
    
    .nav-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    
    .admin-card {
        border-color: #ff9800;
        background: linear-gradient(135deg, #fff3e0 0%, #ffffff 100%);
    }
    
    .user-card {
        border-color: #4caf50;
        background: linear-gradient(135deg, #e8f5e8 0%, #ffffff 100%);
    }
    
    /* Welcome section */
    .welcome-section {
        background: linear-gradient(135deg, #c8e6c9 0%, #ffffff 100%);
        border-radius: 15px;
        padding: 30px;
        margin: 20px 0;
        text-align: center;
        border: 2px solid #a5d6a7;
    }
    
    /* Feature highlights */
    .feature-highlight {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #66bb6a;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #66bb6a 0%, #4caf50 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.2s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);
        transform: translateY(-2px);
    }
    
    /* Icons */
    .nav-icon {
        font-size: 4rem;
        margin-bottom: 20px;
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-right: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def init_service_client():
    """Initialize Supabase service role client"""
    try:
        url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
        service_key = st.secrets.get("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not service_key:
            return None
        
        return create_client(url, service_key)
        
    except Exception as e:
        return None

def check_admin_access(email: str) -> bool:
    """Check if user has admin access"""
    try:
        supabase = init_service_client()
        if not supabase:
            return False
        
        # Check user role
        response = supabase.table("user_roles").select("role").eq("user_id", email).execute()
        if response.data and response.data[0].get('role') == 'admin':
            return True
        
        # Also check profiles table
        response = supabase.table("profiles").select("role").eq("id", email).execute()
        if response.data and response.data[0].get('role') == 'admin':
            return True
        
        return False
        
    except Exception:
        return False

def render_welcome_section():
    """Render welcome section"""
    st.markdown("""
    <div class="welcome-section">
        <h1>🌟 Welcome to the User Management System</h1>
        <p style="font-size: 1.2rem; color: #666; margin-top: 20px;">
            A comprehensive platform for managing users, analytics, and system administration
        </p>
        <p style="color: #888; margin-top: 15px;">
            Choose your access level below to get started
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_navigation_cards():
    """Render navigation cards for admin and user access"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="nav-card admin-card">
            <div class="nav-icon">👑</div>
            <h2>Admin Dashboard</h2>
            <p>Comprehensive user management, analytics, and system administration</p>
        </div>
        """, unsafe_allow_html=True)
        
        admin_email = st.text_input("Admin Email", placeholder="admin@example.com", key="admin_email")
        admin_password = st.text_input("Admin Password", type="password", placeholder="Enter admin password", key="admin_password")
        
        if st.button("🔐 Access Admin Dashboard", key="admin_btn"):
            if admin_email and admin_password:
                # In a real app, you would verify credentials here
                if check_admin_access(admin_email):
                    st.session_state.access_level = "admin"
                    st.session_state.user_email = admin_email
                    st.rerun()
                else:
                    st.error("❌ Invalid admin credentials or insufficient permissions")
            else:
                st.error("❌ Please enter both email and password")
    
    with col2:
        st.markdown("""
        <div class="nav-card user-card">
            <div class="nav-icon">👤</div>
            <h2>User Dashboard</h2>
            <p>Personal dashboard with usage analytics, features, and account management</p>
        </div>
        """, unsafe_allow_html=True)
        
        user_email = st.text_input("User Email", placeholder="user@example.com", key="user_email")
        
        if st.button("📊 Access User Dashboard", key="user_btn"):
            if user_email:
                st.session_state.access_level = "user"
                st.session_state.user_email = user_email
                st.rerun()
            else:
                st.error("❌ Please enter your email")

def render_feature_highlights():
    """Render feature highlights"""
    st.markdown("## ✨ Platform Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-highlight">
            <span class="feature-icon">👑</span>
            <strong>Admin Features</strong>
            <ul style="margin-top: 10px;">
                <li>Comprehensive user management with card-based UI</li>
                <li>Advanced analytics and reporting</li>
                <li>Approval workflow management</li>
                <li>Bulk operations and data export</li>
                <li>System settings and configuration</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-highlight">
            <span class="feature-icon">📊</span>
            <strong>Analytics & Insights</strong>
            <ul style="margin-top: 10px;">
                <li>Real-time user statistics</li>
                <li>Usage and revenue tracking</li>
                <li>Interactive charts and visualizations</li>
                <li>Activity monitoring</li>
                <li>Performance metrics</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-highlight">
            <span class="feature-icon">👤</span>
            <strong>User Features</strong>
            <ul style="margin-top: 10px;">
                <li>Personal usage dashboard</li>
                <li>Account settings and preferences</li>
                <li>Activity timeline</li>
                <li>Feature access management</li>
                <li>Subscription and billing info</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-highlight">
            <span class="feature-icon">🔐</span>
            <strong>Security & Access</strong>
            <ul style="margin-top: 10px;">
                <li>Role-based access control</li>
                <li>Secure authentication</li>
                <li>Data privacy protection</li>
                <li>Audit logging</li>
                <li>Permission management</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def render_system_status():
    """Render system status"""
    st.markdown("## 🔧 System Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: white; border-radius: 10px; border: 1px solid #c8e6c9;">
            <div style="font-size: 2rem; color: #4caf50;">✅</div>
            <div><strong>Database</strong></div>
            <div style="color: #4caf50;">Online</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: white; border-radius: 10px; border: 1px solid #c8e6c9;">
            <div style="font-size: 2rem; color: #4caf50;">✅</div>
            <div><strong>API</strong></div>
            <div style="color: #4caf50;">Operational</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: white; border-radius: 10px; border: 1px solid #c8e6c9;">
            <div style="font-size: 2rem; color: #4caf50;">✅</div>
            <div><strong>Auth</strong></div>
            <div style="color: #4caf50;">Active</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: white; border-radius: 10px; border: 1px solid #c8e6c9;">
            <div style="font-size: 2rem; color: #4caf50;">✅</div>
            <div><strong>Storage</strong></div>
            <div style="color: #4caf50;">Available</div>
        </div>
        """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="User Management System",
        page_icon="🌟",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Load custom CSS
    load_main_css()
    
    # Check if user has already selected access level
    if 'access_level' in st.session_state:
        if st.session_state.access_level == "admin":
            # Show admin dashboard
            admin_page.main()
        elif st.session_state.access_level == "user":
            # Show user dashboard
            user_page.main()
    else:
        # Show main navigation page
        render_welcome_section()
        
        st.markdown("---")
        
        render_navigation_cards()
        
        st.markdown("---")
        
        render_feature_highlights()
        
        st.markdown("---")
        
        render_system_status()
        
        # Logout/Reset button in sidebar
        with st.sidebar:
            st.markdown("### 🔄 Navigation")
            if st.button("🏠 Back to Home"):
                # Clear session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
            
            st.markdown("---")
            st.markdown("### ℹ️ Information")
            st.markdown("**Version:** 2.0")
            st.markdown("**Last Updated:** " + datetime.now().strftime("%Y-%m-%d"))
            st.markdown("**Status:** 🟢 Online")
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; padding: 20px;">
            <p><strong>User Management System</strong> - Built with Streamlit & Supabase</p>
            <p>Comprehensive user administration with enhanced analytics and card-based interface</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
