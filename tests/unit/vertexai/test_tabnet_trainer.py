# -*- coding: utf-8 -*-
# Copyright 2023 Google LLC
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

from importlib import reload
import os
import re
from unittest.mock import Mock

from google.cloud import aiplatform
from google.cloud.aiplatform.compat.types import (
    custom_job as gca_custom_job_compat,
)
from google.cloud.aiplatform.compat.types import io as gca_io_compat
from vertexai.preview._workflow.executor import (
    remote_container_training,
)
from vertexai.preview.tabular_models import (
    tabnet_trainer,
)
from vertexai.preview._workflow.shared import configs
import pandas as pd
import pytest
import tensorflow as tf

_TEST_STAGING_BUCKET = "gs://test_staging_bucket"
_TEST_JOB_DIR = "gs://test_job_dir"
_TEST_TARGET_COLUMN = "target"
_TEST_MODEL_TYPE_CLASSIFICATION = "classification"
_TEST_MODEL_TYPE_REGRESSION = "regression"
_TEST_LEARNING_RATE = 0.01
_TEST_DATA = pd.DataFrame(data={"col_0": [0, 1], "col_1": [2, 3]})
_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_DISPLAY_NAME = "test"
_TEST_MACHINE_TYPE = "n1-highmem-8"
_TEST_ACCELERATOR_COUNT = 8
_TEST_ACCELERATOR_TYPE = "NVIDIA_TESLA_K80"
_TEST_BOOT_DISK_TYPE = "test_boot_disk_type"
_TEST_BOOT_DISK_SIZE_GB = 10


