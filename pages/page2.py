import streamlit as st
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import concurrent.futures
from dataclasses import dataclass
from pathlib import Path
import re

st.set_page_config(page_title="AI Tools", page_icon="🛠️")

if not st.session_state.get("authenticated", False):
    st.warning("Please log in to access this page.")
    st.stop()

@dataclass
class WorkflowFile:
    """Data class to represent a workflow file"""
    name: str
    path: str
    size: int
    download_url: str
    sha: str
    
@dataclass
class WorkflowAnalysis:
    """Data class to represent workflow analysis"""
    name: str
    node_count: int
    connection_count: int
    has_trigger: bool
    node_types: List[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    tags: List[str]
    description: Optional[str]

class GitHubRepository:
    """Class to handle GitHub repository operations"""
    
    def __init__(self, owner: str, repo: str, branch: str = "main"):
        self.owner = owner
        self.repo = repo
        self.branch = branch
        self.api_base_url = f"https://api.github.com/repos/{owner}/{repo}"
        self.raw_base_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}"
    
    @st.cache_data(ttl=300)
    def get_all_json_files(_self, path: str = "") -> List[WorkflowFile]:
        """Recursively fetch all .json files from the repository"""
        json_files = []
        
        try:
            url = f"{_self.api_base_url}/contents/{path}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                items = response.json()
                
                for item in items:
                    if item['type'] == 'file' and item['name'].endswith('.json'):
                        json_files.append(WorkflowFile(
                            name=item['name'],
                            path=item['path'],
                            size=item['size'],
                            download_url=item['download_url'],
                            sha=item['sha']
                        ))
                    elif item['type'] == 'dir':
                        # Recursively get files from subdirectories
                        subdirectory_files = _self.get_all_json_files(item['path'])
                        json_files.extend(subdirectory_files)
            
            return sorted(json_files, key=lambda x: x.name.lower())
            
        except Exception as e:
            st.error(f"Error fetching files from GitHub: {str(e)}")
            return []
    
    @st.cache_data(ttl=600)
    def fetch_workflow_content(_self, file: WorkflowFile) -> Optional[Dict[str, Any]]:
        """Fetch workflow content from a file"""
        try:
            response = requests.get(file.download_url, timeout=15)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            st.error(f"Error fetching {file.name}: {str(e)}")
            return None

class WorkflowAnalyzer:
    """Class to analyze n8n workflow data"""
    
    @staticmethod
    def analyze_workflow(workflow_data: Dict[str, Any]) -> WorkflowAnalysis:
        """Analyze workflow data and extract insights"""
        nodes = workflow_data.get('nodes', [])
        connections = workflow_data.get('connections', {})
        
        # Basic counts
        node_count = len(nodes)
        connection_count = sum(len(conn) for conn in connections.values())
        
        # Node type analysis
        node_types = []
        has_trigger = False
        
        for node in nodes:
            node_type = node.get('type', 'unknown')
            if node_type not in node_types:
                node_types.append(node_type)
            
            # Check for triggers
            if any(trigger_word in node_type.lower() 
                  for trigger_word in ['trigger', 'webhook', 'cron', 'interval']):
                has_trigger = True
        
        # Extract metadata
        name = workflow_data.get('name', 'Unnamed Workflow')
        created_at = workflow_data.get('createdAt')
        updated_at = workflow_data.get('updatedAt')
        tags = workflow_data.get('tags', [])
        description = workflow_data.get('notes') or workflow_data.get('description')
        
        return WorkflowAnalysis(
            name=name,
            node_count=node_count,
            connection_count=connection_count,
            has_trigger=has_trigger,
            node_types=node_types,
            created_at=created_at,
            updated_at=updated_at,
            tags=tags,
            description=description
        )

