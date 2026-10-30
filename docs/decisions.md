# Journal des Décisions Structurantes (Projet 1 - Mix Électrique Régional)

> Conformément à la section 11 du cahier des charges contractuel (CDC-DIA2-UE01-2026), chaque décision structurante (choix d'une méthode, filtrage ou exclusion de données, orientation d'architecture, cadrage du périmètre) est consignée dans ce document avec sa date, son auteur, son contexte et sa justification rationnelle.

---

## Registre des décisions

| Identifiant | Date | Sujet | Impact | Statut |
| :--- | :--- | :--- | :--- | :--- |
| **DEC-01** | 30/10/2026 | Filtrage du périmètre temporel à partir du 01/01/2021 | Réduction volumique et alignement contractuel | **Validé** |
| **DEC-02** | 30/10/2026 | Sélection du triplet de régions d'étude (IDF, AURA, Occitanie) | Cadrage de l'analyse comparative multi-territoires | **Validé** |
| **DEC-03** | 30/10/2026 | Adoption du format Apache Parquet pour les données traitées | Performance, RAM 8 Go et chargement Streamlit < 10 s | **Validé** |

---

## Fiches détaillées des décisions

### DEC-01 : Filtrage temporel à partir du 1er janvier 2021
* **Date d'effet :** 30 octobre 2026
* **Auteur / Équipe :** Équipe Projet 1 - Groupe 2 (Justin, Aymen, Maksen)
* **Contexte :** Le jeu de données brut `eco2mix-regional-cons-def.csv` couvre la période 2013-2026 avec plus de 2,87 millions de lignes (464 Mo). L'Annexe A.7 du cahier des charges spécifie expressément : *"éCO2mix régional consolidé et définitif, RTE, pas demi-heure depuis janvier 2021"*.
* **Décision retenue :** Appliquer un filtre temporel strict `Date >= "2021-01-01"` au sein du pipeline [`src/cleaning.py`](file:///Users/jujutravail/Projet-1-Groupe-2/src/cleaning.py).
* **Justification :**
  1. **Conformité au cahier des charges :** Respect rigoureux du cadre contractuel défini en Annexe A.7.
  2. **Homogénéité méthodologique :** Les filières EnR récentes (notamment l'essor massif du photovoltaïque et le début de l'éolien en mer) et les mécanismes de consolidation RTE ont évolué ; la période 2021-2026 offre une cohérence de mesure maximale.
  3. **Performance mémoire (ET-05) :** Réduction du volume de moitié (1,19 million de lignes au lieu de 2,87 millions), garantissant une exécution fluide et sans saturation sur un poste portable standard de 8 Go de RAM.

---

### DEC-02 : Choix du périmètre géographique comparatif (Île-de-France, AURA, Occitanie)
* **Date d'effet :** 30 octobre 2026
* **Auteur / Équipe :** Équipe Projet 1 - Groupe 2
* **Contexte :** L'Annexe A.7 recommande d'étudier : *"une région détaillée et deux régions de comparaison, toute la période"*.
* **Décision retenue :** 
  * **Région principale d'analyse :** **Île-de-France** (Code INSEE 11).
  * **Deux régions de comparaison :** **Auvergne-Rhône-Alpes** (Code INSEE 84) et **Occitanie** (Code INSEE 76).
* **Justification :**
  1. **Pertinence de la confrontation des profils énergétiques :**
     * L'**Île-de-France** concentre près de 19 % de la population nationale, avec une très forte intensité tertiaire et résidentielle, mais sans capacités de production thermique ou nucléaire d'envergure, la rendant structurellement dépendante des échanges physiques (importateur net).
     * **Auvergne-Rhône-Alpes** constitue le château d'eau et le pôle nucléaire de la France (barrages hydroélectriques majeurs et grands centres de production nucléaire), incarnant le modèle de région massivement exportatrice.
     * L'**Occitanie** illustre la pointe de la transition bas-carbone décentralisée, avec un fort gisement photovoltaïque et hydroélectrique pyrénéen, permettant d'analyser la variabilité et l'autonomie renouvelable.
  2. **Richesse de l'histoire racontée au commanditaire (AREC) :** Offre un contraste saisissant entre dépendance urbaine, puissance pilotable et transition renouvelable.

---

### DEC-03 : Adoption du format Apache Parquet pour les données préparées
* **Date d'effet :** 30 octobre 2026
* **Auteur / Équipe :** Équipe Projet 1 - Groupe 2
* **Contexte :** L'exigence technique ET-05 impose une exécution complète possible sur un poste de 8 Go de RAM et préconise : *"format Parquet si le volume l'impose"*. L'exigence TB-06 impose que le tableau de bord s'affiche en moins de 10 secondes.
* **Décision retenue :** Sauvegarder les données nettoyées sous double format dans `data/processed/` :
  1. `eco2mix-regional-cons-def_clean.parquet` (format primaire utilisé par le notebook et l'application Streamlit).
  2. `eco2mix-regional-cons-def_clean.csv` (format secondaire pour rétrocompatibilité et inspections rapides).
* **Justification :**
  1. **Gain de taille spectaculaire :** Le fichier Parquet ne pèse que **34 Mo** contre **244 Mo** pour le CSV nettoyé et **464 Mo** pour le fichier brut, soit une compression par un facteur supérieur à 7 sans perte d'information.
  2. **Vitesse de lecture I/O :** Chargement instantané en mémoire (< 0,4 seconde avec `pyarrow`), préservant les types (`datetime64`, `float64`, `category`) sans besoin de re-parser les chaînes de dates.
  3. **Conformité stricte à l'exigence TB-06 :** Garantit que l'application Streamlit se lance et charge les données en moins de 2 secondes.

