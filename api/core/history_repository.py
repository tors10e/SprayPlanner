import psycopg2
import pandas as pd
from typing import List, Dict
from models.spray_history import SprayHistoryEntry
from core.config import Config

class SprayHistoryRepository:
    def __init__(self, config: Config):
        self.config = config
        # Only pesticide chemical application attributes are saved in spray_history table
        self.columns = [
            "Pesticide", 
            "Liters/Acre", "Dose/acre", "Dose per L @150 l", 
            "Calculated Dose", "Dose Units", "Actual Amt/acre", "Notes",
            "PHI Date", "REI_TIME"
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

    def load_history(self) -> List[SprayHistoryEntry]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Load from normalized tables (INNER JOIN to spray_events)
        sql = """
        SELECT 
            h.id,
            e."Spray #",
            e."Date",
            e."End Time",
            e."Block ",
            h."Pesticide",
            h."Liters/Acre",
            h."Dose/acre",
            h."Dose per L @150 l",
            h."Calculated Dose",
            h."Dose Units",
            h."Actual Amt/acre",
            h."Notes",
            h."PHI Date",
            h."REI_TIME",
            p."EPA No",
            p."FRAC" as "Group",
            p."Active Ingredient",
            p."Singal Word",
            p.rei as "REI (h)",
            p.phi as "PHI (d)",
            p.units as "Units",
            p.min_rate as "Min Dose",
            p.max_rate as "Max Dose"
        FROM spray_history h
        INNER JOIN spray_events e ON h.event_id = e.id
        LEFT JOIN products p ON h."Pesticide" = p."Product"
        ORDER BY e.id DESC, h.id ASC
        """
        
        cursor.execute(sql)
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(cursor.fetchall(), columns=columns)
        
        cursor.close()
        conn.close()

        entries = []
        for _, row in df.iterrows():
            entry = SprayHistoryEntry(
                entry_id=int(row["id"]),
                spray_number=int(row["Spray #"]) if pd.notna(row["Spray #"]) else None,
                date=str(row["Date"]) if pd.notna(row["Date"]) else "",
                end_time=str(row["End Time"]) if pd.notna(row["End Time"]) else "",
                block=str(row["Block "]) if pd.notna(row["Block "]) else "",
                pesticide=str(row["Pesticide"]) if pd.notna(row["Pesticide"]) else "",
                epa_no=str(row["EPA No"]) if pd.notna(row["EPA No"]) else "",
                group=str(row["Group"]) if pd.notna(row["Group"]) else "",
                active_ingredient=str(row["Active Ingredient"]) if pd.notna(row["Active Ingredient"]) else "",
                pest=str(row["Pest"]) if "Pest" in row and pd.notna(row["Pest"]) else "",
                signal_word=str(row["Singal Word"]) if pd.notna(row["Singal Word"]) else "",
                rei_h=float(row["REI (h)"]) if pd.notna(row["REI (h)"]) else None,
                phi_d=int(row["PHI (d)"]) if pd.notna(row["PHI (d)"]) else None,
                units=str(row["Units"]) if pd.notna(row["Units"]) else "",
                phi_date=str(row["PHI Date"]) if pd.notna(row["PHI Date"]) else "",
                rei_time=str(row["REI_TIME"]) if pd.notna(row["REI_TIME"]) else "",
                liters_acre=float(row["Liters/Acre"]) if pd.notna(row["Liters/Acre"]) else None,
                min_dose=float(row["Min Dose"]) if pd.notna(row["Min Dose"]) else None,
                max_dose=float(row["Max Dose"]) if pd.notna(row["Max Dose"]) else None,
                dose_acre=float(row["Dose/acre"]) if pd.notna(row["Dose/acre"]) else None,
                dose_per_l=float(row["Dose per L @150 l"]) if pd.notna(row["Dose per L @150 l"]) else None,
                rate_units=str(row["Units"]) if pd.notna(row["Units"]) else "",
                calculated_dose=float(row["Calculated Dose"]) if pd.notna(row["Calculated Dose"]) else None,
                dose_units=str(row["Dose Units"]) if pd.notna(row["Dose Units"]) else "",
                actual_amt_acre=float(row["Actual Amt/acre"]) if pd.notna(row["Actual Amt/acre"]) else None,
                notes=str(row["Notes"]) if pd.notna(row["Notes"]) else ""
            )
            entries.append(entry)
            
        return entries

    def _upsert_product_reference(self, cursor, data: Dict):
        p_name = data.get("Pesticide")
        if not p_name:
            return
            
        sql = """
        INSERT INTO products ("Product", "EPA No", "FRAC", "Active Ingredient", "Singal Word", "rei", "phi", "units", "min_rate", "max_rate")
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
        
        cursor.execute(sql, (
            p_name,
            data.get("EPA No") or None,
            data.get("Group") or None,
            data.get("Active Ingredient") or None,
            data.get("Singal Word") or None,
            int(data.get("REI (h)")) if data.get("REI (h)") is not None else None,
            int(data.get("PHI (d)")) if data.get("PHI (d)") is not None else None,
            data.get("Units") or None,
            float(data.get("Min Dose")) if data.get("Min Dose") is not None else None,
            float(data.get("Max Dose")) if data.get("Max Dose") is not None else None
        ))

    def add_entry(self, entry_data: Dict) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Upsert product reference
            self._upsert_product_reference(cursor, entry_data)
            
            # 2. Find or insert spray_event
            spray_num = self._normalize_val(entry_data.get("Spray #"))
            block = self._normalize_val(entry_data.get("Block "))
            date = self._normalize_val(entry_data.get("Date"))
            end_time = self._normalize_val(entry_data.get("End Time"))
            
            cursor.execute(
                'SELECT id FROM spray_events WHERE "Spray #" IS NOT DISTINCT FROM %s AND "Block " IS NOT DISTINCT FROM %s AND "Date" IS NOT DISTINCT FROM %s AND "End Time" IS NOT DISTINCT FROM %s',
                (spray_num, block, date, end_time)
            )
            row = cursor.fetchone()
            if row:
                event_id = row[0]
            else:
                cursor.execute(
                    'INSERT INTO spray_events ("Spray #", "Block ", "Date", "End Time") VALUES (%s, %s, %s, %s) RETURNING id',
                    (spray_num, block, date, end_time)
                )
                event_id = cursor.fetchone()[0]
                
            # 3. Insert spray_history record
            remapped_data = {self._clean_key(k): self._normalize_val(v) for k, v in entry_data.items() if k in self.columns}
            remapped_data['event_id'] = event_id
            
            for col in self.columns:
                cleaned = self._clean_key(col)
                if cleaned not in remapped_data:
                    remapped_data[cleaned] = None
                    
            columns_sql = 'event_id, ' + ", ".join([f'"{c}"' for c in self.columns])
            placeholders_sql = '%(event_id)s, ' + ", ".join([f"%({self._clean_key(c)})s" for c in self.columns])
            
            sql = f"INSERT INTO spray_history ({columns_sql}) VALUES ({placeholders_sql}) RETURNING id"
            cursor.execute(sql, remapped_data)
            new_id = cursor.fetchone()[0]
            
            conn.commit()
            return new_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def update_entry(self, entry_id: int, entry_data: Dict):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            self._upsert_product_reference(cursor, entry_data)
            
            cursor.execute("SELECT event_id FROM spray_history WHERE id = %s", (entry_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"History entry with id {entry_id} not found.")
            event_id = row[0]
            
            spray_num = self._normalize_val(entry_data.get("Spray #"))
            block = self._normalize_val(entry_data.get("Block "))
            date = self._normalize_val(entry_data.get("Date"))
            end_time = self._normalize_val(entry_data.get("End Time"))
            
            cursor.execute(
                'UPDATE spray_events SET "Spray #" = %s, "Block " = %s, "Date" = %s, "End Time" = %s WHERE id = %s',
                (spray_num, block, date, end_time, event_id)
            )
            
            update_keys = [k for k in entry_data.keys() if k in self.columns]
            if update_keys:
                set_clause = ", ".join([f'"{col}" = %({self._clean_key(col)})s' for col in update_keys])
                remapped_data = {self._clean_key(k): self._normalize_val(v) for k, v in entry_data.items() if k in self.columns}
                remapped_data['entry_id'] = entry_id
                sql = f"UPDATE spray_history SET {set_clause} WHERE id = %(entry_id)s"
                cursor.execute(sql, remapped_data)
                
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def delete_entry(self, entry_id: int):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM spray_history WHERE id = %s", (entry_id,))
        conn.commit()
        cursor.close()
        conn.close()

    def bulk_add_entries(self, entries_list: List[Dict]) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        event_map = {}
        count = 0
        
        try:
            for entry_data in entries_list:
                spray_num = self._normalize_val(entry_data.get("Spray #"))
                block = self._normalize_val(entry_data.get("Block "))
                date = self._normalize_val(entry_data.get("Date"))
                end_time = self._normalize_val(entry_data.get("End Time"))
                
                event_key = (spray_num, block, date, end_time)
                if event_key in event_map:
                    event_id = event_map[event_key]
                else:
                    cursor.execute(
                        'SELECT id FROM spray_events WHERE "Spray #" IS NOT DISTINCT FROM %s AND "Block " IS NOT DISTINCT FROM %s AND "Date" IS NOT DISTINCT FROM %s AND "End Time" IS NOT DISTINCT FROM %s',
                        (spray_num, block, date, end_time)
                    )
                    row = cursor.fetchone()
                    if row:
                        event_id = row[0]
                    else:
                        cursor.execute(
                            'INSERT INTO spray_events ("Spray #", "Block ", "Date", "End Time") VALUES (%s, %s, %s, %s) RETURNING id',
                            (spray_num, block, date, end_time)
                        )
                        event_id = cursor.fetchone()[0]
                    event_map[event_key] = event_id
                    
                self._upsert_product_reference(cursor, entry_data)
                
                remapped_data = {self._clean_key(k): self._normalize_val(v) for k, v in entry_data.items() if k in self.columns}
                remapped_data['event_id'] = event_id
                
                for col in self.columns:
                    cleaned = self._clean_key(col)
                    if cleaned not in remapped_data:
                        remapped_data[cleaned] = None
                        
                columns_sql = 'event_id, ' + ", ".join([f'"{c}"' for c in self.columns])
                placeholders_sql = '%(event_id)s, ' + ", ".join([f"%({self._clean_key(c)})s" for c in self.columns])
                sql = f"INSERT INTO spray_history ({columns_sql}) VALUES ({placeholders_sql})"
                
                cursor.execute(sql, remapped_data)
                count += 1
                
            conn.commit()
            return count
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def _clean_key(self, key: str) -> str:
        return key.replace(' ', '_').replace('#', 'num').replace('(', '').replace(')', '').replace('@', 'at').replace('/', '_')

    def _normalize_val(self, val):
        if pd.isna(val) or val == "" or val == "None" or val == "NA":
            return None
        return val
