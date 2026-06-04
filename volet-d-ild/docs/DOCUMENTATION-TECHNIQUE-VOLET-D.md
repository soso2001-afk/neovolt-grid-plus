# Documentation technique — Volet D (ESIS ILD)
## Néovolt Grid+ — Ingénierie logiciel & Data Engineering

**Auteur :** [Ton nom]  
**Groupe :** [Nom du groupe]  
**Date :** juin 2026  
**Repo :** https://github.com/soso2001-afk/neovolt-grid-plus

---

> Ce document sert de guide technique complet pour le professeur et l’équipe :  
> comprendre la solution, la tester, et l’intégrer (Data Analyst, Data Scientist, Cyber).

---

## Table des matières

1. Contexte et objectifs du Volet D  
2. Stack technique utilisée  
3. Architecture globale  
4. Structure du dépôt (`volet-d-ild/`)  
5. Prérequis  
6. Installation et démarrage (Docker — recommandé)  
7. Interface Pipeline Studio (`/studio`)  
8. API REST (endpoints)  
9. Modèle de données (PostgreSQL)  
10. Pipeline d’ingestion et journal `ingestion_logs`  
11. Validation des fichiers CSV  
12. Guide de test pas à pas (équipe)  
13. Captures d’écran à insérer  
14. Intégration avec les autres volets  
15. Dépannage (erreurs fréquentes)  
16. Annexes (commandes, variables d’environnement)

---

## 1. Contexte et objectifs du Volet D

### 1.1 Rôle dans le projet Néovolt Grid+

Le Volet D fournit la **fondation technique** de la plateforme data :

| Sans Volet D | Avec Volet D |
|--------------|--------------|
| CSV dispersés | Données centralisées en base |
| Pas d’API | Accès REST pour BI / ML / dashboards |
| Pas de traçabilité | Journal `ingestion_logs` (succès/erreur) |
| Prototype non reproductible | Docker : une commande pour tout lancer |

### 1.2 Livrables réalisés (conformes au sujet d’examen)

- Architecture technique (flux CSV → pipeline → PostgreSQL → API)  
- Prototype de pipeline d’ingestion (batch, par chunks pour gros volumes)  
- API REST (FastAPI) pour exposer les données  
- Déploiement Docker reproductible  
- Interface **Pipeline Studio** (style orchestrateur / Data Factory simplifié)  
- Journal d’ingestion avec statut, erreurs, timestamps  

---

## 2. Stack technique utilisée

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| Langage | Python 3.12 | Pipeline + API |
| Framework API | FastAPI | Endpoints REST + Swagger |
| Serveur HTTP | Uvicorn | Exécution de l’API |
| ORM | SQLAlchemy 2.x | Modèles et accès BDD |
| Base de données | PostgreSQL 16 | Stockage des données |
| Traitement données | Pandas | Lecture CSV, nettoyage, insert |
| Conteneurisation | Docker + Docker Compose | Déploiement local reproductible |
| Upload fichiers | python-multipart | Upload CSV dans le Studio |

---

## 3. Architecture globale

```
[Fichiers CSV]  ──►  [Pipeline ingestion]  ──►  [PostgreSQL]
        │                      │                      │
        │                      ▼                      │
        │              [ingestion_logs]             │
        │                      │                      │
        └──────────────────────┴──────────────────────┘
                               │
                               ▼
                    [API FastAPI — port 8000]
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
        [Power BI]      [Notebooks ML]    [Audit Cyber]
     (Volet B)           (Volet C)         (Volet E)
```

**Flux :**

1. Les CSV sont lus depuis `donnees/donnees/` (fichiers fournis) ou uploadés via `/studio`.  
2. Le pipeline charge les tables (`compteurs`, `clients`, `releves_consommation`, `releves_horaires`).  
3. Chaque import crée une ligne dans `ingestion_logs`.  
4. L’API expose les données pour les autres volets.

---

## 4. Structure du dépôt (`volet-d-ild/`)

```
volet-d-ild/
├── api/
│   ├── main.py              # Routes API + Studio
│   ├── models.py            # Modèles SQLAlchemy
│   ├── database.py          # Connexion PostgreSQL
│   ├── pipeline_service.py  # Orchestration pipeline (run, upload)
│   └── static/
│       └── studio.html      # Interface web Pipeline Studio
├── pipeline/
│   ├── ingest.py            # Ingestion CSV → PostgreSQL
│   └── validate.py          # Validation colonnes CSV
├── integration/             # (à la racine repo) docker-compose.yml
├── data/staging/            # Fichiers CSV uploadés (custom)
├── docs/
│   ├── schema-tables.md
│   └── DOCUMENTATION-TECHNIQUE-VOLET-D.md
├── Dockerfile
├── entrypoint.sh
├── requirements.txt
└── README.md
```

