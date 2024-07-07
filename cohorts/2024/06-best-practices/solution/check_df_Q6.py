import pandas as pd
import os

S3_ENDPOINT_URL = "http://localhost:4566"

options = {
    'client_kwargs': {
        'endpoint_url': S3_ENDPOINT_URL
    }
}

filename = 's3://nyc-duration/out/2022-01.parquet'
df = pd.read_parquet(filename, storage_options=options)

print(f'Predicted durations sum: {df["predicted_duration"].sum():.2f}')
