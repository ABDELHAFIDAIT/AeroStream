import streamlit as st
import pandas as pd
import requests
import plotly.express as px



# Configuration de la page
st.set_page_config(
    page_title="AeroStream Analytics",
    page_icon="✈️",
    layout="wide"
)



# Définition de l'URL de l'API
API_URL = "http://fastapi:8000"




# --- FONCTIONS UTILITAIRES ---

def fetch_data(limit=500):
    """Récupère les tweets depuis l'API FastAPI."""
    try:
        # On demande plus de tweets pour avoir des stats pertinentes
        response = requests.get(f"{API_URL}/tweets", params={"limit": limit})
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data["tweets"])
        else:
            st.error("Erreur lors de la récupération des données.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Impossible de contacter l'API : {e}")
        return pd.DataFrame()










def trigger_batch_generation(size=20):
    """Déclenche la génération de tweets via l'API."""
    try:
        requests.post(f"{API_URL}/batch", params={"batch_size": size})
        st.success(f"{size} nouveaux tweets générés et analysés !")
    except Exception as e:
        st.error(f"Erreur lors de la génération : {e}")

# --- INTERFACE UTILISATEUR ---

st.title("✈️ AeroStream Analytics Dashboard")
st.markdown("Surveillance en temps réel de la satisfaction client des compagnies aériennes.")

# --- SIDEBAR (Contrôles) ---
with st.sidebar:
    st.header("🎮 Contrôles")
    
    # Bouton pour simuler de l'activité
    if st.button("Générer 20 Tweets (Simulation)"):
        trigger_batch_generation(20)
        st.rerun() # Rafraîchit la page immédiatement

    st.divider()
    st.info("Ce dashboard se connecte à l'API FastAPI, récupère les données stockées dans PostgreSQL et affiche les analyses du modèle SVC.")

# --- CHARGEMENT DES DONNÉES ---
df = fetch_data(limit=1000)

if not df.empty:
    
    # Conversion de la date pour un tri correct si besoin
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"])

    # --- PARTIE 1 : STATISTIQUES GLOBALES (KPIs) ---
    st.subheader("📊 Statistiques Générales")
    
    kpi1, kpi2, kpi3 = st.columns(3)

    # 1. Nombre total de tweets
    total_tweets = len(df)
    kpi1.metric("Volume de Tweets analysés", total_tweets)

    # 2. Nombre de compagnies aériennes
    nb_airlines = df["airline"].nunique()
    kpi2.metric("Compagnies Aériennes", nb_airlines)

    # 3. Pourcentage de tweets négatifs
    if total_tweets > 0:
        pct_negative = (df[df["sentiment"] == "negative"].shape[0] / total_tweets) * 100
        kpi3.metric("Tweets Négatifs", f"{pct_negative:.1f}%", delta_color="inverse")
    
    st.divider()

    # --- PARTIE 2 : VISUALISATIONS GRAPHIQUES ---

    # Ligne 1 : Volume et Sentiments
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Volume de Tweets par Compagnie")
        # Agrégation
        vol_per_airline = df["airline"].value_counts().reset_index()
        vol_per_airline.columns = ["Compagnie", "Nombre de Tweets"]
        
        fig_vol = px.bar(vol_per_airline, x="Compagnie", y="Nombre de Tweets", 
                         color="Compagnie", title="Volume total")
        st.plotly_chart(fig_vol, use_container_width=True)

    with col2:
        st.subheader("2. Répartition des Sentiments")
        # Agrégation croisée
        sentiment_dist = df.groupby(["airline", "sentiment"]).size().reset_index(name="Count")
        
        # Mapping couleur pour respecter la logique (rouge = négatif, vert = positif)
        color_map = {"negative": "#EF553B", "neutral": "#636EFA", "positive": "#00CC96"}
        
        fig_sent = px.bar(sentiment_dist, x="airline", y="Count", color="sentiment", 
                          title="Sentiments par Compagnie",
                          color_discrete_map=color_map, barmode="group")
        st.plotly_chart(fig_sent, use_container_width=True)

    # Ligne 2 : Satisfaction et Causes
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("3. Taux de Satisfaction (%)")
        # Calcul : (Nb Positif / Total Compagnie) * 100
        # On crée un DataFrame pivot
        pivot = pd.crosstab(df["airline"], df["sentiment"], normalize='index') * 100
        if "positive" in pivot.columns:
            satisfaction = pivot["positive"].reset_index()
            satisfaction.columns = ["Compagnie", "Taux Satisfaction"]
            satisfaction = satisfaction.sort_values("Taux Satisfaction", ascending=False)
            
            fig_sat = px.bar(satisfaction, x="Compagnie", y="Taux Satisfaction",
                             color="Taux Satisfaction", range_y=[0, 100],
                             color_continuous_scale="RdYlGn",
                             text_auto='.1f')
            st.plotly_chart(fig_sat, use_container_width=True)
        else:
            st.warning("Pas assez de données positives pour calculer le taux.")

    with col4:
        st.subheader("4. Causes principales d'insatisfaction")
        # On filtre uniquement les tweets négatifs avec une raison renseignée
        negative_df = df[(df["sentiment"] == "negative") & (df["negativereason"].notna())]
        
        if not negative_df.empty:
            reasons = negative_df["negativereason"].value_counts().reset_index().head(5)
            reasons.columns = ["Raison", "Nombre"]
            
            fig_reason = px.pie(reasons, names="Raison", values="Nombre", hole=0.4,
                                title="Top 5 des raisons négatives")
            st.plotly_chart(fig_reason, use_container_width=True)
        else:
            st.info("Aucune raison spécifique identifiée pour l'instant.")

    # --- PARTIE 3 : DONNÉES BRUTES (Optionnel mais pratique) ---
    with st.expander("Voir les données brutes récentes"):
        st.dataframe(df.head(50))

else:
    st.warning("Aucune donnée disponible. Veuillez cliquer sur 'Générer' dans la barre latérale.")