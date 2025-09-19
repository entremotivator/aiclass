import streamlit as st
import hashlib
import json
import time
from datetime import datetime, timedelta
import re

st.set_page_config(page_title="New Page 5", page_icon="✨")

if not st.session_state.get("authenticated", False):
    st.warning("Please log in to access this page.")
    st.stop()
# Custom CSS for modern login design
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 500px;
    }
    
    /* Login container */
    .login-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        text-align: center;
        color: white;
        margin: 2rem 0;
    }
    
    /* Logo and branding */
    .logo {
        font-size: 3rem;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .brand-title {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    .brand-subtitle {
        font-size: 1rem;
        opacity: 0.9;
        margin-bottom: 2rem;
    }
    
    /* Form styling */
    .stTextInput > div > div > input {
        background-color: rgba(255,255,255,0.9);
        border: none;
        border-radius: 10px;
        padding: 0.75rem;
        font-size: 1rem;
        color: #333;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .stTextInput > div > div > input:focus {
        background-color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #ff6b6b, #ee5a52);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: bold;
        width: 100%;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(238, 90, 82, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(238, 90, 82, 0.4);
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: rgba(40, 167, 69, 0.9);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .stError {
        background-color: rgba(220, 53, 69, 0.9);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: rgba(255,255,255,0.7);
        border-radius: 8px;
        font-weight: bold;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: rgba(255,255,255,0.2);
        color: white;
    }
    
    /* Features section */
    .features-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .feature-item {
        display: flex;
        align-items: center;
        margin: 1rem 0;
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    
    .feature-icon {
        font-size: 1.5rem;
        margin-right: 1rem;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #666;
        margin-top: 3rem;
        padding: 2rem;
        background-color: #f8f9fa;
        border-radius: 15px;
    }
    
    /* Security indicator */
    .security-indicator {
        background-color: rgba(40, 167, 69, 0.1);
        border: 1px solid #28a745;
        border-radius: 8px;
        padding: 0.5rem;
        margin: 1rem 0;
        color: #28a745;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Demo users database (in production, use proper database)
DEMO_USERS = {
    "admin@novamind.ai": {
        "password": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",  # "password"
        "name": "Admin User",
        "role": "Administrator",
        "last_login": None
    },
    "demo@novamind.ai": {
        "password": "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f",  # "demo123"
        "name": "Demo User",
        "role": "User",
        "last_login": None
    }
}

# Utility functions
def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

def authenticate_user(email, password):
    """Authenticate user credentials"""
    if email in DEMO_USERS:
        hashed_password = hash_password(password)
        if DEMO_USERS[email]["password"] == hashed_password:
            # Update last login
            DEMO_USERS[email]["last_login"] = datetime.now()
            return True, DEMO_USERS[email]
    return False, None

def register_user(email, password, name):
    """Register new user (demo implementation)"""
    if email in DEMO_USERS:
        return False, "User already exists"
    
    DEMO_USERS[email] = {
        "password": hash_password(password),
        "name": name,
        "role": "User",
        "last_login": None
    }
    return True, "User registered successfully"

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.session_state.login_attempts = 0
    st.session_state.last_attempt_time = None

# Main login interface
def show_login():
    # Header with logo and branding
    st.markdown("""
    <div class="login-container">
        <div class="logo">🧠</div>
        <div class="brand-title">NovaMind AI</div>
        <div class="brand-subtitle">Advanced Multi-LLM Platform</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Security indicator
    st.markdown("""
    <div class="security-indicator">
        🔒 Your connection is secure and encrypted
    </div>
    """, unsafe_allow_html=True)
    
    # Login/Register tabs
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.markdown("### Welcome Back!")
        
        # Check for rate limiting
        if st.session_state.login_attempts >= 5:
            if st.session_state.last_attempt_time:
                time_diff = datetime.now() - st.session_state.last_attempt_time
                if time_diff < timedelta(minutes=5):
                    st.error("Too many failed attempts. Please wait 5 minutes before trying again.")
                    st.info(f"Time remaining: {5 - time_diff.total_seconds()//60:.0f} minutes")
                    return
                else:
                    st.session_state.login_attempts = 0
        
        with st.form("login_form"):
            email = st.text_input("📧 Email Address", placeholder="Enter your email")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                remember_me = st.checkbox("Remember me")
            with col2:
                forgot_password = st.form_submit_button("Forgot Password?")
            
            login_button = st.form_submit_button("🚀 Login to NovaMind", use_container_width=True)
            
            # Handle form submissions
            if forgot_password:
                st.info("🔄 Password reset functionality would be implemented here. For demo, use: demo@novamind.ai / demo123")
            elif login_button:
                if not email or not password:
                    st.error("Please enter both email and password")
                elif not validate_email(email):
                    st.error("Please enter a valid email address")
                else:
                    success, user_info = authenticate_user(email, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_info = user_info
                        st.session_state.login_attempts = 0
                        st.success(f"Welcome back, {user_info['name']}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.session_state.login_attempts += 1
                        st.session_state.last_attempt_time = datetime.now()
                        st.error(f"Invalid credentials. Attempts: {st.session_state.login_attempts}/5")
    
    with tab2:
        st.markdown("### Join NovaMind AI")
        
        with st.form("register_form"):
            reg_name = st.text_input("👤 Full Name", placeholder="Enter your full name")
            reg_email = st.text_input("📧 Email Address", placeholder="Enter your email")
            reg_password = st.text_input("🔒 Password", type="password", placeholder="Create a password")
            reg_confirm = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")
            
            agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
            
            register_button = st.form_submit_button("✨ Create Account", use_container_width=True)
            
            if register_button:
                if not all([reg_name, reg_email, reg_password, reg_confirm]):
                    st.error("Please fill in all fields")
                elif not validate_email(reg_email):
                    st.error("Please enter a valid email address")
                elif reg_password != reg_confirm:
                    st.error("Passwords do not match")
                elif not agree_terms:
                    st.error("Please agree to the Terms of Service")
                else:
                    valid, message = validate_password(reg_password)
                    if not valid:
                        st.error(message)
                    else:
                        success, message = register_user(reg_email, reg_password, reg_name)
                        if success:
                            st.success("Account created successfully! Please login.")
                        else:
                            st.error(message)

def show_dashboard():
    """Display the main dashboard after login"""
    # Header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.title(f"🧠 Welcome, {st.session_state.user_info['name']}!")
    with col2:
        st.metric("Role", st.session_state.user_info['role'])
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_info = None
            st.rerun()
    
    st.markdown("---")
    
    # Dashboard content
    tab1, tab2, tab3 = st.tabs(["🏠 Dashboard", "🤖 AI Chat", "⚙️ Settings"])
    
    with tab1:
        st.markdown("### 🚀 NovaMind AI Platform")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Active Models", "6", "↗️ +2")
        with col2:
            st.metric("API Calls", "1,234", "↗️ +56")
        with col3:
            st.metric("Success Rate", "99.8%", "↗️ +0.2%")
        
        st.markdown("### 🎯 Quick Actions")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🤖 Start AI Chat", use_container_width=True):
                st.info("Redirecting to AI Chat...")
        with col2:
            if st.button("📊 View Analytics", use_container_width=True):
                st.info("Analytics dashboard would open here")
        with col3:
            if st.button("🔧 Configure APIs", use_container_width=True):
                st.info("API configuration panel would open here")
        
        st.markdown("### 📈 Recent Activity")
        activity_data = [
            "✅ Connected to OpenAI GPT-4",
            "✅ DeepSeek API configured",
            "✅ Ollama model downloaded",
            "⏰ Claude API usage: 85% of quota"
        ]
        for activity in activity_data:
            st.text(activity)
    
    with tab2:
        st.markdown("### 🤖 AI Chat Interface")
        st.info("Your enhanced multi-LLM chatbot would be embedded here.")
        
        # Placeholder for chatbot integration
        st.markdown("#### Integration Example:")
        st.code("""
# This would integrate with your enhanced chatbot
# The user is already authenticated and can access all features
if st.session_state.authenticated:
    # Load the main chatbot interface
    load_multi_llm_chatbot(user_info=st.session_state.user_info)
        """)
        
        # Sample chat interface preview
        st.markdown("#### Preview:")
        with st.container():
            st.text_input("💬 Chat with AI", placeholder="Ask me anything...")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.selectbox("AI Provider", ["OpenAI", "DeepSeek", "Gemini", "Claude"])
            with col2:
                st.selectbox("Model", ["GPT-4", "GPT-3.5-turbo"])
            with col3:
                if st.button("Send"):
                    st.success("Message would be sent to the AI!")
    
    with tab3:
        st.markdown("### ⚙️ Account Settings")
        
        with st.form("settings_form"):
            st.text_input("Full Name", value=st.session_state.user_info['name'])
            st.selectbox("Preferred AI Provider", ["OpenAI", "DeepSeek", "Gemini", "Claude"])
            st.slider("Default Temperature", 0.0, 2.0, 0.7)
            st.checkbox("Email Notifications", value=True)
            st.checkbox("Dark Mode", value=False)
            st.text_area("API Keys", placeholder="Manage your API keys here...", type="password")
            
            if st.form_submit_button("💾 Save Settings"):
                st.success("Settings saved successfully!")
        
        st.markdown("### 🔒 Security")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔑 Change Password"):
                st.info("Password change form would appear here")
        with col2:
            if st.button("🔐 Two-Factor Auth"):
                st.info("2FA setup would be available here")

# Features showcase
def show_features():
    st.markdown("""
    <div class="features-container">
        <h3 style="text-align: center; color: #333; margin-bottom: 2rem;">🌟 Why Choose NovaMind AI?</h3>
    </div>
    """, unsafe_allow_html=True)
    
    features = [
        ("🤖", "Multi-LLM Support", "Access 6+ leading AI providers in one platform"),
        ("⚡", "Lightning Fast", "Optimized for speed with advanced caching"),
        ("🔒", "Enterprise Security", "Bank-level encryption and compliance"),
        ("📊", "Advanced Analytics", "Detailed insights and usage monitoring"),
        ("🛠️", "Easy Integration", "Simple APIs and comprehensive documentation"),
        ("24/7", "24/7 Support", "Expert technical support when you need it")
    ]
    
    cols = st.columns(2)
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="feature-item">
                <span class="feature-icon">{icon}</span>
                <div>
                    <strong>{title}</strong><br>
                    <small style="color: #666;">{desc}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Demo credentials info
def show_demo_info():
    st.markdown("""
    <div class="features-container">
        <h4 style="color: #333;">🎮 Demo Credentials</h4>
        <div style="background-color: #e8f5e8; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
            <p><strong>👑 Admin Account:</strong></p>
            <ul>
                <li><strong>Email:</strong> admin@novamind.ai</li>
                <li><strong>Password:</strong> password</li>
            </ul>
        </div>
        <div style="background-color: #e3f2fd; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
            <p><strong>👤 User Account:</strong></p>
            <ul>
                <li><strong>Email:</strong> demo@novamind.ai</li>
                <li><strong>Password:</strong> demo123</li>
            </ul>
        </div>
        <p style="color: #666; font-size: 0.9rem;">
            💡 <em>Try both accounts to see different user roles and permissions!</em>
        </p>
    </div>
    """, unsafe_allow_html=True)

# Main application flow
if not st.session_state.authenticated:
    show_login()
    show_features()
    show_demo_info()
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p><strong>NovaMind AI</strong> - Empowering Business with Multi-LLM Intelligence</p>
        <p>🔗 <a href="#" style="color: #667eea;">novamind.ai</a> | 📧 contact@novamind.ai | 📞 1-800-NOVA-AI</p>
        <p style="font-size: 0.9rem; color: #999;">© 2024 NovaMind AI. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    show_dashboard()
