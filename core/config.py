from datetime import datetime
from typing import Dict, Set

class Config:
    def __init__(self):
        self.excel_file = "SprayPlanner/spray_product_information.csv"
        self.database_file = "SprayPlanner/core/database.db"
        self.total_acres = 4
        self.sulfur_sensitive_acres = 0
        self.normal_acres = self.total_acres - self.sulfur_sensitive_acres

        self.frac_limits = {
            "3": 2,
            "7": 2,
            "11": 2,
            "4": 2
        }

        self.frac_window = 3
        self.default_interval = 14
        self.critical_stages = {"pre-bloom", "bloom", "fruit-set"}
        self.high_priority_threshold = 0.8
        self.harvest_date = datetime(2026, 9, 20)
        self.start_date = "2026-04-01"
        self.end_date = "2026-10-20"
        self.phi_buffer_days = 0

        self.effectiveness_map = {
            "e": 4.0,
            "vg": 3.0,
            "g": 2.0,
            "f": 1.0,
            "na": 0.0    
        }

        self.minimum_spray_effectiveness = self.effectiveness_map.get('f')
        self.max_products_per_spray = 4
        self.multisite_fracs = {"M", "M01", "M02", "M03", "M04", "M05"}
        self.frac_cooldown = 1

        self.stage_weights = {
            "budbreak": {"Anthracnose": 0.5, "Powdery": 0.5, "Downy": 0.5, "Phomopsis": 0.5, "Botrytis": 0.0, "Black Rot": 0.5, "Bitter Rot": 0.0},
            "pre-bloom": {"Anthracnose": 1.0, "Powdery": 1.0, "Downy": 1.0, "Phomopsis": 1.0, "Botrytis": 0.5, "Black Rot": 1.0, "Bitter Rot": 0.5},
            "bloom": {"Anthracnose": 0.5, "Powdery": 1.0, "Downy": 1.0, "Phomopsis": 0.8, "Botrytis": 0.5, "Black Rot": 1.0, "Bitter Rot": 0.5},
            "fruit-set": {"Anthracnose": 0.0, "Powdery": 1.0, "Downy": 1.0, "Phomopsis": 0.5, "Botrytis": 0.5, "Black Rot": 0.8, "Bitter Rot": 0.8},
            "veraison": {"Anthracnose": 0.0, "Powdery": 1.0, "Downy": 0.8, "Phomopsis": 0.0, "Botrytis": 0.8, "Black Rot": 0.0, "Bitter Rot": 1.0},
            "pre-harvest": {"Anthracnose": 0.0, "Powdery": 0.8, "Downy": 0.5, "Phomopsis": 0.0, "Botrytis": 1.0, "Black Rot": 0.0, "Bitter Rot": 0.8},
            "post-harvest": {"Anthracnose": 0.0, "Powdery": 0.0, "Downy": 0.5, "Phomopsis": 0.0, "Botrytis": 0.8, "Black Rot": 0.0, "Bitter Rot": 0.5},
        }
