# Jour 3 – Analyse des journaux de sécurité et sécurisation du dashboard Power BI

## Objectif de la journée

Pour ce troisième jour, j’ai poursuivi le travail cybersécurité en commençant à relier l’analyse de risques faite précédemment avec des éléments plus concrets.

Objectifs du jour :

* commencer l’analyse des journaux de sécurité dans une logique SOC/SIEM ;
* prendre en compte les fichiers produits par le volet Data Analyst, notamment le dashboard Power BI et les fichiers CSV préparés.

Cette étape permet de montrer que la sécurité ne concerne pas seulement les serveurs ou les accès techniques, mais aussi les données exploitées, les tableaux de bord, les exports et les usages métiers.

## Analyse des journaux de sécurité

Je me suis appuyé sur le fichier `journaux_securite.csv`, qui contient les événements de sécurité du SI Néovolt.

Les événements les plus importants à surveiller sont :

* les connexions échouées ;
* les connexions réussies inhabituelles ;
* les accès refusés ;
* les modifications de configuration ;
* les exports de données ;
* les activités sur les systèmes sensibles comme le VPN, l’Active Directory, la plateforme data, l’API, le portail client et le SCADA.

L’idée est de repérer les comportements qui peuvent correspondre à un début d’incident ou à une tentative d’attaque.

## Lien avec les scénarios d’attaque

Les journaux de sécurité permettent de faire le lien avec les scénarios d’attaque identifiés au jour 2.

| Scénario                            | Événements à surveiller                                                                 |
| ----------------------------------- | --------------------------------------------------------------------------------------- |
| Compromission VPN                   | Connexions échouées répétées, connexion réussie depuis une adresse externe inhabituelle |
| Exploitation de l’API espace client | Accès refusés répétés ou accès inhabituels à l’API                                      |
| Compromission Active Directory      | Échecs de connexion, modification de droits, activité sur comptes à privilèges          |
| Altération des données              | Modifications de configuration, accès inhabituels à la plateforme data                  |
| Ransomware                          | Activité anormale sur les serveurs critiques et les sauvegardes                         |

## Premières règles de détection SOC/SIEM

À partir de ces observations, j’ai commencé à proposer des règles de détection simples mais adaptées au contexte Néovolt.

| Règle                                       | Description                                                                                                  | Criticité |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | --------- |
| R1 – Échecs de connexion répétés            | Alerte lorsqu’un même compte génère plusieurs échecs de connexion en peu de temps                            | Élevée    |
| R2 – Connexion VPN inhabituelle             | Alerte lorsqu’une connexion VPN provient d’une adresse IP externe ou inhabituelle                            | Critique  |
| R3 – Modification de configuration sensible | Alerte sur toute modification de configuration concernant le SCADA, la plateforme data ou l’Active Directory | Critique  |
| R4 – Export de données                      | Alerte en cas d’export de données depuis la plateforme data ou le BI, surtout hors horaires habituels        | Élevée    |
| R5 – Accès refusés répétés                  | Alerte si plusieurs accès refusés sont observés sur un système critique                                      | Élevée    |

Ces règles restent volontairement simples, car le but est de proposer une base réaliste pour un prototype et non un SOC complet de production.

## Prise en compte du volet Data Analyst

Le volet Data Analyst a produit plusieurs éléments utiles au projet, notamment :

* des notebooks d’exploration et d’analyse ;
* des fichiers CSV préparés pour Power BI ;
* un dashboard Power BI ;
* des données préparées sur les incidents réseau ;
* des données préparées sur les cas de fraude confirmés ;
* des indicateurs globaux de consommation.

Ces éléments doivent être intégrés à l’analyse cybersécurité, car ils manipulent ou restituent des informations sensibles pour Néovolt.

## Risques liés au dashboard Power BI

| Élément concerné      | Risque identifié                              | Impact possible                                            |
| --------------------- | --------------------------------------------- | ---------------------------------------------------------- |
| Dashboard Power BI    | Partage non maîtrisé du rapport               | Fuite d’informations métier ou sensibles                   |
| Fichiers CSV préparés | Stockage ou diffusion non contrôlée           | Exposition de données de consommation, incidents ou fraude |
| Données incidents     | Accès non autorisé                            | Divulgation d’informations sur l’état du réseau            |
| Données fraude        | Mauvaise diffusion ou mauvaise interprétation | Suspicion injustifiée ou impact sur la relation client     |
| KPI globaux           | Données erronées ou manipulées                | Mauvaise décision métier ou financière                     |
| Exports Power BI      | Export Excel/CSV non contrôlé                 | Fuite de données hors du périmètre autorisé                |

## Mesures de sécurité proposées

Pour limiter ces risques, je propose les mesures suivantes :

* limiter l’accès au dashboard aux utilisateurs réellement concernés ;
* appliquer une authentification forte via Microsoft 365 / MFA ;
* gérer les droits par rôle : direction, exploitation réseau, finance, relation client ;
* privilégier les données agrégées plutôt que les données individuelles ;
* limiter les exports Excel/CSV ;
* éviter tout partage public du rapport ;
* utiliser un espace Power BI contrôlé ;
* journaliser les accès au dashboard ;
* revoir régulièrement les habilitations ;
* stocker les fichiers sources dans un espace sécurisé.

## Point RGPD

Les données de consommation et les données liées à la fraude peuvent révéler des informations sensibles sur les clients. Il est donc nécessaire de limiter les données affichées au strict nécessaire.

Lorsque le détail individuel n’est pas utile, les données doivent être agrégées par zone, période, type de client ou indicateur global. Les données détaillées doivent rester accessibles uniquement aux personnes habilitées.

Une attention particulière doit aussi être portée aux exports, car un fichier Excel ou CSV téléchargé peut sortir facilement du périmètre contrôlé.

## Scénario ajouté

À la suite de l’analyse du volet Data Analyst, j’ajoute un scénario de risque supplémentaire.

**S6 – Export non autorisé depuis Power BI**

Un utilisateur interne ou un compte compromis exporte des données de consommation, d’incidents ou de fraude depuis le dashboard Power BI, puis les diffuse en dehors du périmètre autorisé.

Les mesures associées sont :

* restriction des exports ;
* journalisation des téléchargements ;
* revue régulière des accès ;
* MFA obligatoire ;
* sensibilisation des utilisateurs ;
* contrôle des partages externes.

## Conclusion

Le travail du jour 3 permet de faire le lien entre les risques identifiés, les journaux de sécurité et les productions du volet Data Analyst.

Cette analyse montre que la cybersécurité doit couvrir à la fois les accès techniques, les systèmes critiques, les fichiers préparés, les tableaux de bord et les exports. Cela permet de mieux protéger les données exploitées dans Néovolt Grid+ et de rendre le prototype plus cohérent avec les exigences de sécurité, de conformité et de continuité.
