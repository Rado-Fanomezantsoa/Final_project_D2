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


def build_fact(df: pd.DataFrame, dim_city: pd.DataFrame, dim_time: pd.DataFrame) -> pd.DataFrame:
    fact = df.merge(dim_city[["city_id", "city", "country"]], on=["city", "country"], how="left")
    fact = fact.merge(
        dim_time[["time_id", "full_datetime"]],
        left_on="hour_bucket",
        right_on="full_datetime",
        how="left",
    )
    fact = fact.rename(columns={"datetime": "observed_at"})
    fact = fact[["city_id", "time_id", "observed_at"] + POLLUTANT_COLUMNS]
    fact = fact.sort_values(["time_id", "city_id"]).reset_index(drop=True)
    fact.insert(0, "fact_id", range(1, len(fact) + 1))
    return fact


def write_csv_outputs(dim_city: pd.DataFrame, dim_time: pd.DataFrame, fact: pd.DataFrame) -> None:
    WAREHOUSE_DIR.mkdir(exist_ok=True)
    dim_city.to_csv(WAREHOUSE_DIR / "dim_city.csv", index=False)
    dim_time.to_csv(WAREHOUSE_DIR / "dim_time.csv", index=False)
    fact.to_csv(WAREHOUSE_DIR / "fact_air_quality.csv", index=False)
    print(f"[OK] dim_city.csv          : {len(dim_city)} lignes")
    print(f"[OK] dim_time.csv          : {len(dim_time)} lignes")
    print(f"[OK] fact_air_quality.csv  : {len(fact)} lignes")


def load_to_postgres(dim_city: pd.DataFrame, dim_time: pd.DataFrame, fact: pd.DataFrame) -> None:
    """Charge les 3 tables dans PostgreSQL si les identifiants sont présents
    dans .env (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD). Ne plante
    pas le script si la base n'est pas accessible : log l'erreur et continue.
    """
    load_dotenv()
    required = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    if not all(os.getenv(v) for v in required):
        print("[SKIP] Variables PostgreSQL absentes de .env : chargement DB ignoré.")
        return

    from sqlalchemy import create_engine, text

    url = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        f"?sslmode=require"  # obligatoire pour Neon (et bonne pratique en général)
    )
    engine = create_engine(url)

    try:
        with engine.begin() as conn:
            schema_sql = (WAREHOUSE_DIR / "schema.sql").read_text(encoding="utf-8")
            conn.execute(text(schema_sql))

        dim_city.to_sql("dim_city", engine, if_exists="append", index=False)
        dim_time.to_sql("dim_time", engine, if_exists="append", index=False)
        fact.to_sql("fact_air_quality", engine, if_exists="append", index=False)
        print("[OK] Warehouse chargé dans PostgreSQL.")
    except Exception as e:
        print(f"[ERREUR] Chargement PostgreSQL : {e}")


def print_coherence_report(dim_city: pd.DataFrame, dim_time: pd.DataFrame, fact: pd.DataFrame) -> None:
    expected = len(dim_city) * len(dim_time)
    actual = len(fact)
    missing = expected - actual
    print()
    print("--- Rapport de cohérence ---")
    print(f"Villes x heures attendues : {len(dim_city)} x {len(dim_time)} = {expected}")
    print(f"Lignes réelles dans fact_air_quality : {actual}")
    print(f"Écart : {missing} observation(s) manquante(s) ({missing / expected:.2%})")


def build_warehouse(load_db: bool = True):
    df = load_clean()
    dim_city = build_dim_city(df)
    dim_time = build_dim_time(df)
    fact = build_fact(df, dim_city, dim_time)

    write_csv_outputs(dim_city, dim_time, fact)
    print_coherence_report(dim_city, dim_time, fact)

    if load_db:
        load_to_postgres(dim_city, dim_time, fact)

    return dim_city, dim_time, fact


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-load", action="store_true", help="Ne pas charger dans PostgreSQL")
    args = parser.parse_args()
    build_warehouse(load_db=not args.no_load)