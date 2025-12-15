# AeroStream
AeroStream développe un système de classification automatique des avis clients en temps réel basé sur le NLP et le machine learning, en s’appuyant sur Hugging Face, Sentence Transformers, ChromaDB, PostgreSQL, Streamlit et Airflow pour l’analyse, le stockage, la visualisation et l’orchestration des données.

```bash
AeroStream/
│
│
├── airflow/
│   ├── dags.py     # Fichier contenant le dag pour orchestration airflow
│
├── app/
│   ├── app.py              # Interface Stremlit
│
├── chroma_db/              # Base de données vectorielle (Dossier généré par Chroma)
│   ├── chroma.sqlite3
│   └── ... (autres dossiers bizarres)
│
├── data/                   # Dossiers contenant les Dataset après chaque étape puisque je travaille avec des notebooks 
│   └── raw/
│   └── clean/
│   └── processed/
│
├── metadata/              # Dossiers contenant les metadatas après la génération des embeddings
│   └── test.pkl
│   └── train.pkl
│
├── models/
│   └── model.pkl           # Modèle MLP entrainé
│
├── notebboks/              # contient tous les notebooks ipynb
│   └── 01_preparing.ipynb
│   └── 02_analyzing.ipynb
│   └── ...
│   └── 06_training.ipynb
│   └── utils/
│       └── functions.py    # fonctions utiles pour évaluer les modèles entraînés
│
├── fastapi/
│
├── logs/
│
├── test/
│   └── examples.pkl        # exemples des tweets à classifier pour tester le modèle dans streamlit
│
├── README.md
│
└── .gitignore
```
