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
        print(plan_df[["date", "stage", "products", "FRACs", "Total Cost"]])

if __name__ == "__main__":
    main()
