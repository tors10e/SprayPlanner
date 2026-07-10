from core.config import Config
from core.repository import ProductRepository
import pandas as pd

config = Config()
repo = ProductRepository(config)
products = repo.load_products()

target_diseases = ["Anthracnose", "Black Rot", "Bitter Rot", "Botrytis", "Downy", "Phomopsis", "Powdery"]

print(f"{'Product':<30} | {'Multisite':<10} | {'Coverage'}")
print("-" * 60)

for p in products:
    covered = [d for d in target_diseases if p.is_effective(d, config.minimum_spray_effectiveness)]
    if covered:
        print(f"{p.name:<30} | {str(p.is_multisite()):<10} | {', '.join(covered)}")
