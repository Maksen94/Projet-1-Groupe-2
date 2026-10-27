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