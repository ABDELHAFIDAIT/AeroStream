from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import json



default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 12, 20),
    'retries': 1,
    'retry_delay': timedelta(seconds=10),
}




API_URL = "http://fastapi:8000"




# Vérifie si l'API FastAPI est en ligne avant de lancer le job
def check_api_health():
    try:
        response = requests.get(f"{API_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("API FastAPI est accessible.")
        else:
            raise Exception(f"API répond avec le code : {response.status_code}")
    except requests.exceptions.ConnectionError:
        raise Exception("Impossible de se connecter à l'API. Le conteneur 'fastapi' est-il lancé ?")





# Appeler l'endpoint de /batch pour la génération, prédiction et stockage des tweets
def trigger_batch_process():
    # On demande 10 tweets par minute
    params = {"batch_size": 10}
    endpoint = f"{API_URL}/batch"
    
    print(f"Appel de l'endpoint : {endpoint}")
    
    response = requests.post(endpoint, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Succès ! Pipeline terminé.")
        print(f"Résultats : {json.dumps(data, indent=2)}")
    else:
        raise Exception(f"Erreur lors du traitement : {response.text}")



# Définition du DAG
with DAG(
    'aerostream_orchestrator',
    default_args=default_args,
    description='Pipeline MLOps AeroStream : Simulation & Prédiction',
    schedule_interval=None, #'*/1 * * * *'
    catchup=False,
) as dag:

    # Tâche 1 : Healthcheck
    task_check = PythonOperator(
        task_id='check_api_status',
        python_callable=check_api_health,
    )

    # Tâche 2 : Exécution du Pipeline
    task_run = PythonOperator(
        task_id='trigger_ml_pipeline',
        python_callable=trigger_batch_process,
    )

    # Ordre des tâches
    task_check >> task_run