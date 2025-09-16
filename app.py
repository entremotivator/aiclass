import streamlit as st
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

# Page config
st.set_page_config(page_title="Chatbot with OpenAI", page_icon="🤖")

st.title("🤖 Chat with OpenAI")

# Sidebar for API Key input
st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")

# Model selection
model = st.sidebar.selectbox("Choose a model", ["gpt-3.5-turbo", "gpt-4"])

# Check API key
if not api_key:
    st.warning("Please enter your OpenAI API key in the sidebar.")
    st.stop()

# Create client using new OpenAI SDK style
client = OpenAI(api_key=api_key)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

# Show chat history
for msg in st.session_state.messages[1:]:  # Skip system message
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box for user
user_input = st.chat_input("Say something...")

if user_input:
    # Show user message
    st.chat_message("user").markdown(user_input)

    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        # Call OpenAI Chat API
        response = client.chat.completions.create(
            model=model,
            messages=st.session_state.messages,
        )

        # Get assistant's reply
        assistant_msg = response.choices[0].message.content

        # Show assistant message
        st.chat_message("assistant").markdown(assistant_msg)

        # Save assistant message to history
        st.session_state.messages.append({"role": "assistant", "content": assistant_msg})

    except Exception as e:
        st.error(f"Error: {e}")

