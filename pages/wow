#!/usr/bin/env python3
"""
Simple Business AI Assistant - Streamlit Application
A streamlined version with essential AI business assistants and OpenAI integration.
"""

import streamlit as st
from openai import OpenAI
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Business AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main {
    padding-top: 1rem;
}

.chat-message {
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
    border-left: 4px solid #1f77b4;
}

.user-message {
    background-color: #e3f2fd;
    border-left-color: #2196f3;
}

.assistant-message {
    background-color: #f5f5f5;
    border-left-color: #4caf50;
}

.bot-info {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
}

.stButton > button {
    border-radius: 20px;
    border: none;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-weight: 500;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
    transform: translateY(-2px);
}
</style>
""", unsafe_allow_html=True)

# Bot personalities - simplified to key business roles
BOT_PERSONALITIES = {
    "Business Strategist": {
        "description": "I help develop comprehensive business strategies, analyze markets, and create actionable growth plans.",
        "emoji": "📊",
        "category": "Strategy",
        "system_prompt": "You are an expert Business Strategist with 15+ years of experience helping companies develop winning strategies. Provide actionable insights, market analysis, and strategic recommendations."
    },
    "Marketing Expert": {
        "description": "I specialize in digital marketing, brand positioning, and customer acquisition strategies.",
        "emoji": "📱",
        "category": "Marketing",
        "system_prompt": "You are a Marketing Expert specializing in digital marketing, brand strategy, and customer acquisition. Provide practical marketing advice with current best practices."
    },
    "Sales Coach": {
        "description": "I help optimize sales processes, improve conversion rates, and develop effective sales strategies.",
        "emoji": "💼",
        "category": "Sales",
        "system_prompt": "You are a Sales Coach with expertise in sales processes, customer relationships, and conversion optimization. Give specific, actionable sales advice."
    },
    "Financial Advisor": {
        "description": "I provide guidance on financial planning, budgeting, investment strategies, and business finance.",
        "emoji": "💰",
        "category": "Finance",
        "system_prompt": "You are a Financial Advisor specializing in business finance, budgeting, and investment strategies. Provide clear financial guidance and analysis."
    },
    "Operations Manager": {
        "description": "I help streamline operations, improve efficiency, and optimize business processes.",
        "emoji": "⚙️",
        "category": "Operations",
        "system_prompt": "You are an Operations Manager focused on process improvement, efficiency, and operational excellence. Provide practical operational solutions."
    },
    "HR Specialist": {
        "description": "I assist with talent management, employee engagement, and human resources strategies.",
        "emoji": "👥",
        "category": "Human Resources",
        "system_prompt": "You are an HR Specialist with expertise in talent management, employee engagement, and HR strategy. Provide thoughtful people management advice."
    },
    "Technology Consultant": {
        "description": "I provide guidance on digital transformation, technology adoption, and innovation strategies.",
        "emoji": "💻",
        "category": "Technology",
        "system_prompt": "You are a Technology Consultant helping businesses with digital transformation and technology strategy. Provide clear, practical tech guidance."
    },
    "Customer Success Manager": {
        "description": "I help improve customer experience, retention strategies, and relationship management.",
        "emoji": "🤝",
        "category": "Customer Relations",
        "system_prompt": "You are a Customer Success Manager focused on customer experience, retention, and relationship building. Provide customer-centric advice."
    }
}

class ChatManager:
    def __init__(self):
        self.client = None
        self.initialize_client()
    
    def initialize_client(self):
        """Initialize OpenAI client from Streamlit secrets"""
        try:
            if 'OPENAI_API_KEY' in st.secrets:
                self.client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
                return True
            else:
                st.error("OpenAI API key not found in secrets!")
                return False
        except Exception as e:
            st.error(f"Failed to initialize OpenAI client: {str(e)}")
            return False
    
    def generate_response(self, messages, model="gpt-4-turbo", temperature=0.7):
        """Generate response from OpenAI"""
        try:
            if not self.client:
                return "Error: OpenAI client not initialized"
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}"

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_bot" not in st.session_state:
        st.session_state.current_bot = "Business Strategist"
    if "chat_manager" not in st.session_state:
        st.session_state.chat_manager = ChatManager()

def render_sidebar():
    """Render sidebar with bot selection and controls"""
    st.sidebar.title("🤖 AI Assistant")
    
    # Bot selection
    current_bot = st.sidebar.selectbox(
        "Choose Your AI Assistant:",
        list(BOT_PERSONALITIES.keys()),
        index=list(BOT_PERSONALITIES.keys()).index(st.session_state.current_bot)
    )
    
    if current_bot != st.session_state.current_bot:
        st.session_state.current_bot = current_bot
    
    # Display current bot info
    bot_info = BOT_PERSONALITIES[current_bot]
    st.sidebar.markdown(f"""
    <div class="bot-info">
        <h3>{bot_info['emoji']} {current_bot}</h3>
        <p><strong>Category:</strong> {bot_info['category']}</p>
        <p>{bot_info['description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Model selection
    st.sidebar.markdown("### Settings")
    model = st.sidebar.selectbox(
        "AI Model:",
        ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
        help="Choose the AI model to use"
    )
    
    # Chat controls
    st.sidebar.markdown("### Controls")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        if st.button("💾 Export Chat"):
            if st.session_state.messages:
                export_data = {
                    "bot": current_bot,
                    "messages": st.session_state.messages,
                    "exported_at": datetime.now().isoformat()
                }
                st.sidebar.download_button(
                    "📥 Download",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
    # Session stats
    if st.session_state.messages:
        st.sidebar.markdown("### Session Stats")
        st.sidebar.metric("Messages", len(st.session_state.messages))
        
        # Calculate total characters
        total_chars = sum(len(msg["content"]) for msg in st.session_state.messages)
        st.sidebar.metric("Total Characters", f"{total_chars:,}")
    
    return current_bot, model

def render_chat_interface(current_bot, model):
    """Render main chat interface"""
    bot_info = BOT_PERSONALITIES[current_bot]
    
    # Header
    st.title(f"{bot_info['emoji']} {current_bot}")
    st.markdown(f"**{bot_info['category']} Specialist** - {bot_info['description']}")
    
    # Quick action buttons
    st.markdown("### Quick Actions")
    quick_actions = get_quick_actions(current_bot)
    
    if quick_actions:
        cols = st.columns(len(quick_actions))
        for idx, action in enumerate(quick_actions):
            with cols[idx]:
                if st.button(f"⚡ {action}", key=f"action_{idx}"):
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": f"Help me with: {action}"
                    })
                    st.rerun()
    
    # Chat history
    st.markdown("### Conversation")
    
    if not st.session_state.messages:
        st.info(f"👋 Hello! I'm your {current_bot}. How can I help you today?")
    
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>{bot_info['emoji']} {current_bot}:</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your business..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Generate response
        with st.spinner(f"{bot_info['emoji']} Thinking..."):
            # Create messages for API
            system_message = {"role": "system", "content": bot_info["system_prompt"]}
            messages_for_api = [system_message] + st.session_state.messages
            
            response = st.session_state.chat_manager.generate_response(
                messages_for_api, 
                model=model
            )
            
            # Add assistant message
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response
            })
        
        st.rerun()

