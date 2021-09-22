# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime
import os

import batch_read_feature_values_sample
from google.cloud import bigquery

import pytest

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
LOCATION = "us-central1"
INPUT_CSV_FILE = "gs://cloud-samples-data-us-central1/vertex-ai/feature-store/datasets/movie_prediction_perm.csv"


@pytest.fixture(scope="function", autouse=True)
def teardown(teardown_batch_read_feature_values):
    yield


def setup_test():
    # Output dataset
    destination_data_set = "movie_predictions_" + datetime.now().strftime(
        "%Y%m%d%H%M%S"
    )
    # Output table. Make sure that the table does NOT already exist, the
    # BatchReadFeatureValues API cannot overwrite an existing table.
    destination_table_name = "training_data"
    DESTINATION_PATTERN = "bq://{project}.{dataset}.{table}"
    destination_table_uri = DESTINATION_PATTERN.format(
        project=PROJECT_ID, dataset=destination_data_set, table=destination_table_name
    )
    # Create dataset
    bq_client = bigquery.Client(project=PROJECT_ID)
    dataset_id = "{}.{}".format(bq_client.project, destination_data_set)
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = LOCATION
    dataset = bq_client.create_dataset(dataset)
    print("Created dataset {}.{}".format(bq_client.project, dataset.dataset_id))
    return destination_data_set, destination_table_uri


def test_ucaip_generated_batch_read_feature_values_sample_vision(capsys, shared_state):
    destination_data_set, destination_table_uri = setup_test()
    featurestore_id = "perm_sample_featurestore"

    batch_read_feature_values_sample.batch_read_feature_values_sample(
        project=PROJECT_ID,
        featurestore_id=featurestore_id,
        input_csv_file=INPUT_CSV_FILE,
        destination_table_uri=destination_table_uri,
    )
    out, _ = capsys.readouterr()
    assert "batch_read_feature_values_response" in out
    with capsys.disabled():
        print(out)

    shared_state["destination_data_set"] = destination_data_set
