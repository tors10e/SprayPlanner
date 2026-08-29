import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from core.config import Config
from core.repository import ProductRepository
from core.history_repository import SprayHistoryRepository
from constraints.phi_constraint import PHIConstraint
from constraints.frac_rotation_constraint import FRACRotationConstraint
from constraints.max_application_constraint import MaxApplicationConstraint
from constraints.oil_sulfur_constraint import OilSulfurConstraint
from constraints.multi_year_rotation_constraint import MultiYearRotationConstraint
from services.scheduler import Scheduler
from services.mix_builder import MixBuilder
from services.planner import Planner
from datetime import datetime, timedelta
from core.weather import get_block_weather_info
import os
import io
import pandas as pd

app = Flask(__name__)
CORS(app)

config = Config()
repo = ProductRepository(config)
history_repo = SprayHistoryRepository(config)


@app.route('/api/products', methods=['GET'])
def get_products():
    products = repo.load_products(include_all=True)
    return jsonify([{
        'Product': p.name,
        'Primary Disease': p.primary_disease,
        'FRAC': ",".join(p.frac_codes),
        'omri': p.omri,
        'phi': p.phi,
        'Max Applications': p.max_applications,
        'Container Size': p.container_size,
        'units': p.units,
        'Price': p.price,
        'Dose (avg)': p.dose_avg,
        'Cost/Dose': p.cost_per_dose,
        'package_size': p.package_size,
        'price_source': p.price_source,
        'label_url': p.label_url,
        'rei': p.rei,
        'ppe_long_sleeves_pants': p.ppe_long_sleeves_pants,
        'ppe_socks_shoes': p.ppe_socks_shoes,
        'ppe_waterproof_gloves': p.ppe_waterproof_gloves,
        'ppe_protective_eyewear': p.ppe_protective_eyewear,
        'min_rate': p.min_rate,
        'max_rate': p.max_rate,
        'EPA No': p.epa_no,
        'Active Ingredient': p.active_ingredient,
        'Singal Word': p.signal_word,
        'effectiveness': p.effectiveness
    } for p in products])

@app.route('/api/volume_units', methods=['GET'])
def get_volume_units():
    try:
        conn = repo._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT unit FROM volume_units ORDER BY unit')
        units = [r[0] for r in cursor.fetchall()]
        cursor.close()
        conn.close()
        return jsonify(units)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/products/<name>', methods=['PUT'])
