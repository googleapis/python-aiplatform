# Copyright 2020 Google LLC
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

from uuid import uuid4

import pytest

from samples import create_dataset_tables_bigquery_sample
from samples import delete_dataset_sample


PROJECT_ID = "ucaip-sample-tests"
DATASET_NAME = None
BIGQUERY_URI = "bq://ucaip-sample-tests.table_test.all_bq_types"


@pytest.fixture(scope="function", autouse=True)
def teardown():
    yield

    assert DATASET_NAME is not None

    dataset_id = DATASET_NAME.split("/")[-1]

    # Delete the created dataset
    delete_dataset_sample.delete_dataset_sample(
        project=PROJECT_ID, dataset_id=dataset_id
    )


def test_ucaip_generated_create_dataset_tables_bigquery(capsys):
    create_dataset_tables_bigquery_sample.create_dataset_tables_bigquery_sample(
        display_name=f"temp_create_dataset_test_{uuid4()}", 
        bigquery_uri=BIGQUERY_URI, 
        project=PROJECT_ID
    )
    out, _ = capsys.readouterr()
    assert "create_dataset_response" in out

    global DATASET_NAME
    DATASET_NAME = out.split("name:")[1].split("\n")[0]
