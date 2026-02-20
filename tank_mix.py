# -----------------------------
# Tank mix optimizer
# -----------------------------

import spray_config
import pandas as pd
import helpers
import itertools
import product_selector


chem = pd.read_csv(spray_config.EXCEL_FILE, dtype={'FRAC': str})
chem.columns = chem.columns.str.strip()
chem['FRAC'] = chem['FRAC'].fillna('')
chem["Cost/Dose"] = chem["Cost/Dose"].astype(float)

def build_mix(stage_name, recent_fracs, frac_counts):
    weights = spray_config.stage_weights[stage_name]
    is_critical = stage_name in spray_config.CRITICAL_STAGES

    coverage = {d: 0.0 for d in weights}

    selected = []
    used_fracs_this_mix = set()           # individual fracs used so far in this tank mix

  
    mix, cost = product_selector.cheapest_full_coverage(chem, stage_name)
    print("Recommended mix:")
    for m in mix:
        print(m["Product"], "FRAC:", m["FRAC"])
    print("Cost:", cost)


    return mix