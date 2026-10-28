"""Téléchargement des données éCO2mix régional consolidé et définitif (RTE / ODRE)."""

from pathlib import Path

import requests

URL = (
    "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/"
    "eco2mix-regional-cons-def/exports/csv"
)
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
CSV_PATH = RAW_DIR / "eco2mix-regional-cons-def.csv"


def download(force: bool = False) -> Path:
    """Télécharge le CSV dans data/raw/ s'il n'est pas déjà présent."""
    if CSV_PATH.exists() and not force:
        print(f"Fichier déjà présent : {CSV_PATH}")
        return CSV_PATH

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Téléchargement depuis {URL} ...")
    with requests.get(URL, stream=True, timeout=60) as response:
        response.raise_for_status()
        with open(CSV_PATH, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)

    print(f"Fichier enregistré : {CSV_PATH}")
    return CSV_PATH


if __name__ == "__main__":
    download()
