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
from unittest.mock import patch

import pytest
from google.api_core import exceptions

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.compat.types import event as gca_event
from google.cloud.aiplatform.metadata import artifact
from google.cloud.aiplatform.metadata import context
from google.cloud.aiplatform.metadata import execution
from google.cloud.aiplatform.metadata import utils as metadata_utils
from google.cloud.aiplatform_v1 import (
    MetadataServiceClient,
    AddExecutionEventsResponse,
    Event,
    LineageSubgraph,
    Execution as GapicExecution,
    Context as GapicContext,
    Artifact as GapicArtifact,
    MetadataStore as GapicMetadataStore,
    AddContextArtifactsAndExecutionsResponse,
)

import constants as test_constants

# project
_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_METADATA_STORE = "test-metadata-store"
_TEST_ALT_LOCATION = "europe-west4"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/metadataStores/{_TEST_METADATA_STORE}"

# resource attributes
_TEST_DISPLAY_NAME = "test-display-name"
_TEST_SCHEMA_TITLE = "test.Example"
_TEST_SCHEMA_VERSION = "0.0.1"
_TEST_DESCRIPTION = "test description"
_TEST_METADATA = {"test-param1": 1, "test-param2": "test-value", "test-param3": True}
_TEST_UPDATED_METADATA = {
    "test-param1": 2,
    "test-param2": "test-value-1",
    "test-param3": False,
}
_TEST_ORDER_BY = "test_order_by"

# context
_TEST_CONTEXT_ID = "test-context-id"
_TEST_CONTEXT_NAME = f"{_TEST_PARENT}/contexts/{_TEST_CONTEXT_ID}"

# artifact
_TEST_ARTIFACT_ID = "test-artifact-id"
_TEST_ARTIFACT_NAME = f"{_TEST_PARENT}/artifacts/{_TEST_ARTIFACT_ID}"

# execution
_TEST_EXECUTION_ID = "test-execution-id"
_TEST_EXECUTION_NAME = f"{_TEST_PARENT}/executions/{_TEST_EXECUTION_ID}"


@pytest.fixture
def get_context_mock():
    with patch.object(MetadataServiceClient, "get_context") as get_context_mock:
        get_context_mock.return_value = GapicContext(
            name=_TEST_CONTEXT_NAME,
            display_name=_TEST_DISPLAY_NAME,
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
        )
        yield get_context_mock


@pytest.fixture
def get_context_for_get_or_create_mock():
    with patch.object(
        MetadataServiceClient, "get_context"
    ) as get_context_for_get_or_create_mock:
        get_context_for_get_or_create_mock.side_effect = exceptions.NotFound(
            "test: Context Not Found"
        )
        yield get_context_for_get_or_create_mock


@pytest.fixture
def create_context_mock():
    with patch.object(MetadataServiceClient, "create_context") as create_context_mock:
        create_context_mock.return_value = GapicContext(
            name=_TEST_CONTEXT_NAME,
            display_name=_TEST_DISPLAY_NAME,
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
        )
        yield create_context_mock


@pytest.fixture
def list_contexts_mock():
    with patch.object(MetadataServiceClient, "list_contexts") as list_contexts_mock:
        list_contexts_mock.return_value = [
            GapicContext(
                name=_TEST_CONTEXT_NAME,
                display_name=_TEST_DISPLAY_NAME,
                schema_title=_TEST_SCHEMA_TITLE,
                schema_version=_TEST_SCHEMA_VERSION,
                description=_TEST_DESCRIPTION,
                metadata=_TEST_METADATA,
            ),
            GapicContext(
                name=_TEST_CONTEXT_NAME,
                display_name=_TEST_DISPLAY_NAME,
                schema_title=_TEST_SCHEMA_TITLE,
                schema_version=_TEST_SCHEMA_VERSION,
                description=_TEST_DESCRIPTION,
                metadata=_TEST_METADATA,
            ),
        ]
        yield list_contexts_mock


