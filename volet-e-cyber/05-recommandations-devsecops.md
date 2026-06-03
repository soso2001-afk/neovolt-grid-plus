# Recommandations DevSecOps – Volet cybersécurité Néovolt

## Objectif

L'objectif principal est la  proposition des premières recommandations DevSecOps pour le projet Néovolt Grid+.

ces recommandations sont réalistes pour un sprint court, mais elles permettent aussi de montrer ce qu’il faudrait renforcer dans une version industrialisée.

## Gestion des accès

Le premier point important concerne les accès. Les utilisateurs ne doivent pas tous avoir les mêmes droits.

Par exemple, une personne de la direction financière n’a pas besoin des mêmes accès qu’un administrateur technique, qu’un analyste data ou qu’un utilisateur métier du dashboard Power BI.

Les mesures à prévoir sont donc :

- limiter les droits selon le rôle de chaque utilisateur ;
- séparer les comptes administrateurs des comptes standards ;
- activer l’authentification forte sur les accès sensibles ;
- revoir régulièrement les comptes actifs ;
- supprimer les comptes inutilisés ;
- limiter les accès prestataires dans le temps.

Cette mesure est importante parce que des éléments comme le VPN, l’Active Directory, la plateforme data ou le dashboard Power BI peuvent devenir des points d’entrée ou de fuite si les accès sont mal maîtrisés.

## Gestion des secrets

Les mots de passe, clés API, tokens et chaînes de connexion ne doivent pas être écrits directement dans les scripts, les notebooks ou les fichiers poussés sur GitHub.

Dans le cadre du projet, il faut donc éviter de mettre des identifiants en clair dans le dépôt.

Les bonnes pratiques à appliquer sont :

- utiliser un fichier `.env` pour les variables sensibles ;
- ajouter `.env` dans le `.gitignore` ;
- éviter les identifiants en clair dans les notebooks ;
- ne pas partager de mots de passe dans les fichiers du projet ;
- changer un secret s’il a été exposé par erreur.

Même sur un prototype, cette règle est importante. Un secret exposé peut donner accès à une base de données, une API ou un service interne.

## Journalisation

Pour pouvoir détecter un incident, il faut que les actions importantes soient tracées.

Dans le contexte Néovolt, les événements à journaliser en priorité sont :

- les connexions réussies et échouées ;
- les accès refusés ;
- les exports de données ;
- les modifications de configuration ;
- les changements de droits ;
- les accès aux données sensibles ;
- les actions sur les dashboards Power BI.

Ces logs permettent ensuite d’alimenter la logique SOC/SIEM que nous avons commencé à définir. Sans journalisation, il devient difficile de comprendre ce qui s’est passé en cas d’incident.

## Sécurisation des communications

Les échanges entre les composants doivent être protégés.

Dans notre cas, cela concerne notamment les flux entre la plateforme data, les bases de données, l’API, le portail client, le BI et les éventuels exports.

Les mesures proposées sont :

- utiliser HTTPS/TLS pour les API et interfaces web ;
- éviter les flux non chiffrés ;
- limiter les flux réseau entre les zones ;
- ne pas créer de connexion directe non justifiée vers le SCADA ;
- documenter les flux autorisés.

Le SCADA doit rester particulièrement protégé, car il est lié à la supervision du réseau énergétique. La plateforme data ne doit pas fragiliser cet environnement.

## Segmentation réseau

La segmentation permet de limiter les dégâts si un composant est compromis.

Pour Néovolt, on peut raisonner avec plusieurs zones :

| Zone | Éléments concernés | Objectif sécurité |
|---|---|---|
| Zone Internet | Portail client | Exposer uniquement ce qui est nécessaire |
| DMZ | API espace client, passerelle de télérelève | Filtrer les échanges entre Internet et le SI interne |
| Zone interne | Plateforme data, bases de données, BI | Protéger les données et traitements internes |
| Zone critique | SCADA | Isoler les systèmes liés à la continuité énergétique |
| Zone administration | AD, sauvegardes, supervision | Protéger les accès privilégiés |

Cette séparation est importante parce qu’une attaque sur le portail client ou l’API ne doit pas permettre d’atteindre directement les bases de données, l’Active Directory ou le SCADA.

## Sécurité des fichiers et exports

Les fichiers préparés par le volet Data Analyst doivent aussi être protégés.

Même s’il ne s’agit pas toujours de données brutes individuelles, les fichiers CSV et les dashboards peuvent contenir ou révéler des informations sensibles : consommation, incidents réseau, fraude, indicateurs métier.

Les mesures proposées sont :

- stocker les fichiers dans un espace contrôlé ;
- éviter les partages publics ;
- limiter les exports depuis Power BI ;
- privilégier les données agrégées ;
- supprimer les fichiers temporaires inutiles ;
- journaliser les téléchargements sensibles.

Un export mal contrôlé peut facilement sortir du périmètre sécurisé, surtout s’il est téléchargé en Excel ou CSV.

## Contrôle du code et des notebooks

Même si le projet est réalisé en sprint court, il faut garder une bonne hygiène dans le dépôt GitHub.

Les actions proposées sont :

- utiliser des messages de commit clairs ;
- éviter de pousser des fichiers inutiles ;
- vérifier qu’aucun secret n’est présent dans le dépôt ;
- documenter les scripts et notebooks importants ;
- conserver l’historique GitHub pour prouver la contribution de chacun ;
- relire les fichiers avant intégration dans la branche principale.

Cela permet de garder un projet propre et défendable lors de la soutenance.

## Sécurité du dashboard Power BI

Le dashboard Power BI produit par le volet Data Analyst doit être sécurisé, car il sert à la prise de décision.

Les mesures proposées sont :

- limiter l’accès aux utilisateurs autorisés ;
- appliquer le MFA via Microsoft 365 ;
- gérer les droits selon les profils métiers ;
- éviter le partage public du rapport ;
- limiter les exports ;
- journaliser les consultations ;
- revoir régulièrement les habilitations ;
- afficher des données agrégées lorsque le détail individuel n’est pas nécessaire.

L’objectif est de permettre aux décideurs d’avoir une vision claire sans exposer plus de données que nécessaire.

## Conclusion

Ces recommandations DevSecOps permettent de poser une base de sécurité réaliste pour le prototype Néovolt Grid+.

Elles couvrent les accès, les secrets, la journalisation, la segmentation, les flux, les fichiers préparés, les exports et le dashboard Power BI.

Elles ne remplacent pas une architecture de sécurité complète, mais elles montrent que la sécurité a été pensée dès la conception du projet et qu’elle est adaptée au contexte d’une infrastructure énergétique critique.
