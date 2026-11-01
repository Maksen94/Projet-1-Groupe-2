# Questions Analytiques du Projet - Mix Électrique Régional (RTE / éCO2mix)

> **Cadre contractuel :** Projet 1 DIA2 (UE01) - Sujet 7 (Annexe A.7 du CDC-DIA2-UE01-2026)  
> **Commanditaire :** Agence Régionale de l'Énergie et du Climat (AREC)  
> **Périmètre temporel :** Du 1er janvier 2021 au 31 août 2026 (pas demi-heure)  
> **Périmètre géographique retenu (Annexe A.7) :**
> * **Région d'étude principale :** **Île-de-France** (territoire à très forte densité de population, forte demande et déficit structurel de production locale).
> * **Régions de comparaison :**
>   * **Auvergne-Rhône-Alpes** (premier producteur national d'électricité : parc nucléaire et hydroélectricité massive).
>   * **Occitanie** (territoire pionnier de la transition énergétique : forte dynamique solaire photovoltaïque et éolienne).

---

## Besoin métier exprimé par le commanditaire

> *"Nous devons montrer au conseil régional où en est la région : quelle part de notre consommation est couverte par notre propre production renouvelable, à quels moments nous dépendons des autres régions, et comment cela évolue."*

---

## Questions analytiques formalisées (Exigence EF-01)

### Question 1 : Couverture de la consommation par les énergies renouvelables locales
* **Énoncé analytique :** Quelle est la part réelle des énergies renouvelables locales (éolien, solaire, hydraulique et bioénergies) dans la couverture de la consommation électrique régionale depuis janvier 2021, et comment ce taux de couverture évolue-t-il mensuellement et annuellement ?
* **Objectif métier :** Mesurer le degré d'autonomie verte de l'Île-de-France face aux deux régions repères et évaluer la trajectoire de décarbonation.
* **Indicateurs clés :**
  * Production EnR totale en MWh ($E = \sum P \times 0.5$).
  * Taux de couverture EnR global ($TCO_{\text{EnR}} = \frac{\text{Production EnR}}{\text{Consommation}} \times 100$).
  * Taux de couverture par filière (TCO Eolien, TCO Solaire, TCO Hydraulique, TCO Bioénergies).
* **Colonnes exactes mobilisées :**
  * `Date - Heure` (dimension temporelle fine)
  * `Date` (agrégation quotidienne, mensuelle, annuelle)
  * `Région` (filtrage géographique)
  * `Consommation (MW)` (demande électrique)
  * `Eolien (MW)`, `Solaire (MW)`, `Hydraulique (MW)`, `Bioénergies (MW)` (puissances renouvelables injectées)
  * `Pompage (MW)` (consommation liée au stockage hydraulique / STEP)
  * `TCO Eolien (%)`, `TCO Solaire (%)`, `TCO Hydraulique (%)`, `TCO Bioénergies (%)` (ratios officiels RTE)

---

### Question 2 : Dépendance inter-régionale et pointes de consommation hivernales
* **Énoncé analytique :** Comment le solde des échanges physiques inter-régionaux (importations / exportations) évolue-t-il lors des pics de consommation hivernaux, et à quelles heures de la journée et mois de l'année l'Île-de-France présente-t-elle sa plus forte dépendance vis-à-vis des autres régions comparée à l'Auvergne-Rhône-Alpes et l'Occitanie ?
* **Objectif métier :** Identifier la résilience du réseau régional lors des vagues de froid, cartographier les heures critiques d'importation (pointe 19h) et quantifier les volumes physiques d'énergie importée.
* **Indicateurs clés :**
  * Solde moyen et cumulé des échanges physiques en MW et MWh ($>0$ : importateur net ; $<0$ : exportateur net).
  * Profil horaire moyen journalier par saison (courbe de charge et dépendance).
  * Fréquence des heures en situation d'importation nette ($> 0\text{ MW}$).
* **Colonnes exactes mobilisées :**
  * `Date - Heure` (détection des pics horaires)
  * `Date` (filtrage des mois d'hiver : décembre, janvier, février)
  * `Heure` (profil journalier de 00:00 à 23:30)
  * `Région` (comparaison Île-de-France vs Auvergne-Rhône-Alpes vs Occitanie)
  * `Consommation (MW)` (charge électrique appelée)
  * `Ech. physiques (MW)` (flux nets mesurés aux frontières régionales)

---

### Question 3 : Saisonnalité, intermittence des EnR et facteur de confusion météorologique (EF-08)
* **Énoncé analytique :** Quelle est l'influence des variations saisonnières et infra-journalières sur la régularité et le facteur de charge des filières solaire et éolienne entre les territoires ?
* **Objectif métier :** Évaluer l'intermittence des EnR non pilotables et anticiper les besoins en stockage ou en capacités d'appoint pilotables.
* **Indicateurs clés :**
  * Taux de charge moyen ($TCH = \frac{\text{Production mesurée}}{\text{Puissance installée raccordée}}$).
  * Facteur de variabilité (écart interquartile, coefficient de variation journalier).
* **Colonnes exactes mobilisées :**
  * `Date`, `Heure` (cycle journalier et saisonnier)
  * `Région` (comparaison du gisement solaire en Occitanie vs Île-de-France)
  * `Eolien (MW)`, `Solaire (MW)` (puissance instantanée produite)
  * `TCH Eolien (%)`, `TCH Solaire (%)` (taux d'utilisation des capacités installées)
* **Discussion du facteur de confusion (Exigence EF-08) :**
  * *Facteur de confusion identifié :* **La température extérieure et les conditions météorologiques synchrones (thermosensibilité).**
  * *Explication causale :* Une baisse des températures hivernales induit mécaniquement une forte augmentation de la consommation (effet chauffage électrique français ~2 400 MW par degré perdu). Concomitamment, la saison hivernale présente un rayonnement solaire minimal (jours courts, nébulosité). Une corrélation négative observée entre consommation et production solaire ne traduit pas un lien de cause à effet direct entre demande et soleil, mais l'impact conjoint du cycle thermique hivernal.

---

### Question 4 : Structure du mix, profil carbone et comparaison par habitant (EF-06 & EF-07)
* **Énoncé analytique :** Quelle est la structure globale du mix de production électrique des 3 régions étudiées, son impact sur l'intensité carbone locale, et comment se comparent équitablement les régions une fois les volumes de consommation et de production rapportés à la population municipale ?
* **Objectif métier :** Fournir une vision objective et normalisée aux décideurs régionaux, en évitant les biais de comparaison liés à la taille démographique des territoires.
* **Indicateurs clés :**
  * Répartition en pourcentage du mix de production par filière (nucléaire, hydraulique, thermique, solaire, éolien, bioénergies).
  * Consommation annuelle par habitant (MWh / habitant).
  * Production renouvelable par habitant (MWh / habitant).
  * Émissions directes ou taux estimé d'émissions associées au thermique.
* **Colonnes exactes mobilisées :**
  * Données éCO2mix RTE :
    * `Région`, `Date`
    * `Consommation (MW)`
    * `Nucléaire (MW)`, `Thermique (MW)`, `Eolien (MW)`, `Solaire (MW)`, `Hydraulique (MW)`, `Bioénergies (MW)`
    * `Taux de Co2 (g/kWh)` (si disponible selon la période)
  * Données externes INSEE (jointure EF-06) :
    * `Code INSEE région` (clé de jointure normalisée)
    * `Population municipale` (référentiel de recensement de population légale INSEE)
