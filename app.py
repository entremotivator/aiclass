import streamlit as st
import hashlib
import json
import time
from datetime import datetime, timedelta
import re
import os
import uuid
from typing import Optional, Dict, Any

# Supabase imports (install: pip install supabase)
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    st.warning("Supabase not installed. Using demo mode. Install with: pip install supabase")

# Page config
st.set_page_config(
    page_title="NovaMind AI - Enterprise Multi-LLM Platform",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS for modern design
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 10px;
    }
    
    /* Main container */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 600px;
    }
    
    /* Animated gradient background */
    .login-container {
        background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #f5576c);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        padding: 3rem 2rem;
        border-radius: 25px;
        box-shadow: 0 25px 50px rgba(0,0,0,0.15);
        text-align: center;
        color: white;
        margin: 2rem 0;
        position: relative;
        overflow: hidden;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Glassmorphism effect */
    .glass-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
    }
    
    /* Enhanced logo with glow effect */
    .logo {
        font-size: 4rem;
        margin-bottom: 1rem;
        text-shadow: 0 0 20px rgba(255,255,255,0.5);
        animation: logoGlow 2s ease-in-out infinite alternate;
    }
    
    @keyframes logoGlow {
        from { text-shadow: 0 0 20px rgba(255,255,255,0.5); }
        to { text-shadow: 0 0 30px rgba(255,255,255,0.8); }
    }
    
    .brand-title {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        background: linear-gradient(45deg, #fff, #f0f0f0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .brand-subtitle {
        font-size: 1.1rem;
        opacity: 0.95;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    /* Enhanced form styling */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.95);
        border: 2px solid transparent;
        border-radius: 15px;
        padding: 1rem;
        font-size: 1rem;
        color: #333;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        background: white;
        border-color: #667eea;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.25);
        transform: translateY(-2px);
    }
    
    .stSelectbox > div > div > div {
        background: rgba(255,255,255,0.95);
        border: 2px solid transparent;
        border-radius: 15px;
        padding: 0.5rem;
    }
    
    /* Enhanced button styling with hover effects */
    .stButton > button {
        background: linear-gradient(45deg, #ff6b6b, #ee5a52, #ff9a9e);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 1rem 2rem;
        font-size: 1.1rem;
        font-weight: bold;
        width: 100%;
        margin: 1rem 0;
        box-shadow: 0 6px 20px rgba(238, 90, 82, 0.3);
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 10px 30px rgba(238, 90, 82, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(-1px) scale(1.01);
    }
    
    /* Success/Error messages with animations */
    .stSuccess {
        background: linear-gradient(135deg, #28a745, #20c997);
        border: none;
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 6px 20px rgba(40, 167, 69, 0.3);
        animation: slideInUp 0.5s ease-out;
    }
    
    .stError {
        background: linear-gradient(135deg, #dc3545, #e83e8c);
        border: none;
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 6px 20px rgba(220, 53, 69, 0.3);
        animation: shake 0.5s ease-out;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #17a2b8, #6f42c1);
        border: none;
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 6px 20px rgba(23, 162, 184, 0.3);
    }
    
    @keyframes slideInUp {
        from { transform: translateY(30px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    @keyframes shake {
        0%, 20%, 40%, 60%, 80% { transform: translateX(-5px); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(5px); }
    }
    
    /* Enhanced tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 5px;
        background: rgba(255,255,255,0.15);
        border-radius: 15px;
        padding: 8px;
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: rgba(255,255,255,0.8);
        border-radius: 12px;
        font-weight: bold;
        font-size: 1rem;
        padding: 12px 20px;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(255,255,255,0.25);
        color: white;
        box-shadow: 0 4px 15px rgba(255,255,255,0.2);
    }
    
    /* Enhanced features section */
    .features-container {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        padding: 3rem 2rem;
        border-radius: 25px;
        margin: 2rem 0;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
    }
    
    .features-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .feature-item {
        display: flex;
        align-items: center;
        margin: 1.5rem 0;
        padding: 1.5rem;
        background: white;
        border-radius: 20px;
        border-left: 5px solid #667eea;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        position: relative;
        z-index: 1;
    }
    
    .feature-item:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);
        border-left-color: #ff6b6b;
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-right: 1.5rem;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Dashboard enhancements */
    .metric-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
        margin: 1rem 0;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
    }
    
    /* Security indicator enhancement */
    .security-indicator {
        background: linear-gradient(135deg, #28a745, #20c997);
        border: none;
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        color: white;
        font-size: 1rem;
        text-align: center;
        box-shadow: 0 6px 20px rgba(40, 167, 69, 0.3);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 6px 20px rgba(40, 167, 69, 0.3); }
        50% { box-shadow: 0 8px 25px rgba(40, 167, 69, 0.4); }
        100% { box-shadow: 0 6px 20px rgba(40, 167, 69, 0.3); }
    }
    
    /* Footer enhancement */
    .footer {
        text-align: center;
        color: #666;
        margin-top: 3rem;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border-radius: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    /* Loading spinner */
    .loading-spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Progress bar */
    .progress-bar {
        width: 100%;
        height: 10px;
        background-color: #f0f0f0;
        border-radius: 5px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea, #764ba2);
        transition: width 0.3s ease;
        animation: progressGlow 2s ease-in-out infinite alternate;
    }
    
    @keyframes progressGlow {
        from { box-shadow: 0 0 5px rgba(102, 126, 234, 0.5); }
        to { box-shadow: 0 0 20px rgba(102, 126, 234, 0.8); }
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .login-container {
            margin: 1rem;
            padding: 2rem 1.5rem;
        }
        
        .brand-title {
            font-size: 2rem;
        }
        
        .logo {
            font-size: 3rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Supabase Configuration
class SupabaseManager:
    def __init__(self):
        self.client: Optional[Client] = None
        self.initialize()
    
    def initialize(self):
        """Initialize Supabase client"""
        if not SUPABASE_AVAILABLE:
            return
        
        # Get from environment variables or Streamlit secrets
        try:
            supabase_url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
            supabase_key = st.secrets.get("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_ANON_KEY")
            
            if supabase_url and supabase_key:
                self.client = create_client(supabase_url, supabase_key)
                st.success("✅ Connected to Supabase")
            else:
                st.warning("⚠️ Supabase credentials not found. Add SUPABASE_URL and SUPABASE_ANON_KEY to secrets.toml")
        except Exception as e:
            st.error(f"❌ Supabase connection failed: {str(e)}")
    
    def sign_up(self, email: str, password: str, metadata: Dict[str, Any] = None) -> tuple:
        """Sign up user with Supabase"""
        if not self.client:
            return False, "Supabase not available"
        
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {"data": metadata or {}}
            })
            
            if response.user:
                return True, "Account created successfully! Check your email for verification."
            else:
                return False, "Failed to create account"
        except Exception as e:
            return False, f"Registration error: {str(e)}"
    
    def sign_in(self, email: str, password: str) -> tuple:
        """Sign in user with Supabase"""
        if not self.client:
            return False, None
        
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                return True, {
                    "id": response.user.id,
                    "email": response.user.email,
                    "name": response.user.user_metadata.get("name", "User"),
                    "role": response.user.user_metadata.get("role", "User"),
                    "last_login": datetime.now(),
                    "verified": response.user.email_confirmed_at is not None
                }
            else:
                return False, None
        except Exception as e:
            return False, None
    
    def sign_out(self) -> bool:
        """Sign out user"""
        if not self.client:
            return True
        
        try:
            self.client.auth.sign_out()
            return True
        except Exception:
            return False
    
    def reset_password(self, email: str) -> tuple:
        """Send password reset email"""
        if not self.client:
            return False, "Supabase not available"
        
        try:
            self.client.auth.reset_password_email(email)
            return True, "Password reset email sent!"
        except Exception as e:
            return False, f"Error: {str(e)}"

# Initialize Supabase manager
supabase_manager = SupabaseManager()

# Demo users database (fallback when Supabase is not available)
DEMO_USERS = {
    "admin@novamind.ai": {
        "password": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",  # "password"
        "name": "Admin User",
        "role": "Administrator",
        "last_login": None,
        "verified": True
    },
    "demo@novamind.ai": {
        "password": "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f",  # "demo123"
        "name": "Demo User",
        "role": "User",
        "last_login": None,
        "verified": True
    },
    "premium@novamind.ai": {
        "password": "481f6cc0511143ccdd7e2d1b1b94faf0a700a8b49cd13922a70b5ae28acaa8c5",  # "premium"
        "name": "Premium User",
        "role": "Premium",
        "last_login": None,
        "verified": True
    }
}

# Utility functions
def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> tuple:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    return True, "Password is valid"

def authenticate_user(email: str, password: str) -> tuple:
    """Authenticate user credentials"""
    # Try Supabase first
    if supabase_manager.client:
        return supabase_manager.sign_in(email, password)
    
    # Fallback to demo users
    if email in DEMO_USERS:
        hashed_password = hash_password(password)
        if DEMO_USERS[email]["password"] == hashed_password:
            DEMO_USERS[email]["last_login"] = datetime.now()
            return True, DEMO_USERS[email]
    return False, None

def register_user(email: str, password: str, name: str) -> tuple:
    """Register new user"""
    # Try Supabase first
    if supabase_manager.client:
        return supabase_manager.sign_up(email, password, {"name": name, "role": "User"})
    
    # Fallback to demo mode
    if email in DEMO_USERS:
        return False, "User already exists"
    
    DEMO_USERS[email] = {
        "password": hash_password(password),
        "name": name,
        "role": "User",
        "last_login": None,
        "verified": False
    }
    return True, "Account created successfully! (Demo mode - no email verification needed)"

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.session_state.login_attempts = 0
    st.session_state.last_attempt_time = None
    st.session_state.dark_mode = False
    st.session_state.selected_ai_provider = "OpenAI"
    st.session_state.chat_history = []

# Main login interface
def show_login():
    # Header with animated logo and branding
    st.markdown("""
    <div class="login-container">
        <div class="logo">🧠</div>
        <div class="brand-title">NovaMind AI</div>
        <div class="brand-subtitle">Enterprise Multi-LLM Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced security indicator
    st.markdown("""
    <div class="security-indicator">
        🔒 SSL Encrypted • SOC 2 Compliant • GDPR Ready
    </div>
    """, unsafe_allow_html=True)
    
    # Login/Register/Reset Password tabs
    tab1, tab2, tab3 = st.tabs(["🔐 Login", "📝 Register", "🔄 Reset Password"])
    
    with tab1:
        st.markdown("### Welcome Back to NovaMind!")
        
        # Check for rate limiting
        if st.session_state.login_attempts >= 5:
            if st.session_state.last_attempt_time:
                time_diff = datetime.now() - st.session_state.last_attempt_time
                if time_diff < timedelta(minutes=5):
                    st.error("🚫 Too many failed attempts. Please wait 5 minutes before trying again.")
                    remaining_time = 5 - (time_diff.total_seconds() // 60)
                    st.markdown(f"""
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {(5 - remaining_time) * 20}%;"></div>
                    </div>
                    <p style="margin: 0;"><strong>📧 Email:</strong> demo@novamind.ai</p>
                    <p style="margin: 5px 0 0 0;"><strong>🔑 Password:</strong> demo123</p>
                </div>
                <p style="margin: 0; font-size: 0.9rem; opacity: 0.9;">
                    🎯 <strong>Core Features:</strong> AI chat, basic analytics, project creation, and collaboration tools
                </p>
            </div>
            
            <div style="background: linear-gradient(135deg, #ff6b6b, #ee5a52); padding: 1.5rem; 
                        border-radius: 15px; color: white; box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);">
                <h5 style="margin: 0 0 1rem 0; display: flex; align-items: center;">
                    <span style="font-size: 1.5rem; margin-right: 10px;">💎</span> Premium User
                </h5>
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                    <p style="margin: 0;"><strong>📧 Email:</strong> premium@novamind.ai</p>
                    <p style="margin: 5px 0 0 0;"><strong>🔑 Password:</strong> premium</p>
                </div>
                <p style="margin: 0; font-size: 0.9rem; opacity: 0.9;">
                    🚀 <strong>Premium Access:</strong> Advanced AI models, priority support, enhanced analytics, and beta features
                </p>
            </div>
        </div>
        
        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 15px; margin: 1.5rem 0;">
            <h5 style="color: #333; margin: 0 0 1rem 0; text-align: center;">🌟 Demo Features</h5>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 10px;">🤖</div>
                    <strong>Multi-LLM Chat</strong><br>
                    <small style="color: #666;">Test 6+ AI providers</small>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 10px;">📊</div>
                    <strong>Analytics Dashboard</strong><br>
                    <small style="color: #666;">Usage insights & metrics</small>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 10px;">👥</div>
                    <strong>Team Management</strong><br>
                    <small style="color: #666;">Collaboration tools</small>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 10px;">🎯</div>
                    <strong>Project Templates</strong><br>
                    <small style="color: #666;">Ready-to-use solutions</small>
                </div>
            </div>
        </div>
        
        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea, #764ba2); 
                    border-radius: 15px; color: white; margin: 1.5rem 0;">
            <p style="margin: 0; font-size: 1.1rem;">
                💡 <strong>Pro Tip:</strong> Try different user roles to explore various permission levels and features!
            </p>
        </div>
        
        <div style="text-align: center; margin-top: 2rem;">
            <p style="color: #666; font-size: 0.9rem; margin: 0;">
                🔒 All demo data is simulated and secure • 🚀 Full functionality available • ⚡ No signup required
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Enhanced footer
def show_footer():
    """Enhanced footer with more information"""
    st.markdown("""
    <div class="footer">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 30px; margin-bottom: 2rem;">
            <div>
                <h4 style="color: #333; margin-bottom: 1rem;">🧠 NovaMind AI</h4>
                <p style="color: #666; font-size: 0.9rem; line-height: 1.6;">
                    The world's most advanced Multi-LLM platform, empowering businesses to harness 
                    the full potential of artificial intelligence with enterprise-grade security and performance.
                </p>
            </div>
            
            <div>
                <h5 style="color: #333; margin-bottom: 1rem;">🔗 Quick Links</h5>
                <div style="color: #667eea; font-size: 0.9rem; line-height: 2;">
                    <div>📚 Documentation</div>
                    <div>🔧 API Reference</div>
                    <div>💬 Community Forum</div>
                    <div>📺 Video Tutorials</div>
                </div>
            </div>
            
            <div>
                <h5 style="color: #333; margin-bottom: 1rem;">🏢 Enterprise</h5>
                <div style="color: #667eea; font-size: 0.9rem; line-height: 2;">
                    <div>🎯 Custom Solutions</div>
                    <div>🤝 Partner Program</div>
                    <div>📊 Case Studies</div>
                    <div>💼 Enterprise Sales</div>
                </div>
            </div>
            
            <div>
                <h5 style="color: #333; margin-bottom: 1rem;">🛡️ Trust & Security</h5>
                <div style="color: #667eea; font-size: 0.9rem; line-height: 2;">
                    <div>🔒 SOC 2 Certified</div>
                    <div>🌍 GDPR Compliant</div>
                    <div>🔐 ISO 27001</div>
                    <div>📋 Security Whitepaper</div>
                </div>
            </div>
        </div>
        
        <div style="border-top: 1px solid #e0e0e0; padding-top: 2rem; text-align: center;">
            <div style="display: flex; justify-content: center; gap: 30px; margin-bottom: 1.5rem; flex-wrap: wrap;">
                <div style="color: #667eea; font-weight: bold;">🌐 novamind.ai</div>
                <div style="color: #667eea; font-weight: bold;">📧 hello@novamind.ai</div>
                <div style="color: #667eea; font-weight: bold;">📞 1-800-NOVA-AI</div>
                <div style="color: #667eea; font-weight: bold;">💬 Live Chat 24/7</div>
            </div>
            
            <div style="display: flex; justify-content: center; gap: 20px; margin-bottom: 1.5rem;">
                <span style="background: #1da1f2; color: white; padding: 8px 15px; border-radius: 20px; font-size: 0.8rem;">🐦 Twitter</span>
                <span style="background: #0077b5; color: white; padding: 8px 15px; border-radius: 20px; font-size: 0.8rem;">💼 LinkedIn</span>
                <span style="background: #333; color: white; padding: 8px 15px; border-radius: 20px; font-size: 0.8rem;">🐱 GitHub</span>
                <span style="background: #7289da; color: white; padding: 8px 15px; border-radius: 20px; font-size: 0.8rem;">💬 Discord</span>
            </div>
            
            <p style="color: #999; font-size: 0.9rem; margin: 0;">
                © 2024 NovaMind AI Technologies Inc. All rights reserved. 
                <span style="color: #667eea;">Privacy Policy</span> • 
                <span style="color: #667eea;">Terms of Service</span> • 
                <span style="color: #667eea;">Cookie Policy</span>
            </p>
            
            <div style="margin-top: 1rem; padding: 1rem; background: linear-gradient(135deg, #667eea, #764ba2); 
                        border-radius: 15px; color: white;">
                <p style="margin: 0; font-weight: bold;">🚀 Ready to revolutionize your AI workflow?</p>
                <p style="margin: 5px 0 0 0; font-size: 0.9rem;">
                    Join 10,000+ companies already using NovaMind AI to build the future.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Main application flow with enhanced features
def main():
    """Main application entry point"""
    
    # Add floating action button for quick access
    if st.session_state.authenticated:
        st.markdown("""
        <div style="position: fixed; bottom: 20px; right: 20px; z-index: 1000;">
            <div style="background: linear-gradient(45deg, #667eea, #764ba2); 
                        width: 60px; height: 60px; border-radius: 50%; 
                        display: flex; align-items: center; justify-content: center; 
                        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4); 
                        cursor: pointer; animation: pulse 2s infinite;">
                <span style="color: white; font-size: 1.5rem;">💬</span>
            </div>
        </div>
        
        <style>
        @keyframes pulse {
            0% { box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4); }
            50% { box-shadow: 0 4px 30px rgba(102, 126, 234, 0.6); }
            100% { box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4); }
        }
        </style>
        """, unsafe_allow_html=True)

# Execute main application
if not st.session_state.authenticated:
    show_login()
    show_features()
    show_demo_info()
    show_footer()
else:
    show_dashboard()

# Add loading states and animations
if st.session_state.get('show_loading', False):
    st.markdown("""
    <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                background: rgba(255,255,255,0.9); display: flex; align-items: center; 
                justify-content: center; z-index: 9999;">
        <div class="loading-spinner"></div>
    </div>
    """, unsafe_allow_html=True)

# Add keyboard shortcuts info
if st.session_state.authenticated:
    with st.expander("⌨️ Keyboard Shortcuts"):
        st.markdown("""
        **Navigation:**
        - `Ctrl + 1`: Dashboard
        - `Ctrl + 2`: AI Chat
        - `Ctrl + 3`: Analytics
        - `Ctrl + R`: Refresh data
        - `Ctrl + /`: Search
        - `Esc`: Close modals
        
        **Chat:**
        - `Enter`: Send message
        - `Shift + Enter`: New line
        - `↑/↓`: Navigate history
        """)

# Add system notifications
if st.session_state.authenticated and st.session_state.user_info.get('role') == 'Administrator':
    notifications = [
        {"type": "info", "message": "System maintenance scheduled for tonight at 2 AM UTC", "dismissible": True},
        {"type": "warning", "message": "Claude API usage is at 95% of monthly quota", "dismissible": True},
        {"type": "success", "message": "New team member Alice Brown has been added", "dismissible": True}
    ]
    
    for i, notification in enumerate(notifications):
        if notification["dismissible"] and st.session_state.get(f"notification_{i}_dismissed", False):
            continue
            
        color_map = {"info": "#17a2b8", "warning": "#ffc107", "success": "#28a745", "error": "#dc3545"}
        icon_map = {"info": "ℹ️", "warning": "⚠️", "success": "✅", "error": "❌"}
        
        col1, col2 = st.columns([10, 1])
        with col1:
            st.markdown(f"""
            <div style="background: {color_map[notification['type']]}; color: white; 
                        padding: 10px 15px; border-radius: 10px; margin: 5px 0;
                        display: flex; align-items: center;">
                <span style="margin-right: 10px; font-size: 1.2rem;">{icon_map[notification['type']]}</span>
                {notification['message']}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if notification["dismissible"]:
                if st.button("✕", key=f"dismiss_{i}"):
                    st.session_state[f"notification_{i}_dismissed"] = True
                    st.rerun()

main()="text-align: center;">Time remaining: {remaining_time:.0f} minutes</p>
                    """, unsafe_allow_html=True)
                    return
                else:
                    st.session_state.login_attempts = 0
        
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("📧 Email Address", placeholder="Enter your email address", key="login_email")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="login_password")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                remember_me = st.checkbox("🔄 Remember me", key="remember_login")
            with col2:
                show_password = st.checkbox("👁️ Show password", key="show_login_password")
                if show_password and password:
                    st.text(f"Password: {password}")
            
            login_button = st.form_submit_button("🚀 Sign In to NovaMind", use_container_width=True)
            
            # OAuth buttons (placeholder)
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.form_submit_button("🔍 Google", use_container_width=True):
                    st.info("Google OAuth integration would be implemented here")
            with col2:
                if st.form_submit_button("💼 Microsoft", use_container_width=True):
                    st.info("Microsoft OAuth integration would be implemented here")
            with col3:
                if st.form_submit_button("🐱 GitHub", use_container_width=True):
                    st.info("GitHub OAuth integration would be implemented here")
            
            if login_button:
                if not email or not password:
                    st.error("⚠️ Please enter both email and password")
                elif not validate_email(email):
                    st.error("⚠️ Please enter a valid email address")
                else:
                    with st.spinner("🔐 Authenticating..."):
                        success, user_info = authenticate_user(email, password)
                        if success:
                            st.session_state.authenticated = True
                            st.session_state.user_info = user_info
                            st.session_state.login_attempts = 0
                            st.success(f"🎉 Welcome back, {user_info['name']}!")
                            
                            # Show loading animation
                            progress_bar = st.progress(0)
                            for i in range(100):
                                time.sleep(0.01)
                                progress_bar.progress(i + 1)
                            
                            st.rerun()
                        else:
                            st.session_state.login_attempts += 1
                            st.session_state.last_attempt_time = datetime.now()
                            st.error(f"❌ Invalid credentials. Attempts: {st.session_state.login_attempts}/5")
    
    with tab2:
        st.markdown("### Join the NovaMind Revolution!")
        
        with st.form("register_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                reg_first_name = st.text_input("👤 First Name", placeholder="John")
            with col2:
                reg_last_name = st.text_input("👥 Last Name", placeholder="Doe")
            
            reg_email = st.text_input("📧 Email Address", placeholder="john.doe@company.com")
            reg_company = st.text_input("🏢 Company", placeholder="Your Company Name")
            reg_password = st.text_input("🔒 Password", type="password", placeholder="Create a strong password")
            reg_confirm = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")
            
            col1, col2 = st.columns(2)
            with col1:
                account_type = st.selectbox("📋 Account Type", ["Standard", "Premium", "Enterprise"])
            with col2:
                industry = st.selectbox("🏭 Industry", ["Technology", "Healthcare", "Finance", "Education", "Other"])
            
            agree_terms = st.checkbox("✅ I agree to the Terms of Service and Privacy Policy")
            subscribe_newsletter = st.checkbox("📬 Subscribe to NovaMind newsletter for updates")
            
            register_button = st.form_submit_button("✨ Create My Account", use_container_width=True)
            
            if register_button:
                full_name = f"{reg_first_name} {reg_last_name}".strip()
                
                if not all([reg_first_name, reg_last_name, reg_email, reg_password, reg_confirm]):
                    st.error("⚠️ Please fill in all required fields")
                elif not validate_email(reg_email):
                    st.error("⚠️ Please enter a valid email address")
                elif reg_password != reg_confirm:
                    st.error("⚠️ Passwords do not match")
                elif not agree_terms:
                    st.error("⚠️ Please agree to the Terms of Service")
                else:
                    valid, message = validate_password(reg_password)
                    if not valid:
                        st.error(f"⚠️ {message}")
                    else:
                        with st.spinner("🚀 Creating your account..."):
                            success, message = register_user(reg_email, reg_password, full_name)
                            if success:
                                st.success(f"🎉 {message}")
                                st.balloons()
                            else:
                                st.error(f"❌ {message}")
    
    with tab3:
        st.markdown("### Reset Your Password")
        
        with st.form("reset_form"):
            reset_email = st.text_input("📧 Email Address", placeholder="Enter your registered email")
            reset_button = st.form_submit_button("🔄 Send Reset Link", use_container_width=True)
            
            if reset_button:
                if not reset_email:
                    st.error("⚠️ Please enter your email address")
                elif not validate_email(reset_email):
                    st.error("⚠️ Please enter a valid email address")
                else:
                    if supabase_manager.client:
                        success, message = supabase_manager.reset_password(reset_email)
                        if success:
                            st.success(f"✅ {message}")
                        else:
                            st.error(f"❌ {message}")
                    else:
                        st.info("🔄 Password reset functionality would send an email here. For demo, use existing credentials.")

def show_dashboard():
    """Enhanced dashboard with comprehensive features"""
    # Enhanced header with user avatar and notifications
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col1:
        st.markdown(f"""
        <div style="display: flex; align-items: center;">
            <div style="width: 50px; height: 50px; background: linear-gradient(45deg, #667eea, #764ba2); 
                        border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                        margin-right: 15px; color: white; font-size: 20px; font-weight: bold;">
                {st.session_state.user_info['name'][0].upper()}
            </div>
            <div>
                <h2 style="margin: 0;">Welcome back, {st.session_state.user_info['name']}! 👋</h2>
                <p style="margin: 0; color: #666;">Role: {st.session_state.user_info['role']} | Last login: {st.session_state.user_info.get('last_login', 'N/A')}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🔔 Notifications", use_container_width=True):
            st.info("📬 You have 3 new notifications")
    
    with col3:
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.show_settings = True
    
    with col4:
        if st.button("🚪 Logout", use_container_width=True):
            if supabase_manager.sign_out():
                st.session_state.authenticated = False
                st.session_state.user_info = None
                st.success("👋 Successfully logged out!")
                time.sleep(1)
                st.rerun()

    st.markdown("---")
    
    # Main dashboard tabs with enhanced features
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏠 Dashboard", 
        "🤖 AI Chat", 
        "📊 Analytics", 
        "🔧 API Manager", 
        "👥 Team", 
        "🎯 Projects"
    ])
    
    with tab1:
        show_main_dashboard()
    
    with tab2:
        show_ai_chat()
    
    with tab3:
        show_analytics()
    
    with tab4:
        show_api_manager()
    
    with tab5:
        show_team_management()
    
    with tab6:
        show_project_management()

def show_main_dashboard():
    """Main dashboard overview"""
    st.markdown("### 🚀 NovaMind AI Platform Overview")
    
    # Real-time metrics with enhanced styling
    col1, col2, col3, col4 = st.columns(4)
    
    metrics_data = [
        ("🤖 Active Models", "8", "+2 this week", "#667eea"),
        ("🔥 API Calls Today", "2,847", "+15% vs yesterday", "#ff6b6b"),
        ("⚡ Avg Response Time", "1.2s", "-0.3s improvement", "#28a745"),
        ("💎 Success Rate", "99.7%", "+0.1% this month", "#17a2b8")
    ]
    
    for i, (title, value, change, color) in enumerate(metrics_data):
        with [col1, col2, col3, col4][i]:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, {color}, {color}dd);">
                <h3 style="margin: 0; font-size: 0.9rem; opacity: 0.9;">{title}</h3>
                <h1 style="margin: 10px 0; font-size: 2rem;">{value}</h1>
                <p style="margin: 0; font-size: 0.8rem; opacity: 0.8;">{change}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Enhanced quick actions with more options
    st.markdown("### 🎯 Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    quick_actions = [
        ("🤖 New AI Chat", "Start chatting with AI models", "primary"),
        ("📊 View Reports", "Access detailed analytics", "secondary"),
        ("🔧 API Keys", "Manage your API credentials", "success"),
        ("👥 Invite Team", "Add team members", "info")
    ]
    
    for i, (title, desc, variant) in enumerate(quick_actions):
        with [col1, col2, col3, col4][i]:
            if st.button(f"{title}\n{desc}", key=f"quick_{i}", use_container_width=True):
                st.success(f"✅ {title} activated!")
    
    st.markdown("---")
    
    # Activity feed and system status
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📈 Recent Activity")
        activities = [
            ("🤖 Connected to OpenAI GPT-4", "2 minutes ago", "success"),
            ("🔧 DeepSeek API configured", "15 minutes ago", "info"),
            ("📊 Generated analytics report", "1 hour ago", "warning"),
            ("👥 Team member invited", "2 hours ago", "info"),
            ("🔒 Security scan completed", "3 hours ago", "success"),
            ("⚡ Performance optimized", "5 hours ago", "success")
        ]
        
        for activity, time_ago, status_color in activities:
            status_colors = {
                "success": "#28a745",
                "info": "#17a2b8", 
                "warning": "#ffc107",
                "danger": "#dc3545"
            }
            
            st.markdown(f"""
            <div style="display: flex; align-items: center; padding: 10px; margin: 5px 0; 
                        background: white; border-radius: 10px; border-left: 4px solid {status_colors.get(status_color, '#666')};
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="flex-grow: 1;">
                    <strong>{activity}</strong><br>
                    <small style="color: #666;">{time_ago}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🛡️ System Status")
        
        services = [
            ("🤖 AI Models", "Operational", "success"),
            ("🔌 API Gateway", "Operational", "success"), 
            ("📊 Analytics", "Operational", "success"),
            ("🔒 Security", "Operational", "success"),
            ("💾 Database", "Minor Issues", "warning"),
            ("📧 Email Service", "Operational", "success")
        ]
        
        for service, status, color in services:
            color_map = {"success": "🟢", "warning": "🟡", "danger": "🔴"}
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; 
                        padding: 8px; margin: 3px 0; background: #f8f9fa; border-radius: 8px;">
                <span>{service}</span>
                <span>{color_map.get(color, '⚪')} {status}</span>
            </div>
            """, unsafe_allow_html=True)

def show_ai_chat():
    """Enhanced AI chat interface with multiple providers"""
    st.markdown("### 🤖 Multi-LLM Chat Interface")
    
    # AI Provider selection with enhanced UI
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        ai_providers = {
            "OpenAI": {"models": ["GPT-4", "GPT-3.5-turbo", "GPT-4-turbo"], "icon": "🔮"},
            "DeepSeek": {"models": ["DeepSeek-V2", "DeepSeek-Coder"], "icon": "🧠"},
            "Gemini": {"models": ["Gemini-Pro", "Gemini-1.5-Pro"], "icon": "💎"},
            "Claude": {"models": ["Claude-3-Opus", "Claude-3-Sonnet"], "icon": "🎭"},
            "Mistral": {"models": ["Mistral-Large", "Mistral-7B"], "icon": "🌪️"},
            "Ollama": {"models": ["Llama-2", "CodeLlama"], "icon": "🦙"}
        }
        
        selected_provider = st.selectbox(
            "🎯 Select AI Provider", 
            options=list(ai_providers.keys()),
            index=list(ai_providers.keys()).index(st.session_state.selected_ai_provider),
            format_func=lambda x: f"{ai_providers[x]['icon']} {x}"
        )
        st.session_state.selected_ai_provider = selected_provider
    
    with col2:
        available_models = ai_providers[selected_provider]["models"]
        selected_model = st.selectbox("🔧 Model", available_models)
    
    with col3:
        temperature = st.slider("🌡️ Temperature", 0.0, 2.0, 0.7, 0.1)
    
    # Chat settings
    with st.expander("⚙️ Advanced Settings"):
        col1, col2, col3 = st.columns(3)
        with col1:
            max_tokens = st.number_input("📝 Max Tokens", 100, 4000, 2000)
        with col2:
            top_p = st.slider("🎯 Top P", 0.0, 1.0, 0.9, 0.1)
        with col3:
            stream_response = st.checkbox("⚡ Stream Response", True)
    
    # Chat interface
    st.markdown("---")
    
    # Chat history display
    if st.session_state.chat_history:
        st.markdown("### 💬 Chat History")
        for i, (role, message, timestamp) in enumerate(st.session_state.chat_history[-5:]):  # Show last 5 messages
            avatar = "🧠" if role == "assistant" else "👤"
            st.markdown(f"""
            <div style="display: flex; margin: 10px 0; align-items: flex-start;">
                <div style="margin-right: 10px; font-size: 20px;">{avatar}</div>
                <div style="flex-grow: 1; background: {'#f0f8ff' if role == 'assistant' else '#f5f5f5'}; 
                           padding: 15px; border-radius: 15px; max-width: 80%;">
                    <strong>{role.title()}:</strong><br>{message}<br>
                    <small style="color: #666; font-size: 0.8rem;">{timestamp}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Chat input
    user_input = st.text_area("💬 Your Message", placeholder="Ask me anything...", height=100)
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        if st.button("🚀 Send Message", use_container_width=True):
            if user_input.strip():
                # Add user message to history
                timestamp = datetime.now().strftime("%H:%M:%S")
                st.session_state.chat_history.append(("user", user_input, timestamp))
                
                # Simulate AI response
                with st.spinner(f"🤖 {selected_provider} is thinking..."):
                    time.sleep(2)  # Simulate processing time
                    
                    # Generate mock response based on provider
                    responses = {
                        "OpenAI": "This is a simulated response from OpenAI's GPT models. In a real implementation, this would connect to the OpenAI API.",
                        "DeepSeek": "DeepSeek AI response simulation. This model excels at reasoning and coding tasks.",
                        "Gemini": "Google's Gemini response simulation. Known for multimodal capabilities and strong reasoning.",
                        "Claude": "Anthropic's Claude response simulation. Focuses on helpful, harmless, and honest interactions.",
                        "Mistral": "Mistral AI response simulation. Open-source alternative with strong performance.",
                        "Ollama": "Ollama local model response simulation. Perfect for on-premise deployments."
                    }
                    
                    ai_response = f"{responses.get(selected_provider, 'AI Response')} Your question was: '{user_input}'"
                    st.session_state.chat_history.append(("assistant", ai_response, timestamp))
                
                st.rerun()
    
    with col2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    with col3:
        if st.button("💾 Save Chat"):
            st.success("💾 Chat saved to history!")
    
    with col4:
        if st.button("📤 Export Chat"):
            st.success("📤 Chat exported as JSON!")

def show_analytics():
    """Analytics dashboard with comprehensive metrics"""
    st.markdown("### 📊 Analytics & Insights")
    
    # Date range selector
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        date_range = st.selectbox("📅 Time Range", 
                                ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last 3 Months"])
    with col2:
        auto_refresh = st.checkbox("🔄 Auto Refresh", True)
    with col3:
        if st.button("📥 Export Data"):
            st.success("📊 Analytics exported successfully!")
    
    # Key metrics overview
    st.markdown("#### 📈 Usage Overview")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    analytics_metrics = [
        ("Total Requests", "15,847", "+12%", "🚀"),
        ("Avg Response Time", "1.23s", "-8%", "⚡"),
        ("Error Rate", "0.3%", "-15%", "✅"),
        ("Cost This Month", "$284", "+5%", "💰"),
        ("Active Users", "1,245", "+23%", "👥")
    ]
    
    for i, (title, value, change, icon) in enumerate(analytics_metrics):
        with [col1, col2, col3, col4, col5][i]:
            st.markdown(f"""
            <div style="background: white; padding: 20px; border-radius: 15px; 
                        box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center; margin: 5px 0;">
                <div style="font-size: 2rem;">{icon}</div>
                <h3 style="margin: 10px 0 5px 0; font-size: 1.5rem;">{value}</h3>
                <p style="margin: 0; color: #666; font-size: 0.9rem;">{title}</p>
                <p style="margin: 5px 0 0 0; color: {'#28a745' if '+' in change else '#dc3545'}; 
                          font-size: 0.8rem; font-weight: bold;">{change}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts and visualizations
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 📈 Usage Trends")
        
        # Sample data for chart
        import random
        chart_data = {
            "Date": [f"Day {i+1}" for i in range(7)],
            "Requests": [random.randint(1000, 3000) for _ in range(7)],
            "Errors": [random.randint(5, 50) for _ in range(7)]
        }
        
        st.line_chart(chart_data, x="Date", y=["Requests", "Errors"])
    
    with col2:
        st.markdown("#### 🤖 Model Usage Distribution")
        
        model_usage = {
            "GPT-4": 35,
            "GPT-3.5": 25,
            "Claude-3": 20,
            "Gemini": 15,
            "DeepSeek": 5
        }
        
        for model, percentage in model_usage.items():
            st.markdown(f"""
            <div style="margin: 10px 0;">
                <div style="display: flex; justify-content: space-between;">
                    <span><strong>{model}</strong></span>
                    <span>{percentage}%</span>
                </div>
                <div style="background: #f0f0f0; height: 10px; border-radius: 5px; margin-top: 5px;">
                    <div style="background: linear-gradient(90deg, #667eea, #764ba2); 
                               height: 100%; width: {percentage}%; border-radius: 5px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Detailed analytics tables
    st.markdown("---")
    st.markdown("#### 📋 Detailed Reports")
    
    tab1, tab2, tab3 = st.tabs(["🔍 Usage Details", "💰 Cost Analysis", "🚨 Error Logs"])
    
    with tab1:
        # Sample usage data
        usage_data = [
            {"Timestamp": "2024-01-15 10:30", "Model": "GPT-4", "Tokens": 1500, "Cost": "$0.03", "Status": "✅"},
            {"Timestamp": "2024-01-15 10:25", "Model": "Claude-3", "Tokens": 1200, "Cost": "$0.024", "Status": "✅"},
            {"Timestamp": "2024-01-15 10:20", "Model": "GPT-3.5", "Tokens": 800, "Cost": "$0.016", "Status": "⚠️"},
            {"Timestamp": "2024-01-15 10:15", "Model": "Gemini", "Tokens": 950, "Cost": "$0.019", "Status": "✅"},
        ]
        
        for item in usage_data:
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; 
                        padding: 10px; margin: 5px 0; background: white; border-radius: 10px;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <div><strong>{item['Timestamp']}</strong></div>
                <div>{item['Model']}</div>
                <div>{item['Tokens']} tokens</div>
                <div>{item['Cost']}</div>
                <div>{item['Status']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("**💰 Monthly Cost Breakdown**")
        
        cost_data = {
            "OpenAI": "$150",
            "Claude": "$89",
            "Gemini": "$45",
            "DeepSeek": "$25"
        }
        
        total_cost = sum([int(cost.replace(', '')) for cost in cost_data.values()])
        
        for provider, cost in cost_data.items():
            percentage = (int(cost.replace(', '')) / total_cost) * 100
            st.markdown(f"**{provider}**: {cost} ({percentage:.1f}%)")
            st.progress(percentage / 100)
    
    with tab3:
        st.markdown("**🚨 Recent Error Logs**")
        
        errors = [
            {"Time": "10:45", "Error": "Rate limit exceeded", "Model": "GPT-4", "Severity": "⚠️ Warning"},
            {"Time": "09:30", "Error": "API key invalid", "Model": "Claude", "Severity": "🔴 Error"},
            {"Time": "08:15", "Error": "Timeout", "Model": "Gemini", "Severity": "🟡 Info"}
        ]
        
        for error in errors:
            st.error(f"**{error['Time']}** - {error['Model']}: {error['Error']} ({error['Severity']})")

def show_api_manager():
    """API key and integration management"""
    st.markdown("### 🔧 API Key Management")
    
    # API Status overview
    st.markdown("#### 🛡️ API Status Overview")
    
    api_status = {
        "OpenAI": {"status": "🟢 Active", "usage": "85%", "quota": "1M tokens/month"},
        "DeepSeek": {"status": "🟢 Active", "usage": "45%", "quota": "500K tokens/month"},
        "Claude": {"status": "🟡 Limited", "usage": "95%", "quota": "100K tokens/month"},
        "Gemini": {"status": "🟢 Active", "usage": "30%", "quota": "2M tokens/month"},
        "Mistral": {"status": "🔴 Inactive", "usage": "0%", "quota": "N/A"},
        "Ollama": {"status": "🟢 Local", "usage": "N/A", "quota": "Unlimited"}
    }
    
    for api, info in api_status.items():
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 2, 1])
        
        with col1:
            st.markdown(f"**🤖 {api}**")
        with col2:
            st.markdown(info["status"])
        with col3:
            if info["usage"] != "N/A":
                st.progress(int(info["usage"].replace('%', '')) / 100)
                st.markdown(f"<small>{info['usage']}</small>", unsafe_allow_html=True)
        with col4:
            st.markdown(f"<small>{info['quota']}</small>", unsafe_allow_html=True)
        with col5:
            if st.button("⚙️", key=f"config_{api}"):
                st.info(f"Configure {api} API settings")
    
    st.markdown("---")
    
    # API Key Management
    st.markdown("#### 🔑 Manage API Keys")
    
    tab1, tab2, tab3 = st.tabs(["➕ Add New", "🔄 Update Existing", "📊 Usage Monitoring"])
    
    with tab1:
        with st.form("add_api_key"):
            col1, col2 = st.columns(2)
            with col1:
                provider = st.selectbox("🎯 Provider", ["OpenAI", "DeepSeek", "Claude", "Gemini", "Mistral"])
            with col2:
                key_name = st.text_input("🏷️ Key Name", placeholder="Production Key")
            
            api_key = st.text_input("🔑 API Key", type="password", placeholder="sk-...")
            
            col1, col2 = st.columns(2)
            with col1:
                environment = st.selectbox("🌍 Environment", ["Production", "Development", "Testing"])
            with col2:
                rate_limit = st.number_input("⚡ Rate Limit (req/min)", 1, 1000, 60)
            
            if st.form_submit_button("➕ Add API Key", use_container_width=True):
                st.success(f"✅ {provider} API key added successfully!")
    
    with tab2:
        st.markdown("**🔄 Existing API Keys**")
        
        existing_keys = [
            {"Provider": "OpenAI", "Name": "Production", "Status": "🟢 Active", "Last Used": "2 min ago"},
            {"Provider": "Claude", "Name": "Development", "Status": "🟡 Warning", "Last Used": "1 hour ago"},
            {"Provider": "Gemini", "Name": "Testing", "Status": "🟢 Active", "Last Used": "30 min ago"}
        ]
        
        for key in existing_keys:
            col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1, 1])
            with col1:
                st.markdown(f"**{key['Provider']}**")
            with col2:
                st.markdown(key['Name'])
            with col3:
                st.markdown(key['Status'])
            with col4:
                st.markdown(f"<small>{key['Last Used']}</small>", unsafe_allow_html=True)
            with col5:
                if st.button("✏️", key=f"edit_{key['Provider']}"):
                    st.info(f"Edit {key['Provider']} key")
            with col6:
                if st.button("🗑️", key=f"delete_{key['Provider']}"):
                    st.error(f"Delete {key['Provider']} key?")
    
    with tab3:
        st.markdown("**📊 API Usage Monitoring**")
        
        # Real-time usage chart
        st.markdown("##### 📈 Real-time API Calls")
        
        # Sample real-time data
        import datetime
        import random
        
        current_time = datetime.datetime.now()
        time_points = [(current_time - datetime.timedelta(minutes=x)).strftime("%H:%M") for x in range(10, 0, -1)]
        api_calls = [random.randint(50, 200) for _ in range(10)]
        
        chart_data = {"Time": time_points, "API Calls": api_calls}
        st.line_chart(chart_data, x="Time", y="API Calls")
        
        # Usage alerts
        st.markdown("##### 🚨 Usage Alerts")
        alerts = [
            {"Type": "⚠️ Warning", "Message": "Claude API approaching rate limit (95% used)", "Time": "5 min ago"},
            {"Type": "ℹ️ Info", "Message": "OpenAI API key rotated successfully", "Time": "1 hour ago"},
            {"Type": "✅ Success", "Message": "Gemini API quota increased", "Time": "3 hours ago"}
        ]
        
        for alert in alerts:
            st.markdown(f"""
            <div style="padding: 10px; margin: 5px 0; border-radius: 8px; 
                        background: {'#fff3cd' if '⚠️' in alert['Type'] else '#d1ecf1' if 'ℹ️' in alert['Type'] else '#d4edda'};">
                <strong>{alert['Type']}</strong> {alert['Message']} 
                <small style="color: #666;">({alert['Time']})</small>
            </div>
            """, unsafe_allow_html=True)

def show_team_management():
    """Team and collaboration features"""
    st.markdown("### 👥 Team Management")
    
    # Team overview
    col1, col2, col3, col4 = st.columns(4)
    
    team_stats = [
        ("👥 Total Members", "12", "#667eea"),
        ("🔑 Admins", "3", "#28a745"),
        ("👤 Users", "9", "#17a2b8"),
        ("⏸️ Inactive", "2", "#ffc107")
    ]
    
    for i, (title, value, color) in enumerate(team_stats):
        with [col1, col2, col3, col4][i]:
            st.markdown(f"""
            <div style="background: {color}; color: white; padding: 20px; 
                        border-radius: 15px; text-align: center; margin: 5px 0;">
                <h2 style="margin: 0; font-size: 2rem;">{value}</h2>
                <p style="margin: 5px 0 0 0; font-size: 0.9rem;">{title}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Team management tabs
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Members", "➕ Invite", "🔐 Permissions", "📊 Activity"])
    
    with tab1:
        st.markdown("#### 👥 Team Members")
        
        # Search and filter
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search_term = st.text_input("🔍 Search members", placeholder="Search by name or email")
        with col2:
            role_filter = st.selectbox("🎯 Filter by role", ["All", "Admin", "User", "Viewer"])
        with col3:
            status_filter = st.selectbox("📊 Filter by status", ["All", "Active", "Inactive", "Pending"])
        
        # Team members list
        members = [
            {"Name": "John Doe", "Email": "john@company.com", "Role": "Admin", "Status": "🟢 Active", "Last Seen": "Online", "Joined": "Jan 2024"},
            {"Name": "Jane Smith", "Email": "jane@company.com", "Role": "User", "Status": "🟢 Active", "Last Seen": "2 hours ago", "Joined": "Feb 2024"},
            {"Name": "Bob Wilson", "Email": "bob@company.com", "Role": "User", "Status": "🟡 Away", "Last Seen": "1 day ago", "Joined": "Mar 2024"},
            {"Name": "Alice Brown", "Email": "alice@company.com", "Role": "Viewer", "Status": "🔴 Inactive", "Last Seen": "1 week ago", "Joined": "Apr 2024"}
        ]
        
        for member in members:
            col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1, 1, 1, 1])
            
            with col1:
                st.markdown(f"""
                <div style="display: flex; align-items: center;">
                    <div style="width: 40px; height: 40px; background: linear-gradient(45deg, #667eea, #764ba2); 
                                border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                                margin-right: 10px; color: white; font-weight: bold;">
                        {member['Name'][0]}
                    </div>
                    <div>
                        <strong>{member['Name']}</strong><br>
                        <small style="color: #666;">{member['Email']}</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**Role:** {member['Role']}")
                st.markdown(f"**Joined:** {member['Joined']}")
            
            with col3:
                st.markdown(member['Status'])
            
            with col4:
                st.markdown(f"<small>{member['Last Seen']}</small>", unsafe_allow_html=True)
            
            with col5:
                if st.button("✏️", key=f"edit_member_{member['Email']}"):
                    st.info(f"Edit {member['Name']}'s settings")
            
            with col6:
                if st.button("🗑️", key=f"remove_member_{member['Email']}"):
                    st.error(f"Remove {member['Name']} from team?")
            
            st.markdown("---")
    
    with tab2:
        st.markdown("#### ➕ Invite New Members")
        
        with st.form("invite_member"):
            col1, col2 = st.columns(2)
            with col1:
                invite_email = st.text_input("📧 Email Address", placeholder="colleague@company.com")
            with col2:
                invite_role = st.selectbox("🎯 Role", ["User", "Admin", "Viewer"])
            
            invite_message = st.text_area("💬 Personal Message (Optional)", 
                                        placeholder="Join our NovaMind AI team to collaborate on exciting projects!")
            
            col1, col2 = st.columns(2)
            with col1:
                send_welcome = st.checkbox("📧 Send welcome email", True)
            with col2:
                notify_team = st.checkbox("🔔 Notify existing team", False)
            
            if st.form_submit_button("📤 Send Invitation", use_container_width=True):
                if invite_email:
                    st.success(f"✅ Invitation sent to {invite_email} as {invite_role}")
                    st.balloons()
                else:
                    st.error("⚠️ Please enter an email address")
        
        # Bulk invite option
        st.markdown("---")
        st.markdown("#### 📋 Bulk Invite")
        
        bulk_emails = st.text_area("📧 Email Addresses (one per line)", 
                                 placeholder="user1@company.com\nuser2@company.com\nuser3@company.com")
        
        col1, col2 = st.columns(2)
        with col1:
            bulk_role = st.selectbox("🎯 Default Role", ["User", "Admin", "Viewer"], key="bulk_role")
        with col2:
            if st.button("📤 Send Bulk Invitations"):
                if bulk_emails:
                    email_list = [email.strip() for email in bulk_emails.split('\n') if email.strip()]
                    st.success(f"✅ Sent {len(email_list)} invitations as {bulk_role}")
    
    with tab3:
        st.markdown("#### 🔐 Role & Permission Management")
        
        # Permission matrix
        st.markdown("##### 🛡️ Permission Matrix")
        
        permissions = {
            "AI Chat Access": {"Admin": "✅", "User": "✅", "Viewer": "❌"},
            "API Key Management": {"Admin": "✅", "User": "❌", "Viewer": "❌"},
            "Team Management": {"Admin": "✅", "User": "❌", "Viewer": "❌"},
            "Analytics Access": {"Admin": "✅", "User": "✅", "Viewer": "✅"},
            "Project Creation": {"Admin": "✅", "User": "✅", "Viewer": "❌"},
            "Billing Access": {"Admin": "✅", "User": "❌", "Viewer": "❌"},
            "Settings Management": {"Admin": "✅", "User": "🔸", "Viewer": "❌"}
        }
        
        # Create permission table
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            st.markdown("**Permission**")
        with col2:
            st.markdown("**Admin**")
        with col3:
            st.markdown("**User**")
        with col4:
            st.markdown("**Viewer**")
        
        st.markdown("---")
        
        for permission, roles in permissions.items():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.markdown(permission)
            with col2:
                st.markdown(roles["Admin"])
            with col3:
                st.markdown(roles["User"])
            with col4:
                st.markdown(roles["Viewer"])
        
        st.markdown("---")
        st.markdown("**Legend:** ✅ Full Access | 🔸 Limited Access | ❌ No Access")
        
        # Custom role creation
        st.markdown("##### ➕ Create Custom Role")
        with st.expander("🛠️ Advanced Role Settings"):
            custom_role_name = st.text_input("🏷️ Role Name", placeholder="Custom Role")
            
            st.markdown("**Select Permissions:**")
            for permission in permissions.keys():
                st.checkbox(permission, key=f"custom_{permission}")
            
            if st.button("➕ Create Custom Role"):
                st.success(f"✅ Custom role '{custom_role_name}' created!")
    
    with tab4:
        st.markdown("#### 📊 Team Activity Dashboard")
        
        # Activity metrics
        col1, col2, col3 = st.columns(3)
        
        activity_metrics = [
            ("🔥 Active Today", "8 members", "#28a745"),
            ("💬 Total Messages", "1,247", "#17a2b8"),
            ("🤖 AI Interactions", "456", "#667eea")
        ]
        
        for i, (title, value, color) in enumerate(activity_metrics):
            with [col1, col2, col3][i]:
                st.markdown(f"""
                <div style="background: {color}; color: white; padding: 20px; 
                            border-radius: 15px; text-align: center; margin: 5px 0;">
                    <h2 style="margin: 0; font-size: 1.8rem;">{value}</h2>
                    <p style="margin: 5px 0 0 0; font-size: 0.9rem;">{title}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Recent activity feed
        st.markdown("##### 📈 Recent Team Activity")
        
        team_activities = [
            {"User": "John Doe", "Action": "Created new AI chat session", "Time": "2 minutes ago", "Type": "chat"},
            {"User": "Jane Smith", "Action": "Updated API configuration", "Time": "15 minutes ago", "Type": "config"},
            {"User": "Bob Wilson", "Action": "Exported analytics report", "Time": "1 hour ago", "Type": "export"},
            {"User": "Alice Brown", "Action": "Invited new team member", "Time": "3 hours ago", "Type": "invite"},
            {"User": "John Doe", "Action": "Modified team permissions", "Time": "5 hours ago", "Type": "admin"}
        ]
        
        action_icons = {
            "chat": "💬",
            "config": "⚙️", 
            "export": "📊",
            "invite": "👥",
            "admin": "🔐"
        }
        
        for activity in team_activities:
            icon = action_icons.get(activity["Type"], "📋")
            st.markdown(f"""
            <div style="display: flex; align-items: center; padding: 15px; margin: 10px 0; 
                        background: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        border-left: 4px solid #667eea;">
                <div style="margin-right: 15px; font-size: 1.5rem;">{icon}</div>
                <div style="flex-grow: 1;">
                    <strong>{activity['User']}</strong> {activity['Action']}<br>
                    <small style="color: #666;">{activity['Time']}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)

def show_project_management():
    """Project and workspace management"""
    st.markdown("### 🎯 Project Management")
    
    # Project overview
    col1, col2, col3, col4 = st.columns(4)
    
    project_stats = [
        ("📁 Total Projects", "15", "#667eea"),
        ("🚀 Active", "8", "#28a745"),
        ("⏸️ Paused", "4", "#ffc107"),
        ("✅ Completed", "3", "#17a2b8")
    ]
    
    for i, (title, value, color) in enumerate(project_stats):
        with [col1, col2, col3, col4][i]:
            st.markdown(f"""
            <div style="background: {color}; color: white; padding: 20px; 
                        border-radius: 15px; text-align: center; margin: 5px 0;">
                <h2 style="margin: 0; font-size: 2rem;">{value}</h2>
                <p style="margin: 5px 0 0 0; font-size: 0.9rem;">{title}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Project management tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 All Projects", "➕ Create New", "📊 Templates", "⚙️ Settings"])
    
    with tab1:
        st.markdown("#### 📋 Project Overview")
        
        # Filters and search
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            project_search = st.text_input("🔍 Search projects", placeholder="Search by name...")
        with col2:
            status_filter = st.selectbox("📊 Status", ["All", "Active", "Paused", "Completed"])
        with col3:
            priority_filter = st.selectbox("🔥 Priority", ["All", "High", "Medium", "Low"])
        with col4:
            sort_by = st.selectbox("📑 Sort by", ["Name", "Created", "Updated", "Priority"])
        
        # Projects grid
        st.markdown("---")
        
        projects = [
            {
                "name": "AI Customer Support Bot",
                "description": "Intelligent customer service automation using multiple LLM models",
                "status": "🟢 Active",
                "priority": "🔴 High",
                "team_size": 5,
                "progress": 75,
                "created": "2024-01-15",
                "ai_models": ["GPT-4", "Claude-3"]
            },
            {
                "name": "Content Generation Platform",
                "description": "Automated content creation for marketing campaigns",
                "status": "🟢 Active",
                "priority": "🟡 Medium",
                "team_size": 3,
                "progress": 60,
                "created": "2024-01-20",
                "ai_models": ["GPT-4", "Gemini"]
            },
            {
                "name": "Code Review Assistant",
                "description": "AI-powered code analysis and improvement suggestions",
                "status": "⏸️ Paused",
                "priority": "🔵 Low",
                "team_size": 2,
                "progress": 40,
                "created": "2024-01-10",
                "ai_models": ["DeepSeek-Coder"]
            },
            {
                "name": "Data Analysis Chatbot",
                "description": "Natural language interface for business intelligence",
                "status": "✅ Completed",
                "priority": "🟡 Medium",
                "team_size": 4,
                "progress": 100,
                "created": "2023-12-01",
                "ai_models": ["GPT-4", "Claude-3"]
            }
        ]
        
        for project in projects:
            with st.container():
                st.markdown(f"""
                <div style="background: white; padding: 25px; border-radius: 15px; 
                            box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin: 20px 0;
                            border-left: 5px solid #667eea;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px;">
                        <div>
                            <h3 style="margin: 0; color: #333;">{project['name']}</h3>
                            <p style="margin: 5px 0; color: #666; font-size: 0.9rem;">{project['description']}</p>
                        </div>
                        <div style="text-align: right;">
                            <div>{project['status']}</div>
                            <div style="margin-top: 5px;">{project['priority']}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
                
                with col1:
                    st.markdown(f"**👥 Team:** {project['team_size']}")
                
                with col2:
                    st.markdown(f"**📅 Created:** {project['created']}")
                
                with col3:
                    st.markdown("**📈 Progress:**")
                    st.progress(project['progress'] / 100)
                    st.markdown(f"<small>{project['progress']}% complete</small>", unsafe_allow_html=True)
                
                with col4:
                    st.markdown("**🤖 AI Models:**")
                    for model in project['ai_models']:
                        st.markdown(f"<small>• {model}</small>", unsafe_allow_html=True)
                
                with col5:
                    if st.button("👁️ View", key=f"view_{project['name']}"):
                        st.info(f"Opening {project['name']}...")
                    if st.button("✏️ Edit", key=f"edit_{project['name']}"):
                        st.info(f"Editing {project['name']}...")
    
    with tab2:
        st.markdown("#### ➕ Create New Project")
        
        with st.form("create_project"):
            col1, col2 = st.columns(2)
            
            with col1:
                project_name = st.text_input("📝 Project Name", placeholder="My AI Project")
                project_type = st.selectbox("🎯 Project Type", 
                    ["Chatbot", "Content Generation", "Data Analysis", "Code Assistant", "Custom"])
            
            with col2:
                project_priority = st.selectbox("🔥 Priority", ["High", "Medium", "Low"])
                estimated_duration = st.selectbox("⏱️ Duration", 
                    ["1-2 weeks", "1 month", "2-3 months", "3-6 months", "6+ months"])
            
            project_description = st.text_area("📋 Description", 
                placeholder="Describe your project goals and requirements...")
            
            st.markdown("**🤖 Select AI Models:**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                use_openai = st.checkbox("OpenAI (GPT-4/3.5)")
                use_claude = st.checkbox("Anthropic Claude")
            with col2:
                use_gemini = st.checkbox("Google Gemini")
                use_deepseek = st.checkbox("DeepSeek")
            with col3:
                use_mistral = st.checkbox("Mistral AI")
                use_ollama = st.checkbox("Ollama (Local)")
            
            st.markdown("**👥 Team Settings:**")
            col1, col2 = st.columns(2)
            
            with col1:
                team_members = st.multiselect("Select Team Members", 
                    ["John Doe", "Jane Smith", "Bob Wilson", "Alice Brown"])
            with col2:
                project_visibility = st.selectbox("🔒 Visibility", ["Private", "Team", "Organization"])
            
            advanced_settings = st.checkbox("⚙️ Show Advanced Settings")
            
            if advanced_settings:
                with st.expander("🛠️ Advanced Configuration"):
                    col1, col2 = st.columns(2)
                    with col1:
                        custom_prompts = st.checkbox("📝 Use Custom Prompts")
                        rate_limiting = st.checkbox("⚡ Enable Rate Limiting")
                    with col2:
                        cost_tracking = st.checkbox("💰 Enable Cost Tracking")
                        auto_backup = st.checkbox("💾 Auto Backup")
                    
                    budget_limit = st.number_input("💰 Monthly Budget ($)", 0, 10000, 100)
            
            if st.form_submit_button("🚀 Create Project", use_container_width=True):
                if project_name:
                    st.success(f"✅ Project '{project_name}' created successfully!")
                    st.balloons()
                    
                    # Show project setup progress
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    steps = [
                        "Creating project workspace...",
                        "Setting up AI model connections...",
                        "Configuring team permissions...",
                        "Initializing project settings...",
                        "Project ready!"
                    ]
                    
                    for i, step in enumerate(steps):
                        status_text.text(step)
                        progress_bar.progress((i + 1) / len(steps))
                        time.sleep(0.5)
                    
                    status_text.text("🎉 Project created successfully!")
                else:
                    st.error("⚠️ Please enter a project name")
    
    with tab3:
        st.markdown("#### 📊 Project Templates")
        
        templates = [
            {
                "name": "🤖 AI Chatbot Starter",
                "description": "Ready-to-use chatbot template with multiple LLM integration",
                "features": ["Multi-LLM support", "Chat history", "Custom prompts", "Analytics"],
                "complexity": "Beginner",
                "estimated_time": "1-2 days"
            },
            {
                "name": "📝 Content Generator",
                "description": "Automated content creation for blogs, social media, and marketing",
                "features": ["Content planning", "SEO optimization", "Multi-format output", "Brand voice"],
                "complexity": "Intermediate",
                "estimated_time": "3-5 days"
            },
            {
                "name": "📊 Data Analysis Assistant",
                "description": "Natural language interface for data querying and visualization",
                "features": ["SQL generation", "Chart creation", "Report automation", "Data insights"],
                "complexity": "Advanced",
                "estimated_time": "1-2 weeks"
            },
            {
                "name": "💻 Code Review Bot",
                "description": "Automated code analysis and improvement suggestions",
                "features": ["Code analysis", "Bug detection", "Performance tips", "Documentation"],
                "complexity": "Advanced",
                "estimated_time": "1-2 weeks"
            }
        ]
        
        for template in templates:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div style="background: white; padding: 20px; border-radius: 15px; 
                            box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin: 15px 0;">
                    <h4 style="margin: 0 0 10px 0; color: #333;">{template['name']}</h4>
                    <p style="margin: 0 0 15px 0; color: #666;">{template['description']}</p>
                    
                    <div style="margin-bottom: 15px;">
                        <strong>✨ Features:</strong><br>
                        {' • '.join(template['features'])}
                    </div>
                    
                    <div style="display: flex; gap: 20px; font-size: 0.9rem;">
                        <span><strong>📈 Complexity:</strong> {template['complexity']}</span>
                        <span><strong>⏱️ Setup Time:</strong> {template['estimated_time']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("<br><br>", unsafe_allow_html=True)  # Spacing
                if st.button("🚀 Use Template", key=f"template_{template['name']}", use_container_width=True):
                    st.success(f"✅ Starting project from {template['name']} template!")
                
                if st.button("👁️ Preview", key=f"preview_{template['name']}", use_container_width=True):
                    st.info(f"📋 Showing preview for {template['name']}")
    
    with tab4:
        st.markdown("#### ⚙️ Project Settings & Configuration")
        
        # Global project settings
        st.markdown("##### 🌐 Global Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            default_ai_provider = st.selectbox("🤖 Default AI Provider", 
                ["OpenAI", "Claude", "Gemini", "DeepSeek", "Auto-Select"])
            
            auto_save = st.checkbox("💾 Auto-save project changes", True)
            
            backup_frequency = st.selectbox("🔄 Backup Frequency", 
                ["Real-time", "Hourly", "Daily", "Weekly"])
        
        with col2:
            max_projects = st.number_input("📁 Max Projects per User", 1, 100, 10)
            
            enable_collaboration = st.checkbox("👥 Enable real-time collaboration", True)
            
            cost_alerts = st.checkbox("💰 Enable cost alerts", True)
        
        # Integration settings
        st.markdown("##### 🔗 Integration Settings")
        
        with st.expander("🛠️ Third-party Integrations"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Development Tools:**")
                github_integration = st.checkbox("🐱 GitHub Integration")
                gitlab_integration = st.checkbox("🦊 GitLab Integration")
                vscode_extension = st.checkbox("💻 VS Code Extension")
            
            with col2:
                st.markdown("**Communication:**")
                slack_integration = st.checkbox("💬 Slack Integration")
                teams_integration = st.checkbox("📞 Microsoft Teams")
                discord_integration = st.checkbox("🎮 Discord Integration")
        
        # Security settings
        st.markdown("##### 🔒 Security & Privacy")
        
        col1, col2 = st.columns(2)
        
        with col1:
            data_encryption = st.checkbox("🔐 Encrypt project data", True)
            access_logs = st.checkbox("📋 Enable access logging", True)
            ip_whitelist = st.text_area("🌐 IP Whitelist (optional)", 
                placeholder="192.168.1.0/24\n10.0.0.0/8")
        
        with col2:
            session_timeout = st.selectbox("⏱️ Session Timeout", 
                ["30 minutes", "1 hour", "4 hours", "8 hours", "Never"])
            two_factor_auth = st.checkbox("🔑 Require 2FA for sensitive operations")
            audit_trail = st.checkbox("📊 Enable detailed audit trail", True)
        
        # Save settings
        if st.button("💾 Save Settings", use_container_width=True):
            st.success("✅ Settings saved successfully!")

def show_features():
    """Enhanced features showcase"""
    st.markdown("""
    <div class="features-container">
        <h3 style="text-align: center; color: #333; margin-bottom: 3rem; position: relative; z-index: 1;">
            🌟 Why Choose NovaMind AI?
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    features = [
        ("🤖", "Multi-LLM Integration", "Connect to 10+ AI providers including OpenAI, Claude, Gemini, DeepSeek", "Access the best AI models from a single platform"),
        ("⚡", "Lightning Performance", "Sub-second response times with intelligent caching and load balancing", "Optimized infrastructure for enterprise-grade speed"),
        ("🔒", "Enterprise Security", "SOC 2 compliant with end-to-end encryption and advanced access controls", "Bank-level security for your sensitive data"),
        ("📊", "Advanced Analytics", "Real-time usage monitoring, cost tracking, and performance insights", "Make data-driven decisions with comprehensive reporting"),
        ("👥", "Team Collaboration", "Multi-user workspaces with role-based permissions and real-time collaboration", "Work together seamlessly across your organization"),
        ("🛠️", "Easy Integration", "RESTful APIs, SDKs, and webhooks for seamless system integration", "Connect with your existing tools and workflows"),
        ("🎯", "Project Management", "Organized workspaces with templates, version control, and progress tracking", "Manage AI projects efficiently from start to finish"),
        ("💰", "Cost Optimization", "Intelligent routing, budget controls, and usage optimization algorithms", "Maximize value while minimizing AI infrastructure costs"),
        ("🔄", "Auto-Scaling", "Dynamic resource allocation based on demand with global load balancing", "Handle any workload without manual intervention"),
        ("📱", "Multi-Platform", "Web, mobile, desktop, and API access with full feature parity", "Work from anywhere on any device"),
        ("🎨", "Custom Branding", "White-label solutions with custom themes and domain configuration", "Make it yours with complete brand customization"),
        ("24/7", "Expert Support", "Dedicated technical support with SLA guarantees and priority assistance", "Get help when you need it from AI experts")
    ]
    
    # Create feature cards in a grid
    for i in range(0, len(features), 2):
        col1, col2 = st.columns(2)
        
        for j, col in enumerate([col1, col2]):
            if i + j < len(features):
                icon, title, desc, detail = features[i + j]
                
                with col:
                    st.markdown(f"""
                    <div class="feature-item">
                        <span class="feature-icon">{icon}</span>
                        <div>
                            <strong style="font-size: 1.1rem; color: #333;">{title}</strong><br>
                            <span style="color: #666; font-size: 0.9rem;">{desc}</span><br>
                            <small style="color: #999; font-style: italic;">{detail}</small>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

def show_demo_info():
    """Enhanced demo credentials with additional information"""
    st.markdown("""
    <div class="features-container">
        <h4 style="color: #333; text-align: center; margin-bottom: 2rem;">🎮 Try NovaMind AI Demo</h4>
        
        <div style="display: grid; gap: 20px; margin: 2rem 0;">
            <div style="background: linear-gradient(135deg, #28a745, #20c997); padding: 1.5rem; 
                        border-radius: 15px; color: white; box-shadow: 0 8px 25px rgba(40, 167, 69, 0.3);">
                <h5 style="margin: 0 0 1rem 0; display: flex; align-items: center;">
                    <span style="font-size: 1.5rem; margin-right: 10px;">👑</span> Admin Account
                </h5>
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                    <p style="margin: 0;"><strong>📧 Email:</strong> admin@novamind.ai</p>
                    <p style="margin: 5px 0 0 0;"><strong>🔑 Password:</strong> password</p>
                </div>
                <p style="margin: 0; font-size: 0.9rem; opacity: 0.9;">
                    ✨ <strong>Full Access:</strong> Team management, API configuration, billing, analytics, and all premium features
                </p>
            </div>
            
            <div style="background: linear-gradient(135deg, #17a2b8, #6f42c1); padding: 1.5rem; 
                        border-radius: 15px; color: white; box-shadow: 0 8px 25px rgba(23, 162, 184, 0.3);">
                <h5 style="margin: 0 0 1rem 0; display: flex; align-items: center;">
                    <span style="font-size: 1.5rem; margin-right: 10px;">👤</span> Standard User
                </h5>
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                    <p style
