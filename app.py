import pandas as pd
from datetime import datetime
from SprayPlanner.core.config import Config
from SprayPlanner.core.repository import ProductRepository
from SprayPlanner.services.scheduler import Scheduler
from SprayPlanner.services.mix_builder import MixBuilder
from SprayPlanner.services.planner import Planner
from SprayPlanner.constraints.phi_constraint import PHIConstraint
from SprayPlanner.constraints.frac_rotation_constraint import FRACRotationConstraint
from SprayPlanner.constraints.max_application_constraint import MaxApplicationConstraint
from SprayPlanner.constraints.oil_sulfur_constraint import OilSulfurConstraint
from SprayPlanner.constraints.multi_year_rotation_constraint import MultiYearRotationConstraint

def main():
    # 1. Initialize configuration
    config = Config()

    # 2. Initialize repository and load products
    repo = ProductRepository(config)
    products = repo.load_products()

    # 3. Set up constraints
    # We will instantiate MultiYearRotationConstraint here so it can be used across years
    constraints = [
        PHIConstraint(config),
        FRACRotationConstraint(config),
        MaxApplicationConstraint(),
        OilSulfurConstraint(),
        MultiYearRotationConstraint()
    ]

    # 4. Initialize services
    mix_builder = MixBuilder(config, constraints)
    planner = Planner(config, mix_builder)

    # 5. Run 3-year optimization
    multi_year_plan = {}
    history = {
        "multi_year_history": {}
    }

    years = [2026, 2027, 2028]
    for year in years:
        print(f"\n--- Generating Plan for {year} ---")
        
        # Adjust config for the current year
        config.start_date = f"{year}-04-01"
        config.end_date = f"{year}-10-20"
        config.harvest_date = datetime(year, 9, 20)

        # Build schedule for this year
        scheduler = Scheduler(config)
        schedule = scheduler.build_schedule()

        # Optimize season (passing existing history)
        # Note: we need to modify planner to take history as an optional argument or keep it persistent
        # For now, we'll manually manage history in main() and pass it if we refactor planner further,
        # OR we just let the planner update the 'history' dict we pass in.
        
        # Actually, let's modify Planner.optimize_season to accept initial history
        plan = planner.optimize_season(schedule, products, initial_history=history)
        multi_year_plan[year] = plan
        
        plan_df = pd.DataFrame(plan)
        print(plan_df[["date", "stage", "products", "FRACs", "Total Cost"]])

if __name__ == "__main__":
    main()
