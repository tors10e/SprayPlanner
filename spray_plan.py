import spray_config
import pandas as pd
from datetime import datetime, timedelta

chem = pd.read_csv(spray_config.EXCEL_FILE, dtype={'FRAC': str})
chem.columns = chem.columns.str.strip()
chem['FRAC'] = chem['FRAC'].fillna('')
chem["Cost/Dose"] = chem["Cost/Dose"].astype(float)

frac_counts = {}
recent_fracs = []


# -----------------------------
# Helper functions
# -----------------------------

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


# -----------------------------
# Disease weights by stage
# -----------------------------



def effectiveness(row, disease):
    if disease not in row:
        return 0.0

    val = str(row[disease]).strip().lower()

    return spray_config.rating_map.get(val, 0.0)


def stage(date):
    m = date.month
    if m <= 4: return "budbreak"
    if m == 5: return "pre-bloom"
    if m == 6: return "bloom"
    if m == 7: return "fruit-set"
    if m == 8: return "veraison"
    if m == 9: return "pre-harvest"
    return "post-harvest"


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



# -----------------------------
# Tank mix optimizer
# -----------------------------

def build_mix(stage_name, recent_fracs, frac_counts):
    weights = spray_config.stage_weights[stage_name]
    is_critical = stage_name in spray_config.CRITICAL_STAGES

    coverage = {d: 0.0 for d in weights}

    selected = []
    used_fracs_this_mix = set()           # individual fracs used so far in this tank mix

    def marginal_gain(row):
        fracs = get_all_fracs(row)
        product = str(row["Product"]).lower()

        # Check rotation rules for the whole product
        if not allowed_by_rotation(fracs, recent_fracs, frac_counts):
            return -1.0

        # Prevent duplicate FRAC within same spray (very conservative)
        if all(f in used_fracs_this_mix for f in fracs if not is_low_risk(f)):
            return -1.0

        gain = 0.0
        for disease, w in weights.items():
            eff = effectiveness(row, disease)
            improvement = max(0, eff - coverage[disease])
            gain += improvement * w


        # Optional resistance pressure penalty
        for f in fracs:
            if not is_low_risk(f):
                gain -= frac_counts.get(f, 0) * 0.5

        return gain

    # ─── Select up to 2 high-risk actives ────────────────────────
    for _ in range(2):
        best_gain = -999
        best_row = None

        for _, r in chem.iterrows():
            gain = marginal_gain(r)
            if gain > best_gain:
                best_gain = gain
                best_row = r

        if best_row is None or best_gain <= 0:
            break

        selected.append(best_row)
        fracs = get_all_fracs(best_row)
        used_fracs_this_mix.update(fracs)

        # Update coverage
        for disease in coverage:
            coverage[disease] = max(coverage[disease], effectiveness(best_row, disease))

    # ─── Add active chemical protectant in critical stages ─────────────
    if is_critical and len(selected) > 0:  # only if we have some activity

        active_products = chem[~chem["FRAC"].str.lower().str.startswith("m")].sort_values("Cost/Dose")
        for _, active_product in active_products.iterrows():
            fracs = get_all_fracs(active_product)
            if not any(f in used_fracs_this_mix for f in fracs):
                selected.append(active_product)
                used_fracs_this_mix.update(fracs)
                # update coverage (usually multisites are weak → small effect)
                for disease in coverage:
                    coverage[disease] = max(coverage[disease], effectiveness(active_product, disease))
                break

    return selected


# -----------------------------
# Build default season plan
# -----------------------------

start = datetime(2026, 4, 20)
end = datetime(2026, 10, 20)

dates = []
d = start
while d <= end:
    dates.append(d)
    d += timedelta(days=spray_config.DEFAULT_INTERVAL)

recent_fracs = []
plan = []

for d in dates:
    s = stage(d)
    mix = build_mix(s, recent_fracs, frac_counts)
    
    if not mix:
        continue

    # Collect all individual FRACs used in this spray
    this_spray_fracs = []
    for m in mix:
        this_spray_fracs.extend(get_all_fracs(m))

    # Update counters & recent list
    for f in this_spray_fracs:
        if not is_low_risk(f):
            frac_counts[f] = frac_counts.get(f, 0) + 1

    recent_fracs.extend(this_spray_fracs)
    recent_fracs = recent_fracs[-spray_config.FRAC_COOLDOWN:]   # or -spray_config.FRAC_WINDOW if you prefer

    # Cost calculation (unchanged)
    cost = 0
    for m in mix:
        if "sulfur" in str(m["Product"]).lower():
            cost += m["Cost/Dose"] * spray_config.NORMAL_ACRES
        else:
            cost += m["Cost/Dose"] * spray_config.TOTAL_ACRES

    products = [str(m["Product"]) for m in mix]
    frac_strings = [str(m["FRAC"]) for m in mix]   # for display only

    plan.append({
        "date": d.strftime("%Y-%m-%d"),
        "stage": s,
        "products": " + ".join(products),
        "FRACs": ", ".join(frac_strings),          # original strings for readability
        "individual_fracs": ", ".join(sorted(set(this_spray_fracs))),  # optional: for debugging
        "cost": round(cost, 2)
    })

plan_df = pd.DataFrame(plan)

print(plan_df)
print("\nSeason Cost: $", plan_df["cost"].sum())
