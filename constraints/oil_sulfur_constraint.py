from typing import Dict
from SprayPlanner.constraints.base_constraint import BaseConstraint
from SprayPlanner.models.product import Product
from SprayPlanner.models.spray_event import SprayEvent
from SprayPlanner.models.spray_mix import SprayMix

class OilSulfurConstraint(BaseConstraint):
    def __init__(self):
        # Keywords to identify sulfur and oil products
        self.sulfur_keywords = ["sulfur"]
        self.oil_keywords = ["oil"]

    def is_satisfied(
        self, 
        product: Product, 
        event: SprayEvent, 
        history: Dict,
        current_mix: SprayMix = None
    ) -> bool:
        last_products = history.get("last_products", [])
        
        is_current_sulfur = any(k in product.name.lower() for k in self.sulfur_keywords)
        is_current_oil = any(k in product.name.lower() for k in self.oil_keywords)
        
        if not is_current_sulfur and not is_current_oil:
            return True
            
        # 1. Check against products in the last spray (cross-spray)
        for last_p_name in last_products:
            last_p_lower = last_p_name.lower()
            
            is_last_sulfur = any(k in last_p_lower for k in self.sulfur_keywords)
            is_last_oil = any(k in last_p_lower for k in self.oil_keywords)
            
            if is_current_sulfur and is_last_oil:
                return False
            
            if is_current_oil and is_last_sulfur:
                return False

        # 2. Check against products already in the current mix (same-spray)
        if current_mix:
            for p in current_mix.products:
                p_lower = p.name.lower()
                is_mix_sulfur = any(k in p_lower for k in self.sulfur_keywords)
                is_mix_oil = any(k in p_lower for k in self.oil_keywords)
                
                if is_current_sulfur and is_mix_oil:
                    return False
                if is_current_oil and is_mix_sulfur:
                    return False
                
        return True
