# streamlit_ollama_course.py
import streamlit as st
import time
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Streamlit + Ollama Course",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .lesson-card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border-left: 5px solid #667eea;
    }
    
    .code-block {
        background: #2d3748;
        color: #e2e8f0;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-family: 'Courier New', monospace;
        border-left: 5px solid #667eea;
    }
    
    .highlight-box {
        background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #fdcb6e;
    }
    
    .warning-box {
        background: #fcf8e3;
        border: 1px solid #faebcc;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #f0ad4e;
    }
    
    .success-box {
        background: #dff0d8;
        border: 1px solid #d6e9c6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #5cb85c;
    }
    
    .project-card {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(116, 185, 255, 0.3);
    }
    
    .step-counter {
        background: #667eea;
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "current_lesson" not in st.session_state:
    st.session_state.current_lesson = 0
if "lesson_progress" not in st.session_state:
    st.session_state.lesson_progress = {}
if "show_code_examples" not in st.session_state:
    st.session_state.show_code_examples = True

# Course data structure
LESSONS = [
    {"id": "intro", "title": "Introduction", "icon": "🎯"},
    {"id": "setup", "title": "Setup & Installation", "icon": "⚙️"},
    {"id": "streamlit_basics", "title": "Streamlit Basics", "icon": "🎨"},
    {"id": "ollama_setup", "title": "Ollama Setup", "icon": "🤖"},
    {"id": "integration", "title": "Integration", "icon": "🔗"},
    {"id": "chatbot", "title": "ChatGPT Clone", "icon": "💬"},
    {"id": "advanced", "title": "Advanced Features", "icon": "🚀"},
    {"id": "deployment", "title": "Deployment", "icon": "🌐"}
]

def mark_lesson_complete(lesson_id):
    """Mark a lesson as completed"""
    st.session_state.lesson_progress[lesson_id] = True
    
def is_lesson_complete(lesson_id):
    """Check if lesson is completed"""
    return st.session_state.lesson_progress.get(lesson_id, False)

def get_progress_percentage():
    """Calculate overall progress"""
    completed = sum(1 for lesson in LESSONS if is_lesson_complete(lesson["id"]))
    return int((completed / len(LESSONS)) * 100)

def display_code_block(code, language="python", title=""):
    """Display code block with copy functionality"""
    if title:
        st.subheader(title)
    
    st.markdown('<div class="code-block">', unsafe_allow_html=True)
    st.code(code, language=language)
    st.markdown('</div>', unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.title("Course Navigation")
    
    # Progress indicator
    progress = get_progress_percentage()
    st.metric("Course Progress", f"{progress}%")
    st.progress(progress / 100)
    
    st.markdown("---")
    
    # Lesson navigation
    for i, lesson in enumerate(LESSONS):
        completed_icon = "✅" if is_lesson_complete(lesson["id"]) else "⭕"
        current_icon = "👉" if i == st.session_state.current_lesson else ""
        
        if st.button(
            f"{completed_icon} {current_icon} {lesson['icon']} {lesson['title']}", 
            key=f"nav_{lesson['id']}",
            use_container_width=True,
            type="primary" if i == st.session_state.current_lesson else "secondary"
        ):
            st.session_state.current_lesson = i
            st.rerun()
    
    st.markdown("---")
    
    # Settings
    st.subheader("Settings")
    st.session_state.show_code_examples = st.checkbox(
        "Show Code Examples", 
        value=st.session_state.show_code_examples
    )

# Main content area
current_lesson = LESSONS[st.session_state.current_lesson]

# Header
st.markdown("""
<div class="main-header">
    <h1>Streamlit + Ollama Course</h1>
    <h3>Master AI-Powered Web Applications with Python</h3>
    <p>Build ChatGPT-like applications with local AI models</p>
</div>
""", unsafe_allow_html=True)

# Lesson content based on current selection
lesson_id = current_lesson["id"]

if lesson_id == "intro":
    st.markdown('<div class="lesson-card">', unsafe_allow_html=True)
    st.title("Course Introduction")
    
    # Embedded video for Introduction
    st.markdown("""
    <div style="padding: 56.25% 0 0 0; position: relative">
        <div style="height:100%;left:0;position:absolute;top:0;width:100%">
            <iframe height="100%" width="100%;" src="https://embed.wave.video/9krwfjf82Rh2ihLP" frameborder="0" allow="autoplay; fullscreen" scrolling="no"></iframe>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
    st.markdown("### What You'll Learn")
    st.markdown("""
    - Build interactive web applications with Streamlit
    - Integrate local AI models using Ollama  
    - Create a fully functional ChatGPT clone
    - Deploy your applications to production
    - Advanced AI integration techniques
    - Performance optimization and best practices
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown("### Prerequisites")
        st.markdown("""
        - Basic Python knowledge
        - Understanding of web concepts
        - Python 3.8+ installed
        - 8GB+ RAM recommended for Ollama
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown("### Required Tools")
        st.markdown("""
        - Python 3.8+
        - Code editor (VS Code recommended)
        - Terminal/Command prompt
        - Web browser
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="project-card">', unsafe_allow_html=True)
    st.markdown("### Course Objectives")
    st.markdown("""
    By the end of this course, you'll have built a complete AI-powered web application that can:
    - Run entirely on your local machine
    - Chat with various AI models through an intuitive web interface
    - Handle file uploads and voice input
    - Export/import conversation history
    - Compare responses from multiple models
    - Be deployed to production environments
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("Mark Lesson Complete", key="complete_intro"):
        mark_lesson_complete("intro")
        st.success("Lesson completed!")
        time.sleep(1)
        st.rerun()

elif lesson_id == "setup":
    st.markdown('<div class="lesson-card">', unsafe_allow_html=True)
    st.title("Setup & Installation")
    
    st.markdown("### Step-by-Step Environment Setup")
    
    # Step 1
    st.markdown('<span class="step-counter">1</span>**Create Virtual Environment**', unsafe_allow_html=True)
    
    if st.session_state.show_code_examples:
        display_code_block("""# Create virtual environment
python -m venv streamlit_ollama_env

# Activate virtual environment
# Windows:
streamlit_ollama_env\\Scripts\\activate

# macOS/Linux:
source streamlit_ollama_env/bin/activate""", "bash")
    
    # Step 2
    st.markdown('<span class="step-counter">2</span>**Install Required Packages**', unsafe_allow_html=True)
    
    if st.session_state.show_code_examples:
        display_code_block("""# Install core packages
pip install streamlit>=1.28.0
pip install ollama>=0.1.7
pip install requests>=2.31.0
pip install python-dotenv>=1.0.0""")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("Mark Lesson Complete", key="complete_setup"):
        mark_lesson_complete("setup")
        st.success("Setup completed!")
        time.sleep(1)
        st.rerun()

elif lesson_id == "streamlit_basics":
    st.markdown('<div class="lesson-card">', unsafe_allow_html=True)
    st.title("Streamlit Fundamentals")
    
    st.markdown("### Your First Streamlit App")
    
    if st.session_state.show_code_examples:
        display_code_block("""# app.py
import streamlit as st

st.title("Welcome to Streamlit!")
name = st.text_input("Enter your name:")
if st.button("Submit"):
    st.success(f"Hello {name}!")""")
    
    # Interactive demo
    st.markdown("### Interactive Demo")
    demo_name = st.text_input("Enter your name:", key="demo_name")
    if st.button("Submit Demo", key="demo_submit"):
        st.success(f"Hello {demo_name}!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("Mark Lesson Complete", key="complete_streamlit_basics"):
        mark_lesson_complete("streamlit_basics")
        st.success("Streamlit basics mastered!")
        time.sleep(1)
        st.rerun()

elif lesson_id == "ollama_setup":
    st.markdown('<div class="lesson-card">', unsafe_allow_html=True)
    st.title("Ollama Setup & Configuration")
    
    # Embedded video for Ollama setup
    st.markdown("""
    <div style="padding: 56.25% 0 0 0; position: relative">
        <div style="height:100%;left:0;position:absolute;top:0;width:100%">
            <iframe height="100%" width="100%;" src="https://embed.wave.video/6wo392lMuElNrw3V" frameborder="0" allow="autoplay; fullscreen" scrolling="no"></iframe>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Installing Ollama")
    
    if st.session_state.show_code_examples:
        display_code_block("""# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3.2

# Test the model
ollama run llama3.2""", "bash")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("Mark Lesson Complete", key="complete_ollama_setup"):
        mark_lesson_complete("ollama_setup")
        st.success("Ollama setup completed!")
        time.sleep(1)
        st.rerun()

elif lesson_id == "integration":
    st.markdown('<div class="lesson-card">', unsafe_allow_html=True)
    st.title("Streamlit + Ollama Integration")
    
    if st.session_state.show_code_examples:
        display_code_block("""# integration.py
import streamlit as st
import ollama

st.title("AI Chat App")
user_input = st.text_input("Ask a question:")

if st.button("Send"):
    if user_input:
        response = ollama.chat(
            model='llama3.2',
            messages=[{'role': 'user', 'content': user_input}]
        )
        st.write(response['message']['content'])""")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("Mark Lesson Complete", key="complete_integration"):
        mark_lesson_complete("integration")
        st.success("Integration mastered!")
        time.sleep(1)
        st.rerun()

elif lesson_id == "chatbot":
    st.markdown('<div class="lesson-card">', unsafe_allow_html=True)
    st.title("Build a Complete ChatGPT Clone")
    
    # Embedded video for ChatGPT clone
    st.markdown("""
    <div style="padding: 56.25% 0 0 0; position: relative">
        <div style="height:100%;left:0;position:absolute;top:0;width:100%">
            <iframe height="100%" width="100%;" src="https://embed.wave.video/qA6M90GV0M8JVcKb" frameborder="0" allow="autoplay; fullscreen" scrolling="no"></iframe>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.show_code_examples:
        display_code_block("""# chatgpt_clone.py
import streamlit as st
import ollama

st.title("ChatGPT Clone")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What's your question?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        response = ollama.chat(
            model='llama3.2',
            messages=st.session_state.messages
        )
        st.markdown(response['message']['content'])
    
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response['message']['content']
    })""")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("Mark Lesson Complete", key="complete_chatbot"):
        mark_lesson_complete("chatbot")
        st.success("ChatGPT clone completed!")
        time.sleep(1)
        st.rerun()

elif lesson_id == "advanced":
    st.markdown('<div class="lesson-card">', unsafe_allow_html=True)
    st.title("Advanced Features & Optimization")
    
    st.markdown("### System Prompts & Performance")
    
    if st.session_state.show_code_examples:
        display_code_block("""# Advanced features
PERSONAS = {
    "Assistant": "You are a helpful AI assistant.",
    "Code Expert": "You are a senior software engineer.",
    "Creative Writer": "You are a creative writing assistant."
}

# Persona selection
persona = st.selectbox("Choose AI Persona:", list(PERSONAS.keys()))
system_prompt = PERSONAS[persona]

# File upload
uploaded_file = st.file_uploader("Upload a document", type=['txt', 'md'])
if uploaded_file:
    content = uploaded_file.read().decode('utf-8')
    st.text_area("File content:", value=content, height=200)

# Performance optimization with caching
@st.cache_data
def get_model_info(model_name):
    return ollama.show(model_name)""")
    
    st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
    st.markdown("### Advanced Features Summary")
    st.markdown("""
    - System Prompts: Customize AI behavior with personas
    - File Processing: Upload and analyze documents with AI
    - Performance Optimization: Caching and efficient data handling
    - Model Comparison: Side-by-side evaluation of different AI models
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("Mark Lesson Complete", key="complete_advanced"):
        mark_lesson_complete("advanced")
        st.success("Advanced features mastered!")
        time.sleep(1)
        st.rerun()

elif lesson_id == "deployment":
    st.markdown('<div class="lesson-card">', unsafe_allow_html=True)
    st.title("Deployment & Production")
    
    st.markdown("### Docker Deployment")
    
    if st.session_state.show_code_examples:
        display_code_block("""# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501"]""", "dockerfile")
        
        display_code_block("""# docker-compose.yml
version: '3.8'
services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
  
  streamlit-app:
    build: .
    ports:
      - "8501:8501"
    depends_on:
      - ollama""", "yaml")
    
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("### Security Best Practices")
    st.markdown("""
    - Never expose Ollama directly to the internet
    - Use HTTPS in production with valid SSL certificates
    - Implement proper authentication if handling sensitive data
    - Sanitize user inputs to prevent injection attacks
    - Use environment variables for sensitive configuration
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Course completion
    st.markdown('<div class="project-card">', unsafe_allow_html=True)
    st.markdown("### Congratulations!")
    st.markdown("""
    You've successfully completed the **Streamlit + Ollama Course**! You now have the skills to:
    
    - Build interactive AI-powered web applications with Streamlit
    - Integrate local AI models using Ollama
    - Create production-ready chat applications
    - Deploy applications to cloud platforms
    - Implement security and optimization best practices
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("Generate Course Completion Certificate"):
        st.balloons()
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### Certificate of Completion
        
        **Streamlit + Ollama Course**
        
        **Completed on:** {datetime.now().strftime("%B %d, %Y")}
        **Progress:** {get_progress_percentage()}% Complete
        
        You are now equipped to build AI-powered web applications!
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("Mark Lesson Complete", key="complete_deployment"):
        mark_lesson_complete("deployment")
        st.success("Course completed!")
        st.balloons()
        time.sleep(1)
        st.rerun()

# Navigation buttons
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.session_state.current_lesson > 0:
        if st.button("Previous Lesson"):
            st.session_state.current_lesson -= 1
            st.rerun()

with col3:
    if st.session_state.current_lesson < len(LESSONS) - 1:
        if st.button("Next Lesson"):
            st.session_state.current_lesson += 1
            st.rerun()

# Footer
st.markdown("---")
st.markdown(f"**Built with Streamlit** | Course Progress: {get_progress_percentage()}%")

# Auto-save progress
if st.session_state.lesson_progress:
    st.session_state["last_activity"] = datetime.now().isoformat()
