import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import io
import json

# Configure Streamlit page
st.set_page_config(
    page_title="Conversational Data Explorer",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for better chat UI
st.markdown("""
<style>
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 1rem;
        border-radius: 10px;
        background-color: #f8f9fa;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 10px;
        border-radius: 15px;
        margin: 5px 0;
        max-width: 80%;
        float: right;
        clear: both;
    }
    .assistant-message {
        background-color: #e9ecef;
        color: #333;
        padding: 10px;
        border-radius: 15px;
        margin: 5px 0;
        max-width: 80%;
        float: left;
        clear: both;
    }
    .sample-question-btn {
        background-color: #6c757d;
        color: white;
        border: none;
        border-radius: 20px;
        padding: 8px 16px;
        margin: 4px;
        cursor: pointer;
        font-size: 14px;
    }
    .sample-question-btn:hover {
        background-color: #5a6268;
    }
    /* Keep sidebar toggle visible and prominent */
    .css-1d391kg {
        padding-left: 1rem;
    }
    [data-testid="collapsedControl"] {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        position: fixed !important;
        left: 0 !important;
        top: 50% !important;
        z-index: 999 !important;
        background-color: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 0 8px 8px 0 !important;
        padding: 8px 4px !important;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1) !important;
    }
    [data-testid="collapsedControl"]:hover {
        background-color: #f8f9fa !important;
        border-color: #007bff !important;
    }
    /* Ensure sidebar toggle button is always visible */
    .css-1rs6os {
        display: block !important;
    }
    /* Main content adjustment when sidebar is collapsed */
    .main .block-container {
        padding-left: 3rem !important;
    }
    /* Better text formatting for agent responses */
    .stChatMessage {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        line-height: 1.6;
    }
    .stChatMessage p {
        margin-bottom: 0.5rem;
        word-break: break-word;
    }
    /* Improve spacing for data values */
    .stChatMessage code {
        background-color: #f1f3f4;
        padding: 2px 4px;
        border-radius: 3px;
        font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
    }
</style>
""", unsafe_allow_html=True)

# Backend URL
BACKEND_URL = "http://127.0.0.1:8000"

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "data_uploaded" not in st.session_state:
    st.session_state.data_uploaded = False
if "selected_question" not in st.session_state:
    st.session_state.selected_question = ""

# Sample questions that generate charts
SAMPLE_QUESTIONS = [
    "Show me the top 5 categories by sales and plot it as a bar chart",
    "Plot revenue trends over time as a line chart", 
    "Create a scatter plot comparing price vs quantity sold"
]

def create_chart_from_table(table_data, chart_type="bar"):
    """Create a Plotly chart from table data"""
    df = pd.DataFrame(table_data)
    
    if len(df.columns) >= 2:
        x_col = df.columns[0]
        y_col = df.columns[1]
        
        if chart_type == "bar":
            fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
        elif chart_type == "line":
            fig = px.line(df, x=x_col, y=y_col, title=f"{y_col} over {x_col}")
        elif chart_type == "scatter":
            fig = px.scatter(df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")
        else:
            fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
        
        fig.update_layout(height=400)
        return fig
    return None

def send_message(message):
    """Send message to backend and handle response"""
    if not message.strip():
        return
        
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": message})
    
    # Process the message
    with st.spinner("🤖 Analyzing your data..."):
        try:
            response = requests.post(
                f"{BACKEND_URL}/chat",
                json={
                    "session_id": st.session_state.session_id,
                    "message": message
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Store complete response
                assistant_message = {
                    "role": "assistant", 
                    "content": result["reply"],
                    "tables": result.get("tables"),
                    "chart_data": result.get("chart_data"),
                    "description": result.get("description")
                }
                
                st.session_state.messages.append(assistant_message)
                
            else:
                error_msg = f"❌ Error: {response.text}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                
        except Exception as e:
            error_msg = f"🔌 Connection error: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Title and header
st.title("📊 Conversational Data Explorer")
st.markdown("### Upload your data and start chatting! 🚀")

# Sidebar for file upload
with st.sidebar:
    st.header("📁 Upload Your Data")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        help="Upload your data file to start exploring"
    )
    
    if uploaded_file is not None and not st.session_state.data_uploaded:
        with st.spinner("📤 Uploading and processing file..."):
            try:
                # Prepare file for upload
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                data = {"name": "dataset"}
                
                # Upload to backend
                response = requests.post(f"{BACKEND_URL}/upload", files=files, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.session_id = result["session_id"]
                    st.session_state.data_uploaded = True
                    
                    # Store dataset info for sidebar display
                    st.session_state.dataset_rows = result["rows"]
                    st.session_state.dataset_cols = len(result["cols"])
                    st.session_state.dataset_columns = result["cols"]
                    st.session_state.dataset_schema = result.get("schema", {})
                    
                    st.success("✅ File uploaded successfully!")
                    
                    # Display file info in a nice format
                    st.markdown("#### 📋 Dataset Overview")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Rows", result["rows"])
                    with col2:
                        st.metric("Columns", len(result["cols"]))
                    
                    with st.expander("📊 Column Details"):
                        for col in result["cols"][:15]:  # Show first 15 columns
                            st.text(f"• {col}")
                        if len(result["cols"]) > 15:
                            st.text(f"... and {len(result['cols']) - 15} more columns")
                            
                else:
                    st.error(f"❌ Upload failed: {response.text}")
                    
            except Exception as e:
                st.error(f"❌ Error uploading file: {str(e)}")
    
    if st.session_state.data_uploaded:
        st.success("🎉 Data is ready for analysis!")
        
        # Display current dataset info
        st.markdown("#### 📊 Current Dataset")
        try:
            # Get basic info about the current dataset
            response = requests.post(
                f"{BACKEND_URL}/chat",
                json={
                    "session_id": st.session_state.session_id,
                    "message": "describe the data structure briefly"
                }
            )
            
            if st.session_state.session_id in st.session_state:
                # Show dataset summary
                col1, col2 = st.columns(2)
                with col1:
                    if 'dataset_rows' in st.session_state:
                        st.metric("📊 Rows", st.session_state.get('dataset_rows', 'N/A'))
                with col2:
                    if 'dataset_cols' in st.session_state:
                        st.metric("📋 Columns", st.session_state.get('dataset_cols', 'N/A'))
                
                # Show column names if available
                if 'dataset_columns' in st.session_state:
                    with st.expander("📋 Column Names", expanded=False):
                        cols_list = st.session_state.get('dataset_columns', [])
                        for i, col in enumerate(cols_list[:20], 1):  # Show first 20
                            st.text(f"{i:2d}. {col}")
                        if len(cols_list) > 20:
                            st.text(f"... and {len(cols_list) - 20} more columns")
            
        except Exception as e:
            st.caption("Dataset loaded - ready for analysis")
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("#### ⚡ Quick Actions")
        if st.button("🔍 Analyze Data Structure", use_container_width=True):
            send_message("Describe the data structure and show me a summary")
            st.rerun()
            
        if st.button("📈 Show Data Insights", use_container_width=True):
            send_message("What are some interesting insights from this data?")
            st.rerun()
        
        if st.button("🔄 Reset Chat", use_container_width=True):
            # Reset session
            if st.session_state.session_id:
                requests.post(f"{BACKEND_URL}/reset", json={"session_id": st.session_state.session_id})
            st.session_state.messages = []
            st.rerun()
        
        # Session info
        st.markdown("---")
        st.caption(f"Session: {st.session_state.session_id[:8]}...")

# Main chat interface
if st.session_state.data_uploaded:
    
    # Chat messages container
    st.markdown("#### 💬 Conversation")
    
    # Create a container for chat messages with better styling
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.messages:
            # Welcome message
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown("""
                **Welcome! 👋** I'm your data analysis assistant. 
                
                I can help you:
                - 📊 Create charts and visualizations
                - 🔍 Find patterns and insights
                - 📈 Analyze trends over time
                - 🎯 Filter and explore your data
                
                Try one of the sample questions above or ask me anything about your data!
                """)
        
        # Display chat messages
        for i, message in enumerate(st.session_state.messages):
            avatar = "👤" if message["role"] == "user" else "🤖"
            
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])
                
                # Display tables if present
                if "tables" in message and message["tables"]:
                    for j, table in enumerate(message["tables"]):
                        df = pd.DataFrame(table)
                        
                        # Show table with better formatting
                        st.markdown("**📋 Data Results:**")
                        st.dataframe(df, use_container_width=True, height=200)
                        
                        # Chart generation buttons
                        st.markdown("**Create visualizations:**")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button(f"📊 Bar Chart", key=f"bar_{i}_{j}", use_container_width=True):
                                fig = create_chart_from_table(table, "bar")
                                if fig:
                                    st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            if st.button(f"📈 Line Chart", key=f"line_{i}_{j}", use_container_width=True):
                                fig = create_chart_from_table(table, "line")
                                if fig:
                                    st.plotly_chart(fig, use_container_width=True)
                        
                        with col3:
                            if st.button(f"🎯 Scatter Plot", key=f"scatter_{i}_{j}", use_container_width=True):
                                fig = create_chart_from_table(table, "scatter")
                                if fig:
                                    st.plotly_chart(fig, use_container_width=True)
                
                # Display insights/description if available
                if "description" in message and message["description"]:
                    st.info(f"💡 **Insight:** {message['description']}")
                
                # Display charts directly from chart_data
                if "chart_data" in message and message["chart_data"]:
                    st.markdown("**📊 Generated Visualization:**")
                    chart_info = message["chart_data"]
                    
                    if "data" in chart_info and chart_info["data"]:
                        df_chart = pd.DataFrame(chart_info["data"])
                        
                        if len(df_chart.columns) >= 2:
                            x_col = chart_info.get("x", df_chart.columns[0])
                            y_col = chart_info.get("y", df_chart.columns[1])
                            chart_type = chart_info.get("kind", "bar")
                            
                            if chart_type == "bar":
                                fig = px.bar(df_chart, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
                            elif chart_type == "line":
                                fig = px.line(df_chart, x=x_col, y=y_col, title=f"{y_col} over {x_col}")
                            elif chart_type == "area":
                                fig = px.area(df_chart, x=x_col, y=y_col, title=f"{y_col} over {x_col}")
                            else:
                                fig = px.bar(df_chart, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
                            
                            fig.update_layout(height=400)
                            st.plotly_chart(fig, use_container_width=True)
    
    # Chat input at the bottom
    if prompt := st.chat_input("💬 Ask me anything about your data...", key="chat_input"):
        send_message(prompt)
        st.rerun()

else:
    # Welcome screen when no data is uploaded
    st.markdown("""
    <div style='text-align: center; padding: 2rem; background-color: #f8f9fa; border-radius: 10px; margin: 2rem 0;'>
        <h2>🚀 Get Started</h2>
        <p>Upload your CSV or Excel file from the sidebar to begin exploring your data with AI!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature showcase
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📊 Smart Analytics**
        - Automatic chart generation
        - Top-K analysis
        - Trend identification
        """)
    
    with col2:
        st.markdown("""
        **🤖 Natural Language**
        - Ask questions in plain English
        - Multi-turn conversations
        - Context awareness
        """)
    
    with col3:
        st.markdown("""
        **🎯 Interactive Insights**
        - Real-time visualizations
        - Data filtering
        - Statistical summaries
        """)
    
    # Sample questions preview
    st.markdown("### 💡 Example Questions You Can Ask:")
    for i, question in enumerate(SAMPLE_QUESTIONS, 1):
        st.markdown(f"**{i}.** {question}")
    
    st.markdown("""
    ### More Examples:
    - "What are the top 10 customers by revenue?"
    - "Show me sales trends by month"
    - "Filter products where price > 100"
    - "Describe the data structure"
    - "Find correlations between columns"
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; margin-top: 2rem;'>"
    "Built with Agno Framework, FastAPI, and Streamlit"
    "</div>", 
    unsafe_allow_html=True
)
