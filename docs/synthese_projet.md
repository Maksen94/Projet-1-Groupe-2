# Synthèse Détaillée du Projet - DIA2 UE01 (Mix Électrique Régional)

> **Document de contexte et de passation technique**  
> *Ce document synthétise l'intégralité du travail réalisé, l'architecture du projet, l'état des données et la feuille de route. Il est prêt à être partagé avec une autre IA ou un membre de l'équipe pour reprendre le travail immédiatement sans perte de contexte.*

---

## 1. Fiche d'identité du projet

* **Projet :** DIA2 - UE01 : Exploration et Restitution de Données.
* **Sujet retenu :** **Sujet 7 – Mix électrique régional** (éCO2mix régional consolidé et définitif, source RTE / ODRE).
* **Commanditaire fictif :** Agence Régionale de l'Énergie et du Climat (AREC).
* **Objectif global :** Analyser la couverture de la consommation régionale par les énergies renouvelables (EnR), la dépendance inter-régionale (échanges physiques et pics hivernaux), l'impact carbone, et restituer l'analyse via un notebook et un tableau de bord Streamlit.
* **Contrainte clé du périmètre :** Analyse descriptive et exploratoire stricte — **aucun modèle prédictif / Machine Learning autorisé** (motif de refus au cahier des charges).
* **Stack technique :** Python 3.12+, Pandas, NumPy, Matplotlib, Seaborn, Streamlit, Ruff (linter PEP 8), Git / GitHub.
* **Branche courante de travail :** `Justin` (synchronisée avec `origin/Justin`).

---

## 2. Questions métier et analytiques validées (`docs/questions.md`)

1. **Part des énergies renouvelables :** Quelle est la part réelle des EnR (éolien, solaire, hydraulique, bioénergies) dans la couverture de la consommation électrique régionale ?
2. **Dépendance et échanges inter-régionaux :** Comment le solde des échanges physiques (importations / exportations) évolue-t-il lors des pics de consommation hivernaux ?
3. **Intermittence et météo :** Quelle est l'influence des variations saisonnières sur la production solaire et éolienne ?
4. **Mix de production et intensité carbone :** Quelle est la structure globale du mix régional (nucléaire, thermique fossile, EnR) et son profil environnemental ?

---

## 3. Données et Arborescence du Projet

### Fichiers de données :
* **Données brutes :** `data/raw/eco2mix-regional-cons-def.csv` (464 Mo, ~2,87 millions de lignes, pas demi-heure, 12 régions administratives métropolitaines). Téléchargé via `src/download.py`.
* **Données nettoyées :** `data/processed/eco2mix-regional-cons-def_clean.csv` (493 Mo, 2 874 481 lignes, 31 colonnes). Généré via `src/cleaning.py`.
* **Règle Git (exigence GIT-04) :** Tous les fichiers de données brutes et intermédiaires (`.csv`, `.parquet`) sont strictement ignorés par le `.gitignore` afin de ne jamais encombrer le dépôt GitHub. Seuls les fichiers `.gitkeep` sont versionnés pour maintenir l'arborescence.

### Structure des dossiers :
```text
Projet-1-Groupe-2/
├── .github/workflows/ci.yml       # Intégration continue (Ruff linting)
├── .gitignore                     # Règles strictes d'exclusion (data, cache, secrets)
├── README.md                      # Documentation d'accueil et instructions d'installation
├── requirements.txt               # Dépendances figées (encodé en UTF-8)
├── data/
│   ├── raw/                       # Fichier brut eco2mix-regional-cons-def.csv (.gitkeep)
│   └── processed/                 # Fichier nettoyé eco2mix-regional-cons-def_clean.csv (.gitkeep)
├── docs/
│   ├── questions.md               # 4 questions analytiques métier validées
│   ├── anomalies.md               # Journal contractuel des anomalies (ANO-01 à ANO-04)
│   ├── decisions.md               # Journal des décisions structurantes
│   ├── post-mortem.md             # Bilan rétrospectif post-soutenance
│   └── synthese_projet.md         # Le présent document de synthèse
├── notebooks/
│   └── 01_exploration.ipynb       # Notebook d'exploration (exigences EF-01 à EF-05 validées)
├── src/
│   ├── download.py                # Téléchargement automatisé du jeu de données brut
│   ├── cleaning.py                # Pipeline complet de nettoyage et typage
│   └── indicators.py              # Fonctions factorisées de calcul des indicateurs
└── app/
    └── dashboard.py               # Tableau de bord Streamlit (à développer)
```

---

## 4. Historique et Détail du Pipeline de Nettoyage (`src/cleaning.py`)

### A. Contribution initiale (Aymen) :
Mise en place de l'ossature d'un pipeline en 9 étapes :
1. Suppression de la colonne fantôme `Column 30`.
2. Détection et nettoyage des faux nuls textuels (`"nr"`, `"non renseigné"`, etc.).
3. Cast des colonnes numériques en float (gestion des séparateurs décimaux `,` et `.`).
4. Conversion des dates et gestion du fuseau horaire `Europe/Paris`.
5. Gestion des valeurs sentinelles `-1` (absence de capteur).
6. Déduplication exacte et fonctionnelle (priorité `Données définitives` > `Données consolidées`).
7. Rapport qualité en console.

