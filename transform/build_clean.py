import sys
import glob
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import pandas as pd
from config.cities import cities_coordinates

RAW_DIR = "raw"
OUTPUT_PATH = "clean/final.csv"


CITY_COUNTRY = {
    "Antananarivo": "Madagascar",
    "Paris": "France",
    "London": "United Kingdom",
    "Washington": "United States",
    "Moscow": "Russia",
}

COLUMNS_ORDER = [
    "city", "country", "lat", "lon", "datetime", "aqi",
    "co", "no", "no2", "o3", "so2", "pm2_5", "pm10", "nh3",
]

def load_all_raw():
    csv_files = glob.glob(f"{RAW_DIR}/**/*.csv", recursive=True)
    if not csv_files:
        raise FileNotFoundError("Aucun fichier CSV trouvé dans raw/")
    dfs = [pd.read_csv(f) for f in csv_files]
    return pd.concat(dfs, ignore_index=True)

def build_clean():
    df = load_all_raw()

    df["datetime"] = pd.to_datetime(df["datetime"], utc=True)

    
    df["city"] = df["city"].str.strip()

    
    df["lat"] = df["city"].map(lambda c: cities_coordinates.get(c, (None, None))[0])
    df["lon"] = df["city"].map(lambda c: cities_coordinates.get(c, (None, None))[1])
    df["country"] = df["city"].map(CITY_COUNTRY)

    missing = df[df["country"].isna()]["city"].unique()
    if len(missing) > 0:
        print(f" Villes sans correspondance : {missing}")

    df["hour_bucket"] = df["datetime"].dt.floor("h")
    df = df.sort_values(["datetime"]).drop_duplicates(
        subset=["city", "hour_bucket"], keep="last"
    )

    df = df.drop(columns=["hour_bucket"])
    df = df.sort_values(["datetime", "city"]).reset_index(drop=True)
    df = df[COLUMNS_ORDER]

    Path("clean").mkdir(exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"{len(df)} lignes écrites dans {OUTPUT_PATH}")
    print(f"Villes : {sorted(df['city'].unique())}")
    print(f"Période : {df['datetime'].min()} → {df['datetime'].max()}")

if __name__ == "__main__":
    build_clean()
