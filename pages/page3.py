import streamlit as st
import requests
import os
from datetime import datetime

st.set_page_config(page_title="GitHub Resources", page_icon="📦", layout="wide")

if not st.session_state.get("authenticated", False):
    st.warning("🔒 Please sign in to access GitHub Resources.")
    st.stop()

# Header
col1, col2 = st.columns([1, 6])
with col1:
    if os.path.exists("assets/logo.png"):
        st.image("assets/logo.png", width=80)
with col2:
    st.title("📦 GitHub Resources Hub")
    st.markdown("*Curated collection of AI projects, tools, and agent implementations*")

st.markdown("---")

# Resource categories
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🤖 AI Agents", "🧠 LLM Projects", "🛠️ Tools & Frameworks", "📚 Learning Resources", "🔥 Trending"])

with tab1:
    st.header("🤖 AI Agent Repositories")
    
    # Featured agent projects
    agent_projects = [
        {
            "name": "Microsoft AI Agents for Beginners",
            "repo": "microsoft/ai-agents-for-beginners",
            "description": "12 comprehensive lessons covering AI agent fundamentals",
            "stars": "2.5k",
            "language": "Python",
            "topics": ["Education", "Beginners", "Tutorial"],
            "download_url": "https://github.com/microsoft/ai-agents-for-beginners/archive/refs/heads/main.zip"
        },
        {
            "name": "GenAI Agents Collection",
            "repo": "NirDiamant/GenAI_Agents",
            "description": "Tutorials and implementations for various Generative AI Agent techniques",
            "stars": "1.8k",
            "language": "Python",
            "topics": ["Generative AI", "Advanced", "Implementations"],
            "download_url": "https://github.com/NirDiamant/GenAI_Agents/archive/refs/heads/main.zip"
        },
        {
            "name": "AI Agents Masterclass",
            "repo": "coleam00/ai-agents-masterclass",
            "description": "Complete code repository for AI Agents Masterclass video series",
            "stars": "950",
            "language": "Python",
            "topics": ["Video Course", "Practical", "Hands-on"],
            "download_url": "https://github.com/coleam00/ai-agents-masterclass/archive/refs/heads/main.zip"
        },
        {
            "name": "500+ AI Agent Projects",
            "repo": "ashishpatel26/500-AI-Agents-Projects",
            "description": "Curated collection of AI agent use cases across industries",
            "stars": "1.2k",
            "language": "Multiple",
            "topics": ["Use Cases", "Industry", "Collection"],
            "download_url": "https://github.com/ashishpatel26/500-AI-Agents-Projects/archive/refs/heads/main.zip"
        }
    ]
    
    for project in agent_projects:
        with st.expander(f"⭐ {project['name']} ({project['stars']} stars)"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Repository:** `{project['repo']}`")
                st.markdown(f"**Description:** {project['description']}")
                st.markdown(f"**Language:** {project['language']}")
                
                # Topics as badges
                topics_html = " ".join([f'<span style="background-color: #e1f5fe; color: #01579b; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-right: 4px;">{topic}</span>' for topic in project['topics']])
                st.markdown(topics_html, unsafe_allow_html=True)
            
            with col2:
                st.markdown("### Quick Actions")
                if st.button(f"📥 Download ZIP", key=f"download_{project['repo'].replace('/', '_')}"):
                    st.success(f"Download link: {project['download_url']}")
                    st.markdown(f"[Click here to download]({project['download_url']})")
                
                if st.button(f"🔗 View on GitHub", key=f"github_{project['repo'].replace('/', '_')}"):
                    st.markdown(f"[Open Repository](https://github.com/{project['repo']})")

with tab2:
    st.header("🧠 Large Language Model Projects")
    
    llm_projects = [
        {
            "name": "Ollama",
            "repo": "ollama/ollama",
            "description": "Get up and running with large language models locally",
            "stars": "95k",
            "language": "Go",
            "topics": ["Local LLM", "Production", "CLI"],
            "download_url": "https://github.com/ollama/ollama/archive/refs/heads/main.zip"
        },
        {
            "name": "LocalAI",
            "repo": "mudler/LocalAI",
            "description": "Self-hosted, community-driven, local OpenAI-compatible API",
            "stars": "25k",
            "language": "Go",
            "topics": ["Self-hosted", "OpenAI Compatible", "API"],
            "download_url": "https://github.com/mudler/LocalAI/archive/refs/heads/master.zip"
        },
        {
            "name": "Text Generation WebUI",
            "repo": "oobabooga/text-generation-webui",
            "description": "A Gradio web UI for Large Language Models",
            "stars": "40k",
            "language": "Python",
            "topics": ["Web UI", "Gradio", "Interface"],
            "download_url": "https://github.com/oobabooga/text-generation-webui/archive/refs/heads/main.zip"
        },
        {
            "name": "LlamaIndex",
            "repo": "run-llama/llama_index",
            "description": "LlamaIndex is a data framework for LLM applications",
            "stars": "36k",
            "language": "Python",
            "topics": ["Data Framework", "RAG", "Enterprise"],
            "download_url": "https://github.com/run-llama/llama_index/archive/refs/heads/main.zip"
        }
    ]
    
    col1, col2 = st.columns(2)
    
    for i, project in enumerate(llm_projects):
        with (col1 if i % 2 == 0 else col2):
            with st.container():
                st.markdown(f"### ⭐ {project['name']}")
                st.markdown(f"**{project['stars']} stars** | **{project['language']}**")
                st.markdown(project['description'])
                
                # Topics
                topics_html = " ".join([f'<span style="background-color: #f3e5f5; color: #4a148c; padding: 2px 6px; border-radius: 10px; font-size: 11px; margin-right: 3px;">{topic}</span>' for topic in project['topics']])
                st.markdown(topics_html, unsafe_allow_html=True)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("📥 Download", key=f"llm_download_{i}"):
                        st.success(f"[Download ZIP]({project['download_url']})")
                with col_b:
                    if st.button("🔗 GitHub", key=f"llm_github_{i}"):
                        st.markdown(f"[View Repository](https://github.com/{project['repo']})")
                
                st.markdown("---")

with tab3:
    st.header("🛠️ AI Tools & Frameworks")
    
    frameworks = [
        {
            "category": "🔗 Agent Frameworks",
            "projects": [
                {"name": "LangChain", "repo": "langchain-ai/langchain", "desc": "Build applications with LLMs through composability"},
                {"name": "CrewAI", "repo": "joaomdmoura/crewAI", "desc": "Framework for orchestrating role-playing, autonomous AI agents"},
                {"name": "AutoGen", "repo": "microsoft/autogen", "desc": "Multi-agent conversation framework"},
                {"name": "Semantic Kernel", "repo": "microsoft/semantic-kernel", "desc": "Integrate large language models with conventional programming"}
            ]
        },
        {
            "category": "🎨 Generative AI",
            "projects": [
                {"name": "Stable Diffusion WebUI", "repo": "AUTOMATIC1111/stable-diffusion-webui", "desc": "Web interface for Stable Diffusion"},
                {"name": "ComfyUI", "repo": "comfyanonymous/ComfyUI", "desc": "Powerful and modular stable diffusion GUI"},
                {"name": "Fooocus", "repo": "lllyasviel/Fooocus", "desc": "Focus on prompting and generating"},
                {"name": "InvokeAI", "repo": "invoke-ai/InvokeAI", "desc": "Leading creative engine for Stable Diffusion models"}
            ]
        },
        {
            "category": "📊 ML & Data Science",
            "projects": [
                {"name": "Hugging Face Transformers", "repo": "huggingface/transformers", "desc": "State-of-the-art Machine Learning for PyTorch, TensorFlow, and JAX"},
                {"name": "MLflow", "repo": "mlflow/mlflow", "desc": "Open source platform for the machine learning lifecycle"},
                {"name": "DVC", "repo": "iterative/dvc", "desc": "Data Version Control | Git for Data & Models"},
                {"name": "Weights & Biases", "repo": "wandb/wandb", "desc": "A tool for visualizing and tracking your machine learning experiments"}
            ]
        }
    ]
    
    for framework in frameworks:
        st.subheader(framework["category"])
        
        cols = st.columns(2)
        for i, project in enumerate(framework["projects"]):
            with cols[i % 2]:
                with st.container():
                    st.markdown(f"**{project['name']}**")
                    st.markdown(f"`{project['repo']}`")
                    st.markdown(project['desc'])
                    
                    col_x, col_y = st.columns(2)
                    with col_x:
                        if st.button("📥", key=f"tool_dl_{project['repo'].replace('/', '_')}"):
                            download_url = f"https://github.com/{project['repo']}/archive/refs/heads/main.zip"
                            st.markdown(f"[Download]({download_url})")
                    with col_y:
                        if st.button("🔗", key=f"tool_gh_{project['repo'].replace('/', '_')}"):
                            st.markdown(f"[GitHub](https://github.com/{project['repo']})")
                    
                    st.markdown("---")

with tab4:
    st.header("📚 Learning Resources")
    
    learning_resources = [
        {
            "name": "Machine Learning Yearning",
            "repo": "ajaymache/machine-learning-yearning",
            "description": "Andrew Ng's insights on machine learning projects",
            "type": "📖 Book",
            "level": "Intermediate"
        },
        {
            "name": "Deep Learning Papers Reading Roadmap",
            "repo": "floodsung/Deep-Learning-Papers-Reading-Roadmap",
            "description": "Roadmap for deep learning papers",
            "type": "📄 Papers",
            "level": "Advanced"
        },
        {
            "name": "AI Expert Roadmap",
            "repo": "AMAI-GmbH/AI-Expert-Roadmap",
            "description": "Roadmap to becoming an AI expert",
            "type": "🗺️ Roadmap",
            "level": "All Levels"
        },
        {
            "name": "Awesome Machine Learning",
            "repo": "josephmisiti/awesome-machine-learning",
            "description": "Curated list of awesome ML frameworks, libraries and software",
            "type": "📋 Awesome List",
            "level": "All Levels"
        }
    ]
    
    for resource in learning_resources:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"### {resource['name']}")
                st.markdown(resource['description'])
                st.markdown(f"**Repository:** `{resource['repo']}`")
            
            with col2:
                st.markdown(f"**Type:** {resource['type']}")
                st.markdown(f"**Level:** {resource['level']}")
            
            with col3:
                if st.button("📥 Download", key=f"learn_{resource['repo'].replace('/', '_')}"):
                    download_url = f"https://github.com/{resource['repo']}/archive/refs/heads/main.zip"
                    st.success(f"[Download ZIP]({download_url})")
                
                if st.button("🔗 View", key=f"learn_view_{resource['repo'].replace('/', '_')}"):
                    st.markdown(f"[Open on GitHub](https://github.com/{resource['repo']})")
            
            st.markdown("---")

