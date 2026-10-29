"""cleaning.py - Nettoyage du fichier eco2mix-regional-cons-def.csv.

Operations effectuees :
  1. Chargement et normalisation des colonnes (BOM, espacements)
  2. Suppression des colonnes fantomes (100% NaN ou generiques du type column_*)
  3. Remplacement des valeurs manquantes deguisees (chaines vides, "nan", "nr", etc.)
  4. Conversion des types (25 metriques numeriques en float, separateur decimal)
  5. Conversion des dates (date, heure, date_heure tz-aware Europe/Paris)
  6. Normalisation du code INSEE region
  7. Traitement des valeurs -1 d'absence pour filieres strictement non negatives
  8. Suppression des doublons exacts et fonctionnels (meme region x meme creneau)
  9. Rapport qualite post-nettoyage et export CSV

Usage :
    python src/cleaning.py
"""

import logging
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Configuration des chemins
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# Recherche automatique dans data/raw/ puis a la racine du projet
DEFAULT_RAW = BASE_DIR / "data" / "raw" / "eco2mix-regional-cons-def.csv"
FALLBACK_RAW = BASE_DIR / "eco2mix-regional-cons-def.csv"
RAW_FILE = DEFAULT_RAW if DEFAULT_RAW.exists() else FALLBACK_RAW

CLEAN_FILE = BASE_DIR / "eco2mix-regional-cons-def_clean.csv"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# Valeurs textuelles considerees comme valeurs manquantes deguisees
FAKE_NULL_STRINGS = {
    "",
    "nan",
    "none",
    "null",
    "n/a",
    "na",
    "nd",
    "non renseigne",
    "non renseigné",
    "nr",
    "#n/a",
    "-",
    "n/d",
}

# Colonnes non numeriques connues (tout le reste est considere numerique)
NON_NUMERIC_COLS = {
    "code_insee_region",
    "libelle_region",
    "nature",
    "date",
    "heure",
    "date_heure",
}

# Colonnes physiques pouvant legitimement avoir des valeurs negatives
LEGIT_NEGATIVE_COLS = {
    "pompage",
    "ech_physiques",
    "pompage (mw)",
    "ech. physiques (mw)",
}


# ---------------------------------------------------------------------------
# 1. Chargement
# ---------------------------------------------------------------------------
def load_raw(path: str | Path) -> pd.DataFrame:
    """Charge le fichier brut CSV en utilisant utf-8-sig pour retirer le BOM."""
    log.info("Chargement du fichier brut : %s", path)
    df = pd.read_csv(
        path,
        sep=";",
        encoding="utf-8-sig",
        low_memory=False,
        dtype=str,  # tout en str pour detection fine des valeurs deguisees
    )
    # Nettoyage des noms de colonnes (espaces et BOM eventuel)
    df.columns = df.columns.str.replace(r"^\ufeff", "", regex=True).str.strip()
    log.info("Fichier charge : %d lignes x %d colonnes", *df.shape)
    return df


