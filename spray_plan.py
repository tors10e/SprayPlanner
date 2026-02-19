import pandas as pd
from datetime import datetime, timedelta

EXCEL_FILE = "./SprayPlanAndMaterials_2025.csv"

TOTAL_ACRES = 4
SULFUR_SENSITIVE_ACRES = 1
NORMAL_ACRES = TOTAL_ACRES - SULFUR_SENSITIVE_ACRES

FRAC_WINDOW = 3
DEFAULT_INTERVAL = 10

chem = pd.read_csv(EXCEL_FILE, dtype={'FRAC': str})
chem.columns = chem.columns.str.strip()
chem['FRAC'] = chem['FRAC'].fillna('')
chem["Cost/Dose"] = chem["Cost/Dose"].astype(float)

frac_counts = {}
recent_fracs = []

# -----------------------------
# Helper functions
# -----------------------------

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

stage_weights = {
    "budbreak": {"Downy": 1.0, "Phomopsis": 0.8},
    "pre-bloom": {"Powdery": 1.0, "Downy": 0.9, "Black Rot": 0.8},
    "bloom": {"Powdery": 1.0, "Downy": 0.9, "Botrytis": 1.0, "Black Rot": 0.7},
    "fruit-set": {"Powdery": 1.0, "Downy": 0.9},
    "veraison": {"Botrytis": 1.0},
    "pre-harvest": {"Botrytis": 1.0}
}


CRITICAL_STAGES = {"pre-bloom", "bloom", "fruit-set"}

rating_map = {
    "e": 4.0,
    "vg": 3.0,
    "g": 2.0,
    "f": 1.0
}

FRAC_LIMITS = {
    "3": 3,
    "7": 3,
    "11": 3
}

FRAC_COOLDOWN = 3  # sprays before reuse allowed


def effectiveness(row, disease):
    if disease not in row:
        return 0.0

    val = str(row[disease]).strip().lower()

    return rating_map.get(val, 0.0)


def stage(date):
    m = date.month
    if m <= 4: return "budbreak"
    if m == 5: return "pre-bloom"
    if m == 6: return "bloom"
    if m == 7: return "fruit-set"
    if m == 8: return "veraison"
    return "pre-harvest"


def allowed_by_rotation(frac, recent_fracs, frac_counts):

    # Multisite = always allowed
    if is_low_risk(frac):
        return True

    # Cooldown rule
    if frac in recent_fracs:
        return False

    # Seasonal limit rule
    limit = FRAC_LIMITS.get(frac)

    if limit is not None:
        if frac_counts.get(frac, 0) >= limit:
            return False

    return True



# -----------------------------
# Tank mix optimizer
# -----------------------------

def build_mix(stage_name, recent_fracs, frac_counts):

    weights = stage_weights[stage_name]
    is_critical = stage_name in CRITICAL_STAGES

    # Track achieved protection per disease
    coverage = {d: 0.0 for d in weights.keys()}

    selected = []
    used_fracs = set()

    # -----------------------------
    # HELPER: compute marginal gain
    # -----------------------------
    def marginal_gain(row):

        frac = str(row["FRAC"]).strip()
        product = str(row["Product"]).lower()

        # Avoid sulfur if possible
        if "sulfur" in product and not is_critical:
            return -1

        if not allowed_by_rotation(frac, recent_fracs, frac_counts):
            return -1

        gain = 0.0

        for disease, w in weights.items():

            eff = effectiveness(row, disease)

            # Only reward improvement beyond current coverage
            improvement = max(0, eff - coverage[disease])

            gain += improvement * w

        # Resistance penalty
        if not is_low_risk(frac):
            gain -= frac_counts.get(frac, 0) * 0.5

        return gain

    # -----------------------------
    # SELECT PRIMARY PRODUCTS
    # -----------------------------
    for _ in range(2):  # max 2 primary actives

        best_gain = 0
        best_row = None

        for _, r in chem.iterrows():

            frac = str(r["FRAC"]).strip()

            # Avoid duplicate high-risk FRACs
            if not is_low_risk(frac) and frac in used_fracs:
                continue

            gain = marginal_gain(r)

            if gain > best_gain:
                best_gain = gain
                best_row = r

        if best_row is None:
            break

        selected.append(best_row)
        frac = str(best_row["FRAC"]).strip()
        used_fracs.add(frac)

        # Update coverage achieved
        for disease in coverage:
            coverage[disease] = max(
                coverage[disease],
                effectiveness(best_row, disease)
            )

    # -----------------------------
    # ADD MULTISITE BACKBONE
    # -----------------------------
    if is_critical:

        multisites = chem[
            chem["FRAC"].str.lower().str.startswith("m")
        ].sort_values("Cost/Dose")

        for _, ms in multisites.iterrows():

            frac = str(ms["FRAC"]).strip()

            if frac not in used_fracs:

                selected.append(ms)

                # Update coverage
                for disease in coverage:
                    coverage[disease] = max(
                        coverage[disease],
                        effectiveness(ms, disease)
                    )

                break

    return selected


# -----------------------------
# Build default season plan
# -----------------------------

start = datetime(2026, 4, 20)
end = datetime(2026, 9, 20)

dates = []
d = start
while d <= end:
    dates.append(d)
    d += timedelta(days=DEFAULT_INTERVAL)

recent_fracs = []
plan = []

for d in dates:

    s = stage(d)
    mix = build_mix(s, recent_fracs, frac_counts)
    
    fracs = [str(m["FRAC"]).strip() for m in mix]

    for f in fracs:
        if not is_low_risk(f):
            frac_counts[f] = frac_counts.get(f, 0) + 1

    recent_fracs.extend(fracs)
    recent_fracs = recent_fracs[-FRAC_COOLDOWN:]

    if not mix:
        continue

    products = [m["Product"] for m in mix]
    fracs = [m["FRAC"] for m in mix]

    cost = 0

    for m in mix:
        if "sulfur" in m["Product"].lower():
            cost += m["Cost/Dose"] * NORMAL_ACRES
        else:
            cost += m["Cost/Dose"] * TOTAL_ACRES

    recent_fracs.extend(fracs)
    recent_fracs = recent_fracs[-FRAC_WINDOW:]

    plan.append({
        "date": d.strftime("%Y-%m-%d"),
        "stage": s,
        "products": " + ".join(products),
        "FRACs": ", ".join(fracs),
        "cost": round(cost, 2)
    })

plan_df = pd.DataFrame(plan)

print(plan_df)
print("\nSeason Cost: $", plan_df["cost"].sum())
