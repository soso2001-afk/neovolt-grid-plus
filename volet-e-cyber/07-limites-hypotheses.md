# Limites et hypothèses – Volet cybersécurité Néovolt

## Objectif

Dans cette partie, je précise les limites de mon travail et les hypothèses que j’ai retenues pour avancer.

Comme le projet Néovolt Grid+ se fait sur un sprint court, je ne peux pas prétendre réaliser un audit complet comme dans une mission de plusieurs semaines. Le but est plutôt de proposer une analyse réaliste, basée sur les documents et les données fournies, tout en restant honnête sur ce qui reste à vérifier.

## Limites du travail réalisé

Le travail réalisé jusqu’ici s’appuie sur le dossier de cas, les fichiers fournis et les éléments produits par les autres volets, notamment le dashboard Power BI du volet Data Analyst.

Je n’ai pas accès à un vrai environnement de production Néovolt. Les recommandations proposées sont donc adaptées à un prototype et devront être validées avant une éventuelle mise en production.

Les principales limites sont les suivantes :

- je travaille à partir de fichiers fournis, pas depuis un SI réel ;
- les journaux de sécurité ne couvrent qu’une partie de l’activité ;
- les tests offensifs restent théoriques ou limités au périmètre autorisé ;
- certaines recommandations devront être adaptées aux choix techniques finaux du groupe ;
- les règles SOC/SIEM proposées sont une première base et devront être ajustées après test ;
- l’analyse du dashboard Power BI dépend encore des règles de partage et des profils utilisateurs retenus.

## Hypothèses retenues

Pour pouvoir avancer sans attendre tous les éléments des autres volets, j’ai posé quelques hypothèses.

| Hypothèse | Pourquoi je la retiens |
|---|---|
| Le SCADA reste isolé | C’est un environnement critique, il ne doit pas être exposé inutilement |
| La plateforme data ne se connecte pas directement au SCADA | Cela évite d’ajouter un risque sur un système sensible |
| Les dashboards Power BI utilisent surtout des données préparées ou agrégées | Cela limite l’exposition des données détaillées |
| Les fichiers CSV préparés peuvent contenir des informations sensibles | Ils concernent la consommation, les incidents, la fraude ou les KPI |
| Les accès doivent être gérés par rôle | Tous les utilisateurs n’ont pas les mêmes besoins |
| Les exports doivent être limités | Un fichier exporté peut sortir facilement du cadre sécurisé |
| Les alertes de fraude doivent être vérifiées par un humain | Une anomalie ne doit pas automatiquement devenir une accusation |

## Limites sur l’analyse des journaux

Les journaux de sécurité permettent de proposer une première logique de détection, mais ils ne suffisent pas à eux seuls pour conclure définitivement sur un incident.

Par exemple, plusieurs échecs de connexion peuvent indiquer une attaque, mais aussi une erreur utilisateur. Un export de données peut être suspect, mais il peut aussi correspondre à une action métier légitime.

C’est pour cela que les règles SOC/SIEM proposées doivent être vues comme une base à tester et à ajuster.

Pour aller plus loin, il faudrait disposer de plus d’informations comme :

- les horaires habituels des utilisateurs ;
- la criticité réelle des comptes ;
- les profils métiers associés aux utilisateurs ;
- les adresses IP connues ou autorisées ;
- les volumes habituels d’exports ;
- les journaux applicatifs plus détaillés.

## Limites sur Power BI et les fichiers préparés

Le volet Data Analyst a produit des fichiers CSV préparés et un dashboard Power BI. Ces éléments sont utiles pour le projet, mais ils créent aussi des risques liés au partage, aux exports et aux accès.

À ce stade, certaines informations restent à confirmer :

- qui aura accès au dashboard ;
- quelles données seront visibles dans le rapport ;
- si les exports Excel/CSV seront autorisés ;
- où seront stockés les fichiers préparés ;
- quelles règles Microsoft 365 ou Power BI seront appliquées ;
- si les données affichées sont totalement agrégées ou parfois détaillées.

En attendant ces réponses, je recommande une approche prudente : accès restreints, MFA, limitation des exports, données agrégées autant que possible et journalisation des consultations.

## Limites liées à l’architecture finale

Certaines recommandations dépendent encore de l’architecture technique finale du groupe.

Par exemple, si le groupe utilise une API, Docker, une base PostgreSQL ou un hébergement cloud, il faudra préciser certains points :

- sécurité de l’API ;
- gestion des secrets ;
- chiffrement des flux ;
- scans de dépendances ;
- segmentation réseau ;
- sauvegardes ;
- journalisation applicative.

Ces éléments seront donc à ajuster quand l’architecture finale sera stabilisée.

## Ce qui reste à compléter

| Élément | Ce qu’il faudra compléter |
|---|---|
| Audit du prototype | L’adapter à l’architecture réelle du groupe |
| Sécurité Power BI | Préciser les profils utilisateurs et les règles de partage |
| DevSecOps | Adapter les recommandations aux outils réellement utilisés |
| SOC/SIEM | Tester les règles sur les logs et ajuster les faux positifs |
| PCA/PRA | Préciser les dépendances entre les composants |
| Soutenance | Préparer les explications simples et défendables à l’oral |

## Conclusion

Ces limites ne sont pas un problème en soi. Elles montrent simplement que le travail est fait de manière progressive et réaliste.

À ce stade, j’ai déjà pu cadrer les principaux risques, proposer des mesures de sécurité, préparer une logique de détection, intégrer le dashboard Power BI dans l’analyse cyber et prendre en compte les exigences RGPD/NIS2.

La suite consistera surtout à ajuster cette analyse avec l’architecture finale et les choix techniques retenus par le groupe.
