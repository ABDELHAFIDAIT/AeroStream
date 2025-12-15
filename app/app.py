import streamlit as st
import requests
import os
import time

# Configuration de la page
st.set_page_config(page_title="AeroStream Analytics", layout="wide")

st.title("✈️ AeroStream Analytics Dashboard")

# Récupération de l'URL de l'API depuis les variables d'environnement
# (Défini dans docker-compose: API_URL=http://api:8000)
API_URL = os.getenv("API_URL", "http://api:8000")

# --- Section de Test de Connexion ---
st.header("État du Système")
if st.button("Vérifier la connexion API"):
    try:
        with st.spinner("Connexion à l'API..."):
            response = requests.get(f"{API_URL}/")
            if response.status_code == 200:
                data = response.json()
                st.success(f"✅ API Connectée ! Message : {data['message']}")
                st.json(data) # Affiche les détails techniques
            else:
                st.error(f"❌ Erreur API : {response.status_code}")
    except Exception as e:
        st.error(f"❌ Impossible de contacter l'API. Vérifiez que le conteneur 'api' tourne. Erreur : {e}")

# --- Section Simulation de Classification ---
st.divider()
st.header("Test de Classification en Direct")
user_input = st.text_area("Entrez un avis client :", "The flight was amazing but the food was cold.")

if st.button("Analyser le sentiment"):
    if user_input:
        try:
            payload = {"text": user_input}
            response = requests.post(f"{API_URL}/predict", json=payload)
            result = response.json()
            st.info(f"Sentiment détecté : {result['sentiment']} (Score: {result['score']})")
        except Exception as e:
            st.error(f"Erreur lors de la prédiction : {e}")