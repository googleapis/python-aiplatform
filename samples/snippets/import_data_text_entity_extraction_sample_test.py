import pytest
import os

from uuid import uuid4
from google.cloud import aiplatform

import import_data_text_entity_extraction_sample
import delete_dataset_sample

print(
    f"uCAIP Library Source:\t{aiplatform.__file__}"
)  # Package source location sanity check
print(
    f"uCAIP Import Source:\t{import_data_text_entity_extraction_sample.__file__}"
)  # Package source location sanity check

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
LOCATION = "us-central1"
GCS_SOURCE = "gs://ucaip-test-us-central1/dataset/ucaip_ten_dataset.jsonl"
METADATA_SCHEMA_URI = (
    "gs://google-cloud-aiplatform/schema/dataset/metadata/text_1.0.0.yaml"
)


@pytest.fixture(scope="function", autouse=True)
def dataset_name():
    client_options = {"api_endpoint": "us-central1-aiplatform.googleapis.com"}
    client = aiplatform.gapic.DatasetServiceClient(client_options=client_options)

    dataset = aiplatform.gapic.Dataset(
        display_name=f"temp_import_dataset_test_{uuid4()}",
        metadata_schema_uri=METADATA_SCHEMA_URI,
    )

    operation = client.create_dataset(
        parent=f"projects/{PROJECT_ID}/locations/{LOCATION}", dataset=dataset
    )

    created_dataset = operation.result()

    yield created_dataset.name

    dataset_id = created_dataset.name.split("/")[-1]

    # Delete the created dataset
    delete_dataset_sample.delete_dataset_sample(
        project=PROJECT_ID, dataset_id=dataset_id
    )


def test_ucaip_generated_import_data_text_entity_extraction_sample(
    capsys, dataset_name
):
    dataset_id = dataset_name.split("/")[-1]

    import_data_text_entity_extraction_sample.import_data_text_entity_extraction_sample(
        gcs_source_uri=GCS_SOURCE, project=PROJECT_ID, dataset_id=dataset_id
    )

    out, _ = capsys.readouterr()

    assert "import_data_response" in out
