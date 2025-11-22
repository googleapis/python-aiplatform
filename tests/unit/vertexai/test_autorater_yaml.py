# -*- coding: utf-8 -*-

# Copyright 2025 Google LLC
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
"""Unit tests for autorater metric schema."""

import tempfile
from unittest import mock

from google import auth
from google.auth import credentials as auth_credentials
import vertexai
from google.cloud.aiplatform import initializer
from vertexai.preview.evaluation import autorater_utils
from vertexai.preview.evaluation import metric_utils
from vertexai.preview.evaluation import metrics
from vertexai.preview.evaluation import utils
from vertexai.preview.evaluation.metrics import (
    custom_output_config,
)
from vertexai import generative_models
import pandas as pd
import pytest
import ruamel.yaml


GenerativeModel = generative_models.GenerativeModel
AutoraterConfig = autorater_utils.AutoraterConfig
PairwiseMetric = metrics.PairwiseMetric
PointwiseMetric = metrics.PointwiseMetric
RubricBasedMetric = metrics.RubricBasedMetric
CustomOutputConfig = custom_output_config.CustomOutputConfig
RubricGenerationConfig = metrics.RubricGenerationConfig

yaml = ruamel.yaml.YAML(typ="safe")

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_POINTWISE_YAML = """
  metadata:
    name: "test_autorater_pointwise"
    version: "0.0.1"
    required_inputs:
      - "prompt"
  steps:
    - type: pointwise_metric
      prompt:
        system_instruction: "test_system_instruction"
        template: "test_{prompt}_template"
      model:
        model_name_or_endpoint: "test_model_name_or_endpoint"
      options:
        sample_count: 2
      output:
        type: raw
"""
_TEST_PAIRWISE_YAML = """
  metadata:
    name: "test_autorater_pairwise"
    version: "0.0.1"
    required_inputs:
      - "prompt"
  steps:
    - type: pairwise_metric
      prompt:
        system_instruction: "test_system_instruction"
        template: "test_{prompt}_template"
      model:
        model_name_or_endpoint: "test_model_name_or_endpoint"
      options:
        flip_enabled: true
"""
_TEST_RUBRIC_YAML = """
  metadata:
    name: "test_autorater_rubric"
    version: "0.0.1"
    required_inputs:
      - "prompt"
  steps:
    - type: rubric
      prompt:
        template: "test_rubric_template"
      model:
        model_name_or_endpoint: "publishers/google/models/test_rubric_model_name"
    - type: pointwise_metric
      prompt:
        template: "test_{prompt}_template"
      model:
        model_name_or_endpoint: "test_model_name_or_endpoint"
"""
_TEST_INVALID_YAML = """
  metadata:
    name: "test_autorater_minimal"
    version: "0.0.1"
    required_inputs:
      - "prompt"
  steps:
    - type: pointwise_metric
"""
_TEST_INVALID_REQUIRED_INPUTS_YAML = """
  metadata:
    name: "test_autorater_invalid"
    version: "0.0.1"
    required_inputs:
      - "prompt"
  steps:
    - type: pointwise_metric
      prompt:
        template: "{response}"
"""
_TEST_GCS_PATH = "gs://test-bucket/test-file.yaml"


def _generate_evaluation_dataset() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "response": ["test", "text"],
            "reference": ["test", "ref"],
            "context": ["test", "context"],
            "instruction": ["test", "instruction"],
        }
    )


@pytest.fixture
def google_auth_mock():
    with mock.patch.object(auth, "default") as google_auth_default_mock:
        google_auth_default_mock.return_value = (
            auth_credentials.AnonymousCredentials(),
            _TEST_PROJECT,
        )
        yield google_auth_default_mock


@pytest.fixture
def mock_storage_blob():
    with mock.patch("google.cloud.storage.Blob") as mock_blob:
        mock_blob.from_string.return_value = mock_blob
        mock_blob.from_uri.return_value = mock_blob
        yield mock_blob


