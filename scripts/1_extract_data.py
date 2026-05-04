import requests
import json
import random
import os
from datetime import datetime, timedelta

def fetch_real_patent_data(num_records=1500):
    """
    Attempts to fetch real patent data from an API.
    Falls back to generating realistic mock data if the API is unavailable.
    """
    # Using PatentsView API endpoint for demonstration
    url = 'https://api.patentsview.org/patents/query'
    query = '{"_gte":{"patent_date":"2023-01-01"}}'
    fields = '["patent_id","patent_title","patent_abstract","patent_date","inventor_id","inventor_name_first","inventor_name_last","inventor_country","assignee_id","assignee_organization", "cpc_category_id"]'
    
    print(f"Attempting to fetch real data from PatentsView API: {url}")
    try:
        response = requests.get(f"{url}?q={query}&f={fields}", timeout=10)
        response.raise_for_status()
        data = response.json()
        patents = data.get("patents", [])
        if patents:
            print(f"Successfully fetched {len(patents)} records from API.")
            return patents
    except Exception as e:
        print(f"API fetch failed or timed out: {e}")
        print("Falling back to generating realistic synthetic data to ensure pipeline continuity...")

    return generate_synthetic_patents(num_records)

def generate_synthetic_patents(num_records=1000):
    print(f"Generating {num_records} synthetic patent records...")
    
    # Pre-defined data pools for realistic generation
    tech_keywords = ["Quantum", "Neural", "AI", "Blockchain", "Cloud", "Nano", "Cyber", "Autonomous", "Robotic", "Bio"]
    noun_keywords = ["Network", "Algorithm", "Device", "System", "Processor", "Interface", "Sensor", "Vehicle", "Fabric"]
    
    first_names = ["John", "Alice", "Robert", "Emma", "Michael", "Sarah", "David", "Jessica", "James", "Lily"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    countries = ["USA", "China", "Germany", "Japan", "South Korea", "UK", "France", "Canada"]
    companies = ["IBM", "Samsung", "Google", "Microsoft", "Apple", "Intel", "Sony", "Toyota", "Amazon", "LG"]
    
    # Adding classifications for advanced analysis
    classifications = ["G06F", "H04L", "A61B", "B60R", "C12N", "Y02E", "G01N", "H01L"]
    
    patents = []
    
    for i in range(1, num_records + 1):
        patent_id = f"US{random.randint(10000000, 99999999)}B2"
        title = f"{random.choice(tech_keywords)} {random.choice(noun_keywords)} for Advanced Computing"
        abstract = f"A {title.lower()} that provides enhanced performance and efficiency in modern applications."
        
        # Filing dates between 2000 and 2024
        start_date = datetime(2000, 1, 1)
        end_date = datetime(2024, 1, 1)
        random_days = random.randint(0, (end_date - start_date).days)
        filing_date = start_date + timedelta(days=random_days)
        
        # 1 to 3 inventors per patent
        inventors = []
        for _ in range(random.randint(1, 3)):
            inventors.append({
                "inventor_id": f"INV{random.randint(1000, 9999)}",
                "name": f"{random.choice(first_names)} {random.choice(last_names)}",
                "country": random.choice(countries)
            })
            
        # 1 or 2 companies per patent
        assignees = []
        for _ in range(random.randint(1, 2)):
            assignees.append({
                "company_id": f"COMP{random.randint(100, 999)}",
                "name": random.choice(companies)
            })
            
        patent_record = {
            "patent_id": patent_id,
            "title": title,
            "abstract": abstract,
            "filing_date": filing_date.strftime("%Y-%m-%d"),
            "classification": random.choice(classifications),
            "inventors": inventors,
            "assignees": assignees
        }
        
        # Introduce some missing values randomly to test the pandas cleaning script
        if random.random() < 0.05:
            patent_record["abstract"] = None
        if random.random() < 0.05:
            inventors[0]["country"] = ""
            
        patents.append(patent_record)

    return patents

if __name__ == "__main__":
    output_dir = os.path.join("data", "raw")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "raw_patents.json")
    
    patents_data = fetch_real_patent_data(1500)
    
    with open(output_path, "w") as f:
        json.dump(patents_data, f, indent=4)
        
    print(f"Successfully exported {len(patents_data)} patent records to {output_path}")
