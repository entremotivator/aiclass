import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime
from auth_utils import require_auth
from styles import apply_custom_css, hide_streamlit_elements

st.set_page_config(page_title="Downloads", page_icon="📥", layout="wide")

# Apply custom styling
apply_custom_css()
hide_streamlit_elements()

# Require authentication
require_auth()

# Header
st.title("📥 Downloads Center")
st.markdown("*Access and download available JSON workflow files*")
st.markdown("---")

def get_local_json_files():
    """Get all JSON files from the project root directory"""
    project_root = Path(__file__).parent.parent
    json_files = []
    
    for json_file in project_root.glob("*.json"):
        if json_file.is_file():
            try:
                # Get file stats
                stat = json_file.stat()
                size = stat.st_size
                modified = datetime.fromtimestamp(stat.st_mtime)
                
                # Try to read and validate JSON
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                json_files.append({
                    'name': json_file.name,
                    'path': str(json_file),
                    'size': size,
                    'modified': modified,
                    'data': data,
                    'valid': True
                })
            except Exception as e:
                json_files.append({
                    'name': json_file.name,
                    'path': str(json_file),
                    'size': json_file.stat().st_size if json_file.exists() else 0,
                    'modified': datetime.fromtimestamp(json_file.stat().st_mtime) if json_file.exists() else None,
                    'data': None,
                    'valid': False,
                    'error': str(e)
                })
    
    return sorted(json_files, key=lambda x: x['name'])

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"

def analyze_workflow(data):
    """Analyze workflow JSON data"""
    if not data or not isinstance(data, dict):
        return None
    
    nodes = data.get('nodes', [])
    connections = data.get('connections', {})
    
    analysis = {
        'node_count': len(nodes),
        'connection_count': len(connections),
        'node_types': list(set(node.get('type', 'Unknown') for node in nodes)),
        'active': data.get('active', False),
        'name': data.get('name', 'Unnamed Workflow'),
        'has_webhook': any(node.get('type') == 'n8n-nodes-base.webhook' for node in nodes),
        'has_trigger': any('trigger' in node.get('type', '').lower() for node in nodes)
    }
    
    return analysis

# Main content
st.subheader("📁 Available JSON Files")

# Get local JSON files
json_files = get_local_json_files()

if not json_files:
    st.info("📂 No JSON files found in the project directory.")
else:
    # Summary metrics
    valid_files = [f for f in json_files if f['valid']]
    total_size = sum(f['size'] for f in json_files)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Files", len(json_files))
    with col2:
        st.metric("Valid JSON", len(valid_files))
    with col3:
        st.metric("Total Size", format_file_size(total_size))
    with col4:
        st.metric("Invalid Files", len(json_files) - len(valid_files))
    
    st.markdown("---")
    
    # File listing
    for i, file_info in enumerate(json_files):
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # File header
                if file_info['valid']:
                    st.markdown(f"### ✅ {file_info['name']}")
                    
                    # Analyze workflow if it's valid JSON
                    analysis = analyze_workflow(file_info['data'])
                    if analysis:
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.write(f"**Workflow:** {analysis['name']}")
                            st.write(f"**Status:** {'🟢 Active' if analysis['active'] else '🔴 Inactive'}")
                        with col_b:
                            st.write(f"**Nodes:** {analysis['node_count']}")
                            st.write(f"**Connections:** {analysis['connection_count']}")
                        with col_c:
                            st.write(f"**Has Trigger:** {'✅' if analysis['has_trigger'] else '❌'}")
                            st.write(f"**Has Webhook:** {'✅' if analysis['has_webhook'] else '❌'}")
                        
                        # Node types
                        if analysis['node_types']:
                            with st.expander("🔧 Node Types Used"):
                                for node_type in sorted(analysis['node_types']):
                                    st.write(f"• {node_type}")
                else:
                    st.markdown(f"### ❌ {file_info['name']}")
                    st.error(f"Invalid JSON file: {file_info.get('error', 'Unknown error')}")
                
                # File metadata
                st.caption(f"📅 Modified: {file_info['modified'].strftime('%Y-%m-%d %H:%M:%S') if file_info['modified'] else 'Unknown'} | 📦 Size: {format_file_size(file_info['size'])}")
            
            with col2:
                # Download button
                if file_info['valid']:
                    # Read file content for download
                    try:
                        with open(file_info['path'], 'r', encoding='utf-8') as f:
                            file_content = f.read()
                        
                        st.download_button(
                            label="⬇️ Download",
                            data=file_content,
                            file_name=file_info['name'],
                            mime="application/json",
                            key=f"download_{file_info['name']}_{i}",
                            use_container_width=True
                        )
                        
                        # Pretty print button
                        if st.button("👁️ Preview", key=f"preview_{file_info['name']}_{i}", use_container_width=True):
                            st.session_state[f"show_preview_{file_info['name']}"] = not st.session_state.get(f"show_preview_{file_info['name']}", False)
                        
                    except Exception as e:
                        st.error(f"Error reading file: {str(e)}")
                else:
                    st.write("❌ Cannot download invalid file")
                
                # Show file preview if requested
                if st.session_state.get(f"show_preview_{file_info['name']}", False) and file_info['valid']:
                    with st.expander("📄 JSON Preview", expanded=True):
                        st.json(file_info['data'])
            
            st.divider()

# Additional features
st.markdown("---")
st.subheader("🛠️ Additional Tools")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 📋 How to Use
    1. **Browse** available JSON workflow files above
    2. **Preview** files to see their structure and content
    3. **Download** files by clicking the download button
    4. **Import** downloaded files into your n8n instance
    """)

with col2:
    st.markdown("""
    ### ℹ️ File Information
    - **Valid JSON**: Files that can be parsed successfully
    - **Node Count**: Number of workflow nodes
    - **Active Status**: Whether the workflow is currently active
    - **Triggers**: Workflow entry points (webhooks, schedules, etc.)
    """)

# Footer
st.markdown("---")
st.markdown("*💡 **Tip:** These JSON files contain n8n workflow configurations that can be imported directly into your n8n instance.*")

