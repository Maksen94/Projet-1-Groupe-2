# Journal des Anomalies de Données (éCO2mix Régional)

> Conformément à la section 8 du cahier des charges, toute anomalie constatée dans le jeu de données brut `eco2mix-regional-cons-def.csv` est répertoriée dans ce document. Aucune ligne ou colonne n'est supprimée ou modifiée sans traçabilité.

---

## Synthèse du registre des anomalies

| Identifiant | Colonne(s) concernée(s) | Description sommaire | Ampleur | Traitement retenu | Impact sur l'analyse |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ANO-01** | `Column 30` | Colonne fantôme 100 % vide | 2 874 816 lignes (100 %) | Exclu (suppression de la colonne) | Schéma épuré, allègement mémoire |
| **ANO-02** | Colonnes métriques & texte | Valeurs manquantes déguisées (`""`, `"nr"`, etc.) | Variable selon les séries anciennes | Corrigé (`NaN` standard) | Évite les erreurs de cast et d'agrégation |
| **ANO-03** | Filières de production | Valeurs sentinelles `-1` (absence de mesure) | Selon disponibilité locale des filières | Corrigé (`NaN` ciblé sur filières positives) | Évite les productions d'énergie négatives aberrantes |
| **ANO-04** | `Code INSEE région`, `Date - Heure`, `Nature` | Doublons fonctionnels (même région et créneau) | 335 lignes (~0,012 %) | Exclu (priorité accordée aux données définitives) | Évite le double comptage lors des agrégations |

---

## Fiches détaillées des anomalies

### ANO-01 : Colonne fantôme sans intitulé métier
* **Colonne(s) concernée(s) :** `Column 30`
* **Description :** Une colonne additionnelle sans en-tête explicite apparaît en fin de ligne dans l'export brut. Elle ne contient aucune valeur (100 % de valeurs nulles).
* **Exemple observé :** `;` résiduel en fin de chaque ligne CSV.
* **Ampleur :** 2 874 816 lignes affectées (100 % du fichier).
* **Cause probable :** Export automatique depuis la plateforme Open Data (ODRE/RTE) laissant un délimiteur final sans champ associé.
* **Traitement retenu :** Exclu. Suppression systématique de la colonne via la fonction `drop_ghost_columns()` dans `src/cleaning.py`.
* **Impact sur l'analyse :** Aucun impact sur les valeurs métier ; suppression indispensable pour garantir la propreté du schéma de données.

---

### ANO-02 : Valeurs manquantes déguisées en chaînes de caractères
* **Colonne(s) concernée(s) :** Colonnes de production, de consommation et métriques associées.
* **Description :** Des cellules censées contenir des données numériques ou nulles contiennent des valeurs textuelles signifiant l'absence d'information (`""`, `"nan"`, `"nr"`, `"non renseigné"`, `"-"`).
* **Exemple observé :** Chaînes vides ou mentions `"nr"` dans les relevés anciens (notamment antérieures à 2016).
* **Ampleur :** Présent sur les premières années d'historique (2013-2015).
* **Cause probable :** Changement de nomenclature et d'infrastructure de transmission des données au sein des services RTE au cours de la décennie.
* **Traitement retenu :** Corrigé. Remplacement de ces valeurs par `np.nan` par la fonction `clean_fake_nulls()` avant conversion numérique systématique en `float64`.
* **Impact sur l'analyse :** Permet aux calculs statistiques (moyennes, sommes, médianes) de traiter correctement les données manquantes sans bloquer l'analyse.

---

### ANO-03 : Valeur sentinelle `-1` d'absence sur filières non négatives
* **Colonne(s) concernée(s) :** `Thermique (MW)`, `Nucléaire (MW)`, `Eolien (MW)`, `Solaire (MW)`, `Hydraulique (MW)`, `Bioénergies (MW)`, `Eolien terrestre`, `Eolien offshore`.
* **Description :** Des valeurs égales à `-1` apparaissent sur des filières de production d'énergie alors qu'une production physique ne peut être que positive ou nulle.
* **Exemple observé :** `-1` relevé sur certaines filières éoliennes ou solaires lors d'indisponibilité de capteur.
* **Ampleur :** Quelques dizaines de milliers d'enregistrements sur l'ensemble de l'historique.
* **Cause probable :** Convention RTE historique codant l'indisponibilité technique par la valeur `-1`.
* **Traitement retenu :** Corrigé. Remplacement des `-1` par `np.nan` uniquement pour les filières strictement non-négatives via `flag_minus_one()`. Les colonnes où le négatif est réel (`Pompage (MW)` et `Ech. physiques (MW)`) conservent leurs valeurs négatives.
* **Impact sur l'analyse :** Empêche de fausser le mix de production régional et les bilans d'autosuffisance avec des énergies négatives non réelles.

---

### ANO-04 : Doublons fonctionnels multi-statuts (Consolidé vs Définitif)
* **Colonne(s) concernée(s) :** `Code INSEE région`, `Date - Heure`, `Nature`
* **Description :** Pour un même instant temporel et une même région administrative, plusieurs enregistrements coexistent avec des statuts de révision différents (`Données consolidées` et `Données définitives`).
* **Exemple observé :** 335 doublons sur des créneaux charnières lors des révisions annuelles RTE.
* **Ampleur :** 335 lignes supprimées.
* **Cause probable :** Superposition temporelle lors des publications d'ajustement périodique par RTE.
* **Traitement retenu :** Exclu / Priorisé. Conservation de la ligne avec le statut de révision le plus élevé (`Données définitives` > `Données consolidées`) via `remove_functional_duplicates()`.
* **Impact sur l'analyse :** Élimine tout risque de double comptage de consommation ou de production lors des agrégations mensuelles ou annuelles.

