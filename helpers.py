import pandas as pd
import spray_config
from datetime import datetime
# -----------------------------
# Helper functions
# -----------------------------


def allowed_by_phi(row, spray_date):
    phi = row.get("PHI", 0)

    if pd.isna(phi):
        return True

    days_to_harvest = (spray_config.HARVEST_DATE - datetime.strptime(spray_date, "%Y-%m-%d")).days

    return phi <= days_to_harvest - spray_config.PHI_BUFFER_DAYS


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



# Returns the effectiveness rating of a product for a given disease, based on the rating_map in spray_config.py
def effectiveness(product_row, disease):
    val = str(product_row.get(disease, "")).lower().strip()
    return spray_config.EFFECTIVENESS_MAP.get(val, 0.0)


def is_multisite(row):
    fracs = normalize_frac(row["FRAC"])
    return any(f.upper() in spray_config.MULTISITE_FRACS for f in fracs)

def normalize_frac(frac_str):
    if not frac_str or pd.isna(frac_str):
        return []
    # Common separators: comma, +, space, semicolon
    frac_str = str(frac_str).strip().replace('+', ',').replace(' ', ',').replace(';', ',')
    parts = [p.strip().lower() for p in frac_str.split(',') if p.strip()]
    return [p for p in parts if p]  # remove empty


def get_chemical_data():
    chem = pd.read_csv(spray_config.EXCEL_FILE, dtype={'FRAC': str})
    chem.columns = chem.columns.str.strip()
    chem['FRAC'] = chem['FRAC'].fillna('')
    chem["Cost/Dose"] = chem["Cost/Dose"].astype(float)
    chem =chem[chem['Cost/Dose'] > 0] 
    return chem

def get_all_fracs(row):
    return normalize_frac(row["FRAC"])

def is_low_risk(frac):
    return str(frac).lower().startswith("m")


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

# def effectiveness(row, disease):
#     if disease not in row:
#         return 0.0

#     val = str(row[disease]).strip().lower()

#     return spray_config.rating_map.get(val, 0.0)


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


def violates_max_applications(mix, product_usage):

    for _, row in mix.iterrows():

        product = row["Product"]
        max_apps = row.get("Max_Applications", None)

        if pd.isna(max_apps) or max_apps == "":
            continue  # no restriction recorded

        if product_usage.get(product, 0) >= int(max_apps):
            return True

    return False


# for each product in the mix, check if it has effectiveness greater than the minimum required for each disease in the target diseases. If so, add it to the covered set. If the product is not multisite, also add it to the active_covered set.
           
def get_covered_diseases(mix, target_diseases):
    covered = set()
    active_covered = set()

    for _, row in mix.iterrows():
        # for each disease in the target diseases, check if the product has effectiveness greater than the minimum required. If so, add it to the covered set. If the product is not multisite, also add it to the active_covered set.
        for d in target_diseases:
            if effectiveness(row, d) > spray_config.MINIMUM_SPRAY_EFFECTIVENESS:
                covered.add(d)
                if not is_multisite(row):
                    active_covered.add(d)
    return covered, active_covered


def get_target_diseases(stage, stage_weights):
    target_diseases = [d for d, w in stage_weights.items() if w > 0]
    if not target_diseases:
        return None
    return target_diseases


def has_activity(row, disease):
    if disease not in row:
        return False

    val = str(row[disease]).strip().lower()
    return spray_config.rating_map.get(val, 0.0) > spray_config.MINIMUM_SPRAY_EFFECTIVENESS