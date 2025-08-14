import pandas as pd
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load .env if exists
load_dotenv()

# ------------------ MongoDB Connection ------------------
MONGO_URI = os.getenv("MONGO_URI") or "your_fallback_uri_here"
DB_NAME = os.getenv("DB_NAME") or "test_db"
COLLECTION_NAME = os.getenv("COLLECTION_NAME") or "test_collection"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# ------------------ Extract ------------------
def extract():
    file_path = os.path.join("raw_data", "verified_online.csv")
    print(f"Loading data from {file_path}...")
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} records.")
    return df

# ------------------ Transform ------------------
def transform(df):
    print("Transforming data...")
    # Example transformation: drop empty rows
    df = df.dropna()
    # Convert dataframe to dictionary
    records = df.to_dict(orient='records')
    print(f"Transformed {len(records)} records.")
    return records

# ------------------ Load ------------------
def load(records):
    if records:
        result = collection.insert_many(records)
        print(f"Inserted {len(result.inserted_ids)} records into MongoDB.")
    else:
        print("No records to insert.")

# ------------------ Main ETL ------------------
if __name__ == "__main__":
    df = extract()
    records = transform(df)
    load(records)
