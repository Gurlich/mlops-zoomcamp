# .
# mlflow, version 2.3.1

# export MLFLOW_TRACKING_URI=postgresql://testadmin:test123@localhost:5432/mlflow_db

# --default-artifact-root /home/gurlich/mlops-zoomcamp/ml_artifacts

# mlflow db upgrade postgresql://testadmin:test123@localhost:5432/mlflow_db

# mlflow server --backend-store-uri postgresql://testadmin:test123@localhost:5432/mlflow_db \
#               --default-artifact-root /home/gurlich/mlops-zoomcamp/ml_artifacts

# python preprocess_data.py --raw_data_path ~/mlops-zoomcamp/data --dest_path ~/mlops-zoomcamp/cohorts/2024/02-experiment-tracking/homework/output




# docker compose up -d
# docker compose down

# mlflow server --backend-store-uri $MLFLOW_TRACKING_URI \
#               --default-artifact-root /home/gurlich/mlops-zoomcamp/ml_artifacts
from sklearn.ensemble import RandomForestRegressor

pol = {}

pol['sss'] = 1

print(pol)

rf = RandomForestRegressor()
print(rf.__class__.__name__)


# так делать не надо, название модели идет в переменной estimator_name
# log model name 
# mlflow.set_tag("model", f"{rf.__class__.__name__}")