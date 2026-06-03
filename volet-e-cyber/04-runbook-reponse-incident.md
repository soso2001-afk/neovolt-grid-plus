# Jour 3 – Runbook de réponse à incident cybersécurité

## Objectif

Ce fichier complète l’analyse des journaux de sécurité et les règles SOC/SIEM définies précédemment.

L’objectif est de prévoir les premières actions à mener lorsqu’une alerte est détectée.  
Dans le contexte de Néovolt, il est important de réagir rapidement, car l’entreprise manipule des données sensibles et exploite une infrastructure énergétique critique.

Ce runbook ne remplace pas une procédure complète de gestion de crise, mais il donne une base claire pour traiter les incidents prioritaires identifiés dans le projet.

---

## Principes généraux de réponse

En cas d’alerte ou d’incident, les actions doivent suivre une logique simple :

1. **Qualifier l’alerte** : vérifier si l’événement est réellement suspect.
2. **Limiter l’impact** : bloquer ou isoler ce qui peut aggraver l’incident.
3. **Préserver les traces** : conserver les journaux et éléments utiles à l’analyse.
4. **Escalader** : prévenir les bons interlocuteurs, notamment le RSSI, la DSI ou le DPO selon le cas.
5. **Corriger** : appliquer les mesures de remédiation.
6. **Capitaliser** : documenter l’incident et améliorer les règles de détection.

---

## Incident 1 – Compromission d’un compte VPN

### Déclencheur possible

Une alerte est déclenchée lorsqu’un compte génère plusieurs échecs de connexion, puis une connexion réussie depuis une adresse IP inhabituelle ou externe.

### Risques associés

- Accès non autorisé au SI interne.
- Rebond vers Active Directory ou plateforme data.
- Vol ou modification de données.
- Début d’une compromission plus large.

### Actions immédiates

- Identifier le compte concerné.
- Vérifier l’adresse IP source et l’horaire de connexion.
- Couper la session VPN si elle est toujours active.
- Désactiver temporairement le compte si le doute est sérieux.
- Prévenir le RSSI ou l’équipe sécurité.
- Conserver les journaux VPN et Active Directory.

### Mesures correctives

- Réinitialiser le mot de passe du compte.
- Vérifier si le MFA était activé.
- Revoir les droits du compte.
- Contrôler les actions réalisées après la connexion.
- Ajouter l’adresse IP source à une liste de surveillance si nécessaire.

---

## Incident 2 – Activité suspecte sur Active Directory

### Déclencheur possible

Une alerte apparaît après une modification de groupe, un changement de droits ou une activité inhabituelle sur un compte à privilèges.

### Risques associés

- Élévation de privilèges.
- Création de comptes non autorisés.
- Déplacement latéral dans le SI.
- Prise de contrôle de systèmes critiques.

### Actions immédiates

- Identifier le compte ayant réalisé l’action.
- Vérifier si la modification était prévue ou autorisée.
- Contrôler les groupes administrateurs.
- Désactiver le compte si l’activité semble malveillante.
- Préserver les journaux Active Directory.

### Mesures correctives

- Revenir sur les modifications non autorisées.
- Réinitialiser les mots de passe des comptes concernés.
- Revoir les comptes à privilèges.
- Séparer les comptes administrateurs des comptes standards.
- Mettre en place ou renforcer le principe du moindre privilège.

---

## Incident 3 – Export non autorisé de données depuis Power BI ou la plateforme data

### Déclencheur possible

Une alerte est déclenchée lorsqu’un export de données est réalisé depuis Power BI, le serveur BI ou la plateforme data, notamment hors horaires habituels ou par un utilisateur non prévu.

### Risques associés

- Fuite de données de consommation.
- Exposition d’informations liées aux incidents ou aux fraudes.
- Non-conformité RGPD.
- Atteinte à la confiance des clients.

### Actions immédiates

- Identifier l’utilisateur ayant réalisé l’export.
- Identifier le type de données exportées.
- Vérifier si l’export correspond à un besoin métier légitime.
- Bloquer temporairement l’accès si l’action semble injustifiée.
- Prévenir le responsable métier, le RSSI et le DPO si des données personnelles sont concernées.