@pytest.fixture
def update_context_mock():
    with patch.object(MetadataServiceClient, "update_context") as update_context_mock:
        update_context_mock.return_value = GapicContext(
            name=_TEST_CONTEXT_NAME,
            display_name=_TEST_DISPLAY_NAME,
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        yield update_context_mock


@pytest.fixture
def update_context_with_errors_mock():
    with patch.object(
        MetadataServiceClient, "update_context"
    ) as update_context_with_errors_mock:
        update_context_with_errors_mock.side_effect = [
            exceptions.Aborted(
                "Specified Context `etag`: `1` does not match server `etag`: `2`"
            ),
            GapicContext(
                name=_TEST_CONTEXT_NAME,
                display_name=_TEST_DISPLAY_NAME,
                schema_title=_TEST_SCHEMA_TITLE,
                schema_version=_TEST_SCHEMA_VERSION,
                description=_TEST_DESCRIPTION,
                metadata=_TEST_UPDATED_METADATA,
            ),
        ]
        yield update_context_with_errors_mock


@pytest.fixture
def update_context_with_errors_mock_2():
    with patch.object(
        MetadataServiceClient, "update_context"
    ) as update_context_with_errors_mock_2:
        update_context_with_errors_mock_2.side_effect = [
            exceptions.Aborted(
                "Specified Context `etag`: `2` does not match server `etag`: `1`"
            )
        ]
        yield update_context_with_errors_mock_2


@pytest.fixture
def update_context_with_errors_mock_3():
    with patch.object(
        MetadataServiceClient, "update_context"
    ) as update_context_with_errors_mock_3:
        update_context_with_errors_mock_3.side_effect = [
            exceptions.Aborted(
                "Specified Context `etag`: `1` does not match server `etag`: `2`"
            )
        ] * 6
        yield update_context_with_errors_mock_2


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
            display_name=_TEST_DISPLAY_NAME,
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
        )
        yield get_execution_mock


@pytest.fixture
def get_execution_for_get_or_create_mock():
    with patch.object(
        MetadataServiceClient, "get_execution"
    ) as get_execution_for_get_or_create_mock:
        get_execution_for_get_or_create_mock.side_effect = exceptions.NotFound(
            "test: Execution Not Found"
        )
        yield get_execution_for_get_or_create_mock


@pytest.fixture
def create_execution_mock():
    with patch.object(
        MetadataServiceClient, "create_execution"
    ) as create_execution_mock:
        create_execution_mock.return_value = GapicExecution(
            name=_TEST_EXECUTION_NAME,
            display_name=_TEST_DISPLAY_NAME,
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
            state=GapicExecution.State.RUNNING,
        )
        yield create_execution_mock


@pytest.fixture
def list_executions_mock():
    with patch.object(MetadataServiceClient, "list_executions") as list_executions_mock:
        list_executions_mock.return_value = [
            GapicExecution(
                name=_TEST_EXECUTION_NAME,
                display_name=_TEST_DISPLAY_NAME,
                schema_title=_TEST_SCHEMA_TITLE,
                schema_version=_TEST_SCHEMA_VERSION,
                description=_TEST_DESCRIPTION,
                metadata=_TEST_METADATA,
            ),
            GapicExecution(
                name=_TEST_EXECUTION_NAME,
                display_name=_TEST_DISPLAY_NAME,
                schema_title=_TEST_SCHEMA_TITLE,
                schema_version=_TEST_SCHEMA_VERSION,
                description=_TEST_DESCRIPTION,
                metadata=_TEST_METADATA,
            ),
        ]
        yield list_executions_mock


@pytest.fixture
def query_execution_inputs_and_outputs_mock():
    with patch.object(
        MetadataServiceClient, "query_execution_inputs_and_outputs"
    ) as query_execution_inputs_and_outputs_mock:
        query_execution_inputs_and_outputs_mock.return_value = LineageSubgraph(
            artifacts=[
                GapicArtifact(
                    name=_TEST_ARTIFACT_NAME,
                    display_name=_TEST_DISPLAY_NAME,
                    schema_title=_TEST_SCHEMA_TITLE,
                    schema_version=_TEST_SCHEMA_VERSION,
                    description=_TEST_DESCRIPTION,
                    metadata=_TEST_METADATA,
                ),
            ],
            events=[
                gca_event.Event(
                    artifact=_TEST_ARTIFACT_NAME,
                    execution=_TEST_EXECUTION_NAME,
                    type_=gca_event.Event.Type.OUTPUT,
                )
            ],
        )
        yield query_execution_inputs_and_outputs_mock


