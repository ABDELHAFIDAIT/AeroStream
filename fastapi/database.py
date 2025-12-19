import os
from sqlalchemy import create_engine, text
from datetime import datetime

# 1. Configuration (Variables d'environnement Docker)
# Ces variables sont injectées par le docker-compose.yaml
DB_USER = os.getenv("POSTGRES_USER", "airflow")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "airflow")
DB_HOST = os.getenv("DB_HOST", "postgres") # Nom du service dans docker-compose
DB_NAME = os.getenv("POSTGRES_DB", "aerostream_db")
DB_PORT = "5432"

# 2. Création de l'URL de connexion
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Création du moteur SQLAlchemy
try:
    engine = create_engine(DATABASE_URL)
except Exception as e:
    print(f"❌ Erreur critique configuration DB: {e}")
    engine = None

def init_db():
    """Crée la table 'tweets' au démarrage si elle n'existe pas."""
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
        print("✅ Base de données initialisée (Table 'tweets' vérifiée).")
    except Exception as e:
        print(f"⚠️ Erreur init DB: {e}")

def save_tweet(tweet):
    """Enregistre un tweet et sa prédiction en base."""
    if not engine: return

    try:
        # Gestion de la date (conversion string -> datetime si besoin)
        created_at = tweet.get("tweet_created")
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at)
            except ValueError:
                created_at = datetime.now()

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
        print(f"❌ Erreur sauvegarde tweet: {e}")

def get_tweets(limit=100):
    """Récupère l'historique des tweets."""
    if not engine: return []

    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM tweets ORDER BY created_at DESC LIMIT :limit"),
                {"limit": limit}
            )

            tweets = []
            for row in result:
                # On utilise les index car SQLAlchemy renvoie des tuples par défaut ici
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
        print(f"❌ Erreur lecture tweets: {e}")
        return []