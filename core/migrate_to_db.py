import sqlite3
import pandas as pd
import os

def migrate_csv_to_sqlite(csv_path, db_path):
    # Load the CSV
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    # Normalize data for SQL (handling $, commas, and types)
    # Price
    if 'Price' in df.columns:
        df['Price'] = pd.to_numeric(df['Price'].astype(str).str.replace('$', '').str.replace(',', ''), errors='coerce').fillna(0.0)
    
    # Cost/Dose
    if 'Cost/Dose' in df.columns:
        df['Cost/Dose'] = pd.to_numeric(df['Cost/Dose'].astype(str).str.replace('$', '').str.replace(',', ''), errors='coerce').fillna(0.0)

    # FRAC, omri, units as strings
    for col in ['FRAC', 'omri', 'units', 'Primary Disease']:
        if col in df.columns:
            df[col] = df[col].astype(str).fillna('')

    # phi, Max Applications, Container Size, Dose (avg) as floats/ints
    if 'phi' in df.columns:
        df['phi'] = pd.to_numeric(df['phi'], errors='coerce').fillna(0).astype(int)
    if 'Max Applications' in df.columns:
        df['Max Applications'] = pd.to_numeric(df['Max Applications'], errors='coerce').fillna(999).astype(int)
    if 'Container Size' in df.columns:
        df['Container Size'] = pd.to_numeric(df['Container Size'], errors='coerce').fillna(0.0)
    if 'Dose (avg)' in df.columns:
        df['Dose (avg)'] = pd.to_numeric(df['Dose (avg)'], errors='coerce').fillna(0.0)

    # Effectiveness columns
    disease_cols = ["Anthracnose", "Black Rot", "Bitter Rot", "Botrytis", "Downy", "Phomopsis", "Powdery"]
    for col in disease_cols:
        if col in df.columns:
            df[col] = df[col].fillna('na').astype(str).str.lower().str.strip()

    # Connect to SQLite
    conn = sqlite3.connect(db_path)
    
    # Write to table 'products'
    df.to_sql('products', conn, if_exists='replace', index=False)
    
    # Add a primary key by recreating the table if needed (to_sql doesn't support PKs well)
    # For now, this simple migration is enough for the demo.
    
    conn.close()
    print(f"Migrated {len(df)} products to {db_path}")

if __name__ == "__main__":
    csv_file = "SprayPlanner/spray_product_information.csv"
    sqlite_db = "SprayPlanner/core/database.db"
    migrate_csv_to_sqlite(csv_file, sqlite_db)