@pytest.fixture
def update_execution_mock():
    with patch.object(
        MetadataServiceClient, "update_execution"
    ) as update_execution_mock:
        update_execution_mock.return_value = GapicExecution(
            name=_TEST_EXECUTION_NAME,
            display_name=_TEST_DISPLAY_NAME,
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
            state=GapicExecution.State.RUNNING,
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
            display_name=_TEST_DISPLAY_NAME,
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
        )
        yield get_artifact_mock


@pytest.fixture
def get_artifact_for_get_or_create_mock():
    with patch.object(
        MetadataServiceClient, "get_artifact"
    ) as get_artifact_for_get_or_create_mock:
        get_artifact_for_get_or_create_mock.side_effect = exceptions.NotFound(
            "test: Artifact Not Found"
        )
        yield get_artifact_for_get_or_create_mock


@pytest.fixture
def create_artifact_mock():
    with patch.object(MetadataServiceClient, "create_artifact") as create_artifact_mock:
        create_artifact_mock.return_value = GapicArtifact(
            name=_TEST_ARTIFACT_NAME,
            display_name=_TEST_DISPLAY_NAME,
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
            state=GapicArtifact.State.LIVE,
        )
        yield create_artifact_mock


@pytest.fixture
def list_artifacts_mock():
    with patch.object(MetadataServiceClient, "list_artifacts") as list_artifacts_mock:
        list_artifacts_mock.return_value = [
            GapicArtifact(
                name=_TEST_ARTIFACT_NAME,
                display_name=_TEST_DISPLAY_NAME,
                schema_title=_TEST_SCHEMA_TITLE,
                schema_version=_TEST_SCHEMA_VERSION,
                description=_TEST_DESCRIPTION,
                metadata=_TEST_METADATA,
            ),
            GapicArtifact(
                name=_TEST_ARTIFACT_NAME,
                display_name=_TEST_DISPLAY_NAME,
                schema_title=_TEST_SCHEMA_TITLE,
                schema_version=_TEST_SCHEMA_VERSION,
                description=_TEST_DESCRIPTION,
                metadata=_TEST_METADATA,
            ),
        ]
        yield list_artifacts_mock


@pytest.fixture
def update_artifact_mock():
    with patch.object(MetadataServiceClient, "update_artifact") as update_artifact_mock:
        update_artifact_mock.return_value = GapicArtifact(
            name=_TEST_ARTIFACT_NAME,
            display_name=_TEST_DISPLAY_NAME,
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
            state=GapicArtifact.State.LIVE,
        )
        yield update_artifact_mock


