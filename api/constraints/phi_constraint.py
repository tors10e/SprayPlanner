from datetime import datetime
from typing import Dict
from constraints.base_constraint import BaseConstraint
from models.product import Product
from models.spray_event import SprayEvent
from models.spray_mix import SprayMix
from core.config import Config

class PHIConstraint(BaseConstraint):
    def __init__(self, config: Config):
        self.config = config

    def is_satisfied(
        self, 
        product: Product, 
        event: SprayEvent, 
        history: Dict,
        current_mix: SprayMix = None
    ) -> bool:
        if product.phi == 0:
            return True

        days_to_harvest = (self.config.harvest_date - event.date).days
        return product.phi <= (days_to_harvest - self.config.phi_buffer_days)
