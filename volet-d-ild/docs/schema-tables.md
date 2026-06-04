# Schéma des tables

## ingestion_logs (journal)

| Colonne | Type | Description |
|---------|------|-------------|
| **id** | PK | Identifiant unique du log |
| fichier | texte | Nom du fichier CSV source |
| table_cible | texte | Table de destination |
| statut | texte | `success` ou `error` |
| message_erreur | texte | Rempli en cas d'erreur |
| lignes_ingerees | entier | Nombre de lignes chargées |
| **ingestion_timestamp** | datetime | Date/heure de l'ingestion |

## Tables métier (compteurs, clients, releves_…)

Chaque table contient :

| Colonne | Description |
|---------|-------------|
| **id** | PK auto (identifiant technique) |
| **ingestion_timestamp** | Quand la ligne a été chargée |
| **ingestion_log_id** | FK vers `ingestion_logs.id` |
| … | Colonnes métier du CSV |

Contraintes d'unicité métier : `id_pdl`, `(id_pdl, date)`, etc.

## Validation CSV (Studio)

Avant chaque import, le fichier est contrôlé (`pipeline/validate.py`) :

| Étape | Colonnes obligatoires |
|-------|------------------------|
| compteurs | id_pdl, id_client, zone, type_client, type_compteur, statut |
| clients | id_client, segment, commune, code_postal, date_entree |
| releves | id_pdl, date, consommation_kwh, zone |
| releves_horaires | id_pdl, horodatage, consommation_kwh |

Upload refusé si colonnes manquantes. Bouton **Vérifier** dans `/studio`.
