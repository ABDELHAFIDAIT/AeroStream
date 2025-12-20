import os
from sqlalchemy import create_engine, text
from datetime import datetime

# Configuration des variables de la BD qui correspond à ce qui est dans docker-compose.yaml
DB_USER = "airflow"
DB_PASS = "airflow"
DB_HOST = "postgres"
DB_NAME = "aerostream_db"
DB_PORT = "5432"




# Créer l'URL de connexion avec la BD
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"




# Créer le moteur SQLAlchemy
try:
    engine = create_engine(DATABASE_URL)
except Exception as e:
    print(f"Erreur lors de la configuration de DB: {e}")
    engine = None



# Crée la table tweets au démarrage si elle n'existe pas
def init_db():
    if not engine: return
    
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS tweets (
                    id SERIAL PRIMARY KEY,
                    sentiment VARCHAR(50),
                    confidence FLOAT,
                    airline VARCHAR(100),
                    negativereason VARCHAR(255),
                    created_at TIMESTAMP,
                    text TEXT
                )
            """))
            conn.commit()
        print("Base de données initialisée. Table 'tweets' créé !")
    except Exception as e:
        print(f"Erreur en initialisation de DB: {e}")






# Enregistre un tweet et sa prédiction dans la table tweets en DB
def save_tweet(tweet):
    if not engine: return

    try:
        # Gestion de la date (conversion du string en datetime)
        created_at = tweet.get("tweet_created")
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at)
            except ValueError:
                created_at = datetime.now()

        # Insérer dans la Table tweets 
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO tweets
                (sentiment, confidence, airline, negativereason, created_at, text)
                VALUES (:sentiment, :confidence, :airline, :negativereason, :created_at, :text)
            """), {
                "sentiment": tweet.get("airline_sentiment"),
                "confidence": tweet.get("airline_sentiment_confidence"),
                "airline": tweet.get("airline"),
                "negativereason": tweet.get("negativereason"),
                "created_at": created_at,
                "text": tweet.get("text")
            })
            conn.commit()
    except Exception as e:
        print(f"Erreur lors du sauvegarde du tweet : {e}")






# Récupèrer les Tweets de la DB
def get_tweets(limit=100):
    if not engine: return []

    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM tweets ORDER BY created_at DESC LIMIT :limit"),
                {"limit": limit}
            )

            tweets = []
            for row in result:
                tweets.append({
                    "id": row[0],
                    "sentiment": row[1],
                    "confidence": row[2],
                    "airline": row[3],
                    "negativereason": row[4],
                    "created_at": row[5],
                    "text": row[6],
                })
            return tweets
    except Exception as e:
        print(f"Erreur lors de la récupération des tweets: {e}")
        return []