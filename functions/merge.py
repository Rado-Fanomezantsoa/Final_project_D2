"""
Sauvegarde des fichiers bruts dans raw/, un fichier par ville et par appel.
raw/ n'est jamais modifié une fois écrit.
"""

from pathlib import Path

import pandas as pd

RAW_DIR = Path("raw")


def save_raw(df: pd.DataFrame, city: str, run_date: str, label: str) -> Path:
    """
    Écrit un DataFrame dans raw/<run_date>/aqi_<city>_<label>.csv

    run_date : date du jour d'exécution, format YYYY-MM-DD (nom du sous-dossier)
    label    : identifiant unique de l'appel, ex. l'heure ("14h") pour le hourly,
               ou la période couverte pour le backfill ("2026-04")
    """
    day_dir = RAW_DIR / run_date
    day_dir.mkdir(parents=True, exist_ok=True)

    filename = f"aqi_{city.lower()}_{label}.csv"
    filepath = day_dir / filename

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        df.to_csv(f, index=False)

    return filepath