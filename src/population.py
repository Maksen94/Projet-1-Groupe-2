"""population.py - Intégration des données démographiques INSEE et analyse de consommation par habitant.

Ce module permet de :
1. Charger ou générer le référentiel des 12 populations régionales INSEE (satisfait GIT-04 et issue #12).
2. Charger les données nettoyées de consommation régionale éCO2mix (RTE).
3. Calculer la consommation électrique cumulée mensuelle par habitant (MWh / habitant).
4. Produire un graphique comparatif mensuel accessible (palette viridis, sources explicitées).
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# ---------------------------------------------------------------------------
# Configuration des chemins dynamiques (compatibles toute racine d'exécution)
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"

DEFAULT_INSEE_FILE = DATA_RAW_DIR / "insee_population_regions.csv"
DEFAULT_CONSO_PARQUET = (
    DATA_PROCESSED_DIR / "eco2mix-regional-cons-def_clean.parquet"
)
DEFAULT_CONSO_CSV = DATA_PROCESSED_DIR / "eco2mix-regional-cons-def_clean.csv"
DEFAULT_OUTPUT_PLOT = DATA_PROCESSED_DIR / "comparaison_conso_habitant.png"

# ---------------------------------------------------------------------------
# Référentiel INSEE officiel : 12 régions administratives métropolitaines
# Source : Recensement de la population légale INSEE 2021 (en vigueur au 01/01/2024)
# Conforme à l'issue #12 et à l'exigence GIT-04 (régénération automatique)
# ---------------------------------------------------------------------------
INSEE_POPULATION_REGIONS = {
    "11": {"Région": "Île-de-France", "Population": 12419961},
    "84": {"Région": "Auvergne-Rhône-Alpes", "Population": 8160074},
    "76": {"Région": "Occitanie", "Population": 6053540},
    "75": {"Région": "Nouvelle-Aquitaine", "Population": 6069352},
    "32": {"Région": "Hauts-de-France", "Population": 5997687},
    "44": {"Région": "Grand Est", "Population": 5562651},
    "93": {"Région": "Provence-Alpes-Côte d'Azur", "Population": 5127840},
    "52": {"Région": "Pays de la Loire", "Population": 3873096},
    "53": {"Région": "Bretagne", "Population": 3424892},
    "28": {"Région": "Normandie", "Population": 3325522},
    "27": {"Région": "Bourgogne-Franche-Comté", "Population": 2795301},
    "24": {"Région": "Centre-Val de Loire", "Population": 2573295},
}


def get_or_create_insee_population(file_path: Path | None = None) -> pd.DataFrame:
    """Charge les populations régionales INSEE ou génère le CSV s'il est absent."""
    target_path = file_path or DEFAULT_INSEE_FILE

    if not target_path.exists():
        target_path.parent.mkdir(parents=True, exist_ok=True)
        rows = [
            {
                "Code INSEE région": code,
                "Région": info["Région"],
                "Population": info["Population"],
            }
            for code, info in INSEE_POPULATION_REGIONS.items()
        ]
        df_insee = pd.DataFrame(rows)
        df_insee.to_csv(target_path, index=False)
    else:
        df_insee = pd.read_csv(target_path)

    df_insee["Code INSEE région"] = (
        df_insee["Code INSEE région"].astype(str).str.strip()
    )
    df_insee["Population"] = pd.to_numeric(
        df_insee["Population"].astype(str).str.replace(",", "."),
        errors="coerce",
    )
    return df_insee[["Code INSEE région", "Région", "Population"]]


