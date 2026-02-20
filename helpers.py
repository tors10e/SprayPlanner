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

def normalize_frac(frac_str):
    if not frac_str or pd.isna(frac_str):
        return []
    # Common separators: comma, +, space, semicolon
    frac_str = str(frac_str).strip().replace('+', ',').replace(' ', ',').replace(';', ',')
    parts = [p.strip().lower() for p in frac_str.split(',') if p.strip()]
    return [p for p in parts if p]  # remove empty


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