### B. Correctifs critiques et fiabilisation (Justin) :
* **Résolution d'un bug critique d'écrasement de données :** Dans la version initiale, les colonnes `"Date - Heure"` et `"Région"` n'étaient pas dans la liste d'exclusion du cast numérique. Elles étaient donc converties en `NaN`, ce qui provoquait la suppression par déduplication de 99,8 % du jeu de données. Le correctif a protégé tous les intitulés réels du CSV brut, restaurant l'intégralité des 2,87 millions de lignes.
* **Normalisation des chemins :** Prise en compte dynamique de `data/raw/` pour l'entrée et de `data/processed/` pour la sortie.
* **Correction des encodages :** Passage de `requirements.txt` d'un encodage corrompu UTF-16 Windows en UTF-8 standard.
* **Exécution réussie :** Le fichier propre `data/processed/eco2mix-regional-cons-def_clean.csv` est désormais matérialisé sur disque.

---

## 5. Journal des Anomalies Traitées (`docs/anomalies.md`)

Conformément à l'exigence contractuelle de la section 8 du cahier des charges, 4 anomalies majeures ont été identifiées, traitées et documentées :

* **ANO-01 (`Column 30`) :** Colonne parasite 100 % vide en fin de ligne (problème d'export ODRE). Traitement : Suppression (`drop_ghost_columns`).
* **ANO-02 (Faux nuls) :** Chaînes vides et mentions textuelles (`"nr"`, `"non renseigné"`) présentes dans l'historique ancien. Traitement : Remplacement par `np.nan` (`clean_fake_nulls`).
* **ANO-03 (Valeurs `-1`) :** Convention RTE historique codant l'absence de mesure par `-1` sur les filières de production (qui ne peuvent physiquement être négatives). Traitement : Remplacement ciblé par `np.nan` sans altérer les négatifs réels du `Pompage (MW)` et des `Échanges physiques (MW)` (`flag_minus_one`).
* **ANO-04 (Doublons fonctionnels) :** 335 créneaux temporels redondants entre révisions annuelles. Traitement : Déduplication en conservant le statut le plus récent `Données définitives` (`remove_functional_duplicates`).

---

## 6. Analyse Exploratoire Validée (`notebooks/01_exploration.ipynb`)

Le notebook est fonctionnel de bout en bout (8 cellules de code exécutées avec succès) et couvre les exigences formelles :
* **EF-02 (Profilage) :** 2 874 481 lignes, 31 colonnes, période du 01/01/2013 au 31/08/2026, 12 régions administratives couvertes.
* **EF-03 (Distributions et choix Moyenne vs Médiane) :** 
  * *Moyenne justifiée* pour les bilans énergétiques (passage MW vers MWh).
  * *Médiane justifiée* pour refléter la demande usuelle et filtrer l'asymétrie des vagues de froid ou tempêtes.
* **EF-04 (Agrégations croisées) :** Série temporelle mensuelle comparant Consommation moyenne, Production EnR et Production Nucléaire. Boxplot horizontal de consommation par région.
* **EF-05 (Vérification formelle des 2 hypothèses) :**
  * *Hypothèse 1 (Saisonnalité EnR en hiver) :* **Confirmée.** Le taux de couverture moyen chute en hiver en raison de l'effondrement de la production solaire et de la hausse des besoins de chauffage.
  * *Hypothèse 2 (Dépendance structurelle de l'Île-de-France) :* **Confirmée.** L'Île-de-France présente un solde d'échanges physiques continuellement positif (importateur net massif tout au long de l'année).

---

## 7. Prochaines Étapes du Projet (Feuille de Route)

1. **Exigence EF-06 & EF-07 (Prochaine priorité) :**
   * Récupérer le fichier officiel de la **population des régions INSEE**.
   * Réaliser la **jointure** entre les données éCO2mix et la population régionale.
   * Calculer la **consommation par habitant** (kWh / hab) pour rendre comparables les différentes régions (ex: Île-de-France vs Centre-Val de Loire).
2. **Exigence QC-03 (Factorisation) :**
   * Déplacer les calculs d'agrégation et d'indicateurs (taux de couverture, soldes, parts EnR) du notebook vers [`src/indicators.py`](file:///Users/jujutravail/Projet-1-Groupe-2/src/indicators.py).
3. **Exigences TB-01 à TB-06 (Tableau de bord Streamlit) :**
   * Développer [`app/dashboard.py`](file:///Users/jujutravail/Projet-1-Groupe-2/app/dashboard.py).
   * Intégrer les filtres interactifs (période, région).
   * Afficher en tête les 3 à 5 indicateurs clés (KPIs) pour l'AREC.
   * Optimiser le chargement (utilisation d'un format Parquet ou de données pré-agrégées pour respecter le temps de lancement < 10 secondes sur 8 Go de RAM).

---

## 8. Consignes pour toute IA reprenant ce projet

* **Mode opératoire :** Toujours proposer des modifications pas-à-pas, modulaires et documentées.
* **Qualité de code :** Respecter rigoureusement la PEP 8 (`ruff check .` doit retourner 0 erreur).
* **Respect du périmètre :** Ne proposer aucun algorithme de prédiction, de régression ou de machine learning.
* **Gestion mémoire :** Toujours garder en tête la contrainte d'exécution locale sur un poste à **8 Go de RAM** (ne pas charger aveuglément des copies intégrales de 2,8M lignes sans filtrage ou agrégation).

