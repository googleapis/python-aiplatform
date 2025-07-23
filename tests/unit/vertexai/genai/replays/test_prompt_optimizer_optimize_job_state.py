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

import os

from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai._genai import types
import pytest


def _raise_for_unset_env_vars() -> None:
    if not os.environ.get("VAPO_CONFIG_PATH"):
        raise ValueError("VAPO_CONFIG_PATH environment variable is not set.")
    if not os.environ.get("VAPO_SERVICE_ACCOUNT_PROJECT_NUMBER"):
        raise ValueError(
            "VAPO_SERVICE_ACCOUNT_PROJECT_NUMBER " "environment variable is not set."
        )


# If you re-record this test, you will need to update the replay file to
# include the placeholder values for config path and service account
def test_optimize(client):
    """Tests the optimize request parameters method."""

    _raise_for_unset_env_vars()

    config = types.PromptOptimizerVAPOConfig(
        config_path=os.environ.get("VAPO_CONFIG_PATH"),
        wait_for_completion=True,
        service_account_project_number=os.environ.get(
            "VAPO_SERVICE_ACCOUNT_PROJECT_NUMBER"
        ),
        optimizer_job_display_name="optimizer_job_test",
    )
    job = client.prompt_optimizer.optimize(
        method="vapo",
        config=config,
    )
    assert isinstance(job, types.CustomJob)
    assert job.state == types.JobState.JOB_STATE_SUCCEEDED


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="prompt_optimizer.optimize",
)


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_optimize_async(client):
    _raise_for_unset_env_vars()

    config = types.PromptOptimizerVAPOConfig(
        config_path=os.environ.get("VAPO_CONFIG_PATH"),
        service_account_project_number=os.environ.get(
            "VAPO_SERVICE_ACCOUNT_PROJECT_NUMBER"
        ),
        optimizer_job_display_name="optimizer_job_test",
    )
    job = await client.aio.prompt_optimizer.optimize(
        method="vapo",
        config=config,
    )
    assert isinstance(job, types.CustomJob)
    assert job.state == types.JobState.JOB_STATE_PENDING


@pytest.mark.asyncio
async def test_optimize_async_with_config_wait_for_completion(client, caplog):
    _raise_for_unset_env_vars()

    config = types.PromptOptimizerVAPOConfig(
        config_path=os.environ.get("VAPO_CONFIG_PATH"),
        service_account_project_number=os.environ.get(
            "VAPO_SERVICE_ACCOUNT_PROJECT_NUMBER"
        ),
        optimizer_job_display_name="optimizer_job_test",
        wait_for_completion=True,
    )
    job = await client.aio.prompt_optimizer.optimize(
        method="vapo",
        config=config,
    )
    assert isinstance(job, types.CustomJob)
    assert job.state == types.JobState.JOB_STATE_PENDING
    assert "Ignoring wait_for_completion=True" in caplog.text
