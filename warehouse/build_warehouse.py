import argparse
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

CLEAN_PATH = Path("clean/final.csv")
WAREHOUSE_DIR = Path("warehouse")

DAY_NAMES_FR = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

POLLUTANT_COLUMNS = ["aqi", "co", "no", "no2", "o3", "so2", "pm2_5", "pm10", "nh3"]


def load_clean() -> pd.DataFrame:
    if not CLEAN_PATH.exists():
        raise FileNotFoundError(
            f"{CLEAN_PATH} introuvable : lance d'abord transform/build_clean.py"
        )
    df = pd.read_csv(CLEAN_PATH)
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
    df["hour_bucket"] = df["datetime"].dt.floor("h")
    return df


def build_dim_city(df: pd.DataFrame) -> pd.DataFrame:
    dim_city = (
        df[["city", "country", "lat", "lon"]]
        .drop_duplicates(subset=["city", "country"])
        .sort_values("city")
        .reset_index(drop=True)
        .rename(columns={"lat": "latitude", "lon": "longitude"})
    )
    dim_city.insert(0, "city_id", range(1, len(dim_city) + 1))
    return dim_city


def build_dim_time(df: pd.DataFrame) -> pd.DataFrame:
    hours = df["hour_bucket"].drop_duplicates().sort_values().reset_index(drop=True)
    dim_time = pd.DataFrame({"full_datetime": hours})
    dim_time.insert(0, "time_id", range(1, len(dim_time) + 1))
    dim_time["date"] = dim_time["full_datetime"].dt.date
    dim_time["hour"] = dim_time["full_datetime"].dt.hour
    dim_time["day_of_week"] = dim_time["full_datetime"].dt.dayofweek  # 0=lundi
    dim_time["day_name"] = dim_time["day_of_week"].map(lambda i: DAY_NAMES_FR[i])
    dim_time["is_weekend"] = dim_time["day_of_week"].isin([5, 6])
    dim_time["day"] = dim_time["full_datetime"].dt.day
    dim_time["month"] = dim_time["full_datetime"].dt.month
    dim_time["year"] = dim_time["full_datetime"].dt.year
    return dim_time