# Conformité RGPD et NIS2 – Volet cybersécurité Néovolt

## Objectif

Dans cette partie, je prends en compte les aspects de conformité liés au projet Néovolt Grid+.

Comme le projet utilise des données de consommation, des données clients, des informations sur les incidents réseau et des cas de fraude, il est important de ne pas traiter ces données comme de simples fichiers techniques.

Ces données peuvent avoir un impact sur les clients, sur l’entreprise et sur la continuité du service. C’est pour cela que j’ai intégré les points liés au RGPD, à la sécurité des infrastructures critiques et aux exigences de type NIS2.

L’objectif n’est pas de faire une analyse juridique complète, mais de montrer que le prototype est pensé avec des règles de sécurité et de conformité dès le départ.

## Données personnelles et RGPD

Les données de consommation doivent être traitées avec prudence, car elles peuvent donner des informations sur les habitudes d’un client.

Par exemple, une consommation très basse ou très haute à certains moments peut donner des indications sur la présence, l’absence ou les usages d’un foyer. Même si le projet est technique, il faut donc limiter ce qu’on affiche, ce qu’on exporte et qui peut y accéder.

Dans le cadre de Néovolt Grid+, il faut surtout faire attention à trois points :

* ne pas afficher plus de données que nécessaire ;
* limiter les accès aux personnes qui en ont réellement besoin ;
* éviter les exports non contrôlés, notamment depuis Power BI ou les fichiers CSV préparés.

## Minimisation des données

Pour les tableaux de bord, il n’est pas toujours utile d’afficher le détail client par client.

Dans beaucoup de cas, une vision par zone, par période, par type de client ou par indicateur global suffit pour aider à la décision.

Les mesures que je recommande sont :

* privilégier les données agrégées dans les dashboards ;
* éviter d’afficher inutilement des identifiants clients ou compteurs ;
* réserver les données détaillées aux personnes habilitées ;
* documenter les données réellement utilisées dans le prototype.

Cette approche permet de réduire le risque de fuite tout en gardant une analyse utile pour les métiers.

## Gestion des accès

Tous les utilisateurs ne doivent pas avoir les mêmes droits.

Un décideur financier, un analyste data, une personne du service client ou un administrateur technique n’ont pas les mêmes besoins. Les accès doivent donc être adaptés au rôle de chacun.

Les mesures proposées sont :

* définir des rôles d’accès ;
* limiter les droits selon le profil utilisateur ;
* activer l’authentification forte pour les accès sensibles ;
* revoir régulièrement les comptes ;
* désactiver les comptes inutilisés ;
* tracer les accès aux données sensibles.

Cette partie est importante car une mauvaise gestion des accès peut entraîner une fuite de données ou une utilisation non prévue du dashboard.

## Exports et conservation des fichiers

Les exports représentent un vrai point de vigilance.

Même si les données sont bien sécurisées dans Power BI ou dans la plateforme data, un fichier exporté en Excel ou CSV peut ensuite être envoyé, copié ou stocké sans contrôle.

Je recommande donc de :

* limiter les exports aux profils autorisés ;
* éviter les exports détaillés quand une donnée agrégée suffit ;
* conserver les fichiers préparés dans un espace sécurisé ;
* supprimer les fichiers temporaires inutiles ;
* éviter les copies locales non maîtrisées ;
* journaliser les téléchargements sensibles.

Cela permet de garder la maîtrise des données même après leur utilisation dans le dashboard.

## Détection de fraude et intervention humaine

La détection de fraude est un sujet sensible.

Un indicateur ou un modèle peut signaler une anomalie, mais il ne doit pas être utilisé seul pour accuser un client. Une erreur d’analyse pourrait créer une suspicion injustifiée et détériorer la relation client.

Dans le cadre du projet, les alertes doivent donc rester une aide à la décision.

Les mesures proposées sont :

* prévoir une validation humaine avant toute décision défavorable ;
* documenter les critères utilisés pour signaler une anomalie ;
* éviter les décisions automatiques non expliquées ;
* garder une possibilité de revue ou de contestation ;
* rester attentif aux biais possibles.

