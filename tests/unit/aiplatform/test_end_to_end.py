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
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import models
from google.cloud.aiplatform import schema
from google.cloud.aiplatform import training_jobs

from google.cloud.aiplatform_v1.types import (
    dataset as gca_dataset,
    encryption_spec as gca_encryption_spec,
    io as gca_io,
    model as gca_model,
    pipeline_state as gca_pipeline_state,
    training_pipeline as gca_training_pipeline,
)

import test_datasets
from test_datasets import create_dataset_mock  # noqa: F401
from test_datasets import get_dataset_mock  # noqa: F401
from test_datasets import import_data_mock  # noqa: F401

import test_endpoints
from test_endpoints import create_endpoint_mock  # noqa: F401
from test_endpoints import get_endpoint_mock  # noqa: F401
from test_endpoints import predict_client_predict_mock  # noqa: F401

from test_models import deploy_model_mock  # noqa: F401

import test_training_jobs
from test_training_jobs import mock_model_service_get  # noqa: F401
from test_training_jobs import mock_pipeline_service_create  # noqa: F401
from test_training_jobs import mock_pipeline_service_get  # noqa: F401
from test_training_jobs import (  # noqa: F401
    mock_pipeline_service_create_and_get_with_fail,
)
from test_training_jobs import mock_python_package_to_gcs  # noqa: F401

from google.protobuf import json_format
from google.protobuf import struct_pb2

