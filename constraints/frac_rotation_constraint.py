from typing import Dict, List
from SprayPlanner.constraints.base_constraint import BaseConstraint
from SprayPlanner.models.product import Product
from SprayPlanner.models.spray_event import SprayEvent
from SprayPlanner.models.spray_mix import SprayMix
from SprayPlanner.core.config import Config

class FRACRotationConstraint(BaseConstraint):
    def __init__(self, config: Config):
        self.config = config

    def is_satisfied(
        self, 
        product: Product, 
        event: SprayEvent, 
        history: Dict,
        current_mix: SprayMix = None
    ) -> bool:
        # multisite / low-risk -> always ok
        if product.is_multisite():
            return True

        recent_fracs = history.get("recent_fracs", [])
        frac_counts = history.get("frac_counts", {})

        # 1. Cooldown: none of this product's FRACs can be in recent_fracs
        for f in product.frac_codes:
            if f in recent_fracs:
                return False

        # 2. Seasonal limit
        for f in product.frac_codes:
            limit = self.config.frac_limits.get(f)
            if limit is not None and frac_counts.get(f, 0) >= limit:
                return False

        return True
