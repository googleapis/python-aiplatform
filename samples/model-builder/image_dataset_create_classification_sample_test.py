from google.cloud.aiplatform import schema
from conftest import mock_sdk_init, mock_create_image_dataset
import test_constants as constants
        
import image_dataset_create_classification_sample


def test_image_dataset_create_classification_sample(
    mock_sdk_init, mock_create_image_dataset
):
    image_dataset_create_classification_sample.image_dataset_create_classification_sample(
        project=constants.PROJECT, 
        location=constants.LOCATION, 
        src_uris=constants.GCS_SOURCES,
        display_name=constants.DISPLAY_NAME
    )

    mock_sdk_init.assert_called_once_with(
            project=constants.PROJECT,
            location=constants.LOCATION
    )
    mock_create_image_dataset.assert_called_once_with(
            display_name=constants.DISPLAY_NAME,
            gcs_source=constants.GCS_SOURCES,
            import_schema_uri=schema.dataset.ioformat.image.single_label_classification
    )
