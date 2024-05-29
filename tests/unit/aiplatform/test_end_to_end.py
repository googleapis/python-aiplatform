# -*- coding: utf-8 -*-

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
#

import pytest

from importlib import reload

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import models
from google.cloud.aiplatform import schema

from google.cloud.aiplatform.compat.types import (
    dataset as gca_dataset,
    io as gca_io,
    model as gca_model,
    pipeline_state as gca_pipeline_state,
    training_pipeline as gca_training_pipeline,
)

import constants as test_constants

from google.protobuf import json_format
from google.protobuf import struct_pb2


# Training job test variables
_TEST_CREDENTIALS = test_constants.TrainingJobConstants._TEST_CREDENTIALS
_TEST_JOB_DISPLAY_NAME = "test-display-name"
_TEST_SERVING_CONTAINER_IMAGE = (
    test_constants.TrainingJobConstants._TEST_TRAINING_CONTAINER_IMAGE
)
_TEST_SERVING_CONTAINER_PREDICTION_ROUTE = (
    test_constants.TrainingJobConstants._TEST_SERVING_CONTAINER_PREDICTION_ROUTE
)
_TEST_SERVING_CONTAINER_HEALTH_ROUTE = (
    test_constants.TrainingJobConstants._TEST_SERVING_CONTAINER_HEALTH_ROUTE
)
_TEST_BASE_OUTPUT_DIR = "gs://test-base-output-dir"
_TEST_MACHINE_TYPE = test_constants.TrainingJobConstants._TEST_MACHINE_TYPE
_TEST_ACCELERATOR_TYPE = test_constants.TrainingJobConstants._TEST_ACCELERATOR_TYPE
_TEST_MODEL_DISPLAY_NAME = test_constants.TrainingJobConstants._TEST_MODEL_DISPLAY_NAME
_TEST_TRAINING_FRACTION_SPLIT = (
    test_constants.TrainingJobConstants._TEST_TRAINING_FRACTION_SPLIT
)
_TEST_VALIDATION_FRACTION_SPLIT = (
    test_constants.TrainingJobConstants._TEST_VALIDATION_FRACTION_SPLIT
)
_TEST_TEST_FRACTION_SPLIT = (
    test_constants.TrainingJobConstants._TEST_TEST_FRACTION_SPLIT
)
_TEST_BOOT_DISK_TYPE_DEFAULT = (
    test_constants.TrainingJobConstants._TEST_BOOT_DISK_TYPE_DEFAULT
)
_TEST_BOOT_DISK_SIZE_GB_DEFAULT = (
    test_constants.TrainingJobConstants._TEST_BOOT_DISK_SIZE_GB_DEFAULT
)


# Dataset test variables
_TEST_DATA_LABEL_ITEMS = test_constants.DatasetConstants._TEST_DATA_LABEL_ITEMS
_TEST_IMPORT_SCHEMA_URI = test_constants.DatasetConstants._TEST_IMPORT_SCHEMA_URI
_TEST_IMPORT_SCHEMA_URI_IMAGE = (
    test_constants.DatasetConstants._TEST_IMPORT_SCHEMA_URI_IMAGE
)
_TEST_REQUEST_METADATA = test_constants.DatasetConstants._TEST_REQUEST_METADATA
_TEST_NAME = test_constants.DatasetConstants._TEST_NAME
_TEST_SOURCE_URI_GCS = test_constants.DatasetConstants._TEST_SOURCE_URI_GCS
_TEST_ENCRYPTION_KEY_NAME = test_constants.ProjectConstants._TEST_ENCRYPTION_KEY_NAME
_TEST_ENCRYPTION_SPEC = test_constants.ProjectConstants._TEST_ENCRYPTION_SPEC


def make_training_pipeline(state, add_training_task_metadata=True):
    return gca_training_pipeline.TrainingPipeline(
        name=test_constants.TrainingJobConstants._TEST_PIPELINE_RESOURCE_NAME,
        state=state,
        model_to_upload=gca_model.Model(
            name=test_constants.TrainingJobConstants._TEST_MODEL_NAME
        ),
        training_task_inputs={
            "tensorboard": test_constants.TrainingJobConstants._TEST_TENSORBOARD_RESOURCE_NAME
        },
        training_task_metadata={
            "backingCustomJob": test_constants.TrainingJobConstants._TEST_CUSTOM_JOB_RESOURCE_NAME
        }
        if add_training_task_metadata
        else None,
    )


