import os
import sys
import psycopg2
import pandas as pd
from config import Config

def migrate_csv_to_postgres():
    config = Config()
    

    csv_path = config.excel_file
    if not os.path.exists(csv_path):
        # Fallback to parent dir search
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(os.path.dirname(base_dir), "spray_product_information.csv")
        
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        sys.exit(1)
        
    print(f"Reading products from {csv_path}...")
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    # Normalize data
    if 'Price' in df.columns:
        df['Price'] = pd.to_numeric(df['Price'].astype(str).str.replace('$', '').str.replace(',', ''), errors='coerce').fillna(0.0)
    if 'Cost/Dose' in df.columns:
        df['Cost/Dose'] = pd.to_numeric(df['Cost/Dose'].astype(str).str.replace('$', '').str.replace(',', ''), errors='coerce').fillna(0.0)

    for col in ['FRAC', 'omri', 'units', 'Primary Disease']:
        if col in df.columns:
            df[col] = df[col].astype(str).fillna('')

    if 'phi' in df.columns:
        df['phi'] = pd.to_numeric(df['phi'], errors='coerce').fillna(0).astype(int)
    if 'Max Applications' in df.columns:
        df['Max Applications'] = pd.to_numeric(df['Max Applications'], errors='coerce').fillna(999).astype(int)
    if 'Container Size' in df.columns:
        df['Container Size'] = pd.to_numeric(df['Container Size'], errors='coerce').fillna(0.0)
    if 'Dose (avg)' in df.columns:
        df['Dose (avg)'] = pd.to_numeric(df['Dose (avg)'], errors='coerce').fillna(0.0)

    disease_cols = ["Anthracnose", "Black Rot", "Bitter Rot", "Botrytis", "Downy", "Phomopsis", "Powdery"]
    for col in disease_cols:
        if col in df.columns:
            df[col] = df[col].fillna('na').astype(str).str.lower().str.strip()

    # Establish connection
    print(f"Connecting to PostgreSQL database '{config.db_name}' on {config.db_host}:{config.db_port}...")
    try:
        if config.database_url:
            conn = psycopg2.connect(config.database_url)
        else:
            conn = psycopg2.connect(
                host=config.db_host,
                port=config.db_port,
                database=config.db_name,
                user=config.db_user,
                password=config.db_password
            )
    except Exception as e:
        print(f"Failed to connect to PostgreSQL: {e}")
        sys.exit(1)
        
    cursor = conn.cursor()
    
    # Recreate the table
    print("Recreating 'products' table...")
    cursor.execute('DROP TABLE IF EXISTS products;')
    
    create_table_sql = """
    CREATE TABLE products (
        "Product" VARCHAR(255) PRIMARY KEY,
        "Primary Disease" VARCHAR(255),
        "FRAC" VARCHAR(255),
        "omri" VARCHAR(50),
        "phi" INTEGER,
        "Max Applications" INTEGER,
        "Container Size" DOUBLE PRECISION,
        "units" VARCHAR(50),
        "Price" DOUBLE PRECISION,
        "Dose (avg)" DOUBLE PRECISION,
        "Cost/Dose" DOUBLE PRECISION,
        "Anthracnose" VARCHAR(50),
        "Black Rot" VARCHAR(50),
        "Bitter Rot" VARCHAR(50),
        "Botrytis" VARCHAR(50),
        "Downy" VARCHAR(50),
        "Phomopsis" VARCHAR(50),
        "Powdery" VARCHAR(50),
        package_size NUMERIC(6,1),
        price_source TEXT,
        label_url TEXT,
        rei INTEGER,
        ppe_long_sleeves_pants BOOLEAN DEFAULT FALSE,
        ppe_socks_shoes BOOLEAN DEFAULT FALSE,
        ppe_waterproof_gloves BOOLEAN DEFAULT FALSE,
        ppe_protective_eyewear BOOLEAN DEFAULT FALSE,
        min_rate NUMERIC(4,1),
        max_rate NUMERIC(4,1)
    );
    """
    cursor.execute(create_table_sql)
    
    # Insert rows — new columns (package_size, price_source, etc.) default to None/False for CSV data
    csv_cols = [
        "Product", "Primary Disease", "FRAC", "omri", "phi",
        "Max Applications", "Container Size", "units", "Price",
        "Dose (avg)", "Cost/Dose", "Anthracnose", "Black Rot",
        "Bitter Rot", "Botrytis", "Downy", "Phomopsis", "Powdery"
    ]
    all_cols = csv_cols + [
        "package_size", "price_source", "label_url", "rei",
        "ppe_long_sleeves_pants", "ppe_socks_shoes",
        "ppe_waterproof_gloves", "ppe_protective_eyewear",
        "min_rate", "max_rate"
    ]

    columns_str = ", ".join([f'"{c}"' for c in all_cols])
    placeholders = ", ".join(["%s"] * len(all_cols))
    insert_sql = f'INSERT INTO products ({columns_str}) VALUES ({placeholders})'

    count = 0
    for _, row in df.iterrows():
        vals = []
        for col in csv_cols:
            val = row.get(col)
            if pd.isna(val):
                val = None
            vals.append(val)
        # Append defaults for new fields not present in CSV
        vals += [None, None, None, None, False, False, False, False, None, None]
        cursor.execute(insert_sql, vals)
        count += 1
        
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"Successfully migrated {count} products to PostgreSQL!")

if __name__ == "__main__":
    migrate_csv_to_postgres()
