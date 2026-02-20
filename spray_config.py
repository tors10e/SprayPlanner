EXCEL_FILE = "./SprayPlanAndMaterials_2025.csv"

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

EFF_MAP = {"e": 1.0, "vg": 0.85, "g": 0.65, "f": 0.4, "": 0.0}

HIGH_PRIORITY_THRESHOLD = 0.8

rating_map = {
    "e": 4.0,
    "vg": 3.0,
    "g": 2.0,
    "f": 1.0
}

MAX_PRODUCTS_PER_SPRAY = 4

MINIMUM_SPRAY_EFFECTIVENESS = 3  # can adjust based on your tolerance for risk

MULTISITE_FRACS = {"M01","M02", "M03", "M04", "M05"}

FRAC_COOLDOWN = 1  # sprays before reuse allowed

rating_map = {
    "e": 4.0,
    "vg": 3.0,
    "g": 2.0,
    "f": 1.0
}

stage_weights = {
    "budbreak": {"Anthracnose": 0.8, "Powdery": 0.8, "Downy": 0.8, "Phomopsis": 0.8, "Botrytis": 0.0, "Black Rot": 0.5, "Bitter Rot": 0.0},
    "pre-bloom": {"Anthracnose": 1.0, "Powdery": 1.0, "Downy": 1.0, "Phomopsis": 1.0, "Botrytis": 0.5, "Black Rot": 1.0, "Bitter Rot": 0.5},
    "bloom": {"Anthracnose": 0.5, "Powdery": 1.0, "Downy": 1.0, "Phomopsis": 0.8, "Botrytis": 0.5, "Black Rot": 1.0, "Bitter Rot": 0.5},
    "fruit-set": {"Anthracnose": 0.0, "Powdery": 1.0, "Downy": 1.0, "Phomopsis": 0.5, "Botrytis": 0.5, "Black Rot": 0.8, "Bitter Rot": 0.8},
    "veraison": {"Anthracnose": 0.0, "Powdery": 1.0, "Downy": 0.8, "Phomopsis": 0.0, "Botrytis": 0.8, "Black Rot": 0.0, "Bitter Rot": 1.0},
    "pre-harvest": {"Anthracnose": 0.0, "Powdery": 0.8, "Downy": 0.5, "Phomopsis": 0.0, "Botrytis": 1.0, "Black Rot": 0.0, "Bitter Rot": 0.8},
    "post-harvest": {"Anthracnose": 0.0, "Powdery": 0.0, "Downy": 0.5, "Phomopsis": 0.0, "Botrytis": 0.8, "Black Rot": 0.0, "Bitter Rot": 0.5},
}

START_DATE = "2026-04-20"
END_DATE = "2026-10-20"


