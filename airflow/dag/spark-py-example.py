from datetime import timedelta, datetime
from airflow.operators.python import PythonOperator
from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.now() - timedelta(days=1),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'max_active_runs': 1,
    'retries': 0,
}


def startBatch():
    print('##### startBatch1 #####')

def done():
    print('##### done #####')

with DAG(
    dag_id='spark_pi',
    start_date=datetime.now() - timedelta(days=1),
    default_args=default_args,
    schedule=None,
    tags=['example']
) as dag:
    spark_pi_task = SparkKubernetesOperator(
        task_id='spark_example',
        namespace='spark-jobs',
        application_file='spark-apps/spark-pi.yaml',
        kubernetes_conn_id='kubernetes_default',
        batch_scheduler="yunikorn",
        batch_scheduler_options={"queue": "root.spark-jobs"},  # YuniKorn queue
        conf={
            "spark.kubernetes.namespace": "spark-jobs",
            "spark.kubernetes.driver.serviceAccountName": "spark-operator-spark",
            "spark.kubernetes.executor.serviceAccountName": "spark-operator-spark",
            "spark.kubernetes.driver.label.scheduler.alpha.kubernetes.io/queue": "root.spark-jobs",
            "spark.kubernetes.executor.label.scheduler.alpha.kubernetes.io/queue": "root.spark-jobs"}

    )

    start_batch_task = PythonOperator(
        task_id='startBatch',
        python_callable=startBatch
    )
    done_task = PythonOperator(
        task_id='done',
        python_callable=done
    )


    start_batch_task >> spark_pi_task >> done_task