@pytest.mark.usefixtures("google_auth_mock")
class TestAutoraterYaml:
    """Unit tests for autorater yaml."""

    def setup_method(self):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_dump_to_file(self):
        """Test dump function to a file."""
        test_metric = PointwiseMetric(
            metric="test_autorater_pointwise",
            metric_prompt_template="test_{prompt}_template",
            system_instruction="test_system_instruction",
            autorater_config=AutoraterConfig(
                autorater_model="test_model_name_or_endpoint",
                sampling_count=2,
            ),
            custom_output_config=CustomOutputConfig(return_raw_output=True),
        )
        with tempfile.NamedTemporaryFile() as test_file:
            metric_utils.dump(test_metric, test_file.name, version="0.0.1")
            assert yaml.load(test_file.read()) == yaml.load(_TEST_POINTWISE_YAML)

    def test_dump_to_gcs(self):
        """Test dump function to a GCS file."""
        test_metric = PointwiseMetric(
            metric="test_autorater_pointwise",
            metric_prompt_template="test_{prompt}_template",
            system_instruction="test_system_instruction",
            autorater_config=AutoraterConfig(
                autorater_model="test_model_name_or_endpoint",
                sampling_count=2,
            ),
            custom_output_config=CustomOutputConfig(return_raw_output=True),
        )
        test_path = "gs://test_bucket/test_file"
        with mock.patch.object(
            utils, "_upload_string_to_gcs"
        ) as mock_upload_string_to_gcs:
            metric_utils.dump(test_metric, test_path, version="0.0.1")
            mock_upload_string_to_gcs.assert_called_once()
            mock_args = mock_upload_string_to_gcs.call_args
            assert mock_args.args[0] == test_path
            assert yaml.load(mock_args.args[1]) == yaml.load(_TEST_POINTWISE_YAML)

    def test_dumps_pointwise(self):
        """Test dumps function for pointwise metric."""
        test_metric = PointwiseMetric(
            metric="test_autorater_pointwise",
            metric_prompt_template="test_{prompt}_template",
            system_instruction="test_system_instruction",
            autorater_config=AutoraterConfig(
                autorater_model="test_model_name_or_endpoint",
                sampling_count=2,
            ),
            custom_output_config=CustomOutputConfig(return_raw_output=True),
        )
        test_yaml = metric_utils.dumps(test_metric, version="0.0.1")
        assert yaml.load(test_yaml) == yaml.load(_TEST_POINTWISE_YAML)

    def test_dumps_pairwise(self):
        """Test dumps function for pairwise metric."""
        test_metric = PairwiseMetric(
            metric="test_autorater_pairwise",
            metric_prompt_template="test_{prompt}_template",
            system_instruction="test_system_instruction",
            autorater_config=AutoraterConfig(
                autorater_model="test_model_name_or_endpoint",
                flip_enabled=True,
            ),
        )
        test_yaml = metric_utils.dumps(test_metric, version="0.0.1")
        assert yaml.load(test_yaml) == yaml.load(_TEST_PAIRWISE_YAML)

    def test_dumps_rubric(self):
        """Test dumps function for rubric-based metric."""
        test_metric = RubricBasedMetric(
            generation_config=RubricGenerationConfig(
                prompt_template="test_rubric_template",
                model=GenerativeModel(model_name="test_rubric_model_name"),
            ),
            critique_metric=PointwiseMetric(
                metric="test_autorater_rubric",
                metric_prompt_template="test_{prompt}_template",
                autorater_config=AutoraterConfig(
                    autorater_model="test_model_name_or_endpoint",
                ),
            ),
        )
        test_yaml = metric_utils.dumps(test_metric, version="0.0.1")
        assert yaml.load(test_yaml) == yaml.load(_TEST_RUBRIC_YAML)

    def test_load_from_file(self):
        """Test load function from a file."""
        with tempfile.NamedTemporaryFile() as test_file:
            test_file.write(_TEST_POINTWISE_YAML.encode())
            test_file.seek(0)
            test_metric = metric_utils.load(test_file.name)
            assert isinstance(test_metric, PointwiseMetric)
            assert test_metric.metric_name == "test_autorater_pointwise"
            assert test_metric.metric_prompt_template == "test_{prompt}_template"
            assert test_metric.system_instruction == "test_system_instruction"
            assert test_metric.autorater_config is not None
            assert (
                test_metric.autorater_config.autorater_model
                == "projects/test-project/locations/us-central1/publishers/google/models/test_model_name_or_endpoint"
            )
            assert test_metric.autorater_config.sampling_count == 2

    def test_load_from_gcs(self):
        """Test load function from a GCS file."""
        test_path = "gs://test_bucket/test_file"
        with mock.patch.object(
            utils, "_read_gcs_file_contents"
        ) as mock_read_gcs_file_contents:
            mock_read_gcs_file_contents.return_value = _TEST_POINTWISE_YAML
            test_metric = metric_utils.load(test_path)
            assert isinstance(test_metric, PointwiseMetric)
            assert test_metric.metric_name == "test_autorater_pointwise"
            assert test_metric.metric_prompt_template == "test_{prompt}_template"
            assert test_metric.system_instruction == "test_system_instruction"
            assert test_metric.autorater_config is not None
            assert (
                test_metric.autorater_config.autorater_model
                == "projects/test-project/locations/us-central1/publishers/google/models/test_model_name_or_endpoint"
            )
            assert test_metric.autorater_config.sampling_count == 2

    def test_loads_pointwise(self):
        """Test loads function."""
        test_metric = metric_utils.loads(_TEST_POINTWISE_YAML)
        assert isinstance(test_metric, PointwiseMetric)
        assert test_metric.metric_name == "test_autorater_pointwise"
        assert test_metric.metric_prompt_template == "test_{prompt}_template"
        assert test_metric.system_instruction == "test_system_instruction"
        assert test_metric.autorater_config is not None
        assert (
            test_metric.autorater_config.autorater_model
            == "projects/test-project/locations/us-central1/publishers/google/models/test_model_name_or_endpoint"
        )
        assert test_metric.autorater_config.sampling_count == 2

    def test_loads_pairwise(self):
        """Test loads function for pairwise metric."""
        test_data = _TEST_PAIRWISE_YAML
        test_baseline_model = GenerativeModel(model_name="test_baseline_model")
        test_metric = metric_utils.loads(test_data, test_baseline_model)
        assert isinstance(test_metric, PairwiseMetric)
        assert test_metric.metric_name == "test_autorater_pairwise"
        assert test_metric.metric_prompt_template == "test_{prompt}_template"
        assert test_metric.system_instruction == "test_system_instruction"
        assert test_metric.autorater_config is not None
        assert (
            test_metric.autorater_config.autorater_model
            == "projects/test-project/locations/us-central1/publishers/google/models/test_model_name_or_endpoint"
        )
        assert test_metric.autorater_config.flip_enabled
        assert test_metric.baseline_model == test_baseline_model

    def test_loads_rubric(self):
        """Test loads function for rubric-based metric."""
        test_data = _TEST_RUBRIC_YAML
        test_metric = metric_utils.loads(test_data)
        assert isinstance(test_metric, RubricBasedMetric)
        assert test_metric.generation_config.prompt_template == ("test_rubric_template")
        assert isinstance(test_metric.generation_config.model, GenerativeModel)
        assert (
            test_metric.generation_config.model._model_name
            == "projects/test-project/locations/us-central1/publishers/google/models/test_rubric_model_name"
        )
        assert test_metric.critique_metric.metric_name == "test_autorater_rubric"
        assert (
            test_metric.critique_metric.metric_prompt_template
            == "test_{prompt}_template"
        )
        assert test_metric.critique_metric.autorater_config is not None
        assert (
            test_metric.critique_metric.autorater_config.autorater_model
            == "projects/test-project/locations/us-central1/publishers/google/models/test_model_name_or_endpoint"
        )

    def test_loads_invalid_yaml(self):
        """Test loads function for invalid YAML data."""
        with pytest.raises(ValueError, match="Invalid autorater"):
            metric_utils.loads(_TEST_INVALID_YAML)

    def test_loads_invalid_required_inputs(self):
        """Test loads function with invalid required inputs."""
        with pytest.raises(ValueError, match="placeholders"):
            metric_utils.loads(_TEST_INVALID_REQUIRED_INPUTS_YAML)

    def test_roundtrip_pointwise(self):
        """Test roundtrip for pointwise metric."""
        # First dump.
        test_metric = PointwiseMetric(
            metric="test_autorater_pointwise",
            metric_prompt_template="test_{prompt}_template",
            system_instruction="test_system_instruction",
            autorater_config=AutoraterConfig(
                autorater_model="projects/test-project/locations/us-central1/publishers/google/models/test_model_name_or_endpoint",
                sampling_count=2,
            ),
            custom_output_config=CustomOutputConfig(return_raw_output=True),
        )
        test_yaml = metric_utils.dumps(test_metric, version="0.0.1")
        # Then load.
        loaded_metric = metric_utils.loads(test_yaml)
        # Then verify the loaded metric is the same as the original one.
        assert isinstance(loaded_metric, PointwiseMetric)
        assert test_metric.metric_name == loaded_metric.metric_name
        assert (
            test_metric.metric_prompt_template == loaded_metric.metric_prompt_template
        )
        assert test_metric.system_instruction == loaded_metric.system_instruction
        assert loaded_metric.autorater_config is not None
        assert (
            test_metric.autorater_config.autorater_model
            == loaded_metric.autorater_config.autorater_model
        )
        assert (
            test_metric.autorater_config.sampling_count
            == loaded_metric.autorater_config.sampling_count
        )
        assert test_metric.custom_output_config is not None
        assert loaded_metric.custom_output_config is not None
        assert (
            test_metric.custom_output_config.return_raw_output
            == loaded_metric.custom_output_config.return_raw_output
        )

    def test_roundtrip_pairwise(self):
        """Test roundtrip for pairwise metric."""
        # First dump.
        test_metric = PairwiseMetric(
            metric="test_autorater_pairwise",
            metric_prompt_template="test_{prompt}_template",
            system_instruction="test_system_instruction",
            autorater_config=AutoraterConfig(
                autorater_model="projects/test-project/locations/us-central1/publishers/google/models/test_model_name_or_endpoint",
                flip_enabled=True,
            ),
        )
        test_yaml = metric_utils.dumps(test_metric, version="0.0.1")
        # Then load.
        loaded_metric = metric_utils.loads(test_yaml)
        # Then verify the loaded metric is the same as the original one.
        assert isinstance(loaded_metric, PairwiseMetric)
        assert test_metric.metric_name == loaded_metric.metric_name
        assert (
            test_metric.metric_prompt_template == loaded_metric.metric_prompt_template
        )
        assert test_metric.system_instruction == loaded_metric.system_instruction
        assert loaded_metric.autorater_config is not None
        assert (
            test_metric.autorater_config.autorater_model
            == loaded_metric.autorater_config.autorater_model
        )
        assert (
            test_metric.autorater_config.flip_enabled
            == loaded_metric.autorater_config.flip_enabled
        )
        assert test_metric.custom_output_config == loaded_metric.custom_output_config

    def test_roundtrip_rubric(self):
        """Test roundtrip for rubric-based metric."""
        # First dump.
        test_metric = RubricBasedMetric(
            generation_config=RubricGenerationConfig(
                prompt_template="test_rubric_template",
                model=GenerativeModel(
                    model_name="projects/test-project/locations/us-central1/publishers/google/models/test_rubric_model_name"
                ),
            ),
            critique_metric=PointwiseMetric(
                metric="test_autorater_rubric",
                metric_prompt_template="test_{prompt}_template",
                autorater_config=AutoraterConfig(
                    autorater_model="projects/test-project/locations/us-central1/publishers/google/models/test_model_name_or_endpoint",
                ),
            ),
        )
        test_yaml = metric_utils.dumps(test_metric, version="0.0.1")
        # Then load.
        loaded_metric = metric_utils.loads(test_yaml)
        # Then verify the loaded metric is the same as the original one.
        assert isinstance(loaded_metric, RubricBasedMetric)
        assert (
            test_metric.generation_config.prompt_template
            == loaded_metric.generation_config.prompt_template
        )
        assert isinstance(test_metric.generation_config.model, GenerativeModel)
        assert isinstance(loaded_metric.generation_config.model, GenerativeModel)
        assert (
            test_metric.generation_config.model._model_name
            == loaded_metric.generation_config.model._model_name
        )
        assert (
            test_metric.critique_metric.metric_name
            == loaded_metric.critique_metric.metric_name
        )
        assert (
            test_metric.critique_metric.metric_prompt_template
            == loaded_metric.critique_metric.metric_prompt_template
        )
        assert test_metric.critique_metric.autorater_config is not None
        assert (
            test_metric.critique_metric.autorater_config.autorater_model
            == loaded_metric.critique_metric.autorater_config.autorater_model
        )
        assert (
            test_metric.critique_metric.custom_output_config
            == loaded_metric.critique_metric.custom_output_config
        )

    def test_upload_string_to_gcs(self, mock_storage_blob):
        """Test upload evaluation results to GCS."""
        utils._upload_string_to_gcs(_TEST_GCS_PATH, _TEST_POINTWISE_YAML)
        string_calls = mock_storage_blob.from_string.call_count  # gcs < 3.0.0
        uri_calls = mock_storage_blob.from_uri.call_count  # gcs >= 3.0.0
        assert uri_calls + string_calls == 1
        mock_storage_blob.upload_from_string.assert_called_once()
        data = mock_storage_blob.upload_from_string.call_args.args[0]
        assert data == _TEST_POINTWISE_YAML
