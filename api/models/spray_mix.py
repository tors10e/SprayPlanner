from typing import List, Set
from models.product import Product

class SprayMix:
    def __init__(self, products: List[Product]):
        self.products = products

    def total_cost(self, acres: float) -> float:
        return sum(p.cost_per_dose for p in self.products) * acres

    def cost_per_dose(self) -> float:
        return sum(p.cost_per_dose for p in self.products)

    def get_covered_diseases(self, target_diseases: Set[str], min_rating: float) -> Set[str]:
        covered = set()
        for p in self.products:
            for d in target_diseases:
                if p.is_effective(d, min_rating):
                    covered.add(d)
        return covered

    def get_active_covered_diseases(self, target_diseases: Set[str], min_rating: float) -> Set[str]:
        covered = set()
        for p in self.products:
            if not p.is_multisite():
                for d in target_diseases:
                    if p.is_effective(d, min_rating):
                        covered.add(d)
        return covered

    def has_multisite(self) -> bool:
        return any(p.is_multisite() for p in self.products)

    def has_active_ingredient(self) -> bool:
        return any(not p.is_multisite() for p in self.products)

    def get_frac_codes(self) -> List[str]:
        fracs = []
        for p in self.products:
            fracs.extend(p.frac_codes)
        return fracs

    def __repr__(self):
        return f"SprayMix(products={[p.name for p in self.products]})"