def load_clean_consumption(file_path: Path | None = None) -> pd.DataFrame:
    """Charge le jeu de données nettoyé éCO2mix (Parquet prioritaire, CSV en secours)."""
    if file_path:
        target_path = file_path
    elif DEFAULT_CONSO_PARQUET.exists():
        target_path = DEFAULT_CONSO_PARQUET
    elif DEFAULT_CONSO_CSV.exists():
        target_path = DEFAULT_CONSO_CSV
    else:
        raise FileNotFoundError(
            f"Aucun jeu de données nettoyé trouvé dans {DATA_PROCESSED_DIR}. "
            "Veuillez exécuter préalablement 'python src/cleaning.py'."
        )

    if target_path.suffix == ".parquet":
        conso_df = pd.read_parquet(target_path)
    else:
        # Tente la détection du séparateur usuel pour éCO2mix
        conso_df = pd.read_csv(target_path, sep=";")

    conso_df = conso_df.drop(columns=["Région"], errors="ignore")
    conso_df["Code INSEE région"] = (
        conso_df["Code INSEE région"].astype(str).str.strip()
    )
    conso_df["Consommation (MW)"] = pd.to_numeric(
        conso_df["Consommation (MW)"].astype(str).str.replace(",", "."),
        errors="coerce",
    )
    return conso_df


def compute_monthly_consumption_per_capita(
    conso_df: pd.DataFrame,
    pop_df: pd.DataFrame,
    target_region_codes: list[str] | None = None,
) -> pd.DataFrame:
    """Calcule le cumul mensuel de consommation électrique par habitant (MWh / habitant)."""
    if target_region_codes is None:
        # Codes cibles : 11 (IDF), 84 (Auvergne-Rhône-Alpes), 76 (Occitanie)
        target_region_codes = ["11", "84", "76"]

    merged_df = pd.merge(conso_df, pop_df, on="Code INSEE région", how="inner")

    df_filtered = merged_df[
        merged_df["Code INSEE région"].isin(target_region_codes)
    ].copy()

    # Règle métrologique : Puissance (MW) sur un créneau de 30 min = Énergie (MWh) * 0.5
    df_filtered["Conso (MWh)"] = df_filtered["Consommation (MW)"] * 0.5
    df_filtered["Conso par habitant (MWh)"] = (
        df_filtered["Conso (MWh)"] / df_filtered["Population"]
    )

    df_filtered["Mois"] = pd.to_datetime(df_filtered["Date"]).dt.to_period("M")

    # Agrégation mensuelle par cumul (.sum()) pour obtenir le total mensuel par habitant
    conso_mensuelle = (
        df_filtered.groupby(["Mois", "Région"])["Conso par habitant (MWh)"]
        .sum()
        .unstack()
    )
    conso_mensuelle.index = conso_mensuelle.index.astype(str)
    return conso_mensuelle


def plot_monthly_consumption_per_capita(
    monthly_conso: pd.DataFrame,
    output_path: Path | None = None,
) -> None:
    """Génère et sauvegarde le graphique comparatif mensuel avec une palette accessible."""
    save_path = output_path or DEFAULT_OUTPUT_PLOT
    save_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(11, 6))

    # Palette accessible au daltonisme (viridis)
    monthly_conso.plot(
        kind="line",
        marker="o",
        colormap="viridis",
        linewidth=2,
        ax=ax,
    )

    # Titre avec constat métier explicite et rappel des sources officielles
    ax.set_title(
        "Évolution mensuelle de la consommation électrique par habitant\n"
        "Forte saisonnalité hivernale et disparités régionales | "
        "Sources : RTE (éCO2mix) & INSEE",
        fontsize=12,
        fontweight="bold",
        pad=15,
    )
    ax.set_xlabel("Mois", fontsize=10, labelpad=10)
    ax.set_ylabel(
        "Consommation cumulée mensuelle (MWh / habitant)",
        fontsize=10,
        labelpad=10,
    )
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(title="Régions étudiées", frameon=True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(save_path, dpi=300)
    plt.close(fig)


def main() -> None:
    """Point d'entrée du pipeline de comparaison démographique."""
    print("1/4 Chargement / vérification du référentiel population INSEE...")
    pop_df = get_or_create_insee_population()

    print("2/4 Chargement des données nettoyées éCO2mix...")
    conso_df = load_clean_consumption()

    print("3/4 Calcul du cumul mensuel de consommation par habitant...")
    monthly_conso = compute_monthly_consumption_per_capita(conso_df, pop_df)

    print(
        f"4/4 Génération du graphique comparatif dans {DEFAULT_OUTPUT_PLOT}..."
    )
    plot_monthly_consumption_per_capita(monthly_conso)
    print("Traitement terminé avec succès.")


if __name__ == "__main__":
    main()
