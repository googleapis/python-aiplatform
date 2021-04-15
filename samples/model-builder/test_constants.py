# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from random import randint
from uuid import uuid4

from google.auth import credentials

PROJECT = "abc"
LOCATION = "us-central1"
LOCATION_EUROPE = "europe-west4"
LOCATION_ASIA = "asia-east1"
PARENT = f"projects/{PROJECT}/locations/{LOCATION}"

DISPLAY_NAME = str(uuid4())  # Create random display name
DISPLAY_NAME_2 = str(uuid4())

STAGING_BUCKET = "gs://my-staging-bucket"
EXPERIMENT_NAME = "fraud-detection-trial-72"
CREDENTIALS = credentials.AnonymousCredentials()

RESOURCE_ID = str(randint(10000000, 99999999))  # Create random resource ID
RESOURCE_ID_2 = str(randint(10000000, 99999999))

BATCH_PREDICTION_JOB_NAME = f"{PARENT}/batchPredictionJobs/{RESOURCE_ID}"
DATASET_NAME = f"{PARENT}/datasets/{RESOURCE_ID}"
ENDPOINT_NAME = f"{PARENT}/endpoints/{RESOURCE_ID}"
MODEL_NAME = f"{PARENT}/models/{RESOURCE_ID}"
TRAINING_JOB_NAME = f"{PARENT}/trainingJobs/{RESOURCE_ID}"

BIGQUERY_SOURCE = F"bq://{PROJECT}.{DATASET_NAME}.table1"

GCS_SOURCES = ["gs://bucket1/source1.jsonl", "gs://bucket7/source4.jsonl"]
GCS_DESTINATION = "gs://bucket3/output-dir/"

TABULAR_REGRESSION_OPTIMIZATION_PREDICTION_TYPE = 'regression'
TABULAR_CLASSIFICATION_OPTIMIZATOIN_PREDICTION_TYPE = 'classification'

TRAINING_FRACTION_SPLIT = 0.7
TEST_FRACTION_SPLIT = 0.15
VALIDATION_FRACTION_SPLIT = 0.15

BUDGET_MILLI_NODE_HOURS_8000 = 8000

ENCRYPTION_SPEC_KEY_NAME = f"{PARENT}/keyRings/{RESOURCE_ID}/cryptoKeys/{RESOURCE_ID_2}"

PREDICTION_TEXT_INSTANCE = "This is some text for testing NLP prediction output"

PREDICTION_TABULAR_CLASSIFICATION_INSTANCE = [
    {
        "petal_length": "1.4",
        "petal_width": "1.3",
        "sepal_length": "5.1",
        "sepal_width": "2.8",
    }
]
PREDICTION_TABULAR_REGRESSOIN_INSTANCE = [
    {
        "BOOLEAN_2unique_NULLABLE": False,
        "DATETIME_1unique_NULLABLE": "2019-01-01 00:00:00",
        "DATE_1unique_NULLABLE": "2019-01-01",
        "FLOAT_5000unique_NULLABLE": 1611,
        "FLOAT_5000unique_REPEATED": [2320, 1192],
        "INTEGER_5000unique_NULLABLE": "8",
        "NUMERIC_5000unique_NULLABLE": 16,
        "STRING_5000unique_NULLABLE": "str-2",
        "STRUCT_NULLABLE": {
            "BOOLEAN_2unique_NULLABLE": False,
            "DATE_1unique_NULLABLE": "2019-01-01",
            "DATETIME_1unique_NULLABLE": "2019-01-01 00:00:00",
            "FLOAT_5000unique_NULLABLE": 1308,
            "FLOAT_5000unique_REPEATED": [2323, 1178],
            "FLOAT_5000unique_REQUIRED": 3089,
            "INTEGER_5000unique_NULLABLE": "1777",
            "NUMERIC_5000unique_NULLABLE": 3323,
            "TIME_1unique_NULLABLE": "23:59:59.999999",
            "STRING_5000unique_NULLABLE": "str-49",
            "TIMESTAMP_1unique_NULLABLE": "1546387199999999",
        },
        "TIMESTAMP_1unique_NULLABLE": "1546387199999999",
        "TIME_1unique_NULLABLE": "23:59:59.999999",
    }
]
