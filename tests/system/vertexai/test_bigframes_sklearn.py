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

import os
from unittest import mock

from google.cloud import aiplatform
import vertexai
from tests.system.aiplatform import e2e_base
from vertexai.preview._workflow.executor import training
from vertexai.preview._workflow.serialization_engine import (
    serializers,
)
import numpy as np

import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

import bigframes.pandas as bf
from bigframes.ml.model_selection import train_test_split as bf_train_test_split


bf.options.bigquery.location = "us"  # Dataset is in 'us' not 'us-central1'
bf.options.bigquery.project = e2e_base._PROJECT


# Wrap classes
StandardScaler = vertexai.preview.remote(StandardScaler)
LogisticRegression = vertexai.preview.remote(LogisticRegression)


@mock.patch.object(
    training,
    "VERTEX_AI_DEPENDENCY_PATH",
    "google-cloud-aiplatform[preview] @ git+https://github.com/googleapis/"
    f"python-aiplatform.git@{os.environ['KOKORO_GIT_COMMIT']}"
    if os.environ.get("KOKORO_GIT_COMMIT")
    else "google-cloud-aiplatform[preview] @ git+https://github.com/googleapis/python-aiplatform.git@main",
)
@mock.patch.object(
    training,
    "VERTEX_AI_DEPENDENCY_PATH_AUTOLOGGING",
    "google-cloud-aiplatform[preview,autologging] @ git+https://github.com/googleapis/"
    f"python-aiplatform.git@{os.environ['KOKORO_GIT_COMMIT']}"
    if os.environ.get("KOKORO_GIT_COMMIT")
    else "google-cloud-aiplatform[preview,autologging] @ git+https://github.com/googleapis/python-aiplatform.git@main",
)
# To avoid flaky test due to autolog enabled in parallel tests
@mock.patch.object(vertexai.preview.initializer._Config, "autolog", False)
@pytest.mark.usefixtures(
    "prepare_staging_bucket", "delete_staging_bucket", "tear_down_resources"
)
class TestRemoteExecutionBigframesSklearn(e2e_base.TestEndToEnd):

    _temp_prefix = "temp-vertexai-remote-execution"

    def test_remote_execution_sklearn(self, shared_state):
        # Initialize vertexai
        vertexai.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            staging_bucket=f"gs://{shared_state['staging_bucket_name']}",
        )

        # Prepare dataset
        df = bf.read_gbq("bigquery-public-data.ml_datasets.iris")
        species_categories = {
            "versicolor": 0,
            "virginica": 1,
            "setosa": 2,
        }
        df["species"] = df["species"].map(species_categories)
        index_col = "index"
        df.index.name = index_col
        feature_columns = df[
            ["sepal_length", "sepal_width", "petal_length", "petal_width"]
        ]
        label_columns = df[["species"]]
        train_X, test_X, train_y, _ = bf_train_test_split(
            feature_columns, label_columns, test_size=0.2
        )

        # Remote fit_transform on bf train dataset
        vertexai.preview.init(remote=True)
        transformer = StandardScaler()
        transformer.fit_transform.vertex.remote_config.display_name = (
            self._make_display_name("bigframes-fit-transform")
        )
        X_train = transformer.fit_transform(train_X)

        # Assert the right serializer is being used
        remote_job = aiplatform.CustomJob.list(
            filter=f'display_name="{transformer.fit_transform.vertex.remote_config.display_name}"'
        )[0]
        base_path = remote_job.job_spec.base_output_directory.output_uri_prefix

        input_estimator_metadata = serializers._get_metadata(
            os.path.join(base_path, "input/input_estimator")
        )
        assert input_estimator_metadata["serializer"] == "SklearnEstimatorSerializer"

        output_estimator_metadata = serializers._get_metadata(
            os.path.join(base_path, "output/output_estimator")
        )
        assert output_estimator_metadata["serializer"] == "SklearnEstimatorSerializer"

        train_x_metadata = serializers._get_metadata(os.path.join(base_path, "input/X"))
        assert train_x_metadata["serializer"] == "BigframeSerializer"
        assert train_x_metadata["framework"] == "sklearn"

        shared_state["resources"] = [remote_job]

        assert type(X_train) is np.ndarray
        assert X_train.shape == (120, 4)

        # Remote transform on bf test dataset
        transformer.transform.vertex.remote_config.display_name = (
            self._make_display_name("bigframes-transform")
        )
        X_test = transformer.transform(test_X)

        # Assert the right serializer is being used
        remote_job = aiplatform.CustomJob.list(
            filter=f'display_name="{transformer.transform.vertex.remote_config.display_name}"'
        )[0]
        base_path = remote_job.job_spec.base_output_directory.output_uri_prefix

        input_estimator_metadata = serializers._get_metadata(
            os.path.join(base_path, "input/input_estimator")
        )
        assert input_estimator_metadata["serializer"] == "SklearnEstimatorSerializer"

        test_x_metadata = serializers._get_metadata(os.path.join(base_path, "input/X"))
        assert test_x_metadata["serializer"] == "BigframeSerializer"
        assert train_x_metadata["framework"] == "sklearn"

        shared_state["resources"].append(remote_job)

        assert type(X_test) is np.ndarray
        assert X_test.shape == (30, 4)

        # Remote training on sklearn
        vertexai.preview.init(remote=True)

        model = LogisticRegression(warm_start=True)
        model.fit.vertex.remote_config.display_name = self._make_display_name(
            "bigframes-sklearn-training"
        )
        model.fit(train_X, train_y)

        # Assert the right serializer is being used
        remote_job = aiplatform.CustomJob.list(
            filter=f'display_name="{model.fit.vertex.remote_config.display_name}"'
        )[0]
        base_path = remote_job.job_spec.base_output_directory.output_uri_prefix

        input_estimator_metadata = serializers._get_metadata(
            os.path.join(base_path, "input/input_estimator")
        )
        assert input_estimator_metadata["serializer"] == "SklearnEstimatorSerializer"

        output_estimator_metadata = serializers._get_metadata(
            os.path.join(base_path, "output/output_estimator")
        )
        assert output_estimator_metadata["serializer"] == "SklearnEstimatorSerializer"

        train_x_metadata = serializers._get_metadata(os.path.join(base_path, "input/X"))
        assert train_x_metadata["serializer"] == "BigframeSerializer"
        assert train_x_metadata["framework"] == "sklearn"

        train_y_metadata = serializers._get_metadata(os.path.join(base_path, "input/y"))
        assert train_y_metadata["serializer"] == "BigframeSerializer"
        assert train_y_metadata["framework"] == "sklearn"

        shared_state["resources"].append(remote_job)
