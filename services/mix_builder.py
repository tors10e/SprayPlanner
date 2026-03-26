import itertools
from typing import List, Dict, Set, Optional
from SprayPlanner.models.product import Product
from SprayPlanner.models.spray_event import SprayEvent
from SprayPlanner.models.spray_mix import SprayMix
from SprayPlanner.core.config import Config
from SprayPlanner.constraints.base_constraint import BaseConstraint

class MixBuilder:
    def __init__(self, config: Config, constraints: List[BaseConstraint]):
        self.config = config
        self.constraints = constraints

    def build_cost_optimal_mix(
        self,
        available_products: List[Product],
        event: SprayEvent,
        history: Dict
    ) -> Optional[SprayMix]:
        
        target_diseases = event.growth_stage.get_target_diseases()
        if not target_diseases:
            return None

        # Filter candidates based on constraints and activity
        candidates = []
        for p in available_products:
            # Must satisfy all constraints
            if not all(c.is_satisfied(p, event, history) for c in self.constraints):
                continue
            
            # Must have some effectiveness against target diseases
            if not any(p.is_effective(d, self.config.minimum_spray_effectiveness) for d in target_diseases):
                continue
                
            candidates.append(p)

        # Sort candidates by cost
        candidates.sort(key=lambda p: p.cost_per_dose)

        # Try combinations of increasing size
        for size in range(1, self.config.max_products_per_spray + 1):
            for product_combo in itertools.combinations(candidates, size):
                # We need to check if the combination itself is valid (e.g., same-spray constraints)
                valid_combo = True
                temp_mix = SprayMix([])
                for p in product_combo:
                    if not all(c.is_satisfied(p, event, history, temp_mix) for c in self.constraints):
                        valid_combo = False
                        break
                    temp_mix.products.append(p)
                
                if not valid_combo:
                    continue

                mix = temp_mix

                # Rule: Must have a multisite backbone
                if not mix.has_multisite():
                    continue

                # Rule: During critical periods, must have an active ingredient
                if event.is_critical and not mix.has_active_ingredient():
                    continue

                # Rule: Must cover all target diseases
                covered = mix.get_covered_diseases(target_diseases, self.config.minimum_spray_effectiveness)
                if covered != target_diseases:
                    continue

                return mix

        return None
