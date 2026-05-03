import time
import psutil
from fastapi import FastAPI, Request
from starlette.responses import Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(
    title="Plateforme de Gestion Énergétique API",
    description="API pour la gestion des capteurs, indicateurs et modèles d'optimisation.",
    version="1.0.0"
)

# ---------------------------------------------------------
# Métriques Prometheus (Four Golden Signals)
# ---------------------------------------------------------

HTTP_REQUESTS = Counter(
    'http_requests_total',
    'Total des requêtes HTTP reçues (Traffic & Errors)',
    labelnames=['method', 'endpoint', 'status_code']
)

HTTP_LATENCY = Histogram(
    'http_request_duration_seconds',
    'Latence des requêtes HTTP en secondes (Latency)',
    labelnames=['method', 'endpoint']
)

SYSTEM_CPU = Gauge(
    'process_cpu_usage_percent',
    'Utilisation du CPU par le processus (Saturation)'
)
SYSTEM_RAM = Gauge(
    'process_memory_usage_percent',
    'Utilisation de la mémoire virtuelle par le processus (Saturation)'
)

def update_saturation_metrics():
    """Mise à jour des métriques de saturation."""
    SYSTEM_CPU.set(psutil.cpu_percent())
    SYSTEM_RAM.set(psutil.virtual_memory().percent)

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    method = request.method
    endpoint = request.url.path
    status_code = response.status_code

    HTTP_REQUESTS.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
    HTTP_LATENCY.labels(method=method, endpoint=endpoint).observe(process_time)
    
    return response

@app.get("/metrics", include_in_schema=False)
async def metrics():
    update_saturation_metrics()
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API du Système de Gestion Énergétique Intelligent"}

# Les routes pour les capteurs et les modèles seront ajoutées ici
