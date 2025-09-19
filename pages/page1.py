import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="AI Knowledge Base", page_icon="🧠", layout="wide")

if not st.session_state.get("authenticated", False):
    st.warning("🔒 Please sign in to access the AI Knowledge Base.")
    st.stop()

# Header with logo
col1, col2 = st.columns([1, 6])
with col1:
    if st.file_exists("assets/logo.png"):
        st.image("assets/logo.png", width=80)
with col2:
    st.title("🧠 AI Knowledge Base")
    st.markdown("*Comprehensive guides and resources for artificial intelligence*")

st.markdown("---")

# Navigation tabs
tab1, tab2, tab3, tab4 = st.tabs(["📚 Fundamentals", "🤖 Machine Learning", "🔬 Advanced Topics", "📈 Trends & Research"])

with tab1:
    st.header("AI Fundamentals")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 What is Artificial Intelligence?")
        st.markdown("""
        Artificial Intelligence (AI) refers to the simulation of human intelligence in machines that are programmed to think and learn like humans. 
        
        **Key Concepts:**
        - **Machine Learning**: Algorithms that improve through experience
        - **Deep Learning**: Neural networks with multiple layers
        - **Natural Language Processing**: Understanding and generating human language
        - **Computer Vision**: Interpreting and analyzing visual information
        """)
        
        with st.expander("📖 Learn More About AI History"):
            st.markdown("""
            **Timeline of AI Development:**
            - **1950s**: Alan Turing proposes the Turing Test
            - **1956**: The term "Artificial Intelligence" is coined
            - **1980s**: Expert systems gain popularity
            - **1990s**: Machine learning algorithms advance
            - **2010s**: Deep learning revolution begins
            - **2020s**: Large language models emerge
            """)
    
    with col2:
        st.subheader("🛠️ AI Applications")
        st.markdown("""
        **Current Applications:**
        - Healthcare diagnostics and drug discovery
        - Autonomous vehicles and transportation
        - Financial fraud detection and trading
        - Content creation and recommendation systems
        - Virtual assistants and chatbots
        - Image and speech recognition
        """)
        
        st.info("💡 **Did you know?** AI is projected to contribute $15.7 trillion to the global economy by 2030.")

with tab2:
    st.header("Machine Learning Deep Dive")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Types of Machine Learning")
        
        st.markdown("**1. Supervised Learning**")
        st.markdown("- Uses labeled training data")
        st.markdown("- Examples: Classification, Regression")
        st.markdown("- Algorithms: Linear Regression, Random Forest, SVM")
        
        st.markdown("**2. Unsupervised Learning**")
        st.markdown("- Finds patterns in unlabeled data")
        st.markdown("- Examples: Clustering, Dimensionality Reduction")
        st.markdown("- Algorithms: K-Means, PCA, DBSCAN")
        
        st.markdown("**3. Reinforcement Learning**")
        st.markdown("- Learns through interaction and rewards")
        st.markdown("- Examples: Game playing, Robotics")
        st.markdown("- Algorithms: Q-Learning, Policy Gradient")
    
    with col2:
        st.subheader("🧮 Popular ML Frameworks")
        
        frameworks = {
            "TensorFlow": "Google's open-source ML platform",
            "PyTorch": "Facebook's dynamic neural network library",
            "Scikit-learn": "Simple and efficient ML tools for Python",
            "Keras": "High-level neural networks API",
            "XGBoost": "Optimized gradient boosting framework"
        }
        
        for framework, description in frameworks.items():
            with st.expander(f"🔧 {framework}"):
                st.markdown(f"**{description}**")
                st.markdown("Perfect for beginners and experts alike!")

with tab3:
    st.header("Advanced AI Topics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔮 Large Language Models (LLMs)")
        st.markdown("""
        **Understanding LLMs:**
        - Transformer architecture revolutionized NLP
        - Pre-trained on massive text datasets
        - Fine-tuned for specific tasks
        
        **Popular Models:**
        - GPT series (OpenAI)
        - BERT and variants (Google)
        - LLaMA (Meta)
        - Claude (Anthropic)
        """)
        
        st.subheader("🎨 Generative AI")
        st.markdown("""
        **Applications:**
        - Text generation and completion
        - Image synthesis and editing
        - Code generation and debugging
        - Music and art creation
        """)
    
    with col2:
        st.subheader("🤖 AI Agents & Automation")
        st.markdown("""
        **Agent Architectures:**
        - ReAct (Reasoning + Acting)
        - Multi-agent systems
        - Tool-using agents
        - Memory-augmented agents
        
        **Popular Frameworks:**
        - LangChain
        - CrewAI
        - AutoGen
        - Semantic Kernel
        """)
        
        st.success("🚀 **Next Step**: Explore our Ollama Course to learn about local AI deployment!")

with tab4:
    st.header("Latest Trends & Research")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Current Trends (2024-2025)")
        trends = [
            "🏠 Local AI deployment with Ollama",
            "🔗 Multi-modal AI systems",
            "🧠 Retrieval-Augmented Generation (RAG)",
            "🤝 AI agent collaboration",
            "⚡ Edge AI and optimization",
            "🛡️ AI safety and alignment"
        ]
        
        for trend in trends:
            st.markdown(f"- {trend}")
    
    with col2:
        st.subheader("🔬 Research Areas")
        st.markdown("""
        **Hot Research Topics:**
        - Constitutional AI and RLHF
        - Few-shot and zero-shot learning
        - Federated learning
        - Explainable AI (XAI)
        - Quantum machine learning
        - Neuromorphic computing
        """)

# Footer with quick actions
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🦙 Explore Ollama Course", use_container_width=True):
        st.switch_page("pages/Ollama.py")

with col2:
    if st.button("📦 Browse GitHub Resources", use_container_width=True):
        st.switch_page("pages/page3.py")

with col3:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("app.py")

# Sidebar with quick reference
with st.sidebar:
    st.markdown("### 📚 Quick Reference")
    st.markdown("""
    **AI Glossary:**
    - **AGI**: Artificial General Intelligence
    - **API**: Application Programming Interface
    - **CNN**: Convolutional Neural Network
    - **GPU**: Graphics Processing Unit
    - **NLP**: Natural Language Processing
    - **RNN**: Recurrent Neural Network
    """)
    
    st.markdown("### 🔗 Useful Links")
    st.markdown("""
    - [Papers With Code](https://paperswithcode.com/)
    - [Hugging Face](https://huggingface.co/)
    - [OpenAI Documentation](https://platform.openai.com/docs)
    - [Google AI](https://ai.google/)
    """)










