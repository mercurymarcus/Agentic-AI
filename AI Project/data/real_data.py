import openmeteo_requests
import requests_cache
import pandas as pd
import numpy as np
from retry_requests import retry
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
# GHANA LOCATION — Accra coordinates
# ─────────────────────────────────────────────
GHANA_LAT = 5.6037
GHANA_LON = -0.1870
LOCATION_NAME = "Accra, Ghana"

def get_real_energy_data(start_date=None, end_date=None, days=30):
    """
    Fetches real weather data from Open-Meteo API for Ghana.
    Accepts either a date range (start_date, end_date) or number of days.

    Converts weather variables into energy output in MW:
    Solar  — from real solar radiation data (W/m²)
    Wind   — from real wind speed data (km/h → m/s)
    Hydro  — modelled from real rainfall with Akosombo base (1580 MW)

    Returns: DataFrame with columns [timestamp, source, output_mw]
    """

    # Setup API client with caching
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Work out date range
    if start_date and end_date:
        start = pd.Timestamp(start_date)
        end = pd.Timestamp(end_date)
        delta_days = (end - start).days + 1
    else:
        start = pd.Timestamp.now().normalize()
        delta_days = days
        end = start + pd.Timedelta(days=delta_days - 1)

    # API only supports max 16 days forecast
    fetch_days = min(delta_days, 16)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": GHANA_LAT,
        "longitude": GHANA_LON,
        "hourly": [
            "shortwave_radiation",
            "windspeed_10m",
            "precipitation",
            "temperature_2m"
        ],
        "timezone": "Africa/Accra",
        "forecast_days": fetch_days
    }

    try:
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]

        hourly = response.Hourly()
        hourly_solar_rad   = hourly.Variables(0).ValuesAsNumpy()
        hourly_wind_speed  = hourly.Variables(1).ValuesAsNumpy()
        hourly_precip      = hourly.Variables(2).ValuesAsNumpy()
        hourly_temperature = hourly.Variables(3).ValuesAsNumpy()

        time_index = pd.date_range(
            start=pd.Timestamp(hourly.Time(), unit="s", tz="Africa/Accra"),
            end=pd.Timestamp(hourly.TimeEnd(), unit="s", tz="Africa/Accra"),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )

        n = len(time_index)

        # ── SOLAR OUTPUT ──
        panel_efficiency = 0.18
        solar_capacity_mw = 186
        solar_radiation_normalized = hourly_solar_rad / 1000
        temperature_factor = 1 - 0.004 * (hourly_temperature - 25)
        solar_output_mw = (
            solar_radiation_normalized *
            panel_efficiency *
            solar_capacity_mw *
            temperature_factor
        )
        solar_output_mw = np.maximum(0, solar_output_mw[:n])

        # ── WIND OUTPUT ──
        wind_speed_ms = hourly_wind_speed / 3.6
        wind_output_mw = np.minimum(wind_speed_ms ** 3 * 0.5, 100)
        wind_output_mw = np.maximum(0, wind_output_mw[:n])

        # ── HYDRO OUTPUT ──
        base_hydro = 1580
        rainfall_factor = np.clip(hourly_precip[:n] * 10, -200, 200)
        noise = np.random.normal(0, 30, size=n)
        hydro_output_mw = np.maximum(0, base_hydro + rainfall_factor + noise)

        # ── BUILD COMBINED DATAFRAME ──
        solar_df = pd.DataFrame({
            "timestamp": time_index,
            "source": "Solar",
            "output_mw": solar_output_mw
        })

        wind_df = pd.DataFrame({
            "timestamp": time_index,
            "source": "Wind",
            "output_mw": wind_output_mw
        })

        hydro_df = pd.DataFrame({
            "timestamp": time_index,
            "source": "Hydro",
            "output_mw": hydro_output_mw
        })

        combined = pd.concat([solar_df, wind_df, hydro_df], ignore_index=True)
        combined = combined.sort_values("timestamp").reset_index(drop=True)
        combined["timestamp"] = combined["timestamp"].dt.tz_localize(None)

        return combined, LOCATION_NAME

    except Exception as e:
        print(f"⚠️ Real data fetch failed: {e}")
        return None, None


def get_real_summary(start_date=None, end_date=None, days=30):
    
    df, location = get_real_energy_data(
        start_date=start_date,
        end_date=end_date,
        days=days
    )

    if df is None:
        return None, None

    summary = df.groupby("source")["output_mw"].agg(
        ["sum", "mean", "max"]
    ).round(2)
    summary.columns = ["Total mw", "Avg mw/hr", "Peak mw"]

    return summary, location