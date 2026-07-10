from typing import Dict, Set

class GrowthStage:
    def __init__(self, name: str, disease_weights: Dict[str, float], is_critical: bool):
        self.name = name
        self.disease_weights = disease_weights
        self._is_critical = is_critical

    @property
    def is_critical(self) -> bool:
        return self._is_critical

    def get_target_diseases(self) -> Set[str]:
        return {d for d, w in self.disease_weights.items() if w > 0}

    def get_high_priority_diseases(self, threshold: float) -> Set[str]:
        return {d for d, w in self.disease_weights.items() if w >= threshold}

    def __repr__(self):
        return f"GrowthStage({self.name}, critical={self.is_critical})"
