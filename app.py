import pandas as pd
from SprayPlanner.core.config import Config
from SprayPlanner.core.repository import ProductRepository
from SprayPlanner.services.scheduler import Scheduler
from SprayPlanner.services.mix_builder import MixBuilder
from SprayPlanner.services.planner import Planner
from SprayPlanner.constraints.phi_constraint import PHIConstraint
from SprayPlanner.constraints.frac_rotation_constraint import FRACRotationConstraint
from SprayPlanner.constraints.max_application_constraint import MaxApplicationConstraint
from SprayPlanner.constraints.oil_sulfur_constraint import OilSulfurConstraint

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
        OilSulfurConstraint()
    ]

    # 5. Initialize services
    mix_builder = MixBuilder(config, constraints)
    planner = Planner(config, mix_builder)

    # 6. Run optimization
    plan = planner.optimize_season(schedule, products)

    # 7. Output result
    plan_df = pd.DataFrame(plan)
    print(plan_df)

if __name__ == "__main__":
    main()
