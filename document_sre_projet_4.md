# Document SRE - Projet 4

## Objectif

Ce document formalise les objectifs de fiabilite du **Systeme de gestion energetique intelligent**. Il couvre les **SLI**, les **SLO**, les **SLA** et les **error budgets** associes au projet.

L'objectif est double :

- disposer d'objectifs mesurables et suivables dans **Prometheus** et **Grafana** ;
- donner a l'equipe une regle claire pour arbitrer entre **vitesse de livraison** et **fiabilite**.

## Perimetre du service

Les objectifs ci-dessous s'appliquent a l'environnement applicatif du projet :

- **API FastAPI** exposee sur `:3000` ;
- **dashboard Streamlit** expose sur `:8501` ;
- **supervision Prometheus/Grafana** utilisee pour observer le service.

Le perimetre **utilisateur** retenu pour les SLO/SLA est le suivant :

- l'API doit repondre correctement aux requetes HTTP ;
- le dashboard doit etre accessible et exploitable pour lancer une simulation et consulter les resultats ;
- les outils de supervision doivent permettre de suivre ces indicateurs.

Elements exclus du SLA utilisateur :

- les postes de developpement locaux ;
- les executions ponctuelles de scripts CLI ;
- les indisponibilites volontaires pendant maintenance pedagogique annoncee.

Fenetre de mesure retenue :

- **30 jours glissants** pour les SLO et les SLA ;
- fuseau de reference : **Europe/Paris**.

## Definitions

- **SLI** : indicateur brut mesure par l'outillage.
- **SLO** : objectif interne que l'equipe cherche a tenir.
- **SLA** : engagement de service annonce aux utilisateurs du projet.
- **Error budget** : part de non-fiabilite acceptable avant de ralentir les changements.

Dans ce projet, le SLA n'est **pas contractuel au sens commercial**. En cas de non-respect, la contrepartie attendue est une **analyse d'incident**, un **plan d'action** et une **priorisation des corrections**.

## SLI retenus et mode de calcul

### 1. Disponibilite de l'API

Source :

- metrique Prometheus `up{job="backend_api"}`.

PromQL :

```promql
avg_over_time(up{job="backend_api"}[30d]) * 100
```

Interpretation :

- `100%` signifie que la cible Prometheus a toujours ete joignable sur la periode ;
- `0%` signifie qu'elle ne l'a jamais ete.

### 2. Taux de succes des requetes API

Source :

- metrique `http_requests_total` exposee par l'API.

PromQL :

```promql
100 * (
  1 -
  (
    sum(increase(http_requests_total{job="backend_api", status_code=~"5..", endpoint!="/metrics"}[30d]))
    /
    sum(increase(http_requests_total{job="backend_api", endpoint!="/metrics"}[30d]))
  )
)
```

Interpretation :

- mesure la part de requetes API qui ne se terminent pas en erreur serveur `5xx` ;
- le endpoint `/metrics` est exclu pour ne pas melanger trafic metier et trafic de supervision.

### 3. Latence de l'API

Source :

- histogramme `http_request_duration_seconds`.

PromQL :

```promql
histogram_quantile(
  0.95,
  sum by (le) (
    rate(http_request_duration_seconds_bucket{job="backend_api", endpoint!="/metrics"}[5m])
  )
)
```

Interpretation :

- donne la **latence p95** sur une fenetre courte de 5 minutes ;
- sert a verifier que l'API reste reactive, meme si elle n'est pas totalement indisponible.

### 4. Disponibilite du dashboard

Source :

- metrique Prometheus `up{job="frontend_dashboard"}`.

PromQL :

```promql
avg_over_time(up{job="frontend_dashboard"}[30d]) * 100
```

Interpretation :

- le dashboard est considere disponible si son exporter Prometheus et son processus applicatif repondent.

### 5. Latence du dashboard

Source :

- histogramme `streamlit_run_duration_seconds`.

PromQL :

```promql
histogram_quantile(
  0.95,
  sum by (le) (
    rate(streamlit_run_duration_seconds_bucket{job="frontend_dashboard"}[5m])
  )
)
```

Interpretation :

- mesure le temps de calcul/rechargement du dashboard ;
- la mesure est pertinente pour la navigation et le lancement des simulations.

### 6. Erreurs fonctionnelles du dashboard

Source :

- `streamlit_errors_total` ;
- `streamlit_interactions_total`.

PromQL :

```promql
100 * (
  1 -
  (
    increase(streamlit_errors_total{job="frontend_dashboard"}[30d])
    /
    increase(streamlit_interactions_total{job="frontend_dashboard"}[30d])
  )
)
```

Interpretation :

- cet indicateur mesure la part d'interactions qui ne debouchent pas sur une erreur visible cote application ;
- il inclut notamment les erreurs de traitement ou de chargement remontees dans l'interface.

### 7. Saturation technique

Sources :

- `process_cpu_usage_percent` ;
- `process_memory_usage_percent`.

PromQL :

```promql
max_over_time(process_cpu_usage_percent{job="backend_api"}[5m])
max_over_time(process_memory_usage_percent{job="backend_api"}[5m])
max_over_time(process_cpu_usage_percent{job="frontend_dashboard"}[5m])
max_over_time(process_memory_usage_percent{job="frontend_dashboard"}[5m])
```

