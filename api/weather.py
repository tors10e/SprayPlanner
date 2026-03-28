from meteostat import Point, Daily
from datetime import datetime

# Location (example: Saratoga, WY area)
location = Point(41.45, -106.81)

start = datetime(2026, 4, 1)
end = datetime(2026, 9, 30)

data = Daily(location, start, end)
weather = data.fetch()

print(weather.head())
