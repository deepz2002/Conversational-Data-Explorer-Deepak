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


### Quick Analytics
- "Who are the top 10 customers by total sales?"
- "What are the top 5 products by profit?"
- "Plot sales trends over time by order date"
- "Create a bar chart showing total sales by region"
- "Show me a bar chart of revenue by product category"
- "Plot profit margins by customer segment"
- "Create a scatter plot of shipping cost versus sales amount"

### Screenshots
![alt text](<Screenshot 2025-09-10 at 7.12.44 PM.png>)
![alt text](<Screenshot 2025-09-10 at 7.41.10 PM.png>)

**Built with Agno Framework, FastAPI, and Streamlit**