from flask import Flask, request, jsonify
from flask_cors import CORS
from core.config import Config
from core.repository import ProductRepository
from core.history_repository import SprayHistoryRepository
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

if __name__ == '__main__':
    app.run(debug=True, port=5001)

