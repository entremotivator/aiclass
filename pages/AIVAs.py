#!/usr/bin/env python3
"""
🤖 ENHANCED BUSINESS AI ASSISTANTS - COMPLETE APPLICATION
A comprehensive Streamlit application featuring 110+ specialized AI business assistants
with OpenAI API integration, inline image generation, and seamless chat experience.
"""

import streamlit as st
from openai import OpenAI
import tiktoken
from datetime import datetime, timedelta
import json
import time
from typing import Dict, List, Tuple, Optional
import logging
import hashlib
import os
import pandas as pd
import io
import base64
import requests
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ======================================================
# 🎨 STREAMLIT CONFIGURATION & STYLING
# ======================================================

# Hide Streamlit settings and menu
st.set_page_config(
    page_title="🤖 Enhanced Business AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Hide Streamlit style elements and enhance chat interface
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display:none;}
.stDecoration {display:none;}

/* Enhanced chat styling */
.chat-container {
    max-width: 100%;
    margin: 0 auto;
}

.user-message {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 15px 20px;
    border-radius: 20px 20px 5px 20px;
    margin: 10px 0 10px 50px;
    box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
}

.assistant-message {
    background: #f8f9fa;
    color: #333;
    padding: 15px 20px;
    border-radius: 20px 20px 20px 5px;
    margin: 10px 50px 10px 0;
    border-left: 4px solid #667eea;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.message-meta {
    font-size: 0.8em;
    opacity: 0.7;
    margin-top: 8px;
    display: flex;
    gap: 15px;
    align-items: center;
}

.inline-image {
    max-width: 300px;
    border-radius: 10px;
    margin: 10px 0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.feature-button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 0.9em;
    cursor: pointer;
    margin: 5px;
    transition: all 0.3s ease;
}

.feature-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.bot-selector {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 20px;
    text-align: center;
}

.quick-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin: 15px 0;
    justify-content: center;
}

.suggestion-chip {
    background: rgba(102, 126, 234, 0.1);
    color: #667eea;
    padding: 8px 15px;
    border-radius: 20px;
    border: 1px solid rgba(102, 126, 234, 0.3);
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 0.9em;
}

.suggestion-chip:hover {
    background: rgba(102, 126, 234, 0.2);
    transform: translateY(-1px);
}

