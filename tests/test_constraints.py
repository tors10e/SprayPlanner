from datetime import datetime
from SprayPlanner.models.product import Product
from SprayPlanner.models.spray_event import SprayEvent
from SprayPlanner.models.growth_stage import GrowthStage
from SprayPlanner.core.config import Config
from SprayPlanner.constraints.phi_constraint import PHIConstraint
from SprayPlanner.constraints.frac_rotation_constraint import FRACRotationConstraint
from SprayPlanner.constraints.max_application_constraint import MaxApplicationConstraint
from SprayPlanner.constraints.oil_sulfur_constraint import OilSulfurConstraint
from SprayPlanner.constraints.multi_year_rotation_constraint import MultiYearRotationConstraint
from SprayPlanner.models.spray_mix import SprayMix

def test_phi_constraint():
    config = Config()
    config.harvest_date = datetime(2026, 9, 20)
    config.phi_buffer_days = 0
    
    constraint = PHIConstraint(config)
    
    # 5 days PHI, 10 days before harvest
    p1 = Product("P1", ["1"], 10.0, 5, 5, {}, False)
    e1 = SprayEvent(datetime(2026, 9, 10), GrowthStage("test", {}, False))
    assert constraint.is_satisfied(p1, e1, {}) is True
    
    # 15 days PHI, 10 days before harvest
    p2 = Product("P2", ["1"], 10.0, 15, 5, {}, False)
    assert constraint.is_satisfied(p2, e1, {}) is False

def test_frac_rotation_constraint():
    config = Config()
    config.frac_limits = {"1": 2}
    config.multisite_fracs = {"M"}
    
    constraint = FRACRotationConstraint(config)
    event = SprayEvent(datetime(2026, 5, 1), GrowthStage("test", {}, False))
    
    # Cooldown violation
    p1 = Product("P1", ["1"], 10.0, 0, 5, {}, False)
    history = {"recent_fracs": ["1"], "frac_counts": {}}
    assert constraint.is_satisfied(p1, event, history) is False
    
    # Seasonal limit violation
    history = {"recent_fracs": ["2"], "frac_counts": {"1": 2}}
    assert constraint.is_satisfied(p1, event, history) is False
    
    # Multisite always ok
    p_multi = Product("PM", ["M"], 5.0, 0, 5, {}, True)
    history = {"recent_fracs": ["M"], "frac_counts": {"M": 10}}
    assert constraint.is_satisfied(p_multi, event, history) is True

def test_max_application_constraint():
    constraint = MaxApplicationConstraint()
    product = Product("Test", ["1"], 10.0, 0, 2, {}, False)
    event = SprayEvent(datetime(2026, 5, 1), GrowthStage("test", {}, False))
    
    history = {"product_usage": {"Test": 1}}
    assert constraint.is_satisfied(product, event, history) is True
    
    history = {"product_usage": {"Test": 2}}
    assert constraint.is_satisfied(product, event, history) is False

def test_oil_sulfur_constraint():
    constraint = OilSulfurConstraint()
    sulfur = Product("Sulfur", ["M02"], 10.0, 0, 99, {}, True)
    oil = Product("JMS Stylet Oil", ["M"], 15.0, 0, 99, {}, True)
    event = SprayEvent(datetime(2026, 5, 1), GrowthStage("test", {}, False))
    
    # OK: No history
    assert constraint.is_satisfied(sulfur, event, {"last_products": []}) is True
    
    # FAIL: Sulfur current, Oil in last spray
    history = {"last_products": ["JMS Stylet Oil"]}
    assert constraint.is_satisfied(sulfur, event, history) is False
    
    # FAIL: Oil current, Sulfur in last spray
    history = {"last_products": ["Sulfur"]}
    assert constraint.is_satisfied(oil, event, history) is False
    
    # FAIL: Sulfur and Oil in same mix
    mix_with_oil = SprayMix([oil])
    assert constraint.is_satisfied(sulfur, event, {}, mix_with_oil) is False
    
    # OK: Non-conflicting
    other = Product("Captan", ["M04"], 10.0, 0, 99, {}, True)
    assert constraint.is_satisfied(other, event, {"last_products": ["Sulfur"]}) is True

def test_multi_year_rotation_constraint():
    constraint = MultiYearRotationConstraint()
    p_active = Product("Active", ["1"], 10.0, 0, 99, {}, False)
    p_multi = Product("Multi", ["M"], 5.0, 0, 99, {}, True)
    
    # Event in 2027, critical stage
    stage = GrowthStage("bloom", {"D": 1.0}, True)
    event_2027 = SprayEvent(datetime(2027, 6, 1), stage)
    
    # OK: No multi-year history
    assert constraint.is_satisfied(p_active, event_2027, {"multi_year_history": {}}) is True
    
    # FAIL: Used in SAME stage in 2026
    history = {
        "multi_year_history": {
            2026: {"bloom": ["Active"]}
        }
    }
    assert constraint.is_satisfied(p_active, event_2027, history) is False
    
    # OK: Used in DIFFERENT stage in 2026
    history = {
        "multi_year_history": {
            2026: {"budbreak": ["Active"]}
        }
    }
    assert constraint.is_satisfied(p_active, event_2027, history) is True
    
    # OK: Multisite is exempt
    history = {
        "multi_year_history": {
            2026: {"bloom": ["Multi"]}
        }
    }
    assert constraint.is_satisfied(p_multi, event_2027, history) is True
    
    # OK: Not critical stage
    non_critical_stage = GrowthStage("budbreak", {"D": 1.0}, False)
    event_non_crit = SprayEvent(datetime(2027, 4, 1), non_critical_stage)
    history = {
        "multi_year_history": {
            2026: {"budbreak": ["Active"]}
        }
    }
    assert constraint.is_satisfied(p_active, event_non_crit, history) is True
