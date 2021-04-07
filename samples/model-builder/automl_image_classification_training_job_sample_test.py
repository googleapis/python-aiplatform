import google.cloud.aiplatform as aip
import test_constants as constants
        
import automl_image_classification_training_job_sample


def test_automl_image_classification_training_job_sample(
        mock_sdk_init, mock_init_dataset, mock_init_automl_image_training_job, mock_run_automl_image_training_job
):
    dataset = aip.Dataset(constants.DATASET_NAME)
    automl_image_classification_training_job_sample.automl_image_classification_training_job_sample(
        project=constants.PROJECT, 
        location=constants.LOCATION, 
        display_name=constants.DISPLAY_NAME,
        dataset=dataset)

    mock_sdk_init.assert_called_once_with(
            project=constants.PROJECT,
            location=constants.LOCATION
    )

    mock_init_automl_image_training_job.assert_called_once_with(
            display_name=constants.DISPLAY_NAME,
            base_model=None,
            model_type="CLOUD",
            multi_label=False,
            prediction_type="classification"
    )

    mock_run_automl_image_training_job.assert_called_once_with(
            budget_milli_node_hours=8000,
            disable_early_stopping=False,
            test_fraction_split=0.2,
            training_fraction_split=0.6,
            validation_fraction_split=0.2,
            model_display_name=constants.DISPLAY_NAME,
            dataset=dataset
    )