### Mesures correctives

- Limiter les droits d’export.
- Revoir les habilitations Power BI.
- Journaliser systématiquement les téléchargements.
- Privilégier les données agrégées.
- Sensibiliser les utilisateurs aux risques liés aux exports.

---

## Incident 4 – Exploitation ou tentative d’accès non autorisé à l’API espace client

### Déclencheur possible

Plusieurs accès refusés, erreurs répétées ou requêtes inhabituelles sont observés sur l’API espace client.

### Risques associés

- Accès non autorisé aux données clients.
- Fuite de données de consommation.
- Saturation ou abus de l’API.
- Exploitation d’une vulnérabilité applicative.

### Actions immédiates

- Identifier l’adresse IP source.
- Vérifier les comptes ou jetons utilisés.
- Contrôler les routes API concernées.
- Bloquer temporairement l’adresse IP si le comportement est anormal.
- Préserver les logs applicatifs et réseau.

### Mesures correctives

- Mettre en place une limitation de débit.
- Vérifier l’authentification et les autorisations.
- Tester l’API avec une approche OWASP.
- Renforcer les contrôles d’accès.
- Ajouter une surveillance spécifique sur les routes sensibles.

---

## Incident 5 – Suspicion de ransomware sur un serveur critique

### Déclencheur possible

Une activité inhabituelle est observée sur un serveur critique ou sur le serveur de sauvegarde : accès massif, suppression, modification anormale de fichiers ou comportement suspect.

### Risques associés

- Chiffrement de données.
- Indisponibilité de la plateforme data.
- Perte de capacité de restauration.
- Impact sur la continuité d’activité.

### Actions immédiates

- Isoler le serveur concerné du réseau.
- Ne pas éteindre brutalement la machine si une analyse doit être réalisée.
- Prévenir immédiatement le RSSI et la DSI.
- Vérifier l’état des sauvegardes.
- Bloquer les comptes potentiellement compromis.
- Conserver les journaux système et sécurité.

### Mesures correctives

- Restaurer depuis une sauvegarde saine si nécessaire.
- Vérifier l’intégrité des sauvegardes.
- Corriger le point d’entrée identifié.
- Renforcer la segmentation réseau.
- Tester régulièrement la restauration.

---

## Incident 6 – Modification non autorisée sur SCADA ou passerelle de télérelève

### Déclencheur possible

Une modification de configuration est détectée sur un composant lié au SCADA ou à la passerelle de télérelève.

### Risques associés

- Perte de supervision.
- Altération des flux de télérelève.
- Impact sur la continuité du service énergétique.
- Risque sur une infrastructure critique.

### Actions immédiates

- Ne pas intervenir directement sur le SCADA sans validation.
- Vérifier si la modification était planifiée.
- Prévenir le RSSI et l’équipe exploitation réseau.
- Identifier le compte et l’origine de l’action.
- Conserver les journaux de configuration et d’accès.

### Mesures correctives

- Revenir à la configuration validée si nécessaire.
- Renforcer la séparation entre SI bureautique, plateforme data et environnement SCADA.
- Limiter les accès aux seuls comptes nominativement autorisés.
- Journaliser toutes les modifications.
- Mettre en place une validation préalable pour toute modification sensible.

---

## Synthèse des priorités

| Priorité | Incident | Pourquoi c’est prioritaire |
|---|---|---|
| 1 | Compromission Active Directory | Risque de prise de contrôle globale du SI |
| 2 | Compromission VPN | Point d’entrée distant vers le SI interne |
| 3 | Incident SCADA / télérelève | Impact possible sur un service essentiel |
| 4 | Ransomware | Risque fort sur la disponibilité et la reprise |
| 5 | Export non autorisé | Risque RGPD et fuite de données sensibles |
| 6 | Exploitation API | Risque d’accès non autorisé aux données clients |

---

## Conclusion

Ce runbook permet de structurer les premières réactions face aux incidents les plus probables dans le contexte Néovolt.

Il complète les règles SOC/SIEM en précisant quoi faire lorsqu’une alerte est déclenchée.  
L’objectif est de réduire le temps de réaction, limiter l’impact des incidents et préserver les preuves nécessaires à l’analyse.
