from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Arguments par défaut pour le DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Définition du DAG
with DAG(
    dag_id='aerostream_pipeline_test',
    default_args=default_args,
    description='Un DAG de test pour vérifier la connexion Airflow -> FastAPI',
    start_date=datetime(2023, 1, 1),
    schedule_interval='@daily',
    catchup=False,
) as dag:

    # Tâche 1 : Juste un echo pour dire que ça commence
    start_task = BashOperator(
        task_id='start_pipeline',
        bash_command='echo "Démarrage du pipeline AeroStream..."'
    )

    # Tâche 2 : Vérifier que l'API est en ligne (GET /)
    # Utilise la connexion définie dans docker-compose : AIRFLOW_CONN_FASTAPI_CONN
    check_api_health = SimpleHttpOperator(
        task_id='check_api_health',
        http_conn_id='fastapi_conn',  # L'ID de connexion
        endpoint='/',                 # La route à appeler
        method='GET',
        response_check=lambda response: response.status_code == 200,
        log_response=True
    )

    # Tâche 3 : Simuler un déclenchement d'entraînement (Pour l'instant juste un log)
    end_task = BashOperator(
        task_id='end_pipeline',
        bash_command='echo "Pipeline terminé avec succès."'
    )

    # Ordonnancement des tâches
    start_task >> check_api_health >> end_task