# -*- coding: utf-8 -*-

# Copyright 2024 Google LLC
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
"""Unit tests for generative model tuning."""
# pylint: disable=protected-access,bad-continuation

import copy
import datetime
from typing import Dict, Iterable
from unittest import mock
import uuid

import vertexai
from google.cloud.aiplatform import compat
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils as aiplatform_utils
from google.cloud.aiplatform_v1.services import gen_ai_tuning_service
from google.cloud.aiplatform_v1.types import job_state
from google.cloud.aiplatform_v1.types import tuning_job as gca_tuning_job
from vertexai.preview import tuning
from vertexai.preview.tuning import supervised_tuning
from vertexai.tuning import _tuning
import pytest

from google.rpc import status_pb2


_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"


_global_tuning_jobs: Dict[str, gca_tuning_job.TuningJob] = {}


class MockGenAiTuningServiceClient(gen_ai_tuning_service.GenAiTuningServiceClient):

    def __init__(self, **_):
        # self._tuning_jobs: Dict[str, gca_tuning_job.TuningJob] = {}
        pass

    @property
    def _tuning_jobs(self) -> Dict[str, gca_tuning_job.TuningJob]:
        return _global_tuning_jobs

    def create_tuning_job(
        self,
        *,
        parent: str,
        tuning_job: gca_tuning_job.TuningJob,
        **_,
    ) -> gca_tuning_job.TuningJob:
        tuning_job = copy.deepcopy(tuning_job)
        resource_id = uuid.uuid4().hex
        resource_name = f"{parent}/tuningJobs/{resource_id}"
        tuning_job.name = resource_name
        current_time = datetime.datetime.now(datetime.UTC)
        tuning_job.create_time = current_time
        tuning_job.update_time = current_time
        tuning_job.state = job_state.JobState.JOB_STATE_PENDING
        self._tuning_jobs[resource_name] = tuning_job
        return tuning_job

    def _progress_tuning_job(self, name: str):
        tuning_job: gca_tuning_job.TuningJob = self._tuning_jobs[name]
        current_time = datetime.datetime.now(datetime.UTC)
        if tuning_job.state == job_state.JobState.JOB_STATE_PENDING:
            if "invalid_dataset" in tuning_job.supervised_tuning_spec.training_dataset_uri:
                tuning_job.state = job_state.JobState.JOB_STATE_FAILED
                tuning_job.error = status_pb2.Status(
                    code=400,
                    message="Invalid dataset."
                )
            else:
                tuning_job.state = job_state.JobState.JOB_STATE_RUNNING
            tuning_job.update_time = current_time
        elif tuning_job.state == job_state.JobState.JOB_STATE_RUNNING:
            parent = tuning_job.name.partition("/tuningJobs/")[0]
            tuning_job.state = job_state.JobState.JOB_STATE_SUCCEEDED
            experiment_id = uuid.uuid4().hex
            tuned_model_id = uuid.uuid4().hex
            tuned_model_endpoint_id = uuid.uuid4().hex
            tuning_job.experiment = f"{parent}/metadataStores/default/contexts/{experiment_id}"
            tuning_job.tuned_model = gca_tuning_job.TunedModel(
                model=f"{parent}/models/{tuned_model_id}",
                endpoint=f"{parent}/endpoints/{tuned_model_endpoint_id}",
            )
            tuning_job.end_time = current_time
            tuning_job.update_time = current_time
        else:
            pass

    def get_tuning_job(self, *, name: str, **_) -> gca_tuning_job.TuningJob:
        tuning_job = self._tuning_jobs[name]
        tuning_job = copy.deepcopy(tuning_job)
        self._progress_tuning_job(name)
        return tuning_job

    def list_tuning_jobs(
        self, *, parent: str, **_
    ) -> Iterable[gca_tuning_job.TuningJob]:
        return [
            tuning_job
            for name, tuning_job in self._tuning_jobs.items()
            if name.startswith(parent + "/")
        ]

    def cancel_tuning_job(self, *, name: str, **_) -> None:
        tuning_job = self._tuning_jobs[name]
        assert tuning_job.state in (
            job_state.JobState.JOB_STATE_RUNNING, job_state.JobState.JOB_STATE_PENDING
        )
        tuning_job.state = job_state.JobState.JOB_STATE_CANCELLED


class MockTuningJobClientWithOverride(aiplatform_utils.ClientWithOverride):
    _is_temporary = False
    _default_version = compat.V1
    _version_map = (
        (compat.V1, MockGenAiTuningServiceClient),
        # v1beta1 version does not exist
        # (compat.V1BETA1, gen_ai_tuning_service_v1beta1.client.JobServiceClient),
    )


@pytest.mark.usefixtures("google_auth_mock")
class TestgenerativeModelTuning:
    """Unit tests for generative model tuning."""

    def setup_method(self):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @mock.patch.object(
        target=tuning.TuningJob,
        attribute="client_class",
        new=MockTuningJobClientWithOverride,
    )
    def test_genai_tuning_service_supervised_tuning_tune_model(self):
        sft_tuning_job = supervised_tuning.tune_model(
            source_model="gemini-1.0-pro-001",
            training_data="gs://some-bucket/some_dataset.jsonl",
            # Optional:
            validation_data="gs://some-bucket/some_dataset.jsonl",
            number_of_epochs=300,
            learning_rate_multiplier=1.0,
        )
        assert not sft_tuning_job.done()
        sft_tuning_job.wait_for_completion()
        assert sft_tuning_job.done()
        assert sft_tuning_job.state == job_state.JobState.JOB_STATE_SUCCEEDED
        assert sft_tuning_job._experiment_name
        assert sft_tuning_job._tuned_model_name
        assert sft_tuning_job._tuned_model_endpoint_name
