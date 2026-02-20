import spray_config
import tank_mix
import pandas as pd
import helpers
from datetime import datetime, timedelta
import product_selector
import scheduler

# -----------------------------
# Build default season plan
# -----------------------------

# recent_fracs = []
# plan = []

# for d in dates:
#     stage = helpers.determine_stage(d)
#     mix = tank_mix.build_mix(stage, recent_fracs, frac_counts)
    
#     if not mix:
#         continue

#     # Collect all individual FRACs used in this spray
#     this_spray_fracs = []
#     for m in mix:
#         this_spray_fracs.extend(helpers.get_all_fracs(m))

#     # Update counters & recent list
#     for f in this_spray_fracs:
#         if not helpers.is_low_risk(f):
#             frac_counts[f] = frac_counts.get(f, 0) + 1

#     recent_fracs.extend(this_spray_fracs)
#     recent_fracs = recent_fracs[-spray_config.FRAC_COOLDOWN:]   # or -spray_config.FRAC_WINDOW if you prefer

#     # Cost calculation (unchanged)
#     cost = 0
#     for m in mix:
#         if "sulfur" in str(m["Product"]).lower():
#             cost += m["Cost/Dose"] * spray_config.NORMAL_ACRES
#         else:
#             cost += m["Cost/Dose"] * spray_config.TOTAL_ACRES

#     products = [str(m["Product"]) for m in mix]
#     frac_strings = [str(m["FRAC"]) for m in mix]   # for display only

#     plan.append({
#         "date": d.strftime("%Y-%m-%d"),
#         "stage": stage,
#         "products": " + ".join(products),
#         "FRACs": ", ".join(frac_strings),          # original strings for readability
#         "individual_fracs": ", ".join(sorted(set(this_spray_fracs))),  # optional: for debugging
#         "cost": round(cost, 2)
#     })

# plan_df = pd.DataFrame(plan)

# print(plan_df)
# print("\nSeason Cost: $", plan_df["cost"].sum())

schedule = scheduler.build_schedule()
spray_materials = helpers.get_chemical_materials()

plan = product_selector.optimize_season(schedule, spray_materials, sulfur_acres=spray_config.SULFUR_SENSITIVE_ACRES, total_acres=spray_config.TOTAL_ACRES)
plan_df = pd.DataFrame(plan)
print(plan_df)
