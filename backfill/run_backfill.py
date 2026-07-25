"""
Backfill de l'historique AQI pour toutes les villes, via l'API OpenWeather
Air Pollution History.

Rejouable : relancer ce script régénère les mêmes fichiers raw/ (mêmes noms),
sans dupliquer les appels déjà faits si tu ajoutes une vérification d'existence
(voir SKIP_EXISTING plus bas).

L'historique OpenWeather n'est disponible qu'à partir du 27/11/2020.
Découpage mois par mois pour limiter la taille de chaque appel/fichier
(cohérent avec la règle "un fichier par ville et par appel").

Usage :
    export OPENWEATHER_API_KEY=xxxx
    python -m backfill.run_backfill
"""

import calendar
from datetime import datetime, timezone

from config.cities import cities_coordinates
from functions.extract import extract_aqi_history
from functions.merge import save_raw

START_DATE = datetime(2026, 4, 24, tzinfo=timezone.utc)
END_DATE = datetime.now(timezone.utc)

SKIP_EXISTING = True


def month_chunks(start: datetime, end: datetime):
    """Génère des tuples (chunk_start, chunk_end, label) découpés mois par mois."""
    current = start.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    while current <= end:
        last_day = calendar.monthrange(current.year, current.month)[1]
        month_end = current.replace(day=last_day, hour=23, minute=59, second=59)

        chunk_start = max(current, start)
        chunk_end = min(month_end, end)
        label = current.strftime("%Y-%m")

        yield chunk_start, chunk_end, label

        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)


def main():
    print(f"Backfill du {START_DATE.date()} au {END_DATE.date()}")

    for city, (lat, lon) in cities_coordinates.items():
        for chunk_start, chunk_end, label in month_chunks(START_DATE, END_DATE):
            run_date = chunk_start.strftime("%Y-%m-%d")

            if SKIP_EXISTING:
                from pathlib import Path
                expected = Path("raw") / run_date / f"aqi_{city.lower()}_{label}.csv"
                if expected.exists():
                    print(f"[SKIP] {city} {label} (déjà présent)")
                    continue

            try:
                df = extract_aqi_history(
                    city, lat, lon,
                    start_ts=int(chunk_start.timestamp()),
                    end_ts=int(chunk_end.timestamp()),
                )
                filepath = save_raw(df, city, run_date, label)
                print(f"[OK] {city} {label} -> {filepath} ({len(df)} lignes)")
            except Exception as e:
                print(f"[ERREUR] {city} {label} : {e}")
                continue


if __name__ == "__main__":
    main()