class TestTabNetTrainer:
    def setup_method(self):
        reload(aiplatform.initializer)
        reload(aiplatform)

    @pytest.mark.usefixtures(
        "google_auth_mock",
        "mock_uuid",
        "mock_get_custom_job_succeeded",
        "mock_blob_upload_from_filename",
    )
    def test_tabnet_trainer_default(
        self,
        mock_create_custom_job,
        mock_blob_download_to_filename,
        mock_tf_saved_model_load,
    ):
        test_tabnet_trainer = tabnet_trainer.TabNetTrainer(
            model_type=_TEST_MODEL_TYPE_CLASSIFICATION,
            target_column=_TEST_TARGET_COLUMN,
            learning_rate=_TEST_LEARNING_RATE,
        )
        test_tabnet_trainer.fit.vertex.remote_config.staging_bucket = (
            _TEST_STAGING_BUCKET
        )
        expected_binding = {
            "model_type": _TEST_MODEL_TYPE_CLASSIFICATION,
            "target_column": _TEST_TARGET_COLUMN,
            "learning_rate": _TEST_LEARNING_RATE,
            "enable_profiler": False,
            "job_dir": "",
            "cache_data": "auto",
            "seed": 1,
            "large_category_dim": 1,
            "large_category_thresh": 300,
            "yeo_johnson_transform": False,
            "weight_column": "",
            "max_steps": -1,
            "max_train_secs": -1,
            "measurement_selection_type": "BEST_MEASUREMENT",
            "optimization_metric": "",
            "eval_steps": 0,
            "batch_size": 100,
            "eval_frequency_secs": 600,
            "feature_dim": 64,
            "feature_dim_ratio": 0.5,
            "num_decision_steps": 6,
            "relaxation_factor": 1.5,
            "decay_every": 100.0,
            "decay_rate": 0.95,
            "gradient_thresh": 2000.0,
            "sparsity_loss_weight": 0.00001,
            "batch_momentum": 0.95,
            "batch_size_ratio": 0.25,
            "num_transformer_layers": 4,
            "num_transformer_layers_ratio": 0.25,
            "class_weight": 1.0,
            "loss_function_type": "default",
            "alpha_focal_loss": 0.25,
            "gamma_focal_loss": 2.0,
            "is_remote_trainer": True,
        }
        assert test_tabnet_trainer._binding == expected_binding

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        test_tabnet_trainer.fit(training_data=_TEST_DATA, validation_data=_TEST_DATA)

        expected_display_name = "TabNetTrainer-fit"
        expected_job_dir = os.path.join(_TEST_STAGING_BUCKET, "custom_job")
        expected_args = [
            f"--model_type={_TEST_MODEL_TYPE_CLASSIFICATION}",
            f"--target_column={_TEST_TARGET_COLUMN}",
            f"--learning_rate={_TEST_LEARNING_RATE}",
            f"--job_dir={expected_job_dir}",
            "--enable_profiler=False",
            "--cache_data=auto",
            "--seed=1",
            "--large_category_dim=1",
            "--large_category_thresh=300",
            "--yeo_johnson_transform=False",
            "--weight_column=",
            "--max_steps=-1",
            "--max_train_secs=-1",
            "--measurement_selection_type=BEST_MEASUREMENT",
            "--optimization_metric=",
            "--eval_steps=0",
            "--batch_size=100",
            "--eval_frequency_secs=600",
            "--feature_dim=64",
            "--feature_dim_ratio=0.5",
            "--num_decision_steps=6",
            "--relaxation_factor=1.5",
            "--decay_every=100.0",
            "--decay_rate=0.95",
            "--gradient_thresh=2000.0",
            "--sparsity_loss_weight=1e-05",
            "--batch_momentum=0.95",
            "--batch_size_ratio=0.25",
            "--num_transformer_layers=4",
            "--num_transformer_layers_ratio=0.25",
            "--class_weight=1.0",
            "--loss_function_type=default",
            "--alpha_focal_loss=0.25",
            "--gamma_focal_loss=2.0",
            "--is_remote_trainer=True",
            f"--training_data_path={_TEST_STAGING_BUCKET}/input/training_data_path",
            f"--validation_data_path={_TEST_STAGING_BUCKET}/input/validation_data_path",
            f"--output_model_path={_TEST_STAGING_BUCKET}/output/output_model_path",
        ]
        expected_worker_pool_specs = [
            {
                "replica_count": 1,
                "machine_spec": {
                    "machine_type": "c2-standard-16",
                    "accelerator_type": remote_container_training._DEFAULT_ACCELERATOR_TYPE,
                    "accelerator_count": remote_container_training._DEFAULT_ACCELERATOR_COUNT,
                },
                "disk_spec": {
                    "boot_disk_type": "pd-ssd",
                    "boot_disk_size_gb": 100,
                },
                "container_spec": {
                    "image_uri": tabnet_trainer._TABNET_TRAINING_IMAGE,
                    "args": [],
                },
            }
        ]
        expected_custom_job = gca_custom_job_compat.CustomJob(
            display_name=f"{expected_display_name}-0",
            job_spec=gca_custom_job_compat.CustomJobSpec(
                worker_pool_specs=expected_worker_pool_specs,
                base_output_directory=gca_io_compat.GcsDestination(
                    output_uri_prefix=os.path.join(_TEST_STAGING_BUCKET, "custom_job"),
                ),
            ),
        )
        mock_create_custom_job.assert_called_once()

        assert (
            mock_create_custom_job.call_args[1]["parent"]
            == f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
        )
        assert not mock_create_custom_job.call_args[1]["timeout"]
        test_custom_job = mock_create_custom_job.call_args[1]["custom_job"]

        test_args = test_custom_job.job_spec.worker_pool_specs[0].container_spec.args
        assert set(test_args) == set(expected_args)

        test_custom_job.job_spec.worker_pool_specs[0].container_spec.args = []
        assert test_custom_job == expected_custom_job

        mock_blob_download_to_filename.assert_called_once()
        mock_tf_saved_model_load.assert_called_once()

    @pytest.mark.usefixtures(
        "google_auth_mock",
        "mock_uuid",
        "mock_get_custom_job_succeeded",
        "mock_blob_upload_from_filename",
    )
    def test_tabnet_trainer_all_args(
        self,
        mock_create_custom_job,
        mock_blob_download_to_filename,
        mock_tf_saved_model_load,
    ):
        test_tabnet_trainer = tabnet_trainer.TabNetTrainer(
            model_type=_TEST_MODEL_TYPE_CLASSIFICATION,
            target_column=_TEST_TARGET_COLUMN,
            learning_rate=_TEST_LEARNING_RATE,
            job_dir=_TEST_JOB_DIR,
            enable_profiler=True,
            cache_data="test",
            seed=2,
            large_category_dim=2,
            large_category_thresh=10,
            yeo_johnson_transform=True,
            weight_column="weight",
            max_steps=5,
            max_train_secs=600,
            measurement_selection_type="LAST_MEASUREMENT",
            optimization_metric="rmse",
            eval_steps=1,
            batch_size=10,
            eval_frequency_secs=60,
            feature_dim=8,
            feature_dim_ratio=0.1,
            num_decision_steps=3,
            relaxation_factor=1.2,
            decay_every=10.0,
            decay_rate=0.9,
            gradient_thresh=200.0,
            sparsity_loss_weight=0.01,
            batch_momentum=0.9,
            batch_size_ratio=0.2,
            num_transformer_layers=2,
            num_transformer_layers_ratio=0.2,
            class_weight=1.2,
            loss_function_type="rmse",
            alpha_focal_loss=0.2,
            gamma_focal_loss=2.5,
        )
        expected_binding = {
            "model_type": _TEST_MODEL_TYPE_CLASSIFICATION,
            "target_column": _TEST_TARGET_COLUMN,
            "learning_rate": _TEST_LEARNING_RATE,
            "job_dir": _TEST_JOB_DIR,
            "enable_profiler": True,
            "cache_data": "test",
            "seed": 2,
            "large_category_dim": 2,
            "large_category_thresh": 10,
            "yeo_johnson_transform": True,
            "weight_column": "weight",
            "max_steps": 5,
            "max_train_secs": 600,
            "measurement_selection_type": "LAST_MEASUREMENT",
            "optimization_metric": "rmse",
            "eval_steps": 1,
            "batch_size": 10,
            "eval_frequency_secs": 60,
            "feature_dim": 8,
            "feature_dim_ratio": 0.1,
            "num_decision_steps": 3,
            "relaxation_factor": 1.2,
            "decay_every": 10.0,
            "decay_rate": 0.9,
            "gradient_thresh": 200.0,
            "sparsity_loss_weight": 0.01,
            "batch_momentum": 0.9,
            "batch_size_ratio": 0.2,
            "num_transformer_layers": 2,
            "num_transformer_layers_ratio": 0.2,
            "class_weight": 1.2,
            "loss_function_type": "rmse",
            "alpha_focal_loss": 0.2,
            "gamma_focal_loss": 2.5,
            "is_remote_trainer": True,
        }
        assert test_tabnet_trainer._binding == expected_binding

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        test_tabnet_trainer.fit.vertex.remote_config.staging_bucket = (
            _TEST_STAGING_BUCKET
        )
        test_tabnet_trainer.fit.vertex.remote_config.machine_type = _TEST_MACHINE_TYPE
        test_tabnet_trainer.fit.vertex.remote_config.display_name = _TEST_DISPLAY_NAME
        (
            test_tabnet_trainer.fit.vertex.remote_config.boot_disk_type
        ) = _TEST_BOOT_DISK_TYPE
        (
            test_tabnet_trainer.fit.vertex.remote_config.boot_disk_size_gb
        ) = _TEST_BOOT_DISK_SIZE_GB
        (
            test_tabnet_trainer.fit.vertex.remote_config.accelerator_type
        ) = _TEST_ACCELERATOR_TYPE
        (
            test_tabnet_trainer.fit.vertex.remote_config.accelerator_count
        ) = _TEST_ACCELERATOR_COUNT
        test_tabnet_trainer.fit(training_data=_TEST_DATA, validation_data=_TEST_DATA)

        expected_display_name = "TabNetTrainer-test"
        expected_args = [
            f"--model_type={_TEST_MODEL_TYPE_CLASSIFICATION}",
            f"--target_column={_TEST_TARGET_COLUMN}",
            f"--learning_rate={_TEST_LEARNING_RATE}",
            f"--job_dir={_TEST_JOB_DIR}",
            "--enable_profiler=True",
            "--cache_data=test",
            "--seed=2",
            "--large_category_dim=2",
            "--large_category_thresh=10",
            "--yeo_johnson_transform=True",
            "--weight_column=weight",
            "--max_steps=5",
            "--max_train_secs=600",
            "--measurement_selection_type=LAST_MEASUREMENT",
            "--optimization_metric=rmse",
            "--eval_steps=1",
            "--batch_size=10",
            "--eval_frequency_secs=60",
            "--feature_dim=8",
            "--feature_dim_ratio=0.1",
            "--num_decision_steps=3",
            "--relaxation_factor=1.2",
            "--decay_every=10.0",
            "--decay_rate=0.9",
            "--gradient_thresh=200.0",
            "--sparsity_loss_weight=0.01",
            "--batch_momentum=0.9",
            "--batch_size_ratio=0.2",
            "--num_transformer_layers=2",
            "--num_transformer_layers_ratio=0.2",
            "--class_weight=1.2",
            "--loss_function_type=rmse",
            "--alpha_focal_loss=0.2",
            "--gamma_focal_loss=2.5",
            "--is_remote_trainer=True",
            f"--training_data_path={_TEST_STAGING_BUCKET}/input/training_data_path",
            f"--validation_data_path={_TEST_STAGING_BUCKET}/input/validation_data_path",
            f"--output_model_path={_TEST_STAGING_BUCKET}/output/output_model_path",
        ]
        expected_worker_pool_specs = [
            {
                "replica_count": 1,
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                    "accelerator_type": _TEST_ACCELERATOR_TYPE,
                    "accelerator_count": _TEST_ACCELERATOR_COUNT,
                },
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB,
                },
                "container_spec": {
                    "image_uri": tabnet_trainer._TABNET_TRAINING_IMAGE,
                    "args": [],
                },
            }
        ]
        expected_custom_job = gca_custom_job_compat.CustomJob(
            display_name=f"{expected_display_name}-0",
            job_spec=gca_custom_job_compat.CustomJobSpec(
                worker_pool_specs=expected_worker_pool_specs,
                base_output_directory=gca_io_compat.GcsDestination(
                    output_uri_prefix=os.path.join(_TEST_STAGING_BUCKET, "custom_job"),
                ),
            ),
        )
        mock_create_custom_job.assert_called_once()

        assert (
            mock_create_custom_job.call_args[1]["parent"]
            == f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
        )
        assert not mock_create_custom_job.call_args[1]["timeout"]
        test_custom_job = mock_create_custom_job.call_args[1]["custom_job"]

        test_args = test_custom_job.job_spec.worker_pool_specs[0].container_spec.args
        assert set(test_args) == set(expected_args)

        test_custom_job.job_spec.worker_pool_specs[0].container_spec.args = []
        assert test_custom_job == expected_custom_job

        mock_blob_download_to_filename.assert_called_once()
        mock_tf_saved_model_load.assert_called_once()

    @pytest.mark.usefixtures(
        "google_auth_mock",
        "mock_uuid",
        "mock_get_custom_job_succeeded",
        "mock_blob_upload_from_filename",
    )
    def test_tabnet_trainer_all_args_with_set_config_method(
        self,
        mock_create_custom_job,
        mock_blob_download_to_filename,
        mock_tf_saved_model_load,
    ):
        test_tabnet_trainer = tabnet_trainer.TabNetTrainer(
            model_type=_TEST_MODEL_TYPE_CLASSIFICATION,
            target_column=_TEST_TARGET_COLUMN,
            learning_rate=_TEST_LEARNING_RATE,
            job_dir=_TEST_JOB_DIR,
            enable_profiler=True,
            cache_data="test",
            seed=2,
            large_category_dim=2,
            large_category_thresh=10,
            yeo_johnson_transform=True,
            weight_column="weight",
            max_steps=5,
            max_train_secs=600,
            measurement_selection_type="LAST_MEASUREMENT",
            optimization_metric="rmse",
            eval_steps=1,
            batch_size=10,
            eval_frequency_secs=60,
            feature_dim=8,
            feature_dim_ratio=0.1,
            num_decision_steps=3,
            relaxation_factor=1.2,
            decay_every=10.0,
            decay_rate=0.9,
            gradient_thresh=200.0,
            sparsity_loss_weight=0.01,
            batch_momentum=0.9,
            batch_size_ratio=0.2,
            num_transformer_layers=2,
            num_transformer_layers_ratio=0.2,
            class_weight=1.2,
            loss_function_type="rmse",
            alpha_focal_loss=0.2,
            gamma_focal_loss=2.5,
        )
        expected_binding = {
            "model_type": _TEST_MODEL_TYPE_CLASSIFICATION,
            "target_column": _TEST_TARGET_COLUMN,
            "learning_rate": _TEST_LEARNING_RATE,
            "job_dir": _TEST_JOB_DIR,
            "enable_profiler": True,
            "cache_data": "test",
            "seed": 2,
            "large_category_dim": 2,
            "large_category_thresh": 10,
            "yeo_johnson_transform": True,
            "weight_column": "weight",
            "max_steps": 5,
            "max_train_secs": 600,
            "measurement_selection_type": "LAST_MEASUREMENT",
            "optimization_metric": "rmse",
            "eval_steps": 1,
            "batch_size": 10,
            "eval_frequency_secs": 60,
            "feature_dim": 8,
            "feature_dim_ratio": 0.1,
            "num_decision_steps": 3,
            "relaxation_factor": 1.2,
            "decay_every": 10.0,
            "decay_rate": 0.9,
            "gradient_thresh": 200.0,
            "sparsity_loss_weight": 0.01,
            "batch_momentum": 0.9,
            "batch_size_ratio": 0.2,
            "num_transformer_layers": 2,
            "num_transformer_layers_ratio": 0.2,
            "class_weight": 1.2,
            "loss_function_type": "rmse",
            "alpha_focal_loss": 0.2,
            "gamma_focal_loss": 2.5,
            "is_remote_trainer": True,
        }
        assert test_tabnet_trainer._binding == expected_binding

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

        test_tabnet_trainer.fit.vertex.set_config(
            staging_bucket=_TEST_STAGING_BUCKET,
            machine_type=_TEST_MACHINE_TYPE,
            display_name=_TEST_DISPLAY_NAME,
            boot_disk_type=_TEST_BOOT_DISK_TYPE,
            boot_disk_size_gb=_TEST_BOOT_DISK_SIZE_GB,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
        )

        assert isinstance(
            test_tabnet_trainer.fit.vertex.remote_config,
            configs.DistributedTrainingConfig,
        )

        test_tabnet_trainer.fit(training_data=_TEST_DATA, validation_data=_TEST_DATA)

        expected_display_name = "TabNetTrainer-test"
        expected_args = [
            f"--model_type={_TEST_MODEL_TYPE_CLASSIFICATION}",
            f"--target_column={_TEST_TARGET_COLUMN}",
            f"--learning_rate={_TEST_LEARNING_RATE}",
            f"--job_dir={_TEST_JOB_DIR}",
            "--enable_profiler=True",
            "--cache_data=test",
            "--seed=2",
            "--large_category_dim=2",
            "--large_category_thresh=10",
            "--yeo_johnson_transform=True",
            "--weight_column=weight",
            "--max_steps=5",
            "--max_train_secs=600",
            "--measurement_selection_type=LAST_MEASUREMENT",
            "--optimization_metric=rmse",
            "--eval_steps=1",
            "--batch_size=10",
            "--eval_frequency_secs=60",
            "--feature_dim=8",
            "--feature_dim_ratio=0.1",
            "--num_decision_steps=3",
            "--relaxation_factor=1.2",
            "--decay_every=10.0",
            "--decay_rate=0.9",
            "--gradient_thresh=200.0",
            "--sparsity_loss_weight=0.01",
            "--batch_momentum=0.9",
            "--batch_size_ratio=0.2",
            "--num_transformer_layers=2",
            "--num_transformer_layers_ratio=0.2",
            "--class_weight=1.2",
            "--loss_function_type=rmse",
            "--alpha_focal_loss=0.2",
            "--gamma_focal_loss=2.5",
            "--is_remote_trainer=True",
            f"--training_data_path={_TEST_STAGING_BUCKET}/input/training_data_path",
            f"--validation_data_path={_TEST_STAGING_BUCKET}/input/validation_data_path",
            f"--output_model_path={_TEST_STAGING_BUCKET}/output/output_model_path",
        ]
        expected_worker_pool_specs = [
            {
                "replica_count": 1,
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                    "accelerator_type": _TEST_ACCELERATOR_TYPE,
                    "accelerator_count": _TEST_ACCELERATOR_COUNT,
                },
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB,
                },
                "container_spec": {
                    "image_uri": tabnet_trainer._TABNET_TRAINING_IMAGE,
                    "args": [],
                },
            }
        ]
        expected_custom_job = gca_custom_job_compat.CustomJob(
            display_name=f"{expected_display_name}-0",
            job_spec=gca_custom_job_compat.CustomJobSpec(
                worker_pool_specs=expected_worker_pool_specs,
                base_output_directory=gca_io_compat.GcsDestination(
                    output_uri_prefix=os.path.join(_TEST_STAGING_BUCKET, "custom_job"),
                ),
            ),
        )
        mock_create_custom_job.assert_called_once()

        assert (
            mock_create_custom_job.call_args[1]["parent"]
            == f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
        )
        assert not mock_create_custom_job.call_args[1]["timeout"]
        test_custom_job = mock_create_custom_job.call_args[1]["custom_job"]

        test_args = test_custom_job.job_spec.worker_pool_specs[0].container_spec.args
        assert set(test_args) == set(expected_args)

        test_custom_job.job_spec.worker_pool_specs[0].container_spec.args = []
        assert test_custom_job == expected_custom_job

        mock_blob_download_to_filename.assert_called_once()
        mock_tf_saved_model_load.assert_called_once()

    def test_tabnet_trainer_predict_classification(self):
        test_col_0 = [1.0, 3.0, 5.0]
        test_col_1 = [2, 4, 6]
        test_col_cat = [0, 1, 0]

        test_tabnet_trainer = tabnet_trainer.TabNetTrainer(
            model_type=_TEST_MODEL_TYPE_CLASSIFICATION,
            target_column=_TEST_TARGET_COLUMN,
            learning_rate=_TEST_LEARNING_RATE,
        )
        test_tabnet_trainer.model = Mock()
        mock_serving_default = Mock()
        mock_serving_default.return_value = {
            "scores": tf.constant([[0.1, 0.9], [0.8, 0.2], [0.4, 0.6]]),
            "classes": tf.constant([[0, 1], [0, 1], [0, 1]]),
        }
        expected_predict_results = pd.DataFrame({_TEST_TARGET_COLUMN: [1, 0, 1]})
        test_tabnet_trainer.model.signatures = {"serving_default": mock_serving_default}
        test_data = pd.DataFrame(
            {"col_0": test_col_0, "col_1": test_col_1, "col_cat": test_col_cat}
        )
        test_data["col_cat"] = test_data["col_cat"].astype("category")
        test_predict_results = test_tabnet_trainer.predict(test_data)
        assert test_predict_results.equals(expected_predict_results)

        mock_serving_default.assert_called_once()

        assert not mock_serving_default.call_args[0]
        assert list(mock_serving_default.call_args[1].keys()) == [
            "col_0",
            "col_1",
            "col_cat",
        ]

        expected_input_col_0 = tf.constant(test_col_0, dtype=tf.float64)
        assert (
            tf.equal(mock_serving_default.call_args[1]["col_0"], expected_input_col_0)
            .numpy()
            .all()
        )
        expected_input_col_1 = tf.constant(test_col_1, dtype=tf.int64)
        assert (
            tf.equal(mock_serving_default.call_args[1]["col_1"], expected_input_col_1)
            .numpy()
            .all()
        )
        expected_input_col_cat = tf.constant(test_col_cat, dtype=tf.int64)
        assert (
            tf.equal(
                mock_serving_default.call_args[1]["col_cat"], expected_input_col_cat
            )
            .numpy()
            .all()
        )

    def test_tabnet_trainer_predict_regression(self):
        test_col_0 = [1.0, 3.0, 5.0]
        test_col_1 = [2, 4, 6]
        test_col_cat = [0, 1, 0]

        test_tabnet_trainer = tabnet_trainer.TabNetTrainer(
            model_type=_TEST_MODEL_TYPE_REGRESSION,
            target_column=_TEST_TARGET_COLUMN,
            learning_rate=_TEST_LEARNING_RATE,
        )
        test_tabnet_trainer.model = Mock()
        mock_serving_default = Mock()
        mock_serving_default.return_value = {
            "value": tf.constant([[0.1], [0.2], [0.3]], dtype=tf.float64)
        }
        expected_predict_results = pd.DataFrame({_TEST_TARGET_COLUMN: [0.1, 0.2, 0.3]})
        test_tabnet_trainer.model.signatures = {"serving_default": mock_serving_default}
        test_data = pd.DataFrame(
            {"col_0": test_col_0, "col_1": test_col_1, "col_cat": test_col_cat}
        )
        test_data["col_cat"] = test_data["col_cat"].astype("category")
        test_predict_results = test_tabnet_trainer.predict(test_data)
        assert test_predict_results.equals(expected_predict_results)

        mock_serving_default.assert_called_once()

        assert not mock_serving_default.call_args[0]
        assert list(mock_serving_default.call_args[1].keys()) == [
            "col_0",
            "col_1",
            "col_cat",
        ]

        expected_input_col_0 = tf.constant(test_col_0, dtype=tf.float64)
        assert (
            tf.equal(mock_serving_default.call_args[1]["col_0"], expected_input_col_0)
            .numpy()
            .all()
        )
        expected_input_col_1 = tf.constant(test_col_1, dtype=tf.int64)
        assert (
            tf.equal(mock_serving_default.call_args[1]["col_1"], expected_input_col_1)
            .numpy()
            .all()
        )
        expected_input_col_cat = tf.constant(test_col_cat, dtype=tf.int64)
        assert (
            tf.equal(
                mock_serving_default.call_args[1]["col_cat"], expected_input_col_cat
            )
            .numpy()
            .all()
        )

    def test_tabnet_trainer_predict_load_model(self, mock_tf_saved_model_load):
        test_col_0 = [1.0, 3.0, 5.0]
        test_col_1 = [2, 4, 6]
        test_col_cat = [0, 1, 0]

        test_tabnet_trainer = tabnet_trainer.TabNetTrainer(
            model_type=_TEST_MODEL_TYPE_CLASSIFICATION,
            target_column=_TEST_TARGET_COLUMN,
            learning_rate=_TEST_LEARNING_RATE,
        )
        test_tabnet_trainer.output_model_path = (
            f"{_TEST_STAGING_BUCKET}/output/output_model_path"
        )
        mock_serving_default = Mock()
        mock_serving_default.return_value = {
            "scores": tf.constant([[0.1, 0.9], [0.8, 0.2], [0.4, 0.6]]),
            "classes": tf.constant([[0, 1], [0, 1], [0, 1]]),
        }
        expected_predict_results = pd.DataFrame({_TEST_TARGET_COLUMN: [1, 0, 1]})
        mock_tf_saved_model_load.return_value.signatures = {
            "serving_default": mock_serving_default
        }
        test_data = pd.DataFrame(
            {"col_0": test_col_0, "col_1": test_col_1, "col_cat": test_col_cat}
        )
        test_data["col_cat"] = test_data["col_cat"].astype("category")
        test_predict_results = test_tabnet_trainer.predict(test_data)
        assert test_predict_results.equals(expected_predict_results)

        mock_tf_saved_model_load.assert_called_once_with(
            test_tabnet_trainer.output_model_path
        )
        mock_serving_default.assert_called_once()

        assert not mock_serving_default.call_args[0]
        assert list(mock_serving_default.call_args[1].keys()) == [
            "col_0",
            "col_1",
            "col_cat",
        ]

        expected_input_col_0 = tf.constant(test_col_0, dtype=tf.float64)
        assert (
            tf.equal(mock_serving_default.call_args[1]["col_0"], expected_input_col_0)
            .numpy()
            .all()
        )
        expected_input_col_1 = tf.constant(test_col_1, dtype=tf.int64)
        assert (
            tf.equal(mock_serving_default.call_args[1]["col_1"], expected_input_col_1)
            .numpy()
            .all()
        )
        expected_input_col_cat = tf.constant(test_col_cat, dtype=tf.int64)
        assert (
            tf.equal(
                mock_serving_default.call_args[1]["col_cat"], expected_input_col_cat
            )
            .numpy()
            .all()
        )

    def test_tabnet_trainer_predict_no_trained_model(self):
        test_tabnet_trainer = tabnet_trainer.TabNetTrainer(
            model_type=_TEST_MODEL_TYPE_CLASSIFICATION,
            target_column=_TEST_TARGET_COLUMN,
            learning_rate=_TEST_LEARNING_RATE,
        )
        err_msg = re.escape("No trained model. Please call .fit first.")
        with pytest.raises(ValueError, match=err_msg):
            test_tabnet_trainer.predict(pd.DataFrame())

        self.output_model_path = None
        with pytest.raises(ValueError, match=err_msg):
            test_tabnet_trainer.predict(pd.DataFrame())

    def test_tabnet_trainer_predict_invalid_model_type(self):
        test_invalid_model_type = "invalid"
        test_tabnet_trainer = tabnet_trainer.TabNetTrainer(
            model_type=test_invalid_model_type,
            target_column=_TEST_TARGET_COLUMN,
            learning_rate=_TEST_LEARNING_RATE,
        )
        test_tabnet_trainer.model = Mock()
        test_tabnet_trainer.model.signatures = {"serving_default": Mock()}
        err_msg = f"Unsupported model type: {test_invalid_model_type}"
        with pytest.raises(ValueError, match=err_msg):
            test_tabnet_trainer.predict(pd.DataFrame())

    def test_tabnet_trainer_invalid_gcs_path(self):
        test_invalid_path = "invalid_gcs_path"
        err_msg = re.escape(
            f"Invalid GCS path {test_invalid_path}. Please provide a valid GCS path starting with 'gs://'"
        )
        with pytest.raises(ValueError, match=err_msg):
            tabnet_trainer.TabNetTrainer(
                model_type=_TEST_MODEL_TYPE_CLASSIFICATION,
                target_column=_TEST_TARGET_COLUMN,
                learning_rate=_TEST_LEARNING_RATE,
                job_dir=test_invalid_path,
            )
