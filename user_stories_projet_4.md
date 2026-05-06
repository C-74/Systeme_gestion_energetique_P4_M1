# User Stories - Projet 4

Projet concerné : **Système de gestion énergétique intelligent**.

Ces user stories couvrent le socle fonctionnel et technique attendu par le sujet, sans inclure les critères d'acceptation.

## Personae retenus

- Gestionnaire énergétique
- Analyste data
- Administrateur de la plateforme
- Responsable SRE / exploitation

## Backlog des user stories

### US-01 - Simulation des données énergétiques

En tant que **gestionnaire énergétique**, je veux **disposer de données simulées de consommation, de production solaire et de stockage**, afin de **tester la plateforme même en l'absence de capteurs physiques réels**.

### US-02 - Supervision des capteurs virtuels

En tant que **gestionnaire énergétique**, je veux **consulter l'état et les valeurs des capteurs virtuels**, afin de **surveiller rapidement l'activité énergétique d'un bâtiment ou d'un quartier**.

### US-03 - Import de mesures externes

En tant que **gestionnaire énergétique**, je veux **importer un fichier CSV de mesures énergétiques**, afin de **comparer des données personnalisées avec les scénarios simulés par la plateforme**.

### US-04 - Calcul automatique des KPI énergétiques

En tant que **gestionnaire énergétique**, je veux **obtenir automatiquement les principaux indicateurs de performance énergétique**, afin d'**évaluer la qualité de fonctionnement du système énergétique**.

### US-05 - Comparaison entre scénario initial et scénario optimisé

En tant que **gestionnaire énergétique**, je veux **comparer un scénario de référence avec un scénario optimisé**, afin de **mesurer les gains sur l'import réseau, l'autonomie, l'autoconsommation, le coût et les émissions**.

### US-06 - Proposition d'optimisation de la consommation

En tant que **gestionnaire énergétique**, je veux **recevoir des recommandations sur le déplacement des charges flexibles et l'usage du stockage**, afin de **réduire les pics de consommation et améliorer la performance énergétique globale**.

### US-07 - Consultation d'un tableau de bord web

En tant que **gestionnaire énergétique**, je veux **accéder à une interface web centralisée**, afin de **visualiser en un seul endroit les capteurs, les KPI et les résultats d'optimisation**.

### US-08 - Exposition des données pour l'analyse

En tant qu'**analyste data**, je veux **accéder aux données énergétiques et aux KPI via une API ou une source exploitable**, afin de **produire des analyses et des tableaux de bord pertinents**.

### US-09 - Analyse des tendances sur plusieurs jours

En tant qu'**analyste data**, je veux **disposer d'un historique exploitable sur plusieurs jours**, afin d'**identifier des tendances, détecter des anomalies et formuler des pistes d'amélioration**.

### US-10 - Production d'analyses énergétiques pertinentes

En tant qu'**analyste data**, je veux **produire au moins trois analyses pertinentes à partir des données collectées**, afin d'**aider l'équipe à interpréter les performances énergétiques et à orienter les décisions d'optimisation**.

### US-11 - Déploiement reproductible de la plateforme

En tant qu'**administrateur de la plateforme**, je veux **déployer l'application dans des conteneurs**, afin de **garantir une exécution homogène entre les environnements de développement, de test et de production**.

### US-12 - Automatisation de la qualité et du déploiement

En tant qu'**administrateur de la plateforme**, je veux **disposer d'un pipeline CI/CD**, afin d'**automatiser les tests, la construction de l'application et la préparation du déploiement**.

### US-13 - Supervision de la fiabilité du service

En tant que **responsable SRE / exploitation**, je veux **suivre la disponibilité, les erreurs et les indicateurs de service de la plateforme**, afin d'**anticiper les incidents et piloter la fiabilité du système**.

### US-14 - Suivi des objectifs de service

En tant que **responsable SRE / exploitation**, je veux **définir et suivre des objectifs de service comme les SLO, SLA et error budgets**, afin de **mesurer objectivement la qualité de service rendue**.
