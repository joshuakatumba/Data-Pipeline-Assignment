import pandas as pd
import json
import os

def clean_data():
    print("Loading raw patent data...")
    raw_path = os.path.join("data", "raw", "raw_patents.json")
    clean_dir = os.path.join("data", "clean")
    os.makedirs(clean_dir, exist_ok=True)
    
    with open(raw_path, 'r') as f:
        raw_data = json.load(f)
        
    print(f"Loaded {len(raw_data)} records. Cleaning and normalizing...")
    
    # Extract entities
    patents = []
    inventors = []
    companies = []
    relationships = []
    
    for record in raw_data:
        # Patent data
        # Extract year from filing_date
        year = record.get("filing_date", "").split("-")[0] if record.get("filing_date") else None
        
        patents.append({
            "patent_id": record.get("patent_id"),
            "title": record.get("title"),
            "abstract": record.get("abstract", "No abstract provided"), # Fill missing abstract
            "filing_date": record.get("filing_date"),
            "year": year
        })
        
        # Inventors
        for inv in record.get("inventors", []):
            inv_country = inv.get("country", "")
            if not inv_country:
                inv_country = "Unknown"
            
            inventors.append({
                "inventor_id": inv.get("inventor_id"),
                "name": inv.get("name"),
                "country": inv_country
            })
            
            # Link inventor to patent
            relationships.append({
                "patent_id": record.get("patent_id"),
                "inventor_id": inv.get("inventor_id"),
                "company_id": None
            })
            
        # Companies (Assignees)
        for comp in record.get("assignees", []):
            companies.append({
                "company_id": comp.get("company_id"),
                "name": comp.get("name")
            })
            
            # Link company to patent
            relationships.append({
                "patent_id": record.get("patent_id"),
                "inventor_id": None,
                "company_id": comp.get("company_id")
            })
            
    # Create DataFrames
    df_patents = pd.DataFrame(patents)
    df_inventors = pd.DataFrame(inventors).drop_duplicates(subset=["inventor_id"])
    df_companies = pd.DataFrame(companies).drop_duplicates(subset=["company_id"])
    df_relationships = pd.DataFrame(relationships)
    
    # Fix any remaining missing values
    df_patents['abstract'] = df_patents['abstract'].fillna("No abstract provided")
    
    # Export to CSV
    patents_csv = os.path.join(clean_dir, "clean_patents.csv")
    inventors_csv = os.path.join(clean_dir, "clean_inventors.csv")
    companies_csv = os.path.join(clean_dir, "clean_companies.csv")
    relationships_csv = os.path.join(clean_dir, "clean_relationships.csv")
    
    df_patents.to_csv(patents_csv, index=False)
    df_inventors.to_csv(inventors_csv, index=False)
    df_companies.to_csv(companies_csv, index=False)
    df_relationships.to_csv(relationships_csv, index=False)
    
    print(f"Exported {len(df_patents)} patents to {patents_csv}")
    print(f"Exported {len(df_inventors)} unique inventors to {inventors_csv}")
    print(f"Exported {len(df_companies)} unique companies to {companies_csv}")
    print(f"Exported {len(df_relationships)} relationship records to {relationships_csv}")

if __name__ == "__main__":
    clean_data()
