"""
Extraction horaire : pour chaque ville, appelle l'API OpenWeather et sauvegarde
un CSV brut dans raw/<date>/. Ne doit jamais planter le job complet si une
ville échoue (try/except par ville, log de l'erreur, on continue).
"""

from datetime import datetime, timezone

from dotenv import load_dotenv

from config.cities import cities_coordinates
from functions.extract import extract_aqi_current
from functions.merge import save_raw

from pathlib import Path

load_dotenv()


def main():
    now = datetime.now(timezone.utc)
    run_date = now.strftime("%Y-%m-%d")
    label = now.strftime("%Hh")

    for city, (lat, lon) in cities_coordinates.items():
        if Path("raw") / run_date / f"aqi_{city.lower()}_{label}.csv".exists():
            print(f"[SKIP] {city} {label} (déjà présent)")
            continue
        try:
            df = extract_aqi_current(city, lat, lon)
            filepath = save_raw(df, city, run_date, label)
            print(f"[OK] {city} -> {filepath}")
        except Exception as e:
            print(f"[ERREUR] {city} : {e}")
            continue


if __name__ == "__main__":
    main()