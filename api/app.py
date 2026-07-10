import pandas as pd
from datetime import datetime
from core.config import Config
from core.repository import ProductRepository
from services.scheduler import Scheduler
from services.mix_builder import MixBuilder
from services.planner import Planner
from constraints.phi_constraint import PHIConstraint
from constraints.frac_rotation_constraint import FRACRotationConstraint
from constraints.max_application_constraint import MaxApplicationConstraint
from constraints.oil_sulfur_constraint import OilSulfurConstraint
from constraints.multi_year_rotation_constraint import MultiYearRotationConstraint

def main():
    # 1. Initialize configuration
    config = Config()

    # 2. Initialize repository and load products
    repo = ProductRepository(config)
    products = repo.load_products()

    # Prompt for organic mode
    organic_response = input("Do you want to generate an organic-only spray plan? (yes/no): ").lower().strip()
    if organic_response == 'yes' or organic_response == 'y':
        print("Organic mode enabled. Filtering for OMRI-listed products...")
        # Database stores OMRI as 1 for Yes, 0 for No
        products = [p for p in products if str(p.omri) == '1']
    elif organic_response == 'no' or organic_response == 'n':
        pass
    else:
        print("Invalid input. Proceeding with all products.")

    # 3. Build schedule
    scheduler = Scheduler(config)
    schedule = scheduler.build_schedule()

    # 4. Set up constraints
    constraints = [
        PHIConstraint(config),
        FRACRotationConstraint(config),
        MaxApplicationConstraint(),
        OilSulfurConstraint(),
        MultiYearRotationConstraint()
    ]

    # 5. Initialize services
    # MixBuilder and Planner are initialized without organic_mode
    mix_builder = MixBuilder(config, constraints)
    planner = Planner(config, mix_builder)

    # 6. Run 3-year optimization
    multi_year_plan = {}
    history = {
        "multi_year_history": {}
    }

    years = [2026, 2027, 2028]
    for year in years:
        print(f"--- Generating Plan for {year} ---")
        
        # Adjust config for the current year
        config.start_date = f"{year}-04-01"
        config.end_date = f"{year}-10-20"
        config.harvest_date = datetime(year, 9, 20)

        # Build schedule for this year
        scheduler = Scheduler(config)
        schedule = scheduler.build_schedule()

        # Optimize season (passing existing history)
        plan = planner.optimize_season(schedule, products, initial_history=history)
        multi_year_plan[year] = plan
        
        plan_df = pd.DataFrame(plan)
        
        # Check if we have a valid plan (at least one row with 'products')
        if "products" in plan_df.columns:
            # For display purposes, fill NaN values for rows with 'NO VALID MIX'
            cols_to_show = ["date", "stage", "products", "FRACs", "Total Cost"]
            # Ensure all columns exist before printing
            existing_cols = [c for c in cols_to_show if c in plan_df.columns]
            print(plan_df[existing_cols])
        else:
            print("No valid mixes found for any events this year.")
            print(plan_df[["date", "stage", "mix"]])

if __name__ == "__main__":
    main()
