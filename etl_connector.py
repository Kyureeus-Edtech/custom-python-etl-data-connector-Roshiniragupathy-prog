import pandas as pd
import os

# ------------------ Extract ------------------
def extract():
    file_path = os.path.join("raw_data", "verified_online.csv")  # your file name
    print(f"Loading data from {file_path}...")
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} total records.")
    return df

# ------------------ Transform ------------------
def transform(df):
    print("Transforming data...")
    # Keep only active phishing sites
    df_active = df[df['online'] == 'yes']
    print(f"Filtered to {len(df_active)} active phishing sites.")
    
    # Keep important columns
    df_active = df_active[['phish_id', 'phish_detail_url', 'submission_time', 'target']]
    
    # Sort by latest submission
    df_active = df_active.sort_values(by='submission_time', ascending=False)
    return df_active

# ------------------ Analysis ------------------
def analyze(df):
    print("\nTop 10 targeted brands/companies:")
    top_targets = df['target'].value_counts().head(10)
    print(top_targets)
    return top_targets

# ------------------ Load ------------------
def load(df):
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "phishtank_clean.csv")
    df.to_csv(output_path, index=False)
    print(f"Saved cleaned data to {output_path}")

def main():
    df = extract()
    df_clean = transform(df)
    analyze(df_clean)
    load(df_clean)

if __name__ == "__main__":
    main()
