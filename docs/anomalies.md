# Journal des Anomalies de Données (éCO2mix Régional)

> Conformément à la section 8 du cahier des charges (CDC-DIA2-UE01-2026), toute anomalie constatée dans le jeu de données brut `eco2mix-regional-cons-def.csv` est répertoriée dans ce document. Aucune ligne ou colonne n'est supprimée ou modifiée sans traçabilité écrite.

---

## Synthèse du registre des anomalies

| Identifiant | Colonne(s) concernée(s) | Description sommaire | Ampleur (2021-2026) | Traitement retenu | Impact sur l'analyse |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ANO-01** | `Column 30` | Colonne fantôme 100 % vide en queue de fichier | 1 191 744 lignes (100 %) | **Exclu** (suppression systématique) | Schéma assaini, allègement mémoire |
| **ANO-02** | Colonnes métriques & texte | Valeurs manquantes déguisées (`""`, `"nr"`, `"nan"`) | 120 cellules identifiées | **Corrigé** (`np.nan` standard) | Évite les échecs de conversion de types |
| **ANO-03** | Filières de production EnR & thermique | Valeurs sentinelles `-1` (absence de mesure capteur) | Historique résiduel | **Corrigé** (`np.nan` ciblé sur filières non négatives) | Prévient les productions d'énergie négatives aberrantes |
| **ANO-04** | `Code INSEE région`, `Date - Heure`, `Nature` | Doublons fonctionnels (même région x même créneau) | 144 lignes | **Exclu / Priorisé** (conservation de `Données définitives`) | Évite le surcomptage d'énergie lors des agrégations |
| **ANO-05** | Filières de production (`Nucléaire`, `Eolien offshore`, etc.) | Confusion entre filière structurellement absente et production nulle | Récurrent selon les régions (ex: IDF sans nucléaire) | **Conservé / Documenté** (distinction NaN structurel vs 0 MW d'inactivité) | Évite de calculer des facteurs de charge absurdes |
| **ANO-06** | `Date - Heure`, `Date`, `Heure` | Ruptures de continuité lors des bascules Été / Hiver | 2 bascules par an (mars et octobre) | **Corrigé** (horodatage UTC converti en `Europe/Paris`) | Évite les incohérences de pas temporel infra-journalier |
| **ANO-07** | Ensemble des colonnes de puissance (MW) et `Nature` | Risque de confusion entre puissance instantanée (MW) et énergie (MWh) | 100 % des variables quantitatives physiques | **Normalisé** (facteur $0.5\,\text{h}$ appliqué aux cumuls temporels) | Garantit l'exactitude physique des bilans d'énergie en MWh |

---

## Fiches détaillées des anomalies

### ANO-01 : Colonne fantôme sans intitulé métier
* **Colonne(s) concernée(s) :** `Column 30`
* **Description :** Une colonne additionnelle sans intitulé métier apparaît en queue de chaque enregistrement dans l'export Open Data. Elle ne contient aucune donnée.
* **Exemple observé :** Délimiteur `;` résiduel terminant chaque ligne du CSV brut.
* **Ampleur :** 100 % des lignes brutes (1 191 744 enregistrements sur la période 2021-2026).
* **Cause probable :** Export automatisé de la plateforme Open Data (ODRE/RTE) générant un séparateur supplémentaire sans entête.
* **Traitement retenu :** **Exclu.** Suppression automatique via `drop_ghost_columns()` dans [`src/cleaning.py`](file:///Users/jujutravail/Projet-1-Groupe-2/src/cleaning.py).
* **Impact sur l'analyse :** Aucun impact sur les métriques physiques ; libération mémoire et conformité stricte du schéma de données.

---

### ANO-02 : Valeurs manquantes déguisées en chaînes de caractères
* **Colonne(s) concernée(s) :** Colonnes de consommation, de production et taux RTE.
* **Description :** Présence de chaînes textuelles exprimant le vide (`""`, `"nr"`, `"non renseigné"`, `"nan"`, `"-"`) au lieu d'un type numérique ou `null`.
* **Exemple observé :** Chaîne vide `""` ou mention textuelle `"nr"` dans les données de télérelève.
* **Ampleur :** 120 cellules sur le périmètre 2021-2026.
* **Cause probable :** Télétransmission momentanément interrompue ou formatage hétérogène de la source de données.
* **Traitement retenu :** **Corrigé.** Remplacement systématique par `np.nan` via `clean_fake_nulls()` avant conversion en `float64`.
* **Impact sur l'analyse :** Sécurise le typage Pandas et évite les erreurs de calcul (`TypeError` ou écrasement intempestif de colonnes).

---

### ANO-03 : Valeur sentinelle `-1` d'absence sur filières non négatives
* **Colonne(s) concernée(s) :** `Thermique (MW)`, `Nucléaire (MW)`, `Eolien (MW)`, `Solaire (MW)`, `Hydraulique (MW)`, `Bioénergies (MW)`, `Eolien terrestre`, `Eolien offshore`.
* **Description :** Des valeurs `-1` sont injectées par RTE pour indiquer une indisponibilité ou une absence de mesure, alors qu'une injection sur le réseau est obligatoirement positive ou nulle.
* **Exemple observé :** `-1` sur certaines séries éoliennes régionales.
* **Ampleur :** Historique RTE ponctuel.
* **Cause probable :** Code d'erreur interne RTE historiquement utilisé pour signifier "télémesure indisponible".
* **Traitement retenu :** **Corrigé.** Remplacement ciblé par `np.nan` par `flag_minus_one()`. Les colonnes physiques où les valeurs négatives sont légitimes (`Pompage (MW)` et `Ech. physiques (MW)`) sont rigoureusement préservées.
* **Impact sur l'analyse :** Empêche d'introduire des valeurs aberrantes négatives dans le calcul de la production totale d'électricité.

---

### ANO-04 : Doublons fonctionnels multi-statuts (Consolidé vs Définitif)
* **Colonne(s) concernée(s) :** `Code INSEE région`, `Date - Heure`, `Nature`
* **Description :** Pour une même région et un même créneau temporel au pas demi-heure, deux enregistrements coexistent avec deux niveaux de consolidation distincts (`Données consolidées` et `Données définitives`).
* **Exemple observé :** 144 créneaux redondants observés sur les périodes de consolidation annuelle.
* **Ampleur :** 144 lignes dédupliquées sur la période 2021-2026.
* **Cause probable :** Période de chevauchement lors de la publication des ajustements définitifs d'une année par RTE.
* **Traitement retenu :** **Exclu / Priorisé.** Déduplication fonctionnelle via `remove_functional_duplicates()`, conservant obligatoirement l'enregistrement labellisé `Données définitives`.
* **Impact sur l'analyse :** Neutralise tout risque de sur-évaluation de la consommation ou de la production d'électricité lors des sommes et moyennes.

---

### ANO-05 : Absence structurelle d'une filière régionale vs production nulle
* **Colonne(s) concernée(s) :** `Nucléaire (MW)`, `TCH Nucléaire (%)`, `Eolien offshore`, `Hydraulique (MW)`.
* **Description :** Certaines filières n'existent physiquement pas dans certaines régions administratives (ex: absence totale de réacteur nucléaire en Île-de-France, en Bretagne ou dans les Pays de la Loire ; absence d'éolien offshore dans les régions intérieures). Ces cas génèrent des `NaN` massifs sur le taux de charge (`TCH Nucléaire (%)` = 41,67 % de NaN). À l'inverse, le solaire produit `0 MW` la nuit dans toutes les régions.
* **Exemple observé :** `TCH Nucléaire (%)` est à `NaN` pour 100 % des relevés en Île-de-France (496 507 cellules manquantes au global).
* **Ampleur :** Concerne 41,67 % des lignes pour le nucléaire.
* **Cause probable :** Spécificité du mix géographique français : un taux de charge n'a aucun sens mathématique sur une puissance installée nulle ($0 / 0$).
* **Traitement retenu :** **Conservé et contextualisé.** Pour la production volumique, la valeur est assimilée à 0 MW (aucune énergie produite). Pour le taux de charge, les NaN sont conservés afin de ne pas fausser la moyenne des régions productrices.
* **Impact sur l'analyse :** Évite d'attribuer une contre-performance à une région sur une filière dont elle ne dispose pas.

---

### ANO-06 : Ruptures de continuité lors des bascules horaires Été / Hiver
* **Colonne(s) concernée(s) :** `Date - Heure`, `Date`, `Heure`.
* **Description :** Les passages à l'heure d'été (dernier dimanche de mars : passage direct de 02:00 à 03:00) créent deux pas de demi-heure manquants en temps local. À l'inverse, le passage à l'heure d'hiver (dernier dimanche d'octobre : recul de 03:00 à 02:00) génère deux créneaux d'horodatage identiques en heure locale civile.
* **Exemple observé :** 2 créneaux d'horodatage locaux identiques le dernier dimanche d'octobre à 02:00 et 02:30.
* **Ampleur :** 2 occurrences par an sur les 12 régions (soit 48 lignes de bascule par an).
* **Cause probable :** Décalage légal du fuseau horaire français (`UTC+1` en hiver, `UTC+2` en été).
* **Traitement retenu :** **Corrigé.** Utilisation du champ horodaté ISO 8601 complet avec fuseau (`Date - Heure` converti en `datetime64[Europe/Paris]` avec prise en compte du décalage UTC).
* **Impact sur l'analyse :** Garantit la continuité de l'axe temporel sans discontinuité ni doublon artificiel.

