import streamlit as st
import openai

# Page config
st.set_page_config(page_title="Chatbot with OpenAI", page_icon="🤖")

st.title("🤖 Chat with OpenAI")

# Sidebar for API Key input
st.sidebar.title("API Key Settings")
api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")

# If no API key provided
if not api_key:
    st.warning("Please enter your OpenAI API key in the sidebar.")
    st.stop()

# Set the OpenAI API key
openai.api_key = api_key

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

# Display chat history
for msg in st.session_state.messages[1:]:  # Skip system prompt
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_input = st.chat_input("Say something...")

if user_input:
    # Show user message
    st.chat_message("user").markdown(user_input)

    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        # Get response from OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Or gpt-4 if available
            messages=st.session_state.messages,
        )

        assistant_msg = response['choices'][0]['message']['content']

        # Append assistant message
        st.session_state.messages.append({"role": "assistant", "content": assistant_msg})

        # Show assistant response
        st.chat_message("assistant").markdown(assistant_msg)

    except Exception as e:
        st.error(f"Error: {str(e)}")
