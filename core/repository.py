import sqlite3
import pandas as pd
from typing import List, Dict, Set
from SprayPlanner.models.product import Product
from SprayPlanner.core.config import Config

class ProductRepository:
    def __init__(self, config: Config):
        self.config = config
        self.diseases = [
            "Anthracnose", "Black Rot", "Bitter Rot", "Botrytis", 
            "Downy", "Phomopsis", "Powdery"
        ]

    def load_products(self) -> List[Product]:
        conn = sqlite3.connect(self.config.database_file)
        
        # Load all products from the 'products' table
        query = "SELECT * FROM products"
        df = pd.read_sql_query(query, conn)
        conn.close()

        # Filtering out entries with 0 cost per dose
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
                cost_per_dose=float(row["Cost/Dose"]),
                phi=int(row["phi"]),
                max_applications=int(row["Max Applications"]),
                effectiveness=effectiveness,
                is_multisite=is_multisite
            )
            products.append(product)
        
        return products

    def _normalize_frac(self, frac_str: str) -> List[str]:
        if not frac_str:
            return []
        # Common separators handled in migration or original data
        frac_str = str(frac_str).strip().replace('+', ',').replace(' ', ',').replace(';', ',')
        parts = [p.strip().lower() for p in frac_str.split(',') if p.strip()]
        return [p for p in parts if p]
