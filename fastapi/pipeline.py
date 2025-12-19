from model_service import predict_sentiment
from database import save_tweet
from datetime import datetime

def process_tweets_pipeline(tweets):
    """
    Reçoit une liste de tweets bruts (dictionnaires),
    prédit leur sentiment, et sauvegarde le tout en base.
    """
    
    # 1. Extraction des textes uniquement (pour l'envoyer au modèle)
    texts = []
    for tweet in tweets:
        texts.append(tweet.get("text", ""))

    # 2. Prédiction (Appel au fichier model_service.py)
    # Cela retourne : [{"text": "...", "sentiment": "positive", "confidence": 0.95}, ...]
    results = predict_sentiment(texts)

    # 3. Sauvegarde (Appel au fichier database.py)
    processed_count = 0
    
    # On parcourt les tweets originaux et les résultats de l'IA en parallèle
    for tweet, result in zip(tweets, results):
        
        # On prépare l'objet final formaté pour la base de données
        tweet_data_for_db = {
            "airline_sentiment": result["sentiment"],
            "airline_sentiment_confidence": result["confidence"],
            "airline": tweet.get("airline", "Unknown"),
            "negativereason": tweet.get("negativereason"),
            # On garde la date d'origine, ou on met l'heure actuelle si absente
            "tweet_created": tweet.get("tweet_created", datetime.now().isoformat()),
            "text": tweet.get("text")
        }
        
        # On appelle la fonction de sauvegarde
        save_tweet(tweet_data_for_db)
        processed_count += 1

    return {
        "status": "success",
        "processed": processed_count
    }