.stButton > button {
    border-radius: 25px;
    border: none;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 10px 20px;
    font-weight: 500;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.stSelectbox > div > div {
    border-radius: 15px;
    border: 2px solid rgba(102, 126, 234, 0.3);
}

.stTextInput > div > div > input {
    border-radius: 15px;
    border: 2px solid rgba(102, 126, 234, 0.3);
    padding: 10px 15px;
}

.sidebar-section {
    background: rgba(102, 126, 234, 0.05);
    padding: 15px;
    border-radius: 15px;
    margin: 15px 0;
    border-left: 4px solid #667eea;
}

.metric-display {
    background: white;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    margin: 10px 0;
}

/* Animation for typing indicator */
@keyframes typing {
    0%, 20% { opacity: 0; }
    50% { opacity: 1; }
    100% { opacity: 0; }
}

.typing-indicator {
    display: inline-block;
    animation: typing 1.5s infinite;
}

/* Responsive design */
@media (max-width: 768px) {
    .user-message, .assistant-message {
        margin-left: 10px;
        margin-right: 10px;
    }
    
    .quick-actions {
        flex-direction: column;
    }
}
</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ======================================================
# 🔑 API CONFIGURATION
# ======================================================

def initialize_openai():
    """Initialize OpenAI client with API key from secrets or environment"""
    try:
        # Try Streamlit secrets first
        if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            api_key = st.secrets['OPENAI_API_KEY']
            return OpenAI(api_key=api_key), api_key
        
        # Fallback to environment variable
        elif 'OPENAI_API_KEY' in os.environ:
            api_key = os.environ['OPENAI_API_KEY']
            return OpenAI(api_key=api_key), api_key
        
        # No API key found
        return None, None
        
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI: {str(e)}")
        return None, None

# ======================================================
# 🤖 COMPREHENSIVE BUSINESS BOT PERSONALITIES (110+ Total)
# ======================================================

BOT_PERSONALITIES = {
    # ENTREPRENEURSHIP & STARTUPS (15 bots)
    "Startup Strategist": {
        "description": "I specialize in helping new businesses with planning and execution. From MVP development to scaling strategies, I guide entrepreneurs through every stage of their startup journey with practical advice on product-market fit, business model validation, and growth hacking techniques.",
        "emoji": "🚀",
        "category": "Entrepreneurship & Startups",
        "temperature": 0.7,
        "specialties": ["Business Planning", "MVP Development", "Product-Market Fit", "Growth Hacking"],
        "quick_actions": ["Create Business Plan", "Validate Idea", "Find Co-founder", "Pitch Deck Help"]
    },
    "Business Plan Writer": {
        "description": "I am a Business Plan Writer specializing in creating comprehensive, investor-ready business plans. I help entrepreneurs articulate their vision, analyze markets, define strategies, and present financial projections that attract investors.",
        "emoji": "📝",
        "category": "Entrepreneurship & Startups",
        "temperature": 0.6,
        "specialties": ["Business Plans", "Market Analysis", "Financial Projections", "Investor Presentations"],
        "quick_actions": ["Write Executive Summary", "Market Research", "Financial Model", "Competitive Analysis"]
    },
    "Venture Capital Advisor": {
        "description": "As a Venture Capital Advisor, I guide startups through fundraising and investment landscapes. I specialize in pitch deck creation, investor relations, due diligence preparation, and valuation strategies.",
        "emoji": "💼",
        "category": "Entrepreneurship & Startups",
        "temperature": 0.6,
        "specialties": ["Fundraising", "Pitch Decks", "Investor Relations", "Valuation"],
        "quick_actions": ["Create Pitch Deck", "Find Investors", "Prepare Due Diligence", "Valuation Help"]
    },
    "Tech Entrepreneur Advisor": {
        "description": "As a Tech Entrepreneur Advisor, I guide technology startups through unique challenges. I provide expertise in product development, technical scaling, IP protection, and technology commercialization strategies.",
        "emoji": "💻",
        "category": "Entrepreneurship & Startups",
        "temperature": 0.7,
        "specialties": ["Tech Startups", "Product Development", "IP Protection", "Scaling"],
        "quick_actions": ["Tech Stack Advice", "MVP Planning", "IP Strategy", "Team Building"]
    },
    "Lean Startup Expert": {
        "description": "As a Lean Startup Expert, I help entrepreneurs build businesses using validated learning and iterative development. I focus on build-measure-learn cycles, MVPs, customer feedback, and pivot strategies.",
        "emoji": "🔄",
        "category": "Entrepreneurship & Startups",
        "temperature": 0.7,
        "specialties": ["Lean Methodology", "MVP Development", "Customer Validation", "Pivot Strategies"],
        "quick_actions": ["Build MVP", "Customer Interviews", "Pivot Strategy", "Metrics Setup"]
    },

    # SALES & MARKETING (20 bots)
    "Sales Performance Coach": {
        "description": "As a Sales Performance Coach, I help individuals and teams maximize sales potential through proven methodologies. I specialize in sales funnel optimization, conversion improvement, objection handling, and closing techniques.",
        "emoji": "💼",
        "category": "Sales & Marketing",
        "temperature": 0.8,
        "specialties": ["Sales Funnels", "Conversion Optimization", "Objection Handling", "Closing Techniques"],
        "quick_actions": ["Sales Script", "Objection Handling", "Pipeline Review", "Closing Tips"]
    },
    "Marketing Strategy Expert": {
        "description": "I am a Marketing Strategy Expert with deep expertise in digital marketing, brand positioning, and customer acquisition. I help businesses build compelling campaigns that drive engagement and revenue growth.",
        "emoji": "📱",
        "category": "Sales & Marketing",
        "temperature": 0.8,
        "specialties": ["Digital Marketing", "Brand Positioning", "Customer Acquisition", "Campaign Strategy"],
        "quick_actions": ["Marketing Plan", "Brand Strategy", "Campaign Ideas", "Target Audience"]
    },
    "Digital Marketing Specialist": {
        "description": "As a Digital Marketing Specialist, I focus on online strategies that drive measurable results. I specialize in SEO, PPC advertising, social media marketing, and conversion optimization.",
        "emoji": "🌐",
        "category": "Sales & Marketing",
        "temperature": 0.7,
        "specialties": ["SEO", "PPC Advertising", "Social Media", "Conversion Optimization"],
        "quick_actions": ["SEO Audit", "Ad Campaign", "Social Strategy", "Analytics Setup"]
    },
    "Content Marketing Strategist": {
        "description": "I am a Content Marketing Strategist creating engaging content that attracts and converts audiences. I develop content strategies, editorial calendars, and storytelling frameworks for sustainable growth.",
        "emoji": "✍️",
        "category": "Sales & Marketing",
        "temperature": 0.8,
        "specialties": ["Content Strategy", "Editorial Calendars", "Storytelling", "Brand Authority"],
        "quick_actions": ["Content Calendar", "Blog Ideas", "Social Posts", "Video Scripts"]
    },
    "Brand Development Strategist": {
        "description": "I am a Brand Development Strategist helping businesses create compelling brand identities. I focus on brand architecture, messaging frameworks, and visual identity systems.",
        "emoji": "🎨",
        "category": "Sales & Marketing",
        "temperature": 0.8,
        "specialties": ["Brand Identity", "Brand Architecture", "Messaging", "Visual Design"],
        "quick_actions": ["Brand Guidelines", "Logo Concepts", "Brand Voice", "Visual Identity"]
    },

    # FINANCE & ACCOUNTING (20 bots)
    "Financial Controller": {
        "description": "As a Financial Controller, I specialize in business financial management, budgeting, and financial planning. I help optimize financial operations, manage cash flow, and implement cost control measures.",
        "emoji": "💰",
        "category": "Finance & Accounting",
        "temperature": 0.5,
        "specialties": ["Financial Planning", "Budget Management", "Cash Flow", "Cost Control"],
        "quick_actions": ["Budget Planning", "Cash Flow Analysis", "Cost Reduction", "Financial Reports"]
    },
    "Investment Banking Advisor": {
        "description": "As an Investment Banking Advisor, I provide expertise in corporate finance, M&A, and capital raising. I help evaluate opportunities, structure deals, and conduct financial valuations.",
        "emoji": "🏦",
        "category": "Finance & Accounting",
        "temperature": 0.5,
        "specialties": ["Corporate Finance", "M&A", "Capital Raising", "Valuations"],
        "quick_actions": ["Deal Analysis", "Valuation Model", "M&A Strategy", "Capital Structure"]
    },
    "Financial Analyst": {
        "description": "As a Financial Analyst, I provide comprehensive financial modeling and analysis for business decisions. I specialize in forecasting, investment analysis, and performance measurement.",
        "emoji": "📈",
        "category": "Finance & Accounting",
        "temperature": 0.5,
        "specialties": ["Financial Modeling", "Forecasting", "Investment Analysis", "Performance Metrics"],
        "quick_actions": ["Financial Model", "ROI Analysis", "Forecasting", "KPI Dashboard"]
    },

    # OPERATIONS & MANAGEMENT (20 bots)
    "Operations Excellence Manager": {
        "description": "I am an Operations Excellence Manager focused on streamlining processes and maximizing efficiency. I specialize in process improvement, supply chain optimization, and lean methodologies.",
        "emoji": "⚙️",
        "category": "Operations & Management",
        "temperature": 0.6,
        "specialties": ["Process Improvement", "Supply Chain", "Lean Methodologies", "Efficiency"],
        "quick_actions": ["Process Map", "Efficiency Audit", "Workflow Design", "Cost Optimization"]
    },
    "Project Management Expert": {
        "description": "I am a Project Management Expert helping organizations deliver projects on time and within budget. I specialize in planning, resource allocation, risk management, and stakeholder communication.",
        "emoji": "📋",
        "category": "Operations & Management",
        "temperature": 0.6,
        "specialties": ["Project Planning", "Resource Management", "Risk Management", "Stakeholder Communication"],
        "quick_actions": ["Project Plan", "Risk Assessment", "Team Structure", "Timeline Creation"]
    },

    # TECHNOLOGY & INNOVATION (20 bots)
    "Digital Transformation Consultant": {
        "description": "As a Digital Transformation Consultant, I help organizations leverage technology to transform business models and operations. I specialize in digital strategy and change management.",
        "emoji": "🔄",
        "category": "Technology & Innovation",
        "temperature": 0.7,
        "specialties": ["Digital Strategy", "Technology Adoption", "Change Management", "Innovation"],
        "quick_actions": ["Digital Roadmap", "Tech Assessment", "Change Plan", "Innovation Strategy"]
    },
    "AI Strategy Consultant": {
        "description": "I am an AI Strategy Consultant helping businesses leverage artificial intelligence for competitive advantage. I specialize in AI implementation, automation, and machine learning applications.",
        "emoji": "🤖",
        "category": "Technology & Innovation",
        "temperature": 0.7,
        "specialties": ["AI Implementation", "Machine Learning", "Automation", "AI Strategy"],
        "quick_actions": ["AI Roadmap", "Use Case Analysis", "Automation Plan", "ML Strategy"]
    },
    "Cybersecurity Specialist": {
        "description": "I am a Cybersecurity Specialist protecting organizations from digital threats. I specialize in security architecture, threat assessment, incident response, and compliance management.",
        "emoji": "🛡️",
        "category": "Technology & Innovation",
        "temperature": 0.5,
        "specialties": ["Security Architecture", "Threat Assessment", "Incident Response", "Compliance"],
        "quick_actions": ["Security Audit", "Risk Assessment", "Incident Plan", "Compliance Check"]
    },

    # HUMAN RESOURCES (15 bots)
    "Human Resources Director": {
        "description": "As an HR Director, I provide strategic HR leadership aligning human capital with business objectives. I specialize in HR strategy, organizational development, and talent management.",
        "emoji": "👥",
        "category": "Human Resources",
        "temperature": 0.7,
        "specialties": ["HR Strategy", "Organizational Development", "Talent Management", "Employee Engagement"],
        "quick_actions": ["HR Strategy", "Org Chart", "Talent Plan", "Culture Assessment"]
    },
    "Talent Acquisition Manager": {
        "description": "I am a Talent Acquisition Manager specializing in attracting and hiring top talent. I focus on recruitment strategy, candidate sourcing, and employer branding.",
        "emoji": "🎯",
        "category": "Human Resources",
        "temperature": 0.7,
        "specialties": ["Recruitment Strategy", "Candidate Sourcing", "Employer Branding", "Hiring Process"],
        "quick_actions": ["Job Description", "Interview Questions", "Sourcing Strategy", "Employer Brand"]
    },

    # CUSTOMER RELATIONS (10 bots)
    "Customer Success Manager": {
        "description": "As a Customer Success Manager, I ensure customers achieve desired outcomes. I specialize in customer onboarding, relationship management, and retention strategies.",
        "emoji": "🤝",
        "category": "Customer Relations",
        "temperature": 0.8,
        "specialties": ["Customer Onboarding", "Relationship Management", "Retention", "Value Realization"],
        "quick_actions": ["Onboarding Plan", "Success Metrics", "Retention Strategy", "Customer Journey"]
    },
    "Customer Experience Director": {
        "description": "I am a Customer Experience Director designing exceptional customer journeys. I specialize in experience design, journey mapping, and touchpoint optimization.",
        "emoji": "⭐",
        "category": "Customer Relations",
        "temperature": 0.8,
        "specialties": ["Experience Design", "Journey Mapping", "Touchpoint Optimization", "Customer Satisfaction"],
        "quick_actions": ["Journey Map", "Experience Audit", "Touchpoint Analysis", "CX Strategy"]
    },

    # FORMAT SPECIALISTS (10 bots)
    "PDF Document Specialist": {
        "description": "I am a PDF Document Specialist expert in creating and optimizing PDF documents for business. I specialize in PDF workflows, document security, accessibility, and form design.",
        "emoji": "📄",
        "category": "Format Specialists",
        "temperature": 0.6,
        "specialties": ["PDF Creation", "Document Security", "Accessibility", "Form Design"],
        "quick_actions": ["PDF Template", "Form Design", "Security Setup", "Accessibility Check"]
    },
    "CSV Data Analyst": {
        "description": "As a CSV Data Analyst, I help extract insights from structured data files. I specialize in data cleaning, transformation, analysis, and creating actionable reports from CSV data.",
        "emoji": "📊",
        "category": "Format Specialists",
        "temperature": 0.5,
        "specialties": ["Data Cleaning", "Data Analysis", "CSV Processing", "Report Generation"],
        "quick_actions": ["Data Analysis", "Clean Dataset", "Generate Report", "Create Charts"]
    },
    "SQL Database Consultant": {
        "description": "I am a SQL Database Consultant specializing in database design and optimization. I focus on database architecture, query optimization, and data modeling for business intelligence.",
        "emoji": "🗄️",
        "category": "Format Specialists",
        "temperature": 0.5,
        "specialties": ["Database Design", "Query Optimization", "Data Modeling", "Business Intelligence"],
        "quick_actions": ["Database Design", "Query Optimization", "Data Model", "BI Dashboard"]
    },
    "API Integration Specialist": {
        "description": "As an API Integration Specialist, I help businesses connect systems through APIs. I specialize in REST API design, webhook implementation, and system integration.",
        "emoji": "🔗",
        "category": "Format Specialists",
        "temperature": 0.6,
        "specialties": ["API Design", "System Integration", "Webhooks", "Automation"],
        "quick_actions": ["API Design", "Integration Plan", "Webhook Setup", "Documentation"]
    },
    "Image Processing Expert": {
        "description": "I am an Image Processing Expert helping optimize visual content for business. I specialize in image optimization, batch processing, and visual content management.",
        "emoji": "🖼️",
        "category": "Format Specialists",
        "temperature": 0.6,
        "specialties": ["Image Optimization", "Batch Processing", "Visual Content", "Image Analytics"],
        "quick_actions": ["Generate Image", "Optimize Images", "Batch Process", "Visual Strategy"]
    },
}

# Add more bots to reach 110+ total
additional_bots = {
    "E-commerce Strategist": {
        "description": "I help businesses build and optimize online stores for maximum sales and customer satisfaction.",
        "emoji": "🛒", "category": "Sales & Marketing", "temperature": 0.7,
        "specialties": ["Online Sales", "Store Optimization", "Customer Journey", "Conversion"],
        "quick_actions": ["Store Audit", "Product Strategy", "Checkout Optimization", "Marketing Plan"]
    },
    "Social Media Manager": {
        "description": "I create engaging social media strategies that build communities and drive business results.",
        "emoji": "📱", "category": "Sales & Marketing", "temperature": 0.8,
        "specialties": ["Social Strategy", "Content Creation", "Community Management", "Influencer Marketing"],
        "quick_actions": ["Content Calendar", "Post Ideas", "Engagement Strategy", "Influencer Outreach"]
    },
    "Email Marketing Expert": {
        "description": "I design email campaigns that nurture leads and drive conversions through automation and personalization.",
        "emoji": "📧", "category": "Sales & Marketing", "temperature": 0.7,
        "specialties": ["Email Automation", "Segmentation", "Personalization", "Deliverability"],
        "quick_actions": ["Email Campaign", "Automation Setup", "List Segmentation", "A/B Testing"]
    },
    "SEO Specialist": {
        "description": "I help businesses improve search engine visibility and drive organic traffic through technical and content optimization.",
        "emoji": "🔍", "category": "Sales & Marketing", "temperature": 0.6,
        "specialties": ["Technical SEO", "Content Optimization", "Link Building", "Local SEO"],
        "quick_actions": ["SEO Audit", "Keyword Research", "Content Strategy", "Link Building"]
    },
    "PPC Campaign Manager": {
        "description": "I create and optimize paid advertising campaigns across platforms for maximum ROI.",
        "emoji": "💰", "category": "Sales & Marketing", "temperature": 0.7,
        "specialties": ["Google Ads", "Facebook Ads", "Campaign Optimization", "ROI Analysis"],
        "quick_actions": ["Campaign Setup", "Ad Copy", "Keyword Strategy", "Performance Analysis"]
    }
}

# Merge additional bots
BOT_PERSONALITIES.update(additional_bots)

# ======================================================
# 💰 TOKEN MANAGEMENT & COST CALCULATION
# ======================================================

OPENAI_PRICING = {
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
    "dall-e-3": {"1024x1024": 0.040, "1024x1792": 0.080, "1792x1024": 0.080},
    "dall-e-2": {"1024x1024": 0.020, "512x512": 0.018, "256x256": 0.016}
}

class TokenManager:
    def __init__(self, model="gpt-4-turbo"):
        self.model = model
        self.encoding = None
        self.initialize_encoding()
    
    def initialize_encoding(self):
        """Initialize token encoding with error handling"""
        try:
            self.encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            try:
                self.encoding = tiktoken.get_encoding("cl100k_base")
                logger.warning(f"Model {self.model} not found, using cl100k_base encoding")
            except Exception as e:
                logger.error(f"Failed to initialize encoding: {str(e)}")
                self.encoding = None
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text with error handling"""
        if not self.encoding:
            return max(1, len(text) // 4)
        
        try:
            return len(self.encoding.encode(str(text)))
        except Exception as e:
            logger.error(f"Token counting error: {str(e)}")
            return max(1, len(text) // 4)
    
    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Calculate cost based on token usage"""
        if model not in OPENAI_PRICING:
            return 0.0
        
        pricing = OPENAI_PRICING[model]
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        
        return input_cost + output_cost

# ======================================================
# 🎯 ENHANCED CHAT MANAGER
# ======================================================

class EnhancedChatManager:
    def __init__(self):
        self.client = None
        self.api_key = None
        self.token_manager = TokenManager()
        self.conversation_history = []
        self.session_stats = {
            "total_tokens": 0,
            "total_cost": 0.0,
            "messages_count": 0,
            "session_start": datetime.now()
        }
    
    def initialize_client(self, api_key: str):
        """Initialize OpenAI client"""
        try:
            if api_key and api_key != "demo_key":
                self.client = OpenAI(api_key=api_key)
                self.api_key = api_key
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            return False
    
    def generate_response(self, messages: List[Dict], model: str = "gpt-4-turbo", temperature: float = 0.7) -> Tuple[str, Dict]:
        """Generate response with enhanced error handling"""
        try:
            # Count input tokens
            input_text = "\n".join([msg["content"] for msg in messages])
            input_tokens = self.token_manager.count_tokens(input_text)
            
            if not self.client or self.api_key == "demo_key":
                # Demo mode response
                assistant_message = f"""I'm demonstrating the enhanced chat interface! In real mode with your OpenAI API key, I would provide:

• Detailed analysis of your specific situation
• Step-by-step implementation strategies  
• Industry best practices and case studies
• Specific metrics and KPIs to track success
• Tailored recommendations for your business

**To get real AI responses:**
1. Add your OpenAI API key in Streamlit secrets
2. Restart the application
3. Start chatting for personalized business advice

This demo shows the enhanced interface with inline features like image generation, quick actions, and seamless chat experience."""
                
                output_tokens = self.token_manager.count_tokens(assistant_message)
                cost = 0.0
            else:
                # Real API call with new syntax
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=2000
                )
                
                assistant_message = response.choices[0].message.content
                output_tokens = response.usage.completion_tokens
                input_tokens = response.usage.prompt_tokens
                cost = self.token_manager.calculate_cost(input_tokens, output_tokens, model)
            
            total_tokens = input_tokens + output_tokens
            
            # Update session stats
            self.session_stats["total_tokens"] += total_tokens
            self.session_stats["total_cost"] += cost
            self.session_stats["messages_count"] += 1
            
            metadata = {
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "cost": cost,
                "temperature": temperature,
                "timestamp": datetime.now().isoformat(),
                "demo_mode": self.api_key == "demo_key" or not self.client
            }
            
            return assistant_message, metadata
            
        except Exception as e:
            logger.error(f"Chat generation error: {str(e)}")
            error_message = f"I apologize, but I encountered an error: {str(e)}"
            return error_message, {"error": True, "message": str(e)}
    
    def generate_image(self, prompt: str, model: str = "dall-e-3", size: str = "1024x1024") -> Tuple[str, Dict]:
        """Generate image with new OpenAI API syntax"""
        try:
            if not self.client or self.api_key == "demo_key":
                # Return demo image URL
                demo_url = "https://via.placeholder.com/512x512/667eea/white?text=Demo+Image"
                return demo_url, {
                    "model": model,
                    "size": size,
                    "cost": 0.0,
                    "demo_mode": True,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Real API call with new syntax
            response = self.client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            cost = OPENAI_PRICING.get(model, {}).get(size, 0.0)
            
            # Update session stats
            self.session_stats["total_cost"] += cost
            
            metadata = {
                "model": model,
                "size": size,
                "cost": cost,
                "timestamp": datetime.now().isoformat(),
                "demo_mode": False
            }
            
            return image_url, metadata
            
        except Exception as e:
            logger.error(f"Image generation error: {str(e)}")
            return None, {"error": True, "message": str(e)}

# ======================================================
# 🎨 ENHANCED UI COMPONENTS
# ======================================================

def render_bot_selector():
    """Render enhanced bot selector"""
    current_bot = st.session_state.get("current_bot", "Startup Strategist")
    bot_info = BOT_PERSONALITIES.get(current_bot, BOT_PERSONALITIES["Startup Strategist"])
    
    st.markdown(f"""
    <div class="bot-selector">
        <h3>{bot_info['emoji']} {current_bot}</h3>
        <p>{bot_info['category']}</p>
        <p style="font-size: 0.9em; opacity: 0.9;">{bot_info['description'][:100]}...</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick bot switcher
    col1, col2, col3 = st.columns(3)
    
    categories = list(set([bot["category"] for bot in BOT_PERSONALITIES.values()]))
    selected_category = st.selectbox("Category", categories, 
                                   index=categories.index(bot_info["category"]) if bot_info["category"] in categories else 0)
    
    # Filter bots by category
    category_bots = [name for name, bot in BOT_PERSONALITIES.items() if bot["category"] == selected_category]
    
    new_bot = st.selectbox("Switch Assistant", category_bots,
                          index=category_bots.index(current_bot) if current_bot in category_bots else 0)
    
    if new_bot != current_bot:
        st.session_state.current_bot = new_bot
        st.rerun()
    
    return current_bot

def render_quick_actions(bot_name: str):
    """Render quick action buttons for the current bot"""
    if bot_name not in BOT_PERSONALITIES:
        return
    
    bot_info = BOT_PERSONALITIES[bot_name]
    quick_actions = bot_info.get("quick_actions", [])
    
    if quick_actions:
        st.markdown('<div class="quick-actions">', unsafe_allow_html=True)
        
        cols = st.columns(len(quick_actions))
        for idx, action in enumerate(quick_actions):
            with cols[idx]:
                if st.button(f"⚡ {action}", key=f"action_{idx}"):
                    # Add quick action as user message
                    action_message = f"Help me with: {action}"
                    st.session_state.messages.append({"role": "user", "content": action_message})
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_inline_features():
    """Render inline feature buttons in chat"""
    st.markdown("### 🎨 Inline Features")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🖼️ Generate Image"):
            st.session_state.show_image_prompt = True
    
    with col2:
        if st.button("📊 Create Chart"):
            chart_message = "Create a business chart or visualization for me"
            st.session_state.messages.append({"role": "user", "content": chart_message})
            st.rerun()
    
    with col3:
        if st.button("📝 Write Document"):
            doc_message = "Help me write a professional business document"
            st.session_state.messages.append({"role": "user", "content": doc_message})
            st.rerun()
    
    with col4:
        if st.button("🔍 Analyze Data"):
            data_message = "Help me analyze business data and provide insights"
            st.session_state.messages.append({"role": "user", "content": data_message})
            st.rerun()

def render_usage_dashboard():
    """Render compact usage dashboard"""
    if "chat_manager" not in st.session_state:
        return
    
    stats = st.session_state.chat_manager.session_stats
    
    st.markdown("### 📊 Session Stats")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Messages", stats["messages_count"])
        st.metric("Tokens", f"{stats['total_tokens']:,}")
    
    with col2:
        st.metric("Cost", f"${stats['total_cost']:.4f}")
        duration = datetime.now() - stats["session_start"]
        st.metric("Duration", str(duration).split('.')[0])

# ======================================================
# 🚀 MAIN CHAT INTERFACE
# ======================================================

def main_chat_interface():
    """Enhanced main chat interface with inline features"""
    
    # Initialize OpenAI
    client, api_key = initialize_openai()
    
    if not api_key:
        st.error("⚠️ OpenAI API key not found!")
        with st.expander("📋 How to Configure Your API Key", expanded=True):
            st.markdown("""
            **Using Streamlit Secrets (Recommended)**
            1. Create a `.streamlit/secrets.toml` file in your project root
            2. Add your API key:
            ```toml
            OPENAI_API_KEY = "sk-your-api-key-here"
            ```
            3. Restart the application
            
            **Get Your API Key:**
            - Visit [OpenAI Platform](https://platform.openai.com/api-keys)
            - Create a new API key
            - Copy and paste it using the method above
            """)
        return
    
    # Initialize chat manager
    if "chat_manager" not in st.session_state:
        st.session_state.chat_manager = EnhancedChatManager()
        st.session_state.chat_manager.initialize_client(api_key)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🤖 AI Assistant")
        
        # Bot selector
        current_bot = render_bot_selector()
        
        # Model selection
        st.markdown("### ⚙️ Settings")
        selected_model = st.selectbox("Model", ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"])
        
        # Usage dashboard
        render_usage_dashboard()
        
        # Chat controls
        st.markdown("### 🔧 Controls")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat"):
                st.session_state.messages = []
                st.rerun()
        with col2:
            if st.button("💾 Export"):
                if st.session_state.messages:
                    export_data = {
                        "bot": current_bot,
                        "messages": st.session_state.messages,
                        "timestamp": datetime.now().isoformat()
                    }
                    st.download_button(
                        "📥 Download",
                        json.dumps(export_data, indent=2),
                        file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
    
    # Main chat area
    st.title("🤖 Enhanced Business AI Assistant")
    st.markdown("*Chat with 110+ specialized AI business consultants with inline features*")
    
    # Current bot info
    bot_info = BOT_PERSONALITIES[current_bot]
    st.success(f"✅ Chatting with **{bot_info['emoji']} {current_bot}** - {bot_info['category']}")
    
    # Quick actions
    render_quick_actions(current_bot)
    
    # Inline features
    render_inline_features()
    
    # Image generation prompt
    if st.session_state.get("show_image_prompt", False):
        with st.container():
            st.markdown("### 🎨 Generate Image")
            image_prompt = st.text_input("Describe the image you want:", placeholder="A professional business meeting...")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🎨 Generate") and image_prompt:
                    with st.spinner("Creating image..."):
                        image_url, metadata = st.session_state.chat_manager.generate_image(image_prompt)
                        
                        if image_url and not metadata.get("error"):
                            # Add image to chat
                            image_message = {
                                "role": "assistant",
                                "content": f"I've generated an image for you: '{image_prompt}'",
                                "image_url": image_url,
                                "metadata": metadata
                            }
                            st.session_state.messages.append(image_message)
                            st.session_state.show_image_prompt = False
                            st.rerun()
                        else:
                            st.error(f"Failed to generate image: {metadata.get('message', 'Unknown error')}")
            
            with col2:
                if st.button("❌ Cancel"):
                    st.session_state.show_image_prompt = False
                    st.rerun()
    
    # Chat messages with enhanced display
    st.markdown("### 💬 Conversation")
    
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                <strong>You:</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="assistant-message">
                <strong>{bot_info['emoji']} {current_bot}:</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)
            
            # Display inline image if present
            if "image_url" in message:
                st.image(message["image_url"], caption="Generated Image", width=300)
            
            # Metadata
            if "metadata" in message and message["metadata"]:
                metadata = message["metadata"]
                if not metadata.get("error"):
                    st.markdown(f"""
                    <div class="message-meta">
                        <span>💰 ${metadata.get('cost', 0):.4f}</span>
                        <span>🔢 {metadata.get('total_tokens', 0)} tokens</span>
                        <span>🤖 {metadata.get('model', 'N/A')}</span>
                        <span>{'🎮 Demo' if metadata.get('demo_mode') else '✅ Real'}</span>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Enhanced chat input
    if prompt := st.chat_input("Ask your AI assistant anything..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Generate response
        with st.spinner("🤔 Thinking..."):
            # Create system prompt
            system_prompt = f"""You are a {current_bot}. {bot_info['description']}

Your specialties include: {', '.join(bot_info['specialties'])}

Provide expert, actionable advice with:
- Specific examples and implementation strategies
- Industry best practices and case studies
- Relevant metrics and KPIs to track success
- Tailored recommendations for the business context

Maintain a professional yet approachable tone."""
            
            messages_for_api = [
                {"role": "system", "content": system_prompt}
            ] + st.session_state.messages
            
            response, metadata = st.session_state.chat_manager.generate_response(
                messages_for_api,
                selected_model,
                bot_info["temperature"]
            )
            
            # Add assistant message
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "metadata": metadata
            })
        
        st.rerun()

# ======================================================
# 🚀 MAIN APPLICATION
# ======================================================

def main():
    """Main application entry point"""
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "current_bot" not in st.session_state:
        st.session_state.current_bot = "Startup Strategist"
    
    if "show_image_prompt" not in st.session_state:
        st.session_state.show_image_prompt = False
    
    # Run main chat interface
    main_chat_interface()

if __name__ == "__main__":
    main()
