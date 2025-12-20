from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import random
from faker import Faker

from pipeline import process_tweets_pipeline
from database import init_db, get_tweets

app = FastAPI(title="Aerostream Analytics API", version="2.0")

# Faker pour Génération des Tweets
fake = Faker()
Faker.seed(42)




# Constantes pour la Génération Aléatoire
AIRLINES = ['Virgin America', 'United', 'Southwest', 'Delta', 'US Airways', 'American']
SENTIMENTS = ['neutral', 'positive', 'negative']
NEGATIVE_REASONS = [
    None,
    'Bad Flight',
    "Can't Tell",
    'Late Flight',
    'Customer Service Issue',
    'Flight Booking Problems',
    'Lost Luggage',
    'Flight Attendant Complaints',
    'Cancelled Flight',
    'Damaged Luggage',
    'longlines'
]




# Structure de Base à Respecter pour les Tweets
class Tweet(BaseModel):
    airline_sentiment_confidence: float
    airline: str
    negativereason: Optional[str]
    tweet_created: str 
    text: str





def generate_tweet() -> Tweet:
    # Random Choix des Compagnies d'Airlines
    airline = random.choice(AIRLINES)

    # Random Choix des Sentiments
    sentiment = random.choices(
        SENTIMENTS,
        weights=[0.3, 0.25, 0.45], # Associer des Poids à Chaque Sentiment pour simuler la vie réelle
        k=1 # Tirer un seul sentiment
    )[0] # Puisque .coices renvoie une Liste des Sentiments, on Choisis le 1er Elément 

    confidence = round(random.uniform(0.5, 1.0), 3) # pour chaque sentiment, on assigne un score de confiance entre >0.5 et <1.0
    if sentiment == 'neutral':
        confidence = round(random.uniform(0.3, 0.7), 3) # pour neutral, on réduit le score de confiance en simulant le vrai terrain

    negativereason = None
    if sentiment == 'negative':
        negativereason = random.choice(NEGATIVE_REASONS[1:]) # Un tweet négatif doit obligatoirement avoir une raison mais on l'empêche de choisir None
    elif sentiment == 'neutral':
        negativereason = random.choice(NEGATIVE_REASONS) # Pas de Slicing 

    handles = {
        'Virgin America': '@VirginAmerica',
        'United': '@united',
        'Southwest': '@SouthwestAir',
        'Delta': '@Delta',
        'US Airways': '@USAirways',
        'American': '@AmericanAir'
    }
    handle = handles[airline]

    if sentiment == 'positive':
        texts = [
            f"{handle} Great service today — flight was on time and crew was amazing! ✈️👏",
            f"Shoutout to {handle} for upgrading me last minute. You made my day!",
            f"Smooth flight with {handle} — love the new seats and in-flight snacks. 🍪",
        ]
    elif sentiment == 'negative':
        texts = [
            f"{handle} why are your first fares in May over three times more than other carriers when all seats are available to select???",
            f"{handle} flight delayed 4 hours with no updates. Terrible communication. #disappointed",
            f"{handle} lost my luggage AGAIN. This is the third time this year. Unacceptable.",
            f"{handle} customer service hung up on me. What kind of support is that?!",
            f"{handle} 2-hour line at check-in for pre-paid bags. Ridiculous inefficiency.",
        ]
    else: 
        texts = [
            f"{handle} flight was fine. Boarding took a while, but nothing major.",
            f"Average experience with {handle}. On time, but seat was a bit tight.",
            f"Checked in online with {handle}, flight happened. No complaints, no praise.",
        ]

    text = random.choice(texts) # Choix Aléatoire des Tweets
    
    # on injecte une phrase inutile dans 30% des tweets pour tester le modele contre des données imparfaites
    if random.random() < 0.3:
        text += " " + fake.sentence(nb_words=6).rstrip(".")

    tweet_created = datetime.now(timezone.utc).isoformat() # ajouter la date de création du tweet

    return Tweet(
        airline_sentiment_confidence=confidence,
        airline=airline,
        negativereason=negativereason,
        tweet_created=tweet_created,
        text=text
    )






# transforme DB vide en une DB structurée avec la table tweets prete à travailler
@app.on_event("startup")
async def startup():
    print("Démarrage de l'API AeroStream v2...")
    init_db()








# --- ENDPOINTS ---


# Endpoint pour la génération des microbatchs de tweets (par défaut 10 tweets)
@app.post("/batch")
def get_microbatch(batch_size: int = 10):
    # Sécurise la variable batch_size pour qu'elle reste dans une plage raisonnable (entre 1 et 100)
    batch_size = min(max(batch_size, 1), 100)
    
    print(f"Génération de {batch_size} tweets...")
    
    # Génération des objets Tweet (Crée une liste d'objets "Tweet")
    generated_tweets_objects = [generate_tweet() for _ in range(batch_size)]
    
    # 2. Conversion en dictionnaires pour pipeline.py
    tweets_dicts = [t.dict() for t in generated_tweets_objects]
    
    # 3. Envoi au pipeline
    return process_tweets_pipeline(tweets_dicts)




# Endpoint pour récupérer un nombre (par défaut 50) des tweets de la DB
@app.get("/tweets")
def read_tweets(limit: int = 50):
    tweets = get_tweets(limit)
    return {
        "total": len(tweets),
        "tweets": tweets
    }