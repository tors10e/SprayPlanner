import json
import psycopg2
import sys
from config import Config

def dump_db_to_json():
    config = Config()
    print(f"Connecting to database '{config.db_name}' to dump current data...")
    try:
        conn = psycopg2.connect(
            host=config.db_host,
            port=config.db_port,
            database=config.db_name,
            user="postgres",
            password="Black1ce!"
        )
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)
        
    cursor = conn.cursor()
    
    tables = [
        "volume_units",
        "products",
        "vineyard_blocks",
        "vineyard_rows",
        "spray_events",
        "block_events",
        "spray_history"
    ]
    
    dump_data = {}
    
    for table in tables:
        # Check if table exists
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = %s)", (table,))
        if not cursor.fetchone()[0]:
            print(f"Table '{table}' does not exist, skipping.")
            continue
            
        # Get column names
        cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}' ORDER BY ordinal_position")
        columns = [r[0] for r in cursor.fetchall()]
        
        # Get all rows
        if table == "vineyard_blocks":
            cols_str = ", ".join(f'"{c}"' if c != 'block_area' else 'ST_AsText(block_area) as block_area' for c in columns)
            cursor.execute(f"SELECT {cols_str} FROM {table}")
        else:
            cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        
        # Convert rows to dicts
        table_rows = []
        from decimal import Decimal
        for r in rows:
            row_dict = {}
            for col, val in zip(columns, r):
                if isinstance(val, Decimal):
                    val = float(val)
                elif hasattr(val, 'isoformat'):
                    val = val.isoformat()
                elif hasattr(val, 'strftime'):
                    val = str(val)
                row_dict[col] = val
            table_rows.append(row_dict)
            
        dump_data[table] = table_rows
        print(f"Dumped {len(table_rows)} rows from table '{table}'.")
        
    cursor.close()
    conn.close()
    
    seed_file = "api/core/db_seed_data.json"
    with open(seed_file, "w") as f:
        json.dump(dump_data, f, indent=2)
    print(f"Successfully wrote database seed data to {seed_file}!")

if __name__ == "__main__":
    dump_db_to_json()
