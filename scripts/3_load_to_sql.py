import sqlite3
import pandas as pd
import os

def setup_database():
    print("Setting up SQLite database...")
    db_path = "patents.db"
    schema_path = os.path.join("sql", "schema.sql")
    clean_dir = os.path.join("data", "clean")
    
    # Connect to SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Read and execute schema.sql
    print(f"Executing schema from {schema_path}...")
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    cursor.executescript(schema_sql)
    conn.commit()
    
    # Load clean data
    patents_csv = os.path.join(clean_dir, "clean_patents.csv")
    inventors_csv = os.path.join(clean_dir, "clean_inventors.csv")
    companies_csv = os.path.join(clean_dir, "clean_companies.csv")
    relationships_csv = os.path.join(clean_dir, "clean_relationships.csv")
    
    print("Loading data into tables...")
    
    # Patents
    df_patents = pd.read_csv(patents_csv)
    df_patents.to_sql("patents", conn, if_exists="append", index=False)
    print(f"Inserted {len(df_patents)} records into 'patents' table.")
    
    # Inventors
    df_inventors = pd.read_csv(inventors_csv)
    df_inventors.to_sql("inventors", conn, if_exists="append", index=False)
    print(f"Inserted {len(df_inventors)} records into 'inventors' table.")
    
    # Companies
    df_companies = pd.read_csv(companies_csv)
    df_companies.to_sql("companies", conn, if_exists="append", index=False)
    print(f"Inserted {len(df_companies)} records into 'companies' table.")
    
    # Relationships
    df_rel = pd.read_csv(relationships_csv)
    df_rel[["patent_id", "inventor_id", "company_id"]].to_sql("relationships", conn, if_exists="append", index=False)
    print(f"Inserted {len(df_rel)} records into 'relationships' table.")
    
    conn.close()
    print(f"Database successfully populated: {db_path}")

if __name__ == "__main__":
    setup_database()
