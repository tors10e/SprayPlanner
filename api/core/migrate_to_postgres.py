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
        conn = psycopg2.connect(
            host=config.db_host,
            port=config.db_port,
            database=config.db_name,
            user="postgres",
            password="Black1ce!"
        )
    except Exception as e:
        print(f"Failed to connect to PostgreSQL: {e}")
        sys.exit(1)
        
    cursor = conn.cursor()
    
    # Recreate the table
    print("Recreating 'products' table...")
    cursor.execute('DROP TABLE IF EXISTS products CASCADE;')
    
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
        max_rate NUMERIC(4,1),
        "EPA No" VARCHAR(100),
        "Active Ingredient" VARCHAR(200),
        "Singal Word" VARCHAR(100)
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
        "min_rate", "max_rate", "EPA No", "Active Ingredient", "Singal Word"
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
        vals += [None, None, None, None, False, False, False, False, None, None, None, None, None]
        cursor.execute(insert_sql, vals)
        count += 1
        
    print(f"Successfully migrated {count} products to PostgreSQL!")

    # --- Recreate and Seed spray_history table ---
    print("Recreating database tables in normalized schema...")
    cursor.execute('DROP TABLE IF EXISTS spray_history CASCADE;')
    cursor.execute('DROP TABLE IF EXISTS spray_events CASCADE;')
    
    create_events_table = """
    CREATE TABLE spray_events (
        id SERIAL PRIMARY KEY,
        "Spray #" INTEGER,
        "Block " VARCHAR(50),
        "Date" VARCHAR(50),
        "End Time" VARCHAR(50)
    );
    CREATE UNIQUE INDEX unique_spray_event_entry ON spray_events (
        COALESCE("Spray #", -1),
        "Block ",
        "Date",
        COALESCE("End Time", 'NA')
    );
    """
    cursor.execute(create_events_table)
    
    create_history_table = """
    CREATE TABLE spray_history (
        id SERIAL PRIMARY KEY,
        event_id INTEGER REFERENCES spray_events(id) ON DELETE CASCADE,
        "Pesticide" VARCHAR(255) REFERENCES products("Product") ON UPDATE CASCADE ON DELETE RESTRICT,
        "Liters/Acre" DOUBLE PRECISION,
        "Dose/acre" DOUBLE PRECISION,
        "Dose per L @150 l" DOUBLE PRECISION,
        "Calculated Dose" DOUBLE PRECISION,
        "Dose Units" VARCHAR(50),
        "Actual Amt/acre" DOUBLE PRECISION,
        "Notes" TEXT,
        "PHI Date" VARCHAR(50),
        "REI_TIME" VARCHAR(50)
    );
    CREATE UNIQUE INDEX unique_spray_history_chemical ON spray_history (
        event_id,
        "Pesticide"
    );
    """
    cursor.execute(create_history_table)

    seed_history = [
        [4, "5/11/26", "1312", "cs", "manzate", "70506-234", "m", "mancozeb", "downy", "caution", 24.0, 66, "lbs", "7/16/26", "", 100.0, None, None, None, None, None, None, None, 1.5, ""],
        [4, "5/11/26", "1312", "cs", "yellow jacket sulfur", "6325-13", "m2", "sulfur", "powdery", "caution", 24.0, 0, "lbs", "5/11/26", "", 100.0, None, None, 3.0, 0.03, "lbs", None, None, 3.0, ""],
        [4, "5/11/26", "1312", "cs", "zampro", "7969=302", "45/40", "Ametoctradin, dimethomorph", "downy", "caution", 12.0, 14, "fl oz", "5/25/26", "", 200.0, 11.0, 14.0, 12.5, 0.0625, "fl oz", 375.0, "ml", 16.0, ""],
        [4, "5/11/26", "1312", "cs", "inspire super", "100-1262", "3", "Difenoconazole, Cyprodinil*", "powdery, black rot, botrytus", "caution", 12.0, 14, "", "5/25/26", "", 16.0, 20.0, None, None, None, None, None, None, 12.0, ""],
        [4, "5/11/26", "1448", "cs", "kphite", "42750-61-72693", "na", "Mono and dipotasium salts of phosphorous acids", "downy", "caution", 4.0, 0, "", "5/11/26", "", 150.0, None, None, 2.0, None, None, None, None, 2.0, ""],
        [4, "5/11/26", "1448", "pm", "manzate", "70506-234", "m", "mancozeb", "downy", "caution", 24.0, 66, "lbs", "7/16/26", "", 100.0, None, None, None, None, None, None, None, 1.5, ""],
        [4, "5/11/26", "1448", "pm", "yellow jacket sulfur", "6325-13", "m2", "sulfur", "powdery", "caution", 24.0, 0, "lbs", "5/11/26", "", 100.0, None, None, 3.0, 0.03, "lbs", None, None, 3.0, ""],
        [4, "5/11/26", "1448", "pm", "zampro", "7969=302", "45/40", "Ametoctradin, dimethomorph", "downy", "caution", 12.0, 14, "fl oz", "5/25/26", "", 200.0, 11.0, 14.0, 12.5, 0.0625, "fl oz", 375.0, "ml", 16.0, ""],
        [4, "5/11/26", "1448", "pm", "inspire super", "100-1262", "3", "Difenoconazole, Cyprodinil*", "powdery, black rot, botrytus", "caution", 12.0, 14, "", "5/25/26", "", None, None, None, None, None, None, None, None, 12.0, ""],
        [4, "5/11/26", "1600", "tr", "manzate", "70506-234", "m", "mancozeb", "downy", "caution", 24.0, 66, "lbs", "7/16/26", "", 100.0, None, None, None, None, None, None, None, 1.5, ""],
        [4, "5/11/26", "1600", "tr", "yellow jacket sulfur", "6325-13", "m2", "sulfur", "powdery", "caution", 24.0, 0, "lbs", "5/11/26", "", 100.0, None, None, 3.0, 0.03, "lbs", None, None, 3.0, ""],
        [4, "5/11/26", "1600", "tr", "zampro", "7969=302", "45/40", "Ametoctradin, dimethomorph", "downy", "caution", 12.0, 14, "fl oz", "5/25/26", "", 200.0, 11.0, 14.0, 12.5, 0.0625, "fl oz", 375.0, "ml", 16.0, ""],
        [4, "5/11/26", "1600", "tr", "inspire super", "100-1262", "3", "Difenoconazole, Cyprodinil*", "powdery, black rot, botrytus", "caution", 12.0, 14, "", "5/25/26", "", None, None, None, None, None, None, None, None, 12.0, ""],
        [4, "5/11/26", "1700", "ch", "damoil", None, None, None, None, None, None, None, "", "", "", None, None, None, None, None, None, None, None, 2.0, ""],
        [4, "5/11/26", "1700", "ch", "kphite", None, None, None, None, None, None, None, "", "", "", None, None, None, None, None, None, None, None, 2.0, ""],
        [5, "5/30/26", "NA", "cs", "sulfur", None, None, None, None, None, None, None, "", "", "", 3.0, None, None, None, None, None, None, None, None, ""],
        [None, "", "", "cs", "Vivando", "7969-284", "U8", "Metrafenanone", "powdery mildew", "caution", 12.0, 14, "fl oz", "1/14/00", "", 200.0, 10.3, 15.4, 12.85, 12.0, "fl oz", 72000.0, "ml", 250.0, ""],
        [None, "", "", "cs", "renaz", "91234-198", "21", "Cyazofamid", "Downy", "caution", 12.0, 30, "fl oz", "1/30/00", "", 150.0, 2.1, 2.75, 2.425, 2.5, "fl oz", 375.0, "", None, ""],
        [None, "", "", "cs", "kphite", "42750-61-72693", "na", "Mono and dipotasium salts of phosphorous acids", "downy", "caution", 4.0, 0, "", "1/0/00", "", 150.0, None, None, 2.0, None, None, None, None, 2.0, ""],
        [None, "", "", "cs", "manzate", "70506-234", "m", "mancozeb", "downy", "caution", 24.0, 66, "lbs", "3/6/00", "", None, None, None, None, None, None, None, None, 1.5, ""],
        [None, "", "", "pm", "sulfur", None, None, None, None, None, None, None, "", "", "", 3.0, None, None, None, None, None, None, None, None, ""],
        [None, "", "", "pm", "Vivando", "7969-284", "U8", "Metrafenanone", "powdery mildew", "caution", 12.0, 14, "fl oz", "1/14/00", "", 200.0, 10.3, 15.4, 12.85, 12.0, "fl oz", 72000.0, "ml", 250.0, ""],
        [None, "", "", "pm", "renaz", "91234-198", "21", "Cyazofamid", "Downy", "caution", 12.0, 30, "fl oz", "1/30/00", "", 150.0, 2.1, 2.75, 2.425, 2.5, "fl oz", 375.0, "", None, ""],
        [None, "", "", "pm", "kphite", "42750-61-72693", "na", "Mono and dipotasium salts of phosphorous acids", "downy", "caution", 4.0, 0, "", "1/0/00", "", 150.0, None, None, 2.0, None, None, None, None, 2.0, ""],
        [None, "", "", "pm", "manzate", "70506-234", "m", "mancozeb", "downy", "caution", 24.0, 66, "lbs", "3/6/00", "", None, None, None, None, None, None, None, None, 1.5, ""],
        [None, "", "", "tr", "sulfur", None, None, None, None, None, None, None, "", "", "", 3.0, None, None, None, None, None, None, None, None, ""],
        [None, "", "", "tr", "Vivando", "7969-284", "U8", "Metrafenanone", "powdery mildew", "caution", 12.0, 14, "fl oz", "1/14/00", "", 200.0, 10.3, 15.4, 12.85, 12.0, "fl oz", 72000.0, "ml", 250.0, ""],
        [None, "", "", "tr", "renaz", "91234-198", "21", "Cyazofamid", "Downy", "caution", 12.0, 30, "fl oz", "1/30/00", "", 150.0, 2.1, 2.75, 2.425, 2.5, "fl oz", 375.0, "", None, ""],
        [None, "", "", "tr", "kphite", "42750-61-72693", "na", "Mono and dipotasium salts of phosphorous acids", "downy", "caution", 4.0, 0, "", "1/0/00", "", 150.0, None, None, 2.0, None, None, None, None, 2.0, ""],
        [None, "", "", "ch", "damoil", "19713-123", "na", "mineral oil", "powdery, botrytis", "caution", 4.0, 2, "", "1/2/00", "", None, None, None, None, None, None, None, None, 2.0, ""],
        [None, "", "", "ch", "kphite", "42750-61-72693", "na", "Mono and dipotasium salts of phosphorous acids", "downy", "caution", 4.0, 0, "", "1/0/00", "", 150.0, None, None, 2.0, None, None, None, None, 2.0, ""]
    ]

    # UPSERT chemical products first to fulfill foreign key references
    print("Upserting seed products from history...")
    sql_product_upsert = """
    INSERT INTO products ("Product", "EPA No", "FRAC", "Active Ingredient", "Primary Disease", "Singal Word", "rei", "phi", "units", "min_rate", "max_rate")
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT ("Product") DO UPDATE SET
        "EPA No" = COALESCE(EXCLUDED."EPA No", products."EPA No"),
        "FRAC" = COALESCE(EXCLUDED."FRAC", products."FRAC"),
        "Active Ingredient" = COALESCE(EXCLUDED."Active Ingredient", products."Active Ingredient"),
        "Singal Word" = COALESCE(EXCLUDED."Singal Word", products."Singal Word"),
        "rei" = COALESCE(EXCLUDED."rei", products."rei"),
        "phi" = COALESCE(EXCLUDED."phi", products."phi"),
        "units" = COALESCE(EXCLUDED."units", products."units"),
        "min_rate" = COALESCE(EXCLUDED."min_rate", products."min_rate"),
        "max_rate" = COALESCE(EXCLUDED."max_rate", products."max_rate")
    """
    
    for row in seed_history:
        p_name = row[4]
        if not p_name:
            continue
        cursor.execute(sql_product_upsert, (
            p_name,
            row[5] or None,
            row[6] or None,
            row[7] or None,
            row[8] or None,
            row[9] or None,
            int(row[10]) if row[10] is not None else None,
            int(row[11]) if row[11] is not None else None,
            row[12] or None,
            row[16] or None,
            row[17] or None
        ))

    # Seed events and chemical logs in normalized structure
    print("Seeding normalized events and chemical applications...")
    event_map = {}
    h_count = 0
    
    for row in seed_history:
        # Extract event fields
        spray_num = int(row[0]) if row[0] is not None else None
        date = row[1] or None
        end_time = row[2] or None
        block = row[3] or None
        
        # Normalize empty values to None/NULL matching database representation
        clean_spray_num = None if spray_num == "" or spray_num is None else int(spray_num)
        clean_block = None if block == "" or block is None else block
        clean_date = None if date == "" or date is None else date
        clean_end_time = None if end_time == "" or end_time is None else end_time
        
        event_key = (clean_spray_num, clean_block, clean_date, clean_end_time)
        if event_key not in event_map:
            cursor.execute(
                'INSERT INTO spray_events ("Spray #", "Block ", "Date", "End Time") VALUES (%s, %s, %s, %s) RETURNING id',
                (clean_spray_num, clean_block, clean_date, clean_end_time)
            )
            event_id = cursor.fetchone()[0]
            event_map[event_key] = event_id
        else:
            event_id = event_map[event_key]
            
        # Insert chemical log
        pesticide = row[4]
        phi_date = row[13] or None
        rei_time = row[14] or None
        liters_acre = float(row[15]) if row[15] is not None else None
        dose_acre = float(row[18]) if row[18] is not None else None
        dose_per_l = float(row[19]) if row[19] is not None else None
        calc_dose = float(row[21]) if row[21] is not None else None
        dose_units = row[22] or None
        actual_amt = float(row[23]) if row[23] is not None else None
        notes = row[24] or ""
        
        insert_history_sql = """
        INSERT INTO spray_history (
            event_id, "Pesticide", "Liters/Acre", "Dose/acre", 
            "Dose per L @150 l", "Calculated Dose", "Dose Units", 
            "Actual Amt/acre", "Notes", "PHI Date", "REI_TIME"
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_history_sql, (
            event_id, pesticide, liters_acre, dose_acre,
            dose_per_l, calc_dose, dose_units,
            actual_amt, notes, phi_date, rei_time
        ))
        h_count += 1

    print("Granting table and sequence privileges to sprayplanner_user...")
    cursor.execute('GRANT ALL PRIVILEGES ON TABLE products TO sprayplanner_user;')
    cursor.execute('GRANT ALL PRIVILEGES ON TABLE spray_events TO sprayplanner_user;')
    cursor.execute('GRANT ALL PRIVILEGES ON TABLE spray_history TO sprayplanner_user;')
    cursor.execute('GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sprayplanner_user;')

    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"Successfully seeded {h_count} normalized history records to PostgreSQL!")

if __name__ == "__main__":
    migrate_csv_to_postgres()
