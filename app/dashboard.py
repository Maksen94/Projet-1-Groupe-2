"""Tableau de bord Streamlit du mix électrique régional (issue #16).

Lancement depuis la racine du projet :
    streamlit run app/dashboard.py
"""

from pathlib import Path

import pandas as pd
import streamlit as st

# Fichier de données produit par src/cleaning.py
RACINE = Path(__file__).resolve().parent.parent
CHEMIN_PARQUET = (
    RACINE / "data" / "processed" / "eco2mix-regional-cons-def_clean.parquet"
)

# Filières renouvelables retenues (identiques au notebook d'exploration)
COLONNES_ENR = [
    "Eolien (MW)",
    "Solaire (MW)",
    "Hydraulique (MW)",
    "Bioénergies (MW)",
]
COLONNES_UTILES = [
    "Région",
    "Date",
    "Consommation (MW)",
    "Ech. physiques (MW)",
] + COLONNES_ENR
REGION_PAR_DEFAUT = "Île-de-France"


@st.cache_data
def charger_donnees() -> pd.DataFrame:
    """Charge uniquement les colonnes utiles du fichier Parquet nettoyé."""
    return pd.read_parquet(CHEMIN_PARQUET, columns=COLONNES_UTILES)


def formater(nombre: float, decimales: int = 2) -> str:
    """Affiche un nombre avec une virgule comme séparateur décimal."""
    return f"{nombre:.{decimales}f}".replace(".", ",")


st.set_page_config(page_title="Mix électrique régional", layout="wide")
st.title("Mix électrique régional")

if not CHEMIN_PARQUET.exists():
    st.error("Données introuvables. Lancez d'abord : python src/cleaning.py")
    st.stop()

df = charger_donnees()

# --- Barre latérale : filtres ---
st.sidebar.header("Filtres")

regions = sorted(df["Région"].unique())
region = st.sidebar.selectbox(
    "Région", regions, index=regions.index(REGION_PAR_DEFAUT)
)

date_min = df["Date"].min().date()
date_max = df["Date"].max().date()
periode = st.sidebar.date_input(
    "Période",
    value=(date_min, date_max),
    min_value=date_min,
    max_value=date_max,
)

# Tant que seule la date de début est choisie, on attend la date de fin
if len(periode) != 2:
    st.info("Choisissez une date de fin.")
    st.stop()

debut, fin = periode

# --- Filtrage des données ---
masque = (
    (df["Région"] == region)
    & (df["Date"] >= pd.Timestamp(debut))
    & (df["Date"] <= pd.Timestamp(fin))
)
selection = df[masque]

if selection.empty:
    st.warning("Aucune donnée pour cette sélection.")
    st.stop()

# --- Calcul des indicateurs ---
# Les valeurs sont des puissances (MW) au pas demi-heure :
# énergie (MWh) = puissance (MW) x 0,5 h, puis / 1 000 000 pour obtenir des TWh.
consommation_twh = selection["Consommation (MW)"].sum() * 0.5 / 1_000_000
production_enr_twh = selection[COLONNES_ENR].sum().sum() * 0.5 / 1_000_000
taux_enr = production_enr_twh / consommation_twh * 100
solde_twh = selection["Ech. physiques (MW)"].sum() * 0.5 / 1_000_000

# --- Affichage des indicateurs ---
st.subheader(f"{region} : du {debut:%d/%m/%Y} au {fin:%d/%m/%Y}")

col1, col2, col3 = st.columns(3)
col1.metric("Consommation totale", f"{formater(consommation_twh)} TWh")
col2.metric(
    "Taux de couverture EnR",
    f"{formater(taux_enr, 1)} %",
    help="Production renouvelable (éolien, solaire, hydraulique, bioénergies) "
    "divisée par la consommation de la région.",
)
col3.metric(
    "Solde des échanges",
    f"{formater(solde_twh)} TWh",
    help="Positif : la région importe plus qu'elle n'exporte. "
    "Négatif : elle exporte plus qu'elle n'importe.",
)

if solde_twh > 0:
    st.write("Sur cette période, la région est **importatrice nette** d'électricité.")
else:
    st.write("Sur cette période, la région est **exportatrice nette** d'électricité.")

st.caption(
    "Source : éCO2mix régional consolidé et définitif (RTE / ODRE), "
    "Licence Ouverte Etalab 2.0."
)
