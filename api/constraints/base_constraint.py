from abc import ABC, abstractmethod
from typing import Dict, List
from models.product import Product
from models.spray_event import SprayEvent
from models.spray_mix import SprayMix

class BaseConstraint(ABC):
    @abstractmethod
    def is_satisfied(
        self, 
        product: Product, 
        event: SprayEvent, 
        history: Dict,
        current_mix: SprayMix = None
    ) -> bool:
        pass
