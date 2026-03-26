from typing import Dict
from SprayPlanner.constraints.base_constraint import BaseConstraint
from SprayPlanner.models.product import Product
from SprayPlanner.models.spray_event import SprayEvent
from SprayPlanner.models.spray_mix import SprayMix

class MaxApplicationConstraint(BaseConstraint):
    def is_satisfied(
        self, 
        product: Product, 
        event: SprayEvent, 
        history: Dict,
        current_mix: SprayMix = None
    ) -> bool:
        product_usage = history.get("product_usage", {})
        if product_usage.get(product.name, 0) >= product.max_applications:
            return False
        return True
