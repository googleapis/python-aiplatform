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
# pylint: disable=protected-access,bad-continuation,missing-function-docstring
import re

from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai._genai import types

_TEST_PROJECT = "977012026409"
_TEST_LOCATION = "us-central1"


def test_create_and_get_evaluation_metric(client):
    client._api_client._http_options.api_version = "v1beta1"
    client._api_client._http_options.base_url = (
        "https://us-central1-staging-aiplatform.sandbox.googleapis.com/"
    )
    result = client.evals.create_evaluation_metric(
        display_name="test_metric",
        description="test_description",
        metric=types.RubricMetric.GENERAL_QUALITY,
    )
    assert isinstance(result, str)
    assert re.match(
        r"^projects/[^/]+/locations/[^/]+/evaluationMetrics/[^/]+$",
        result,
    )
    metric = client.evals.get_evaluation_metric(metric_resource_name=result)
    assert isinstance(metric, types.EvaluationMetric)
    assert metric.display_name == "test_metric"


def test_list_evaluation_metrics(client):
    client._api_client._http_options.api_version = "v1beta1"
    client._api_client._http_options.base_url = (
        "https://us-central1-staging-aiplatform.sandbox.googleapis.com/"
    )
    response = client.evals.list_evaluation_metrics()
    assert isinstance(response, types.ListEvaluationMetricsResponse)
    assert len(response.evaluation_metrics) >= 0


# The setup function registers the module and method for the recorder
pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.create_evaluation_metric",
)
