from SprayPlanner.models.product import Product
from SprayPlanner.models.growth_stage import GrowthStage
from SprayPlanner.models.spray_mix import SprayMix

def test_product_effectiveness():
    effectiveness = {"Downy": 3.0, "Powdery": 2.0}
    product = Product("Test", ["1"], 10.0, 0, 5, effectiveness, False)
    
    assert product.get_effectiveness("Downy") == 3.0
    assert product.get_effectiveness("Botrytis") == 0.0
    assert product.is_effective("Downy", 2.0) is True
    assert product.is_effective("Powdery", 3.0) is False

def test_growth_stage_diseases():
    weights = {"Downy": 1.0, "Powdery": 0.5, "Botrytis": 0.0}
    stage = GrowthStage("bloom", weights, True)
    
    assert stage.get_target_diseases() == {"Downy", "Powdery"}
    assert stage.get_high_priority_diseases(0.8) == {"Downy"}

def test_spray_mix_coverage():
    p1 = Product("P1", ["1"], 10.0, 0, 5, {"Downy": 3.0}, False)
    p2 = Product("P2", ["M"], 5.0, 0, 5, {"Powdery": 3.0}, True)
    mix = SprayMix([p1, p2])
    
    target = {"Downy", "Powdery"}
    assert mix.get_covered_diseases(target, 2.0) == target
    assert mix.get_active_covered_diseases(target, 2.0) == {"Downy"}
    assert mix.has_multisite() is True
    assert mix.has_active_ingredient() is True
    assert mix.total_cost(10) == 150.0
