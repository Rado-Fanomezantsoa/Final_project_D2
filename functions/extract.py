"""
Fonctions d'extraction des données de qualité de l'air via l'API
OpenWeatherMap Air Pollution.

Documentation : https://openweathermap.org/api/air-pollution
- Endpoint "current"  : /data/2.5/air_pollution
- Endpoint "history"  : /data/2.5/air_pollution/history
  (historique disponible depuis le 27/11/2020, start/end en timestamps Unix UTC)

Toutes les fonctions renvoient un pandas.DataFrame avec un schéma commun :
    city, lat, lon, datetime, aqi, co, no, no2, o3, so2, pm2_5, pm10, nh3

Note : le champ `aqi` renvoyé par OpenWeather est son propre indice interne
(échelle 1 à 5), pas l'AQI américain standard (0-500). À documenter dans le README.
"""

import os

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.openweathermap.org/data/2.5/air_pollution"
TIMEOUT = 30

COMPONENT_COLUMNS = ["co", "no", "no2", "o3", "so2", "pm2_5", "pm10", "nh3"]


def _get_api_key() -> str:
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Variable d'environnement OPENWEATHER_API_KEY manquante."
        )
    return api_key


def _response_to_dataframe(city: str, lat: float, lon: float, payload: dict) -> pd.DataFrame:
    """Transforme la réponse JSON OpenWeather en DataFrame au schéma standard."""
    rows = []
    for entry in payload.get("list", []):
        components = entry.get("components", {})
        row = {
            "city": city,
            "lat": lat,
            "lon": lon,
            "datetime": pd.to_datetime(entry["dt"], unit="s", utc=True),
            "aqi": entry.get("main", {}).get("aqi"),
        }
        for col in COMPONENT_COLUMNS:
            row[col] = components.get(col)
        rows.append(row)

    columns = ["city", "lat", "lon", "datetime", "aqi"] + COMPONENT_COLUMNS
    return pd.DataFrame(rows, columns=columns)


def extract_aqi_current(city: str, lat: float, lon: float) -> pd.DataFrame:
    """Récupère la mesure AQI actuelle pour une ville (1 ligne)."""
    api_key = _get_api_key()
    params = {"lat": lat, "lon": lon, "appid": api_key}

    response = requests.get(BASE_URL, params=params, timeout=TIMEOUT)
    response.raise_for_status()

    return _response_to_dataframe(city, lat, lon, response.json())


def extract_aqi_history(city: str, lat: float, lon: float, start_ts: int, end_ts: int) -> pd.DataFrame:
    """
    Récupère l'historique horaire AQI entre deux timestamps Unix (UTC).
    Utilisé pour le backfill, par tranches (ex : mois par mois).
    """
    api_key = _get_api_key()
    params = {
        "lat": lat,
        "lon": lon,
        "start": start_ts,
        "end": end_ts,
        "appid": api_key,
    }

    response = requests.get(f"{BASE_URL}/history", params=params, timeout=TIMEOUT)
    response.raise_for_status()

    return _response_to_dataframe(city, lat, lon, response.json())
