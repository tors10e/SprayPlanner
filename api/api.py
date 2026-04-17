from flask import Flask, request, jsonify
from flask_cors import CORS
from core.config import Config
from core.repository import ProductRepository
import os

app = Flask(__name__)
CORS(app)

config = Config()
repo = ProductRepository(config)

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
            "Bitter Rot", "Botrytis", "Downy", "Phomopsis", "Powdery"
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
            "Bitter Rot", "Botrytis", "Downy", "Phomopsis", "Powdery"
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

if __name__ == '__main__':
    app.run(debug=True, port=5001)
