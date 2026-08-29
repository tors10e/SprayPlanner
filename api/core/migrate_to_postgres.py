import os
import sys
import json
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
            df[col] = df[col].fillna('').astype(str).str.strip()
            df.loc[df[col].str.lower() == 'nan', col] = ''

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

    # Safety guard: if database is already initialized and has data, skip seeding/migrations
    force_migrate = "--force" in sys.argv
    if not force_migrate:
        try:
            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'spray_history')")
            if cursor.fetchone()[0]:
                cursor.execute("SELECT COUNT(*) FROM spray_history")
                if cursor.fetchone()[0] > 0:
                    print("PostgreSQL database is already initialized and contains data. Skipping seeding/migrations.")
                    # Run schema migration on existing DB to enable PostGIS and add the geometry column safely
                    try:
                        cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
                        cursor.execute("ALTER TABLE vineyard_blocks ADD COLUMN IF NOT EXISTS block_area GEOMETRY(Polygon, 4326);")
                        
                        # Rename block_events to block_applications if it exists
                        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'block_events')")
                        if cursor.fetchone()[0]:
                            print("Migrating table 'block_events' to 'block_applications'...")
                            cursor.execute("ALTER TABLE block_events RENAME TO block_applications;")
                            cursor.execute("ALTER TABLE spray_history RENAME COLUMN block_event_id TO block_application_id;")
                            cursor.execute("ALTER SEQUENCE IF EXISTS block_events_id_seq RENAME TO block_applications_id_seq;")
                            
                        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS system_settings (
                            key VARCHAR(100) PRIMARY KEY,
                            value VARCHAR(500)
                        );
                        """)
                        defaults = {
                            "min_spray_interval": "7",
                            "max_spray_interval": "14",
                            "rain_threshold_inch": "1.0",
                            "min_rain_free_hours": "12",
                            "wunderground_api_key": "",
                            "wunderground_station_id": "KGALAKEM20",
                            "weather_provider": "NOAA"
                        }
                        for k, v in defaults.items():
                            cursor.execute("INSERT INTO system_settings (key, value) VALUES (%s, %s) ON CONFLICT (key) DO NOTHING;", (k, v))
                        conn.commit()
                        print("PostgreSQL schema migration completed: block_area and system_settings verified/added.")
                    except Exception as migration_err:
                        print("Error during database alteration migration:", migration_err)
                        conn.rollback()
                    cursor.close()
                    conn.close()
                    return
        except Exception as e:
            print("Checking database initialization status:", e)

    # Try to load all existing tables to preserve them as seed data
    existing_data = {}
    
    try:
        # Check if table 'block_events' exists but not 'block_applications', and rename it first!
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'block_events')")
        if cursor.fetchone()[0]:
            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'block_applications')")
            if not cursor.fetchone()[0]:
                print("Renaming block_events to block_applications during schema preservation...")
                cursor.execute("ALTER TABLE block_events RENAME TO block_applications;")
                cursor.execute("ALTER TABLE spray_history RENAME COLUMN block_event_id TO block_application_id;")
                cursor.execute("ALTER SEQUENCE IF EXISTS block_events_id_seq RENAME TO block_applications_id_seq;")
                conn.commit()
    except Exception as pres_rename_err:
        print("Warning: Could not rename block_events to block_applications during preservation:", pres_rename_err)
        conn.rollback()

    tables_to_preserve = [
        "volume_units",
        "products",
        "vineyard_blocks",
        "vineyard_rows",
        "spray_events",
        "block_applications",
        "spray_history"
    ]
    
    try:
        for table in tables_to_preserve:
            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = %s)", (table,))
            if cursor.fetchone()[0]:
                cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}' ORDER BY ordinal_position")
                cols = [r[0] for r in cursor.fetchall()]
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                existing_data[table] = []
                for r in rows:
                    row_dict = {}
                    for col, val in zip(cols, r):
                        if hasattr(val, 'isoformat'):
                            val = val.isoformat()
                        elif hasattr(val, 'strftime'):
                            val = str(val)
                        row_dict[col] = val
                    existing_data[table].append(row_dict)
        if existing_data.get("spray_events"):
            print(f"Successfully loaded {len(existing_data['spray_events'])} existing spray events to preserve.")
    except Exception as e:
        print("Warning: Could not read existing database state:", e)

    # Load seed file if we don't have database data in memory
    seed_file = os.path.join(os.path.dirname(__file__), "db_seed_data.json")
    if not existing_data.get("spray_events") and os.path.exists(seed_file):
        print(f"No active database records found to preserve. Loading seed from '{seed_file}'...")
        try:
            with open(seed_file, "r") as f:
                existing_data = json.load(f)
        except Exception as e:
            print("Warning: Could not read seed file:", e)
    
    # Recreate the volume_units lookup table
    print("Recreating 'volume_units' table...")
    cursor.execute('DROP TABLE IF EXISTS volume_units CASCADE;')
    cursor.execute("""
    CREATE TABLE volume_units (
        unit VARCHAR(50) PRIMARY KEY
    );
    """)

    # Seed volume_units with standard and CSV units
    unique_units = set(["lbs", "fl oz", "oz", "qt", "gal", "ml", "L"])
    if "units" in df.columns:
        unique_units.update(df["units"].dropna().astype(str).str.strip().unique())
    for u in sorted(unique_units):
        u_clean = str(u).strip()
        if u_clean and u_clean.lower() not in ['nan', 'none', 'null', '']:
            cursor.execute('INSERT INTO volume_units (unit) VALUES (%s) ON CONFLICT DO NOTHING;', (u_clean,))

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
        "units" VARCHAR(50) REFERENCES volume_units(unit) ON UPDATE CASCADE ON DELETE RESTRICT,
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
    cursor.execute('CREATE UNIQUE INDEX unique_product_name_case_insensitive ON products (LOWER("Product"));')
    
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
            if pd.isna(val) or str(val).strip() == '' or str(val).lower() == 'nan':
                val = None
            vals.append(val)
        vals += [None, None, None, None, False, False, False, False, None, None, None, None, None]
        cursor.execute(insert_sql, vals)
        count += 1
    print(f"Successfully migrated {count} products to PostgreSQL!")

    # Restore products from previous state/seed to avoid foreign key errors on custom products
    if "products" in existing_data and existing_data["products"]:
        print(f"Restoring {len(existing_data['products'])} products from previous state/seed...")
        for p in existing_data["products"]:
            u = p.get("units")
            if u:
                cursor.execute('INSERT INTO volume_units (unit) VALUES (%s) ON CONFLICT DO NOTHING;', (u,))
                
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'products' ORDER BY ordinal_position")
        cols = [r[0] for r in cursor.fetchall()]
        cols_str = ", ".join([f'"{c}"' for c in cols])
        placeholders = ", ".join(["%s"] * len(cols))
        insert_prod_sql = f'INSERT INTO products ({cols_str}) VALUES ({placeholders}) ON CONFLICT ("Product") DO NOTHING;'
        
        for p in existing_data["products"]:
            vals = [p.get(c) for c in cols]
            cursor.execute(insert_prod_sql, vals)

    # --- Recreate database tables in normalized 3-table schema ---
    print("Recreating database tables in normalized 3-table schema...")
    cursor.execute('CREATE EXTENSION IF NOT EXISTS postgis;')
    cursor.execute('DROP TABLE IF EXISTS vineyard_rows CASCADE;')
    cursor.execute('DROP TABLE IF EXISTS vineyard_blocks CASCADE;')
    cursor.execute('DROP TABLE IF EXISTS spray_history CASCADE;')
    cursor.execute('DROP TABLE IF EXISTS block_applications CASCADE;')
    cursor.execute('DROP TABLE IF EXISTS spray_events CASCADE;')

    create_vineyard_blocks_table = """
    CREATE TABLE vineyard_blocks (
        block_code VARCHAR(50) PRIMARY KEY,
        varieties VARCHAR(255),
        acres DOUBLE PRECISION,
        vine_spacing DOUBLE PRECISION,
        row_spacing DOUBLE PRECISION,
        trellis_type VARCHAR(100),
        rootstock VARCHAR(100),
        block_area GEOMETRY(Polygon, 4326)
    );
    """
    cursor.execute(create_vineyard_blocks_table)
    
    create_vineyard_rows_table = """
    CREATE TABLE vineyard_rows (
        id SERIAL PRIMARY KEY,
        block_code VARCHAR(50) REFERENCES vineyard_blocks(block_code) ON DELETE CASCADE,
        row_number INTEGER,
        row_length DOUBLE PRECISION,
        UNIQUE(block_code, row_number)
    );
    """
    cursor.execute(create_vineyard_rows_table)

    # Helper to convert coordinates to WKT format
    def coords_to_wkt_polygon(coords):
        if not coords or len(coords) < 3:
            return None
        try:
            pts = list(coords)
            if pts[0] != pts[-1]:
                pts.append(pts[0])
            wkt_pts = ", ".join(f"{p[1]} {p[0]}" for p in pts)
            return f"POLYGON(({wkt_pts}))"
        except Exception as e:
            print(f"Error formatting coordinates to WKT: {e}")
            return None

    # Seed vineyard blocks and rows
    if "vineyard_blocks" in existing_data and existing_data["vineyard_blocks"]:
        print(f"Restoring {len(existing_data['vineyard_blocks'])} vineyard blocks...")
        for b in existing_data["vineyard_blocks"]:
            block_area_data = b.get("block_area") or b.get("polygon")
            wkt = None
            if block_area_data:
                if isinstance(block_area_data, str):
                    wkt = block_area_data
                else:
                    wkt = coords_to_wkt_polygon(block_area_data)

            cursor.execute(
                'INSERT INTO vineyard_blocks (block_code, varieties, acres, vine_spacing, row_spacing, trellis_type, rootstock, block_area) VALUES (%s, %s, %s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326)) ON CONFLICT (block_code) DO NOTHING;',
                (b["block_code"], b["varieties"], b["acres"], b["vine_spacing"], b["row_spacing"], b["trellis_type"], b["rootstock"], wkt)
            )
        if "vineyard_rows" in existing_data and existing_data["vineyard_rows"]:
            print(f"Restoring {len(existing_data['vineyard_rows'])} vineyard rows...")
            for r in existing_data["vineyard_rows"]:
                cursor.execute(
                    'INSERT INTO vineyard_rows (id, block_code, row_number, row_length) VALUES (%s, %s, %s, %s) ON CONFLICT (block_code, row_number) DO NOTHING;',
                    (r.get("id"), r["block_code"], r["row_number"], r["row_length"])
                )
            cursor.execute("SELECT setval('vineyard_rows_id_seq', COALESCE((SELECT MAX(id)+1 FROM vineyard_rows), 1), false)")
    else:
        print("Seeding with default vineyard blocks and rows...")
        default_blocks = [
            ("cs", "Cabernet Sauvignon", 1.0, 6.0, 9.0, "VSP", "3309C"),
            ("pm", "Pinot Meunier", 1.0, 6.0, 9.0, "VSP", "101-14"),
            ("tr", "Traminette", 1.0, 6.0, 9.0, "High Wire", "Own"),
            ("ch", "Chardonnay", 1.0, 6.0, 9.0, "VSP", "3309C")
        ]
        for bcode, var, ac, vs, rs, tr, rs_stock in default_blocks:
            cursor.execute(
                'INSERT INTO vineyard_blocks (block_code, varieties, acres, vine_spacing, row_spacing, trellis_type, rootstock, block_area) VALUES (%s, %s, %s, %s, %s, %s, %s, NULL);',
                (bcode, var, ac, vs, rs, tr, rs_stock)
            )
            for rnum in range(1, 11):
                cursor.execute(
                    'INSERT INTO vineyard_rows (block_code, row_number, row_length) VALUES (%s, %s, %s);',
                    (bcode, rnum, 300.0)
                )

    create_spray_events_table = """
    CREATE TABLE spray_events (
        id SERIAL PRIMARY KEY,
        "Spray #" INTEGER
    );
    CREATE UNIQUE INDEX unique_scheduled_spray ON spray_events ("Spray #") WHERE "Spray #" IS NOT NULL;
    """
    cursor.execute(create_spray_events_table)
    
    create_block_applications_table = """
    CREATE TABLE block_applications (
        id SERIAL PRIMARY KEY,
        event_id INTEGER REFERENCES spray_events(id) ON DELETE CASCADE,
        "Block " VARCHAR(50) REFERENCES vineyard_blocks(block_code) ON UPDATE CASCADE ON DELETE RESTRICT,
        "Date" VARCHAR(50),
        "End Time" VARCHAR(50),
        "Liters/Acre" DOUBLE PRECISION
    );
    CREATE UNIQUE INDEX unique_event_block ON block_applications (event_id, "Block ");
    """
    cursor.execute(create_block_applications_table)
    
    create_history_table = """
    CREATE TABLE spray_history (
        id SERIAL PRIMARY KEY,
        block_application_id INTEGER REFERENCES block_applications(id) ON DELETE CASCADE,
        "Pesticide" VARCHAR(255) REFERENCES products("Product") ON UPDATE CASCADE ON DELETE RESTRICT,
        "Dose/acre" DOUBLE PRECISION,
        "Dose per L @150 l" DOUBLE PRECISION,
        "Calculated Dose" DOUBLE PRECISION,
        "Dose Units" VARCHAR(50),
        "Notes" TEXT,
        "PHI Date" VARCHAR(50),
        "REI_TIME" VARCHAR(50)
    );
    CREATE UNIQUE INDEX unique_spray_history_chemical ON spray_history (
        block_application_id,
        "Pesticide"
    );
    """
    cursor.execute(create_history_table)

    print("Creating 'system_settings' table...")
    cursor.execute('DROP TABLE IF EXISTS system_settings CASCADE;')
    cursor.execute("""
    CREATE TABLE system_settings (
        key VARCHAR(100) PRIMARY KEY,
        value VARCHAR(500)
    );
    """)
    defaults = {
        "min_spray_interval": "7",
        "max_spray_interval": "14",
        "rain_threshold_inch": "1.0",
        "min_rain_free_hours": "12",
        "wunderground_api_key": "",
        "wunderground_station_id": "KGALAKEM20",
        "weather_provider": "NOAA"
    }
    for k, v in defaults.items():
        cursor.execute("INSERT INTO system_settings (key, value) VALUES (%s, %s) ON CONFLICT (key) DO NOTHING;", (k, v))

    if "spray_events" in existing_data and existing_data["spray_events"]:
        print(f"Restoring {len(existing_data['spray_events'])} spray events...")
        for e in existing_data["spray_events"]:
            cursor.execute('INSERT INTO spray_events (id, "Spray #") VALUES (%s, %s) ON CONFLICT (id) DO NOTHING;', (e["id"], e["Spray #"]))
        cursor.execute("SELECT setval('spray_events_id_seq', COALESCE((SELECT MAX(id)+1 FROM spray_events), 1), false)")
        
        block_apps = existing_data.get("block_applications") or existing_data.get("block_events")
        if block_apps:
            print(f"Restoring {len(block_apps)} block applications...")
            for b in block_apps:
                cursor.execute(
                    'INSERT INTO block_applications (id, event_id, "Block ", "Date", "End Time", "Liters/Acre") VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;',
                    (b["id"], b["event_id"], b["Block "], b["Date"], b["End Time"], b["Liters/Acre"])
                )
            cursor.execute("SELECT setval('block_applications_id_seq', COALESCE((SELECT MAX(id)+1 FROM block_applications), 1), false)")
            
        if "spray_history" in existing_data and existing_data["spray_history"]:
            print(f"Restoring {len(existing_data['spray_history'])} chemical application logs...")
            h_count = 0
            for h in existing_data["spray_history"]:
                b_app_id = h.get("block_application_id") or h.get("block_event_id")
                cursor.execute(
                    'INSERT INTO spray_history (id, block_application_id, "Pesticide", "Dose/acre", "Dose per L @150 l", "Calculated Dose", "Dose Units", "Notes", "PHI Date", "REI_TIME") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;',
                    (h["id"], b_app_id, h["Pesticide"], h["Dose/acre"], h["Dose per L @150 l"], h["Calculated Dose"], h["Dose Units"], h["Notes"], h["PHI Date"], h["REI_TIME"])
                )
                h_count += 1
            cursor.execute("SELECT setval('spray_history_id_seq', COALESCE((SELECT MAX(id)+1 FROM spray_history), 1), false)")
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
        block_application_map = {}
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
                
            # 2. Get child block_application ID
            block_key = (event_id, clean_block)
            if block_key not in block_application_map:
                cursor.execute(
                    'INSERT INTO block_applications (event_id, "Block ", "Date", "End Time", "Liters/Acre") VALUES (%s, %s, %s, %s, %s) RETURNING id',
                    (event_id, clean_block, clean_date, clean_end_time, liters_acre)
                )
                block_application_id = cursor.fetchone()[0]
                block_application_map[block_key] = block_application_id
            else:
                block_application_id = block_application_map[block_key]
                
            # Insert chemical log
            pesticide = row[4]
            phi_date = row[13] or None
            rei_time = row[14] or None
            dose_acre = float(row[18]) if row[18] is not None and str(row[18]).strip() != "" else None
            dose_per_l = float(row[19]) if row[19] is not None and str(row[19]).strip() != "" else None
            calc_dose = float(row[21]) if row[21] is not None and str(row[21]).strip() != "" else None
            dose_units = row[22] or None
            notes = row[24] or ""
            
            insert_history_sql = """
            INSERT INTO spray_history (
                block_application_id, "Pesticide", "Dose/acre", 
                "Dose per L @150 l", "Calculated Dose", "Dose Units", 
                "Notes", "PHI Date", "REI_TIME"
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_history_sql, (
                block_application_id, pesticide, dose_acre,
                dose_per_l, calc_dose, dose_units,
                notes, phi_date, rei_time
            ))
            h_count += 1

    # Commit the main migration transaction first
    conn.commit()

    print("Granting table and sequence privileges to sprayplanner_user...")
    try:
        # Create a new cursor to start a new transaction for privileges
        cursor.close()
        cursor = conn.cursor()
        cursor.execute('GRANT ALL PRIVILEGES ON TABLE volume_units TO sprayplanner_user;')
        cursor.execute('GRANT ALL PRIVILEGES ON TABLE products TO sprayplanner_user;')
        cursor.execute('GRANT ALL PRIVILEGES ON TABLE vineyard_blocks TO sprayplanner_user;')
        cursor.execute('GRANT ALL PRIVILEGES ON TABLE vineyard_rows TO sprayplanner_user;')
        cursor.execute('GRANT ALL PRIVILEGES ON TABLE spray_events TO sprayplanner_user;')
        cursor.execute('GRANT ALL PRIVILEGES ON TABLE block_applications TO sprayplanner_user;')
        cursor.execute('GRANT ALL PRIVILEGES ON TABLE spray_history TO sprayplanner_user;')
        cursor.execute('GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sprayplanner_user;')
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("Warning: Could not grant privileges to sprayplanner_user (role may not exist):", e)

    cursor.close()
    conn.close()
    
    print(f"Successfully seeded {h_count} normalized history records to PostgreSQL!")

if __name__ == "__main__":
    migrate_csv_to_postgres()
