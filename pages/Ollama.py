import streamlit as st
import os
from datetime import datetime

st.set_page_config(page_title="Ollama Course", page_icon="🦙", layout="wide")

if not st.session_state.get("authenticated", False):
    st.warning("🔒 Please sign in to access the Ollama Course.")
    st.stop()

# Header
col1, col2 = st.columns([1, 6])
with col1:
    if os.path.exists("assets/logo.png"):
        st.image("assets/logo.png", width=80)
with col2:
    st.title("🦙 Ollama Mastery Course")
    st.markdown("*Complete guide to running AI models locally*")

st.markdown("---")

# Course progress tracking
if "ollama_progress" not in st.session_state:
    st.session_state.ollama_progress = {
        "completed_lessons": [],
        "current_lesson": 1,
        "total_lessons": 12
    }

# Progress bar
progress = len(st.session_state.ollama_progress["completed_lessons"]) / st.session_state.ollama_progress["total_lessons"]
st.progress(progress, text=f"Course Progress: {len(st.session_state.ollama_progress['completed_lessons'])}/{st.session_state.ollama_progress['total_lessons']} lessons completed")

# Course navigation
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚀 Getting Started", "⚙️ Installation", "🎯 Basic Usage", "🔧 Advanced Topics", "📚 Resources"])

with tab1:
    st.header("Welcome to Ollama!")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## What is Ollama?
        
        Ollama is a powerful tool that allows you to run large language models locally on your machine. 
        It's designed to make AI accessible, private, and fast - without relying on cloud services.
        
        ### 🎯 Why Choose Ollama?
        
        **Privacy First**
        - Your data never leaves your machine
        - No internet connection required for inference
        - Complete control over your AI interactions
        
        **Cost Effective**
        - No API fees or usage limits
        - Run unlimited queries locally
        - One-time setup, lifetime usage
        
        **Performance**
        - Optimized for local hardware
        - GPU acceleration support
        - Fast inference times
        
        **Flexibility**
        - Support for multiple model formats
        - Easy model switching
        - Custom model fine-tuning
        """)
        
        if st.button("✅ Mark Lesson 1 Complete", key="lesson1"):
            if 1 not in st.session_state.ollama_progress["completed_lessons"]:
                st.session_state.ollama_progress["completed_lessons"].append(1)
                st.success("Lesson 1 completed! 🎉")
                st.rerun()
    
    with col2:
        st.markdown("### 📋 Course Overview")
        
        lessons = [
            "🚀 Introduction to Ollama",
            "💻 System Requirements",
            "⬇️ Installation Guide",
            "🔧 First Setup",
            "🤖 Running Your First Model",
            "💬 Chat Interface",
            "🛠️ Model Management",
            "⚡ Performance Optimization",
            "🔌 API Integration",
            "🎨 Custom Models",
            "🔒 Security & Privacy",
            "🚀 Advanced Use Cases"
        ]
        
        for i, lesson in enumerate(lessons, 1):
            if i in st.session_state.ollama_progress["completed_lessons"]:
                st.success(f"{lesson} ✅")
            else:
                st.markdown(f"{lesson}")

with tab2:
    st.header("Installation Guide")
    
    # OS selection
    os_choice = st.selectbox("Select your operating system:", ["Windows", "macOS", "Linux"])
    
    if os_choice == "Linux":
        st.subheader("🐧 Linux Installation")
        
        st.markdown("### Quick Install (Recommended)")
        st.code("curl -fsSL https://ollama.com/install.sh | sh", language="bash")
        
        st.markdown("### Manual Installation")
        with st.expander("📋 Step-by-step manual installation"):
            st.markdown("""
            1. **Download the binary:**
            ```bash
            curl -L https://ollama.com/download/ollama-linux-amd64 -o ollama
            chmod +x ollama
            sudo mv ollama /usr/local/bin/
            ```
            
            2. **Create a service user:**
            ```bash
            sudo useradd -r -s /bin/false -m -d /usr/share/ollama ollama
            ```
            
            3. **Create systemd service:**
            ```bash
            sudo tee /etc/systemd/system/ollama.service > /dev/null <<EOF
            [Unit]
            Description=Ollama Service
            After=network-online.target
            
            [Service]
            ExecStart=/usr/local/bin/ollama serve
            User=ollama
            Group=ollama
            Restart=always
            RestartSec=3
            
            [Install]
            WantedBy=default.target
            EOF
            ```
            
            4. **Start the service:**
            ```bash
            sudo systemctl daemon-reload
            sudo systemctl enable ollama
            sudo systemctl start ollama
            ```
            """)
    
    elif os_choice == "macOS":
        st.subheader("🍎 macOS Installation")
        
        st.markdown("### Option 1: Download from Website")
        st.markdown("1. Visit [ollama.com](https://ollama.com/download)")
        st.markdown("2. Download the macOS installer")
        st.markdown("3. Run the installer and follow instructions")
        
        st.markdown("### Option 2: Using Homebrew")
        st.code("brew install ollama", language="bash")
        
        st.markdown("### Starting Ollama")
        st.code("ollama serve", language="bash")
    
    elif os_choice == "Windows":
        st.subheader("🪟 Windows Installation")
        
        st.markdown("### Download and Install")
        st.markdown("1. Visit [ollama.com](https://ollama.com/download)")
        st.markdown("2. Download the Windows installer")
        st.markdown("3. Run the installer as Administrator")
        st.markdown("4. Follow the installation wizard")
        
        st.markdown("### Environment Variables")
        with st.expander("⚙️ Configure Windows Environment"):
            st.markdown("""
            Set these environment variables for optimal performance:
            
            - `OLLAMA_HOST`: Set to `0.0.0.0:11434` for network access
            - `OLLAMA_MODELS`: Custom model storage location
            - `OLLAMA_NUM_PARALLEL`: Number of parallel requests
            """)
    
    if st.button("✅ Mark Installation Complete", key="lesson2"):
        if 2 not in st.session_state.ollama_progress["completed_lessons"]:
            st.session_state.ollama_progress["completed_lessons"].append(2)
            st.success("Installation lesson completed! 🎉")
            st.rerun()

with tab3:
    st.header("Basic Usage")
    
    st.subheader("🤖 Your First Model")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Step 1: Pull a Model
        Start with a lightweight model like Llama 3.2:
        """)
        st.code("ollama pull llama3.2", language="bash")
        
        st.markdown("""
        ### Step 2: Run the Model
        Start an interactive chat session:
        """)
        st.code("ollama run llama3.2", language="bash")
        
        st.markdown("""
        ### Step 3: Chat!
        Type your questions and press Enter. Use `/bye` to exit.
        """)
        
        st.info("💡 **Tip**: Start with smaller models (7B parameters) before trying larger ones.")
    
    with col2:
        st.markdown("### 📚 Popular Models to Try")
        
        models = {
            "llama3.2": "Meta's latest model, great for general use",
            "codellama": "Specialized for code generation",
            "mistral": "Fast and efficient for most tasks",
            "phi3": "Microsoft's compact but powerful model",
            "gemma": "Google's open model family"
        }
        
        for model, description in models.items():
            with st.expander(f"🤖 {model}"):
                st.markdown(f"**{description}**")
                st.code(f"ollama pull {model}", language="bash")
    
    if st.button("✅ Mark Basic Usage Complete", key="lesson3"):
        if 3 not in st.session_state.ollama_progress["completed_lessons"]:
            st.session_state.ollama_progress["completed_lessons"].append(3)
            st.success("Basic usage lesson completed! 🎉")
            st.rerun()

