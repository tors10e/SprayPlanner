import pandas as pd
from datetime import datetime, timedelta

EXCEL_FILE = "./SprayPlanAndMaterials_2025.csv"

TOTAL_ACRES = 4
SULFUR_SENSITIVE_ACRES = 1
NORMAL_ACRES = TOTAL_ACRES - SULFUR_SENSITIVE_ACRES

FRAC_WINDOW = 3
DEFAULT_INTERVAL = 10  # days

# -----------------------------
# LOAD CHEMICAL DATA
# -----------------------------

chem = pd.read_csv(EXCEL_FILE, dtype={'FRAC': str})
# Replace all NaN values with an empty string
chem['FRAC'] = chem['FRAC'].fillna('')
chem.columns = chem.columns.str.strip()

chem = chem[[
    "Product",
    "Primary Disease",
    "FRAC",
    "PHI",
    "Cost/Dose",
    "Anthracnose",
    "Black Rot",
    "Bitter Rot",
    "Botrytis",
    "Downy",
    "Phomopsis",
    "Downy"
]].copy()

chem["Primary Disease"] = chem["Primary Disease"].str.lower().fillna("")
chem["FRAC"] = chem["FRAC"].astype(str)
chem["Cost/Dose"] = chem["Cost/Dose"].astype(float)

# -----------------------------
# PHENOLOGY MODEL
# -----------------------------

def stage(date):
    m = date.month
    if m <= 4: return "budbreak"
    if m == 5: return "pre-bloom"
    if m == 6: return "bloom"
    if m == 7: return "fruit-set"
    if m == 8: return "veraison"
    return "pre-harvest"

stage_targets = {
    "budbreak": ["downy"],
    "pre-bloom": ["powdery", "downy"],
    "bloom": ["botrytis", "powdery", "downy"],
    "fruit-set": ["powdery", "downy"],
    "veraison": ["botrytis"],
    "pre-harvest": ["botrytis"]
}

CRITICAL_STAGES = {"pre-bloom", "bloom", "fruit-set"}


# -----------------------------
# TANK MIX BUILDER
# -----------------------------

def is_low_risk(frac):
    return str(frac).lower().startswith("m")


def build_mix(targets, recent_fracs):

    selected = []
    used_fracs = set()

    for disease in targets:

        options = chem[
            chem["Primary Disease"].str.contains(disease)
        ].sort_values("Cost/Dose")
 
        for _, r in options.iterrows():

            frac = r["FRAC"]

            # Skip duplicate FRAC within same tank
            #todo: dont apply this to low risk fracs like and frac not is_low_risk(frac)
            if frac in used_fracs:
                continue
                

            # Enforce rotation ONLY for high-risk FRACs
            if not is_low_risk(frac) and frac in recent_fracs:
                continue
            selected.append(r)
            used_fracs.add(frac)
            break

    return selected


# -----------------------------
# DEFAULT SEASON PLAN
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
    targets = stage_targets[s]

    mix = build_mix(targets, recent_fracs)

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