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
        container_size: float = 0.0,
        package_size: float = 0.0,
        price_source: str = "",
        label_url: str = "",
        rei: int = 0,
        ppe_long_sleeves_pants: bool = False,
        ppe_socks_shoes: bool = False,
        ppe_waterproof_gloves: bool = False,
        ppe_protective_eyewear: bool = False,
        min_rate: float = 0.0,
        max_rate: float = 0.0,
        epa_no: str = "",
        active_ingredient: str = "",
        signal_word: str = ""
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
        self.package_size = package_size
        self.price_source = price_source
        self.label_url = label_url
        self.rei = rei
        self.ppe_long_sleeves_pants = ppe_long_sleeves_pants
        self.ppe_socks_shoes = ppe_socks_shoes
        self.ppe_waterproof_gloves = ppe_waterproof_gloves
        self.ppe_protective_eyewear = ppe_protective_eyewear
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.epa_no = epa_no
        self.active_ingredient = active_ingredient
        self.signal_word = signal_word

    def is_multisite(self) -> bool:
        return self._is_multisite

    def get_effectiveness(self, disease: str) -> float:
        return self.effectiveness.get(disease, 0.0)

    def is_effective(self, disease: str, min_rating: float) -> bool:
        return self.get_effectiveness(disease) >= min_rating

    def __repr__(self):
        return f"Product({self.name}, FRAC={self.frac_codes}, Cost={self.cost_per_dose})"
