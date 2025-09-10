Conversational Data Explorer
A smart LLM-powered agent that enables natural language interactions with your CSV and Excel data. Upload your datasets and ask questions like "Show me top 5 customers by revenue" or "Plot sales trends over time" - the agent will automatically understand your data structure and provide intelligent analysis with visualizations.
🚀 Features

Natural Language Queries: Ask questions about your data in plain English
Smart Column Detection: Automatically identifies relevant columns for your queries
Multi-turn Conversations: Maintains context across multiple interactions
Visual Analytics: Generates interactive charts and plots
Intelligent Fallbacks: Provides helpful suggestions when queries are ambiguous
Session Memory: Remembers preferences and data context throughout conversations
Multiple File Formats: Supports CSV and Excel files

🏗️ Architecture & Flow
System Components
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit     │    │    FastAPI       │    │   Agno Agent    │
│   Frontend      │◄──►│    Backend       │◄──►│   Framework     │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Chat Interface  │    │ Session Manager  │    │   LLM Tools     │
│ File Upload     │    │ Memory & State   │    │   Integration   │
│ Visualizations  │    │ Data Registry    │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
Request Processing Flow

Intent Detection → Analyzes user query to determine purpose (plot, filter, analyze, etc.)
Smart Data Exploration → Automatically maps data columns to semantic meanings
Tool Selection → Chooses appropriate tools based on intent and data structure
Tool Execution → Runs analysis, generates plots, or processes data
Response Generation → LLM synthesizes results into natural language with visuals

Memory Management

Session Memory: Maintains user preferences and conversation context
Data Registry: Stores uploaded datasets with schema information
Smart Columns: Remembers semantic mappings (e.g., "sales" → "total_revenue")

📋 Setup Instructions
Prerequisites

Python 3.8+
Google API Key for Gemini

Installation

Clone the repository
bashgit clone <your-repo-url>
cd conversational-data-explorer

Create virtual environment
bashpython -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

Install dependencies
bashpip install -r requirements.txt

Environment Configuration
bashcp .env.example .env
Edit .env and add your Google API key:
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL_ID=gemini-2.0-flash-001
ALLOWED_ORIGINS=*

Run the application
bash# Start the FastAPI backend
chmod +x run.sh
./run.sh

# In a separate terminal, start Streamlit frontend
streamlit run streamlit_app.py

Access the application

Open your browser to http://localhost:8501
Backend API runs on http://localhost:8000



🎯 Sample Interactions
Basic Data Exploration
User: "Upload sales_data.csv and describe the data"
Agent: "I've loaded your dataset with 1,250 rows and 8 columns. The data contains:
        - Customer information (customer_name, region)
        - Sales metrics (total_revenue, units_sold)
        - Time data (order_date)
        - Product details (product_category, price_per_unit)"
Smart Analysis
User: "Show me top 5 customers by sales"
Agent: [Automatically detects customer_name and total_revenue columns]
        "Here are the top 5 customers by total revenue:
        
        | Customer Name    | Total Revenue |
        |------------------|---------------|
        | TechCorp Inc     | $125,430     |
        | Global Solutions | $98,750      |
        | ... "
        
        [Generates bar chart visualization]
Trend Analysis
User: "Plot revenue trends over time"
Agent: [Detects order_date and total_revenue, creates time series]
        "Here's the revenue trend analysis showing monthly patterns:
        
        [Interactive line chart showing revenue over time]
        
        Key insights: Revenue shows seasonal patterns with peaks in Q4..."
Intelligent Clarification
User: "Show me something interesting"
Agent: "Based on your data, I can show you several interesting analyses:
        1. Revenue trends by region over time
        2. Top performing product categories
        3. Customer purchase patterns and seasonality
        
        Which would you like to explore first?"
🛠️ Available Tools
ToolPurposeExample UsageSmart ExploreAutomatically maps data structureIdentifies customer, sales, date columnsTop K AnalysisFinds top performers by metrics"Top 10 products by revenue"FilteringApplies data filters"Show sales where revenue > 1000"PlottingCreates visualizations"Plot sales trends", "Bar chart of categories"Data DescriptionStatistical summaries"Describe the sales data"Suggestion EngineRecommends analysis optionsWhen queries are ambiguous
🔧 Technical Details
Core Technologies

Agent Framework: Agno (equivalent to LangGraph)
LLM: Google Gemini 2.0 Flash
Backend: FastAPI with async support
Frontend: Streamlit with real-time chat
Visualization: Plotly with interactive charts
Data Processing: Pandas with smart type inference

Key Features

Dynamic Column Resolution: Matches user terms to actual column names
Schema-Agnostic: Works with any CSV/Excel structure
Error Recovery: Provides suggestions when queries fail
Memory Persistence: Maintains context across conversation turns
Visual Outputs: Automatic chart generation with multiple types

File Structure
app/
├── agent/
│   ├── agent.py          # Main Agno agent configuration
│   ├── tools.py          # Tool implementations
│   ├── memory.py         # Session memory management
│   ├── router.py         # Intent detection
│   └── llm.py           # Gemini LLM configuration
├── services/
│   ├── plotting.py       # Plotly visualization service
│   ├── data_registry.py  # Data storage and retrieval
│   └── utils.py         # Helper functions
└── main.py              # FastAPI application
🤝 Usage Examples
Business Intelligence

"What's our monthly recurring revenue trend?"
"Which sales regions are underperforming?"
"Show customer churn analysis by segment"

Data Science

"Plot correlation between price and sales volume"
"Identify outliers in the revenue data"
"Show distribution of customer purchase amounts"

Quick Analytics

"Top 10 products by profit margin"
"Filter customers from New York with sales > $50K"
"Compare Q3 vs Q4 performance"