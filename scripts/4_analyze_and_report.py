import sqlite3
import pandas as pd
import json
import os

def generate_reports():
    print("Connecting to database and generating reports...")
    db_path = "patents.db"
    conn = sqlite3.connect(db_path)
    
    # Run queries and fetch DataFrames
    
    # Total Patents
    df_total = pd.read_sql_query("SELECT COUNT(*) as total FROM patents", conn)
    total_patents = int(df_total.iloc[0]['total'])
    
    # Q1: Top Inventors
    query_top_inventors = """
    SELECT i.name, COUNT(r.patent_id) as total_patents
    FROM inventors i
    JOIN relationships r ON i.inventor_id = r.inventor_id
    GROUP BY i.inventor_id, i.name
    ORDER BY total_patents DESC
    LIMIT 10;
    """
    df_top_inventors = pd.read_sql_query(query_top_inventors, conn)
    
    # Q2: Top Companies
    query_top_companies = """
    SELECT c.name, COUNT(r.patent_id) as total_patents
    FROM companies c
    JOIN relationships r ON c.company_id = r.company_id
    GROUP BY c.company_id, c.name
    ORDER BY total_patents DESC
    LIMIT 10;
    """
    df_top_companies = pd.read_sql_query(query_top_companies, conn)
    
    # Q3: Top Countries
    query_top_countries = """
    SELECT i.country, COUNT(DISTINCT r.patent_id) as total_patents
    FROM inventors i
    JOIN relationships r ON i.inventor_id = r.inventor_id
    GROUP BY i.country
    ORDER BY total_patents DESC
    """
    df_top_countries = pd.read_sql_query(query_top_countries, conn)
    
    # Q4: Trends Over Time
    query_trends = """
    SELECT year, COUNT(patent_id) as total_patents
    FROM patents
    WHERE year IS NOT NULL
    GROUP BY year
    ORDER BY year;
    """
    df_trends = pd.read_sql_query(query_trends, conn)
    
    # 1. Console Report
    print("\n================== PATENT REPORT ===================")
    print(f"Total Patents: {total_patents}")
    
    print("Top Inventors:")
    for idx, row in df_top_inventors.head(3).iterrows():
        print(f"{idx+1}. {row['name']} - {row['total_patents']}")
        
    print("Top Companies:")
    for idx, row in df_top_companies.head(3).iterrows():
        print(f"{idx+1}. {row['name']} - {row['total_patents']}")
        
    print("Top Countries:")
    for idx, row in df_top_countries.head(3).iterrows():
        print(f"{idx+1}. {row['country']}")
    print("====================================================\n")
    
    # 2. Export CSV Files
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    df_top_inventors.to_csv(os.path.join(reports_dir, "top_inventors.csv"), index=False)
    df_top_companies.to_csv(os.path.join(reports_dir, "top_companies.csv"), index=False)
    df_trends.to_csv(os.path.join(reports_dir, "country_trends.csv"), index=False)
    print("Exported CSV reports.")
    
    # 3. JSON Report
    json_report = {
        "total_patents": total_patents,
        "top_inventors": [
            {"name": row['name'], "patents": int(row['total_patents'])} 
            for _, row in df_top_inventors.head(5).iterrows()
        ],
        "top_companies": [
            {"name": row['name'], "patents": int(row['total_patents'])} 
            for _, row in df_top_companies.head(5).iterrows()
        ],
        "top_countries": [
            {
                "country": row['country'], 
                "share": round(int(row['total_patents']) / total_patents, 4) if total_patents > 0 else 0
            } 
            for _, row in df_top_countries.head(5).iterrows()
        ]
    }
    
    json_path = os.path.join(reports_dir, "report.json")
    with open(json_path, "w") as f:
        json.dump(json_report, f, indent=4)
    print(f"Exported JSON report to {json_path}.")
    
    conn.close()

if __name__ == "__main__":
    generate_reports()
