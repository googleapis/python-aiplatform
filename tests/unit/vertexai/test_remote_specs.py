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

"""Tests for developer/remote_specs.py.
"""

import json
import os
import re
import tempfile
from typing import Any, Dict, List

import cloudpickle
import vertexai
from vertexai.preview.developer import remote_specs
import mock
import pandas as pd
import pytest
import torch


_TEST_BINDING = {
    "arg_0": 10,
    "arg_1": lambda x: x + 1,
    "arg_2": pd.DataFrame(data={"col_0": [0, 1], "col_1": [2, 3]}),
}

_TEST_MACHINE_TYPE = "n1-standard-16"
_TEST_REPLICA_COUNT = 1
_TEST_BOOT_DISK_TYPE_DEFAULT = "pd-ssd"
_TEST_BOOT_DISK_SIZE_GB_DEFAULT = 100

_TEST_WORKER_POOL_SPEC_OBJ_MACHINE_TYPE = remote_specs.WorkerPoolSpec(
    machine_type=_TEST_MACHINE_TYPE, replica_count=_TEST_REPLICA_COUNT
)

_TEST_WORKER_POOL_SPEC_MACHINE_TYPE = {
    "machine_spec": {"machine_type": _TEST_MACHINE_TYPE},
    "replica_count": _TEST_REPLICA_COUNT,
    "disk_spec": {
        "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
        "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
    },
}

_TEST_WORKER_POOL_SPEC_MACHINE_TYPE_CONTAINER_SPEC = {
    "machine_spec": {"machine_type": _TEST_MACHINE_TYPE},
    "replica_count": _TEST_REPLICA_COUNT,
    "disk_spec": {
        "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
        "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
    },
    "container_spec": {
        "image_uri": "test-image",
        "command": ["python3", "run.py"],
        "args": [],
    },
}

_TEST_CLUSTER_SPEC_CHIEF_STR = '{"cluster":{"workerpool0":["cmle-training-workerpool0-1d969d3ba6-0:2222"],"workerpool1":["cmle-training-workerpool1-1d969d3ba6-0:2222"]},"environment":"cloud","task":{"type":"workerpool0","index":0}}'
_TEST_CLUSTER_SPEC_WORKER_STR = '{"cluster":{"workerpool0":["cmle-training-workerpool0-1d969d3ba6-0:2222"],"workerpool1":["cmle-training-workerpool1-1d969d3ba6-0:2222"]},"environment":"cloud","task":{"type":"workerpool1","index":0}}'

_TEST_OUTPUT_PATH = "gs://test-bucket/output"


def _get_vertex_cluster_spec(task_type: str = "workerpool0", task_index: int = 0):
    # pylint: disable=protected-access,missing-function-docstring
    return {
        "cluster": {
            remote_specs._CHIEF: ["cmle-training-workerpool0-id-0:2222"],
            remote_specs._WORKER: [
                "cmle-training-workerpool1-id-0:2222",
                "cmle-training-workerpool1-id-1:2222",
                "cmle-training-workerpool1-id-2:2222",
            ],
            remote_specs._SERVER: [
                "cmle-training-workerpool2-id-0:2222",
                "cmle-training-workerpool2-id-1:2222",
                "cmle-training-workerpool2-id-2:2222",
            ],
            remote_specs._EVALUATOR: ["cmle-training-workerpool3-id-0:2222"],
        },
        remote_specs._TASK: {
            remote_specs._TYPE: task_type,
            remote_specs._INDEX: task_index,
        },
    }


