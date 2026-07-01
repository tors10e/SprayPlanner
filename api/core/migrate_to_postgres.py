import os
import sys
import psycopg2
import pandas as pd
from config import Config

def migrate_csv_to_postgres():
    config = Config()
    
    # Check if database is configured for Postgres
    if config.db_type != "postgres":
        print("Error: DB_TYPE in configuration is not set to 'postgres'. Please set DB_TYPE=postgres.")
        sys.exit(1)
        
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
        "Powdery" VARCHAR(50)
    );
    """
    cursor.execute(create_table_sql)
    
    # Insert rows
    cols = [
        "Product", "Primary Disease", "FRAC", "omri", "phi", 
        "Max Applications", "Container Size", "units", "Price", 
        "Dose (avg)", "Cost/Dose", "Anthracnose", "Black Rot", 
        "Bitter Rot", "Botrytis", "Downy", "Phomopsis", "Powdery"
    ]
    
    columns_str = ", ".join([f'"{c}"' for c in cols])
    placeholders = ", ".join(["%s"] * len(cols))
    insert_sql = f'INSERT INTO products ({columns_str}) VALUES ({placeholders})'
    
    count = 0
    for _, row in df.iterrows():
        vals = []
        for col in cols:
            val = row.get(col)
            if pd.isna(val):
                val = None
            vals.append(val)
        cursor.execute(insert_sql, vals)
        count += 1
        
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"Successfully migrated {count} products to PostgreSQL!")

if __name__ == "__main__":
    migrate_csv_to_postgres()
