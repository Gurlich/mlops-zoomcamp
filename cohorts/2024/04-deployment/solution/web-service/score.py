#!/usr/bin/env python
# coding: utf-8

import os
import sys
import pickle
import pandas as pd
import numpy as np


taxi_type = sys.argv[1] # 'yellow'
year = int(sys.argv[2]) # 2023
month = int(sys.argv[3]) # 3


with open('model.bin', 'rb') as f_in:
    dv, model = pickle.load(f_in)


def read_dataframe(filename: str):
    df = pd.read_parquet(filename)

    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()
    
    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')
    return df


def prepare_dictionaries(df: pd.DataFrame):
    categorical = ['PULocationID', 'DOLocationID']
    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    
    dicts = df[categorical].to_dict(orient='records')
    return dicts


print('Reading data to predict...')
df = read_dataframe(f'https://d37ci6vzurychx.cloudfront.net/trip-data/{taxi_type}_tripdata_{year:04d}-{month:02d}.parquet')
# df = read_dataframe(f'~/mlops-zoomcamp/data/{taxi_type}_tripdata_{year:04d}-{month:02d}.parquet')

print('Predicting duration...')
dicts = prepare_dictionaries(df)
X_val = dv.transform(dicts)
y_pred = model.predict(X_val)

stnd_dev = np.std(y_pred)
print(f"Standart deviation of the predicted duration: {stnd_dev:.2f}")

mean_duration = np.mean(y_pred)
print(f"Mean predicted duration: {mean_duration:.2f}")

print('Preparing result dataset...')
df_result = pd.DataFrame()
df_result['ride_id'] = df['ride_id']
df_result['predict'] = y_pred


output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)
output_file = f"predict-{year:04d}-{month:02d}.parquet"
file_path = output_dir+'/'+output_file

# save result to a parquet file
print(f'Saving predictions to {output_file} file...')
df_result.to_parquet(
    file_path,
    engine='pyarrow',
    compression=None,
    index=False
)


