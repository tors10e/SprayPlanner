from typing import List, Dict, Set

class Product:
    def __init__(
        self,
        name: str,
        frac_codes: List[str],
        cost_per_dose: float,
        phi: int,
        max_applications: int,
        effectiveness: Dict[str, float],
        is_multisite: bool,
        primary_disease: str = "",
        omri: str = "",
        units: str = "",
        price: float = 0.0,
        dose_avg: float = 0.0,
        container_size: float = 0.0
    ):
        self.name = name
        self.frac_codes = frac_codes
        self.cost_per_dose = cost_per_dose
        self.phi = phi
        self.max_applications = max_applications
        self.effectiveness = effectiveness
        self._is_multisite = is_multisite
        self.primary_disease = primary_disease
        self.omri = omri
        self.units = units
        self.price = price
        self.dose_avg = dose_avg
        self.container_size = container_size

    def is_multisite(self) -> bool:
        return self._is_multisite

    def get_effectiveness(self, disease: str) -> float:
        return self.effectiveness.get(disease, 0.0)

    def is_effective(self, disease: str, min_rating: float) -> bool:
        return self.get_effectiveness(disease) >= min_rating

    def __repr__(self):
        return f"Product({self.name}, FRAC={self.frac_codes}, Cost={self.cost_per_dose})"
