# Copyright 2026 Google LLC
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

from agentplatform._genai import types
from tests.unit.agentplatform.genai.replays import pytest_helper
from google.genai._api_client import HttpOptions
import pytest

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.update_evaluation_experiment",
    http_options=HttpOptions(
        api_version="v1beta1",
    ),
)

pytest_plugins = ("pytest_asyncio",)


def test_update_and_delete(client):
    experiment = client.evals.create_evaluation_experiment(
        display_name="sdk-update-delete-test"
    )
    assert isinstance(experiment, types.EvaluationExperiment)

    updated = client.evals.update_evaluation_experiment(
        name=experiment.name,
        config={
            "display_name": "sdk-update-delete-test-renamed",
            "update_mask": "display_name",
        },
    )
    assert isinstance(updated, types.EvaluationExperiment)
    assert updated.display_name == "sdk-update-delete-test-renamed"

    delete_operation = client.evals.delete_evaluation_experiment(
        name=experiment.name
    )
    assert isinstance(
        delete_operation, types.DeleteEvaluationExperimentOperation
    )


@pytest.mark.asyncio
async def test_update_and_delete_async(client):
    experiment = await client.aio.evals.create_evaluation_experiment(
        display_name="sdk-update-delete-test-async"
    )
    assert isinstance(experiment, types.EvaluationExperiment)

    updated = await client.aio.evals.update_evaluation_experiment(
        name=experiment.name,
        config={
            "display_name": "sdk-update-delete-test-async-renamed",
            "update_mask": "display_name",
        },
    )
    assert isinstance(updated, types.EvaluationExperiment)
    assert updated.display_name == "sdk-update-delete-test-async-renamed"

    delete_operation = await client.aio.evals.delete_evaluation_experiment(
        name=experiment.name
    )
    assert isinstance(
        delete_operation, types.DeleteEvaluationExperimentOperation
    )