class TestRemoteSpec:
    """Tests for parameter spec classes and helper function(s)."""

    # pylint: disable=protected-access,missing-function-docstring
    @pytest.mark.parametrize(
        "name,expected_argument_name",
        [
            ("self.a", "a"),
            ("a.b.c", "c"),
            ("_arg_0", "arg_0"),
            ("__arg_0", "__arg_0"),
            ("arg_0", "arg_0"),
        ],
    )
    def test_get_argument_name(self, name: str, expected_argument_name: str):
        argument_name = remote_specs._get_argument_name(name)
        assert argument_name == expected_argument_name

    # pylint: disable=missing-function-docstring,protected-access
    @pytest.mark.parametrize(
        "name",
        [
            ("."),
            (".."),
            ("_"),
        ],
    )
    def test_get_argument_name_invalid(self, name: str):
        err_msg = f"Failed to get argument name from name {name}."
        with pytest.raises(ValueError) as e:
            remote_specs._get_argument_name(name)
        assert re.match(err_msg, str(e.value))

    def test_input_parameter_spec_default(self):
        param_spec = remote_specs._InputParameterSpec("arg_0")
        assert param_spec.name == "arg_0"
        assert param_spec.argument_name == "arg_0"
        assert param_spec.serializer == "literal"

    def test_input_parameter_spec_argument_name(self):
        param_spec = remote_specs._InputParameterSpec("arg_0", argument_name="input_0")
        assert param_spec.name == "arg_0"
        assert param_spec.argument_name == "input_0"
        assert param_spec.serializer == "literal"

    def test_input_parameter_spec_argument_name_empty(self):
        err_msg = "Input parameter name cannot be empty"
        with pytest.raises(ValueError) as e:
            remote_specs._InputParameterSpec("")
        assert re.match(err_msg, str(e.value))

    @pytest.mark.parametrize("serializer", ["literal", "parquet", "cloudpickle"])
    def test_input_parameter_spec_serializer_valid(self, serializer: str):
        param_spec = remote_specs._InputParameterSpec("arg_0", serializer=serializer)
        assert param_spec.name == "arg_0"
        assert param_spec.argument_name == "arg_0"
        assert param_spec.serializer == serializer

    def test_input_parameter_spec_serializer_invalid(self):
        err_msg = "Invalid serializer"
        with pytest.raises(ValueError) as e:
            remote_specs._InputParameterSpec("arg_0", serializer="invalid")
        assert re.match(err_msg, str(e.value))

    def test_input_format_arg_literal(self):
        test_spec = remote_specs._InputParameterSpec("arg_0", serializer="literal")
        assert test_spec.format_arg("", _TEST_BINDING) == _TEST_BINDING["arg_0"]

    # pylint: disable=redefined-outer-name
    @pytest.mark.usefixtures("google_auth_mock")
    def test_input_format_arg_cloudpickle(
        self, mock_named_temp_file, mock_blob_upload_from_filename
    ):

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = os.path.join(tmp_dir, "tmp")
            tmp_handler = open(tmp_path, "wb")
            (mock_named_temp_file.return_value.__enter__.return_value) = tmp_handler

            spec = remote_specs._InputParameterSpec("arg_1", serializer="cloudpickle")
            assert (
                spec.format_arg("gs://bucket/path", _TEST_BINDING)
                == "gs://bucket/path/arg_1"
            )
            mock_blob_upload_from_filename.assert_called_once()

            with open(tmp_path, "rb") as f:
                assert cloudpickle.loads(f.read())(1) == _TEST_BINDING["arg_1"](1)

    @pytest.mark.usefixtures("google_auth_mock")
    def test_input_format_arg_parquet(
        self, mock_named_temp_file, mock_blob_upload_from_filename
    ):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_serialized_path = os.path.join(tmp_dir, "serialized")
            tmp_serialized_handler = open(tmp_serialized_path, "wb")

            tmp_metadata_path = os.path.join(tmp_dir, "metadata")
            tmp_handler = open(tmp_metadata_path, "wb")
            (mock_named_temp_file.return_value.__enter__.side_effect) = [
                tmp_serialized_handler,
                tmp_handler,
            ]

            spec = remote_specs._InputParameterSpec("arg_2", serializer="parquet")
            assert (
                spec.format_arg("gs://bucket/path", _TEST_BINDING)
                == "gs://bucket/path/arg_2"
            )
            assert mock_blob_upload_from_filename.call_count == 2

            upload_calls = mock_blob_upload_from_filename.call_args_list

            metadata_path = upload_calls[1][1]["filename"]

            assert metadata_path == tmp_metadata_path
            expected_metadata = {
                "col_0": {
                    "dtype": "int64",
                    "feature_type": "dense",
                },
                "col_1": {
                    "dtype": "int64",
                    "feature_type": "dense",
                },
            }
            with open(tmp_metadata_path, "rb") as f:
                assert cloudpickle.loads(f.read()) == expected_metadata

    @pytest.mark.parametrize(
        "spec,binding,msg",
        [
            (
                remote_specs._InputParameterSpec("arg_4"),
                _TEST_BINDING,
                "Input arg_4 not found in binding",
            ),
            (
                remote_specs._InputParameterSpec("arg", serializer="parquet"),
                {"arg": 10},
                "Parquet serializer is only supported for",
            ),
            (
                remote_specs._InputParameterSpec("arg_0"),
                _TEST_BINDING,
                "Unsupported serializer:",
            ),
        ],
    )
    @pytest.mark.usefixtures("google_auth_mock")
    def test_input_format_arg_invalid(self, spec, binding, msg):
        if msg == "Unsupported serializer:":
            spec.serializer = "invalid"
        with pytest.raises(ValueError, match=msg):
            spec.format_arg("gs://bucket/path", binding)

    def test_output_parameter_spec_default(self):
        param_spec = remote_specs._OutputParameterSpec("arg_0")
        assert param_spec.name == "arg_0"
        assert param_spec.argument_name == "arg_0"
        assert param_spec.deserializer == "literal"

    def test_output_parameter_spec_argument_name(self):
        param_spec = remote_specs._OutputParameterSpec("arg_0", argument_name="input_0")
        assert param_spec.name == "arg_0"
        assert param_spec.argument_name == "input_0"
        assert param_spec.deserializer == "literal"

    def test_output_parameter_spec_argument_name_empty(self):
        err_msg = "Output parameter name cannot be empty"
        with pytest.raises(ValueError) as e:
            remote_specs._OutputParameterSpec("")
        assert re.match(err_msg, str(e.value))

    @pytest.mark.parametrize("deserializer", ["literal", "cloudpickle"])
    def test_output_parameter_spec_serializer_valid(self, deserializer):
        param_spec = remote_specs._OutputParameterSpec(
            "arg_0", deserializer=deserializer
        )
        assert param_spec.name == "arg_0"
        assert param_spec.argument_name == "arg_0"
        assert param_spec.deserializer == deserializer

    def test_output_parameter_spec_deserializer_invalid(self):
        err_msg = "Invalid deserializer"
        with pytest.raises(ValueError) as e:
            remote_specs._OutputParameterSpec("arg_0", deserializer="invalid")
        assert re.match(err_msg, str(e.value))

    @pytest.mark.usefixtures("google_auth_mock")
    def test_deserialize_output_literal(
        self, mock_named_temp_file, mock_blob_download_to_filename
    ):
        spec = remote_specs._OutputParameterSpec(
            "arg_0", deserializer=remote_specs._LITERAL
        )
        test_path = "gs://bucket/path"
        test_val = "output"

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = os.path.join(tmp_dir, "tmp_path")
            mock_temp_file = mock_named_temp_file.return_value.__enter__()
            mock_temp_file.name = tmp_path

            # Writes to a file to be read from.
            with open(tmp_path, "w") as f:
                f.write(test_val)

            # Tests reading literal output from GCS.
            assert spec.deserialize_output(test_path) == test_val
            mock_blob_download_to_filename.assert_called_once_with(filename=tmp_path)

    @pytest.mark.usefixtures("google_auth_mock")
    def test_deserialize_output_cloudpickle(
        self, mock_named_temp_file, mock_blob_download_to_filename
    ):
        spec = remote_specs._OutputParameterSpec(
            "arg_1", deserializer=remote_specs._CLOUDPICKLE
        )
        test_path = "gs://bucket/path"
        test_val = cloudpickle.dumps(_TEST_BINDING["arg_1"])

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = os.path.join(tmp_dir, "tmp_path")
            mock_handler = mock_named_temp_file.return_value.__enter__()
            mock_handler.name = tmp_path

            # Writes to a file to be read from.
            with open(tmp_path, "wb") as f:
                f.write(test_val)

            # Tests the deserialized output function works as expected.
            with open(tmp_path, "rb") as f:
                mock_handler.read = f.read
                # Verifies that calling the functions return the same results.
                assert spec.deserialize_output(test_path)(1) == _TEST_BINDING["arg_1"](
                    1
                )
                mock_blob_download_to_filename.assert_called_once_with(
                    filename=tmp_path
                )

    @pytest.mark.usefixtures("google_auth_mock")
    def test_deserialize_output_invalid(self):
        spec = remote_specs._OutputParameterSpec("arg_0")
        spec.deserializer = "invalid"
        with pytest.raises(ValueError, match="Unsupported deserializer:"):
            spec.deserialize_output("gs://bucket/path")

    def test_gen_gcs_path(self):
        base_dir = "gs://test_bucket"
        name = "test_name"
        expected_path = "gs://test_bucket/test_name"
        assert remote_specs._gen_gcs_path(base_dir, name) == expected_path

    def test_gen_gcs_path_invalid(self):
        base_dir = "test_bucket"
        name = "test_name"
        with pytest.raises(ValueError):
            remote_specs._gen_gcs_path(base_dir, name)

    def test_gen_gcs_path_remove_suffix(self):
        base_dir = "gs://test_bucket"
        name = "test_name/"
        expected_path = "gs://test_bucket/test_name"
        assert remote_specs._gen_gcs_path(base_dir, name) == expected_path

    def test_generate_feature_metadata(self):
        df = pd.DataFrame(
            {
                "col_int": [1, 2, 3],
                "col_float": [0.1, 0.2, 0.3],
                0: [0, 1, 0],
                "ignored_cat_0": ["0", "1", "0"],
                "ignored_cat_1": ["a", "b", "c"],
                "ignored_type": ["d", "e", "f"],
            }
        )
        df["col_int"] = df["col_int"].astype("int64")
        df["col_float"] = df["col_float"].astype("float64")
        df[0] = df[0].astype("category")
        df["ignored_cat_0"] = df["ignored_cat_0"].astype("category")
        df["ignored_cat_1"] = df["ignored_cat_1"].astype("category")
        df["ignored_type"] = df["ignored_type"].astype("object")

        # ignored_cat and ignored_type do not have feature metadata
        expected__metadata = {
            "col_int": {
                "dtype": "int64",
                "feature_type": "dense",
            },
            "col_float": {
                "dtype": "float64",
                "feature_type": "dense",
            },
            "0": {
                "dtype": "int64",
                "feature_type": "dense",
                "categories": [0, 1],
            },
        }

        original_df = df.copy(deep=True)
        assert remote_specs._generate_feature_metadata(df) == expected__metadata

        # Checks that the original dataframe is not modified
        assert df.equals(original_df)

    def test_generate_feature_metadata_invalid(self):
        with pytest.raises(ValueError, match="Generating feature metadata is"):
            remote_specs._generate_feature_metadata([0, 1, 2])


