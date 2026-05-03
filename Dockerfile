FROM python:3.10-slim

WORKDIR /app

# Installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Ajout du dossier src au PYTHONPATH pour que les modules soient trouvés
ENV PYTHONPATH="${PYTHONPATH}:/app/src"

# Le port 3000 pour l'API (Backend) et 80 pour Streamlit (Frontend)
EXPOSE 3000 80

# Par défaut, on ne met pas d'ENTRYPOINT strict pour pouvoir lancer soit uvicorn soit streamlit via la commande (CMD)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "3000"]