def get_quick_actions(bot_name):
    """Get quick action buttons for each bot"""
    actions_map = {
        "Business Strategist": ["Business Plan", "Market Analysis", "Growth Strategy", "Competitive Analysis"],
        "Marketing Expert": ["Marketing Plan", "Social Media Strategy", "SEO Audit", "Campaign Ideas"],
        "Sales Coach": ["Sales Process", "Lead Generation", "Closing Techniques", "Pipeline Review"],
        "Financial Advisor": ["Budget Planning", "Cash Flow Analysis", "Investment Strategy", "Financial Forecast"],
        "Operations Manager": ["Process Improvement", "Efficiency Audit", "Workflow Design", "Cost Optimization"],
        "HR Specialist": ["Hiring Strategy", "Employee Engagement", "Performance Management", "Team Development"],
        "Technology Consultant": ["Digital Strategy", "Tech Stack Review", "Automation Plan", "Innovation Roadmap"],
        "Customer Success Manager": ["Customer Journey", "Retention Strategy", "Satisfaction Survey", "Support Process"]
    }
    return actions_map.get(bot_name, [])

def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Check if OpenAI client is available
    if not st.session_state.chat_manager.client:
        st.error("⚠️ OpenAI API key not configured in Streamlit secrets!")
        st.info("Please add your OpenAI API key to the Streamlit secrets configuration.")
        return
    
    # Render UI
    current_bot, model = render_sidebar()
    render_chat_interface(current_bot, model)

if __name__ == "__main__":
    main()
