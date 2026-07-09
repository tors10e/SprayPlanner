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
from datetime import datetime
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
    repo.delete_product(name)
    return jsonify({'status': 'success'})

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
                
            # 2. Find or create the block event row
            if block_event_id is not None:
                # Update existing block event
                cursor.execute(
                    'UPDATE block_events SET event_id = %s, "Block " = %s, "Date" = %s, "End Time" = %s, "Liters/Acre" = %s WHERE id = %s',
                    (target_event_id, clean_block, clean_date, clean_end_time, clean_liters_acre, int(block_event_id))
                )
                actual_block_event_id = int(block_event_id)
                # Clear old chemicals
                cursor.execute('DELETE FROM spray_history WHERE block_event_id = %s', (actual_block_event_id,))
            else:
                # Insert new block event
                cursor.execute(
                    'INSERT INTO block_events (event_id, "Block ", "Date", "End Time", "Liters/Acre") VALUES (%s, %s, %s, %s, %s) RETURNING id',
                    (target_event_id, clean_block, clean_date, clean_end_time, clean_liters_acre)
                )
                actual_block_event_id = cursor.fetchone()[0]
            
            # 3. Insert new/updated chemical rows in spray_history
            for row in rows:
                # Make sure the chemical product reference exists/is upserted
                history_repo._upsert_product_reference(cursor, row)
                
                # Build insertion columns and placeholders
                remapped_data = {history_repo._clean_key(k): history_repo._normalize_val(v) for k, v in row.items() if k in history_repo.columns}
                remapped_data['block_event_id'] = actual_block_event_id
                for col in history_repo.columns:
                    cleaned = history_repo._clean_key(col)
                    if cleaned not in remapped_data:
                        remapped_data[cleaned] = None
                        
                columns_sql = "block_event_id, " + ", ".join([f'"{c}"' for c in history_repo.columns])
                placeholders_sql = "%(block_event_id)s, " + ", ".join([f"%({history_repo._clean_key(c)})s" for c in history_repo.columns])
                sql = f"INSERT INTO spray_history ({columns_sql}) VALUES ({placeholders_sql})"
                
                cursor.execute(sql, remapped_data)
                
            # 4. Clean up any empty parent spray_events (which have no block_events left)
            cursor.execute('DELETE FROM spray_events WHERE id NOT IN (SELECT DISTINCT event_id FROM block_events)')
                
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
        block_event_id = data.get("block_event_id")
        
        conn = history_repo._get_connection()
        cursor = conn.cursor()
        
        if block_event_id is not None:
            cursor.execute('DELETE FROM block_events WHERE id = %s', (int(block_event_id),))
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
                DELETE FROM block_events 
                WHERE id IN (
                    SELECT b.id 
                    FROM block_events b
                    INNER JOIN spray_events e ON b.event_id = e.id
                    WHERE e."Spray #" IS NOT DISTINCT FROM %s
                      AND b."Block " IS NOT DISTINCT FROM %s
                      AND b."Date" IS NOT DISTINCT FROM %s
                      AND b."End Time" IS NOT DISTINCT FROM %s
                )
            """, (clean_spray_number, clean_block, clean_date, clean_end_time))
            
        # Clean up empty parent spray_events
        cursor.execute('DELETE FROM spray_events WHERE id NOT IN (SELECT DISTINCT event_id FROM block_events)')
            
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error deleting history event: {e}")
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
                    'UPDATE block_events SET event_id = %s WHERE event_id = %s',
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
        cursor.execute('DELETE FROM spray_events WHERE id NOT IN (SELECT DISTINCT event_id FROM block_events)')
        
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
                target_event_id = target_row[0]
            else:
                cursor.execute('INSERT INTO spray_events ("Spray #") VALUES (%s) RETURNING id', (clean_new,))
                target_event_id = cursor.fetchone()[0]
                
            cursor.execute('SELECT id, "Block ", "Date", "End Time", "Liters/Acre" FROM block_events WHERE event_id = %s', (source_event_id,))
            blocks = cursor.fetchall()
            
            for old_block_id, block_name, date, end_time, liters_acre in blocks:
                cursor.execute(
                    'SELECT id FROM block_events WHERE event_id = %s AND "Block " IS NOT DISTINCT FROM %s',
                    (target_event_id, block_name)
                )
                existing_block_row = cursor.fetchone()
                if existing_block_row:
                    new_block_event_id = existing_block_row[0]
                    cursor.execute('DELETE FROM spray_history WHERE block_event_id = %s', (new_block_event_id,))
                else:
                    cursor.execute(
                        'INSERT INTO block_events (event_id, "Block ", "Date", "End Time", "Liters/Acre") VALUES (%s, %s, %s, %s, %s) RETURNING id',
                        (target_event_id, block_name, date, end_time, liters_acre)
                    )
                    new_block_event_id = cursor.fetchone()[0]
                    
                cursor.execute("""
                    SELECT "Pesticide", "Dose/acre", "Dose per L @150 l", "Calculated Dose", "Dose Units", "Notes", "PHI Date", "REI_TIME"
                    FROM spray_history
                    WHERE block_event_id = %s
                """, (old_block_id,))
                chemicals = cursor.fetchall()
                
                for chem in chemicals:
                    cursor.execute("""
                        INSERT INTO spray_history (
                            block_event_id, "Pesticide", "Dose/acre", 
                            "Dose per L @150 l", "Calculated Dose", "Dose Units", 
                            "Notes", "PHI Date", "REI_TIME"
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (new_block_event_id, *chem))
                    
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

if __name__ == '__main__':
    app.run(debug=True, port=5001)

