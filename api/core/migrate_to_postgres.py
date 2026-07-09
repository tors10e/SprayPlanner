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
    
    # Recreate the products table
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
        vals += [None, None, None, None, False, False, False, False, None, None, None, None, None]
        cursor.execute(insert_sql, vals)
        count += 1
        
    print(f"Successfully migrated {count} products to PostgreSQL!")

    # Try to load existing history entries to preserve them as seed data
    existing_entries = []
    try:
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'block_events')")
        block_events_exists = cursor.fetchone()[0]
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'spray_history')")
        history_exists = cursor.fetchone()[0]
        
        if block_events_exists and history_exists:
            print("Found 3-table layout data. Reading to preserve...")
            cursor.execute("""
                SELECT 
                    e."Spray #", b."Date", b."End Time", b."Block ",
                    h."Pesticide", b."Liters/Acre", h."Dose/acre", 
                    h."Dose per L @150 l", h."Calculated Dose", h."Dose Units", 
                    h."Actual Amt/acre", h."Notes", h."PHI Date", h."REI_TIME",
                    p."EPA No", p."FRAC", p."Active Ingredient", p."Singal Word",
                    p.rei, p.phi, p.units, p.min_rate, p.max_rate
                FROM spray_history h
                INNER JOIN block_events b ON h.block_event_id = b.id
                INNER JOIN spray_events e ON b.event_id = e.id
                LEFT JOIN products p ON h."Pesticide" = p."Product"
            """)
            rows = cursor.fetchall()
        elif history_exists:
            print("Found 2-table layout data. Reading to preserve...")
            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'spray_events')")
            events_exists = cursor.fetchone()[0]
            if events_exists:
                cursor.execute("SELECT COLUMN_NAME FROM information_schema.columns WHERE table_name = 'spray_history' AND column_name = 'Liters/Acre'")
                water_in_history = cursor.fetchone() is not None
                if water_in_history:
                    cursor.execute("""
                        SELECT 
                            e."Spray #", e."Date", e."End Time", e."Block ",
                            h."Pesticide", h."Liters/Acre", h."Dose/acre", 
                            h."Dose per L @150 l", h."Calculated Dose", h."Dose Units", 
                            h."Actual Amt/acre", h."Notes", h."PHI Date", h."REI_TIME",
                            p."EPA No", p."FRAC", p."Active Ingredient", p."Singal Word",
                            p.rei, p.phi, p.units, p.min_rate, p.max_rate
                        FROM spray_history h
                        INNER JOIN spray_events e ON h.event_id = e.id
                        LEFT JOIN products p ON h."Pesticide" = p."Product"
                    """)
                else:
                    cursor.execute("""
                        SELECT 
                            e."Spray #", e."Date", e."End Time", e."Block ",
                            h."Pesticide", e."Liters/Acre", h."Dose/acre", 
                            h."Dose per L @150 l", h."Calculated Dose", h."Dose Units", 
                            h."Actual Amt/acre", h."Notes", h."PHI Date", h."REI_TIME",
                            p."EPA No", p."FRAC", p."Active Ingredient", p."Singal Word",
                            p.rei, p.phi, p.units, p.min_rate, p.max_rate
                        FROM spray_history h
                        INNER JOIN spray_events e ON h.event_id = e.id
                        LEFT JOIN products p ON h."Pesticide" = p."Product"
                    """)
                rows = cursor.fetchall()
            else:
                rows = []
        else:
            rows = []
            
        for r in rows:
            existing_entries.append([
                r[0], # Spray #
                r[1], # Date
                r[2], # End Time
                r[3], # Block
                r[4], # Pesticide
                r[14], # EPA No
                r[15], # FRAC
                r[16], # Active Ingredient
                None, # Primary Disease
                r[17], # Signal Word
                r[18], # rei
                r[19], # phi
                r[20], # units
                r[12], # PHI Date
                r[13], # REI_TIME
                r[5], # Liters/Acre
                r[21], # Min Dose
                r[22], # Max Dose
                r[6], # Dose/acre
                r[7], # Dose per L
                r[20], # Rate Units
                r[8], # Calculated Dose
                r[9], # Dose Units
                r[10], # Actual Amt
                r[11] # Notes
            ])
        if rows:
            print(f"Successfully loaded {len(existing_entries)} records to preserve.")
    except Exception as e:
        print("Warning: Could not read existing history data:", e)

    # --- Recreate database tables in normalized 3-table schema ---
    print("Recreating database tables in normalized 3-table schema...")
    cursor.execute('DROP TABLE IF EXISTS spray_history CASCADE;')
    cursor.execute('DROP TABLE IF EXISTS block_events CASCADE;')
    cursor.execute('DROP TABLE IF EXISTS spray_events CASCADE;')
    
    create_spray_events_table = """
    CREATE TABLE spray_events (
        id SERIAL PRIMARY KEY,
        "Spray #" INTEGER
    );
    CREATE UNIQUE INDEX unique_scheduled_spray ON spray_events ("Spray #") WHERE "Spray #" IS NOT NULL;
    """
    cursor.execute(create_spray_events_table)
    
    create_block_events_table = """
    CREATE TABLE block_events (
        id SERIAL PRIMARY KEY,
        event_id INTEGER REFERENCES spray_events(id) ON DELETE CASCADE,
        "Block " VARCHAR(50),
        "Date" VARCHAR(50),
        "End Time" VARCHAR(50),
        "Liters/Acre" DOUBLE PRECISION
    );
    CREATE UNIQUE INDEX unique_event_block ON block_events (event_id, "Block ");
    """
    cursor.execute(create_block_events_table)
    
    create_history_table = """
    CREATE TABLE spray_history (
        id SERIAL PRIMARY KEY,
        block_event_id INTEGER REFERENCES block_events(id) ON DELETE CASCADE,
        "Pesticide" VARCHAR(255) REFERENCES products("Product") ON UPDATE CASCADE ON DELETE RESTRICT,
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
        block_event_id,
        "Pesticide"
    );
    """
    cursor.execute(create_history_table)

    if existing_entries:
        seed_history = existing_entries
        print(f"Using {len(seed_history)} existing database records as seed data.")
    else:
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
        print("No existing database data found. Seeding with fallback default records.")

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
            int(row[10]) if row[10] is not None and str(row[10]).strip() != "" else None,
            int(row[11]) if row[11] is not None and str(row[11]).strip() != "" else None,
            row[12] or None,
            row[16] or None,
            row[17] or None
        ))

    # Seed events and chemical logs in normalized 3-table structure
    print("Seeding normalized events and chemical applications...")
    spray_event_map = {}
    block_event_map = {}
    h_count = 0
    
    for row in seed_history:
        # Extract fields
        spray_num = int(row[0]) if row[0] is not None and str(row[0]).strip() != "" else None
        date = row[1] or None
        end_time = row[2] or None
        block = row[3] or None
        liters_acre = float(row[15]) if row[15] is not None and str(row[15]).strip() != "" else None
        
        # Normalize empty values
        clean_spray_num = None if spray_num == "" or spray_num is None else int(spray_num)
        clean_block = None if block == "" or block is None else block
        clean_date = None if date == "" or date is None else date
        clean_end_time = None if end_time == "" or end_time is None else end_time
        
        # 1. Get parent spray_event ID
        if clean_spray_num is not None:
            if clean_spray_num not in spray_event_map:
                cursor.execute(
                    'INSERT INTO spray_events ("Spray #") VALUES (%s) RETURNING id',
                    (clean_spray_num,)
                )
                event_id = cursor.fetchone()[0]
                spray_event_map[clean_spray_num] = event_id
            else:
                event_id = spray_event_map[clean_spray_num]
        else:
            # Unscheduled: Create a new parent event row
            cursor.execute(
                'INSERT INTO spray_events ("Spray #") VALUES (NULL) RETURNING id'
            )
            event_id = cursor.fetchone()[0]
            
        # 2. Get child block_event ID
        block_key = (event_id, clean_block)
        if block_key not in block_event_map:
            cursor.execute(
                'INSERT INTO block_events (event_id, "Block ", "Date", "End Time", "Liters/Acre") VALUES (%s, %s, %s, %s, %s) RETURNING id',
                (event_id, clean_block, clean_date, clean_end_time, liters_acre)
            )
            block_event_id = cursor.fetchone()[0]
            block_event_map[block_key] = block_event_id
        else:
            block_event_id = block_event_map[block_key]
            
        # Insert chemical log
        pesticide = row[4]
        phi_date = row[13] or None
        rei_time = row[14] or None
        dose_acre = float(row[18]) if row[18] is not None and str(row[18]).strip() != "" else None
        dose_per_l = float(row[19]) if row[19] is not None and str(row[19]).strip() != "" else None
        calc_dose = float(row[21]) if row[21] is not None and str(row[21]).strip() != "" else None
        dose_units = row[22] or None
        actual_amt = float(row[23]) if row[23] is not None and str(row[23]).strip() != "" else None
        notes = row[24] or ""
        
        insert_history_sql = """
        INSERT INTO spray_history (
            block_event_id, "Pesticide", "Dose/acre", 
            "Dose per L @150 l", "Calculated Dose", "Dose Units", 
            "Actual Amt/acre", "Notes", "PHI Date", "REI_TIME"
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_history_sql, (
            block_event_id, pesticide, dose_acre,
            dose_per_l, calc_dose, dose_units,
            actual_amt, notes, phi_date, rei_time
        ))
        h_count += 1

    print("Granting table and sequence privileges to sprayplanner_user...")
    cursor.execute('GRANT ALL PRIVILEGES ON TABLE products TO sprayplanner_user;')
    cursor.execute('GRANT ALL PRIVILEGES ON TABLE spray_events TO sprayplanner_user;')
    cursor.execute('GRANT ALL PRIVILEGES ON TABLE block_events TO sprayplanner_user;')
    cursor.execute('GRANT ALL PRIVILEGES ON TABLE spray_history TO sprayplanner_user;')
    cursor.execute('GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sprayplanner_user;')

    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"Successfully seeded {h_count} normalized history records to PostgreSQL!")

if __name__ == "__main__":
    migrate_csv_to_postgres()
