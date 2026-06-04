# Néovolt Grid+

Projet examen — groupe.

```
tronc-commun/          → travail commun
volet-a-cpid/
volet-b-data-analyst/
volet-c-data-scientist/
volet-d-ild/           → pipeline, API, Docker
volet-e-cyber/
integration/           → docker-compose, démo
donnees/               → CSV (dézip donnees.zip ici)
docs/                  → docs équipe
```

Chacun travaille dans son dossier volet.

## Git — règles équipe

**Ne pas pousser sur `main`.** Branche protégée : seul le propriétaire du repo peut fusionner sur `main`.  
Si Git refuse ton push → crée une branche + Pull Request (c’est normal).

### Workflow

1. Récupérer la dernière version :
   ```bash
   git checkout main
   git pull
   ```
2. Créer une branche depuis `main` :
   ```bash
   git checkout -b volet-d/ma-feature
   ```
3. Travailler, committer sur **ta branche** :
   ```bash
   git add .
   git commit -m "feat(volet-d): description courte"
   git push -u origin volet-d/ma-feature
   ```
4. Ouvrir une **Pull Request** sur GitHub → fusion dans `main` après relecture (ou accord du groupe).

### Nom des branches

| Format | Exemple |
|--------|---------|
| `volet-a/...` | `volet-a/cadrage-budget` |
| `volet-b/...` | `volet-b/dashboard-powerbi` |
| `volet-c/...` | `volet-c/modele-fraude` |
| `volet-d/...` | `volet-d/api-releves` |
| `volet-e/...` | `volet-e/audit-api` |
| `tronc-commun/...` | `tronc-commun/architecture` |

### Messages de commit

`type(scope): description` — ex. `feat(volet-d): ajout endpoint relevés`

Types : `feat`, `fix`, `docs`, `chore`
