import spray_config
from datetime import datetime, timedelta
import pandas as pd
import helpers



def get_spray_dates(start_date, end_date, interval):
    dates = []
    d = start_date
    while d <= end_date:
        dates.append(d)
        d += timedelta(days=interval)
    return dates


def build_schedule():
    start_date = datetime.strptime(spray_config.START_DATE, "%Y-%m-%d")
    end_date = datetime.strptime(spray_config.END_DATE, "%Y-%m-%d")
    interval = spray_config.DEFAULT_INTERVAL

    dates = get_spray_dates(start_date, end_date, interval)

    schedule = []
    for d in dates:
        stage = helpers.determine_stage(d)
        weights = spray_config.stage_weights.get(stage, {})
        schedule.append({"date": d.strftime("%Y-%m-%d"), "stage": stage, "stage_weights": weights})

    return schedule

# build_schedule()

# schedule = [
#     {"date": "2025-04-15", "stage": "shoot_10cm",
#      "stage_weights": {"PM": 0.3, "DM": 0.2}},

#     {"date": "2025-05-10", "stage": "pre_bloom",
#      "stage_weights": {"PM": 1.0, "DM": 1.0, "Botrytis": 0.6}},

#     {"date": "2025-05-25", "stage": "bloom",
#      "stage_weights": {"PM": 1.0, "DM": 1.0, "Botrytis": 1.0}},

#     {"date": "2025-06-10", "stage": "fruit_set",
#      "stage_weights": {"PM": 0.9, "DM": 0.9}},