---

### ANO-07 : Unité de puissance (MW) vs énergie (MWh) et coexistence des statuts
* **Colonne(s) concernée(s) :** Toutes les variables quantitatives de puissance (`Consommation (MW)`, `Nucléaire (MW)`, `Thermique (MW)`, `Eolien (MW)`, `Solaire (MW)`, `Hydraulique (MW)`, `Bioénergies (MW)`, `Pompage (MW)`, `Ech. physiques (MW)`) et `Nature`.
* **Description :** Les données transmises par RTE représentent des puissances moyennes appelées ou injectées au cours du pas demi-heure, exprimées en Mégawatts (**MW**). La sommation directe de ces puissances sur une journée, un mois ou un an produit une grandeur physiquement erronée (somme de flux instantanés et non une énergie consommée).
* **Exemple observé :** 48 relevés à 2 000 MW sur une journée représentent $2\,000 \times 24\,\text{h} = 48\,000\,\text{MWh}$, alors qu'une simple somme des lignes donnerait la valeur aberrante de $96\,000$.
* **Ampleur :** Concerne 100 % des variables quantitatives physiques.
* **Cause probable :** Métrologie électrique standard de gestion de l'équilibre offre/demande par le gestionnaire de réseau RTE.
* **Traitement retenu :** **Normalisé.** Tout calcul énergétique cumulé (en MWh) applique obligatoirement la formule :
  $$\text{Énergie (MWh)} = \sum \text{Puissance (MW)} \times 0.5\,\text{h}$$
  Par ailleurs, la coexistence des statuts `Données définitives` (années consolidées N-1 et antérieures) et `Données consolidées` (mois récents de l'année en cours) est systématiquement explicitée sur les graphiques et le tableau de bord.
* **Impact sur l'analyse :** Rigueur scientifique absolue dans les bilans énergétiques régionaux et respect strict du cahier des charges.