Interpretation :

- ces indicateurs servent surtout de **signaux de prevention** ;
- ils ne portent pas le SLA, mais aident a expliquer une degradation de latence ou d'erreurs.

## SLO cibles

### SLO-1 - Disponibilite API

- Objectif : disponibilite de l'API >= **99,5%** sur 30 jours glissants.
- SLI associe : `up{job="backend_api"}`.
- Error budget : **0,5%** d'indisponibilite autorisee.
- Conversion budget : **3 h 36 min** d'indisponibilite maximale par periode de 30 jours.

### SLO-2 - Taux de succes API

- Objectif : taux de succes API >= **99,0%** sur 30 jours glissants.
- SLI associe : ratio de requetes non `5xx`.
- Error budget : **1,0%** des requetes peuvent echouer en `5xx`.
- Conversion budget : **1 requete sur 100** au maximum peut etre en erreur serveur sur la periode.

### SLO-3 - Latence API

- Objectif : latence **p95 < 500 ms** sur au moins **95%** des fenetres de 5 minutes.
- SLI associe : `http_request_duration_seconds`.
- Error budget : **5%** des fenetres de 5 minutes peuvent depasser le seuil.
- Conversion budget : sur 30 jours, cela represente au maximum **432 fenetres de 5 minutes** degradees.

### SLO-4 - Disponibilite dashboard

- Objectif : disponibilite du dashboard >= **99,0%** sur 30 jours glissants.
- SLI associe : `up{job="frontend_dashboard"}`.
- Error budget : **1,0%** d'indisponibilite autorisee.
- Conversion budget : **7 h 12 min** d'indisponibilite maximale par periode de 30 jours.

### SLO-5 - Latence dashboard

- Objectif : latence **p95 < 2 s** sur au moins **95%** des fenetres de 5 minutes.
- SLI associe : `streamlit_run_duration_seconds`.
- Error budget : **5%** des fenetres de 5 minutes peuvent depasser le seuil.
- Conversion budget : **432 fenetres de 5 minutes** degradees au maximum sur 30 jours.

### SLO-6 - Taux de succes des interactions dashboard

- Objectif : taux d'interactions sans erreur >= **98,0%** sur 30 jours glissants.
- SLI associe : `streamlit_interactions_total` vs `streamlit_errors_total`.
- Error budget : **2,0%** des interactions peuvent se terminer en erreur applicative.
- Conversion budget : **2 interactions sur 100** au maximum peuvent echouer.

## SLA retenus

Les SLA sont legerement moins stricts que les SLO, afin de garder une marge d'exploitation raisonnable.

### SLA-1 - Disponibilite API

- Engagement annonce : disponibilite API >= **99,0%** sur 30 jours glissants.
- Budget d'indisponibilite correspondant : **7 h 12 min** maximum par periode de 30 jours.

### SLA-2 - Disponibilite dashboard

- Engagement annonce : disponibilite dashboard >= **98,5%** sur 30 jours glissants.
- Budget d'indisponibilite correspondant : **10 h 48 min** maximum par periode de 30 jours.

### SLA-3 - Communication incident

- En cas d'incident majeur identifie par l'equipe, un etat doit etre partage au groupe projet dans la **journee ouvrée**.
- En cas de non-respect d'un SLA, l'equipe produit un **mini post-mortem** avec cause, impact et action corrective.

## Politique d'error budget

Le budget d'erreur sert a piloter la cadence de changement.

- **0% a 50% du budget consomme** : rythme normal, livraisons autorisees.
- **50% a 80%** : vigilance renforcee, verification manuelle et revue des dashboards avant livraison.
- **80% a 100%** : seules les corrections, ameliorations de tests et changements a faible risque sont autorises.
- **Au-dela de 100%** : gel des changements non critiques jusqu'au retour sous controle du service.

Actions attendues si le budget est depasse :

- ouvrir un incident ou une action corrective dans le backlog ;
- identifier la cause principale ;
- corriger la source de degradation ;
- ajouter ou ajuster tests, observabilite et documentation si necessaire.

## Suivi operationnel recommande

Les panneaux minimum a afficher dans Grafana sont :

- disponibilite API ;
- disponibilite dashboard ;
- taux d'erreurs `5xx` API ;
- latence p95 API ;
- latence p95 dashboard ;
- CPU/RAM backend ;
- CPU/RAM frontend.

Rythme de suivi recommande :

- verification rapide a chaque sprint ;
- revue hebdomadaire de l'etat des budgets ;
- revue mensuelle SRE pour constater si les SLO et SLA ont ete respectes.

## Decision de reference pour le projet

Pour ce projet, l'equipe retient les principes suivants :

- le **dashboard** est le point d'entree principal du service ;
- l'**API** doit rester plus exigeante en disponibilite que le dashboard ;
- les **latences** sont suivies comme objectifs de qualite d'experience ;
- les **error budgets** servent de garde-fou avant d'ajouter de nouvelles fonctionnalites.

Ce document constitue la reference SRE du projet pour les US-13 et US-14.