@pytest.mark.usefixtures("google_auth_mock")
class TestEndToEnd:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @pytest.mark.usefixtures(
        "get_dataset_mock",
        "create_endpoint_mock",
        "get_endpoint_mock",
        "deploy_model_mock",
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_dataset_create_to_model_predict(
        self,
        create_dataset_mock,  # noqa: F811
        import_data_mock,  # noqa: F811
        predict_client_predict_mock,  # noqa: F811
        mock_python_package_to_gcs,  # noqa: F811
        mock_pipeline_service_create,  # noqa: F811
        mock_model_service_get,  # noqa: F811
        mock_pipeline_service_get,  # noqa: F811
        sync,
    ):

        aiplatform.init(
            project=test_constants.ProjectConstants._TEST_PROJECT,
            staging_bucket=test_constants.TrainingJobConstants._TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        my_dataset = aiplatform.ImageDataset.create(
            display_name=test_constants.DatasetConstants._TEST_DISPLAY_NAME,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
            sync=sync,
            create_request_timeout=None,
        )

        my_dataset.import_data(
            gcs_source=_TEST_SOURCE_URI_GCS,
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI,
            data_item_labels=_TEST_DATA_LABEL_ITEMS,
            sync=sync,
            import_request_timeout=None,
        )

        job = aiplatform.CustomTrainingJob(
            display_name=_TEST_JOB_DISPLAY_NAME,
            script_path=test_constants.TrainingJobConstants._TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=test_constants.TrainingJobConstants._TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        model_from_job = job.run(
            dataset=my_dataset,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=test_constants.TrainingJobConstants._TEST_RUN_ARGS,
            replica_count=1,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=test_constants.TrainingJobConstants._TEST_ACCELERATOR_TYPE,
            accelerator_count=test_constants.TrainingJobConstants._TEST_ACCELERATOR_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
            sync=sync,
            create_request_timeout=None,
        )

        created_endpoint = models.Endpoint.create(
            display_name=test_constants.EndpointConstants._TEST_DISPLAY_NAME,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
            sync=sync,
            create_request_timeout=None,
        )

        my_endpoint = model_from_job.deploy(
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
            sync=sync,
            deploy_request_timeout=None,
        )

        endpoint_deploy_return = created_endpoint.deploy(model_from_job, sync=sync)

        assert endpoint_deploy_return is None

        if not sync:
            # Accessing attribute in Endpoint that has not been created raises informatively
            with pytest.raises(
                RuntimeError, match=r"Endpoint resource has not been created."
            ):
                my_endpoint.network

            my_endpoint.wait()
            created_endpoint.wait()

        test_prediction = created_endpoint.predict(
            instances=[[1.0, 2.0, 3.0], [1.0, 3.0, 4.0]], parameters={"param": 3.0}
        )

        true_prediction = models.Prediction(
            predictions=test_constants.EndpointConstants._TEST_PREDICTION,
            deployed_model_id=test_constants.EndpointConstants._TEST_ID,
            model_resource_name=model_from_job.resource_name,
            model_version_id=model_from_job.version_id,
        )

        assert true_prediction == test_prediction
        predict_client_predict_mock.assert_called_once_with(
            endpoint=test_constants.EndpointConstants._TEST_ENDPOINT_NAME,
            instances=[[1.0, 2.0, 3.0], [1.0, 3.0, 4.0]],
            parameters={"param": 3.0},
            timeout=None,
        )

        expected_dataset = gca_dataset.Dataset(
            display_name=test_constants.DatasetConstants._TEST_DISPLAY_NAME,
            metadata_schema_uri=test_constants.DatasetConstants._TEST_METADATA_SCHEMA_URI_NONTABULAR,
            metadata=test_constants.DatasetConstants._TEST_NONTABULAR_DATASET_METADATA,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        expected_import_config = gca_dataset.ImportDataConfig(
            gcs_source=gca_io.GcsSource(uris=[_TEST_SOURCE_URI_GCS]),
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI,
            data_item_labels=_TEST_DATA_LABEL_ITEMS,
        )

        create_dataset_mock.assert_called_once_with(
            parent=test_constants.ProjectConstants._TEST_PARENT,
            dataset=expected_dataset,
            metadata=_TEST_REQUEST_METADATA,
            timeout=None,
        )

        import_data_mock.assert_called_once_with(
            name=_TEST_NAME,
            import_configs=[expected_import_config],
            timeout=None,
        )

        expected_dataset.name = _TEST_NAME
        assert my_dataset._gca_resource == expected_dataset

        mock_python_package_to_gcs.assert_called_once_with(
            gcs_staging_dir=test_constants.TrainingJobConstants._TEST_BUCKET_NAME,
            project=test_constants.ProjectConstants._TEST_PROJECT,
            credentials=initializer.global_config.credentials,
        )

        true_args = test_constants.TrainingJobConstants._TEST_RUN_ARGS

        true_worker_pool_spec = {
            "replica_count": test_constants.TrainingJobConstants._TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE,
                "accelerator_type": _TEST_ACCELERATOR_TYPE,
                "accelerator_count": test_constants.TrainingJobConstants._TEST_ACCELERATOR_COUNT,
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "python_package_spec": {
                "executor_image_uri": test_constants.TrainingJobConstants._TEST_TRAINING_CONTAINER_IMAGE,
                "python_module": test_constants.TrainingJobConstants._TEST_MODULE_NAME,
                "package_uris": [
                    test_constants.TrainingJobConstants._TEST_OUTPUT_PYTHON_PACKAGE_PATH
                ],
                "args": true_args,
            },
        }

        true_fraction_split = gca_training_pipeline.FractionSplit(
            training_fraction=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction=_TEST_TEST_FRACTION_SPLIT,
        )

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            container_spec=true_container_spec,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            fraction_split=true_fraction_split,
            dataset_id=my_dataset.name,
            gcs_destination=gca_io.GcsDestination(
                output_uri_prefix=_TEST_BASE_OUTPUT_DIR
            ),
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_JOB_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

        assert job._gca_resource == make_training_pipeline(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

        mock_model_service_get.assert_called_once_with(
            name=test_constants.TrainingJobConstants._TEST_MODEL_NAME,
            retry=base._DEFAULT_RETRY,
        )

        assert model_from_job._gca_resource is mock_model_service_get.return_value

        assert job.get_model()._gca_resource is mock_model_service_get.return_value

        assert not job.has_failed

        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED

    @pytest.mark.usefixtures(
        "get_dataset_mock",
        "create_endpoint_mock",
        "get_endpoint_mock",
        "deploy_model_mock",
    )
    def test_dataset_create_to_model_predict_with_pipeline_fail(
        self,
        create_dataset_mock,  # noqa: F811
        import_data_mock,  # noqa: F811
        mock_python_package_to_gcs,  # noqa: F811
        mock_pipeline_service_create_and_get_with_fail,  # noqa: F811
        mock_model_service_get,  # noqa: F811
    ):

        sync = False

        aiplatform.init(
            project=test_constants.ProjectConstants._TEST_PROJECT,
            staging_bucket=test_constants.TrainingJobConstants._TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
        )

        my_dataset = aiplatform.ImageDataset.create(
            display_name=test_constants.DatasetConstants._TEST_DISPLAY_NAME,
            sync=sync,
            create_request_timeout=None,
        )

        my_dataset.import_data(
            gcs_source=_TEST_SOURCE_URI_GCS,
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI,
            data_item_labels=_TEST_DATA_LABEL_ITEMS,
            sync=sync,
            import_request_timeout=None,
        )

        job = aiplatform.CustomTrainingJob(
            display_name=_TEST_JOB_DISPLAY_NAME,
            script_path=test_constants.TrainingJobConstants._TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=test_constants.TrainingJobConstants._TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        created_endpoint = models.Endpoint.create(
            display_name=test_constants.EndpointConstants._TEST_DISPLAY_NAME,
            sync=sync,
            create_request_timeout=None,
        )

        model_from_job = job.run(
            dataset=my_dataset,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=test_constants.TrainingJobConstants._TEST_RUN_ARGS,
            replica_count=1,
            machine_type=test_constants.TrainingJobConstants._TEST_MACHINE_TYPE,
            accelerator_type=test_constants.TrainingJobConstants._TEST_ACCELERATOR_TYPE,
            accelerator_count=test_constants.TrainingJobConstants._TEST_ACCELERATOR_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
            sync=sync,
            create_request_timeout=None,
        )

        with pytest.raises(RuntimeError):
            my_endpoint = model_from_job.deploy(sync=sync)
            my_endpoint.wait()

        with pytest.raises(RuntimeError):
            endpoint_deploy_return = created_endpoint.deploy(model_from_job, sync=sync)
            assert endpoint_deploy_return is None
            created_endpoint.wait()

        expected_dataset = gca_dataset.Dataset(
            display_name=test_constants.DatasetConstants._TEST_DISPLAY_NAME,
            metadata_schema_uri=test_constants.DatasetConstants._TEST_METADATA_SCHEMA_URI_NONTABULAR,
            metadata=test_constants.DatasetConstants._TEST_NONTABULAR_DATASET_METADATA,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        expected_import_config = gca_dataset.ImportDataConfig(
            gcs_source=gca_io.GcsSource(uris=[_TEST_SOURCE_URI_GCS]),
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI,
            data_item_labels=_TEST_DATA_LABEL_ITEMS,
        )

        create_dataset_mock.assert_called_once_with(
            parent=test_constants.ProjectConstants._TEST_PARENT,
            dataset=expected_dataset,
            metadata=_TEST_REQUEST_METADATA,
            timeout=None,
        )

        import_data_mock.assert_called_once_with(
            name=_TEST_NAME,
            import_configs=[expected_import_config],
            timeout=None,
        )

        expected_dataset.name = _TEST_NAME
        assert my_dataset._gca_resource == expected_dataset

        mock_python_package_to_gcs.assert_called_once_with(
            gcs_staging_dir=test_constants.TrainingJobConstants._TEST_BUCKET_NAME,
            project=test_constants.ProjectConstants._TEST_PROJECT,
            credentials=initializer.global_config.credentials,
        )

        true_args = test_constants.TrainingJobConstants._TEST_RUN_ARGS

        true_worker_pool_spec = {
            "replica_count": test_constants.TrainingJobConstants._TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": test_constants.TrainingJobConstants._TEST_MACHINE_TYPE,
                "accelerator_type": test_constants.TrainingJobConstants._TEST_ACCELERATOR_TYPE,
                "accelerator_count": test_constants.TrainingJobConstants._TEST_ACCELERATOR_COUNT,
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "python_package_spec": {
                "executor_image_uri": test_constants.TrainingJobConstants._TEST_TRAINING_CONTAINER_IMAGE,
                "python_module": test_constants.TrainingJobConstants._TEST_MODULE_NAME,
                "package_uris": [
                    test_constants.TrainingJobConstants._TEST_OUTPUT_PYTHON_PACKAGE_PATH
                ],
                "args": true_args,
            },
        }

        true_fraction_split = gca_training_pipeline.FractionSplit(
            training_fraction=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction=_TEST_TEST_FRACTION_SPLIT,
        )

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            container_spec=true_container_spec,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            fraction_split=true_fraction_split,
            dataset_id=my_dataset.name,
            gcs_destination=gca_io.GcsDestination(
                output_uri_prefix=_TEST_BASE_OUTPUT_DIR
            ),
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_JOB_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create_and_get_with_fail[0].assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

        assert (
            job._gca_resource
            is mock_pipeline_service_create_and_get_with_fail[1].return_value
        )

        mock_model_service_get.assert_not_called()

        with pytest.raises(RuntimeError):
            job.get_model()

        assert job.has_failed

        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_FAILED
