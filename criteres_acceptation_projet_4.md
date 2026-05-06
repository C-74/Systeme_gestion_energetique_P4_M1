# Critères d'acceptation - Projet 4

Projet concerné : **Système de gestion énergétique intelligent**.

Ce document complète les user stories du fichier `user_stories_projet_4.md` en précisant :

- la **Definition of Done** de l'équipe ;
- les **critères d'acceptation** associés à chaque user story.

## Definition of Done

Une tâche ou une user story est considérée comme **finie** si toutes les conditions suivantes sont remplies :

- le besoin décrit dans la user story est implémenté et fonctionne localement ;
- les critères d'acceptation de la user story sont vérifiés ;
- le code est versionné, relu si nécessaire et intégré proprement dans le dépôt ;
- les tests automatisés existants passent, et de nouveaux tests sont ajoutés si la fonctionnalité le justifie ;
- aucune erreur bloquante n'apparaît au lancement de l'application ou des services concernés ;
- la documentation minimale est mise à jour si le comportement, l'utilisation ou le déploiement changent ;
- si la fonctionnalité impacte l'infrastructure, le conteneur, la CI/CD ou le monitoring, les fichiers associés sont aussi mis à jour ;
- le résultat est démontrable par l'équipe pendant une revue de sprint.

## Critères d'acceptation par user story

### US-01 - Simulation des données énergétiques

- Étant donné une date de simulation, quand la génération est lancée, alors un jeu de données cohérent est produit.
- Les données générées contiennent au minimum des horodatages, la consommation, la production solaire et le stockage ou les éléments nécessaires à son calcul.
- Les données simulées sont exploitables par les autres modules de la plateforme sans retraitement manuel.

### US-02 - Supervision des capteurs virtuels

- Étant donné que l'application est lancée, quand un utilisateur consulte les capteurs virtuels, alors il peut voir leur type et leur état.
- Chaque capteur affiché correspond à une source énergétique identifiée du projet : consommation, solaire ou stockage.
- Les informations affichées sont lisibles et accessibles depuis l'interface prévue.

### US-03 - Import de mesures externes

- Étant donné un fichier CSV valide, quand l'utilisateur l'importe, alors les données sont chargées sans erreur.
- Si le fichier est invalide ou incomplet, alors un message explicite indique le problème.
- Les données importées peuvent être réutilisées par les modules de calcul de KPI et d'optimisation.

### US-04 - Calcul automatique des KPI énergétiques

- À partir d'un jeu de données valide, la plateforme calcule automatiquement les KPI attendus du projet.
- Les indicateurs produits incluent au minimum les mesures utiles à l'évaluation énergétique : consommation, import ou export réseau, autonomie, autoconsommation, coût ou émissions.
- Les résultats sont restitués dans un format lisible et réutilisable.

### US-05 - Comparaison entre scénario initial et scénario optimisé

- Pour une même période, la plateforme affiche les résultats du scénario initial et du scénario optimisé.
- L'utilisateur peut identifier clairement les écarts entre les deux scénarios sur les KPI principaux.
- La comparaison ne demande pas de calcul manuel supplémentaire pour interpréter le gain obtenu.

### US-06 - Proposition d'optimisation de la consommation

- À partir des données disponibles, la plateforme fournit une stratégie ou une proposition d'optimisation.
- La proposition agit sur des leviers cohérents avec le sujet, comme le déplacement de charge ou l'utilisation du stockage.
- Le résultat de l'optimisation est mesurable via une amélioration d'au moins un KPI énergétique.

### US-07 - Consultation d'un tableau de bord web

- L'application propose une interface web accessible au lancement du projet.
- Le tableau de bord permet au minimum de consulter une vue d'ensemble, les capteurs, les KPI et l'optimisation.
- La navigation entre les sections ne provoque pas d'erreur bloquante.

### US-08 - Exposition des données pour l'analyse

- Les données énergétiques sont accessibles via une API ou une source exploitable annoncée par l'équipe.
- Le schéma des données exposées est cohérent et documenté minimalement.
- Les données retournées sont suffisantes pour être exploitées par un analyste data sans ressaisie manuelle.

### US-09 - Analyse des tendances sur plusieurs jours

- La plateforme ou les scripts permettent de produire un historique sur plusieurs jours.
- Cet historique permet d'observer des évolutions dans la consommation, la production ou les KPI.
- Les données multi-jours sont exportables ou consultables dans un format exploitable.

### US-10 - Production d'analyses énergétiques pertinentes

- L'équipe livre au moins trois analyses distinctes à partir des données collectées.
- Chaque analyse répond à un objectif clair, par exemple tendance, anomalie, comparaison ou prédiction simple.
- Les résultats des analyses sont présentables dans un support lisible, comme un tableau de bord, un rapport ou une visualisation.

### US-11 - Déploiement reproductible de la plateforme

- L'application peut être lancée via les conteneurs prévus par le projet.
- Le démarrage de l'environnement ne dépend pas d'installations manuelles non documentées.
- Un membre de l'équipe peut reproduire le lancement sur une autre machine avec les instructions fournies.

### US-12 - Automatisation de la qualité et du déploiement

- Un pipeline CI/CD exécute automatiquement au moins les étapes essentielles de vérification du projet.
- En cas d'échec des tests ou du build, le pipeline signale clairement l'erreur.
- Le pipeline couvre le flux attendu par l'équipe pour sécuriser l'intégration continue.

### US-13 - Supervision de la fiabilité du service

- Les composants principaux de la plateforme exposent des informations de supervision exploitables.
- L'équipe peut visualiser au moins l'état du service, les erreurs ou des métriques techniques utiles.
- En cas de dysfonctionnement, les outils de monitoring permettent d'identifier rapidement qu'un problème existe.

### US-14 - Suivi des objectifs de service

- L'équipe définit explicitement au moins un ensemble d'objectifs de service mesurables.
- Les SLO, SLA ou error budgets retenus sont documentés et compréhensibles par l'équipe.
- Les indicateurs choisis peuvent être suivis à partir des outils de supervision mis en place.
