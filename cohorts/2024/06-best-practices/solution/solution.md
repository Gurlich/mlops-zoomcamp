# Solution

## Q1

Change `batch.py` file

* add `main` function, and all previous code moved in, except `read_data` function
* add `if` block, to invoke script when file run

## Q2

* install `pytest` with pipenv
* create `tests` dir
* create `__init__.py` file inside the dir
* configure VScode to work with the dir

## Q3

* create `test_batch.py` file inside `tests` dir
* prepare expected dataframe after `prepare_data` function
* drope indexes

## Q4

* installing aws command line

```bash
sudo apt update

sudo apt install awscli
```

aws required `requests==2.29 urllib3==1.26`, these versions does not conflict. So reinstall python packages in core OS

```bash
pip install requests==2.29 urllib3==1.26
```

* Then copy `docker-compose.yaml` from course, add servise `s3` and run only kinesis

```bash
docker compose up kinesis
```

---

* Next with AWS CLI create a bucket:

```bash
aws --endpoint-url=http://localhost:4566 s3 mb s3://nyc-duration
```

check that the bucket was successfully created

```bash
aws --endpoint-url=http://localhost:4566 s3 ls
```

## Q5

Creating file `integration_test.py` to save synthetic prepared data from Q3 to localstack s3. This synthetic data save as January 2022

```python
input_file = "s3://nyc-duration/in/2022-01.parquet"
```

## Q6

Change `batch.py` file

* Adding check wich file we want to read (local or from s3) in `read_data` function

* Creating `save_data` function in `batch.py`.

Running `batch.py` on synthetic data from Q5.

Getting predicted durations sum from localstack s3 output file on synthetic data.

```bash
python batch.py 2022 01

python check_df_Q6.py
```

## Other tips

### Creating kinesis stream

* create `nyc-duration` stream

```bash
aws --endpoint-url=http://localhost:4566 \
    kinesis create-stream \
    --stream-name nyc-duration \
    --shard-count 1
```

* check the stream

```bash
aws --endpoint-url=http://localhost:4566 \
    kinesis list-streams
```

```bash
aws  --endpoint-url=http://localhost:4566 \
    kinesis     get-shard-iterator \
    --shard-id shardId-000000000000 \
    --shard-iterator-type TRIM_HORIZON \
    --stream-name nyc-duration \
    --query 'ShardIterator'
```

### Building and running Docker images

```bash
docker build -t 06-homework:v1 .
```

Running image and passing parameters for 2023 March dataset.

Note: Symlink folders does not pass into a container, use hardlinks to files.

```bash
docker run -it --rm \
    -p 8080:8080 \
    -v $(pwd)/data:/data \
    -v $(pwd)/output:/output \
    06-homework:v1 \
    2023 3
```