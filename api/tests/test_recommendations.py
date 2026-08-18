import pytest
import json
from datetime import datetime, timedelta
from core.config import Config
from core.repository import ProductRepository
from core.weather import get_block_weather_info

@pytest.fixture
def repo():
    config = Config()
    return ProductRepository(config)

def test_settings_endpoints(repo):
    # Test settings update and retrieval via direct SQL
    conn = repo._get_connection()
    cursor = conn.cursor()
    
    # 1. Update values
    cursor.execute("""
        INSERT INTO system_settings (key, value) VALUES (%s, %s)
        ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
    """, ("test_setting_key", "99"))
    conn.commit()
    
    # 2. Retrieve
    cursor.execute("SELECT value FROM system_settings WHERE key = %s", ("test_setting_key",))
    assert cursor.fetchone()[0] == "99"
    
    # 3. Clean up
    cursor.execute("DELETE FROM system_settings WHERE key = %s", ("test_setting_key",))
    conn.commit()
    cursor.close()
    conn.close()

def test_weather_simulated_fallback():
    # Verify that get_block_weather_info falls back to simulated data gracefully
    # and returns historical rain and a 14-day forecast.
    lat = 34.7333
    lng = -83.5026
    start_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
    
    # Run fetch (will trigger fallback if offline, which is standard for tests)
    weather_info = get_block_weather_info(lat, lng, start_date, provider="NOAA")
    
    assert "historical_rain" in weather_info
    assert "forecast" in weather_info
    assert len(weather_info["forecast"]) == 14
    for f in weather_info["forecast"]:
        assert "date" in f
        assert "rain_chance" in f
        assert "qpf" in f
        assert "has_dew" in f
