# Conversational Data Explorer

A smart LLM-powered agent that enables natural language interactions with your CSV and Excel data. Upload your datasets and ask questions like "Show me top 5 customers by revenue" or "Plot sales trends over time" - the agent will automatically understand your data structure and provide intelligent analysis with visualizations.

## 🚀 Features

- **Natural Language Queries**: Ask questions about your data in plain English
- **Smart Column Detection**: Automatically identifies relevant columns for your queries
- **Multi-turn Conversations**: Maintains context across multiple interactions
- **Visual Analytics**: Generates interactive charts and plots
- **Intelligent Fallbacks**: Provides helpful suggestions when queries are ambiguous
- **Session Memory**: Remembers preferences and data context throughout conversations
- **Multiple File Formats**: Supports CSV and Excel files

## 📋 Setup Instructions

### Prerequisites

- Python 3.8+
- Google API Key for Gemini

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd conversational-data-explorer
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Google API key:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   GEMINI_MODEL_ID=gemini-2.0-flash-001
   ALLOWED_ORIGINS=*
   ```

5. **Run the application**

   **Option 1: Single Command (Recommended)**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```
   This will start both the FastAPI backend and Streamlit frontend automatically.

   **Option 2: Manual (Two Terminals)**
   ```bash
   # Terminal 1: Start FastAPI backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Terminal 2: Start Streamlit frontend
   streamlit run streamlit_app.py
   ```

6. **Access the application**
   - Open your browser to `http://localhost:8501`
   - Backend API runs on `http://localhost:8000`

## 🎯 Usage Examples

### Business Intelligence
- "What's our monthly recurring revenue trend?"
- "Which sales regions are underperforming?"
- "Show customer churn analysis by segment"

### Data Science
- "Plot correlation between price and sales volume"
- "Identify outliers in the revenue data"
- "Show distribution of customer purchase amounts"

### Quick Analytics
- "Top 10 products by profit margin"
- "Filter customers from New York with sales > $50K"
- "Compare Q3 vs Q4 performance"

## 🛠️ Available Tools

| Tool | Purpose | Example Usage |
|------|---------|---------------|
| **Smart Explore** | Automatically maps data structure | Identifies customer, sales, date columns |
| **Top K Analysis** | Finds top performers by metrics | "Top 10 products by revenue" |
| **Filtering** | Applies data filters | "Show sales where revenue > 1000" |
| **Plotting** | Creates visualizations | "Plot sales trends", "Bar chart of categories" |
| **Data Description** | Statistical summaries | "Describe the sales data" |
| **Suggestion Engine** | Recommends analysis options | When queries are ambiguous |

## 💡 Sample Interactions

### Basic Data Exploration
```
User: "Upload sales_data.csv and describe the data"
Agent: "I've loaded your dataset with 1,250 rows and 8 columns. The data contains:
        - Customer information (customer_name, region)
        - Sales metrics (total_revenue, units_sold)
        - Time data (order_date)
        - Product details (product_category, price_per_unit)"
```

### Smart Analysis
```
User: "Show me top 5 customers by sales"
Agent: [Automatically detects customer_name and total_revenue columns]
        "Here are the top 5 customers by total revenue:
        
        | Customer Name    | Total Revenue |
        |------------------|---------------|
        | TechCorp Inc     | $125,430     |
        | Global Solutions | $98,750      |
        | ... "
        
        [Generates bar chart visualization]
```

### Trend Analysis
```
User: "Plot revenue trends over time"
Agent: [Detects order_date and total_revenue, creates time series]
        "Here's the revenue trend analysis showing monthly patterns:
        
        [Interactive line chart showing revenue over time]
        
        Key insights: Revenue shows seasonal patterns with peaks in Q4..."
```

### Intelligent Clarification
```
User: "Show me something interesting"
Agent: "Based on your data, I can show you several interesting analyses:
        1. Revenue trends by region over time
        2. Top performing product categories
        3. Customer purchase patterns and seasonality
        
        Which would you like to explore first?"
```

## 🔧 Technical Stack

- **Agent Framework**: Agno (equivalent to LangGraph)
- **LLM**: Google Gemini 2.0 Flash
- **Backend**: FastAPI with async support
- **Frontend**: Streamlit with real-time chat
- **Visualization**: Plotly with interactive charts
- **Data Processing**: Pandas with smart type inference

## 🔍 Troubleshooting

### Common Issues
1. **File Upload Fails**: Ensure CSV has proper headers and encoding (UTF-8)
2. **Charts Not Displaying**: Check that Kaleido is installed (`pip install kaleido`)
3. **API Errors**: Verify Google API key is set correctly in `.env`
4. **Backend Connection Issues**: Ensure FastAPI is running on port 8000

### Debug Mode
Set environment variable `DEBUG=1` for detailed logging and error traces.

---

**Built with Agno Framework, FastAPI, and Streamlit**