class UIComponents:
    """Class containing reusable UI components"""
    
    @staticmethod
    def render_custom_css():
        """Render custom CSS styles"""
        st.markdown("""
        <style>
            .workflow-card {
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                padding: 20px;
                margin: 15px 0;
                background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
            }
            .workflow-card:hover {
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                transform: translateY(-2px);
            }
            .workflow-title {
                color: #1f77b4;
                font-weight: 600;
                font-size: 1.3em;
                margin-bottom: 10px;
            }
            .workflow-path {
                color: #666;
                font-size: 0.85em;
                font-family: monospace;
                background: #f1f1f1;
                padding: 2px 6px;
                border-radius: 4px;
            }
            .metric-container {
                background: #ffffff;
                border-radius: 8px;
                padding: 10px;
                text-align: center;
                border: 1px solid #e9ecef;
            }
            .status-badge {
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 0.8em;
                font-weight: 500;
            }
            .status-success { background: #d4edda; color: #155724; }
            .status-warning { background: #fff3cd; color: #856404; }
            .status-info { background: #d1ecf1; color: #0c5460; }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_workflow_card(file: WorkflowFile, analysis: Optional[WorkflowAnalysis], 
                           repo: GitHubRepository) -> None:
        """Render a workflow card with analysis and download options"""
        with st.container():
            st.markdown('<div class="workflow-card">', unsafe_allow_html=True)
            
            # Header
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f'<div class="workflow-title">📋 {file.name}</div>', 
                          unsafe_allow_html=True)
                st.markdown(f'<span class="workflow-path">{file.path}</span>', 
                          unsafe_allow_html=True)
            
            with col2:
                file_size_kb = file.size / 1024
                st.caption(f"Size: {file_size_kb:.1f} KB")
            
            if analysis:
                # Metrics row
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                    st.metric("Nodes", analysis.node_count)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                    st.metric("Connections", analysis.connection_count)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col3:
                    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                    trigger_status = "✅ Yes" if analysis.has_trigger else "❌ No"
                    st.metric("Has Trigger", trigger_status)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col4:
                    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                    st.metric("Node Types", len(analysis.node_types))
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Additional info
                if analysis.name and analysis.name != 'Unnamed Workflow':
                    st.write(f"**Workflow Name:** {analysis.name}")
                
                if analysis.description:
                    st.write(f"**Description:** {analysis.description[:200]}{'...' if len(analysis.description) > 200 else ''}")
                
                if analysis.node_types:
                    st.write(f"**Node Types:** {', '.join(analysis.node_types[:8])}{'...' if len(analysis.node_types) > 8 else ''}")
                
                if analysis.tags:
                    tag_badges = ' '.join([f'<span class="status-badge status-info">{tag}</span>' 
                                         for tag in analysis.tags[:5]])
                    st.markdown(f"**Tags:** {tag_badges}", unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def render_sidebar_filters() -> Dict[str, Any]:
        """Render sidebar filters and return filter values"""
        st.header("⚙️ Configuration")
        
        # Repository settings
        st.subheader("📁 Repository Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            owner = st.text_input("Repository Owner", value="entremotivator", help="GitHub username or organization")
        with col2:
            repo = st.text_input("Repository Name", value="Toolkitflow", help="Repository name")
        
        branch = st.text_input("Branch", value="main", help="Git branch to fetch from")
        
        # Display options
        st.subheader("📊 Display Options")
        show_analysis = st.checkbox("Show workflow analysis", value=True)
        items_per_page = st.slider("Items per page", 5, 50, 15)
        
        # Filters
        st.subheader("🔍 Filters")
        search_term = st.text_input("Search workflows", placeholder="Enter filename, workflow name, or node type...")
        
        col1, col2 = st.columns(2)
        with col1:
            min_nodes = st.slider("Min nodes", 0, 100, 0)
        with col2:
            max_nodes = st.slider("Max nodes", 0, 500, 500)
        
        folder_filter = st.text_input("Folder path filter", placeholder="e.g., workflows/automation", help="Filter by folder path")
        
        # Node type filter
        node_type_filter = st.text_input("Node type contains", placeholder="e.g., webhook, http", help="Filter by node types")
        
        return {
            'owner': owner,
            'repo': repo,
            'branch': branch,
            'show_analysis': show_analysis,
            'items_per_page': items_per_page,
            'search_term': search_term.lower() if search_term else '',
            'min_nodes': min_nodes,
            'max_nodes': max_nodes,
            'folder_filter': folder_filter.lower() if folder_filter else '',
            'node_type_filter': node_type_filter.lower() if node_type_filter else ''
        }

class WorkflowManager:
    """Main class to manage the workflow application"""
    
    def __init__(self):
        self.ui = UIComponents()
        self.analyzer = WorkflowAnalyzer()
        
        # Initialize session state
        if 'workflows_data' not in st.session_state:
            st.session_state.workflows_data = {}
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 0
        if 'loaded_analyses' not in st.session_state:
            st.session_state.loaded_analyses = {}
    
    def filter_workflows(self, files: List[WorkflowFile], filters: Dict[str, Any]) -> List[WorkflowFile]:
        """Filter workflows based on user criteria"""
        filtered = files
        
        # Search filter
        if filters['search_term']:
            filtered = [f for f in filtered if (
                filters['search_term'] in f.name.lower() or
                filters['search_term'] in f.path.lower() or
                (f.name in st.session_state.loaded_analyses and 
                 filters['search_term'] in st.session_state.loaded_analyses[f.name].name.lower())
            )]
        
        # Folder filter
        if filters['folder_filter']:
            filtered = [f for f in filtered if filters['folder_filter'] in f.path.lower()]
        
        # Node count and type filters (only for loaded workflows)
        if filters['min_nodes'] > 0 or filters['max_nodes'] < 500 or filters['node_type_filter']:
            filtered = [f for f in filtered if self._passes_analysis_filters(f, filters)]
        
        return filtered
    
    def _passes_analysis_filters(self, file: WorkflowFile, filters: Dict[str, Any]) -> bool:
        """Check if a workflow passes analysis-based filters"""
        if file.name not in st.session_state.loaded_analyses:
            return True  # Don't filter out unloaded workflows
        
        analysis = st.session_state.loaded_analyses[file.name]
        
        # Node count filter
        if not (filters['min_nodes'] <= analysis.node_count <= filters['max_nodes']):
            return False
        
        # Node type filter
        if filters['node_type_filter']:
            node_types_str = ' '.join(analysis.node_types).lower()
            if filters['node_type_filter'] not in node_types_str:
                return False
        
        return True
    
    def load_workflows_batch(self, files: List[WorkflowFile], repo: GitHubRepository) -> None:
        """Load multiple workflows with progress tracking"""
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            future_to_file = {
                executor.submit(repo.fetch_workflow_content, file): file 
                for file in files
            }
            
            completed = 0
            successful = 0
            
            for future in concurrent.futures.as_completed(future_to_file):
                file = future_to_file[future]
                try:
                    data = future.result()
                    if data:
                        st.session_state.workflows_data[file.name] = data
                        st.session_state.loaded_analyses[file.name] = self.analyzer.analyze_workflow(data)
                        successful += 1
                except Exception as e:
                    st.error(f"Error loading {file.name}: {str(e)}")
                
                completed += 1
                progress_bar.progress(completed / len(files))
                status_text.text(f"Loaded {completed}/{len(files)} workflows ({successful} successful)")
        
        progress_bar.empty()
        status_text.empty()
        st.success(f"✅ Batch loading complete! {successful}/{len(files)} workflows loaded successfully.")
    
    def generate_comprehensive_report(self, files: List[WorkflowFile]) -> None:
        """Generate a comprehensive analysis report"""
        if not st.session_state.loaded_analyses:
            st.info("📥 Load some workflows first to generate a report.")
            return
        
        st.header("📊 Comprehensive Workflow Analysis Report")
        
        analyses = list(st.session_state.loaded_analyses.values())
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Workflows", len(analyses))
        with col2:
            total_nodes = sum(a.node_count for a in analyses)
            st.metric("Total Nodes", total_nodes)
        with col3:
            avg_nodes = total_nodes / len(analyses) if analyses else 0
            st.metric("Avg Nodes/Workflow", f"{avg_nodes:.1f}")
        with col4:
            workflows_with_triggers = sum(1 for a in analyses if a.has_trigger)
            st.metric("Workflows with Triggers", f"{workflows_with_triggers}/{len(analyses)}")
        
        # Distribution analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Node Count Distribution")
            node_counts = [a.node_count for a in analyses]
            if node_counts:
                st.write(f"• **Min nodes:** {min(node_counts)}")
                st.write(f"• **Max nodes:** {max(node_counts)}")
                st.write(f"• **Median nodes:** {sorted(node_counts)[len(node_counts)//2]}")
        
        with col2:
            st.subheader("🔧 Most Popular Node Types")
            all_node_types = {}
            for analysis in analyses:
                for node_type in analysis.node_types:
                    all_node_types[node_type] = all_node_types.get(node_type, 0) + 1
            
            if all_node_types:
                sorted_types = sorted(all_node_types.items(), key=lambda x: x[1], reverse=True)[:10]
                for i, (node_type, count) in enumerate(sorted_types, 1):
                    st.write(f"{i}. **{node_type}**: {count} workflows")
    
    def run(self):
        """Main application entry point"""
        # Render custom CSS
        self.ui.render_custom_css()
        
        # Title and description
        st.title("🔧 Toolkitflow – Advanced n8n Workflow Manager")
        st.markdown("*Discover, analyze, and download n8n workflows from any GitHub repository*")
        
        # Sidebar filters
        with st.sidebar:
            filters = self.ui.render_sidebar_filters()
        
        # Initialize repository
        repo = GitHubRepository(filters['owner'], filters['repo'], filters['branch'])
        
        # Control buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔍 Scan Repository", type="primary"):
                st.cache_data.clear()
                st.rerun()
        
        with col2:
            scan_and_load = st.button("📥 Scan & Load All")
        
        with col3:
            if st.button("🗑️ Clear Cache"):
                st.cache_data.clear()
                st.session_state.workflows_data = {}
                st.session_state.loaded_analyses = {}
                st.success("Cache cleared!")
        
        with col4:
            if st.button("📊 Generate Report"):
                st.session_state.show_report = True
        
        # Get all JSON files
        with st.spinner("🔍 Scanning repository for JSON files..."):
            files = repo.get_all_json_files()
        
        if not files:
            st.warning("⚠️ No JSON files found in the repository. Check your repository settings.")
            return
        
        st.success(f"📁 Found **{len(files)}** JSON files across all directories")
        
        # Show folder structure summary
        folders = {}
        for file in files:
            folder = str(Path(file.path).parent)
            if folder == '.':
                folder = 'Root'
            folders[folder] = folders.get(folder, 0) + 1
        
        if len(folders) > 1:
            st.expander_content = st.expander("📂 Directory Structure")
            with st.expander_content:
                for folder, count in sorted(folders.items()):
                    st.write(f"• **{folder}**: {count} files")
        
        # Scan and load all functionality
        if scan_and_load:
            self.load_workflows_batch(files, repo)
        
        # Apply filters
        filtered_files = self.filter_workflows(files, filters)
        
        if len(filtered_files) != len(files):
            st.info(f"🔍 Showing {len(filtered_files)} of {len(files)} files after applying filters")
        
        # Pagination
        total_pages = (len(filtered_files) - 1) // filters['items_per_page'] + 1 if filtered_files else 1
        
        if total_pages > 1:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.button("⬅️ Previous") and st.session_state.current_page > 0:
                    st.session_state.current_page -= 1
            with col2:
                st.markdown(f"<div style='text-align: center'>Page {st.session_state.current_page + 1} of {total_pages}</div>", unsafe_allow_html=True)
            with col3:
                if st.button("➡️ Next") and st.session_state.current_page < total_pages - 1:
                    st.session_state.current_page += 1
        
        # Display workflows
        if filtered_files:
            start_idx = st.session_state.current_page * filters['items_per_page']
            end_idx = min(start_idx + filters['items_per_page'], len(filtered_files))
            current_files = filtered_files[start_idx:end_idx]
            
            for file in current_files:
                # Load individual workflow if not loaded
                if file.name not in st.session_state.workflows_data:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.markdown(f"### 📋 {file.name}")
                        st.caption(f"Path: {file.path}")
                    
                    with col2:
                        if st.button(f"📥 Load", key=f"load_{file.sha}"):
                            with st.spinner(f"Loading {file.name}..."):
                                data = repo.fetch_workflow_content(file)
                                if data:
                                    st.session_state.workflows_data[file.name] = data
                                    st.session_state.loaded_analyses[file.name] = self.analyzer.analyze_workflow(data)
                                    st.rerun()
                    
                    with col3:
                        st.download_button(
                            label="⬇️ Download",
                            data=requests.get(file.download_url).text,
                            file_name=file.name,
                            mime="application/json",
                            key=f"download_{file.sha}"
                        )
                else:
                    # Display loaded workflow
                    analysis = st.session_state.loaded_analyses.get(file.name) if filters['show_analysis'] else None
                    self.ui.render_workflow_card(file, analysis, repo)
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        workflow_data = st.session_state.workflows_data[file.name]
                        st.download_button(
                            label="⬇️ Download JSON",
                            data=json.dumps(workflow_data, indent=2),
                            file_name=file.name,
                            mime="application/json",
                            key=f"download_loaded_{file.sha}"
                        )
                    
                    with col2:
                        if st.button("📋 Copy Raw URL", key=f"copy_{file.sha}"):
                            st.code(f"{repo.raw_base_url}/{file.path}")
                            st.info("✅ Raw URL displayed above")
                    
                    with col3:
                        if st.button("🗑️ Remove", key=f"remove_{file.sha}"):
                            if file.name in st.session_state.workflows_data:
                                del st.session_state.workflows_data[file.name]
                            if file.name in st.session_state.loaded_analyses:
                                del st.session_state.loaded_analyses[file.name]
                            st.rerun()
                
                st.divider()
        else:
            st.info("🔍 No workflows match your current filters. Try adjusting your search criteria.")
        
        # Generate report if requested
        if st.session_state.get('show_report', False):
            st.session_state.show_report = False
            self.generate_comprehensive_report(filtered_files)

# Application entry point
def main():
    """Main application entry point"""
    app = WorkflowManager()
    app.run()

if __name__ == "__main__":
    main()

