# PCA/PRA du projet Néovolt Grid+

## Objectif

Dans cette partie, je présente les premiers éléments de continuité et de reprise d’activité pour le volet cybersécurité du projet Néovolt Grid+.

L’idée est de prévoir ce que Néovolt doit faire si un incident cyber perturbe la plateforme data, les accès, les sauvegardes, le dashboard ou un système critique.

Comme Néovolt est une infrastructure énergétique critique, l’objectif n’est pas seulement de protéger les données. Il faut aussi être capable de continuer l’activité ou de reprendre rapidement après un incident.

## La différence entre PCA et PRA

Le PCA, ou Plan de Continuité d’Activité, sert à maintenir un minimum de service pendant un incident.

Le PRA, ou Plan de Reprise d’Activité, sert à redémarrer les services après un incident.

Dans le cas de Néovolt :

- le PCA permettrait de continuer à suivre les informations essentielles même en mode dégradé ;
- le PRA permettrait de restaurer les systèmes, les données et les accès après une cyberattaque ou une panne importante.

## Les ctifs prioritaires pour la continuité

Tous les actifs ne doivent pas être traités au même niveau. Pour Néovolt, certains éléments sont prioritaires car ils ont un impact direct sur la continuité du service ou sur les données sensibles.

| Actif | Pourquoi il est important | Priorité |
|---|---|---|
| SCADA / supervision réseau | Il est lié à la continuité du réseau énergétique | Critique |
| Passerelle de télérelève | Elle permet la remontée des données des compteurs | Critique |
| Plateforme data | Elle centralise et traite les données de consommation | Critique |
| Bases clients et relevés | Elles contiennent les données nécessaires à l’analyse et à la facturation | Critique |
| Active Directory | Il gère les identités et les droits d’accès | Critique |
| VPN | Il permet les accès distants au SI | Élevée |
| Serveur BI / Power BI | Il sert aux tableaux de bord et à la prise de décision | Élevée |
| Sauvegardes | Elles permettent de restaurer les données et services après incident | Critique |

## Les Scénarios à prévoir

Les principaux scénarios à prendre en compte sont les suivants :

| Scénario | Impact possible | Réponse attendue |
|---|---|---|
| Ransomware sur un serveur interne | Indisponibilité de la plateforme ou des données | Isoler, analyser, restaurer depuis une sauvegarde saine |
| Compromission Active Directory | Perte de maîtrise des accès | Désactiver les comptes compromis, revoir les groupes, réinitialiser les accès |
| Compromission VPN | Accès non autorisé au SI interne | Couper la session, bloquer le compte, vérifier les actions réalisées |
| Fuite de données depuis Power BI | Risque RGPD et perte de confiance | Identifier l’export, bloquer l’accès, alerter RSSI/DPO |
| Incident sur la plateforme data | Données indisponibles ou altérées | Passer en mode dégradé, restaurer les données, vérifier leur intégrité |
| Modification non autorisée sur SCADA ou télérelève | Risque sur la supervision ou les flux compteurs | Escalader à l’exploitation réseau et au RSSI, ne pas intervenir sans validation |

## les mesures de continuité proposées

Pour limiter l’impact d’un incident, Néovolt doit prévoir plusieurs mesures de continuité.

Les principales mesures sont :

- conserver des sauvegardes régulières des bases et fichiers critiques ;
- tester les restaurations, pas seulement créer des sauvegardes ;
- isoler les environnements critiques comme le SCADA ;
- prévoir un mode dégradé si le dashboard ou la plateforme data ne sont plus disponibles ;
- documenter les procédures de reprise ;
- identifier les personnes à contacter en cas d’incident ;
- conserver les journaux utiles à l’analyse.

## Sauvegardes

Les sauvegardes sont un point central du PRA.

Elles doivent permettre de restaurer les données de consommation, les bases clients, les fichiers de configuration et les éléments utiles au dashboard.

Les recommandations sont :

- sauvegarder régulièrement les bases critiques ;
- protéger les sauvegardes contre la modification ou la suppression ;
- limiter les accès au serveur de sauvegarde ;
- tester les restaurations ;
- conserver au moins une copie isolée ou difficilement modifiable.

Ce point est important car un ransomware peut aussi viser les sauvegardes. Si les sauvegardes sont compromises, la reprise devient beaucoup plus difficile.

## Mode dégradé

En cas d’incident, tout ne pourra pas forcément être restauré immédiatement.

Il faut donc prévoir un mode dégradé.

Par exemple :

- si Power BI est indisponible, utiliser temporairement des exports validés et contrôlés ;
- si la plateforme data est indisponible, conserver les dernières données fiables disponibles ;
- si un compte est compromis, suspendre l’accès et utiliser un compte de secours encadré ;
- si un incident touche la télérelève, maintenir les procédures métier minimales le temps de l’analyse.

L’objectif du mode dégradé n’est pas d’avoir toutes les fonctionnalités, mais de garder les fonctions essentielles.

## les Rôles en cas d’incident

Pour éviter la confusion pendant un incident, les rôles doivent être clairs.

| Rôle | Responsabilité |
|---|---|
| RSSI | Piloter la réponse cyber et valider les mesures de sécurité |
| DSI | Coordonner les équipes techniques |
| DPO | Intervenir si des données personnelles sont concernées |
| Exploitation réseau | Gérer les impacts sur le SCADA et le réseau énergétique |
| Data / BI | Vérifier l’intégrité des données et tableaux de bord |
| Support IT | Aider à la gestion des comptes et postes concernés |
| Direction | Décider en cas d’impact majeur ou de communication externe |

## Priorités de reprise

La reprise doit se faire dans un ordre logique.

| Priorité | Élément à restaurer ou sécuriser | Justification |
|---|---|---|
| 1 | Identités et accès critiques | Sans contrôle des accès, la reprise n’est pas fiable |
| 2 | Sauvegardes et données critiques | Nécessaires pour restaurer les services |
| 3 | Plateforme data et bases principales | Nécessaires pour les analyses et décisions |
| 4 | BI / Power BI | Utile pour le pilotage métier |
| 5 | Services secondaires | À restaurer après les services prioritaires |

Le SCADA doit rester traité avec une procédure spécifique, car il ne doit pas être manipulé sans validation de l’exploitation réseau et du RSSI.

## Points de vigilance

Plusieurs points doivent être surveillés :

- ne pas restaurer un système sans vérifier qu’il est sain ;
- éviter de reconnecter trop vite une machine compromise ;
- conserver les preuves avant nettoyage ;
- vérifier les comptes utilisés pendant l’incident ;
- informer le DPO si des données personnelles sont concernées ;
- documenter toutes les actions réalisées.

## Conclusion

Le PCA/PRA cyber permet de préparer la réaction de Néovolt face à un incident important.

Dans ce projet, les priorités sont la protection des accès, la disponibilité des données, l’intégrité des sauvegardes, l’isolation du SCADA et la capacité à reprendre rapidement les services nécessaires.

Cette partie complète l’analyse de risques et le runbook incident en montrant comment Néovolt peut limiter l’impact d’une cyberattaque et reprendre ses activités de manière maîtrisée.
