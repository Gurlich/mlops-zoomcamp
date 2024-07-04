import pandas as pd
from datetime import datetime

import batch

def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)

def test_prepare_data():
    
    data = [
    (None, None, dt(1, 1), dt(1, 10)),
    (1, 1, dt(1, 2), dt(1, 10)),
    (1, None, dt(1, 2, 0), dt(1, 2, 59)),
    (3, 4, dt(1, 2, 0), dt(2, 2, 1)),      
]

    columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']
    df = pd.DataFrame(data, columns=columns)


    expected_data =[
        (-1, -1, 1672534860000000000, 1672535400000000000, 9.0),
        (1, 1, 1672534920000000000, 1672535400000000000, 8.0),
    ]
    expected_columns = ['PULocationID', 
                        'DOLocationID', 
                        'tpep_pickup_datetime', 
                        'tpep_dropoff_datetime', 
                        'duration']
    expected_response = pd.DataFrame(expected_data, columns=expected_columns)
    expected_response[columns] = expected_response[columns].astype('str')
    actual_response = batch.prepare_data(df, columns)


    assert expected_response.equals(actual_response)
