FROM python:3.10-slim

# Empêche Python d'écrire des fichiers .pyc et active le logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code (sera écrasé par le volume docker-compose, mais bonne pratique)
COPY . .

# Port par défaut de Streamlit
EXPOSE 8501

# Lancement de l'application
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]