import os
from fastapi import FastAPI
from pydantic import BaseModel

# Initialisation de l'application
app = FastAPI(title="AeroStream API", version="1.0")

# --- Modèle de données pour recevoir un avis (Exemple) ---
class ReviewRequest(BaseModel):
    text: str

# --- Route de vérification (Health Check) ---
@app.get("/")
def read_root():
    return {
        "status": "online", 
        "message": "Bienvenue sur l'API AeroStream v1",
        "env_chroma_path": os.getenv("CHROMA_DB_PATH"), # Pour vérifier que la config passe bien
        "env_models_path": os.getenv("MODELS_PATH")
    }

# --- Route de prédiction (Simulée pour l'instant) ---
@app.post("/predict")
def predict_sentiment(review: ReviewRequest):
    # TODO: Ici, vous chargerez le modèle et ferez la prédiction réelle
    # Pour le test, on renvoie une fausse prédiction
    return {
        "text": review.text,
        "sentiment": "positive", # Fake result
        "score": 0.95
    }