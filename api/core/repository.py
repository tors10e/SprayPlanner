import sqlite3
import pandas as pd
from typing import List, Dict, Set
from models.product import Product
from core.config import Config

class ProductRepository:
    def __init__(self, config: Config):
        self.config = config
        self.diseases = [
            "Anthracnose", "Black Rot", "Bitter Rot", "Botrytis", 
            "Downy", "Phomopsis", "Powdery"
        ]

    def load_products(self, include_all=False) -> List[Product]:
        conn = sqlite3.connect(self.config.database_file)
        
        # Load all products from the 'products' table
        query = "SELECT * FROM products"
        df = pd.read_sql_query(query, conn)
        conn.close()

        # Filtering out entries with 0 cost per dose unless include_all is True
        if not include_all:
            df = df[df['Cost/Dose'] > 0]

        products = []
        for _, row in df.iterrows():
            frac_codes = self._normalize_frac(row["FRAC"])
            is_multisite = any(f.upper() in self.config.multisite_fracs for f in frac_codes)
            
            effectiveness = {}
            for disease in self.diseases:
                # Effectiveness is already stored as lowercase in DB by migration script
                effectiveness[disease] = self.config.effectiveness_map.get(row[disease], 0.0)

            product = Product(
                name=row["Product"],
                frac_codes=frac_codes,
                cost_per_dose=float(row.get("Cost/Dose", 0.0)),
                phi=int(row["phi"]) if pd.notna(row["phi"]) else 0,
                max_applications=int(row["Max Applications"]) if pd.notna(row["Max Applications"]) else 999,
                effectiveness=effectiveness,
                is_multisite=is_multisite,
                primary_disease=row.get("Primary Disease", ""),
                omri=row.get("omri", ""),
                units=row.get("units", ""),
                price=float(row.get("Price", 0.0)),
                dose_avg=float(row.get("Dose (avg)", 0.0)),
                container_size=float(row.get("Container Size", 0.0))
            )
            products.append(product)
        
        return products

    def add_product(self, product_data: Dict):
        conn = sqlite3.connect(self.config.database_file)
        cursor = conn.cursor()
        
        # Remap keys for placeholders (sqlite doesn't like spaces or special chars in placeholder names)
        # We replace spaces, parentheses, and slashes with underscores
        remapped_data = {self._clean_key(k): v for k, v in product_data.items()}
        columns = [f"\"{k}\"" for k in product_data.keys()]
        placeholders = ":" + ", :".join(remapped_data.keys())
        sql = f"INSERT INTO products ({', '.join(columns)}) VALUES ({placeholders})"
        
        cursor.execute(sql, remapped_data)
        conn.commit()
        conn.close()

    def update_product(self, name: str, product_data: Dict):
        conn = sqlite3.connect(self.config.database_file)
        cursor = conn.cursor()
        
        # Use double quotes for column names to handle spaces (e.g., "Max Applications")
        set_clause = ", ".join([f"\"{col}\" = :{self._clean_key(col)}" for col in product_data.keys()])
        sql = f"UPDATE products SET {set_clause} WHERE Product = :old_name"
        
        # Remap keys for placeholders
        remapped_data = {self._clean_key(k): v for k, v in product_data.items()}
        remapped_data['old_name'] = name
        
        cursor.execute(sql, remapped_data)
        conn.commit()
        conn.close()

    def _clean_key(self, key: str) -> str:
        """Cleans a key to be used as a SQLite placeholder name."""
        return key.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')

    def delete_product(self, name: str):
        conn = sqlite3.connect(self.config.database_file)
        cursor = conn.cursor()
        sql = "DELETE FROM products WHERE Product = ?"
        cursor.execute(sql, (name,))
        conn.commit()
        conn.close()

    def _normalize_frac(self, frac_str: str) -> List[str]:
        if not frac_str:
            return []
        # Common separators handled in migration or original data
        frac_str = str(frac_str).strip().replace('+', ',').replace(' ', ',').replace(';', ',')
        parts = [p.strip().lower() for p in frac_str.split(',') if p.strip()]
        return [p for p in parts if p]
