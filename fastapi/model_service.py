import joblib
import os
import re
import string
import numpy as np
from sentence_transformers import SentenceTransformer


# On récupère le chemin depuis docker-compose, ou on utilise une valeur par défaut
MODELS_PATH = os.getenv("MODELS_PATH", "/code/models")
MODEL_FILENAME = "ML/linear_svc_tuned.pkl"



# Variables globales pour les modèles
svc_model = None
embedding_model = None




# Fonction pour charger les modèles (SVC et Embedding)
def load_models():
    global svc_model, embedding_model
    
    # Chargement du Classifier (Linear SVC)
    model_full_path = os.path.join(MODELS_PATH, MODEL_FILENAME)
    if svc_model is None:
        if os.path.exists(model_full_path):
            try:
                svc_model = joblib.load(model_full_path)
                print(f"Modèle chargé avec succès depuis : {model_full_path}")
            except Exception as e:
                print(f"Erreur lors du Chargement du modèle Linear SVC : {e}")
        else:
            print(f"Fichier modèle introuvable à : {model_full_path}")

    # Chargement de l'Embedder (Sentence Transformer)
    if embedding_model is None:
        print("Chargement du modèle d'embedding ...")
        embedding_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
        print("Modèle Embedding chargé avec Succès !")




# Fonction pour le nettoyae des textes 
def clean_text(text):
    if not isinstance(text, str): 
        return ""
    # Mise en miniscules
    text = text.lower()
    # Suppression des URLs
    text = re.sub(r"http\S+|@\w+|#\w+", "", text)
    # Suppression des ponctuations
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text.strip()





# Fonction utilitaire pour transformer des scores en probabilités
def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0)





# Fonction de prediction des sentiments qui reçoit une liste de textes, et retourne une liste de dictionnaires avec sentiment et confiance.
def predict_sentiment(texts):
    # Charger les modèles SVC et Embedder
    load_models()
    
    # Au cas d'echec de chargement des modèles
    if not svc_model or not embedding_model:
        return [{"sentiment": "error_model_missing", "confidence": 0.0} for t in texts]

    # Nettoyage des textes
    cleaned_texts = [clean_text(t) for t in texts]

    # Embedings des textes
    vectors = embedding_model.encode(cleaned_texts)

    # Prédiction des sentiments
    predictions = svc_model.predict(vectors)

    results = []
    
    # On calcule les probabilités en lot (Batch)
    try:
        if hasattr(svc_model, "predict_proba"):
            probs = svc_model.predict_proba(vectors)
            confidences = [round(float(max(p)), 3) for p in probs]
        elif hasattr(svc_model, "decision_function"):
            # Si le modèle n'a pas predict_proba comme pur LinearSVC, on utilise softmax sur decision_function
            scores = svc_model.decision_function(vectors)
            probs = [softmax(s) for s in scores]
            confidences = [round(float(max(p)), 3) for p in probs]
        else:
            confidences = [1.0] * len(predictions)
    except Exception as e:
        print(f"Erreur lors du calcul du score de confiance : {e}")
        confidences = [0.0] * len(predictions)

    # Mapping des labels numériques (0, 1, 2) vers des sentiments textes
    LABEL_MAP = {0: "negative", 1: "neutral", 2: "positive"}
    
    for i in range(len(texts)):
        pred_val = predictions[i]
        # Si le modèle retourne un chiffre (0,1,2), on le convertit, sinon on garde le texte
        sentiment_label = LABEL_MAP.get(pred_val, str(pred_val)) if isinstance(pred_val, (int, np.integer)) else pred_val
        
        if isinstance(pred_val, (int, np.integer)) :
            # regarde dans le dictionnaire LABEL_MAP pour trouver le nom correspondant
            sentiment_label = LABEL_MAP.get(pred_val, str(pred_val))
        else :
            sentiment_label = pred_val
        
        results.append({
            "text": texts[i],
            "sentiment": sentiment_label,
            "confidence": confidences[i]
        })

    return results