Cette approche permet de protéger à la fois Néovolt et les clients.

## Traçabilité

La traçabilité est nécessaire pour comprendre ce qui se passe dans le système.

Il faut pouvoir savoir qui s’est connecté, qui a consulté des données, qui a exporté un fichier ou qui a modifié une configuration.

Dans le contexte Néovolt, les éléments à tracer en priorité sont :

* les connexions réussies et échouées ;
* les accès refusés ;
* les exports depuis Power BI ou la plateforme data ;
* les accès aux données sensibles ;
* les modifications de configuration ;
* les changements de droits.

Ces journaux serviront aussi à alimenter les règles SOC/SIEM définies dans la partie détection.

## Prise en compte de NIS2

Néovolt est présenté comme une infrastructure critique. Cela veut dire qu’un incident cyber ne doit pas être vu seulement comme un problème informatique.

Une attaque ou une panne peut avoir des conséquences sur la continuité du service, la supervision du réseau, la relation client et la confiance des usagers.

Dans cette logique, il faut donc prévoir :

* une analyse des risques ;
* une surveillance des systèmes sensibles ;
* une procédure de réaction en cas d’incident ;
* une capacité de reprise après incident ;
* une notification rapide en cas d’incident majeur ;
* une attention particulière aux prestataires et aux comptes à privilèges.

## Continuité de service

La continuité du service est un point central pour Néovolt.

Les actifs comme le SCADA, la passerelle de télérelève, la plateforme data, l’Active Directory, le VPN et les sauvegardes doivent être protégés en priorité.

Les mesures proposées sont :

* isoler les systèmes critiques ;
* limiter les accès au SCADA ;
* tester régulièrement les sauvegardes ;
* prévoir un mode dégradé ;
* documenter les procédures de reprise ;
* éviter les dépendances directes non maîtrisées entre la plateforme data et l’environnement SCADA.

L’objectif est de réduire l’impact d’un incident et de permettre à Néovolt de continuer ou reprendre ses activités rapidement.

## Sécurité des prestataires

Le SI existant mentionne des accès hétérogènes et des comptes prestataires avec des droits élevés. C’est un point de vigilance important.

Les prestataires peuvent être nécessaires, mais leurs accès doivent être encadrés.

Les mesures proposées sont :

* limiter les droits prestataires au strict nécessaire ;
* donner des accès temporaires ;
* tracer les actions réalisées ;
* désactiver les accès après intervention ;
* revoir régulièrement les comptes externes.

Cela permet de réduire le risque d’un accès oublié ou trop permissif.

## Synthèse

| Sujet                   | Risque principal                   | Mesure proposée                           |
| ----------------------- | ---------------------------------- | ----------------------------------------- |
| Données de consommation | Atteinte à la vie privée           | Agrégation, minimisation, accès limité    |
| Dashboard Power BI      | Partage ou export non maîtrisé     | MFA, RBAC, restriction des exports        |
| Détection de fraude     | Suspicion injustifiée              | Validation humaine et critères documentés |
| Journaux de sécurité    | Manque de preuve en cas d’incident | Journalisation et conservation maîtrisée  |
| SCADA                   | Impact sur un service essentiel    | Isolation, segmentation, accès strict     |
| Prestataires            | Droits trop larges ou oubliés      | Accès temporaires et revue régulière      |
| Incident majeur         | Réaction trop lente                | Procédure d’escalade et notification      |

## Conclusion

La conformité RGPD et NIS2 doit être intégrée dès la conception du projet Néovolt Grid+.

Pour le RGPD, l’objectif est de limiter l’exposition des données personnelles, de maîtriser les accès et de contrôler les exports. Pour NIS2, l’enjeu est surtout de gérer les risques, assurer la continuité du service et réagir rapidement en cas d’incident.

Cette partie montre que le prototype ne se limite pas à produire des analyses ou des tableaux de bord : il doit aussi respecter les exigences de sécurité, de confidentialité et de continuité attendues pour une infrastructure énergétique critique.