class TestClusterSpec:
    """Tests for cluster spec classes and other distributed training helper functions."""

    # pylint: disable=protected-access,missing-function-docstring
    def test_invalid_cluster_info(self):
        cluster = {
            remote_specs._CHIEF: ["cmle-training-workerpool0-id-0:2222"],
            "worker": ["cmle-training-workerpool1-id-0:2222"],
        }

        err_msg = "Invalid task type: worker."
        with pytest.raises(ValueError) as e:
            remote_specs._Cluster(cluster)
        assert re.match(err_msg, str(e.value))

    def test_task_types(self):
        cluster = remote_specs._Cluster(_get_vertex_cluster_spec()["cluster"])
        assert cluster.task_types == [
            remote_specs._CHIEF,
            remote_specs._WORKER,
            remote_specs._SERVER,
            remote_specs._EVALUATOR,
        ]

    @pytest.mark.parametrize(
        "task_type,expected_num_tasks",
        [
            (remote_specs._CHIEF, 1),
            (remote_specs._WORKER, 3),
            (remote_specs._SERVER, 3),
            (remote_specs._EVALUATOR, 1),
        ],
    )
    def test_get_num_tasks(self, task_type, expected_num_tasks):
        cluster = remote_specs._Cluster(_get_vertex_cluster_spec()["cluster"])
        assert cluster.get_num_tasks(task_type) == expected_num_tasks

    @pytest.mark.parametrize(
        "task_type,expected_task_addresses",
        [
            (remote_specs._CHIEF, ["cmle-training-workerpool0-id-0:2222"]),
            (
                remote_specs._WORKER,
                [
                    "cmle-training-workerpool1-id-0:2222",
                    "cmle-training-workerpool1-id-1:2222",
                    "cmle-training-workerpool1-id-2:2222",
                ],
            ),
            (
                remote_specs._SERVER,
                [
                    "cmle-training-workerpool2-id-0:2222",
                    "cmle-training-workerpool2-id-1:2222",
                    "cmle-training-workerpool2-id-2:2222",
                ],
            ),
            (remote_specs._EVALUATOR, ["cmle-training-workerpool3-id-0:2222"]),
        ],
    )
    def test_get_task_addresses(self, task_type, expected_task_addresses):
        cluster = remote_specs._Cluster(_get_vertex_cluster_spec()["cluster"])
        assert cluster.get_task_addresses(task_type) == expected_task_addresses

    @pytest.mark.parametrize(
        "cluster_spec,expected_rank",
        [
            (
                remote_specs._ClusterSpec(
                    _get_vertex_cluster_spec(remote_specs._CHIEF, 0)
                ),
                0,
            ),
            (
                remote_specs._ClusterSpec(
                    _get_vertex_cluster_spec(remote_specs._WORKER, 2)
                ),
                3,
            ),
            (
                remote_specs._ClusterSpec(
                    _get_vertex_cluster_spec(remote_specs._SERVER, 1)
                ),
                5,
            ),
            (
                remote_specs._ClusterSpec(
                    _get_vertex_cluster_spec(remote_specs._EVALUATOR, 0)
                ),
                7,
            ),
        ],
    )
    def test_get_rank(self, cluster_spec, expected_rank):
        assert cluster_spec.get_rank() == expected_rank

    def test_get_world_size(self):
        cluster_spec = remote_specs._ClusterSpec(_get_vertex_cluster_spec())
        assert cluster_spec.get_world_size() == 8

    def test_get_chief_address_port(self):
        cluster_spec = remote_specs._ClusterSpec(_get_vertex_cluster_spec())
        assert cluster_spec.get_chief_address_port() == (
            "cmle-training-workerpool0-id-0",
            2222,
        )


