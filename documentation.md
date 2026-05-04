# Streamlit Dashboard Workflow Documentation (`app.py`)

This document outlines the workflow, architecture, and data flow of the `app.py` interactive dashboard used in the Global Patent Intelligence Data Pipeline.

## Overview
`app.py` is a Python script that leverages the **Streamlit** framework to create a real-time, interactive web dashboard. Its primary purpose is to visually render the analytical results derived from the `patents.db` SQLite database.

## Workflow & Data Execution Flow

### 1. Initialization and Page Setup
The script begins by importing necessary libraries: `streamlit`, `sqlite3`, `pandas`, and `matplotlib`.
```python
st.set_page_config(page_title="Patent Intelligence Dashboard", layout="wide")
```
It configures the Streamlit page to use a `wide` layout and sets the dashboard titles and markdown descriptions visible at the top of the UI.

### 2. Data Loading & Caching (`load_data` function)
Streamlit apps re-run from top to bottom on every user interaction. To prevent expensive database queries from running repeatedly, the script uses the `@st.cache_data` decorator. 

When `load_data()` is called, it performs the following steps:
1. **Database Connection:** Connects to the local `patents.db` SQLite database.
2. **SQL Execution via Pandas:** Executes four distinct SQL queries using `pd.read_sql_query`:
   - **Q1 (Top Inventors):** Joins `inventors` and `relationships` to find the individuals with the most patents.
   - **Q2 (Top Companies):** Joins `companies` and `relationships` to find top assignees.
   - **Q4 (Trends):** Groups patents by `year` to show filing volume over time.
   - **Q8 (Advanced Analysis):** Groups patents by `classification` to identify top technology categories.
3. **Return DataFrames:** The function closes the database connection and returns four distinct pandas DataFrames containing the aggregated data.

### 3. Rendering the UI Elements
The script utilizes a `try-except` block to catch `sqlite3.OperationalError`, which gracefully handles scenarios where the user runs the dashboard before generating the database.

Inside the `try` block, the layout is split into columns using `st.columns(2)` to create a grid-like dashboard:

#### Row 1: Top Entities
- **Column 1:** Renders a horizontal bar chart (`st.bar_chart`) showing the **Top 10 Inventors**, using the inventor's name as the index.
- **Column 2:** Renders a horizontal bar chart showing the **Top 10 Companies**.

#### Row 2: Trends and Categories
- **Column 3:** Renders a line chart (`st.line_chart`) to visualize **Patent Filings Over Time** (Trends).
- **Column 4:** Renders a bar chart to visualize the **Top Patent Categories** (Advanced Analysis).

### 4. Error Handling
If the database `patents.db` is missing or the schema is incorrect (triggering the `except` block), the dashboard catches the error and displays a helpful warning (`st.error`) along with a code block (`st.code`) instructing the user to run the four main pipeline scripts sequentially.

## How to Run
To execute the dashboard workflow locally, ensure your virtual environment is active and run:
```bash
streamlit run app.py
```
This will start a local server and automatically open the interactive web interface in your default web browser.
