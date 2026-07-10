import psycopg2
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

    def _get_connection(self):
        if self.config.database_url:
            return psycopg2.connect(self.config.database_url)
        return psycopg2.connect(
            host=self.config.db_host,
            port=self.config.db_port,
            database=self.config.db_name,
            user=self.config.db_user,
            password=self.config.db_password
        )

    def load_products(self, include_all=False) -> List[Product]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Load all products from the 'products' table ordered alphabetically
        query = "SELECT * FROM products ORDER BY LOWER(\"Product\") ASC"
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(cursor.fetchall(), columns=columns)
        cursor.close()
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
                effectiveness[disease] = self.config.effectiveness_map.get(row[disease], 0.0)

            product = Product(
                name=row["Product"],
                frac_codes=frac_codes,
                cost_per_dose=float(row.get("Cost/Dose", 0.0)) if pd.notna(row.get("Cost/Dose")) else 0.0,
                phi=int(row["phi"]) if pd.notna(row["phi"]) else 0,
                max_applications=int(row["Max Applications"]) if pd.notna(row["Max Applications"]) else 999,
                effectiveness=effectiveness,
                is_multisite=is_multisite,
                primary_disease=str(row.get("Primary Disease")) if pd.notna(row.get("Primary Disease")) else "",
                omri=str(row.get("omri")) if pd.notna(row.get("omri")) else "",
                units=str(row.get("units")) if pd.notna(row.get("units")) else "",
                price=float(row.get("Price")) if pd.notna(row.get("Price")) else 0.0,
                dose_avg=float(row.get("Dose (avg)")) if pd.notna(row.get("Dose (avg)")) else 0.0,
                container_size=float(row.get("Container Size")) if pd.notna(row.get("Container Size")) else 0.0,
                package_size=float(row.get("package_size")) if pd.notna(row.get("package_size")) else 0.0,
                price_source=str(row.get("price_source")) if pd.notna(row.get("price_source")) else "",
                label_url=str(row.get("label_url")) if pd.notna(row.get("label_url")) else "",
                rei=int(row.get("rei")) if pd.notna(row.get("rei")) else 0,
                ppe_long_sleeves_pants=bool(row.get("ppe_long_sleeves_pants")) if pd.notna(row.get("ppe_long_sleeves_pants")) else False,
                ppe_socks_shoes=bool(row.get("ppe_socks_shoes")) if pd.notna(row.get("ppe_socks_shoes")) else False,
                ppe_waterproof_gloves=bool(row.get("ppe_waterproof_gloves")) if pd.notna(row.get("ppe_waterproof_gloves")) else False,
                ppe_protective_eyewear=bool(row.get("ppe_protective_eyewear")) if pd.notna(row.get("ppe_protective_eyewear")) else False,
                min_rate=float(row.get("min_rate")) if pd.notna(row.get("min_rate")) else 0.0,
                max_rate=float(row.get("max_rate")) if pd.notna(row.get("max_rate")) else 0.0,
                epa_no=str(row.get("EPA No")) if pd.notna(row.get("EPA No")) else "",
                active_ingredient=str(row.get("Active Ingredient")) if pd.notna(row.get("Active Ingredient")) else "",
                signal_word=str(row.get("Singal Word")) if pd.notna(row.get("Singal Word")) else ""
            )

            products.append(product)
        
        return products

    def add_product(self, product_data: Dict):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check duplicate name case-insensitive
        p_name = product_data.get("Product")
        if p_name:
            cursor.execute('SELECT "Product" FROM products WHERE LOWER("Product") = LOWER(%s)', (p_name,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                raise ValueError(f"Product '{p_name}' already exists (case-insensitive duplicate).")

        remapped_data = {self._clean_key(k): v for k, v in product_data.items()}
        columns = [f"\"{k}\"" for k in product_data.keys()]
        placeholders = ", ".join([f"%({self._clean_key(k)})s" for k in product_data.keys()])
            
        sql = f"INSERT INTO products ({', '.join(columns)}) VALUES ({placeholders})"
        
        cursor.execute(sql, remapped_data)
        conn.commit()
        cursor.close()
        conn.close()

    def update_product(self, name: str, product_data: Dict):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check duplicate name case-insensitive
        new_name = product_data.get("Product")
        if new_name and new_name.lower() != name.lower():
            cursor.execute('SELECT "Product" FROM products WHERE LOWER("Product") = LOWER(%s)', (new_name,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                raise ValueError(f"Product '{new_name}' already exists (case-insensitive duplicate).")

        # Use double quotes for column names to handle spaces and preserve casing
        set_clause = ", ".join([f"\"{col}\" = %({self._clean_key(col)})s" for col in product_data.keys()])
        sql = f"UPDATE products SET {set_clause} WHERE \"Product\" = %(old_name)s"
        
        remapped_data = {self._clean_key(k): v for k, v in product_data.items()}
        remapped_data['old_name'] = name
        
        cursor.execute(sql, remapped_data)
        conn.commit()
        cursor.close()
        conn.close()

    def _clean_key(self, key: str) -> str:
        """Cleans a key to be used as a placeholder name."""
        return key.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')

    def delete_product(self, name: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        sql = "DELETE FROM products WHERE \"Product\" = %s"
        cursor.execute(sql, (name,))
        conn.commit()
        cursor.close()
        conn.close()

    def _normalize_frac(self, frac_str: str) -> List[str]:
        if not frac_str:
            return []
        frac_str = str(frac_str).strip().replace('+', ',').replace(' ', ',').replace(';', ',')
        parts = [p.strip().lower() for p in frac_str.split(',') if p.strip()]
        return [p for p in parts if p]