with tab5:
    st.header("🔥 Trending AI Projects")
    
    st.info("🚀 **Hot Right Now**: These projects are gaining significant attention in the AI community!")
    
    trending = [
        {
            "name": "OpenAI Swarm",
            "repo": "openai/swarm",
            "description": "Educational framework for multi-agent orchestration",
            "trend": "🔥 New Release",
            "stars": "15k+"
        },
        {
            "name": "Cursor Rules",
            "repo": "PatrickJS/awesome-cursorrules",
            "description": "Awesome list of cursor rules for AI-powered coding",
            "trend": "📈 Rapidly Growing",
            "stars": "5k+"
        },
        {
            "name": "Open WebUI",
            "repo": "open-webui/open-webui",
            "description": "User-friendly WebUI for LLMs (Formerly Ollama WebUI)",
            "trend": "⭐ Community Favorite",
            "stars": "45k+"
        },
        {
            "name": "Aider",
            "repo": "paul-gauthier/aider",
            "description": "AI pair programming in your terminal",
            "trend": "🚀 Developer Tool",
            "stars": "20k+"
        }
    ]
    
    for project in trending:
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"### ⭐ {project['name']} ({project['stars']} stars)")
                st.markdown(project['description'])
                st.markdown(f"**Repository:** `{project['repo']}`")
                st.markdown(f"**Status:** {project['trend']}")
            
            with col2:
                st.markdown("### Actions")
                if st.button("📥 Download", key=f"trend_{project['repo'].replace('/', '_')}"):
                    download_url = f"https://github.com/{project['repo']}/archive/refs/heads/main.zip"
                    st.success(f"[Download ZIP]({download_url})")
                
                if st.button("🔗 GitHub", key=f"trend_gh_{project['repo'].replace('/', '_')}"):
                    st.markdown(f"[View Repository](https://github.com/{project['repo']})")
            
            st.markdown("---")

