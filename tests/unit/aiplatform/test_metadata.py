# -*- coding: utf-8 -*-

# Copyright 2021 Google LLC
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
from unittest.mock import patch

import pytest

from google.cloud import aiplatform
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.metadata import constants
from google.cloud.aiplatform.metadata import metadata
from google.cloud.aiplatform_v1beta1 import (
    AddContextArtifactsAndExecutionsResponse,
    Event,
)
from google.cloud.aiplatform_v1beta1 import Artifact as GapicArtifact
from google.cloud.aiplatform_v1beta1 import Context as GapicContext
from google.cloud.aiplatform_v1beta1 import Execution as GapicExecution
from google.cloud.aiplatform_v1beta1 import (
    MetadataServiceClient,
    AddExecutionEventsResponse,
)
from google.cloud.aiplatform_v1beta1 import MetadataStore as GapicMetadataStore

# project
_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_PARENT = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/metadataStores/default"
)
_TEST_EXPERIMENT = "test-experiment"
_TEST_RUN = "run"

# resource attributes
_TEST_METADATA = {"test-param1": 1, "test-param2": "test-value", "test-param3": True}

# metadataStore
_TEST_METADATASTORE = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/metadataStores/default"
)

# context
_TEST_CONTEXT_ID = _TEST_EXPERIMENT
_TEST_CONTEXT_NAME = f"{_TEST_PARENT}/contexts/{_TEST_CONTEXT_ID}"

# execution
_TEST_EXECUTION_ID = f"{_TEST_EXPERIMENT}-{_TEST_RUN}"
_TEST_EXECUTION_NAME = f"{_TEST_PARENT}/executions/{_TEST_EXECUTION_ID}"

# artifact
_TEST_ARTIFACT_ID = f"{_TEST_EXPERIMENT}-{_TEST_RUN}-metrics"
_TEST_ARTIFACT_NAME = f"{_TEST_PARENT}/artifacts/{_TEST_ARTIFACT_ID}"

# parameters
_TEST_PARAMS = {"learning_rate": 0.01, "dropout": 0.2}

# metrics
_TEST_METRICS = {"rmse": 222, "accuracy": 1}


@pytest.fixture
def get_metadata_store_mock():
    with patch.object(
        MetadataServiceClient, "get_metadata_store"
    ) as get_metadata_store_mock:
        get_metadata_store_mock.return_value = GapicMetadataStore(
            name=_TEST_METADATASTORE,
        )
        yield get_metadata_store_mock


@pytest.fixture
def get_context_mock():
    with patch.object(MetadataServiceClient, "get_context") as get_context_mock:
        get_context_mock.return_value = GapicContext(
            name=_TEST_CONTEXT_NAME,
            display_name=_TEST_EXPERIMENT,
            schema_title=constants.SYSTEM_EXPERIMENT,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_EXPERIMENT],
            metadata={constants.UI_DETECTION_KEY: constants.UI_DETECTION_VALUE},
        )
        yield get_context_mock


@pytest.fixture
def add_context_artifacts_and_executions_mock():
    with patch.object(
        MetadataServiceClient, "add_context_artifacts_and_executions"
    ) as add_context_artifacts_and_executions_mock:
        add_context_artifacts_and_executions_mock.return_value = (
            AddContextArtifactsAndExecutionsResponse()
        )
        yield add_context_artifacts_and_executions_mock


@pytest.fixture
def get_execution_mock():
    with patch.object(MetadataServiceClient, "get_execution") as get_execution_mock:
        get_execution_mock.return_value = GapicExecution(
            name=_TEST_EXECUTION_NAME,
            display_name=_TEST_RUN,
            schema_title=constants.SYSTEM_RUN,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_RUN],
        )
        yield get_execution_mock


@pytest.fixture
def update_execution_mock():
    with patch.object(
        MetadataServiceClient, "update_execution"
    ) as update_execution_mock:
        update_execution_mock.return_value = GapicExecution(
            name=_TEST_EXECUTION_NAME,
            display_name=_TEST_RUN,
            schema_title=constants.SYSTEM_RUN,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_RUN],
            metadata=_TEST_PARAMS,
        )
        yield update_execution_mock


@pytest.fixture
def add_execution_events_mock():
    with patch.object(
        MetadataServiceClient, "add_execution_events"
    ) as add_execution_events_mock:
        add_execution_events_mock.return_value = AddExecutionEventsResponse()
        yield add_execution_events_mock


