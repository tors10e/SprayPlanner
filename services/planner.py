from typing import List, Dict, Optional
from SprayPlanner.core.config import Config
from SprayPlanner.models.product import Product
from SprayPlanner.models.spray_event import SprayEvent
from SprayPlanner.models.spray_mix import SprayMix
from SprayPlanner.services.mix_builder import MixBuilder

class Planner:
    def __init__(self, config: Config, mix_builder: MixBuilder):
        self.config = config
        self.mix_builder = mix_builder

    def optimize_season(self, schedule: List[SprayEvent], products: List[Product]) -> List[Dict]:
        history = {
            "recent_fracs": [],
            "frac_counts": {},
            "product_usage": {},
            "last_products": []
        }
        
        season_plan = []

        for event in schedule:
            mix = self.mix_builder.build_cost_optimal_mix(products, event, history)

            if mix is None:
                season_plan.append({
                    "date": event.date.strftime("%Y-%m-%d"),
                    "stage": event.growth_stage.name,
                    "mix": "NO VALID MIX"
                })
                continue

            # Update history
            self._update_history(mix, history)

            season_plan.append({
                "date": event.date.strftime("%Y-%m-%d"),
                "stage": event.growth_stage.name,
                "products": [p.name for p in mix.products],
                "FRACs": mix.get_frac_codes(),
                "Cost/Dose": mix.cost_per_dose(),
                "Total Cost": mix.total_cost(self.config.total_acres)
            })

        return season_plan

    def _update_history(self, mix: SprayMix, history: Dict):
        # Update product usage counts
        for p in mix.products:
            history["product_usage"][p.name] = history["product_usage"].get(p.name, 0) + 1

        # Update FRAC history
        new_fracs = mix.get_frac_codes()
        for f in new_fracs:
            if f.upper() in self.config.multisite_fracs:
                continue
            history["frac_counts"][f] = history["frac_counts"].get(f, 0) + 1
        
        # Store last spray products
        history["last_products"] = [p.name for p in mix.products]

        # In a real app, recent_fracs might track the last few sprays
        # For this refactor, we'll keep it simple and just store the last spray's non-multisite FRACs
        history["recent_fracs"] = [f for f in new_fracs if f.upper() not in self.config.multisite_fracs]
