from typing import List, Dict, Optional
from core.config import Config
from models.product import Product
from models.spray_event import SprayEvent
from models.growth_stage import GrowthStage
from services.mix_builder import MixBuilder
from models.spray_mix import SprayMix # Added import

class Planner:
    def __init__(self, config: Config, mix_builder: MixBuilder):
        self.config = config
        self.mix_builder = mix_builder

    def optimize_season(self, schedule: List[SprayEvent], products: List[Product], initial_history: Optional[Dict] = None) -> List[Dict]:
        if initial_history is not None:
            history = initial_history
            # Reset seasonal history for the new year
            history["recent_fracs"] = []
            history["recent_fracs_window"] = []
            history["frac_counts"] = {}
            history["product_usage"] = {}
            history["last_products"] = []
            # Ensure multi_year_history exists
            if "multi_year_history" not in history: history["multi_year_history"] = {}
        else:
            history = {
                "recent_fracs": [],
                "recent_fracs_window": [],
                "frac_counts": {},
                "product_usage": {},
                "last_products": [],
                "multi_year_history": {}
            }
        
        season_plan = []

        for event in schedule:
            mix = self.mix_builder.build_cost_optimal_mix(products, event, history) # Removed organic_mode

            if mix is None:
                season_plan.append({
                    "date": event.date.strftime("%Y-%m-%d"),
                    "stage": event.growth_stage.name,
                    "mix": "NO VALID MIX"
                })
                continue # Correctly indented under 'if'

            # Update history
            self._update_history(mix, history, event) 

            season_plan.append({ # Correctly indented under 'for' loop
                "date": event.date.strftime("%Y-%m-%d"),
                "stage": event.growth_stage.name,
                "products": [p.name for p in mix.products],
                "FRACs": mix.get_frac_codes(),
                "Cost/Dose": mix.cost_per_dose(),
                "Total Cost": mix.total_cost(self.config.total_acres)
            })

        return season_plan

    def _update_history(self, mix: SprayMix, history: Dict, event: Optional[SprayEvent] = None):
        # Update product usage counts
        for p in mix.products:
            history["product_usage"][p.name] = history["product_usage"].get(p.name, 0) + 1

        # Update multi-year history if critical
        if event and event.is_critical:
            year = event.year
            stage = event.growth_stage.name
            if year not in history["multi_year_history"]:
                history["multi_year_history"][year] = {}
            if stage not in history["multi_year_history"][year]:
                history["multi_year_history"][year][stage] = []
            
            for p in mix.products:
                if not p.is_multisite(): # Only non-multisite products count for rotation
                    history["multi_year_history"][year][stage].append(p.name)

        # Update FRAC history
        new_fracs = [f for f in mix.get_frac_codes() if f.upper() not in self.config.multisite_fracs]
        for f in new_fracs:
            history["frac_counts"][f] = history["frac_counts"].get(f, 0) + 1
        
        # Maintain a sliding window of recent FRACs based on frac_cooldown
        # history["recent_fracs"] will be a list of sets/lists, one for each recent spray
        if "recent_fracs_window" not in history:
            history["recent_fracs_window"] = []
        
        history["recent_fracs_window"].append(new_fracs)
        
        # Keep only the last 'frac_cooldown' sprays in the window
        if len(history["recent_fracs_window"]) > self.config.frac_cooldown:
            history["recent_fracs_window"].pop(0)
            
        # Flatten the window for the constraint to check easily
        history["recent_fracs"] = [f for spray in history["recent_fracs_window"] for f in spray]
        
        # Store last spray products
        history["last_products"] = [p.name for p in mix.products]