with tab4:
    st.header("Advanced Topics")
    
    subtab1, subtab2, subtab3 = st.tabs(["🔌 API Usage", "⚡ Optimization", "🎨 Custom Models"])
    
    with subtab1:
        st.subheader("REST API Integration")
        
        st.markdown("### Generate Endpoint")
        st.code("""
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Why is the sky blue?",
  "stream": false
}'
        """, language="bash")
        
        st.markdown("### Python Integration")
        st.code("""
import requests
import json

def chat_with_ollama(message, model="llama3.2"):
    url = "http://localhost:11434/api/chat"
    data = {
        "model": model,
        "messages": [{"role": "user", "content": message}],
        "stream": False
    }
    
    response = requests.post(url, json=data)
    return response.json()["message"]["content"]

# Usage
response = chat_with_ollama("Explain quantum computing")
print(response)
        """, language="python")
    
    with subtab2:
        st.subheader("Performance Optimization")
        
        st.markdown("### GPU Acceleration")
        st.markdown("Ollama automatically detects and uses available GPUs:")
        st.code("ollama run llama3.2 --gpu", language="bash")
        
        st.markdown("### Memory Management")
        st.markdown("Control memory usage with environment variables:")
        st.code("""
export OLLAMA_NUM_PARALLEL=2
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_FLASH_ATTENTION=1
        """, language="bash")
    
    with subtab3:
        st.subheader("Creating Custom Models")
        
        st.markdown("### Modelfile Format")
        st.code("""
FROM llama3.2

# Set custom parameters
PARAMETER temperature 0.7
PARAMETER top_p 0.9

# Set system message
SYSTEM You are a helpful AI assistant specialized in Python programming.
        """, language="dockerfile")

with tab5:
    st.header("Resources & Community")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📚 Official Resources")
        st.markdown("""
        - [Ollama GitHub](https://github.com/ollama/ollama)
        - [Official Documentation](https://ollama.com/docs)
        - [Model Library](https://ollama.com/library)
        - [API Reference](https://github.com/ollama/ollama/blob/main/docs/api.md)
        """)
    
    with col2:
        st.subheader("🤝 Community")
        st.markdown("""
        - [Discord Server](https://discord.gg/ollama)
        - [Reddit Community](https://reddit.com/r/ollama)
        - [GitHub Discussions](https://github.com/ollama/ollama/discussions)
        - [Stack Overflow](https://stackoverflow.com/questions/tagged/ollama)
        """)
    
    # Course completion
    if len(st.session_state.ollama_progress["completed_lessons"]) >= 8:
        st.success("🎉 Congratulations! You've completed the Ollama course!")
        if st.button("🏆 Generate Certificate"):
            st.balloons()
            st.markdown("### 🏆 Certificate of Completion")
            st.markdown(f"""
            **This certifies that {st.session_state.get('username', 'Student')} has successfully completed the Ollama Mastery Course**
            
            Date: {datetime.now().strftime('%B %d, %Y')}
            """)

# Sidebar with quick navigation
with st.sidebar:
    st.markdown("### 🧭 Quick Navigation")
    
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("app.py")
    
    if st.button("🧠 AI Knowledge", use_container_width=True):
        st.switch_page("pages/page1.py")
    
    if st.button("📦 GitHub Resources", use_container_width=True):
        st.switch_page("pages/page3.py")
    
    st.markdown("---")
    st.markdown("### 📊 Your Progress")
    st.metric("Lessons Completed", len(st.session_state.ollama_progress["completed_lessons"]))
    st.metric("Course Progress", f"{int(progress * 100)}%")