# pylint: disable=protected-access
class TestWorkerPoolSpecs:
    """Tests for worker pool spec classes and related functions."""

    @pytest.mark.parametrize(
        "worker_pool_specs,expected_spec",
        [
            (
                remote_specs.WorkerPoolSpecs(_TEST_WORKER_POOL_SPEC_OBJ_MACHINE_TYPE),
                [_TEST_WORKER_POOL_SPEC_MACHINE_TYPE_CONTAINER_SPEC],
            ),
            (
                remote_specs.WorkerPoolSpecs(
                    _TEST_WORKER_POOL_SPEC_OBJ_MACHINE_TYPE,
                    evaluator=_TEST_WORKER_POOL_SPEC_OBJ_MACHINE_TYPE,
                ),
                [
                    _TEST_WORKER_POOL_SPEC_MACHINE_TYPE_CONTAINER_SPEC,
                    {},
                    {},
                    _TEST_WORKER_POOL_SPEC_MACHINE_TYPE_CONTAINER_SPEC,
                ],
            ),
            (
                remote_specs.WorkerPoolSpecs(
                    _TEST_WORKER_POOL_SPEC_OBJ_MACHINE_TYPE,
                    server=_TEST_WORKER_POOL_SPEC_OBJ_MACHINE_TYPE,
                ),
                [
                    _TEST_WORKER_POOL_SPEC_MACHINE_TYPE_CONTAINER_SPEC,
                    {},
                    _TEST_WORKER_POOL_SPEC_MACHINE_TYPE_CONTAINER_SPEC,
                ],
            ),
        ],
    )
    def test_prepare_worker_pool_specs(
        self,
        worker_pool_specs: remote_specs.WorkerPoolSpecs,
        expected_spec: List[Dict[str, Any]],
    ):
        assert (
            remote_specs._prepare_worker_pool_specs(
                worker_pool_specs, "test-image", ["python3", "run.py"], []
            )
            == expected_spec
        )

    @pytest.mark.parametrize(
        "cluster_spec_str,expected_output_path",
        [
            (
                _TEST_CLUSTER_SPEC_CHIEF_STR,
                os.path.join(_TEST_OUTPUT_PATH, "output_estimator"),
            ),
            (
                _TEST_CLUSTER_SPEC_WORKER_STR,
                os.path.join(_TEST_OUTPUT_PATH, "temp/workerpool1_0"),
            ),
            ("", os.path.join(_TEST_OUTPUT_PATH, "output_estimator")),
        ],
    )
    def test_get_output_path_for_distributed_training(
        self, cluster_spec_str, expected_output_path
    ):
        with mock.patch.dict(
            os.environ, {remote_specs._CLUSTER_SPEC: cluster_spec_str}, clear=True
        ):
            with mock.patch("os.makedirs"):
                output_path = remote_specs._get_output_path_for_distributed_training(
                    _TEST_OUTPUT_PATH, "output_estimator"
                )
        assert output_path == expected_output_path

    # Temporarily remove these tests since they require tensorflow >= 2.12.0
    # but in our external test environment tf 2.12 is not available due to conflict
    # TODO(jayceeli) Add these tests back once we fix the external environment issue.

    # def test_set_keras_distributed_strategy_enable_distributed_multi_worker(self):
    #     model = tf.keras.Sequential(
    #         [tf.keras.layers.Dense(5, input_shape=(4,)), tf.keras.layers.Softmax()]
    #     )
    #     model.compile(optimizer="adam", loss="mean_squared_error")
    #     with mock.patch.dict(
    #         os.environ,
    #         {remote_specs._CLUSTER_SPEC: _TEST_CLUSTER_SPEC_CHIEF_STR},
    #         clear=True,
    #     ):
    #         strategy = remote_specs._get_keras_distributed_strategy(True, None)
    #         updated_model = remote_specs._set_keras_distributed_strategy(
    #             model, strategy
    #         )

    #     assert updated_model.get_config() == model.get_config()
    #     assert updated_model.get_compile_config() == model.get_compile_config()
    #     assert "CollectiveAllReduceStrategy" in str(
    #         type(updated_model.distribute_strategy)
    #     )

    # def test_set_keras_distributed_strategy_enable_distributed_multi_gpu(self):
    #     model = tf.keras.Sequential(
    #         [tf.keras.layers.Dense(5, input_shape=(4,)), tf.keras.layers.Softmax()]
    #     )
    #     model.compile(optimizer="adam", loss="mean_squared_error")
    #     # no cluster_spec is set for single worker training
    #     strategy = remote_specs._get_keras_distributed_strategy(True, None)
    #     updated_model = remote_specs._set_keras_distributed_strategy(model, strategy)

    #     assert updated_model.get_config() == model.get_config()
    #     assert updated_model.get_compile_config() == model.get_compile_config()
    #     assert "MirroredStrategy" in str(type(updated_model.distribute_strategy))

    # def test_set_keras_distributed_strategy_multi_gpu(self):
    #     model = tf.keras.Sequential(
    #         [tf.keras.layers.Dense(5, input_shape=(4,)), tf.keras.layers.Softmax()]
    #     )
    #     model.compile(optimizer="adam", loss="mean_squared_error")
    #     # no cluster_spec is set for single worker training
    #     strategy = remote_specs._get_keras_distributed_strategy(False, 3)
    #     updated_model = remote_specs._set_keras_distributed_strategy(model, strategy)

    #     assert updated_model.get_config() == model.get_config()
    #     assert updated_model.get_compile_config() == model.get_compile_config()
    #     assert "MirroredStrategy" in str(type(updated_model.distribute_strategy))

    @mock.patch.dict(os.environ, {}, clear=True)
    @mock.patch.object(torch.distributed, "init_process_group")
    @mock.patch("torch.nn.parallel.DistributedDataParallel")
    def test_setup_pytorch_distributed_training(
        self,
        mock_distributed_data_parallel,
        mock_init_process_group,
    ):
        class TestClass(vertexai.preview.VertexModel, torch.nn.Module):
            def __init__(self):
                torch.nn.Module.__init__(self)
                vertexai.preview.VertexModel.__init__(self)
                self.linear = torch.nn.Linear(4, 3)
                self.softmax = torch.nn.Softmax(dim=1)

            def forward(self, x):
                return self.softmax(self.linear(x))

            @vertexai.preview.developer.mark.train()
            def test_method(self):
                return

        model = TestClass()
        setattr(
            model,
            "cluster_spec",
            remote_specs._ClusterSpec(json.loads(_TEST_CLUSTER_SPEC_CHIEF_STR)),
        )
        setattr(model, "_enable_cuda", False)

        output = remote_specs.setup_pytorch_distributed_training(model)

        mock_init_process_group.assert_called_once_with(
            backend="gloo", rank=0, world_size=2
        )
        mock_distributed_data_parallel.assert_called_once_with(model)

        assert (
            os.getenv(remote_specs._MASTER_ADDR)
            == "cmle-training-workerpool0-1d969d3ba6-0"
        )
        assert os.getenv(remote_specs._MASTER_PORT) == "2222"
        assert next(output.parameters()).is_cpu

    @mock.patch.dict(os.environ, {}, clear=True)
    def test_setup_pytorch_distributed_training_no_cluster_spec(self):
        class TestClass(vertexai.preview.VertexModel, torch.nn.Module):
            def __init__(self):
                torch.nn.Module.__init__(self)
                vertexai.preview.VertexModel.__init__(self)
                self.linear = torch.nn.Linear(4, 3)
                self.softmax = torch.nn.Softmax(dim=1)

            def forward(self, x):
                return self.softmax(self.linear(x))

            @vertexai.preview.developer.mark.train()
            def test_method(self):
                return

        model = TestClass()

        assert model == remote_specs.setup_pytorch_distributed_training(model)
