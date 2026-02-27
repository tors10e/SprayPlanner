from datetime import datetime


EXCEL_FILE = "./spray_product_information.csv"

TOTAL_ACRES = 4
SULFUR_SENSITIVE_ACRES = 0
NORMAL_ACRES = TOTAL_ACRES - SULFUR_SENSITIVE_ACRES

FRAC_LIMITS = {
    "3": 2,
    "7": 2,
    "11": 2,
    "4": 2
}

FRAC_WINDOW = 3
DEFAULT_INTERVAL = 14
CRITICAL_STAGES = {"pre-bloom", "bloom", "fruit-set"}
HIGH_PRIORITY_THRESHOLD = 0.8
HARVEST_DATE = datetime(2026, 9, 20)
START_DATE = "2026-04-01"
END_DATE = "2026-10-20"
PHI_BUFFER_DAYS = 0   # extra safety margin if desired

EFFECTIVENESS_MAP = {
    "e": 4.0,
    "vg": 3.0,
    "g": 2.0,
    "f": 1.0,
    "na": 0.0    
}

MINIMUM_SPRAY_EFFECTIVENESS = EFFECTIVENESS_MAP.get('f') # can adjust based on your tolerance for risk
MAX_PRODUCTS_PER_SPRAY = 4
MULTISITE_FRACS = {"M", "M01", "M02", "M03", "M04", "M05"}
FRAC_COOLDOWN = 1  # sprays before reuse allowed

stage_weights = {
    "budbreak": {"Anthracnose": 0.5, "Powdery": 0.5, "Downy": 0.5, "Phomopsis": 0.5, "Botrytis": 0.0, "Black Rot": 0.5, "Bitter Rot": 0.0},
    "pre-bloom": {"Anthracnose": 1.0, "Powdery": 1.0, "Downy": 1.0, "Phomopsis": 1.0, "Botrytis": 0.5, "Black Rot": 1.0, "Bitter Rot": 0.5},
    "bloom": {"Anthracnose": 0.5, "Powdery": 1.0, "Downy": 1.0, "Phomopsis": 0.8, "Botrytis": 0.5, "Black Rot": 1.0, "Bitter Rot": 0.5},
    "fruit-set": {"Anthracnose": 0.0, "Powdery": 1.0, "Downy": 1.0, "Phomopsis": 0.5, "Botrytis": 0.5, "Black Rot": 0.8, "Bitter Rot": 0.8},
    "veraison": {"Anthracnose": 0.0, "Powdery": 1.0, "Downy": 0.8, "Phomopsis": 0.0, "Botrytis": 0.8, "Black Rot": 0.0, "Bitter Rot": 1.0},
    "pre-harvest": {"Anthracnose": 0.0, "Powdery": 0.8, "Downy": 0.5, "Phomopsis": 0.0, "Botrytis": 1.0, "Black Rot": 0.0, "Bitter Rot": 0.8},
    "post-harvest": {"Anthracnose": 0.0, "Powdery": 0.0, "Downy": 0.5, "Phomopsis": 0.0, "Botrytis": 0.8, "Black Rot": 0.0, "Bitter Rot": 0.5},
}