@pytest.fixture
def get_artifact_mock():
    with patch.object(MetadataServiceClient, "get_artifact") as get_artifact_mock:
        get_artifact_mock.return_value = GapicArtifact(
            name=_TEST_ARTIFACT_NAME,
            display_name=_TEST_ARTIFACT_ID,
            schema_title=constants.SYSTEM_METRICS,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_METRICS],
        )
        yield get_artifact_mock


@pytest.fixture
def update_artifact_mock():
    with patch.object(MetadataServiceClient, "update_artifact") as update_artifact_mock:
        update_artifact_mock.return_value = GapicArtifact(
            name=_TEST_ARTIFACT_NAME,
            display_name=_TEST_ARTIFACT_ID,
            schema_title=constants.SYSTEM_METRICS,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_METRICS],
            metadata=_TEST_METRICS,
        )
        yield update_artifact_mock


class TestMetadata:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)
        reload(metadata)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_init_experiment_with_existing_metadataStore_and_context(
        self, get_metadata_store_mock, get_context_mock
    ):
        aiplatform.init(
            project=_TEST_PROJECT, location=_TEST_LOCATION, experiment=_TEST_EXPERIMENT
        )

        get_metadata_store_mock.assert_called_once_with(name=_TEST_METADATASTORE)
        get_context_mock.assert_called_once_with(name=_TEST_CONTEXT_NAME)

    @pytest.mark.usefixtures("get_metadata_store_mock")
    @pytest.mark.usefixtures("get_context_mock")
    def test_set_run_with_existing_execution_and_artifact(
        self,
        get_execution_mock,
        add_context_artifacts_and_executions_mock,
        get_artifact_mock,
        add_execution_events_mock,
    ):
        aiplatform.init(
            project=_TEST_PROJECT, location=_TEST_LOCATION, experiment=_TEST_EXPERIMENT
        )
        aiplatform.set_run(_TEST_RUN)

        get_execution_mock.assert_called_once_with(name=_TEST_EXECUTION_NAME)
        add_context_artifacts_and_executions_mock.assert_called_once_with(
            context=_TEST_CONTEXT_NAME,
            artifacts=None,
            executions=[_TEST_EXECUTION_NAME],
        )
        get_artifact_mock.assert_called_once_with(name=_TEST_ARTIFACT_NAME)
        add_execution_events_mock.assert_called_once_with(
            execution=_TEST_EXECUTION_NAME,
            events=[Event(artifact=_TEST_ARTIFACT_NAME, type_=Event.Type.OUTPUT)],
        )

    @pytest.mark.usefixtures("get_metadata_store_mock")
    @pytest.mark.usefixtures("get_context_mock")
    @pytest.mark.usefixtures("get_execution_mock")
    @pytest.mark.usefixtures("add_context_artifacts_and_executions_mock")
    @pytest.mark.usefixtures("get_artifact_mock")
    @pytest.mark.usefixtures("add_execution_events_mock")
    def test_log_params(
        self, update_execution_mock,
    ):
        aiplatform.init(
            project=_TEST_PROJECT, location=_TEST_LOCATION, experiment=_TEST_EXPERIMENT
        )
        aiplatform.set_run(_TEST_RUN)
        aiplatform.log_params(_TEST_PARAMS)

        updated_execution = GapicExecution(
            name=_TEST_EXECUTION_NAME,
            display_name=_TEST_RUN,
            schema_title=constants.SYSTEM_RUN,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_RUN],
            metadata=_TEST_PARAMS,
        )

        update_execution_mock.assert_called_once_with(execution=updated_execution)

    @pytest.mark.usefixtures("get_metadata_store_mock")
    @pytest.mark.usefixtures("get_context_mock")
    @pytest.mark.usefixtures("get_execution_mock")
    @pytest.mark.usefixtures("add_context_artifacts_and_executions_mock")
    @pytest.mark.usefixtures("get_artifact_mock")
    @pytest.mark.usefixtures("add_execution_events_mock")
    def test_log_metrics(
        self, update_artifact_mock,
    ):
        aiplatform.init(
            project=_TEST_PROJECT, location=_TEST_LOCATION, experiment=_TEST_EXPERIMENT
        )
        aiplatform.set_run(_TEST_RUN)
        aiplatform.log_metrics(_TEST_METRICS)

        updated_artifact = GapicArtifact(
            name=_TEST_ARTIFACT_NAME,
            display_name=_TEST_ARTIFACT_ID,
            schema_title=constants.SYSTEM_METRICS,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_METRICS],
            metadata=_TEST_METRICS,
        )

        update_artifact_mock.assert_called_once_with(artifact=updated_artifact)
