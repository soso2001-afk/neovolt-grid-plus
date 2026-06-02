# Jour 1 – Cadrage du volet cybersécurité

## Objectif

L’objectif du volet cybersécurité est d’identifier les risques pesant sur l’infrastructure Néovolt Grid+, de sécuriser les composants critiques et de proposer une démarche de détection, de réponse et de conformité adaptée à une infrastructure énergétique critique.

## Périmètre retenu

Le périmètre cyber que j'ai retenu couvre les éléments suivants :

- SCADA / supervision réseau électrique ;
- plateforme data ;
- portail client ;
- API espace client ;
- VPN ;
- Active Directory ;
- bases clients et relevés compteurs ;
- serveur BI ;
- compteurs communicants.

j'ai retenu ces actifs car ils participent à la continuité du service énergétique, au traitement de données sensibles, à l’exposition du SI vers Internet ou la DMZ.

## Méthodologie retenue

En m’appuyant sur l’état du SI existant de Néovolt Grid+, j’ai défini la méthodologie suivante :

- analyse de risques simplifiée inspirée d’EBIOS Risk Manager ;
- analyse des journaux de sécurité dans une logique SOC/SIEM ;
- recommandations DevSecOps : accès, secrets, journalisation, segmentation, chiffrement ;
- prise en compte des exigences RGPD/NIS2 et des besoins de continuité de service.

## Données utilisées

Les fichiers identifiés pour le volet cybersécurité sont :

- `actifs_si.csv` : cartographie des actifs et analyse de risques ;
- `journaux_securite.csv` : analyse SOC/SIEM ;
- `incidents_reseau.csv` : continuité d’activité, PCA/PRA ;
- `cas_fraude_confirmes.csv` : scénarios de fraude et d’anomalies ;
- `compteurs.csv` : risques liés aux compteurs communicants.
