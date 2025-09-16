import streamlit as st
import requests
import json
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
import time
from datetime import datetime
import base64
from io import BytesIO
import pandas as pd

# Page config with enhanced styling
st.set_page_config(
    page_title="NovaMind AI Multi-LLM Chatbot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .provider-info {
        background-color: #f0f2f6;
        padding: 0.5rem;
        border-radius: 5px;
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    .chat-stats {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .sidebar-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🧠 NovaMind AI Multi-LLM Assistant</h1>
    <p>Advanced AI chatbot supporting multiple LLM providers</p>
</div>
""", unsafe_allow_html=True)

# Sidebar configuration
st.sidebar.title("⚙️ Configuration")

# LLM Provider Selection
provider = st.sidebar.selectbox(
    "🤖 Choose AI Provider",
    ["OpenAI", "DeepSeek", "Gemini", "Ollama", "Claude (Anthropic)", "Groq"],
    help="Select your preferred LLM provider"
)

# Provider-specific configurations
if provider == "OpenAI":
    st.sidebar.markdown("### 🔑 OpenAI Settings")
    api_key = st.sidebar.text_input("OpenAI API Key", type="password")
    model = st.sidebar.selectbox(
        "Model",
        ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o", "gpt-4o-mini"],
        index=0
    )
    
elif provider == "DeepSeek":
    st.sidebar.markdown("### 🔑 DeepSeek Settings")
    api_key = st.sidebar.text_input("DeepSeek API Key", type="password")
    model = st.sidebar.selectbox(
        "Model",
        ["deepseek-chat", "deepseek-coder", "deepseek-reasoner"],
        index=0
    )
    
elif provider == "Gemini":
    st.sidebar.markdown("### 🔑 Google Gemini Settings")
    api_key = st.sidebar.text_input("Gemini API Key", type="password")
    model = st.sidebar.selectbox(
        "Model",
        ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash-exp"],
        index=0
    )
    
elif provider == "Ollama":
    st.sidebar.markdown("### 🔑 Ollama Settings")
    ollama_url = st.sidebar.text_input("Ollama Base URL", value="http://localhost:11434")
    model = st.sidebar.selectbox(
        "Model",
        ["llama3.2", "llama3.1", "mistral", "codellama", "phi3", "qwen2.5"],
        index=0
    )
    api_key = None  # Ollama doesn't need API key
    
elif provider == "Claude (Anthropic)":
    st.sidebar.markdown("### 🔑 Anthropic Settings")
    api_key = st.sidebar.text_input("Anthropic API Key", type="password")
    model = st.sidebar.selectbox(
        "Model",
        ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"],
        index=0
    )
    
elif provider == "Groq":
    st.sidebar.markdown("### 🔑 Groq Settings")
    api_key = st.sidebar.text_input("Groq API Key", type="password")
    model = st.sidebar.selectbox(
        "Model",
        ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"],
        index=0
    )

# Advanced settings
st.sidebar.markdown("### 🎛️ Advanced Settings")
temperature = st.sidebar.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
max_tokens = st.sidebar.slider("Max Tokens", 100, 4000, 1000, 100)
system_prompt_option = st.sidebar.selectbox(
    "System Prompt",
    ["NovaMind AI Assistant", "General Assistant", "Code Expert", "Creative Writer", "Business Analyst", "Custom"]
)

# Custom system prompt
if system_prompt_option == "Custom":
    custom_prompt = st.sidebar.text_area("Custom System Prompt", height=100)
else:
    custom_prompt = None

# Chat settings
st.sidebar.markdown("### 💬 Chat Settings")
chat_mode = st.sidebar.selectbox("Chat Mode", ["Conversation", "Q&A", "Code Assistant"])
clear_chat = st.sidebar.button("🗑️ Clear Chat History")

# Statistics
if "message_count" not in st.session_state:
    st.session_state.message_count = 0
    st.session_state.start_time = datetime.now()

st.sidebar.markdown("### 📊 Session Stats")
st.sidebar.metric("Messages", st.session_state.message_count)
if st.session_state.message_count > 0:
    duration = datetime.now() - st.session_state.start_time
    st.sidebar.metric("Duration", f"{duration.seconds // 60}m {duration.seconds % 60}s")

# System prompts dictionary
SYSTEM_PROMPTS = {
    "NovaMind AI Assistant": """
    You are an AI assistant representing NovaMind AI, a cutting-edge AI agency that provides:
    - Custom AI chatbot development
    - Multi-LLM integration and optimization
    - AI automation for business workflows
    - API integration and fine-tuning services
    - Prompt engineering and AI strategy consulting
    - Enterprise AI solutions and deployment
    
    NovaMind AI specializes in helping businesses of all sizes harness the power of multiple AI providers to create robust, scalable solutions. We work with OpenAI, DeepSeek, Gemini, Ollama, Claude, Groq, and other leading AI platforms.
    
    Brand voice: professional, innovative, and solution-focused. Provide detailed technical insights while remaining accessible. Always highlight how our multi-LLM approach gives clients flexibility, redundancy, and optimal performance for their specific use cases.
    
    If users ask about services, pricing, technical capabilities, or implementation strategies, provide comprehensive information and invite them to explore our solutions.
    """,
    
    "General Assistant": """
    You are a helpful, knowledgeable AI assistant. Provide accurate, detailed, and well-structured responses to user queries across a wide range of topics.
    """,
    
    "Code Expert": """
    You are an expert software developer and programmer. Provide high-quality code solutions, explain programming concepts clearly, debug issues, and offer best practices for software development.
    """,
    
    "Creative Writer": """
    You are a creative writing assistant. Help users with storytelling, content creation, copywriting, and creative projects. Provide engaging, imaginative, and well-crafted content.
    """,
    
    "Business Analyst": """
    You are a business analysis expert. Help users with business strategy, market analysis, process optimization, and data-driven decision making. Provide actionable insights and professional recommendations.
    """
}

# LLM API functions
def call_openai(messages, model, temperature, max_tokens, api_key):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content

def call_deepseek(messages, model, temperature, max_tokens, api_key):
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content

def call_gemini(messages, model, temperature, max_tokens, api_key):
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model_obj = genai.GenerativeModel(model)
    
    # Convert messages to Gemini format
    conversation_text = ""
    for msg in messages:
        if msg["role"] == "system":
            conversation_text += f"System: {msg['content']}\n\n"
        elif msg["role"] == "user":
            conversation_text += f"User: {msg['content']}\n\n"
        elif msg["role"] == "assistant":
            conversation_text += f"Assistant: {msg['content']}\n\n"
    
    response = model_obj.generate_content(conversation_text)
    return response.text

def call_ollama(messages, model, temperature, max_tokens, ollama_url):
    url = f"{ollama_url}/api/chat"
    
    payload = {
        "model": model,
        "messages": messages,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()["message"]["content"]

def call_claude(messages, model, temperature, max_tokens, api_key):
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    
    # Extract system message
    system_msg = ""
    conversation_msgs = []
    
    for msg in messages:
        if msg["role"] == "system":
            system_msg = msg["content"]
        else:
            conversation_msgs.append(msg)
    
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_msg,
        messages=conversation_msgs
    )
    return response.content[0].text

def call_groq(messages, model, temperature, max_tokens, api_key):
    from groq import Groq
    client = Groq(api_key=api_key)
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content

# Initialize chat history
if "messages" not in st.session_state or clear_chat:
    system_content = custom_prompt if custom_prompt else SYSTEM_PROMPTS.get(system_prompt_option, SYSTEM_PROMPTS["General Assistant"])
    st.session_state.messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": system_content.strip()}
    ]
    if clear_chat:
        st.session_state.message_count = 0
        st.session_state.start_time = datetime.now()
        st.rerun()

# Main chat interface
col1, col2 = st.columns([3, 1])

with col1:
    # Display provider info
    st.markdown(f"""
    <div class="provider-info">
        <strong>🤖 Current Provider:</strong> {provider} | <strong>📋 Model:</strong> {model} | <strong>🌡️ Temperature:</strong> {temperature}
    </div>
    """, unsafe_allow_html=True)

    # Display chat history
    for msg in st.session_state.messages[1:]:  # Skip system prompt
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

with col2:
    st.markdown("### 🎯 Quick Actions")
    
    if st.button("💡 Get AI Recommendations"):
        st.info("Ask me about:\n- AI strategy for your business\n- Best LLM for your use case\n- Implementation approaches\n- Cost optimization")
    
    if st.button("📝 Example Prompts"):
        examples = [
            "Compare different LLM providers for my chatbot",
            "How can NovaMind AI help automate my workflow?",
            "What's the best model for code generation?",
            "Explain multi-LLM architecture benefits"
        ]
        for example in examples:
            st.text(f"• {example}")
    
    st.markdown("### 📊 Model Capabilities")
    capabilities = {
        "OpenAI": "General purpose, strong reasoning",
        "DeepSeek": "Coding, mathematical reasoning",
        "Gemini": "Multimodal, long context",
        "Ollama": "Local deployment, privacy",
        "Claude": "Analysis, safety, writing",
        "Groq": "Fast inference, efficiency"
    }
    
    for prov, cap in capabilities.items():
        if prov.split()[0] == provider.split()[0]:
            st.success(f"**{prov}**: {cap}")
        else:
            st.text(f"**{prov}**: {cap}")

# Chat input
user_input = st.chat_input("Ask me anything about AI, NovaMind services, or get help with your projects...")

if user_input:
    # Validate API configuration
    if provider != "Ollama" and not api_key:
        st.error(f"Please enter your {provider} API key in the sidebar.")
        st.stop()
    
    # Show user message
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.message_count += 1
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner(f"Thinking with {provider}..."):
            try:
                # Route to appropriate API
                if provider == "OpenAI":
                    response = call_openai(st.session_state.messages, model, temperature, max_tokens, api_key)
                elif provider == "DeepSeek":
                    response = call_deepseek(st.session_state.messages, model, temperature, max_tokens, api_key)
                elif provider == "Gemini":
                    response = call_gemini(st.session_state.messages, model, temperature, max_tokens, api_key)
                elif provider == "Ollama":
                    response = call_ollama(st.session_state.messages, model, temperature, max_tokens, ollama_url)
                elif provider == "Claude (Anthropic)":
                    response = call_claude(st.session_state.messages, model, temperature, max_tokens, api_key)
                elif provider == "Groq":
                    response = call_groq(st.session_state.messages, model, temperature, max_tokens, api_key)
                
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                st.error(f"Error with {provider}: {str(e)}")
                st.info("💡 Try checking your API key, model selection, or network connection.")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🚀 NovaMind AI Services")
    st.markdown("- Multi-LLM Integration\n- Custom AI Development\n- Business Automation")

with col2:
    st.markdown("### 🔧 Technical Features")
    st.markdown("- 6+ LLM Providers\n- Advanced Configuration\n- Real-time Processing")

with col3:
    st.markdown("### 📞 Get Started")
    st.markdown("[Visit Website](#) | [Book Demo](#) | [Contact Sales](#)")

st.markdown("""
<div style='text-align: center; color: #666; margin-top: 2rem;'>
    Built with ❤️ by NovaMind AI | Powered by Multiple LLM Providers
</div>
""", unsafe_allow_html=True)
