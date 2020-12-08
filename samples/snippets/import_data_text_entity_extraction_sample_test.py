import os

import pytest

import import_data_text_entity_extraction_sample


PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
LOCATION = "us-central1"
GCS_SOURCE = "gs://ucaip-test-us-central1/dataset/ucaip_ten_dataset.jsonl"
METADATA_SCHEMA_URI = (
    "gs://google-cloud-aiplatform/schema/dataset/metadata/text_1.0.0.yaml"
)


@pytest.fixture(scope="function", autouse=True)
def setup(create_dataset):
    create_dataset(PROJECT_ID, LOCATION, METADATA_SCHEMA_URI)
    yield


@pytest.fixture(scope="function", autouse=True)
def teardown(teardown_dataset):
    yield


def test_ucaip_generated_import_data_text_entity_extraction_sample(
    capsys, shared_state
):
    dataset_id = shared_state["dataset_name"].split("/")[-1]

    import_data_text_entity_extraction_sample.import_data_text_entity_extraction_sample(
        gcs_source_uri=GCS_SOURCE, project=PROJECT_ID, dataset_id=dataset_id
    )

    out, _ = capsys.readouterr()

    assert "import_data_response" in out
