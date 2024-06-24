import datetime
import time
import random
import logging 
# import uuid
# import pytz
import pandas as pd
# import io
import psycopg
import joblib
import sys

# from prefect import task, flow

from evidently.report import Report
from evidently import ColumnMapping
from evidently.metrics import ColumnDriftMetric, DatasetDriftMetric, DatasetMissingValuesMetric, ColumnQuantileMetric, ColumnCorrelationsMetric

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

SEND_TIMEOUT = 10
rand = random.Random()

taxi_type = sys.argv[1] # 'green'
year = int(sys.argv[2]) # 2024
month = int(sys.argv[3]) # 3
# reference_data_path = sys.argv[4] # path to reference data 'data/reference.parquet'

create_table_statement = """
drop table if exists nytaxi_metrics;
create table nytaxi_metrics(
	timestamp timestamp,
	prediction_drift float,
	num_drifted_columns integer,
	share_missing_values float,
	pearson_corr_passenger_count float,
	fare_amount_0_5_quantile float
)
"""
# df = read_dataframe(f'~/mlops-zoomcamp/data/{taxi_type}_tripdata_{year:04d}-{month:02d}.parquet')

reference_data = pd.read_parquet('data/hw05_reference.parquet')
with open('models/hw05_lin_reg.bin', 'rb') as f_in:
	model = joblib.load(f_in)

raw_data = pd.read_parquet(f'data/{taxi_type}_tripdata_{year:04d}-{month:02d}.parquet')

begin = datetime.datetime(2024, 3, 1, 0, 0)
num_features = ['passenger_count', 'trip_distance', 'fare_amount', 'total_amount']
cat_features = ['PULocationID', 'DOLocationID']
column_mapping = ColumnMapping(
    prediction='prediction',
    numerical_features=num_features,
    categorical_features=cat_features,
    target=None
)

report = Report(metrics = [
    ColumnDriftMetric(column_name='prediction'),
    DatasetDriftMetric(),
    DatasetMissingValuesMetric(),
	ColumnCorrelationsMetric(column_name="fare_amount"),
    ColumnQuantileMetric(column_name="fare_amount", quantile=0.5),
])

POSTGRES_PASSWORD='password'
POSTGRES_USER='postgres'
METRICS_DB='metrics_db'

# @task
def prep_db():
	with psycopg.connect(f"host=localhost port=5432 user={POSTGRES_USER} password={POSTGRES_PASSWORD}", autocommit=True) as conn:
		res = conn.execute(f"SELECT 1 FROM pg_database WHERE datname='{METRICS_DB}'")
		if len(res.fetchall()) == 0:
			conn.execute(f"create database {METRICS_DB};")
		print(f'DB {METRICS_DB} exits')
		with psycopg.connect(f"host=localhost port=5432 dbname={METRICS_DB} user={POSTGRES_USER} password={POSTGRES_PASSWORD}") as conn:
			conn.execute(create_table_statement)

# @task
def calculate_metrics_postgresql(curr, i):
	current_data = raw_data[(raw_data.lpep_pickup_datetime >= (begin + datetime.timedelta(i))) &
		(raw_data.lpep_pickup_datetime < (begin + datetime.timedelta(i + 1)))]

	#current_data.fillna(0, inplace=True)
	current_data['prediction'] = model.predict(current_data[num_features + cat_features].fillna(0))

	report.run(reference_data = reference_data, current_data = current_data,
		column_mapping=column_mapping)

	result = report.as_dict()

	prediction_drift = result['metrics'][0]['result']['drift_score']
	num_drifted_columns = result['metrics'][1]['result']['number_of_drifted_columns']
	share_missing_values = result['metrics'][2]['result']['current']['share_of_missing_values']
	pearson_corr_passenger_count = result['metrics'][3]['result']['current']['pearson']['values']['y'][0]
	fare_amount_0_5_quantile = result['metrics'][4]['result']['current']['value']

	print(f"Inserting values for day {begin + datetime.timedelta(i)}")
	curr.execute(
		"insert into nytaxi_metrics(timestamp, prediction_drift, num_drifted_columns, share_missing_values, pearson_corr_passenger_count, fare_amount_0_5_quantile) values (%s, %s, %s, %s, %s, %s)",
		(begin + datetime.timedelta(i), prediction_drift, num_drifted_columns, share_missing_values, pearson_corr_passenger_count, fare_amount_0_5_quantile)
	)

# @flow
def batch_monitoring_backfill():
	prep_db()
	last_send = datetime.datetime.now() - datetime.timedelta(seconds=10)
	with psycopg.connect(f"host=localhost port=5432 dbname={METRICS_DB} user={POSTGRES_USER} password={POSTGRES_PASSWORD}", autocommit=True) as conn:
		for i in range(0, 31):
			# print(f"Run day {i+1}")
			with conn.cursor() as curr:
				calculate_metrics_postgresql(curr, i)

			new_send = datetime.datetime.now()
			seconds_elapsed = (new_send - last_send).total_seconds()
			if seconds_elapsed < SEND_TIMEOUT:
				time.sleep(SEND_TIMEOUT - seconds_elapsed)
			while last_send < new_send:
				last_send = last_send + datetime.timedelta(seconds=10)
			logging.info("data sent")

if __name__ == '__main__':
	batch_monitoring_backfill()
