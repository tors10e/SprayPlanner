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


schedule = scheduler.build_schedule()
spray_materials = helpers.get_chemical_data()

plan = product_selector.optimize_season(schedule, spray_materials, total_acres=spray_config.TOTAL_ACRES)
plan_df = pd.DataFrame(plan)
print(plan_df)
