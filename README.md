# Projet 1 : Exploration et restitution de données - Mix Électrique Régional (RTE)

## Contexte
* **Commanditaire :** Agence régionale de l'énergie et du climat
* **Sujet retenu :** Annexe A, n° 7 - Mix électrique régional
* **Besoin exprimé :** Montrer au conseil régional où en est la région : quelle part de notre consommation est couverte par notre propre production renouvelable, à quels moments nous dépendons des autres régions, et comment cela évolue.

## Questions analytiques
1. Quelle est la part réelle des énergies renouvelables (éolien, solaire, hydraulique) dans la couverture de la consommation électrique régionale ?
2. Comment le solde des échanges inter-régionaux (importations / exportations) évolue-t-il lors des pics de consommation hivernaux ?
3. Quelle est l'influence des variations saisonnières et météorologiques sur la production d'origine solaire et éolienne ?
4. Quelle est la structure globale du mix de production et quel est son impact carbone associé ?

## Données
* **Source :** Données éCO2mix régional consolidé et définitif
* **Producteur :** RTE
* **Licence :** Licence Ouverte Etalab 2.0
* **Période couverte :** Pas de temps demi-heure, depuis janvier 2021

## Installation
Commandes pour créer l'environnement virtuel et installer les dépendances du projet :
```bash
python -m venv .venv
# Sur Windows (PowerShell) :
.venv\Scripts\Activate.ps1
# Installation des dépendances :
pip install -r requirements.txt

## Installation
Commandes pour créer l'environnement virtuel et installer les dépendances du projet (Python 3.11 ou version ultérieure requise) :

```bash
python -m venv .venv

# Sous Windows (PowerShell) :
.venv\Scripts\Activate.ps1
# Sous macOS / Linux :
source .venv/bin/activate

# Installation des dépendances :
pip install -r requirements.txt
```

## Récupération des données
Le fichier de données (environ 450 Mo) dépasse la taille autorisée par GitHub : il n'est donc pas versionné, et le dossier `data/` est exclu par le `.gitignore`.

Pour le télécharger, exécuter depuis la racine du projet :

```bash
python src/download.py
```

* **Fichier obtenu :** `data/raw/eco2mix-regional-cons-def.csv`
* **Source :** [éCO2mix régional consolidé et définitif](https://odre.opendatasoft.com/explore/dataset/eco2mix-regional-cons-def/) – ODRE / RTE
* **Format :** CSV, séparateur `;`, encodage UTF-8

Si le fichier est déjà présent, le script ne le télécharge pas une seconde fois. Le téléchargement n'est à effectuer qu'une seule fois par poste : le fichier reste dans `data/raw/`, quelle que soit la branche active.

### Chargement des données

```python
import pandas as pd

df = pd.read_csv("data/raw/eco2mix-regional-cons-def.csv", sep=";")
```

Depuis un notebook du dossier `notebooks/`, utiliser le chemin relatif `../data/raw/eco2mix-regional-cons-def.csv`.

### Travailler depuis une branche existante
Si votre branche a été créée avant l'ajout du script, intégrez d'abord la dernière version de `main`, puis lancez le téléchargement :

```bash
git checkout <nom-de-votre-branche>
git pull origin main
python src/download.py
```

⚠️ Ne téléchargez pas le fichier sur une branche qui ne contient pas encore le nouveau `.gitignore` : un `git add .` l'ajouterait au commit, et le push serait rejeté par GitHub (limite de 100 Mo par fichier).