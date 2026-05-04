import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Patent Intelligence Dashboard", layout="wide")

st.title("Global Patent Intelligence Dashboard")
st.markdown("A simple data pipeline dashboard analyzing synthetic real-world patent data.")

# Connect to database
@st.cache_data
def load_data():
    conn = sqlite3.connect("patents.db")
    
    # Q1: Top Inventors
    df_inventors = pd.read_sql_query("""
    SELECT i.name, COUNT(r.patent_id) as total_patents
    FROM inventors i
    JOIN relationships r ON i.inventor_id = r.inventor_id
    GROUP BY i.inventor_id, i.name
    ORDER BY total_patents DESC
    LIMIT 10;
    """, conn)
    
    # Q2: Top Companies
    df_companies = pd.read_sql_query("""
    SELECT c.name, COUNT(r.patent_id) as total_patents
    FROM companies c
    JOIN relationships r ON c.company_id = r.company_id
    GROUP BY c.company_id, c.name
    ORDER BY total_patents DESC
    LIMIT 10;
    """, conn)
    
    # Q4: Trends
    df_trends = pd.read_sql_query("""
    SELECT year, COUNT(patent_id) as total_patents
    FROM patents
    WHERE year IS NOT NULL
    GROUP BY year
    ORDER BY year;
    """, conn)
    
    # Q8: Advanced Analysis - Categories
    df_categories = pd.read_sql_query("""
    SELECT classification, COUNT(patent_id) as total_patents
    FROM patents
    WHERE classification IS NOT NULL
    GROUP BY classification
    ORDER BY total_patents DESC
    LIMIT 10;
    """, conn)
    
    conn.close()
    return df_inventors, df_companies, df_trends, df_categories

try:
    df_inventors, df_companies, df_trends, df_categories = load_data()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 10 Inventors")
        st.bar_chart(df_inventors.set_index("name"))
        
    with col2:
        st.subheader("Top 10 Companies")
        st.bar_chart(df_companies.set_index("name"))
        
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Patent Filings Over Time")
        st.line_chart(df_trends.set_index("year"))
        
    with col4:
        st.subheader("Top Patent Categories")
        st.bar_chart(df_categories.set_index("classification"))
    
    
except sqlite3.OperationalError:
    st.error("Database not found! Please run the data pipeline scripts first.")
    st.code("python scripts/1_extract_data.py\npython scripts/2_clean_data.py\npython scripts/3_load_to_sql.py\npython scripts/4_analyze_and_report.py")