# ---------------------------------------------------------------------------
# 2. Colonnes 100% vides (fantomes) et colonnes generiques sans metier
# ---------------------------------------------------------------------------
def drop_ghost_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Supprime les colonnes totalement vides ou generiques (ex: column_30)."""
    all_null = df.columns[df.isnull().all()].tolist()
    generic = [
        c
        for c in df.columns
        if c.lower().startswith("column ") or c.lower().startswith("column_")
    ]
    to_drop = list(set(all_null + generic))
    if to_drop:
        log.info("Colonnes fantomes supprimees : %s", to_drop)
        df = df.drop(columns=to_drop)
    else:
        log.info("Aucune colonne fantome detectee.")
    return df


# ---------------------------------------------------------------------------
# 3. Valeurs manquantes deguisees dans les colonnes texte
# ---------------------------------------------------------------------------
def clean_fake_nulls(df: pd.DataFrame) -> pd.DataFrame:
    """Remplace les valeurs vides ou deguisees ("n/a", "nr", etc.) par NaN."""
    # Compatibilite pandas 2 et 3 sans avertissement select_dtypes
    str_cols = df.select_dtypes(include=["object", "string"]).columns
    count = 0
    for col in str_cols:
        mask = df[col].str.strip().str.lower().isin(FAKE_NULL_STRINGS)
        count += int(mask.sum())
        df.loc[mask, col] = np.nan
    log.info("Valeurs manquantes deguisees remplacees : %d cellules", count)
    return df


# ---------------------------------------------------------------------------
# 4. Conversion des types
# ---------------------------------------------------------------------------
def cast_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """Convertit toutes les colonnes metriques en float (gere ',' et '.')."""
    numeric_candidates = [
        c
        for c in df.columns
        if c.lower() not in NON_NUMERIC_COLS
        and not (
            c.lower().startswith("column ") or c.lower().startswith("column_")
        )
    ]
    for col in numeric_candidates:
        if df[col].dtype == object or df[col].dtype == "string":
            df[col] = df[col].str.replace(",", ".", regex=False)
        df[col] = pd.to_numeric(df[col], errors="coerce")
    log.info("Colonnes numeriques converties : %d colonnes", len(numeric_candidates))
    return df


def cast_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Convertit date, verifie heure et parse date_heure en Europe/Paris."""
    col_map = {c.lower(): c for c in df.columns}

    # Colonne 'date'
    if "date" in col_map:
        col = col_map["date"]
        df[col] = pd.to_datetime(df[col], format="%Y-%m-%d", errors="coerce")
        log.info("Colonne '%s' -> datetime.", col)

    # Colonne 'heure'
    if "heure" in col_map:
        col = col_map["heure"]
        bad = df[col].notna() & ~df[col].astype(str).str.match(r"^\d{2}:\d{2}$")
        if bad.any():
            log.warning("'%s' : %d valeurs au format inattendu", col, bad.sum())

    # Colonne 'date_heure' ou 'date - heure'
    col_dh = None
    for cand in ["date_heure", "date - heure", "dateheure"]:
        if cand in col_map:
            col_dh = col_map[cand]
            break

    if col_dh:
        df[col_dh] = pd.to_datetime(df[col_dh], utc=True, errors="coerce")
        df[col_dh] = df[col_dh].dt.tz_convert("Europe/Paris")
        log.info(
            "Colonne '%s' -> datetime tz-aware (Europe/Paris).",
            col_dh,
        )

    return df


