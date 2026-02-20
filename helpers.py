import pandas as pd
import spray_config

# -----------------------------
# Helper functions
# -----------------------------

def allowed_by_rotation(frac_list, recent_fracs, frac_counts):
    """
    frac_list: list of individual frac codes for ONE product
    Returns True if this PRODUCT is allowed given current state
    """
    # Multisite / low-risk → always ok unless you want stricter rules
    if any(is_low_risk(f) for f in frac_list):
        return True

    # 1. Cooldown: none of this product's FRACs can be in recent_fracs
    if any(f in recent_fracs for f in frac_list):
        return False

    # 2. Seasonal limit
    for f in frac_list:
        limit = spray_config.FRAC_LIMITS.get(f)
        if limit is not None and frac_counts.get(f, 0) >= limit:
            return False

    return True


def covers_diseases(product_row, diseases):
    return any(effectiveness(product_row, d) > 0 for d in diseases)


def effectiveness(product_row, disease):
    val = str(product_row.get(disease, "")).lower().strip()
    return spray_config.EFF_MAP.get(val, 0.0)


def is_multisite(product_row):
    fracs = normalize_frac(product_row["FRAC"])
    return any(f in spray_config.MULTISITE_FRACS for f in fracs)


def normalize_frac(frac_str):
    if not frac_str or pd.isna(frac_str):
        return []
    # Common separators: comma, +, space, semicolon
    frac_str = str(frac_str).strip().replace('+', ',').replace(' ', ',').replace(';', ',')
    parts = [p.strip().lower() for p in frac_str.split(',') if p.strip()]
    return [p for p in parts if p]  # remove empty


def get_chemical_materials():
    chem = pd.read_csv(spray_config.EXCEL_FILE, dtype={'FRAC': str})
    chem.columns = chem.columns.str.strip()
    chem['FRAC'] = chem['FRAC'].fillna('')
    chem["Cost/Dose"] = chem["Cost/Dose"].astype(float)
    return chem


def get_all_fracs(row):
    return normalize_frac(row["FRAC"])

def is_low_risk(frac):
    return str(frac).lower().startswith("m")


def effectiveness(row, disease):
    if disease not in row:
        return 0
    try:
        return float(row[disease])
    except:
        return 0

def determine_stage(date):
    m = date.month
    if m <= 4: return "budbreak"
    if m == 5: return "pre-bloom"
    if m == 6: return "bloom"
    if m == 7: return "fruit-set"
    if m == 8: return "veraison"
    if m == 9: return "pre-harvest"
    return "post-harvest"


# -----------------------------
# Disease weights by stage
# -----------------------------

def effectiveness(row, disease):
    if disease not in row:
        return 0.0

    val = str(row[disease]).strip().lower()

    return spray_config.rating_map.get(val, 0.0)


# Get multsite backbone products
def get_multisite_chems(chem):
    return chem[chem["FRAC"].str.lower().str.startswith("m", na=False)]

# Get active chemicals for critical periods (exclude multisite/backbone)
def get_active_chems(chem, disease):
    return chem[~chem["FRAC"].str.lower().str.startswith("m", na=False)]




def update_frac_history(fracs, frac_history):
    for f in fracs:
        if f in spray_config.MULTISITE_FRACS:
            continue
        frac_history[f] = frac_history.get(f, 0) + 1

def normalize_frac(frac):
    return [f.strip() for f in str(frac).split("+")]

def violates_rotation(fracs, frac_history):
    for f in fracs:
        if f in spray_config.MULTISITE_FRACS:
            continue
        if frac_history.get(f, 0) >= spray_config.FRAC_COOLDOWN:
            return True
    return False