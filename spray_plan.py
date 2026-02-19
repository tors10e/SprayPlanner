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
    "7": 2,
    "11": 2
}

FRAC_COOLDOWN = 2  # sprays before reuse allowed


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

    scores = []

    # -----------------------------
    # SCORE ALL CANDIDATES
    # -----------------------------
    for _, r in chem.iterrows():

        frac = str(r["FRAC"]).strip()
        product = str(r["Product"]).lower()

        # Skip sulfur if possible (sensitive block)
        if "sulfur" in product and not is_critical:
            continue

        # Enforce resistance rules
        if not allowed_by_rotation(frac, recent_fracs, frac_counts):
            continue

        # Calculate disease protection score
        score = 0.0
        for disease, w in weights.items():
            score += effectiveness(r, disease) * w

        if score <= 0:
            continue

        # Resistance penalty (soft discouragement)
        if not is_low_risk(frac):
            penalty = frac_counts.get(frac, 0) * 0.5
            score -= penalty

        scores.append((score, r))

    # -----------------------------
    # CRITICAL FALLBACK
    # -----------------------------
    if not scores and is_critical:

        for _, r in chem.iterrows():

            frac = str(r["FRAC"]).strip()

            score = 0.0
            for disease, w in weights.items():
                score += effectiveness(r, disease) * w

            if score > 0:
                scores.append((score, r))

    if not scores:
        return []

    scores.sort(reverse=True, key=lambda x: x[0])

    # -----------------------------
    # SELECT TANK MIX COMPONENTS
    # -----------------------------
    selected = []
    used_fracs = set()

    for score, r in scores:

        frac = str(r["FRAC"]).strip()

        # Avoid duplicate high-risk FRACs in same tank
        if not is_low_risk(frac) and frac in used_fracs:
            continue

        selected.append(r)
        used_fracs.add(frac)

        # Typical tank = 2 actives
        if len(selected) >= 2:
            break

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
                used_fracs.add(frac)
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
