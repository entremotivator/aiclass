import streamlit as st
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

# Page config
st.set_page_config(page_title="NovaMind AI Chatbot", page_icon="🧠")

st.title("🤖 NovaMind AI Assistant")

# Sidebar for API Key input
st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")

model = st.sidebar.selectbox("Choose a model", ["gpt-3.5-turbo", "gpt-4"])

# AI Agency Persona / Training
YOUR_AGENCY_PROFILE = """
You are an AI assistant representing a company called *NovaMind AI*, a cutting-edge AI agency that provides:
- Custom AI chatbot development
- AI automation for business workflows
- OpenAI API integration
- Fine-tuning & prompt engineering
- Consulting for AI strategy and implementation

NovaMind AI helps startups, SMEs, and enterprise clients harness the power of AI to grow faster and work smarter.

Brand voice: professional, clear, and solution-focused. Avoid hype or overly technical jargon. Your job is to help users understand how NovaMind AI can solve their problems using practical AI solutions.

If a user asks about services, pricing, how to get started, or technical possibilities, respond with helpful detail and invite them to reach out or visit the website.
"""

# Check API key
if not api_key:
    st.warning("Please enter your OpenAI API key in the sidebar.")
    st.stop()

# Create OpenAI client
client = OpenAI(api_key=api_key)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": YOUR_AGENCY_PROFILE.strip()}
    ]

# Display previous messages
for msg in st.session_state.messages[1:]:  # Skip system prompt
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Get user input
user_input = st.chat_input("Ask me anything about NovaMind AI...")

if user_input:
    # Show user message
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        # Get response from OpenAI
        response = client.chat.completions.create(
            model=model,
            messages=st.session_state.messages
        )

        assistant_msg = response.choices[0].message.content
        st.chat_message("assistant").markdown(assistant_msg)

        st.session_state.messages.append({
            "role": "assistant",
            "content": assistant_msg
        })

    except Exception as e:
        st.error(f"Error: {e}")
