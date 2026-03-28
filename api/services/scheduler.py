from datetime import datetime, timedelta
from typing import List
from core.config import Config
from models.growth_stage import GrowthStage
from models.spray_event import SprayEvent

class Scheduler:
    def __init__(self, config: Config):
        self.config = config

    def build_schedule(self) -> List[SprayEvent]:
        start_date = datetime.strptime(self.config.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(self.config.end_date, "%Y-%m-%d")
        interval = self.config.default_interval

        dates = self._get_spray_dates(start_date, end_date, interval)

        schedule = []
        for d in dates:
            stage_name = self._determine_stage_name(d)
            weights = self.config.stage_weights.get(stage_name, {})
            is_critical = stage_name in self.config.critical_stages
            
            growth_stage = GrowthStage(name=stage_name, disease_weights=weights, is_critical=is_critical)
            schedule.append(SprayEvent(date=d, growth_stage=growth_stage))

        return schedule

    def _get_spray_dates(self, start_date: datetime, end_date: datetime, interval: int) -> List[datetime]:
        dates = []
        d = start_date
        while d <= end_date:
            dates.append(d)
            d += timedelta(days=interval)
        return dates

    def _determine_stage_name(self, date: datetime) -> str:
        m = date.month
        if m <= 4: return "budbreak"
        if m == 5: return "pre-bloom"
        if m == 6: return "bloom"
        if m == 7: return "fruit-set"
        if m == 8: return "veraison"
        if m == 9: return "pre-harvest"
        return "post-harvest"
