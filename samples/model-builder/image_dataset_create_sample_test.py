from google.cloud.aiplatform import schema
from conftest import mock_sdk_init, mock_create_image_dataset
import test_constants as constants

import image_dataset_create_sample


def test_image_dataset_create_sample(mock_sdk_init, mock_create_image_dataset):
    image_dataset_create_sample.image_dataset_create_sample(
        project=constants.PROJECT,
        location=constants.LOCATION,
        display_name=constants.DISPLAY_NAME,
    )

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT, location=constants.LOCATION
    )
    mock_create_image_dataset.assert_called_once_with(
        display_name=constants.DISPLAY_NAME
    )
