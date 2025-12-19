import joblib
import os
import re
import string
import numpy as np
from sentence_transformers import SentenceTransformer

# --- CONFIGURATION ---
# On récupère le chemin depuis docker-compose, ou on utilise une valeur par défaut
MODELS_PATH = os.getenv("MODELS_PATH", "/code/models")
MODEL_FILENAME = "ML/linear_svc_tuned.pkl"  # Assurez-vous que votre fichier s'appelle bien comme ça dans le dossier models/



# Variables globales pour les modèles (Lazy Loading)
svm_model = None
embedding_model = None



def load_models():
    """Charge les modèles en mémoire s'ils ne le sont pas déjà."""
    global svm_model, embedding_model
    
    # 1. Chargement du Classifier (SVM)
    model_full_path = os.path.join(MODELS_PATH, MODEL_FILENAME)
    if svm_model is None:
        if os.path.exists(model_full_path):
            try:
                svm_model = joblib.load(model_full_path)
                print(f"✅ Modèle ML chargé depuis : {model_full_path}")
            except Exception as e:
                print(f"❌ Erreur chargement SVM : {e}")
        else:
            print(f"⚠️ Fichier modèle introuvable à : {model_full_path}")
            print("   -> Assurez-vous d'avoir mis votre fichier .pkl dans le dossier 'models/' à la racine du projet.")

    # 2. Chargement de l'Embedder (Sentence Transformer)
    if embedding_model is None:
        print("⏳ Chargement du modèle d'embedding (peut prendre du temps la 1ère fois)...")
        # J'ai remis le modèle 'paraphrase-multilingual' car il est plus léger et polyvalent que BAAI
        # Si vous tenez absolument à BAAI, remplacez par "BAAI/bge-large-en-v1.5"
        embedding_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
        print("✅ Modèle Embedding chargé.")




def clean_text(text):
    """Nettoie le texte (minuscules, suppression liens/ponctuation)."""
    if not isinstance(text, str): 
        return ""
    text = text.lower()                       
    text = re.sub(r"http\S+|@\w+|#\w+", "", text)  
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text.strip()



def softmax(x):
    """Fonction utilitaire pour transformer des scores en probabilités."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0)



def predict_sentiment(texts):
    """
    Reçoit une liste de textes, et retourne une liste de dictionnaires 
    avec sentiment et confiance.
    """
    # On s'assure que les modèles sont là
    load_models()
    
    # Si les modèles ont échoué à charger, on renvoie une erreur silencieuse
    if not svm_model or not embedding_model:
        return [{"sentiment": "error_model_missing", "confidence": 0.0} for t in texts]

    # 1. Nettoyage
    cleaned_texts = [clean_text(t) for t in texts]

    # 2. Vectorisation
    vectors = embedding_model.encode(cleaned_texts)

    # 3. Prédiction
    predictions = svm_model.predict(vectors)

    # 4. Calcul de la confiance (Compatible avec tous les modèles Scikit-Learn)
    results = []
    
    # On calcule les probabilités en lot (Batch) si possible
    try:
        if hasattr(svm_model, "predict_proba"):
            probs = svm_model.predict_proba(vectors)
            confidences = [round(float(max(p)), 3) for p in probs]
        elif hasattr(svm_model, "decision_function"):
            # Si le modèle n'a pas predict_proba (ex: LinearSVC par défaut), on utilise softmax sur decision_function
            scores = svm_model.decision_function(vectors)
            # Gestion cas binaire vs multiclasse
            if len(scores.shape) == 1: 
                # Cas binaire, on simule une proba
                confidences = [0.9 if abs(s) > 1 else 0.6 for s in scores] 
            else:
                probs = [softmax(s) for s in scores]
                confidences = [round(float(max(p)), 3) for p in probs]
        else:
            confidences = [1.0] * len(predictions)
    except Exception as e:
        print(f"⚠️ Erreur calcul confiance : {e}")
        confidences = [0.0] * len(predictions)

    # 5. Formatage du résultat
    # Mapping des labels numériques (0, 1, 2) vers texte si nécessaire
    LABEL_MAP = {0: "negative", 1: "neutral", 2: "positive"}
    
    for i in range(len(texts)):
        pred_val = predictions[i]
        # Si le modèle retourne un chiffre (0,1,2), on le convertit, sinon on garde le texte
        sentiment_label = LABEL_MAP.get(pred_val, str(pred_val)) if isinstance(pred_val, (int, np.integer)) else pred_val
        
        results.append({
            "text": texts[i],
            "sentiment": sentiment_label,
            "confidence": confidences[i]
        })

    return results