# Audit sécurité du prototype technique – Volet D

## Objectif

Cette partie complète le volet cybersécurité en tenant compte de l’architecture technique mise en place par le volet D.

Le volet D fournit la base technique du projet Néovolt Grid+ : ingestion de fichiers CSV, stockage PostgreSQL, API FastAPI, interface Pipeline Studio et déploiement avec Docker Compose.

L’objectif de cette analyse est donc d’identifier les principaux points de vigilance sécurité sur ce prototype, sans le traiter comme un système de production complet. L’idée est de proposer des mesures réalistes, adaptées au contexte du projet et utiles pour la soutenance.

## Éléments techniques pris en compte

D’après la documentation du volet D, le prototype repose sur les composants suivants :

| Composant | Rôle dans le projet | Point de vigilance cybersécurité |
|---|---|---|
| FastAPI / Uvicorn | Exposition de l’API REST | Sécurisation des endpoints et contrôle des accès |
| PostgreSQL 16 | Stockage des données ingérées | Protection de la base, droits, sauvegardes |
| Docker Compose | Déploiement reproductible du prototype | Ports exposés, secrets, isolation des conteneurs |
| Pipeline Studio | Interface de pilotage du pipeline | Accès à protéger, actions sensibles à tracer |
| Upload CSV | Chargement de fichiers personnalisés | Validation stricte des fichiers et contrôle des erreurs |
| `ingestion_logs` | Journal des imports | Traçabilité, audit et détection d’anomalies |
| Swagger `/docs` | Documentation interactive de l’API | Exposition à limiter hors environnement de test |

## Analyse de sécurité de l’API FastAPI

L’API FastAPI permet d’exposer les données et de piloter certaines actions du pipeline.

Les endpoints identifiés dans la documentation technique sont notamment :

- `/health`
- `/api/v1/stats`
- `/api/v1/pdl`
- `/api/v1/pdl/{id}/releves`
- `/api/v1/ingestion/logs`
- `/api/v1/pipeline/run`
- `/api/v1/pipeline/steps/{id}/upload`
- `/api/v1/pipeline/steps/{id}/run`

Même si le prototype fonctionne en local, certains endpoints sont sensibles. Par exemple, les endpoints liés au pipeline permettent de lancer des traitements ou d’uploader des fichiers. Ils ne devraient pas être accessibles librement dans un environnement réel.

Les mesures recommandées sont :

- protéger les endpoints sensibles par authentification ;
- limiter l’accès à Swagger `/docs` en dehors du contexte de test ;
- journaliser les appels aux endpoints critiques ;
- vérifier les paramètres reçus par l’API ;
- éviter d’exposer l’API directement sans filtrage ;
- prévoir une limitation de débit sur les routes sensibles.

## Sécurité de l’upload CSV

Le Pipeline Studio permet d’uploader des fichiers CSV personnalisés. C’est utile pour tester le pipeline, mais c’est aussi un point d’entrée à surveiller.

Un fichier mal structuré, trop volumineux ou volontairement modifié peut perturber l’ingestion, provoquer des erreurs ou fausser les données importées.

Le volet D a déjà prévu une validation des colonnes avant import, ce qui est un point positif. Cette validation limite les erreurs de structure et améliore la qualité des données intégrées.

Mesures recommandées :

- conserver la validation des colonnes avant import ;
- limiter la taille des fichiers uploadés ;
- refuser les formats non attendus ;
- journaliser chaque upload ;
- identifier l’utilisateur à l’origine de l’import ;
- éviter l’écrasement non contrôlé de données ;
- prévoir un message d’erreur clair sans exposer d’informations techniques sensibles.

## Sécurité de PostgreSQL

PostgreSQL stocke les données issues du pipeline. Il s’agit donc d’un composant important, car il contient les données exploitées ensuite par l’API, le BI ou les autres volets.

Les risques principaux sont :

- accès non autorisé à la base ;
- droits trop larges ;
- fuite ou altération des données ;
- absence de sauvegarde ;
- exposition du port PostgreSQL sans contrôle.

Mesures recommandées :

- limiter l’exposition du port PostgreSQL au strict nécessaire ;
- utiliser un compte applicatif avec des droits limités ;
- éviter les identifiants en clair dans le dépôt GitHub ;
- stocker les secrets dans un fichier `.env` non versionné ;
- prévoir des sauvegardes régulières ;
- journaliser les erreurs et accès sensibles ;
- séparer les droits lecture/écriture lorsque c’est possible.