@pytest.fixture
def get_metadata_store_mock():
    with patch.object(
        MetadataServiceClient, "get_metadata_store"
    ) as get_metadata_store_mock:
        get_metadata_store_mock.return_value = GapicMetadataStore(
            name=_TEST_METADATA_STORE
        )
        yield get_metadata_store_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestContext:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_init_context(self, get_context_mock):
        aiplatform.init(project=_TEST_PROJECT)
        context.Context(resource_name=_TEST_CONTEXT_NAME)
        get_context_mock.assert_called_once_with(
            name=_TEST_CONTEXT_NAME, retry=base._DEFAULT_RETRY
        )

    def test_init_context_with_id(self, get_context_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        context.Context(
            resource_name=_TEST_CONTEXT_ID, metadata_store_id=_TEST_METADATA_STORE
        )
        get_context_mock.assert_called_once_with(
            name=_TEST_CONTEXT_NAME, retry=base._DEFAULT_RETRY
        )

    def test_get_or_create_context(
        self, get_context_for_get_or_create_mock, create_context_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        my_context = context.Context.get_or_create(
            resource_id=_TEST_CONTEXT_ID,
            schema_title=_TEST_SCHEMA_TITLE,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
            metadata_store_id=_TEST_METADATA_STORE,
        )

        expected_context = GapicContext(
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
        )
        get_context_for_get_or_create_mock.assert_called_once_with(
            name=_TEST_CONTEXT_NAME, retry=base._DEFAULT_RETRY
        )
        create_context_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            context_id=_TEST_CONTEXT_ID,
            context=expected_context,
        )

        expected_context.name = _TEST_CONTEXT_NAME
        assert my_context._gca_resource == expected_context

    def test_get_context(self, get_context_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_context = context.Context.get(
            resource_id=_TEST_CONTEXT_ID,
            metadata_store_id=_TEST_METADATA_STORE,
        )

        expected_context = GapicContext(
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
        )
        get_context_mock.assert_called_once_with(
            name=_TEST_CONTEXT_NAME, retry=base._DEFAULT_RETRY
        )

        expected_context.name = _TEST_CONTEXT_NAME
        assert my_context._gca_resource == expected_context

    @pytest.mark.usefixtures("get_context_mock")
    @pytest.mark.usefixtures("create_context_mock")
    def test_update_context(self, update_context_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_context = context.Context._create(
            resource_id=_TEST_CONTEXT_ID,
            schema_title=_TEST_SCHEMA_TITLE,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
            metadata_store_id=_TEST_METADATA_STORE,
        )
        my_context.update(_TEST_UPDATED_METADATA)

        updated_context = GapicContext(
            name=_TEST_CONTEXT_NAME,
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )

        update_context_mock.assert_called_once_with(context=updated_context)
        assert my_context._gca_resource == updated_context

    @pytest.mark.usefixtures("get_context_mock")
    @pytest.mark.usefixtures("create_context_mock")
    def test_update_context_with_retry_success(self, update_context_with_errors_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_context = context.Context._create(
            resource_id=_TEST_CONTEXT_ID,
            schema_title=_TEST_SCHEMA_TITLE,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
            metadata_store_id=_TEST_METADATA_STORE,
        )
        my_context.update(_TEST_UPDATED_METADATA)

        updated_context = GapicContext(
            name=_TEST_CONTEXT_NAME,
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )

        update_context_with_errors_mock.assert_called_with(context=updated_context)
        assert my_context._gca_resource == updated_context

    @pytest.mark.usefixtures("get_context_mock")
    @pytest.mark.usefixtures("create_context_mock")
    @pytest.mark.usefixtures("update_context_with_errors_mock_2")
    def test_update_context_with_retry_etag_order_failure(self):
        aiplatform.init(project=_TEST_PROJECT)

        my_context = context.Context._create(
            resource_id=_TEST_CONTEXT_ID,
            schema_title=_TEST_SCHEMA_TITLE,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
            metadata_store_id=_TEST_METADATA_STORE,
        )
        with pytest.raises(exceptions.Aborted):
            my_context.update(_TEST_UPDATED_METADATA)

    @pytest.mark.usefixtures("get_context_mock")
    @pytest.mark.usefixtures("create_context_mock")
    @pytest.mark.usefixtures("update_context_with_errors_mock_3")
    def test_update_context_with_retry_too_many_error_failure(self):
        aiplatform.init(project=_TEST_PROJECT)

        my_context = context.Context._create(
            resource_id=_TEST_CONTEXT_ID,
            schema_title=_TEST_SCHEMA_TITLE,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
            metadata_store_id=_TEST_METADATA_STORE,
        )
        with pytest.raises(exceptions.Aborted):
            my_context.update(_TEST_UPDATED_METADATA)

    @pytest.mark.usefixtures("get_context_mock")
    def test_list_contexts(self, list_contexts_mock):
        aiplatform.init(project=_TEST_PROJECT)

        filter_query = "test-filter"
        context_list = context.Context.list(
            filter=filter_query,
            metadata_store_id=_TEST_METADATA_STORE,
            order_by=_TEST_ORDER_BY,
        )

        expected_context = GapicContext(
            name=_TEST_CONTEXT_NAME,
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
        )

        list_contexts_mock.assert_called_once_with(
            request={
                "parent": _TEST_PARENT,
                "filter": filter_query,
                "order_by": _TEST_ORDER_BY,
            }
        )
        assert len(context_list) == 2
        # pylint: disable-next=protected-access
        assert context_list[0]._gca_resource == expected_context
        # pylint: disable-next=protected-access
        assert context_list[1]._gca_resource == expected_context

    @pytest.mark.usefixtures("get_context_mock")
    def test_add_artifacts_and_executions(
        self, add_context_artifacts_and_executions_mock
    ):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        my_context = context.Context.get_or_create(
            resource_id=_TEST_CONTEXT_ID,
            schema_title=_TEST_SCHEMA_TITLE,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
            metadata_store_id=_TEST_METADATA_STORE,
        )

        my_context.add_artifacts_and_executions(
            artifact_resource_names=[_TEST_ARTIFACT_NAME],
            execution_resource_names=[_TEST_EXECUTION_NAME],
        )
        add_context_artifacts_and_executions_mock.assert_called_once_with(
            context=_TEST_CONTEXT_NAME,
            artifacts=[_TEST_ARTIFACT_NAME],
            executions=[_TEST_EXECUTION_NAME],
        )

    @pytest.mark.usefixtures("get_context_mock")
    def test_add_artifacts_only(self, add_context_artifacts_and_executions_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        my_context = context.Context.get_or_create(
            resource_id=_TEST_CONTEXT_ID,
            schema_title=_TEST_SCHEMA_TITLE,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
            metadata_store_id=_TEST_METADATA_STORE,
        )

        my_context.add_artifacts_and_executions(
            artifact_resource_names=[_TEST_ARTIFACT_NAME]
        )
        add_context_artifacts_and_executions_mock.assert_called_once_with(
            context=_TEST_CONTEXT_NAME,
            artifacts=[_TEST_ARTIFACT_NAME],
            executions=None,
        )

    @pytest.mark.usefixtures("get_context_mock")
    def test_add_executions_only(self, add_context_artifacts_and_executions_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        my_context = context.Context.get_or_create(
            resource_id=_TEST_CONTEXT_ID,
            schema_title=_TEST_SCHEMA_TITLE,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
            metadata_store_id=_TEST_METADATA_STORE,
        )

        my_context.add_artifacts_and_executions(
            execution_resource_names=[_TEST_EXECUTION_NAME]
        )
        add_context_artifacts_and_executions_mock.assert_called_once_with(
            context=_TEST_CONTEXT_NAME,
            artifacts=None,
            executions=[_TEST_EXECUTION_NAME],
        )


_VERTEX_MODEL_ARTIFACT_URI = f"https://{_TEST_LOCATION}-aiplatform.googleapis.com/v1/{test_constants.ModelConstants._TEST_MODEL_OBJ_WITH_VERSION.name}"


@pytest.fixture
def list_vertex_model_artifact_mock():
    with patch.object(MetadataServiceClient, "list_artifacts") as list_artifacts_mock:
        list_artifacts_mock.return_value = [
            GapicArtifact(
                name=_TEST_ARTIFACT_NAME,
                uri=_VERTEX_MODEL_ARTIFACT_URI,
                display_name=_TEST_DISPLAY_NAME,
                schema_title=_TEST_SCHEMA_TITLE,
                schema_version=_TEST_SCHEMA_VERSION,
                description=_TEST_DESCRIPTION,
                metadata=_TEST_METADATA,
            )
        ]
        yield list_artifacts_mock


@pytest.fixture
def list_artifact_empty_mock():
    with patch.object(MetadataServiceClient, "list_artifacts") as list_artifacts_mock:
        list_artifacts_mock.return_value = []
        yield list_artifacts_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestExecution:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_init_execution(self, get_execution_mock):
        aiplatform.init(project=_TEST_PROJECT)
        execution.Execution(execution_name=_TEST_EXECUTION_NAME)
        get_execution_mock.assert_called_once_with(
            name=_TEST_EXECUTION_NAME, retry=base._DEFAULT_RETRY
        )

    def test_init_execution_with_id(self, get_execution_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        execution.Execution(
            execution_name=_TEST_EXECUTION_ID, metadata_store_id=_TEST_METADATA_STORE
        )
        get_execution_mock.assert_called_once_with(
            name=_TEST_EXECUTION_NAME, retry=base._DEFAULT_RETRY
        )

    def test_get_or_create_execution(
        self, get_execution_for_get_or_create_mock, create_execution_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        my_execution = execution.Execution.get_or_create(
            resource_id=_TEST_EXECUTION_ID,
            schema_title=_TEST_SCHEMA_TITLE,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
            metadata_store_id=_TEST_METADATA_STORE,
        )

        expected_execution = GapicExecution(
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
            state=GapicExecution.State.RUNNING,
        )
        get_execution_for_get_or_create_mock.assert_called_once_with(
            name=_TEST_EXECUTION_NAME, retry=base._DEFAULT_RETRY
        )
        create_execution_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            execution_id=_TEST_EXECUTION_ID,
            execution=expected_execution,
        )

        expected_execution.name = _TEST_EXECUTION_NAME
        assert my_execution._gca_resource == expected_execution

    def test_get_execution(self, get_execution_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_execution = execution.Execution.get(
            resource_id=_TEST_EXECUTION_ID,
            metadata_store_id=_TEST_METADATA_STORE,
        )

        expected_execution = GapicExecution(
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
        )
        get_execution_mock.assert_called_once_with(
            name=_TEST_EXECUTION_NAME, retry=base._DEFAULT_RETRY
        )

        expected_execution.name = _TEST_EXECUTION_NAME
        assert my_execution._gca_resource == expected_execution

    @pytest.mark.usefixtures("get_execution_mock")
    @pytest.mark.usefixtures("create_execution_mock")
    def test_update_execution(self, update_execution_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_execution = execution.Execution._create(
            resource_id=_TEST_EXECUTION_ID,
            schema_title=_TEST_SCHEMA_TITLE,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
            metadata_store_id=_TEST_METADATA_STORE,
        )
        my_execution.update(metadata=_TEST_UPDATED_METADATA)

        updated_execution = GapicExecution(
            name=_TEST_EXECUTION_NAME,
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
            state=GapicExecution.State.RUNNING,
        )

        update_execution_mock.assert_called_once_with(execution=updated_execution)
        assert my_execution._gca_resource == updated_execution

    @pytest.mark.usefixtures("get_execution_mock")
    def test_list_executions(self, list_executions_mock):
        aiplatform.init(project=_TEST_PROJECT)

        filter_query = "test-filter"
        execution_list = execution.Execution.list(
            filter=filter_query,
            metadata_store_id=_TEST_METADATA_STORE,
            order_by=_TEST_ORDER_BY,
        )

        expected_execution = GapicExecution(
            name=_TEST_EXECUTION_NAME,
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
        )

        list_executions_mock.assert_called_once_with(
            request={
                "parent": _TEST_PARENT,
                "filter": filter_query,
                "order_by": _TEST_ORDER_BY,
            }
        )
        assert len(execution_list) == 2
        # pylint: disable-next=protected-access
        assert execution_list[0]._gca_resource == expected_execution
        # pylint: disable-next=protected-access
        assert execution_list[1]._gca_resource == expected_execution

    @pytest.mark.usefixtures("get_execution_mock", "get_artifact_mock")
    def test_add_artifact(self, add_execution_events_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        my_execution = execution.Execution.get_or_create(
            resource_id=_TEST_EXECUTION_ID,
            schema_title=_TEST_SCHEMA_TITLE,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
            metadata_store_id=_TEST_METADATA_STORE,
        )

        my_artifact = aiplatform.Artifact(_TEST_ARTIFACT_ID)
        my_execution.assign_output_artifacts(artifacts=[my_artifact])
        add_execution_events_mock.assert_called_once_with(
            execution=_TEST_EXECUTION_NAME,
            events=[Event(artifact=_TEST_ARTIFACT_NAME, type_=Event.Type.OUTPUT)],
        )

    @pytest.mark.usefixtures("get_execution_mock", "get_model_with_version_mock")
    def test_add_vertex_model(
        self, add_execution_events_mock, list_vertex_model_artifact_mock
    ):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        my_execution = execution.Execution.get_or_create(
            resource_id=_TEST_EXECUTION_ID,
            schema_title=_TEST_SCHEMA_TITLE,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
            metadata_store_id=_TEST_METADATA_STORE,
        )

        my_model = aiplatform.Model(test_constants.ModelConstants._TEST_MODEL_NAME)
        my_execution.assign_output_artifacts(artifacts=[my_model])

        list_vertex_model_artifact_mock.assert_called_once_with(
            request=dict(
                parent="projects/test-project/locations/us-central1/metadataStores/default",
                filter=metadata_utils._make_filter_string(
                    schema_title="google.VertexModel", uri=_VERTEX_MODEL_ARTIFACT_URI
                ),
            )
        )

        add_execution_events_mock.assert_called_once_with(
            execution=_TEST_EXECUTION_NAME,
            events=[Event(artifact=_TEST_ARTIFACT_NAME, type_=Event.Type.OUTPUT)],
        )

    @pytest.mark.usefixtures(
        "get_execution_mock", "get_model_with_version_mock", "get_metadata_store_mock"
    )
    def test_add_vertex_model_not_resolved(
        self, add_execution_events_mock, list_artifact_empty_mock, create_artifact_mock
    ):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        my_execution = execution.Execution.get_or_create(
            resource_id=_TEST_EXECUTION_ID,
            schema_title=_TEST_SCHEMA_TITLE,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
            metadata_store_id=_TEST_METADATA_STORE,
        )

        my_model = aiplatform.Model(test_constants.ModelConstants._TEST_MODEL_NAME)
        my_execution.assign_output_artifacts(artifacts=[my_model])

        list_artifact_empty_mock.assert_called_once_with(
            request=dict(
                parent="projects/test-project/locations/us-central1/metadataStores/default",
                filter=metadata_utils._make_filter_string(
                    schema_title="google.VertexModel", uri=_VERTEX_MODEL_ARTIFACT_URI
                ),
            )
        )

        expected_artifact = GapicArtifact(
            schema_title="google.VertexModel",
            display_name=test_constants.ModelConstants._TEST_MODEL_OBJ_WITH_VERSION.display_name,
            uri=_VERTEX_MODEL_ARTIFACT_URI,
            metadata={
                "resourceName": test_constants.ModelConstants._TEST_MODEL_OBJ_WITH_VERSION.name
            },
            state=GapicArtifact.State.LIVE,
        )

        create_artifact_mock.assert_called_once_with(
            parent="projects/test-project/locations/us-central1/metadataStores/default",
            artifact=expected_artifact,
            artifact_id=None,
        )

        add_execution_events_mock.assert_called_once_with(
            execution=_TEST_EXECUTION_NAME,
            events=[Event(artifact=_TEST_ARTIFACT_NAME, type_=Event.Type.OUTPUT)],
        )

    @pytest.mark.usefixtures("get_execution_mock")
    def test_query_input_and_output_artifacts(
        self, query_execution_inputs_and_outputs_mock
    ):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        my_execution = execution.Execution.get_or_create(
            resource_id=_TEST_EXECUTION_ID,
            schema_title=_TEST_SCHEMA_TITLE,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
            metadata_store_id=_TEST_METADATA_STORE,
        )

        artifact_list = my_execution.get_output_artifacts()

        expected_artifact = GapicArtifact(
            name=_TEST_ARTIFACT_NAME,
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
        )

        query_execution_inputs_and_outputs_mock.assert_called_once_with(
            execution=_TEST_EXECUTION_NAME,
        )
        assert len(artifact_list) == 1
        assert artifact_list[0]._gca_resource == expected_artifact


@pytest.mark.usefixtures("google_auth_mock")
class TestArtifact:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_init_artifact(self, get_artifact_mock):
        aiplatform.init(project=_TEST_PROJECT)
        artifact.Artifact(artifact_name=_TEST_ARTIFACT_NAME)
        get_artifact_mock.assert_called_once_with(
            name=_TEST_ARTIFACT_NAME, retry=base._DEFAULT_RETRY
        )

    def test_init_artifact_with_id(self, get_artifact_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        artifact.Artifact(
            artifact_name=_TEST_ARTIFACT_ID, metadata_store_id=_TEST_METADATA_STORE
        )
        get_artifact_mock.assert_called_once_with(
            name=_TEST_ARTIFACT_NAME, retry=base._DEFAULT_RETRY
        )

    def test_extract_metadata_store_id_with_valid_resource_name(self):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        assert "store_id" == artifact.Artifact._extract_metadata_store_id(
            resource_name="projects/project/locations/location/metadataStores/store_id/resource_type/resource_id",
            resource_noun="resource_type",
        )
        assert "store_id" == artifact.Artifact._extract_metadata_store_id(
            resource_name="projects/project/locations/location/metadataStores/store_id/resource_type/resource_id@version",
            resource_noun="resource_type",
        )

    def test_extract_metadata_store_id_with_invalid_resource_name(self):
        invalid_resouce_name = (
            "projects/project/locations/location/resource_type/resource_id/"
        )
        with pytest.raises(ValueError):
            artifact.Artifact._extract_metadata_store_id(
                resource_name=invalid_resouce_name, resource_noun="resource_type"
            )

    def test_get_or_create_artifact(
        self, get_artifact_for_get_or_create_mock, create_artifact_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        my_artifact = artifact.Artifact.get_or_create(
            resource_id=_TEST_ARTIFACT_ID,
            schema_title=_TEST_SCHEMA_TITLE,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
            metadata_store_id=_TEST_METADATA_STORE,
        )

        expected_artifact = GapicArtifact(
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
            state=GapicArtifact.State.LIVE,
        )
        get_artifact_for_get_or_create_mock.assert_called_once_with(
            name=_TEST_ARTIFACT_NAME, retry=base._DEFAULT_RETRY
        )
        create_artifact_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            artifact_id=_TEST_ARTIFACT_ID,
            artifact=expected_artifact,
        )

        expected_artifact.name = _TEST_ARTIFACT_NAME
        assert my_artifact._gca_resource == expected_artifact

    def test_get_artifact(self, get_artifact_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_artifact = artifact.Artifact.get(
            resource_id=_TEST_ARTIFACT_ID,
            metadata_store_id=_TEST_METADATA_STORE,
        )

        expected_artifact = GapicArtifact(
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
        )
        get_artifact_mock.assert_called_once_with(
            name=_TEST_ARTIFACT_NAME, retry=base._DEFAULT_RETRY
        )

        expected_artifact.name = _TEST_ARTIFACT_NAME
        assert my_artifact._gca_resource == expected_artifact

    @pytest.mark.usefixtures("get_artifact_mock")
    @pytest.mark.usefixtures("create_artifact_mock")
    def test_update_artifact(self, update_artifact_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_artifact = artifact.Artifact._create(
            resource_id=_TEST_ARTIFACT_ID,
            schema_title=_TEST_SCHEMA_TITLE,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
            metadata_store_id=_TEST_METADATA_STORE,
        )
        my_artifact.update(metadata=_TEST_UPDATED_METADATA)

        updated_artifact = GapicArtifact(
            name=_TEST_ARTIFACT_NAME,
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
            state=GapicArtifact.State.LIVE,
        )

        update_artifact_mock.assert_called_once_with(artifact=updated_artifact)
        assert my_artifact._gca_resource == updated_artifact

    @pytest.mark.usefixtures("get_artifact_mock")
    def test_list_artifacts(self, list_artifacts_mock):
        aiplatform.init(project=_TEST_PROJECT)

        filter_query = "test-filter"
        artifact_list = artifact.Artifact.list(
            filter=filter_query,
            metadata_store_id=_TEST_METADATA_STORE,
            order_by=_TEST_ORDER_BY,
        )

        expected_artifact = GapicArtifact(
            name=_TEST_ARTIFACT_NAME,
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
        )

        list_artifacts_mock.assert_called_once_with(
            request={
                "parent": _TEST_PARENT,
                "filter": filter_query,
                "order_by": _TEST_ORDER_BY,
            }
        )
        assert len(artifact_list) == 2
        # pylint: disable-next=protected-access
        assert artifact_list[0]._gca_resource == expected_artifact
        # pylint: disable-next=protected-access
        assert artifact_list[1]._gca_resource == expected_artifact