---

## 5. Prérequis

- **Docker Desktop** installé et démarré (Windows / Mac / Linux)  
- **Git** pour cloner le repo  
- **donnees.zip** dézippé (fourni par l’école sur Teams)  
- Navigateur web (Chrome, Edge, Firefox)  
- (Optionnel) Python 3.12+ pour exécution locale sans Docker API  

---

## 6. Installation et démarrage (Docker)

### 6.1 Cloner le projet

```powershell
git clone https://github.com/soso2001-afk/neovolt-grid-plus.git
cd neovolt-grid-plus
```

### 6.2 Préparer les données

```powershell
# Depuis la racine du repo
Expand-Archive -Path donnees.zip -DestinationPath donnees -Force
```

Les CSV doivent être dans : `donnees/donnees/`  
(ex. `compteurs.csv`, `clients.csv`, `releves_consommation.csv`).

### 6.3 Lancer la stack

```powershell
cd integration
docker compose up --build
```

**Services démarrés :**

| Service | Port | Description |
|---------|------|-------------|
| `db` | 5432 | PostgreSQL |
| `api` | 8000 | API + Studio |

### 6.4 URLs utiles

| URL | Usage |
|-----|--------|
| http://localhost:8000/studio | Interface pipeline (recommandé) |
| http://localhost:8000/docs | Swagger (test API) |
| http://localhost:8000/health | Santé API + BDD |

### 6.5 Arrêter / relancer

```powershell
# Arrêter
docker compose down

# Relancer (sans supprimer les données BDD)
docker compose up -d

# Tout réinitialiser (base vide)
docker compose down -v
docker compose up --build
```

### 6.6 Variables Docker (`integration/docker-compose.yml`)

| Variable | Valeur | Effet |
|----------|--------|--------|
| `AUTO_INGEST_ON_START` | `false` | Pas d’ingestion auto — tout passe par `/studio` |
| `INGEST_LIMIT_ROWS` | `100000` | Limite relevés en mode test (supprimer pour tout charger) |
| `DONNEES_PATH` | `/data` | Dossier CSV monté en lecture seule |

---

## 7. Interface Pipeline Studio

### 7.1 Accès

Ouvrir : **http://localhost:8000/studio**

### 7.2 Fonctionnalités

| Action | Description |
|--------|-------------|
| **Lancer tout le pipeline** | Exécute les 4 étapes dans l’ordre |
| **Charger CSV** | Upload d’un fichier pour une étape |
| **Vérifier** | Contrôle des colonnes sans importer |
| **Défaut** | Retour au CSV du dossier `donnees/` |
| **▶ Cette étape** | Lance une seule étape |

### 7.3 Fichier custom vs défaut

- **Défaut** : lit `donnees/donnees/compteurs.csv` (etc.)  
- **Custom (upload)** : fichier stocké en `volet-d-ild/data/staging/{etape}__custom.csv`  
- L’interface affiche `...__custom.csv` en mode upload.

### 7.4 Popup « Cette étape »

- **OK** = vider la table cible puis importer (`TRUNCATE`)  
- **Annuler** = ajouter sans vider (risque doublons si mêmes clés métier)

---

## 8. API REST — Endpoints principaux

### 8.1 Santé et stats

| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/health` | État API + base |
| GET | `/api/v1/stats` | Nb compteurs / relevés |

### 8.2 Données métier

| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/v1/pdl` | Liste compteurs |
| GET | `/api/v1/pdl/{id_pdl}` | Détail compteur |
| GET | `/api/v1/pdl/{id_pdl}/releves` | Relevés d’un PDL |
| GET | `/api/v1/zones/{zone}/aggregats` | Agrégats par zone |

### 8.3 Pipeline et ingestion

| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/v1/pipeline/definition` | Schéma du pipeline |
| GET | `/api/v1/pipeline/status` | Statut en cours |
| POST | `/api/v1/pipeline/run` | Lancer tout le pipeline |
| POST | `/api/v1/pipeline/steps/{id}/upload` | Upload CSV |
| DELETE | `/api/v1/pipeline/steps/{id}/upload` | Retour fichier défaut |
| GET | `/api/v1/pipeline/steps/{id}/validate` | Valider CSV |
| POST | `/api/v1/pipeline/steps/{id}/run` | Lancer une étape |
| GET | `/api/v1/ingestion/logs` | Journal des imports |

**IDs d’étapes :** `compteurs`, `clients`, `releves`, `releves_horaires`

---

## 9. Modèle de données

Voir `docs/schema-tables.md`.

**Tables :**

- `ingestion_logs` — journal de chaque import  
- `compteurs`, `clients`, `releves_consommation`, `releves_horaires`

Chaque ligne métier contient : `id` (PK), `ingestion_timestamp`, `ingestion_log_id`.

---

## 10. Pipeline et journal

### 10.1 Ordre d’exécution

1. compteurs  
2. clients  
3. releves_consommation  
4. releves_horaires  

### 10.2 Table `ingestion_logs`

| statut | Signification |
|--------|----------------|
| `running` | Import en cours |
| `success` | OK, `lignes_ingerees` renseigné |
| `error` | Échec, détail dans `message_erreur` |

---

## 11. Validation CSV

Fichier : `pipeline/validate.py`

Colonnes obligatoires par étape — voir section 9 de `schema-tables.md`.

L’upload est **refusé** si colonnes manquantes.

---

## 12. Guide de test pas à pas (équipe)

### Test 1 — Démarrage

1. `docker compose up --build` dans `integration/`  
2. Ouvrir http://localhost:8000/health → `{"status":"ok","database":"ok"}`  

### Test 2 — Studio + fichier test compteurs

1. Ouvrir `/studio`  
2. Étape **Ingestion compteurs** → fichier `volet-d-ild/data/staging/test_compteurs.csv`  
3. **Charger CSV** → message vert « Fichier valide — 3 lignes »  
4. **▶ Cette étape** → OK (vider table)  
5. Vérifier : statut `success`, 3 lignes dans les logs  

### Test 3 — API Swagger

1. http://localhost:8000/docs  
2. Tester `GET /api/v1/pdl?limit=5`  
3. Tester `GET /api/v1/ingestion/logs`  

### Test 4 — Connexion Power BI / Python (Volet B/C)

- URL base API : `http://localhost:8000`  
- Exemple Python : `requests.get("http://localhost:8000/api/v1/pdl/PDL-000001/releves")`  

---

## 13. Captures d’écran à insérer dans le Word

> Prendre ces captures sur ta machine et les coller aux emplacements indiqués.

| N° | Titre | Comment obtenir |
|----|-------|-----------------|
| 1 | Docker Desktop — conteneurs Running | Onglet Containers : `integration-api-1`, `integration-db-1` |
| 2 | Terminal `docker compose up --build` | Logs de build + « Application startup complete » |
| 3 | Pipeline Studio — vue globale | http://localhost:8000/studio |
| 4 | Studio — upload fichier custom | Bloc compteurs avec `compteurs__custom.csv (upload)` |
| 5 | Studio — étape success | Badge vert `success` + 3 lignes |
| 6 | Journal ingestion_logs | Table à droite dans le Studio |
| 7 | Swagger `/docs` | Page documentation interactive |
| 8 | Endpoint `/health` | Réponse JSON dans navigateur |
| 9 | Structure dossier `volet-d-ild` | Explorateur Windows / VS Code |
| 10 | docker-compose.yml | Fichier ouvert dans l’éditeur |

---

## 14. Intégration autres volets

| Volet | Utilise Volet D via |
|-------|---------------------|
| B — Data Analyst | API ou export ; données propres en BDD |
| C — Data Scientist | API + tables PostgreSQL pour features |
| E — Cyber | Audit API, logs, surface d’attaque Docker |
| A — CPID | Schéma d’archi dans `tronc-commun/` |

---

## 15. Dépannage

| Problème | Cause | Solution |
|----------|-------|----------|
| `duplicate key id_pdl` | Import sans vider table | **OK** dans popup ou cocher reset pipeline |
| 700 lignes au lieu de 3 | Fichier **default** utilisé | Re-**Charger CSV** puis vérifier `__custom.csv` |
| API ne démarre pas | Docker arrêté | Lancer Docker Desktop |
| `multipart not installed` | Dépendance manquante | `pip install python-multipart` (déjà dans requirements) |
| Port 8000 occupé | Autre service | Changer port dans docker-compose |

---

## 16. Annexes

### Commandes Git (branche Volet D)

```powershell
git checkout volet-d/api-pipeline
git add volet-d-ild integration
git commit -m "feat(volet-d): documentation et pipeline"
git push -u origin volet-d/api-pipeline
```

### Fichiers de test fournis

- `volet-d-ild/data/staging/test_compteurs.csv` (3 lignes)  
- `test_clients.csv`, `test_releves.csv`, `test_releves_horaires.csv` (générés pour tests)

---

*Fin du document — Néovolt Grid+ Volet D*