# dataset_encryption
_TEST_ENCRYPTION_KEY_NAME = "key_1234"
_TEST_ENCRYPTION_SPEC = gca_encryption_spec.EncryptionSpec(
    kms_key_name=_TEST_ENCRYPTION_KEY_NAME
)


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
            project=test_datasets._TEST_PROJECT,
            staging_bucket=test_training_jobs._TEST_BUCKET_NAME,
            credentials=test_training_jobs._TEST_CREDENTIALS,
        )

        my_dataset = aiplatform.ImageDataset.create(
            display_name=test_datasets._TEST_DISPLAY_NAME,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
            sync=sync,
        )

        my_dataset.import_data(
            gcs_source=test_datasets._TEST_SOURCE_URI_GCS,
            import_schema_uri=test_datasets._TEST_IMPORT_SCHEMA_URI,
            data_item_labels=test_datasets._TEST_DATA_LABEL_ITEMS,
            sync=sync,
        )

        job = aiplatform.CustomTrainingJob(
            display_name=test_training_jobs._TEST_DISPLAY_NAME,
            script_path=test_training_jobs._TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=test_training_jobs._TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=test_training_jobs._TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=test_training_jobs._TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=test_training_jobs._TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        model_from_job = job.run(
            dataset=my_dataset,
            base_output_dir=test_training_jobs._TEST_BASE_OUTPUT_DIR,
            args=test_training_jobs._TEST_RUN_ARGS,
            replica_count=1,
            machine_type=test_training_jobs._TEST_MACHINE_TYPE,
            accelerator_type=test_training_jobs._TEST_ACCELERATOR_TYPE,
            accelerator_count=test_training_jobs._TEST_ACCELERATOR_COUNT,
            model_display_name=test_training_jobs._TEST_MODEL_DISPLAY_NAME,
            training_fraction_split=test_training_jobs._TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction_split=test_training_jobs._TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction_split=test_training_jobs._TEST_TEST_FRACTION_SPLIT,
            sync=sync,
        )

        created_endpoint = models.Endpoint.create(
            display_name=test_endpoints._TEST_DISPLAY_NAME,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
            sync=sync,
        )

        my_endpoint = model_from_job.deploy(
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME, sync=sync
        )

        endpoint_deploy_return = created_endpoint.deploy(model_from_job, sync=sync)

        assert endpoint_deploy_return is None

        if not sync:
            my_endpoint.wait()
            created_endpoint.wait()

        test_prediction = created_endpoint.predict(
            instances=[[1.0, 2.0, 3.0], [1.0, 3.0, 4.0]], parameters={"param": 3.0}
        )

        true_prediction = models.Prediction(
            predictions=test_endpoints._TEST_PREDICTION,
            deployed_model_id=test_endpoints._TEST_ID,
        )

        assert true_prediction == test_prediction
        predict_client_predict_mock.assert_called_once_with(
            endpoint=test_endpoints._TEST_ENDPOINT_NAME,
            instances=[[1.0, 2.0, 3.0], [1.0, 3.0, 4.0]],
            parameters={"param": 3.0},
        )

        expected_dataset = gca_dataset.Dataset(
            display_name=test_datasets._TEST_DISPLAY_NAME,
            metadata_schema_uri=test_datasets._TEST_METADATA_SCHEMA_URI_NONTABULAR,
            metadata=test_datasets._TEST_NONTABULAR_DATASET_METADATA,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        expected_import_config = gca_dataset.ImportDataConfig(
            gcs_source=gca_io.GcsSource(uris=[test_datasets._TEST_SOURCE_URI_GCS]),
            import_schema_uri=test_datasets._TEST_IMPORT_SCHEMA_URI,
            data_item_labels=test_datasets._TEST_DATA_LABEL_ITEMS,
        )

        create_dataset_mock.assert_called_once_with(
            parent=test_datasets._TEST_PARENT,
            dataset=expected_dataset,
            metadata=test_datasets._TEST_REQUEST_METADATA,
        )

        import_data_mock.assert_called_once_with(
            name=test_datasets._TEST_NAME, import_configs=[expected_import_config]
        )

        expected_dataset.name = test_datasets._TEST_NAME
        assert my_dataset._gca_resource == expected_dataset

        mock_python_package_to_gcs.assert_called_once_with(
            gcs_staging_dir=test_training_jobs._TEST_BUCKET_NAME,
            project=test_training_jobs._TEST_PROJECT,
            credentials=initializer.global_config.credentials,
        )

        true_args = test_training_jobs._TEST_RUN_ARGS

        true_worker_pool_spec = {
            "replicaCount": test_training_jobs._TEST_REPLICA_COUNT,
            "machineSpec": {
                "machineType": test_training_jobs._TEST_MACHINE_TYPE,
                "acceleratorType": test_training_jobs._TEST_ACCELERATOR_TYPE,
                "acceleratorCount": test_training_jobs._TEST_ACCELERATOR_COUNT,
            },
            "pythonPackageSpec": {
                "executorImageUri": test_training_jobs._TEST_TRAINING_CONTAINER_IMAGE,
                "pythonModule": training_jobs._TrainingScriptPythonPackager.module_name,
                "packageUris": [test_training_jobs._TEST_OUTPUT_PYTHON_PACKAGE_PATH],
                "args": true_args,
            },
        }

        true_fraction_split = gca_training_pipeline.FractionSplit(
            training_fraction=test_training_jobs._TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction=test_training_jobs._TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction=test_training_jobs._TEST_TEST_FRACTION_SPLIT,
        )

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=test_training_jobs._TEST_SERVING_CONTAINER_IMAGE,
            predict_route=test_training_jobs._TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=test_training_jobs._TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        true_managed_model = gca_model.Model(
            display_name=test_training_jobs._TEST_MODEL_DISPLAY_NAME,
            container_spec=true_container_spec,
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            fraction_split=true_fraction_split,
            dataset_id=my_dataset.name,
            gcs_destination=gca_io.GcsDestination(
                output_uri_prefix=test_training_jobs._TEST_BASE_OUTPUT_DIR
            ),
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=test_training_jobs._TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "workerPoolSpecs": [true_worker_pool_spec],
                    "baseOutputDirectory": {
                        "output_uri_prefix": test_training_jobs._TEST_BASE_OUTPUT_DIR
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
        )

        assert job._gca_resource is mock_pipeline_service_get.return_value

        mock_model_service_get.assert_called_once_with(
            name=test_training_jobs._TEST_MODEL_NAME
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
            project=test_datasets._TEST_PROJECT,
            staging_bucket=test_training_jobs._TEST_BUCKET_NAME,
            credentials=test_training_jobs._TEST_CREDENTIALS,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
        )

        my_dataset = aiplatform.ImageDataset.create(
            display_name=test_datasets._TEST_DISPLAY_NAME, sync=sync,
        )

        my_dataset.import_data(
            gcs_source=test_datasets._TEST_SOURCE_URI_GCS,
            import_schema_uri=test_datasets._TEST_IMPORT_SCHEMA_URI,
            data_item_labels=test_datasets._TEST_DATA_LABEL_ITEMS,
            sync=sync,
        )

        job = aiplatform.CustomTrainingJob(
            display_name=test_training_jobs._TEST_DISPLAY_NAME,
            script_path=test_training_jobs._TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=test_training_jobs._TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=test_training_jobs._TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=test_training_jobs._TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=test_training_jobs._TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        created_endpoint = models.Endpoint.create(
            display_name=test_endpoints._TEST_DISPLAY_NAME, sync=sync,
        )

        model_from_job = job.run(
            dataset=my_dataset,
            base_output_dir=test_training_jobs._TEST_BASE_OUTPUT_DIR,
            args=test_training_jobs._TEST_RUN_ARGS,
            replica_count=1,
            machine_type=test_training_jobs._TEST_MACHINE_TYPE,
            accelerator_type=test_training_jobs._TEST_ACCELERATOR_TYPE,
            accelerator_count=test_training_jobs._TEST_ACCELERATOR_COUNT,
            model_display_name=test_training_jobs._TEST_MODEL_DISPLAY_NAME,
            training_fraction_split=test_training_jobs._TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction_split=test_training_jobs._TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction_split=test_training_jobs._TEST_TEST_FRACTION_SPLIT,
            sync=sync,
        )

        with pytest.raises(RuntimeError):
            my_endpoint = model_from_job.deploy(sync=sync)
            my_endpoint.wait()

        with pytest.raises(RuntimeError):
            endpoint_deploy_return = created_endpoint.deploy(model_from_job, sync=sync)
            assert endpoint_deploy_return is None
            created_endpoint.wait()

        expected_dataset = gca_dataset.Dataset(
            display_name=test_datasets._TEST_DISPLAY_NAME,
            metadata_schema_uri=test_datasets._TEST_METADATA_SCHEMA_URI_NONTABULAR,
            metadata=test_datasets._TEST_NONTABULAR_DATASET_METADATA,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        expected_import_config = gca_dataset.ImportDataConfig(
            gcs_source=gca_io.GcsSource(uris=[test_datasets._TEST_SOURCE_URI_GCS]),
            import_schema_uri=test_datasets._TEST_IMPORT_SCHEMA_URI,
            data_item_labels=test_datasets._TEST_DATA_LABEL_ITEMS,
        )

        create_dataset_mock.assert_called_once_with(
            parent=test_datasets._TEST_PARENT,
            dataset=expected_dataset,
            metadata=test_datasets._TEST_REQUEST_METADATA,
        )

        import_data_mock.assert_called_once_with(
            name=test_datasets._TEST_NAME, import_configs=[expected_import_config]
        )

        expected_dataset.name = test_datasets._TEST_NAME
        assert my_dataset._gca_resource == expected_dataset

        mock_python_package_to_gcs.assert_called_once_with(
            gcs_staging_dir=test_training_jobs._TEST_BUCKET_NAME,
            project=test_training_jobs._TEST_PROJECT,
            credentials=initializer.global_config.credentials,
        )

        true_args = test_training_jobs._TEST_RUN_ARGS

        true_worker_pool_spec = {
            "replicaCount": test_training_jobs._TEST_REPLICA_COUNT,
            "machineSpec": {
                "machineType": test_training_jobs._TEST_MACHINE_TYPE,
                "acceleratorType": test_training_jobs._TEST_ACCELERATOR_TYPE,
                "acceleratorCount": test_training_jobs._TEST_ACCELERATOR_COUNT,
            },
            "pythonPackageSpec": {
                "executorImageUri": test_training_jobs._TEST_TRAINING_CONTAINER_IMAGE,
                "pythonModule": training_jobs._TrainingScriptPythonPackager.module_name,
                "packageUris": [test_training_jobs._TEST_OUTPUT_PYTHON_PACKAGE_PATH],
                "args": true_args,
            },
        }

        true_fraction_split = gca_training_pipeline.FractionSplit(
            training_fraction=test_training_jobs._TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction=test_training_jobs._TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction=test_training_jobs._TEST_TEST_FRACTION_SPLIT,
        )

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=test_training_jobs._TEST_SERVING_CONTAINER_IMAGE,
            predict_route=test_training_jobs._TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=test_training_jobs._TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        true_managed_model = gca_model.Model(
            display_name=test_training_jobs._TEST_MODEL_DISPLAY_NAME,
            container_spec=true_container_spec,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            fraction_split=true_fraction_split,
            dataset_id=my_dataset.name,
            gcs_destination=gca_io.GcsDestination(
                output_uri_prefix=test_training_jobs._TEST_BASE_OUTPUT_DIR
            ),
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=test_training_jobs._TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "workerPoolSpecs": [true_worker_pool_spec],
                    "baseOutputDirectory": {
                        "output_uri_prefix": test_training_jobs._TEST_BASE_OUTPUT_DIR
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
