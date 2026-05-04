# Projet 4 – Système de gestion énergétique intelligent

Plateforme Python de simulation d'un bâtiment intelligent avec :

- Données factices de capteurs (consommation, production solaire, stockage batterie)
- Calcul d'indicateurs de performance énergétique (KPI)
- Modèle d'optimisation de la consommation flexible

## Objectifs couverts

- Générer des séries temporelles réalistes (mais synthétiques)
- Calculer des indicateurs fiables et vérifiables
- Proposer une stratégie d'optimisation orientée autoconsommation

## Structure

```text
src/energy_management/
	__init__.py
	models.py
	simulator.py
	dispatch.py
	indicators.py
	optimization.py
	cli.py
tests/
	test_indicators.py
	test_optimization.py
pyproject.toml
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Cette installation inclut les dépendances nécessaires pour :

- la CLI métier ;
- l'API FastAPI ;
- le dashboard Streamlit ;
- l'export de métriques Prometheus.

## Exécution

Simulation baseline + optimisation, puis affichage des KPI :

```bash
python -m energy_management.cli --seed 42 --date 2026-03-24
```

Sortie JSON exploitable :

```bash
python -m energy_management.cli --seed 42 --json
```

Utiliser vos propres données (CSV avec colonnes `timestamp,base_load_kwh,flexible_load_kwh,solar_kwh`) :

```bash
python -m energy_management.cli --input-csv data/mesures.csv
```

Générer rapidement un jeu de données synthétiques :

```bash
python scripts/simulate_days.py --start-date 2026-04-14 --days 7 --json
```

Calculer les KPI à partir d'un CSV existant :

```bash
python scripts/kpi_from_csv.py data/mesures.csv --json
```

## Lancement applicatif

API FastAPI :

```bash
uvicorn api.main:app --host 0.0.0.0 --port 3000
```

Dashboard Streamlit :

```bash
streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0
```

## Déploiement local avec Docker Compose

```bash
docker compose up --build
```

Services exposés :

- API : `http://localhost:3000`
- Dashboard : `http://localhost:8501`
- Prometheus : `http://localhost:9090`
- Grafana : `http://localhost:8080`

Documentation SRE :

- Voir `document_sre_projet_4.md` pour les SLI, SLO, SLA et error budgets.

## KPI calculés

- Consommation totale
- Production solaire totale
- Import réseau / Export réseau
- Taux d'autoconsommation solaire
- Taux d'autonomie
- Pic d'appel réseau
- Facteur de charge
- Cycles batterie équivalents
- Coût net énergétique
- Émissions CO₂ liées au réseau

## Tests

```bash
pytest -q
```

Les tests vérifient les formules KPI et la logique d'optimisation.