# Sidebar with utilities
with st.sidebar:
    st.markdown("### 🧭 Quick Navigation")
    
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("app.py")
    
    if st.button("🧠 AI Knowledge", use_container_width=True):
        st.switch_page("pages/page1.py")
    
    if st.button("🦙 Ollama Course", use_container_width=True):
        st.switch_page("pages/Ollama.py")
    
    st.markdown("---")
    
    st.markdown("### 🔧 Download Helper")
    st.markdown("""
    **How to use downloaded projects:**
    
    1. **Extract** the ZIP file
    2. **Read** the README.md file
    3. **Install** dependencies
    4. **Follow** setup instructions
    
    **Common commands:**
    ```bash
    # Python projects
    pip install -r requirements.txt
    
    # Node.js projects  
    npm install
    
    # Docker projects
    docker-compose up
    ```
    """)
    
    st.markdown("---")
    
    st.markdown("### 📊 Resource Stats")
    st.metric("AI Agent Projects", "50+")
    st.metric("LLM Tools", "25+")
    st.metric("Learning Resources", "100+")
    st.metric("Total Downloads", "1000+")

# Footer
st.markdown("---")
st.markdown("### 💡 Pro Tips for Using GitHub Resources")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **🔍 Before Downloading:**
    - Check the README file
    - Review system requirements
    - Look at recent commits
    - Check issue tracker
    """)

with col2:
    st.markdown("""
    **⚙️ After Downloading:**
    - Create virtual environment
    - Install dependencies carefully
    - Follow setup instructions
    - Test with sample data
    """)

with col3:
    st.markdown("""
    **🤝 Contributing Back:**
    - Report bugs you find
    - Suggest improvements
    - Share your modifications
    - Star useful repositories
    """)


