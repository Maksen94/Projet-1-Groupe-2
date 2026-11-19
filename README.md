# Projet 1 : Exploration et Restitution de Données – Mix Électrique Régional (RTE / éCO2mix)

[![CI - Lint & Quality Check](https://github.com/Maksen94/Projet-1-Groupe-2/actions/workflows/ci.yml/badge.svg)](https://github.com/Maksen94/Projet-1-Groupe-2/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Licence: Etalab 2.0](https://img.shields.io/badge/licence-Etalab%202.0-green.svg)](https://www.etalab.gouv.fr/licence-ouverte-open-licence/)

---

## Contexte
* **Projet académique :** DIA2 - UE01 : Exploration et Restitution de Données (Annexe A, sujet n° 7).
* **Commanditaire :** Agence Régionale de l'Énergie et du Climat (AREC).
* **Besoin métier exprimé :** Fournir aux décideurs et élus régionaux une vision objective, claire et reproductible de la trajectoire énergétique régionale :
  * Quelle part de la consommation régionale est couverte par la production locale renouvelable ?
  * À quels moments et dans quelle mesure le territoire dépend-il des échanges avec les régions voisines ?
  * Comment le mix électrique réagit-il aux variations saisonnières et aux vagues de froid hivernales ?

---

## Questions analytiques
Conformément à l'exigence formelle **EF-01** (détaillée dans [`docs/questions.md`](docs/questions.md)), quatre questions orientées métier structurent l'analyse :
1. **Couverture renouvelable locale (EF-01) :** Quelle est la part réelle des énergies renouvelables (éolien, solaire, hydraulique, bioénergies) dans la couverture de la consommation électrique régionale depuis janvier 2021, et comment ce taux de couverture évolue-t-il mensuellement et annuellement ?
2. **Dépendance inter-régionale et pointes hivernales (EF-01) :** Comment le solde des échanges physiques (importations / exportations) évolue-t-il lors des pics de consommation hivernaux, et dans quelle mesure l'Île-de-France dépend-elle structurellement des régions voisines comparée à Auvergne-Rhône-Alpes et à l'Occitanie ?
3. **Intermittence et thermosensibilité météorologique (EF-01 & EF-08) :** Quelle est l'influence des variations saisonnières sur la production solaire et éolienne, et en quoi la thermosensibilité hivernale constitue-t-elle un facteur de confusion majeur ?
4. **Mix de production et intensité par habitant (EF-06 & EF-07) :** Quelle est la structure globale du mix de production électrique et comment se comparent équitablement les régions une fois les volumes rapportés à leur population municipale légale ?

---

## Données
* **Jeu de données principal :** éCO2mix régional consolidé et définitif (RTE / Open Data Réseaux Énergies - ODRE).
* **Producteur :** Réseau de Transport d'Électricité (RTE).
* **Licence :** Licence Ouverte Etalab 2.0.
* **Date de téléchargement :** 14 novembre 2026.
* **Périmètre temporel retenu (Annexe A.7 / DEC-01) :** Du **1er janvier 2021 au 31 août 2026** au pas de temps demi-heure (1 191 600 créneaux temporels observés).
* **Périmètre géographique retenu (DEC-02) :**
  * **Région principale d'analyse :** **Île-de-France** (Code INSEE 11) — territoire dense à forte demande et déficit structurel de production locale.
  * **Régions repères de comparaison :**
    * **Auvergne-Rhône-Alpes** (Code INSEE 84) — premier producteur national (nucléaire et hydroélectricité massive, exportateur net).
    * **Occitanie** (Code INSEE 76) — territoire pionnier des énergies renouvelables (solaire photovoltaïque et éolien).
* **Données démographiques complémentaires (EF-06) :** Référentiel des populations municipales légales régionales de l'INSEE (recensement 2021 en vigueur).

---

## Installation

### Prérequis
* **Python 3.11** ou version ultérieure requis.
* Git installé sur le poste de travail.

### 1. Cloner le dépôt
```bash
git clone https://github.com/Maksen94/Projet-1-Groupe-2.git
cd Projet-1-Groupe-2
```

### 2. Créer et activer l'environnement virtuel
* **Sous Windows (PowerShell) :**
  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  ```
* **Sous macOS / Linux :**
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  ```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

---

## Reproduire l'analyse
Pour reproduire l'intégralité du pipeline de données et restituer les visualisations de zéro, exécuter les commandes suivantes dans l'ordre :

```bash
# 1. Télécharger les données brutes éCO2mix (~278 Mo) depuis l'API RTE/ODRE
python src/download.py

# 2. Nettoyer, typage, dédupliquer et exporter en Parquet haute performance (34 Mo)
python src/cleaning.py

# 3. Calculer les métriques démographiques par habitant (INSEE) et produire le graphique
python src/population.py

# 4. Lancer le notebook d'analyse exploratoire et de validation des hypothèses
jupyter notebook notebooks/01_exploration.ipynb

# 5. Lancer l'application web interactive Streamlit
streamlit run app/dashboard.py
```

---

## Résultats principaux
1. **Autonomie verte très contrastée :** Le taux de couverture moyen de la consommation par les EnR locales atteint seulement **2,9 % en Île-de-France**, contre **52,1 % en Auvergne-Rhône-Alpes** et **53,7 % en Occitanie** sur la période 2021-2026.
2. **Dépendance structurelle quasi-totale de l'Île-de-France :** L'Île-de-France se trouve en situation d'importation nette d'électricité **100 % du temps** (solde physique moyen de **+7 111 MW**, culminant à **13 767 MW** lors des pointes hivernales de 19h), avec un cumul net importé de **+353,1 TWh**. À l'opposé, Auvergne-Rhône-Alpes opère en exportateur net massif 99,8 % du temps (solde moyen négatif de **-5 593 MW**).
3. **Effet de ciseau saisonnier en hiver :** La production solaire moyenne s'effondre en hiver de **-79 % en Île-de-France** (13,3 MW vs 63,1 MW en été) et de **-64 % en Occitanie** (286,4 MW vs 800,4 MW en été), au moment exact où la consommation grimpe de plus de 60 % du fait du chauffage électrique.
4. **Intensité de consommation par habitant (normalisation INSEE) :** La consommation électrique annuelle par habitant s'établit à **5,29 MWh/habitant en Île-de-France**, **6,07 MWh/habitant en Occitanie** et culmine à **7,68 MWh/habitant en Auvergne-Rhône-Alpes**, reflétant le poids considérable de l'industrie lourde et de la métallurgie rhônalpine.

---

## Limites
* **Démarche purement descriptive et exploratoire :** Conformément au cahier des charges contractuel (CDC-DIA2-UE01-2026), **aucun modèle de Machine Learning ou d'inférence statistique prédictive** n'est déployé dans ce projet.
* **Coexistence des statuts de consolidation :** Les données 2021-2024 relèvent de `Données définitives`, tandis que les données récentes de 2025-2026 relèvent de `Données consolidées` (ajustements marginaux ultérieurs possibles par RTE).
* **Filières structurellement absentes :** L'absence d'installations nucléaires en Île-de-France ou d'éolien offshore en région intérieure génère des `NaN` légitimes sur les taux de charge (TCH), documentés dans [`docs/anomalies.md`](docs/anomalies.md).
* **Facteur de confusion thermique (thermosensibilité) :** La corrélation négative observée entre production solaire et consommation globale ne traduit aucun lien de causalité directe, mais résulte de l'action conjointe de la température extérieure (thermosensibilité française estimée à ~2 400 MW par degré Celsius perdu en hiver).

---

## Structure du projet
```text
Projet-1-Groupe-2/
├── .github/workflows/
│   └── ci.yml                 # Intégration continue (Ruff Linter & formatage)
├── .gitignore                 # Exclusion stricte des données brutes, caches et secrets
├── README.md                  # Documentation principale du projet (Annexe B)
├── requirements.txt           # Dépendances Python figées
├── data/
│   ├── raw/                   # Données brutes éCO2mix CSV (.gitkeep)
│   └── processed/             # Données nettoyées Parquet & CSV (.gitkeep)
├── docs/
│   ├── questions.md           # Formalisation des 4 questions analytiques métier
│   ├── anomalies.md           # Registre traçable des 7 anomalies constatées (ANO-01 à ANO-07)
│   ├── decisions.md           # Journal des choix structurants (DEC-01 à DEC-03)
│   ├── post-mortem.md         # Bilan rétrospectif post-soutenance
│   └── synthese_projet.md     # Synthèse globale de passation technique
├── notebooks/
│   └── 01_exploration.ipynb   # Exploration visuelle, validation d'hypothèses et synthèse L2
├── src/
│   ├── download.py            # Téléchargement automatisé du jeu brut (RTE/ODRE)
│   ├── cleaning.py            # Pipeline de nettoyage, typage et export Parquet (ET-05)
│   ├── indicators.py          # Fonctions factorisées de calcul énergétique (QC-03)
│   └── population.py          # Jointure démographique INSEE et conso par habitant (EF-06/07)
└── app/
    └── dashboard.py           # Tableau de bord interactif Streamlit (TB-01 à TB-06)
```

---

## Équipe

Projet réalisé dans le cadre de la formation DIA2 par le **Groupe 2** :

| Membre | Profil GitHub | Rôle dans le projet |
| :--- | :--- | :--- |
| **Justin Bandiola** | [@Justinbnda](https://github.com/Justinbnda) | **Chef de projet** — Pipeline Parquet, notebook d'exploration & coordination |
| **Aymen Khlifi** | [@AkhyRider](https://github.com/AkhyRider) | **Data Engineering & Versioning** — Pipeline de nettoyage, normalisation des en-têtes & jalon `v0.2` |
| **Douglas Quintero** | [@sgDfQ](https://github.com/sgDfQ) | **Ingestion & UI** — Script de téléchargement (`download.py`) & application Streamlit (`dashboard.py`) |
| **David Daupin** | [@DaupinDavid](https://github.com/DaupinDavid) | **Indicateurs métier** — Factorisation des fonctions énergétiques (`src/indicators.py`) |
| **Maksen Benkerrou** | [@Maksen94](https://github.com/Maksen94) | **Qualité & Démographie** — Workflow CI (Ruff), questions métier & jointure INSEE (`src/population.py`) |
