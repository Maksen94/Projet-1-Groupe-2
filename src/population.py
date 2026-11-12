import matplotlib.pyplot as plt
import pandas as pd

# 1. Chargement et nettoyage des données de consommation
conso_df = pd.read_parquet(
    "data/processed/eco2mix-regional-cons-def_clean.parquet"
)
conso_df = conso_df.drop(columns=["Région"], errors="ignore")

# 2. Chargement des données de population INSEE
pop_df = pd.read_csv("data/raw/insee_population_regions.csv")[
    ["Code INSEE région", "Région", "Population"]
]

# 3. Harmonisation du type pour la fusion
conso_df["Code INSEE région"] = (
    conso_df["Code INSEE région"].astype(str).str.strip()
)
pop_df["Code INSEE région"] = pop_df["Code INSEE région"].astype(str).str.strip()

# 4. Jointure des deux tables
merged_df = pd.merge(conso_df, pop_df, on="Code INSEE région", how="inner")

# 5. Conversion numérique des colonnes
merged_df["Consommation (MW)"] = pd.to_numeric(
    merged_df["Consommation (MW)"].astype(str).str.replace(",", "."),
    errors="coerce",
)
merged_df["Population"] = pd.to_numeric(
    merged_df["Population"].astype(str).str.replace(",", "."), errors="coerce"
)

# 6. Application de la règle métrologique
merged_df["Conso par habitant"] = (
    merged_df["Consommation (MW)"] * 0.5
) / merged_df["Population"]
merged_df["Conso par habitant"] = pd.to_numeric(
    merged_df["Conso par habitant"], errors="coerce"
)

# 7. Filtrage sur les codes INSEE cibles (11 : IDF, 84 : ARA, 76 : Occitanie)
codes_cibles = ["11", "84", "76"]
df_filtered = merged_df[
    merged_df["Code INSEE région"].isin(codes_cibles)
].copy()

# 8. Extraction du mois et agrégation mensuelle par région
df_filtered["Mois"] = pd.to_datetime(df_filtered["Date"]).dt.to_period("M")
conso_mensuelle = (
    df_filtered.groupby(["Mois", "Région"])["Conso par habitant"]
    .mean()
    .unstack()
)
conso_mensuelle.index = conso_mensuelle.index.astype(str)

# 9. Production du graphique comparatif mensuel
conso_mensuelle.plot(kind="line", marker="o", figsize=(10, 6))
plt.title(
    "Évolution mensuelle de la consommation électrique par habitant par région"
)
plt.xlabel("Mois")
plt.ylabel("Consommation moyenne (MWh / habitant)")
plt.legend(title="Régions")
plt.grid(True)
plt.tight_layout()

plt.savefig("data/processed/comparaison_conso_habitant.png")