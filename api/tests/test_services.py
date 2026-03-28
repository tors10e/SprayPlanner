from datetime import datetime
from core.config import Config
from services.scheduler import Scheduler
from services.mix_builder import MixBuilder
from services.planner import Planner
from models.product import Product
from models.spray_event import SprayEvent
from models.growth_stage import GrowthStage
from constraints.phi_constraint import PHIConstraint

def test_scheduler_builds_correct_number_of_events():
    config = Config()
    config.start_date = "2026-04-01"
    config.end_date = "2026-05-01"
    config.default_interval = 14
    
    scheduler = Scheduler(config)
    schedule = scheduler.build_schedule()
    
    # April 1, April 15, April 29
    assert len(schedule) == 3
    assert schedule[0].date == datetime(2026, 4, 1)
    assert schedule[2].date == datetime(2026, 4, 29)

def test_mix_builder_finds_optimal_mix():
    config = Config()
    config.max_products_per_spray = 2
    config.minimum_spray_effectiveness = 1.0
    config.critical_stages = {"bloom"}
    
    # Products
    p_multi = Product("Multi", ["M"], 5.0, 0, 99, {"Downy": 3.0, "Powdery": 3.0}, True)
    p_active = Product("Active", ["1"], 15.0, 0, 99, {"Downy": 3.0}, False)
    products = [p_multi, p_active]
    
    # Event
    stage = GrowthStage("bloom", {"Downy": 1.0}, True)
    event = SprayEvent(datetime(2026, 6, 1), stage)
    
    builder = MixBuilder(config, [])
    mix = builder.build_cost_optimal_mix(products, event, {})
    
    assert mix is not None
    assert "Multi" in [p.name for p in mix.products]
    assert "Active" in [p.name for p in mix.products] # Critical stage requires active
    assert mix.cost_per_dose() == 20.0

def test_planner_updates_history():
    config = Config()
    config.total_acres = 1
    config.multisite_fracs = {"M"}
    
    # Mock MixBuilder that always returns a specific mix
    p1 = Product("P1", ["1"], 10.0, 0, 5, {"D": 3.0}, False)
    p2 = Product("P2", ["M"], 5.0, 0, 5, {"D": 3.0}, True)
    
    class MockBuilder:
        def build_cost_optimal_mix(self, products, event, history):
            from models.spray_mix import SprayMix
            return SprayMix([p1, p2])
            
    planner = Planner(config, MockBuilder())
    
    event = SprayEvent(datetime(2026, 4, 1), GrowthStage("test", {"D": 1.0}, False))
    schedule = [event]
    
    plan = planner.optimize_season(schedule, [p1, p2])
    
    assert len(plan) == 1
    assert plan[0]["products"] == ["P1", "P2"]
    # Internal history check would be better if exposed, but we can verify plan output
    assert plan[0]["Cost/Dose"] == 15.0
