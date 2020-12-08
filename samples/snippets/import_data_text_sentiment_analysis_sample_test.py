import os
from uuid import uuid4

from google.cloud import aiplatform
import pytest

import import_data_text_sentiment_analysis_sample

print(
    f"uCAIP Library Source:\t{aiplatform.__file__}"
)  # Package source location sanity check
print(
    f"uCAIP Import Source:\t{import_data_text_sentiment_analysis_sample.__file__}"
)  # Package source location sanity check

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
LOCATION = "us-central1"
GCS_SOURCE = "gs://ucaip-test-us-central1/dataset/ucaip_tst_dataset_10.csv"
METADATA_SCHEMA_URI = (
    "gs://google-cloud-aiplatform/schema/dataset/metadata/text_1.0.0.yaml"
)


@pytest.fixture(scope="function", autouse=True)
def setup(shared_state, dataset_client):
    dataset = aiplatform.gapic.Dataset(
        display_name=f"temp_import_dataset_test_{uuid4()}",
        metadata_schema_uri=METADATA_SCHEMA_URI,
    )

    operation = dataset_client.create_dataset(
        parent=f"projects/{PROJECT_ID}/locations/{LOCATION}", dataset=dataset
    )

    dataset = operation.result(timeout=300)
    shared_state["dataset_name"] = dataset.name

    yield


@pytest.fixture(scope="function", autouse=True)
def teardown(teardown_dataset):
    yield


def test_ucaip_generated_import_data_text_sentiment_analysis_sample(
    capsys, shared_state
):
    dataset_id = shared_state["dataset_name"].split("/")[-1]

    import_data_text_sentiment_analysis_sample.import_data_text_sentiment_analysis_sample(
        gcs_source_uri=GCS_SOURCE, project=PROJECT_ID, dataset_id=dataset_id
    )

    out, _ = capsys.readouterr()

    assert "import_data_response" in out
