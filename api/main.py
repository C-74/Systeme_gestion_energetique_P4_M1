from fastapi import FastAPI

app = FastAPI(
    title="Plateforme de Gestion Énergétique API",
    description="API pour la gestion des capteurs, indicateurs et modèles d'optimisation.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API du Système de Gestion Énergétique Intelligent"}

# Les routes pour les capteurs et les modèles seront ajoutées ici