def update_product(name):
    try:
        data = request.json
        if 'effectiveness' in data:
            eff = data.pop('effectiveness')
            data.update(eff)

        valid_keys = [
            "Product", "Primary Disease", "FRAC", "omri", "phi",
            "Max Applications", "Container Size", "units", "Price",
            "Dose (avg)", "Cost/Dose", "Anthracnose", "Black Rot",
            "Bitter Rot", "Botrytis", "Downy", "Phomopsis", "Powdery",
            "package_size", "price_source", "label_url", "rei",
            "ppe_long_sleeves_pants", "ppe_socks_shoes",
            "ppe_waterproof_gloves", "ppe_protective_eyewear",
            "min_rate", "max_rate", "EPA No", "Active Ingredient", "Singal Word"
        ]
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        
        repo.update_product(name, filtered_data)
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error updating product: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/products', methods=['POST'])
def add_product():
    try:
        data = request.json
        # Flatten effectiveness if it's in the data
        if 'effectiveness' in data:
            eff = data.pop('effectiveness')
            data.update(eff)
        
        # Filter only keys that exist in the database
        valid_keys = [
            "Product", "Primary Disease", "FRAC", "omri", "phi",
            "Max Applications", "Container Size", "units", "Price",
            "Dose (avg)", "Cost/Dose", "Anthracnose", "Black Rot",
            "Bitter Rot", "Botrytis", "Downy", "Phomopsis", "Powdery",
            "package_size", "price_source", "label_url", "rei",
            "ppe_long_sleeves_pants", "ppe_socks_shoes",
            "ppe_waterproof_gloves", "ppe_protective_eyewear",
            "min_rate", "max_rate", "EPA No", "Active Ingredient", "Singal Word"
        ]
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        
        repo.add_product(filtered_data)
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error adding product: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/products/<name>', methods=['DELETE'])
def delete_product(name):
    replacement = request.args.get('replacement')
    try:
        conn = repo._get_connection()
        cursor = conn.cursor()
        
        # Check references count in spray_history
        cursor.execute('SELECT COUNT(*) FROM spray_history WHERE "Pesticide" = %s', (name,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            if not replacement:
                cursor.close()
                conn.close()
                return jsonify({
                    'status': 'conflict',
                    'message': f'Product "{name}" is referenced in {count} spray history entries.',
                    'usage_count': count
                }), 409
            else:
                # Verify that replacement exists in products
                cursor.execute('SELECT EXISTS(SELECT 1 FROM products WHERE "Product" = %s)', (replacement,))
                exists = cursor.fetchone()[0]
                if not exists:
                    cursor.close()
                    conn.close()
                    return jsonify({
                        'status': 'error',
                        'message': f'Replacement product "{replacement}" does not exist.'
                    }), 400
                
                # Remap in a single transaction
                cursor.execute('UPDATE spray_history SET "Pesticide" = %s WHERE "Pesticide" = %s', (replacement, name))
                cursor.execute('DELETE FROM products WHERE "Product" = %s', (name,))
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({'status': 'success'})
        else:
            # Standard deletion
            cursor.close()
            conn.close()
            repo.delete_product(name)
            return jsonify({'status': 'success'})
            
    except Exception as e:
        print(f"Error deleting product: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# --- Spray History Endpoints ---

@app.route('/api/history', methods=['GET'])
def get_history():
    entries = history_repo.load_history()
    return jsonify([e.to_dict() for e in entries])

@app.route('/api/history', methods=['POST'])
def add_history_entry():
    try:
        data = request.json
        new_id = history_repo.add_entry(data)
        return jsonify({'status': 'success', 'id': new_id})
    except Exception as e:
        print(f"Error adding history entry: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/history/<int:entry_id>', methods=['PUT'])
def update_history_entry(entry_id):
    try:
        data = request.json
        history_repo.update_entry(entry_id, data)
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error updating history entry: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/history/<int:entry_id>', methods=['DELETE'])
def delete_history_entry(entry_id):
    try:
        history_repo.delete_entry(entry_id)
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error deleting history entry: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/history/upload', methods=['POST'])
def upload_history():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400
    if file and file.filename.endswith('.csv'):
        try:
            stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
            df = pd.read_csv(stream)
            df.columns = df.columns.str.strip()
            
            # Column normalization: "Signal Word" -> "Singal Word" and "Block" -> "Block "
            column_mapping = {
                "Signal Word": "Singal Word",
                "Block": "Block "
            }
            for k, v in column_mapping.items():
                if k in df.columns and v not in df.columns:
                    df[v] = df[k]
                    
            valid_cols = history_repo.columns
            records = []
            for _, row in df.iterrows():
                record = {}
                for col in valid_cols:
                    if col in df.columns:
                        val = row[col]
                        if pd.isna(val):
                            val = None
                        record[col] = val
                records.append(record)
                
            inserted_count = history_repo.bulk_add_entries(records)
            return jsonify({'status': 'success', 'inserted': inserted_count})
        except Exception as e:
            print(f"Error parsing CSV upload: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    return jsonify({'status': 'error', 'message': 'Invalid file type, only CSV allowed'}), 400

@app.route('/api/history/save_group', methods=['POST'])
def save_history_group():
    try:
        data = request.json
        event_id = data.get("event_id")
        block_event_id = data.get("block_event_id")
        spray_number = data.get("spray_number")
        block = data.get("block")
        date = data.get("date")
        end_time = data.get("end_time")
        liters_acre = data.get("liters_acre")
        
        rows = data.get("rows", [])
        
        # Normalize empty values to None/NULL
        clean_spray_number = None if spray_number == "" or spray_number is None else int(spray_number)
        clean_block = None if block == "" or block is None else block
        clean_date = None if date == "" or date is None else date
        clean_end_time = None if end_time == "" or end_time is None else end_time
        clean_liters_acre = None if liters_acre == "" or liters_acre is None else float(liters_acre)
        
        # Start transactional block
        conn = history_repo._get_connection()
        cursor = conn.cursor()
        try:
            # 1. Resolve parent spray_events row
            if clean_spray_number is not None:
                cursor.execute('SELECT id FROM spray_events WHERE "Spray #" = %s', (clean_spray_number,))
                row = cursor.fetchone()
                if row:
                    target_event_id = row[0]
                else:
                    cursor.execute('INSERT INTO spray_events ("Spray #") VALUES (%s) RETURNING id', (clean_spray_number,))
                    target_event_id = cursor.fetchone()[0]
            else:
                # Unscheduled: Create a new parent event row
                cursor.execute('INSERT INTO spray_events ("Spray #") VALUES (NULL) RETURNING id')
                target_event_id = cursor.fetchone()[0]
                
            # 2. Find or create the block application row
            block_application_id = data.get("block_application_id") or data.get("block_event_id")
            if block_application_id is not None:
                # Update existing block application
                cursor.execute(
                    'UPDATE block_applications SET event_id = %s, "Block " = %s, "Date" = %s, "End Time" = %s, "Liters/Acre" = %s WHERE id = %s',
                    (target_event_id, clean_block, clean_date, clean_end_time, clean_liters_acre, int(block_application_id))
                )
                actual_block_application_id = int(block_application_id)
                # Clear old chemicals
                cursor.execute('DELETE FROM spray_history WHERE block_application_id = %s', (actual_block_application_id,))
            else:
                # Insert new block application
                cursor.execute(
                    'INSERT INTO block_applications (event_id, "Block ", "Date", "End Time", "Liters/Acre") VALUES (%s, %s, %s, %s, %s) RETURNING id',
                    (target_event_id, clean_block, clean_date, clean_end_time, clean_liters_acre)
                )
                actual_block_application_id = cursor.fetchone()[0]
            
            # 3. Insert new/updated chemical rows in spray_history
            for row in rows:
                # Make sure the chemical product reference exists/is upserted
                history_repo._upsert_product_reference(cursor, row)
                
                # Build insertion columns and placeholders
                remapped_data = {history_repo._clean_key(k): history_repo._normalize_val(v) for k, v in row.items() if k in history_repo.columns}
                remapped_data['block_application_id'] = actual_block_application_id
                for col in history_repo.columns:
                    cleaned = history_repo._clean_key(col)
                    if cleaned not in remapped_data:
                        remapped_data[cleaned] = None
                        
                columns_sql = "block_application_id, " + ", ".join([f'"{c}"' for c in history_repo.columns])
                placeholders_sql = "%(block_application_id)s, " + ", ".join([f"%({history_repo._clean_key(c)})s" for c in history_repo.columns])
                sql = f"INSERT INTO spray_history ({columns_sql}) VALUES ({placeholders_sql})"
                
                cursor.execute(sql, remapped_data)
                
            # 4. Clean up any empty parent spray_events (which have no block_applications left)
            cursor.execute('DELETE FROM spray_events WHERE id NOT IN (SELECT DISTINCT event_id FROM block_applications)')
                
            conn.commit()
            return jsonify({'status': 'success'})
        except Exception as ex:
            conn.rollback()
            raise ex
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"Error saving history group: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/history/delete_event', methods=['POST'])
def delete_history_event():
    try:
        data = request.json
        block_application_id = data.get("block_application_id") or data.get("block_event_id")
        
        conn = history_repo._get_connection()
        cursor = conn.cursor()
        
        if block_application_id is not None:
            cursor.execute('DELETE FROM block_applications WHERE id = %s', (int(block_application_id),))
        else:
            # Fallback to block details lookup
            spray_number = data.get("spray_number")
            block = data.get("block")
            date = data.get("date")
            end_time = data.get("end_time")
            
            clean_spray_number = None if spray_number == "" or spray_number is None else int(spray_number)
            clean_block = None if block == "" or block is None else block
            clean_date = None if date == "" or date is None else date
            clean_end_time = None if end_time == "" or end_time is None else end_time
            
            cursor.execute("""
                DELETE FROM block_applications 
                WHERE id IN (
                    SELECT b.id 
                    FROM block_applications b
                    INNER JOIN spray_events e ON b.event_id = e.id
                    WHERE e."Spray #" IS NOT DISTINCT FROM %s
                      AND b."Block " IS NOT DISTINCT FROM %s
                      AND b."Date" IS NOT DISTINCT FROM %s
                      AND b."End Time" IS NOT DISTINCT FROM %s
                )
            """, (clean_spray_number, clean_block, clean_date, clean_end_time))
            
        # Clean up empty parent spray_events
        cursor.execute('DELETE FROM spray_events WHERE id NOT IN (SELECT DISTINCT event_id FROM block_applications)')
            
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error deleting history application: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/history/update_spray_number', methods=['POST'])
def update_spray_number():
    try:
        data = request.json
        old_number = data.get("old_number")
        new_number = data.get("new_number")
        
        if old_number is None or new_number is None:
            return jsonify({'status': 'error', 'message': 'Missing old_number or new_number'}), 400
            
        conn = history_repo._get_connection()
        cursor = conn.cursor()
        
        clean_old = None if old_number == "" or old_number is None else int(old_number)
        clean_new = None if new_number == "" or new_number is None else int(new_number)
        
        # Merge logic to handle Spray Number uniqueness constraint
        cursor.execute('SELECT id FROM spray_events WHERE "Spray #" = %s', (clean_new,))
        new_row = cursor.fetchone()
        
        cursor.execute('SELECT id FROM spray_events WHERE "Spray #" = %s', (clean_old,))
        old_row = cursor.fetchone()
        
        if old_row:
            old_event_id = old_row[0]
            if new_row:
                new_event_id = new_row[0]
                # Merge old blocks under new parent event
                cursor.execute(
                    'UPDATE block_applications SET event_id = %s WHERE event_id = %s',
                    (new_event_id, old_event_id)
                )
                cursor.execute('DELETE FROM spray_events WHERE id = %s', (old_event_id,))
            else:
                # Rename parent event
                cursor.execute(
                    'UPDATE spray_events SET "Spray #" = %s WHERE id = %s',
                    (clean_new, old_event_id)
                )
        
        # Clean up empty parent spray_events
        cursor.execute('DELETE FROM spray_events WHERE id NOT IN (SELECT DISTINCT event_id FROM block_applications)')
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error updating spray number: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/history/clone_spray_group', methods=['POST'])
def clone_spray_group():
    try:
        data = request.json
        source_event_id = data.get("source_event_id")
        new_spray_number = data.get("new_spray_number")
        
        if not source_event_id or new_spray_number is None:
            return jsonify({'status': 'error', 'message': 'Missing source_event_id or new_spray_number'}), 400
            
        clean_new = int(new_spray_number)
        
        conn = history_repo._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT id FROM spray_events WHERE "Spray #" = %s', (clean_new,))
            target_row = cursor.fetchone()
            if target_row:
                return jsonify({'status': 'error', 'message': f'Spray #{clean_new} already exists. Please choose a different target number.'}), 400
                
            cursor.execute('INSERT INTO spray_events ("Spray #") VALUES (%s) RETURNING id', (clean_new,))
            target_event_id = cursor.fetchone()[0]
                
            cursor.execute('SELECT id, "Block ", "Date", "End Time", "Liters/Acre" FROM block_applications WHERE event_id = %s', (source_event_id,))
            blocks = cursor.fetchall()
            
            for old_block_id, block_name, date, end_time, liters_acre in blocks:
                cursor.execute(
                    'SELECT id FROM block_applications WHERE event_id = %s AND "Block " IS NOT DISTINCT FROM %s',
                    (target_event_id, block_name)
                )
                existing_block_row = cursor.fetchone()
                if existing_block_row:
                    new_block_application_id = existing_block_row[0]
                    cursor.execute('DELETE FROM spray_history WHERE block_application_id = %s', (new_block_application_id,))
                else:
                    cursor.execute(
                        'INSERT INTO block_applications (event_id, "Block ", "Date", "End Time", "Liters/Acre") VALUES (%s, %s, %s, %s, %s) RETURNING id',
                        (target_event_id, block_name, date, end_time, liters_acre)
                    )
                    new_block_application_id = cursor.fetchone()[0]
                    
                cursor.execute("""
                    SELECT "Pesticide", "Dose/acre", "Dose per L @150 l", "Calculated Dose", "Dose Units", "Notes", "PHI Date", "REI_TIME"
                    FROM spray_history
                    WHERE block_application_id = %s
                """, (old_block_id,))
                chemicals = cursor.fetchall()
                
                for chem in chemicals:
                    cursor.execute("""
                        INSERT INTO spray_history (
                            block_application_id, "Pesticide", "Dose/acre", 
                            "Dose per L @150 l", "Calculated Dose", "Dose Units", 
                            "Notes", "PHI Date", "REI_TIME"
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (new_block_application_id, *chem))
                    
            conn.commit()
            return jsonify({'status': 'success'})
        except Exception as ex:
            conn.rollback()
            raise ex
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"Error cloning spray group: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/history/delete_spray_group', methods=['POST'])
def delete_spray_group():
    try:
        data = request.json
        event_id = data.get("event_id")
        
        if not event_id:
            return jsonify({'status': 'error', 'message': 'Missing event_id'}), 400
            
        conn = history_repo._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM spray_events WHERE id = %s', (int(event_id),))
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error deleting spray group: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/planner/generate', methods=['POST'])
def generate_spray_plan():
    try:
        data = request.json or {}
        years = data.get("years", [2026])
        organic_only = data.get("organic_only", False)
        default_interval = int(data.get("default_interval", 14))
        start_date_month_day = data.get("start_date_month_day", "04-01")
        end_date_month_day = data.get("end_date_month_day", "10-20")
        total_acres = float(data.get("total_acres", config.total_acres))
        
        temp_config = Config()
        temp_config.total_acres = total_acres
        temp_config.default_interval = default_interval
        
        product_repo = ProductRepository(temp_config)
        products = product_repo.load_products()
        
        if organic_only:
            products = [p for p in products if str(p.omri) == '1']
            
        constraints = [
            PHIConstraint(temp_config),
            FRACRotationConstraint(temp_config),
            MaxApplicationConstraint(),
            OilSulfurConstraint(),
            MultiYearRotationConstraint()
        ]
        
        mix_builder = MixBuilder(temp_config, constraints)
        planner = Planner(temp_config, mix_builder)
        
        multi_year_plan = {}
        history = {
            "multi_year_history": {}
        }
        
        for year in years:
            temp_config.start_date = f"{year}-{start_date_month_day}"
            temp_config.end_date = f"{year}-{end_date_month_day}"
            temp_config.harvest_date = datetime(year, 9, 20)
            
            scheduler = Scheduler(temp_config)
            schedule = scheduler.build_schedule()
            
            plan = planner.optimize_season(schedule, products, initial_history=history)
            multi_year_plan[year] = plan
            
        return jsonify({
            'status': 'success',
            'plans': multi_year_plan
        })
    except Exception as e:
        print(f"Error generating spray plan: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# GIS Helper functions for PostGIS coordinate serialization/deserialization
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

def wkt_or_geojson_to_coords(geometry_data):
    if not geometry_data:
        return []
    try:
        if isinstance(geometry_data, str):
            if geometry_data.startswith("{"):
                geo = json.loads(geometry_data)
                raw_coords = geo.get("coordinates", [[]])[0]
                if raw_coords and len(raw_coords) > 1:
                    return [[p[1], p[0]] for p in raw_coords[:-1]]
            elif geometry_data.upper().startswith("POLYGON"):
                clean = geometry_data.replace("POLYGON", "").replace("polygon", "").strip("() ")
                pts = [list(map(float, pt.strip().split())) for pt in clean.split(",")]
                if pts and len(pts) > 1:
                    return [[p[1], p[0]] for p in pts[:-1]]
        elif isinstance(geometry_data, dict):
            raw_coords = geometry_data.get("coordinates", [[]])[0]
            if raw_coords and len(raw_coords) > 1:
                return [[p[1], p[0]] for p in raw_coords[:-1]]
    except Exception as e:
        print(f"Error parsing geometry data: {e}")
    return []

@app.route('/api/blocks', methods=['GET'])
def get_vineyard_blocks():
    try:
        conn = repo._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                block_code, varieties, acres, vine_spacing, row_spacing, trellis_type, rootstock,
                ST_AsGeoJSON(block_area) as block_area,
                ST_Y(ST_Centroid(block_area)) as centroid_lat,
                ST_X(ST_Centroid(block_area)) as centroid_lng
            FROM vineyard_blocks 
            ORDER BY block_code
        ''')
        blocks = cursor.fetchall()
        
        result = []
        for b in blocks:
            bcode = b[0]
            cursor.execute('SELECT row_number, row_length FROM vineyard_rows WHERE block_code = %s ORDER BY row_number', (bcode,))
            rows = [{"row_number": r[0], "row_length": r[1]} for r in cursor.fetchall()]
            
            block_area_coords = wkt_or_geojson_to_coords(b[7])
            centroid_lat = b[8]
            centroid_lng = b[9]
            centroid = [centroid_lat, centroid_lng] if centroid_lat is not None and centroid_lng is not None else None
            
            result.append({
                "block_code": b[0],
                "varieties": b[1],
                "acres": b[2],
                "vine_spacing": b[3],
                "row_spacing": b[4],
                "trellis_type": b[5],
                "rootstock": b[6],
                "block_area": block_area_coords,
                "centroid": centroid,
                "rows": rows
            })
        
        cursor.close()
        conn.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/blocks', methods=['POST'])
def add_vineyard_block():
    try:
        data = request.json
        bcode = data.get("block_code")
        if not bcode:
            return jsonify({'status': 'error', 'message': 'Block code is required'}), 400
            
        conn = repo._get_connection()
        cursor = conn.cursor()
        
        # Check duplicate block code
        cursor.execute('SELECT block_code FROM vineyard_blocks WHERE LOWER(block_code) = LOWER(%s)', (bcode,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'status': 'error', 'message': f"Block '{bcode}' already exists"}), 400

        wkt = coords_to_wkt_polygon(data.get("block_area"))

        cursor.execute(
            '''
            INSERT INTO vineyard_blocks (block_code, varieties, acres, vine_spacing, row_spacing, trellis_type, rootstock, block_area) 
            VALUES (%s, %s, COALESCE(ST_Area(ST_GeomFromText(%s, 4326)::geography) / 4046.8564224, %s), %s, %s, %s, %s, ST_GeomFromText(%s, 4326))
            ''',
            (
                bcode,
                data.get("varieties"),
                wkt,
                data.get("acres"),
                data.get("vine_spacing"),
                data.get("row_spacing"),
                data.get("trellis_type"),
                data.get("rootstock"),
                wkt
            )
        )
        
        rows = data.get("rows", [])
        for r in rows:
            cursor.execute(
                'INSERT INTO vineyard_rows (block_code, row_number, row_length) VALUES (%s, %s, %s)',
                (bcode, r.get("row_number"), r.get("row_length"))
            )
            
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/blocks/<block_code>', methods=['PUT'])
def update_vineyard_block(block_code):
    try:
        data = request.json
        new_bcode = data.get("block_code", block_code)
        
        conn = repo._get_connection()
        cursor = conn.cursor()
        
        wkt = coords_to_wkt_polygon(data.get("block_area"))

        cursor.execute(
            '''
            UPDATE vineyard_blocks 
            SET block_code=%s, varieties=%s, 
                acres=COALESCE(ST_Area(ST_GeomFromText(%s, 4326)::geography) / 4046.8564224, %s), 
                vine_spacing=%s, row_spacing=%s, trellis_type=%s, rootstock=%s, 
                block_area=ST_GeomFromText(%s, 4326) 
            WHERE block_code=%s
            ''',
            (
                new_bcode,
                data.get("varieties"),
                wkt,
                data.get("acres"),
                data.get("vine_spacing"),
                data.get("row_spacing"),
                data.get("trellis_type"),
                data.get("rootstock"),
                wkt,
                block_code
            )
        )
        
        cursor.execute('DELETE FROM vineyard_rows WHERE block_code = %s', (new_bcode,))
        rows = data.get("rows", [])
        for r in rows:
            cursor.execute(
                'INSERT INTO vineyard_rows (block_code, row_number, row_length) VALUES (%s, %s, %s)',
                (new_bcode, r.get("row_number"), r.get("row_length"))
            )
            
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Helper to parse dates
def parse_date_api(date_str):
    if not date_str:
        return None
    for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d', '%m/%d/%y'):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None

@app.route('/api/settings', methods=['GET'])
def get_settings():
    try:
        conn = repo._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM system_settings")
        settings = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.close()
        conn.close()
        return jsonify(settings)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/settings', methods=['PUT'])
def update_settings():
    try:
        data = request.json
        conn = repo._get_connection()
        cursor = conn.cursor()
        for k, v in data.items():
            cursor.execute(
                "INSERT INTO system_settings (key, value) VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
                (k, str(v))
            )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/recommendations', methods=['GET'])
def get_spray_recommendations():
    try:
        conn = repo._get_connection()
        cursor = conn.cursor()
        
        # 1. Fetch system settings
        cursor.execute("SELECT key, value FROM system_settings")
        settings = {row[0]: row[1] for row in cursor.fetchall()}
        
        min_int = int(settings.get("min_spray_interval", 7))
        max_int = int(settings.get("max_spray_interval", 14))
        rain_thresh = float(settings.get("rain_threshold_inch", 1.0))
        min_rain_free = int(settings.get("min_rain_free_hours", 12))
        provider = settings.get("weather_provider", "NOAA")
        w_api_key = settings.get("wunderground_api_key", "")
        w_station_id = settings.get("wunderground_station_id", "KGALAKEM20")
        
        # 2. Fetch all blocks
        cursor.execute("""
            SELECT block_code, ST_Y(ST_Centroid(block_area)), ST_X(ST_Centroid(block_area)) 
            FROM vineyard_blocks 
            ORDER BY block_code
        """)
        blocks = cursor.fetchall()
        
        results = []
        today = datetime.now().date()
        
        for bcode, centroid_lat, centroid_lng in blocks:
            # Default location: Clarkesville, GA
            lat = centroid_lat if centroid_lat is not None else 34.7333066
            lng = centroid_lng if centroid_lng is not None else -83.5026561
            
            # Fetch last spray date for this block
            cursor.execute("""
                SELECT MAX(be."Date") 
                FROM block_applications be
                JOIN spray_events se ON be.event_id = se.id
                WHERE be."Block " = %s
            """, (bcode,))
            last_date_str = cursor.fetchone()[0]
            
            last_date = parse_date_api(last_date_str) if last_date_str else None
            
            if not last_date:
                results.append({
                    "block_code": bcode,
                    "last_spray_date": None,
                    "days_since_last_spray": None,
                    "rain_since_last_spray": 0.0,
                    "recommended_date": today.strftime("%Y-%m-%d"),
                    "reason": "No previous spray event recorded in logs. Recommended to spray immediately.",
                    "provider_source": "N/A"
                })
                continue
                
            last_date = last_date.date()
            days_since = (today - last_date).days
            
            # Fetch weather forecast and history starting from the day after the last spray
            start_fetch_date = (last_date + timedelta(days=1)).strftime("%Y-%m-%d")
            weather = get_block_weather_info(
                lat=lat,
                lng=lng,
                start_date_str=start_fetch_date,
                provider=provider,
                wunderground_api_key=w_api_key,
                wunderground_station_id=w_station_id
            )
            
            hist_rain = weather.get("historical_rain", 0.0)
            forecast = weather.get("forecast", [])
            source = weather.get("source", "NOAA")
            
            rec_date = None
            reason = ""
            
            # Recommendation Logic
            # Rule A: Cumulative rain has reached 1" since previous spray
            if hist_rain >= rain_thresh:
                # Find the next rain-free window of >= min_rain_free hours.
                # In daily forecast, we find the first day starting today that has qpf == 0.
                rain_free_day = None
                for f in forecast:
                    f_date = datetime.strptime(f["date"], "%Y-%m-%d").date()
                    if f_date >= today:
                        # Assuming qpf == 0 is rain free (provides at least 24h window)
                        if f.get("qpf", 0.0) == 0.0:
                            rain_free_day = f_date
                            break
                            
                if rain_free_day:
                    rec_date = rain_free_day
                    reason = f"Rain threshold ({rain_thresh:.1f}\") exceeded: {hist_rain:.2f}\" accumulated since previous spray. Next rain-free day with >= {min_rain_free}h dry window is recommended."
                else:
                    # Fallback to tomorrow if no rain-free day in forecast
                    rec_date = today + timedelta(days=1)
                    reason = f"Rain threshold ({rain_thresh:.1f}\") exceeded: {hist_rain:.2f}\" accumulated. High precipitation in upcoming forecast. Spray as soon as window permits."
            else:
                # Rule B: Forecast shows rain in the min_int to max_int day window
                rain_forecast_day = None
                min_int_date = last_date + timedelta(days=min_int)
                max_int_date = last_date + timedelta(days=max_int)
                
                for f in forecast:
                    f_date = datetime.strptime(f["date"], "%Y-%m-%d").date()
                    if min_int_date <= f_date <= max_int_date:
                        # If rain is coming (QPF > 0.1" or high chance)
                        if f.get("qpf", 0.0) > 0.1 or f.get("rain_chance", 0) >= 40:
                            rain_forecast_day = f_date
                            break
                            
                if rain_forecast_day:
                    # Recommended date is the day before the rain starts (or min_int_date if that pushes it too early)
                    target_date = rain_forecast_day - timedelta(days=1)
                    if target_date < min_int_date:
                        target_date = min_int_date
                    rec_date = target_date
                    reason = f"Rain forecasted on {rain_forecast_day.strftime('%m/%d/%Y')}. Recommended to spray before rain on {rec_date.strftime('%m/%d/%Y')} to protect foliage."
                else:
                    # Rule C: If dry, no rain, and no dew issues, push to max_int
                    # Check if dew is forecasted on max_int day
                    dew_on_max_day = False
                    for f in forecast:
                        f_date = datetime.strptime(f["date"], "%Y-%m-%d").date()
                        if f_date == max_int_date:
                            if f.get("has_dew", False):
                                dew_on_max_day = True
                                
                    if dew_on_max_day:
                        # Pull back by 1 day if dew is forecasted on the max interval day
                        rec_date = max_int_date - timedelta(days=1)
                        if rec_date < min_int_date:
                            rec_date = min_int_date
                        reason = f"Dry conditions. Dew predicted on max interval day. Pushed out to {rec_date.strftime('%m/%d/%Y')}."
                    else:
                        rec_date = max_int_date
                        reason = f"Dry conditions and no rain forecasted. Next spray pushed out to maximum interval."
            
            # Default fallback safety checks
            if not rec_date:
                rec_date = last_date + timedelta(days=min_int)
                reason = "Recommended spray date at standard interval."
                
            if rec_date < today:
                # If calculated date is in the past, recommend spraying today or as soon as possible
                rec_date = today
                reason = f"Interval exceeded ({days_since} days since last spray). Spray as soon as possible."
                
            results.append({
                "block_code": bcode,
                "last_spray_date": last_date.strftime("%Y-%m-%d"),
                "days_since_last_spray": days_since,
                "rain_since_last_spray": round(hist_rain, 2),
                "recommended_date": rec_date.strftime("%Y-%m-%d"),
                "reason": reason,
                "provider_source": source
            })
            
        cursor.close()
        conn.close()
        return jsonify(results)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
@app.route('/api/blocks/<block_code>', methods=['DELETE'])
def delete_vineyard_block(block_code):
    try:
        conn = repo._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM vineyard_blocks WHERE block_code = %s', (block_code,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