## Sécurité Docker Compose

Le déploiement Docker Compose rend le prototype reproductible, ce qui est positif pour le projet. En revanche, il faut éviter certaines mauvaises pratiques.

Points de vigilance :

- ports exposés inutilement ;
- secrets stockés en clair ;
- conteneurs lancés avec trop de privilèges ;
- absence de contrôle sur les volumes ;
- images non maîtrisées ou non mises à jour.

Mesures recommandées :

- exposer uniquement les ports nécessaires ;
- stocker les variables sensibles dans `.env` ;
- ne pas versionner les secrets ;
- limiter les privilèges des conteneurs ;
- documenter les ports utilisés ;
- vérifier les dépendances Python ;
- éviter les images Docker obsolètes.

## Sécurité de Pipeline Studio

Pipeline Studio est l’interface qui permet de lancer le pipeline complet, de charger un fichier CSV, de vérifier les colonnes et d’exécuter une étape seule.

Cette interface facilite la démonstration, mais elle donne aussi accès à des actions sensibles. Dans un environnement réel, elle ne devrait pas être accessible à tout le monde.

Mesures recommandées :

- limiter l’accès à l’interface aux profils techniques autorisés ;
- journaliser les actions réalisées depuis l’interface ;
- protéger les actions sensibles comme le lancement du pipeline ou l’upload ;
- afficher clairement les erreurs sans exposer trop de détails internes ;
- désactiver l’interface ou la protéger fortement hors environnement de test.

## Exploitation des `ingestion_logs`

Le journal `ingestion_logs` est un point intéressant pour le volet cybersécurité.

Il permet de suivre :

- le fichier importé ;
- la table cible ;
- le statut de l’import ;
- les erreurs ;
- le nombre de lignes ingérées ;
- le timestamp d’ingestion.

Ce journal peut être utilisé pour l’audit, la traçabilité et la détection d’anomalies. Par exemple, un nombre anormal de lignes importées, des erreurs répétées ou des imports hors période prévue peuvent être surveillés.

Exemples d’alertes possibles :

| Situation observée | Risque possible | Réaction proposée |
|---|---|---|
| Erreurs répétées sur un même type de fichier | Fichier malveillant ou mauvais format | Vérifier le fichier et bloquer l’import si nécessaire |
| Import d’un fichier avec volume anormal | Données incohérentes ou injection massive | Contrôler le fichier et comparer avec les volumes attendus |
| Import hors période prévue | Action non autorisée ou erreur d’exploitation | Identifier l’utilisateur et vérifier la justification |
| Échec répété de validation des colonnes | Tentative ou erreur de manipulation | Refuser l’import et journaliser l’événement |

## Synthèse des risques et mesures

| Risque | Composant concerné | Mesure recommandée |
|---|---|---|
| Accès non autorisé à l’API | FastAPI | Authentification, journalisation, limitation des endpoints sensibles |
| Exposition excessive de Swagger | `/docs` | Limitation à l’environnement de test |
| Upload de fichier non conforme | Pipeline Studio / CSV | Validation stricte, taille maximale, logs |
| Fuite de données en base | PostgreSQL | Droits limités, secrets protégés, sauvegardes |
| Secrets exposés dans GitHub | Docker / API / BDD | `.env`, `.gitignore`, revue du dépôt |
| Mauvaise manipulation du pipeline | Pipeline Studio | Accès restreint, traçabilité, validation |
| Perte de traçabilité | Ingestion | Exploitation des `ingestion_logs` |

## Conclusion

L’architecture du volet D apporte une base technique claire au projet Néovolt Grid+ : pipeline d’ingestion, API, base PostgreSQL, Docker Compose et interface de pilotage.

Du point de vue cybersécurité, les priorités sont la protection de l’API, la sécurisation des uploads CSV, la maîtrise des accès à PostgreSQL, la protection des secrets, la limitation des ports exposés et l’exploitation des `ingestion_logs`.

Cette analyse permet d’aligner le volet E-Cyber avec le prototype réel du groupe, tout en gardant une approche réaliste pour un projet de sprint.
