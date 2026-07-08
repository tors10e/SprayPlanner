import os
from datetime import datetime
from typing import Dict, Set

def load_dotenv():
    # config.py is in api/core/config.py, project root is three levels up
    core_dir = os.path.dirname(os.path.abspath(__file__))
    api_dir = os.path.dirname(core_dir)
    project_root = os.path.dirname(api_dir)
    dotenv_path = os.path.join(project_root, ".env")
    if os.path.exists(dotenv_path):
        with open(dotenv_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    val = val.strip().strip('"').strip("'")
                    key_name = key.strip()
                    if key_name not in os.environ:
                        os.environ[key_name] = val

load_dotenv()

class Config:
    def __init__(self):
        # Get the directory of the current file (SprayPlanner/api/core)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.excel_file = os.path.join(base_dir, "spray_product_information.csv")
        
        # Database configurations
        self.database_url = os.environ.get("DATABASE_URL")
        self.db_host = os.environ.get("DB_HOST", "localhost")
        try:
            self.db_port = int(os.environ.get("DB_PORT", 5432))
        except ValueError:
            self.db_port = 5432
        self.db_name = os.environ.get("DB_NAME", "sprayplanner")
        self.db_user = os.environ.get("DB_USER", "postgres")
        self.db_password = os.environ.get("DB_PASSWORD", "Black1ce!")

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

        self.minimum_spray_effectiveness = self.effectiveness_map.get('f') # can adjust based on your tolerance for risk
        self.max_products_per_spray = 4
        self.multisite_fracs = {"M", "M01", "M02", "M03", "M04", "M05"}
        self.frac_cooldown = 2


        self.stage_weights = {
            "budbreak": {"Anthracnose": 0.5, "Powdery": 0.5, "Downy": 0.5, "Phomopsis": 0.5, "Botrytis": 0.0, "Black Rot": 0.5, "Bitter Rot": 0.0},
            "pre-bloom": {"Anthracnose": 1.0, "Powdery": 1.0, "Downy": 1.0, "Phomopsis": 1.0, "Botrytis": 0.5, "Black Rot": 1.0, "Bitter Rot": 0.5},
            "bloom": {"Anthracnose": 0.5, "Powdery": 1.0, "Downy": 1.0, "Phomopsis": 0.8, "Botrytis": 0.5, "Black Rot": 1.0, "Bitter Rot": 0.5},
            "fruit-set": {"Powdery": 0.5, "Downy": 0.5, "Botrytis": 0.3},
            "veraison": {"Anthracnose": 0.0, "Powdery": 1.0, "Downy": 0.8, "Phomopsis": 0.0, "Botrytis": 0.8, "Black Rot": 0.0, "Bitter Rot": 1.0},
            "pre-harvest": {"Anthracnose": 0.0, "Powdery": 0.8, "Downy": 0.5, "Phomopsis": 0.0, "Botrytis": 1.0, "Black Rot": 0.0, "Bitter Rot": 0.8},
            "post-harvest": {"Downy": 0.3, "Botrytis": 0.3},
        }
