# Jour 2 – Cartographie des actifs et analyse de risques initiale

## Objectif

L’objectif du jour 2 est de passer du cadrage à une première analyse concrète des risques cybersécurité. Le travail porte sur l’identification des actifs critiques, leur exposition, les données sensibles traitées et les premiers scénarios de risque.

## Actifs critiques retenus

Pour démarrer l’analyse de risques, j’ai retenu les actifs les plus sensibles du SI Néovolt. Le choix s’est fait en fonction de leur criticité, de leur exposition réseau et des données qu’ils traitent. L’objectif est de concentrer le travail cyber sur les éléments qui pourraient avoir le plus d’impact en cas d’attaque : fuite de données, fraude, compromission d’accès ou interruption du service énergétique.

| ID | Actif | Criticité | Exposition | Données sensibles | Risque principal |
|---|---|---|---|---|---|
| SRV-WEB-01 | Portail client front | Critique | Internet | Oui | Attaque web, vol de comptes, fuite de données |
| SRV-WEB-02 | API espace client | Critique | DMZ | Oui | Exploitation API, accès non autorisé aux données |
| SRV-APP-10 | Plateforme data | Critique | Interne | Oui | Altération ou exfiltration des données de consommation |
| SRV-DB-01 | Base clients et facturation | Critique | Interne | Oui | Fuite de données personnelles et impact RGPD |
| SRV-DB-02 | Base relevés compteurs | Critique | Interne | Oui | Manipulation des consommations, fraude, erreur d’analyse |
| SCADA-01 | Supervision réseau électrique | Critique | Interne | Non | Interruption du service énergétique |
| SCADA-02 | Passerelle télérelève compteurs | Critique | DMZ | Oui | Compromission des flux compteurs |
| AD-01 | Active Directory | Critique | Interne | Oui | Élévation de privilèges, compromission globale |
| VPN-01 | Accès distant | Élevée | Internet | Oui | Compromission d’identifiants et accès non autorisé |
| SRV-BI-01 | Reporting BI | Élevée | Interne | Oui | Fuite ou manipulation des tableaux de bord |

## Analyse de risques initiale

Après avoir identifié les actifs critiques, j’ai commencé une première analyse de risques. L’objectif est de relier chaque actif à une menace concrète, à son exposition et à l’impact possible pour Néovolt. Cette première version permet de prioriser les mesures de sécurité à traiter en priorité.

| Actif | Menace | Vulnérabilité / exposition | Impact | Criticité | Mesure proposée |
|---|---|---|---|---|---|
| SCADA-01 / SCADA-02 | Intrusion ou mauvaise segmentation | SCADA isolé mais critique ; passerelle en DMZ | Interruption du réseau, perte de supervision | Critique | Segmentation stricte, accès nominatif, journalisation renforcée, pas de connexion directe non justifiée |
| VPN-01 | Compromission d’un compte distant | Accès Internet, risque de mot de passe compromis | Accès non autorisé au SI interne | Critique | MFA obligatoire, filtrage IP, détection des échecs répétés, revue des comptes |
| AD-01 | Élévation de privilèges | Comptes à privilèges, prestataires, droits hétérogènes | Prise de contrôle du SI | Critique | PAM, comptes admin séparés, durcissement GPO, revue des groupes |
| SRV-WEB-02 API | Exploitation API | API en DMZ manipulant des données sensibles | Fuite de données clients et consommation | Élevée | Authentification forte, limitation de débit, logs API, tests OWASP |
| SRV-APP-10 / SRV-DB-02 | Altération des données | Plateforme data et relevés compteurs sensibles | Décisions métier faussées, fraude non détectée | Élevée | RBAC, intégrité des flux, traçabilité, contrôle des exports |
| SRV-SAUV-01 | Ransomware ciblant les sauvegardes | Actif essentiel pour reprise | Perte de capacité de restauration | Critique | Sauvegardes immuables, tests de restauration, segmentation, accès restreint |

## Scénarios d’attaque retenus

- S1 – Compromission VPN : un attaquant tente de se connecter depuis une adresse externe puis utilise un compte valide pour accéder au SI interne.
- S2 – Exploitation de l’API espace client : une vulnérabilité ou une mauvaise gestion des droits permettrait d’accéder à des données de consommation.
- S3 – Compromission Active Directory : un compte prestataire ou administrateur est utilisé pour élever les privilèges et se déplacer latéralement.
- S4 – Altération des relevés compteurs : manipulation ou injection de données fausses dans la chaîne de télérelève ou la plateforme data.
- S5 – Ransomware sur serveurs critiques : chiffrement de serveurs internes avec impact sur la disponibilité et la reprise d’activité.
