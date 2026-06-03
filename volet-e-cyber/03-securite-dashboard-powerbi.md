# Jour 3 – Sécurisation du dashboard Power BI et des données Data Analyst

## Objectif

L’objectif de cette partie est d’intégrer les impacts cybersécurité du volet Data Analyst dans le projet Néovolt Grid+.  
Le volet Data Analyst produit un dashboard Power BI à partir de données préparées liées à la consommation, aux incidents réseau, aux cas de fraude confirmés et aux indicateurs globaux. Ces éléments doivent être sécurisés car ils servent à la prise de décision métier et peuvent contenir ou révéler des informations sensibles.

## Données et livrables concernés

Les éléments transmis par mes collègues du  volet Data Analyst sont :

- notebooks d’exploration et de qualité des données ;
- notebooks d’analyse ;
- notebook de préparation du dashboard Power BI ;
- fichiers CSV préparés pour Power BI ;
- fichier Power BI `.pbix` ;
- données préparées sur les incidents réseau ;
- données préparées sur les cas de fraude confirmés.

## Risques identifiés

| Élément concerné | Risque cybersécurité | Impact possible |
|---|---|---|
| Dashboard Power BI | Partage non maîtrisé du rapport | Fuite d’informations métier ou données sensibles |
| CSV préparés | Stockage ou diffusion non contrôlée | Exposition de données de consommation, incidents ou fraude |
| Données incidents | Accès non autorisé | Divulgation d’informations sur l’état du réseau |
| Données fraude | Mauvaise diffusion ou mauvaise interprétation | Suspicion injustifiée, atteinte à la relation client |
| KPI globaux | Manipulation ou erreur de données | Mauvaise décision métier ou financière |
| Exports Power BI | Export Excel/CSV non maîtrisé | Fuite de données hors du périmètre autorisé |

## Mesures de sécurité recommandées

J'ai rélévé quelques mesures  pour sécuriser le dashboard et les données analytiques :

- limiter l’accès au dashboard aux utilisateurs autorisés ;
- appliquer une authentification forte via Microsoft 365 / MFA ;
- mettre en place une gestion des droits par rôle : direction, exploitation réseau, finance, relation client ;
- privilégier les données agrégées plutôt que les données individuelles ;
- limiter les exports Excel/CSV ;
- éviter le partage public du rapport ;
- utiliser un espace Power BI contrôlé ;
- journaliser les accès au dashboard ;
- réaliser une revue régulière des habilitations ;
- conserver les fichiers sources uniquement dans un espace sécurisé.

## Recommandations RGPD

Les données de consommation et de fraude peuvent révéler des informations sensibles sur les clients.  
Il est donc recommandé de :

- limiter les données affichées au strict nécessaire ;
- anonymiser ou agréger les données lorsque le détail individuel n’est pas utile ;
- réserver les données détaillées aux profils habilités ;
- documenter les finalités du traitement ;
- limiter la durée de conservation des exports ;
- prévoir une validation humaine avant toute décision liée à une suspicion de fraude.

## Lien avec les scénarios de risque

Cette analyse ajoute un scénario spécifique au volet cybersécurité :

**S6 – Export non autorisé depuis Power BI** : un utilisateur interne ou un compte compromis exporte des données de consommation, d’incidents ou de fraude depuis le dashboard Power BI, puis les diffuse hors du périmètre autorisé.

Mesures associées :

- restriction des exports ;
- journalisation des téléchargements ;
- revue des accès ;
- MFA ;
- sensibilisation des utilisateurs ;
- contrôle des partages externes.

## Conclusion

L’intégration du volet Data Analyst dans l’analyse cybersécurité permet de mieux protéger les données produites et restituées dans Power BI.  
La sécurité ne doit pas seulement porter sur les serveurs et les accès techniques, mais aussi sur les tableaux de bord, les fichiers préparés, les exports et les usages métiers.
