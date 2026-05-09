import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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
    
    # Qualitative Data
    df_qualitative = pd.read_sql_query("""
    SELECT title as Title, abstract as Abstract, classification as Classification, year as Year
    FROM patents
    ORDER BY year DESC
    LIMIT 100;
    """, conn)
    
    # Overall stats
    total_patents = pd.read_sql_query("SELECT COUNT(*) as cnt FROM patents", conn).iloc[0]['cnt']
    
    conn.close()
    return df_inventors, df_companies, df_trends, df_categories, df_qualitative, total_patents

try:
    df_inventors, df_companies, df_trends, df_categories, df_qualitative, total_patents = load_data()
    
    # --- Quantitative Metrics ---
    st.header("Quantitative Overview")
    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
    mcol1.metric("Total Patents", f"{total_patents:,}")
    mcol2.metric("Top Inventor", df_inventors.iloc[0]['name'] if not df_inventors.empty else "N/A")
    mcol3.metric("Top Company", df_companies.iloc[0]['name'] if not df_companies.empty else "N/A")
    mcol4.metric("Top Category", df_categories.iloc[0]['classification'] if not df_categories.empty else "N/A")
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 10 Inventors")
        st.bar_chart(df_inventors.set_index("name"))
        
    with col2:
        st.subheader("Top 10 Companies")
        st.bar_chart(df_companies.set_index("name"))
        
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Patent Filings & Projections")
        if not df_trends.empty:
            # Prepare historical data
            x_hist = df_trends['year'].values
            y_hist = df_trends['total_patents'].values
            
            # Fit linear model (degree 1)
            z = np.polyfit(x_hist, y_hist, 1)
            p = np.poly1d(z)
            
            # Create future years (next 5 years)
            last_year = int(x_hist[-1])
            x_future = np.arange(last_year + 1, last_year + 6)
            y_future = p(x_future)
            y_future = np.maximum(0, y_future) # Prevent negative predictions
            
            # Combine for plotting
            df_hist = pd.DataFrame({"Year": x_hist, "Historical": y_hist, "Projected": np.nan})
            df_proj = pd.DataFrame({"Year": x_future, "Historical": np.nan, "Projected": y_future})
            
            df_combined = pd.concat([df_hist, df_proj]).set_index("Year")
            
            st.line_chart(df_combined)
        else:
            st.info("Not enough data to show trends.")
        
    with col4:
        st.subheader("Top Patent Categories")
        st.bar_chart(df_categories.set_index("classification"))
    
    st.divider()
    
    # --- Qualitative Data ---
    st.header("Qualitative Analysis")
    st.markdown("Sample of recent patent titles and abstracts for qualitative review.")
    st.dataframe(df_qualitative, width="stretch", hide_index=True)
    
except sqlite3.OperationalError:
    st.error("Database not found! Please run the data pipeline scripts first.")
    st.code("python scripts/1_extract_data.py\npython scripts/2_clean_data.py\npython scripts/3_load_to_sql.py\npython scripts/4_analyze_and_report.py")