def cast_code_insee(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise le Code INSEE region en str (preserve les zeros initiaux)."""
    candidates = [c for c in df.columns if "insee" in c.lower()]
    if not candidates:
        log.warning("Aucune colonne Code INSEE trouvee.")
        return df
    col = candidates[0]
    df[col] = df[col].astype(str).str.strip()
    non_num = df[col].notna() & ~df[col].str.match(r"^\d+$")
    if non_num.any():
        log.warning("Code INSEE : %d valeurs non numeriques.", non_num.sum())
    log.info("Colonne '%s' normalisee en str.", col)
    return df


# ---------------------------------------------------------------------------
# 5. Valeurs -1 codant une absence (convention eco2mix)
# ---------------------------------------------------------------------------
def flag_minus_one(df: pd.DataFrame) -> pd.DataFrame:
    """Remplace -1 par NaN pour les filieres strictement positives."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    count = 0
    for col in numeric_cols:
        # On preserve les colonnes ou le negatif est reel (ex: pompage, ech_physiques)
        if col.lower() in LEGIT_NEGATIVE_COLS:
            continue
        mask = df[col] == -1
        count += int(mask.sum())
        df.loc[mask, col] = np.nan
    if count:
        log.info("Valeurs -1 (absence codee) -> NaN : %d cellules.", count)
    else:
        log.info("Aucune valeur -1 codant une absence trouvee.")
    return df


# ---------------------------------------------------------------------------
# 6. Doublons
# ---------------------------------------------------------------------------
def remove_exact_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Supprime les doublons de lignes identiques a 100%."""
    n = df.duplicated().sum()
    df = df.drop_duplicates()
    log.info("Doublons exacts supprimes : %d", n)
    return df


def remove_functional_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Meme (Code INSEE, Date_Heure) -> conserve 'Donnees definitives' en priorite."""
    col_map = {c.lower(): c for c in df.columns}
    candidates_insee = [c for c in df.columns if "insee" in c.lower()]

    col_dh = None
    for cand in ["date_heure", "date - heure", "dateheure"]:
        if cand in col_map:
            col_dh = col_map[cand]
            break

    if not candidates_insee or not col_dh:
        log.warning("Colonnes cles absentes -> deduplication fonctionnelle ignoree.")
        return df

    col_region = candidates_insee[0]
    key = [col_region, col_dh]
    n_before = len(df)

    order = {
        "donnees consolidees": 0,
        "données consolidées": 0,
        "donnees definitives": 1,
        "données définitives": 1,
    }

    col_nature = col_map.get("nature")
    if col_nature:
        df = df.copy()
        df["_rank"] = (
            df[col_nature]
            .astype(str)
            .str.lower()
            .str.strip()
            .map(order)
            .fillna(0)
            .astype(int)
        )
        df = df.sort_values(key + ["_rank"]).drop_duplicates(
            subset=key, keep="last"
        )
        df = df.drop(columns=["_rank"])
    else:
        df = df.drop_duplicates(subset=key, keep="last")

    log.info("Doublons fonctionnels supprimes : %d (cle : %s)", n_before - len(df), key)
    return df


# ---------------------------------------------------------------------------
# 7. Rapport qualite
# ---------------------------------------------------------------------------
def quality_report(df: pd.DataFrame) -> None:
    """Affiche un resume synthétique de la qualite des donnees nettoyees."""
    log.info("=== RAPPORT QUALITE POST-NETTOYAGE ===")
    log.info("Dimensions : %d lignes x %d colonnes", *df.shape)
    missing = df.isnull().sum()
    pct = (missing / len(df) * 100).round(2)
    report = pd.DataFrame({"Nb NaN": missing, "% NaN": pct})
    report = report[report["Nb NaN"] > 0].sort_values("% NaN", ascending=False)
    if report.empty:
        log.info("Aucune valeur manquante residuelle.")
    else:
        log.info("Valeurs manquantes residuelles :\n%s", report.to_string())
    log.info("Doublons residuels : %d", df.duplicated().sum())
    log.info("=== FIN DU RAPPORT ===")


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------
def clean_pipeline(
    raw_path: str | Path = RAW_FILE,
    clean_path: str | Path = CLEAN_FILE,
) -> pd.DataFrame:
    """Execute la totalite du pipeline de nettoyage et exporte le resultat."""
    raw_path = Path(raw_path)
    clean_path = Path(clean_path)

    if not raw_path.exists():
        raise FileNotFoundError(
            f"Fichier brut introuvable : {raw_path}. "
            "Executez d'abord python src/download.py pour le telecharger."
        )

    df = load_raw(raw_path)
    df = drop_ghost_columns(df)
    df = clean_fake_nulls(df)
    df = cast_numeric(df)
    df = cast_dates(df)
    df = cast_code_insee(df)
    df = flag_minus_one(df)
    df = remove_exact_duplicates(df)
    df = remove_functional_duplicates(df)
    quality_report(df)

    clean_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = clean_path.with_suffix(".csv.tmp")
    log.info("Export -> %s", clean_path)
    df.to_csv(tmp_path, sep=";", index=False, encoding="utf-8-sig")
    if clean_path.exists():
        try:
            clean_path.unlink()
        except OSError:
            pass
    tmp_path.replace(clean_path)
    log.info("Export termine avec succes.")
    return df


if __name__ == "__main__":
    clean_pipeline()
