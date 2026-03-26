from typing import Dict
from SprayPlanner.constraints.base_constraint import BaseConstraint
from SprayPlanner.models.product import Product
from SprayPlanner.models.spray_event import SprayEvent
from SprayPlanner.models.spray_mix import SprayMix

class MultiYearRotationConstraint(BaseConstraint):
    def is_satisfied(
        self, 
        product: Product, 
        event: SprayEvent, 
        history: Dict,
        current_mix: SprayMix = None
    ) -> bool:
        # Only applies during critical periods
        if not event.is_critical:
            return True
            
        # Multisite is exempt
        if product.is_multisite():
            return True

        # multi_year_history format: { year: { stage_name: [product_names] } }
        multi_year_history = history.get("multi_year_history", {})
        
        # Check the immediately preceding year for the same critical stage
        current_year = event.year
        current_stage = event.growth_stage.name
        
        previous_year = current_year - 1
        if previous_year in multi_year_history:
            previous_stages = multi_year_history[previous_year]
            if current_stage in previous_stages: # Check if the current critical stage was used in the previous year
                if product.name in previous_stages[current_stage]: # Check if this specific product was used in that same stage
                    return False
                    
        return True
