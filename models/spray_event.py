from datetime import datetime
from SprayPlanner.models.growth_stage import GrowthStage

class SprayEvent:
    def __init__(self, date: datetime, growth_stage: GrowthStage):
        self.date = date
        self.growth_stage = growth_stage
        self.year = date.year

    @property
    def is_critical(self) -> bool:
        return self.growth_stage.is_critical

    def __repr__(self):
        return f"SprayEvent({self.date.strftime('%Y-%m-%d')}, stage={self.growth_stage.name})"
