# Volet D — Ingénierie logiciel & Data Engineering (ESIS ILD)

Pipeline d'ingestion, API REST, PostgreSQL et **Pipeline Studio** (interface web).

## Documentation

| Fichier | Contenu |
|---------|---------|
| **`docs/DOCUMENTATION-TECHNIQUE-VOLET-D.docx`** | Dossier technique complet (architecture, Docker, Studio, API, guide de test, emplacements pour captures d'écran) — à remettre au prof / à partager avec l'équipe |
| `docs/DOCUMENTATION-TECHNIQUE-VOLET-D.md` | (lecture dans l'éditeur ou sur GitHub) |
| `docs/schema-tables.md` | Schéma PostgreSQL + colonnes obligatoires pour la validation CSV |
| **Ce README** | Démarrage rapide et commandes pour tester en local |

> Pour comprendre le Volet D de A à Z ou préparer la démo : commencer par le **fichier Word** dans `docs/`.  
> Pour lancer et tester rapidement : suivre les sections ci-dessous.

---

## Prérequis

| Outil | Version | Vérification |
|-------|---------|--------------|
| Docker Desktop | récent | `docker --version` |
| Git | — | `git --version` |
| Données examen | `donnees.zip` | fourni sur Teams |

**Docker Desktop doit être démarré** avant toute commande.

---

## Démarrage rapide (recommandé — Docker)

### 1. Cloner le repo

```powershell
git clone https://github.com/soso2001-afk/neovolt-grid-plus.git
cd neovolt-grid-plus
```

### 2. Préparer les données CSV

```powershell
# Depuis la racine du repo
Expand-Archive -Path donnees.zip -DestinationPath donnees -Force
```

Vérifier que ces fichiers existent :

```
donnees/donnees/compteurs.csv
donnees/donnees/clients.csv
donnees/donnees/releves_consommation.csv
donnees/donnees/releves_horaires_echantillon.csv
```

### 3. Lancer la plateforme

```powershell
cd integration
docker compose up --build
```

Attendre le message : `Application startup complete` (Uvicorn sur le port 8000).

### 4. Ouvrir dans le navigateur

| URL | Usage |
|-----|--------|
| http://localhost:8000/studio | **Interface pipeline** (lancer imports, upload CSV) |
| http://localhost:8000/docs | Documentation API interactive (Swagger) |
| http://localhost:8000/health | Vérifier que l'API et la BDD répondent |

---

## Tester en 5 minutes (nouveau membre)

### Test santé

```powershell
Invoke-RestMethod http://localhost:8000/health
```

Réponse attendue : `status: ok`, `database: ok`

### Test Studio — une étape avec fichier de test

1. Ouvrir http://localhost:8000/studio  
2. Bloc **Ingestion compteurs**  
3. Choisir le fichier : `volet-d-ild/data/staging/test_compteurs.csv`  
4. Cliquer **Charger CSV** → message « Fichier valide — 3 lignes »  
5. Cliquer **▶ Cette étape**  
6. Dans la popup : **OK** (vide la table avant import)  
7. Vérifier : statut **success**, **3 lignes** dans le journal à droite  

### Test API (Swagger)

1. http://localhost:8000/docs  
2. `GET /api/v1/stats` → Execute  
3. `GET /api/v1/pdl` → limit=5  
4. `GET /api/v1/ingestion/logs` → voir les imports  

---

## Interface Pipeline Studio

### Actions disponibles

| Bouton | Effet |
|--------|--------|
| **▶ Lancer tout le pipeline** | 4 étapes : compteurs → clients → relevés → horaires |
| **Charger CSV** | Fichier personnalisé pour l'étape (stocké en `data/staging/`) |
| **Vérifier** | Contrôle colonnes sans importer |
| **Défaut** | Retour au CSV du dossier `donnees/donnees/` |
| **▶ Cette étape** | Lance uniquement cette étape |
| **↻ Actualiser** | Rafraîchit statuts et métriques |

### Fichier custom vs défaut

- **Défaut** : `compteurs.csv` dans `donnees/donnees/`  
- **Custom** : après upload, affiché comme `compteurs__custom.csv (upload)`  

### Popup « Cette étape »

- **OK** = vider la table (`TRUNCATE`) puis importer  
- **Annuler** = ajouter sans vider (attention aux doublons `id_pdl`, etc.)

---

## Commandes Docker utiles

```powershell
cd integration

# Démarrer (premier build)
docker compose up --build

# Démarrer en arrière-plan
docker compose up -d --build

# Voir les logs API
docker compose logs -f api

# Arrêter
docker compose down

# Tout réinitialiser (base vide + volumes)
docker compose down -v
docker compose up --build
```

---

## Variables d'environnement (`integration/docker-compose.yml`)

| Variable | Valeur actuelle | Description |
|----------|-----------------|-------------|
| `AUTO_INGEST_ON_START` | `false` | Pas d'ingestion auto au démarrage → utiliser `/studio` |
| `INGEST_LIMIT_ROWS` | `100000` | Limite relevés en mode test. **Supprimer la ligne** pour charger ~513k lignes |
| `DONNEES_PATH` | `/data` | CSV montés depuis `donnees/donnees/` |

---

## API — endpoints pour les autres volets

**Base URL :** `http://localhost:8000`

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/health` | Santé |
| GET | `/api/v1/stats` | Nb compteurs / relevés |
| GET | `/api/v1/pdl` | Liste compteurs (`?zone=`, `?limit=`) |
| GET | `/api/v1/pdl/{id_pdl}` | Détail compteur |
| GET | `/api/v1/pdl/{id_pdl}/releves` | Relevés (`?date_debut=`, `?date_fin=`) |
| GET | `/api/v1/zones/{zone}/aggregats` | Agrégats par zone |
| GET | `/api/v1/ingestion/logs` | Journal des imports |
| POST | `/api/v1/pipeline/run` | Lancer pipeline (`{"reset_db": true}`) |
| POST | `/api/v1/pipeline/steps/{id}/run` | Une étape (`compteurs`, `clients`, `releves`, `releves_horaires`) |

Exemple PowerShell :

```powershell
Invoke-RestMethod "http://localhost:8000/api/v1/pdl?limit=3"
Invoke-RestMethod "http://localhost:8000/api/v1/pdl/PDL-000001/releves?limit=10"
```

Exemple Python :

```python
import requests
r = requests.get("http://localhost:8000/api/v1/stats")
print(r.json())
```

---

## Structure du code

```
volet-d-ild/
├── api/
│   ├── main.py              # Routes FastAPI
│   ├── models.py            # Tables SQLAlchemy
│   ├── database.py          # Connexion PostgreSQL
│   ├── pipeline_service.py  # Orchestration + upload
│   └── static/studio.html   # Interface web
├── pipeline/
│   ├── ingest.py            # Ingestion CSV → PostgreSQL
│   └── validate.py          # Validation colonnes
├── data/staging/            # CSV uploadés (*__custom.csv)
├── docs/
│   ├── schema-tables.md
│   └── DOCUMENTATION-TECHNIQUE-VOLET-D.docx
├── Dockerfile
├── entrypoint.sh
└── requirements.txt
```

---

## Démarrage local (sans Docker API — avancé)

```powershell
cd volet-d-ild
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env

# PostgreSQL seul via Docker
cd ..\integration
docker compose up db -d

# Ingestion manuelle
cd ..\volet-d-ild
python -m pipeline.ingest

# API en local
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Fichiers de test fournis

| Fichier | Lignes | Étape |
|---------|--------|-------|
| `data/staging/test_compteurs.csv` | 3 | compteurs |
| `data/staging/test_clients.csv` | 3 | clients |
| `data/staging/test_releves.csv` | 3 | relevés |
| `data/staging/test_releves_horaires.csv` | 3 | relevés horaires |

---

## Dépannage

| Problème | Solution |
|----------|----------|
| `duplicate key` sur `id_pdl` | Relancer avec **OK** (vider table) ou utiliser des IDs nouveaux |
| 700 lignes au lieu de 3 | Re-**Charger CSV** ; vérifier affichage `__custom.csv (upload)` |
| `Cannot connect to Docker` | Démarrer **Docker Desktop** |
| Port 8000 déjà utilisé | `docker compose down` ou changer le port dans `docker-compose.yml` |
| Upload échoue (colonnes) | Voir colonnes obligatoires dans `docs/schema-tables.md` |

---

## Intégration équipe

| Volet | Comment nous utiliser |
|-------|----------------------|
| **B — Data Analyst** | API `http://localhost:8000/api/v1/...` ou Power BI sur PostgreSQL `:5432` |
| **C — Data Scientist** | API + accès BDD `postgresql://neovolt:neovolt@localhost:5432/neovolt` |
| **E — Cyber** | Audit API, logs `ingestion_logs`, stack Docker |

**Contact Volet D :** Sofiane mahmoudi / teams
