import google.cloud.aiplatform as aip
import test_constants as constants
        
import custom_training_job_sample


def test_custom_training_job_sample(
        mock_sdk_init, mock_init_custom_training_job, mock_run_custom_training_job
):
    custom_training_job_sample.custom_training_job_sample(
        project=constants.PROJECT, 
        location=constants.LOCATION, 
        bucket=constants.STAGING_BUCKET,
        display_name=constants.DISPLAY_NAME,
        script_path=constants.PYTHON_PACKAGE,
        script_args=constants.PYTHON_PACKAGE_CMDARGS,
        train_image=constants.TRAIN_IMAGE,
        deploy_image=constants.DEPLOY_IMAGE,
        requirements="",
        replica_count=1)

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT,
        location=constants.LOCATION,
        staging_bucket=constants.STAGING_BUCKET
    )

    mock_init_custom_training_job.assert_called_once_with(
        display_name=constants.DISPLAY_NAME,
        container_uri=constants.TRAIN_IMAGE,
        model_serving_container_image_uri=constants.DEPLOY_IMAGE,
        requirements='',
        script_path=constants.PYTHON_PACKAGE
    )

    mock_run_custom_training_job.assert_called_once()