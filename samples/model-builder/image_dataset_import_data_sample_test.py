from google.cloud.aiplatform import schema
import google.cloud.aiplatform as aip
import test_constants as constants
import pytest

import image_dataset_import_data_sample


def test_image_dataset_import_data_sample(
    mock_sdk_init, mock_import_data_mock, mock_dataset, mock_init_dataset
):

    image_dataset_import_data_sample.image_dataset_import_data_sample(
        project=constants.PROJECT,
        location=constants.LOCATION,
        src_uris=constants.GCS_SOURCES,
        import_schema_uri=None,
        dataset_id=constants.DATASET_NAME,
    )

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT, location=constants.LOCATION
    )
    mock_import_data_mock.assert_called_once_with(
        gcs_source=constants.GCS_SOURCES, import_schema_uri=None, sync=True
    )
