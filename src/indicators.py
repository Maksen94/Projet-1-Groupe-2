"""Module de calcul des indicateurs energetiques (Exigence QC-03)."""

import pandas as pd

COLONNES_ENR = [
    "Eolien (MW)",
    "Solaire (MW)",
    "Hydraulique (MW)",
    "Bioénergies (MW)",
]

COLONNES_PRODUCTION = [
    "Nucléaire (MW)",
    "Thermique (MW)",
    *COLONNES_ENR,
]


def compute_total_consumption(df: pd.DataFrame) -> float:
    """Calcule la consommation totale d'energie en MWh (E = P * 0.5h)."""
    consommation_mwh = (df["Consommation (MW)"] * 0.5).sum()
    return float(consommation_mwh)


def compute_enr_share(df: pd.DataFrame, sur_consommation: bool = False) -> float:
    """Calcule la part d'energie renouvelable (%) sur la production ou la conso."""
    energie_enr_mwh = float((df[COLONNES_ENR].sum(axis=1) * 0.5).sum())

    if sur_consommation:
        total_reference_mwh = compute_total_consumption(df)
    else:
        total_reference_mwh = float((df[COLONNES_PRODUCTION].sum(axis=1) * 0.5).sum())

    if total_reference_mwh == 0:
        return 0.0
    return round((energie_enr_mwh / total_reference_mwh) * 100, 2)


def compute_trade_balance(df: pd.DataFrame) -> dict[str, float]:
    """Calcule le solde des echanges physiques en MW et en MWh."""
    echanges_mw = df["Ech. physiques (MW)"]
    solde_mw = float(echanges_mw.sum())
    solde_moyen_mw = float(echanges_mw.mean())
    solde_mwh = float((echanges_mw * 0.5).sum())

    return {
        "solde_mw": round(solde_mw, 2),
        "solde_moyen_mw": round(solde_moyen_mw, 2),
        "solde_mwh": round(solde_mwh, 2),
    }


def compute_peak_power(df: pd.DataFrame) -> dict[str, float | str]:
    """Extrait la puissance de pointe maximale (MW) et sa date/heure."""
    index_max = df["Consommation (MW)"].idxmax()
    ligne_max = df.loc[index_max]

    return {
        "puissance_max_mw": float(ligne_max["Consommation (MW)"]),
        "date_heure": str(ligne_max["Date - Heure"]),
        "region": str(ligne_max["Région"]),
    }