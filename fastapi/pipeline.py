from model_service import predict_sentiment
from database import save_tweet
from datetime import datetime

def process_tweets_pipeline(tweets):
    # Extraire les textes uniquement pour l'envoyer au modèle
    texts = []
    for tweet in tweets:
        texts.append(tweet.get("text", ""))

    # 2. Prédire le sentiment de chaque tweet en appelant le fichier model_service.py (sous forme d'array des dicts)
    results = predict_sentiment(texts)

    processed_count = 0
    
    # On parcourt les tweets originaux et les résultats du modèle en parallèle
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