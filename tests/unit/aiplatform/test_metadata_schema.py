# -*- coding: utf-8 -*-

# Copyright 2022 Google LLC
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

import json
import pytest

from importlib import reload
from unittest import mock
from unittest.mock import patch

from google.cloud import aiplatform
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.compat.types import artifact as gca_artifact
from google.cloud.aiplatform.compat.types import execution as gca_execution
from google.cloud.aiplatform.metadata import metadata
from google.cloud.aiplatform.metadata.schema import base_artifact
from google.cloud.aiplatform.metadata.schema import base_execution
from google.cloud.aiplatform.metadata.schema import base_context
from google.cloud.aiplatform.metadata.schema.google import (
    artifact_schema as google_artifact_schema,
)
from google.cloud.aiplatform.metadata.schema.system import (
    artifact_schema as system_artifact_schema,
)
from google.cloud.aiplatform.metadata.schema.system import (
    context_schema as system_context_schema,
)
from google.cloud.aiplatform.metadata.schema.system import (
    execution_schema as system_execution_schema,
)
from google.cloud.aiplatform.metadata.schema import utils
from google.cloud.aiplatform_v1 import MetadataServiceClient
from google.cloud.aiplatform_v1 import Artifact as GapicArtifact
from google.cloud.aiplatform_v1 import Execution as GapicExecution


# project
_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_METADATA_STORE = "test-metadata-store"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"

# resource attributes
_TEST_ARTIFACT_STATE = gca_artifact.Artifact.State.STATE_UNSPECIFIED
_TEST_EXECUTION_STATE = gca_execution.Execution.State.STATE_UNSPECIFIED
_TEST_URI = "test-uri"
_TEST_DISPLAY_NAME = "test-display-name"
_TEST_SCHEMA_TITLE = "test.Example"
_TEST_SCHEMA_VERSION = "0.0.1"
_TEST_DESCRIPTION = "test description"
_TEST_METADATA = {"test-param1": 1, "test-param2": "test-value", "test-param3": True}
_TEST_UPDATED_METADATA = {
    "test-param1": 2.0,
    "test-param2": "test-value-1",
    "test-param3": False,
}

# artifact
_TEST_ARTIFACT_ID = "test-artifact-id"
_TEST_ARTIFACT_NAME = f"{_TEST_PARENT}/metadataStores/{_TEST_METADATA_STORE}/artifacts/{_TEST_ARTIFACT_ID}"

# execution
_TEST_EXECUTION_ID = "test-execution-id"
_TEST_EXECUTION_NAME = f"{_TEST_PARENT}/metadataStores/{_TEST_METADATA_STORE}/executions/{_TEST_EXECUTION_ID}"

# context
_TEST_CONTEXT_ID = "test-context-id"
_TEST_CONTEXT_NAME = (
    f"{_TEST_PARENT}/metadataStores/{_TEST_METADATA_STORE}/contexts/{_TEST_CONTEXT_ID}"
)


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
            state=GapicArtifact.State.STATE_UNSPECIFIED,
        )
        yield get_artifact_mock


@pytest.fixture
def initializer_create_client_mock():
    with patch.object(
        initializer.global_config, "create_client"
    ) as initializer_create_client_mock:
        yield initializer_create_client_mock


@pytest.fixture
def base_artifact_init_with_resouce_name_mock():
    with patch.object(
        base_artifact.BaseArtifactSchema, "_init_with_resource_name"
    ) as base_artifact_init_with_resouce_name_mock:
        yield base_artifact_init_with_resouce_name_mock


@pytest.fixture
def base_execution_init_with_resouce_name_mock():
    with patch.object(
        base_execution.BaseExecutionSchema, "_init_with_resource_name"
    ) as base_execution_init_with_resouce_name_mock:
        yield base_execution_init_with_resouce_name_mock


@pytest.fixture
def base_context_init_with_resouce_name_mock():
    with patch.object(
        base_context.BaseContextSchema, "_init_with_resource_name"
    ) as base_context_init_with_resouce_name_mock:
        yield base_context_init_with_resouce_name_mock


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
            state=GapicExecution.State.RUNNING,
        )
        yield get_execution_mock


@pytest.fixture
def get_context_mock():
    with patch.object(MetadataServiceClient, "get_context") as get_context_mock:
        get_context_mock.return_value = GapicExecution(
            name=_TEST_CONTEXT_NAME,
            display_name=_TEST_DISPLAY_NAME,
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
        )
        yield get_context_mock


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
            state=GapicArtifact.State.STATE_UNSPECIFIED,
        )
        yield create_artifact_mock


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
def create_context_mock():
    with patch.object(MetadataServiceClient, "create_context") as create_context_mock:
        create_context_mock.return_value = GapicExecution(
            name=_TEST_CONTEXT_NAME,
            display_name=_TEST_DISPLAY_NAME,
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
        )
        yield create_context_mock


@pytest.fixture
def list_artifacts_mock():
    with patch.object(MetadataServiceClient, "list_artifacts") as list_artifacts_mock:
        list_artifacts_mock.return_value = []
        yield list_artifacts_mock


@pytest.fixture
def list_executions_mock():
    with patch.object(MetadataServiceClient, "list_executions") as list_executions_mock:
        list_executions_mock.return_value = []
        yield list_executions_mock


@pytest.fixture
def list_contexts_mock():
    with patch.object(MetadataServiceClient, "list_contexts") as list_contexts_mock:
        list_contexts_mock.return_value = []
        yield list_contexts_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestMetadataBaseArtifactSchema:
    def setup_method(self):
        reload(initializer)
        reload(metadata)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_base_class_instatiated_uses_schema_title(self):
        class TestArtifact(base_artifact.BaseArtifactSchema):
            schema_title = _TEST_SCHEMA_TITLE

        artifact = TestArtifact()
        assert artifact.schema_title == _TEST_SCHEMA_TITLE

    def test_base_class_print_output(self, capsys):
        class TestArtifact(base_artifact.BaseArtifactSchema):
            schema_title = _TEST_SCHEMA_TITLE

        artifact = TestArtifact()
        print(artifact)
        captured = capsys.readouterr()
        assert (
            captured.out
            == f"{object.__repr__(artifact)}\n"
            + f"schema_title: {_TEST_SCHEMA_TITLE}\n"
        )

    def test_base_class_inherited_methods_error(self):
        class TestArtifact(base_artifact.BaseArtifactSchema):
            schema_title = _TEST_SCHEMA_TITLE

        artifact = TestArtifact()

        with pytest.raises(RuntimeError) as exception:
            artifact.resource_name
        assert str(exception.value) == "TestArtifact resource has not been created."

        with pytest.raises(RuntimeError) as exception:
            artifact.lineage_console_uri
        assert str(exception.value) == "TestArtifact resource has not been created."

        with pytest.raises(RuntimeError) as exception:
            artifact.sync_resource()
        assert str(exception.value) == "TestArtifact resource has not been created."

        with pytest.raises(RuntimeError) as exception:
            artifact.update(
                metadata=_TEST_UPDATED_METADATA,
                description=_TEST_DESCRIPTION,
            )
        assert str(exception.value) == "TestArtifact resource has not been created."

    def test_base_class_parameters_overrides_default_values(self):
        class TestArtifact(base_artifact.BaseArtifactSchema):
            schema_title = _TEST_SCHEMA_TITLE

        artifact = TestArtifact(
            state=_TEST_ARTIFACT_STATE,
            schema_version=_TEST_SCHEMA_VERSION,
            artifact_id=_TEST_ARTIFACT_ID,
            uri=_TEST_URI,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        assert artifact.state == _TEST_ARTIFACT_STATE
        assert artifact.state == _TEST_ARTIFACT_STATE
        assert artifact.schema_version == _TEST_SCHEMA_VERSION
        assert artifact.artifact_id == _TEST_ARTIFACT_ID
        assert artifact.schema_title == _TEST_SCHEMA_TITLE
        assert artifact.uri == _TEST_URI
        assert artifact.display_name == _TEST_DISPLAY_NAME
        assert artifact.description == _TEST_DESCRIPTION
        assert artifact.metadata == _TEST_UPDATED_METADATA

    def test_base_class_without_schema_title_raises_error(self):
        with pytest.raises(TypeError):
            base_artifact.BaseArtifactSchema()

    @pytest.mark.usefixtures("create_artifact_mock", "get_artifact_mock")
    def test_create_is_called_with_default_parameters(self, create_artifact_mock):
        aiplatform.init(project=_TEST_PROJECT)

        class TestArtifact(base_artifact.BaseArtifactSchema):
            schema_title = _TEST_SCHEMA_TITLE

        artifact = TestArtifact(
            uri=_TEST_URI,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
            state=_TEST_ARTIFACT_STATE,
        )
        artifact.create(metadata_store_id=_TEST_METADATA_STORE)
        create_artifact_mock.assert_called_once_with(
            parent=f"{_TEST_PARENT}/metadataStores/{_TEST_METADATA_STORE}",
            artifact=mock.ANY,
            artifact_id=None,
        )
        _, _, kwargs = create_artifact_mock.mock_calls[0]
        assert kwargs["artifact"].schema_title == _TEST_SCHEMA_TITLE
        assert kwargs["artifact"].uri == _TEST_URI
        assert kwargs["artifact"].display_name == _TEST_DISPLAY_NAME
        assert kwargs["artifact"].description == _TEST_DESCRIPTION
        assert kwargs["artifact"].metadata == _TEST_UPDATED_METADATA
        assert kwargs["artifact"].state == _TEST_ARTIFACT_STATE

    @pytest.mark.usefixtures(
        "base_artifact_init_with_resouce_name_mock",
        "initializer_create_client_mock",
        "create_artifact_mock",
        "get_artifact_mock",
    )
    def test_artifact_create_call_sets_the_user_agent_header(
        self, initializer_create_client_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        class TestArtifact(base_artifact.BaseArtifactSchema):
            schema_title = _TEST_SCHEMA_TITLE

        artifact = TestArtifact(
            uri=_TEST_URI,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
            state=_TEST_ARTIFACT_STATE,
        )
        artifact.create()
        _, _, kwargs = initializer_create_client_mock.mock_calls[0]
        assert kwargs["appended_user_agent"] == [
            "sdk_command/aiplatform.metadata.schema.base_artifact.BaseArtifactSchema.create"
        ]

    @pytest.mark.usefixtures(
        "initializer_create_client_mock",
        "create_artifact_mock",
        "get_artifact_mock",
    )
    def test_artifact_init_call_sets_the_user_agent_header(
        self, initializer_create_client_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        class TestArtifact(base_artifact.BaseArtifactSchema):
            schema_title = _TEST_SCHEMA_TITLE

        artifact = TestArtifact(
            uri=_TEST_URI,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
            state=_TEST_ARTIFACT_STATE,
        )
        artifact._init_with_resource_name(artifact_name=_TEST_ARTIFACT_NAME)
        _, _, kwargs = initializer_create_client_mock.mock_calls[0]
        assert kwargs["appended_user_agent"] == [
            "sdk_command/aiplatform.metadata.schema.base_artifact.BaseArtifactSchema._init_with_resource_name"
        ]

    def test_list_artifacts(self, list_artifacts_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        class TestArtifact(base_artifact.BaseArtifactSchema):
            schema_title = _TEST_SCHEMA_TITLE

        TestArtifact.list()
        list_artifacts_mock.assert_called_once_with(
            request={
                "parent": f"{_TEST_PARENT}/metadataStores/default",
                "filter": f'schema_title="{_TEST_SCHEMA_TITLE}"',
            }
        )


@pytest.mark.usefixtures("google_auth_mock")
class TestMetadataBaseExecutionSchema:
    def setup_method(self):
        reload(initializer)
        reload(metadata)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_base_class_overrides_default_schema_title(self):
        class TestExecution(base_execution.BaseExecutionSchema):
            schema_title = _TEST_SCHEMA_TITLE

        execution = TestExecution()
        assert execution.schema_title == _TEST_SCHEMA_TITLE

    def test_base_class_print_output(self, capsys):
        class TestExecution(base_execution.BaseExecutionSchema):
            schema_title = _TEST_SCHEMA_TITLE

        execution = TestExecution()
        print(execution)
        captured = capsys.readouterr()
        assert (
            captured.out
            == f"{object.__repr__(execution)}\n"
            + f"schema_title: {_TEST_SCHEMA_TITLE}\n"
        )

    def test_base_class_inherited_methods_error(self):
        class TestExecution(base_execution.BaseExecutionSchema):
            schema_title = _TEST_SCHEMA_TITLE

        execution = TestExecution()

        with pytest.raises(RuntimeError) as exception:
            execution.resource_name
        assert str(exception.value) == "TestExecution resource has not been created."

        with pytest.raises(RuntimeError) as exception:
            execution.assign_input_artifacts(artifacts=[_TEST_ARTIFACT_NAME])
        assert str(exception.value) == "TestExecution resource has not been created."

        with pytest.raises(RuntimeError) as exception:
            execution.assign_output_artifacts(artifacts=[_TEST_ARTIFACT_NAME])
        assert str(exception.value) == "TestExecution resource has not been created."

        with pytest.raises(RuntimeError) as exception:
            execution.get_input_artifacts()
        assert str(exception.value) == "TestExecution resource has not been created."

        with pytest.raises(RuntimeError) as exception:
            execution.get_output_artifacts()
        assert str(exception.value) == "TestExecution resource has not been created."

        with pytest.raises(RuntimeError) as exception:
            execution.update(
                state=_TEST_EXECUTION_STATE,
                description=_TEST_DESCRIPTION,
                metadata=_TEST_UPDATED_METADATA,
            )
        assert str(exception.value) == "TestExecution resource has not been created."

    def test_base_class_parameters_overrides_default_values(self):
        class TestExecution(base_execution.BaseExecutionSchema):
            schema_title = _TEST_SCHEMA_TITLE

        execution = TestExecution(
            state=_TEST_EXECUTION_STATE,
            schema_version=_TEST_SCHEMA_VERSION,
            execution_id=_TEST_EXECUTION_ID,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        assert execution.state == _TEST_EXECUTION_STATE
        assert execution.schema_version == _TEST_SCHEMA_VERSION
        assert execution.execution_id == _TEST_EXECUTION_ID
        assert execution.schema_title == _TEST_SCHEMA_TITLE
        assert execution.display_name == _TEST_DISPLAY_NAME
        assert execution.description == _TEST_DESCRIPTION
        assert execution.metadata == _TEST_UPDATED_METADATA

    def test_base_class_without_schema_title_raises_error(self):
        with pytest.raises(TypeError):
            base_execution.BaseExecutionSchema()

    @pytest.mark.usefixtures("create_execution_mock", "get_execution_mock")
    def test_create_method_calls_gapic_library_with_correct_parameters(
        self, create_execution_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        class TestExecution(base_execution.BaseExecutionSchema):
            schema_title = _TEST_SCHEMA_TITLE

        execution = TestExecution(
            state=_TEST_EXECUTION_STATE,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        execution.create(metadata_store_id=_TEST_METADATA_STORE)
        create_execution_mock.assert_called_once_with(
            parent=f"{_TEST_PARENT}/metadataStores/{_TEST_METADATA_STORE}",
            execution=mock.ANY,
            execution_id=None,
        )
        _, _, kwargs = create_execution_mock.mock_calls[0]
        assert kwargs["execution"].schema_title == _TEST_SCHEMA_TITLE
        assert kwargs["execution"].state == _TEST_EXECUTION_STATE
        assert kwargs["execution"].display_name == _TEST_DISPLAY_NAME
        assert kwargs["execution"].description == _TEST_DESCRIPTION
        assert kwargs["execution"].metadata == _TEST_UPDATED_METADATA

    @pytest.mark.usefixtures(
        "base_execution_init_with_resouce_name_mock",
        "initializer_create_client_mock",
        "create_execution_mock",
        "get_execution_mock",
    )
    def test_execution_create_call_sets_the_user_agent_header(
        self, initializer_create_client_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        class TestExecution(base_execution.BaseExecutionSchema):
            schema_title = _TEST_SCHEMA_TITLE

        execution = TestExecution(
            state=_TEST_EXECUTION_STATE,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        execution.create(metadata_store_id=_TEST_METADATA_STORE)
        _, _, kwargs = initializer_create_client_mock.mock_calls[0]
        assert kwargs["appended_user_agent"] == [
            "sdk_command/aiplatform.metadata.schema.base_execution.BaseExecutionSchema.create"
        ]

    @pytest.mark.usefixtures(
        "base_execution_init_with_resouce_name_mock",
        "initializer_create_client_mock",
        "create_execution_mock",
        "get_execution_mock",
    )
    def test_execution_start_execution_call_sets_the_user_agent_header(
        self, initializer_create_client_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        class TestExecution(base_execution.BaseExecutionSchema):
            schema_title = _TEST_SCHEMA_TITLE

        execution = TestExecution(
            state=_TEST_EXECUTION_STATE,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        execution.start_execution()
        _, _, kwargs = initializer_create_client_mock.mock_calls[0]
        assert kwargs["appended_user_agent"] == [
            "sdk_command/aiplatform.metadata.schema.base_execution.BaseExecutionSchema.start_execution"
        ]

    @pytest.mark.usefixtures(
        "initializer_create_client_mock",
        "create_execution_mock",
        "get_execution_mock",
    )
    def test_execution_init_call_sets_the_user_agent_header(
        self, initializer_create_client_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        class TestExecution(base_execution.BaseExecutionSchema):
            schema_title = _TEST_SCHEMA_TITLE

        execution = TestExecution(
            state=_TEST_EXECUTION_STATE,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        execution._init_with_resource_name(execution_name=_TEST_EXECUTION_NAME)
        _, _, kwargs = initializer_create_client_mock.mock_calls[0]
        assert kwargs["appended_user_agent"] == [
            "sdk_command/aiplatform.metadata.schema.base_execution.BaseExecutionSchema._init_with_resource_name"
        ]

    def test_list_executions(self, list_executions_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        class TestExecution(base_execution.BaseExecutionSchema):
            schema_title = _TEST_SCHEMA_TITLE

        TestExecution.list()
        list_executions_mock.assert_called_once_with(
            request={
                "parent": f"{_TEST_PARENT}/metadataStores/default",
                "filter": f'schema_title="{_TEST_SCHEMA_TITLE}"',
            }
        )


@pytest.mark.usefixtures("google_auth_mock")
class TestMetadataBaseContextSchema:
    def setup_method(self):
        reload(initializer)
        reload(metadata)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_base_context_class_instatiated_uses_schema_title(self):
        class TestContext(base_context.BaseContextSchema):
            schema_title = _TEST_SCHEMA_TITLE

        context = TestContext()
        assert context.schema_title == _TEST_SCHEMA_TITLE

    def test_base_class_print_output(self, capsys):
        class TestContext(base_context.BaseContextSchema):
            schema_title = _TEST_SCHEMA_TITLE

        context = TestContext()
        print(context)
        captured = capsys.readouterr()
        assert (
            captured.out
            == f"{object.__repr__(context)}\n" + f"schema_title: {_TEST_SCHEMA_TITLE}\n"
        )

    def test_base_class_inherited_methods_error(self):
        class TestContext(base_context.BaseContextSchema):
            schema_title = _TEST_SCHEMA_TITLE

        context = TestContext()

        with pytest.raises(RuntimeError) as exception:
            context.resource_name
        assert str(exception.value) == "TestContext resource has not been created."

        with pytest.raises(RuntimeError) as exception:
            context.add_artifacts_and_executions(
                artifact_resource_names=[_TEST_ARTIFACT_NAME],
            )
        assert str(exception.value) == "TestContext resource has not been created."

        with pytest.raises(RuntimeError) as exception:
            context.get_artifacts()
        assert str(exception.value) == "TestContext resource has not been created."

        with pytest.raises(RuntimeError) as exception:
            context.add_context_children(
                contexts=[_TEST_CONTEXT_NAME],
            )
        assert str(exception.value) == "TestContext resource has not been created."

        with pytest.raises(RuntimeError) as exception:
            context.query_lineage_subgraph()
        assert str(exception.value) == "TestContext resource has not been created."

        with pytest.raises(RuntimeError) as exception:
            context.get_executions()
        assert str(exception.value) == "TestContext resource has not been created."

    def test_base_context_class_parameters_overrides_default_values(self):
        class TestContext(base_context.BaseContextSchema):
            schema_title = _TEST_SCHEMA_TITLE

        context = TestContext(
            schema_version=_TEST_SCHEMA_VERSION,
            context_id=_TEST_CONTEXT_ID,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        assert context.schema_version == _TEST_SCHEMA_VERSION
        assert context.context_id == _TEST_CONTEXT_ID
        assert context.schema_title == _TEST_SCHEMA_TITLE
        assert context.display_name == _TEST_DISPLAY_NAME
        assert context.description == _TEST_DESCRIPTION
        assert context.metadata == _TEST_UPDATED_METADATA

    def test_base_context_class_without_schema_title_raises_error(self):
        with pytest.raises(TypeError):
            base_context.BaseContextSchema()

    @pytest.mark.usefixtures("create_context_mock", "get_context_mock")
    def test_base_context_create_is_called_with_default_parameters(
        self, create_context_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        class TestContext(base_context.BaseContextSchema):
            schema_title = _TEST_SCHEMA_TITLE

        context = TestContext(
            schema_version=_TEST_SCHEMA_VERSION,
            context_id=_TEST_CONTEXT_ID,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        context.create(metadata_store_id=_TEST_METADATA_STORE)
        create_context_mock.assert_called_once_with(
            parent=f"{_TEST_PARENT}/metadataStores/{_TEST_METADATA_STORE}",
            context=mock.ANY,
            context_id=_TEST_CONTEXT_ID,
        )
        _, _, kwargs = create_context_mock.mock_calls[0]
        assert kwargs["context"].schema_title == _TEST_SCHEMA_TITLE
        assert kwargs["context"].display_name == _TEST_DISPLAY_NAME
        assert kwargs["context"].description == _TEST_DESCRIPTION
        assert kwargs["context"].metadata == _TEST_UPDATED_METADATA

    @pytest.mark.usefixtures(
        "base_context_init_with_resouce_name_mock",
        "initializer_create_client_mock",
        "create_context_mock",
        "get_context_mock",
    )
    def test_base_context_create_call_sets_the_user_agent_header(
        self, initializer_create_client_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        class TestContext(base_context.BaseContextSchema):
            schema_title = _TEST_SCHEMA_TITLE

        context = TestContext(
            schema_version=_TEST_SCHEMA_VERSION,
            context_id=_TEST_CONTEXT_ID,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        context.create()
        _, _, kwargs = initializer_create_client_mock.mock_calls[0]
        assert kwargs["appended_user_agent"] == [
            "sdk_command/aiplatform.metadata.schema.base_context.BaseContextSchema.create"
        ]

    @pytest.mark.usefixtures(
        "initializer_create_client_mock",
        "create_context_mock",
        "get_context_mock",
    )
    def test_base_context_init_call_sets_the_user_agent_header(
        self, initializer_create_client_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        class TestContext(base_context.BaseContextSchema):
            schema_title = _TEST_SCHEMA_TITLE

        context = TestContext(
            schema_version=_TEST_SCHEMA_VERSION,
            context_id=_TEST_CONTEXT_ID,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        context._init_with_resource_name(context_name=_TEST_CONTEXT_NAME)
        _, _, kwargs = initializer_create_client_mock.mock_calls[0]
        assert kwargs["appended_user_agent"] == [
            "sdk_command/aiplatform.metadata.schema.base_context.BaseContextSchema._init_with_resource_name"
        ]

    def test_list_contexts(self, list_contexts_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        class TestContext(base_context.BaseContextSchema):
            schema_title = _TEST_SCHEMA_TITLE

        TestContext.list()
        list_contexts_mock.assert_called_once_with(
            request={
                "parent": f"{_TEST_PARENT}/metadataStores/default",
                "filter": f'schema_title="{_TEST_SCHEMA_TITLE}"',
            }
        )


@pytest.mark.usefixtures("google_auth_mock")
class TestMetadataGoogleArtifactSchema:
    def setup_method(self):
        reload(initializer)
        reload(metadata)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_vertex_dataset_schema_title_is_set_correctly(self):
        artifact = google_artifact_schema.VertexDataset(
            vertex_dataset_name=_TEST_ARTIFACT_NAME,
        )
        assert artifact.schema_title == "google.VertexDataset"

    def test_vertex_dataset_constructor_parameters_are_set_correctly(self):
        artifact = google_artifact_schema.VertexDataset(
            vertex_dataset_name=f"{_TEST_PARENT}/datasets/dataset-id",
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata={},
        )
        assert (
            artifact.uri
            == "https://us-central1-aiplatform.googleapis.com/v1/projects/test-project/locations/us-central1/datasets/dataset-id"
        )
        assert artifact.display_name == _TEST_DISPLAY_NAME
        assert artifact.description == _TEST_DESCRIPTION
        assert artifact.metadata == {
            "resourceName": "projects/test-project/locations/us-central1/datasets/dataset-id"
        }
        assert artifact.schema_version == _TEST_SCHEMA_VERSION

    def test_vertex_model_schema_title_is_set_correctly(self):
        artifact = google_artifact_schema.VertexModel(
            vertex_model_name=_TEST_ARTIFACT_NAME,
        )
        assert artifact.schema_title == "google.VertexModel"

    def test_vertex_model_constructor_parameters_are_set_correctly(self):
        artifact = google_artifact_schema.VertexModel(
            vertex_model_name=f"{_TEST_PARENT}/models/model-id",
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata={},
        )
        assert (
            artifact.uri
            == "https://us-central1-aiplatform.googleapis.com/v1/projects/test-project/locations/us-central1/models/model-id"
        )
        assert artifact.display_name == _TEST_DISPLAY_NAME
        assert artifact.description == _TEST_DESCRIPTION
        assert artifact.metadata == {
            "resourceName": "projects/test-project/locations/us-central1/models/model-id"
        }
        assert artifact.schema_version == _TEST_SCHEMA_VERSION

    def test_vertex_endpoint_schema_title_is_set_correctly(self):
        artifact = google_artifact_schema.VertexEndpoint(
            vertex_endpoint_name=_TEST_ARTIFACT_NAME,
        )
        assert artifact.schema_title == "google.VertexEndpoint"

    def test_vertex_endpoint_constructor_parameters_are_set_correctly(self):
        artifact = google_artifact_schema.VertexEndpoint(
            vertex_endpoint_name=f"{_TEST_PARENT}/endpoints/endpoint-id",
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata={},
        )
        assert (
            artifact.uri
            == "https://us-central1-aiplatform.googleapis.com/v1/projects/test-project/locations/us-central1/endpoints/endpoint-id"
        )
        assert artifact.display_name == _TEST_DISPLAY_NAME
        assert artifact.description == _TEST_DESCRIPTION
        assert artifact.metadata == {
            "resourceName": "projects/test-project/locations/us-central1/endpoints/endpoint-id"
        }
        assert artifact.schema_version == _TEST_SCHEMA_VERSION

    def test_unmanaged_container_model_title_is_set_correctly(self):
        predict_schemata = utils.PredictSchemata(
            instance_schema_uri="instance_uri",
            prediction_schema_uri="prediction_uri",
            parameters_schema_uri="parameters_uri",
        )

        container_spec = utils.ContainerSpec(
            image_uri="gcr.io/test_container_image_uri"
        )
        artifact = google_artifact_schema.UnmanagedContainerModel(
            predict_schemata=predict_schemata,
            container_spec=container_spec,
        )
        assert artifact.schema_title == "google.UnmanagedContainerModel"

    def test_unmanaged_container_model_constructor_parameters_are_set_correctly(self):
        predict_schemata = utils.PredictSchemata(
            instance_schema_uri="instance_uri",
            prediction_schema_uri="prediction_uri",
            parameters_schema_uri="parameters_uri",
        )

        container_spec = utils.ContainerSpec(
            image_uri="gcr.io/test_container_image_uri"
        )

        artifact = google_artifact_schema.UnmanagedContainerModel(
            predict_schemata=predict_schemata,
            container_spec=container_spec,
            artifact_id=_TEST_ARTIFACT_ID,
            uri=_TEST_URI,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        expected_metadata = {
            "test-param1": 2.0,
            "test-param2": "test-value-1",
            "test-param3": False,
            "predictSchemata": {
                "instanceSchemaUri": "instance_uri",
                "parametersSchemaUri": "parameters_uri",
                "predictionSchemaUri": "prediction_uri",
            },
            "containerSpec": {"imageUri": "gcr.io/test_container_image_uri"},
        }

        assert artifact.artifact_id == _TEST_ARTIFACT_ID
        assert artifact.uri == _TEST_URI
        assert artifact.display_name == _TEST_DISPLAY_NAME
        assert artifact.description == _TEST_DESCRIPTION
        assert json.dumps(artifact.metadata, sort_keys=True) == json.dumps(
            expected_metadata, sort_keys=True
        )
        assert artifact.schema_version == _TEST_SCHEMA_VERSION

    def test_classification_metrics_title_is_set_correctly(self):
        artifact = google_artifact_schema.ClassificationMetrics()
        assert artifact.schema_title == "google.ClassificationMetrics"

    def test_classification_metrics_constructor_parameters_are_set_correctly(self):
        aggregation_type = "MACRO_AVERAGE"
        aggregation_threshold = 0.5
        recall = 0.5
        precision = 0.5
        f1_score = 0.5
        accuracy = 0.5
        au_prc = 1.0
        au_roc = 2.0
        log_loss = 0.5
        confusion_matrix = utils.ConfusionMatrix(
            matrix=[[9.0, 1.0], [1.0, 9.0]],
            annotation_specs=[
                utils.AnnotationSpec(display_name="cat"),
                utils.AnnotationSpec(display_name="dog"),
            ],
        )
        confidence_metrics = [
            utils.ConfidenceMetric(
                confidence_threshold=0.9, recall=0.1, false_positive_rate=0.1
            ),
            utils.ConfidenceMetric(
                confidence_threshold=0.5, recall=0.5, false_positive_rate=0.7
            ),
            utils.ConfidenceMetric(
                confidence_threshold=0.1, recall=0.9, false_positive_rate=0.9
            ),
        ]

        artifact = google_artifact_schema.ClassificationMetrics(
            aggregation_type=aggregation_type,
            aggregation_threshold=aggregation_threshold,
            recall=recall,
            precision=precision,
            f1_score=f1_score,
            accuracy=accuracy,
            au_prc=au_prc,
            au_roc=au_roc,
            log_loss=log_loss,
            confusion_matrix=confusion_matrix,
            confidence_metrics=confidence_metrics,
            artifact_id=_TEST_ARTIFACT_ID,
            uri=_TEST_URI,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        expected_metadata = {
            "test-param1": _TEST_UPDATED_METADATA["test-param1"],
            "test-param2": _TEST_UPDATED_METADATA["test-param2"],
            "test-param3": _TEST_UPDATED_METADATA["test-param3"],
            "aggregationType": aggregation_type,
            "aggregationThreshold": aggregation_threshold,
            "recall": recall,
            "precision": precision,
            "f1Score": f1_score,
            "accuracy": accuracy,
            "auPrc": au_prc,
            "auRoc": au_roc,
            "logLoss": log_loss,
            "confusionMatrix": confusion_matrix.to_dict(),
            "confidenceMetrics": [
                confidence_metric.to_dict() for confidence_metric in confidence_metrics
            ],
        }

        assert artifact.artifact_id == _TEST_ARTIFACT_ID
        assert artifact.uri == _TEST_URI
        assert artifact.display_name == _TEST_DISPLAY_NAME
        assert artifact.description == _TEST_DESCRIPTION
        assert json.dumps(artifact.metadata, sort_keys=True) == json.dumps(
            expected_metadata, sort_keys=True
        )
        assert artifact.schema_version == _TEST_SCHEMA_VERSION

    def test_classification_metrics_wrong_aggregation_type(self):
        with pytest.raises(ValueError) as exception:
            google_artifact_schema.ClassificationMetrics(
                aggregation_type="unspecified_type"
            )
        assert (
            str(exception.value)
            == "aggregation_type can only be 'AGGREGATION_TYPE_UNSPECIFIED', 'MACRO_AVERAGE', or 'MICRO_AVERAGE'."
        )

    def test_regression_metrics_title_is_set_correctly(self):
        artifact = google_artifact_schema.RegressionMetrics()
        assert artifact.schema_title == "google.RegressionMetrics"

    def test_regression_metrics_constructor_parameters_are_set_correctly(self):
        root_mean_squared_error = 1.0
        mean_absolute_error = 2.0
        mean_absolute_percentage_error = 0.2
        r_squared = 0.5
        root_mean_squared_log_error = 0.9

        artifact = google_artifact_schema.RegressionMetrics(
            root_mean_squared_error=root_mean_squared_error,
            mean_absolute_error=mean_absolute_error,
            mean_absolute_percentage_error=mean_absolute_percentage_error,
            r_squared=r_squared,
            root_mean_squared_log_error=root_mean_squared_log_error,
            artifact_id=_TEST_ARTIFACT_ID,
            uri=_TEST_URI,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        expected_metadata = {
            "test-param1": 2.0,
            "test-param2": "test-value-1",
            "test-param3": False,
            "rootMeanSquaredError": 1.0,
            "meanAbsoluteError": 2.0,
            "meanAbsolutePercentageError": 0.2,
            "rSquared": 0.5,
            "rootMeanSquaredLogError": 0.9,
        }

        assert artifact.artifact_id == _TEST_ARTIFACT_ID
        assert artifact.uri == _TEST_URI
        assert artifact.display_name == _TEST_DISPLAY_NAME
        assert artifact.description == _TEST_DESCRIPTION
        assert json.dumps(artifact.metadata, sort_keys=True) == json.dumps(
            expected_metadata, sort_keys=True
        )
        assert artifact.schema_version == _TEST_SCHEMA_VERSION

    def test_forecasting_metrics_title_is_set_correctly(self):
        artifact = google_artifact_schema.ForecastingMetrics()
        assert artifact.schema_title == "google.ForecastingMetrics"

    def test_forecasting_metrics_constructor_parameters_are_set_correctly(self):
        root_mean_squared_error = 1.0
        mean_absolute_error = 2.0
        mean_absolute_percentage_error = 0.2
        r_squared = 0.5
        root_mean_squared_log_error = 0.9
        weighted_absolute_percentage_error = 4.0
        root_mean_squared_percentage_error = 0.7
        symmetric_mean_absolute_percentage_error = 0.8

        artifact = google_artifact_schema.ForecastingMetrics(
            root_mean_squared_error=root_mean_squared_error,
            mean_absolute_error=mean_absolute_error,
            mean_absolute_percentage_error=mean_absolute_percentage_error,
            r_squared=r_squared,
            root_mean_squared_log_error=root_mean_squared_log_error,
            weighted_absolute_percentage_error=weighted_absolute_percentage_error,
            root_mean_squared_percentage_error=root_mean_squared_percentage_error,
            symmetric_mean_absolute_percentage_error=symmetric_mean_absolute_percentage_error,
            artifact_id=_TEST_ARTIFACT_ID,
            uri=_TEST_URI,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        expected_metadata = {
            "test-param1": 2.0,
            "test-param2": "test-value-1",
            "test-param3": False,
            "rootMeanSquaredError": 1.0,
            "meanAbsoluteError": 2.0,
            "meanAbsolutePercentageError": 0.2,
            "rSquared": 0.5,
            "rootMeanSquaredLogError": 0.9,
            "weightedAbsolutePercentageError": 4.0,
            "rootMeanSquaredPercentageError": 0.7,
            "symmetricMeanAbsolutePercentageError": 0.8,
        }

        assert artifact.artifact_id == _TEST_ARTIFACT_ID
        assert artifact.uri == _TEST_URI
        assert artifact.display_name == _TEST_DISPLAY_NAME
        assert artifact.description == _TEST_DESCRIPTION
        assert json.dumps(artifact.metadata, sort_keys=True) == json.dumps(
            expected_metadata, sort_keys=True
        )
        assert artifact.schema_version == _TEST_SCHEMA_VERSION

    def test_experiment_model_title_is_set_correctly(self):
        artifact = google_artifact_schema.ExperimentModel(
            framework_name="sklearn",
            framework_version="1.0.0",
            model_file="model.pkl",
            uri=_TEST_URI,
        )
        assert artifact.schema_title == "google.ExperimentModel"
        assert artifact.framework_name == "sklearn"
        assert artifact.framework_version == "1.0.0"
        assert artifact.uri == _TEST_URI

    def test_experiment_model_wrong_metadata_key(self):
        with pytest.raises(ValueError) as exception:
            google_artifact_schema.ExperimentModel(
                framework_name="sklearn",
                framework_version="1.0.0",
                model_file="model.pkl",
                uri=_TEST_URI,
                metadata={"modelFile": "abc"},
            )
        assert (
            str(exception.value) == "'modelFile' is a system reserved key in metadata."
        )

    def test_experiment_model_constructor_parameters_are_set_correctly(self):
        predict_schemata = utils.PredictSchemata(
            instance_schema_uri="instance_uri",
            prediction_schema_uri="prediction_uri",
            parameters_schema_uri="parameters_uri",
        )

        artifact = google_artifact_schema.ExperimentModel(
            framework_name="sklearn",
            framework_version="1.0.0",
            model_file="model.pkl",
            model_class="sklearn.linear_model._base.LinearRegression",
            predict_schemata=predict_schemata,
            artifact_id=_TEST_ARTIFACT_ID,
            uri=_TEST_URI,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        expected_metadata = {
            "test-param1": 2.0,
            "test-param2": "test-value-1",
            "test-param3": False,
            "frameworkName": "sklearn",
            "frameworkVersion": "1.0.0",
            "modelFile": "model.pkl",
            "modelClass": "sklearn.linear_model._base.LinearRegression",
            "predictSchemata": {
                "instanceSchemaUri": "instance_uri",
                "parametersSchemaUri": "parameters_uri",
                "predictionSchemaUri": "prediction_uri",
            },
        }

        assert artifact.artifact_id == _TEST_ARTIFACT_ID
        assert artifact.uri == _TEST_URI
        assert artifact.display_name == _TEST_DISPLAY_NAME
        assert artifact.description == _TEST_DESCRIPTION
        assert json.dumps(artifact.metadata, sort_keys=True) == json.dumps(
            expected_metadata, sort_keys=True
        )
        assert artifact.schema_version == _TEST_SCHEMA_VERSION


@pytest.mark.usefixtures("google_auth_mock")
class TestMetadataSystemArtifactSchema:
    def setup_method(self):
        reload(initializer)
        reload(metadata)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_system_dataset_schema_title_is_set_correctly(self):
        artifact = system_artifact_schema.Dataset()
        assert artifact.schema_title == "system.Dataset"

    def test_system_dataset_constructor_parameters_are_set_correctly(self):
        artifact = system_artifact_schema.Dataset(
            uri=_TEST_URI,
            artifact_id=_TEST_ARTIFACT_ID,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        assert artifact.uri == _TEST_URI
        assert artifact.artifact_id == _TEST_ARTIFACT_ID
        assert artifact.display_name == _TEST_DISPLAY_NAME
        assert artifact.description == _TEST_DESCRIPTION
        assert artifact.metadata == _TEST_UPDATED_METADATA
        assert artifact.schema_version == _TEST_SCHEMA_VERSION

    def test_system_artifact_schema_title_is_set_correctly(self):
        artifact = system_artifact_schema.Artifact()
        assert artifact.schema_title == "system.Artifact"

    def test_system_artifact_constructor_parameters_are_set_correctly(self):
        artifact = system_artifact_schema.Artifact(
            uri=_TEST_URI,
            artifact_id=_TEST_ARTIFACT_ID,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        assert artifact.uri == _TEST_URI
        assert artifact.artifact_id == _TEST_ARTIFACT_ID
        assert artifact.display_name == _TEST_DISPLAY_NAME
        assert artifact.description == _TEST_DESCRIPTION
        assert artifact.metadata == _TEST_UPDATED_METADATA
        assert artifact.schema_version == _TEST_SCHEMA_VERSION

    def test_system_model_schema_title_is_set_correctly(self):
        artifact = system_artifact_schema.Model()
        assert artifact.schema_title == "system.Model"

    def test_system_model_constructor_parameters_are_set_correctly(self):
        artifact = system_artifact_schema.Model(
            uri=_TEST_URI,
            artifact_id=_TEST_ARTIFACT_ID,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        assert artifact.uri == _TEST_URI
        assert artifact.artifact_id == _TEST_ARTIFACT_ID
        assert artifact.display_name == _TEST_DISPLAY_NAME
        assert artifact.description == _TEST_DESCRIPTION
        assert artifact.metadata == _TEST_UPDATED_METADATA
        assert artifact.schema_version == _TEST_SCHEMA_VERSION

    def test_system_metrics_schema_title_is_set_correctly(self):
        artifact = system_artifact_schema.Metrics()
        assert artifact.schema_title == "system.Metrics"

    def test_system_metrics_values_default_to_none(self):
        artifact = system_artifact_schema.Metrics()
        assert artifact._gca_resource.metadata is None

    def test_system_metrics_constructor_parameters_are_set_correctly(self):
        artifact = system_artifact_schema.Metrics(
            accuracy=0.1,
            precision=0.2,
            recall=0.3,
            f1score=0.4,
            mean_absolute_error=0.5,
            mean_squared_error=0.6,
            artifact_id=_TEST_ARTIFACT_ID,
            uri=_TEST_URI,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        assert artifact.uri == _TEST_URI
        assert artifact.artifact_id == _TEST_ARTIFACT_ID
        assert artifact.display_name == _TEST_DISPLAY_NAME
        assert artifact.description == _TEST_DESCRIPTION
        assert artifact.schema_version == _TEST_SCHEMA_VERSION
        assert artifact.metadata["accuracy"] == 0.1
        assert artifact.metadata["precision"] == 0.2
        assert artifact.metadata["recall"] == 0.3
        assert artifact.metadata["f1score"] == 0.4
        assert artifact.metadata["mean_absolute_error"] == 0.5
        assert artifact.metadata["mean_squared_error"] == 0.6


@pytest.mark.usefixtures("google_auth_mock")
class TestMetadataSystemSchemaExecution:
    def setup_method(self):
        reload(initializer)
        reload(metadata)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    # Test system.Execution Schemas
    def test_system_container_execution_schema_title_is_set_correctly(self):
        execution = system_execution_schema.ContainerExecution()
        assert execution.schema_title == "system.ContainerExecution"

    def test_system_custom_job_execution_schema_title_is_set_correctly(self):
        execution = system_execution_schema.CustomJobExecution()
        assert execution.schema_title == "system.CustomJobExecution"

    def test_system_run_execution_schema_title_is_set_correctly(self):
        execution = system_execution_schema.Run()
        assert execution.schema_title == "system.Run"


@pytest.mark.usefixtures("google_auth_mock")
class TestMetadataSystemSchemaContext:
    def setup_method(self):
        reload(initializer)
        reload(metadata)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    # Test system.Context Schemas
    @pytest.mark.usefixtures("create_context_mock", "get_context_mock")
    def test_create_is_called_with_default_parameters(self, create_context_mock):
        aiplatform.init(project=_TEST_PROJECT)

        class TestContext(base_context.BaseContextSchema):
            schema_title = _TEST_SCHEMA_TITLE

        context = TestContext(
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        context.create(metadata_store_id=_TEST_METADATA_STORE)
        create_context_mock.assert_called_once_with(
            parent=f"{_TEST_PARENT}/metadataStores/{_TEST_METADATA_STORE}",
            context=mock.ANY,
            context_id=None,
        )
        _, _, kwargs = create_context_mock.mock_calls[0]
        assert kwargs["context"].schema_title == _TEST_SCHEMA_TITLE
        assert kwargs["context"].display_name == _TEST_DISPLAY_NAME
        assert kwargs["context"].description == _TEST_DESCRIPTION
        assert kwargs["context"].metadata == _TEST_UPDATED_METADATA

    def test_system_experiment_schema_title_is_set_correctly(self):
        context = system_context_schema.Experiment()
        assert context.schema_title == "system.Experiment"

    def test_system_experiment_run_schema_title_is_set_correctly(self):
        context = system_context_schema.ExperimentRun()
        assert context.schema_title == "system.ExperimentRun"

    def test_system_experiment_run_parameters_are_set_correctly(self):
        context = system_context_schema.ExperimentRun(experiment_id=_TEST_CONTEXT_ID)
        assert context.metadata["experiment_id"] == _TEST_CONTEXT_ID

    def test_system_pipeline_schema_title_is_set_correctly(self):
        context = system_context_schema.Pipeline()
        assert context.schema_title == "system.Pipeline"

    def test_system_pipeline_run_schema_title_is_set_correctly(self):
        context = system_context_schema.PipelineRun()
        assert context.schema_title == "system.PipelineRun"

    def test_system_pipeline_run_parameters_are_set_correctly(self):
        context = system_context_schema.PipelineRun(pipeline_id=_TEST_CONTEXT_ID)
        assert context.metadata["pipeline_id"] == _TEST_CONTEXT_ID


@pytest.mark.usefixtures("google_auth_mock")
class TestMetadataUtils:
    def setup_method(self):
        reload(initializer)
        reload(metadata)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_predict_schemata_to_dict_method_returns_correct_schema(self):
        predict_schemata = utils.PredictSchemata(
            instance_schema_uri="instance_uri",
            prediction_schema_uri="prediction_uri",
            parameters_schema_uri="parameters_uri",
        )
        expected_results = {
            "instanceSchemaUri": "instance_uri",
            "parametersSchemaUri": "parameters_uri",
            "predictionSchemaUri": "prediction_uri",
        }

        assert json.dumps(predict_schemata.to_dict()) == json.dumps(expected_results)

    def test_create_uri_from_resource_name_for_valid_resouce_names(self):
        valid_resouce_names = [
            "projects/project/locations/location/resource_type/resource_id",
            "projects/project/locations/location/resource_type/resource_id@version",
            "projects/project/locations/location/metadataStores/store_id/resource_type/resource_id",
            "projects/project/locations/location/metadataStores/store_id/resource_type/resource_id@version",
        ]
        for resouce_name in valid_resouce_names:
            uri = utils.create_uri_from_resource_name(resource_name=resouce_name)
            assert (
                uri == f"https://location-aiplatform.googleapis.com/v1/{resouce_name}"
            )

    def test_create_uri_from_resource_name_for_invalid_resouce_names(self):
        invalid_resouce_name = (
            "projects/project/locations/location/resource_type/resource_id/"
        )
        with pytest.raises(ValueError):
            utils.create_uri_from_resource_name(resource_name=invalid_resouce_name)

    def test_container_spec_to_dict_method_returns_correct_schema(self):
        container_spec = utils.ContainerSpec(
            image_uri="gcr.io/some_container_image_uri",
            command=["test_command"],
            args=["test_args"],
            env=[{"env_var_name": "env_var_value"}],
            ports=[1],
            predict_route="test_prediction_rout",
            health_route="test_health_rout",
        )

        expected_results = {
            "imageUri": "gcr.io/some_container_image_uri",
            "command": ["test_command"],
            "args": ["test_args"],
            "env": [{"env_var_name": "env_var_value"}],
            "ports": [1],
            "predictRoute": "test_prediction_rout",
            "healthRoute": "test_health_rout",
        }

        assert json.dumps(container_spec.to_dict()) == json.dumps(expected_results)

    def test_annotation_spec_to_dict_method_returns_correct_schema(self):
        annotation_spec = utils.AnnotationSpec(
            display_name="test_display_name",
            id="test_annotation_id",
        )

        expected_results = {
            "displayName": "test_display_name",
            "id": "test_annotation_id",
        }

        assert json.dumps(annotation_spec.to_dict(), sort_keys=True) == json.dumps(
            expected_results, sort_keys=True
        )

    def test_confusion_matrix_to_dict_method_returns_correct_schema(self):
        confusion_matrix = utils.ConfusionMatrix(
            matrix=[[9, 1], [1, 9]],
            annotation_specs=[
                utils.AnnotationSpec(display_name="cat"),
                utils.AnnotationSpec(display_name="dog"),
            ],
        )

        expected_results = {
            "rows": [[9, 1], [1, 9]],
            "annotationSpecs": [
                {"displayName": "cat"},
                {"displayName": "dog"},
            ],
        }

        assert json.dumps(confusion_matrix.to_dict(), sort_keys=True) == json.dumps(
            expected_results, sort_keys=True
        )

    def test_confusion_matrix_to_dict_method_length_error(self):
        confusion_matrix = utils.ConfusionMatrix(
            matrix=[[9, 1], [1, 9]],
            annotation_specs=[
                utils.AnnotationSpec(display_name="cat"),
                utils.AnnotationSpec(display_name="dog"),
                utils.AnnotationSpec(display_name="bird"),
            ],
        )

        with pytest.raises(ValueError) as exception:
            confusion_matrix.to_dict()
        assert (
            str(exception.value)
            == "Length of annotation_specs and matrix must be the same. Got lengths 3 and 2 respectively."
        )

    def test_confidence_metric_to_dict_method_returns_correct_schema(self):
        confidence_metric = utils.ConfidenceMetric(
            confidence_threshold=0.5,
            recall=0.5,
            precision=0.5,
            f1_score=0.5,
            max_predictions=1,
            false_positive_rate=0.5,
            accuracy=0.5,
            true_positive_count=1,
            false_positive_count=1,
            false_negative_count=1,
            true_negative_count=1,
            recall_at_1=0.5,
            precision_at_1=0.5,
            false_positive_rate_at_1=0.5,
            f1_score_at_1=0.5,
            confusion_matrix=utils.ConfusionMatrix(
                matrix=[[9, 1], [1, 9]],
                annotation_specs=[
                    utils.AnnotationSpec(display_name="cat"),
                    utils.AnnotationSpec(display_name="dog"),
                ],
            ),
        )

        expected_results = {
            "confidenceThreshold": 0.5,
            "recall": 0.5,
            "precision": 0.5,
            "f1Score": 0.5,
            "maxPredictions": 1,
            "falsePositiveRate": 0.5,
            "accuracy": 0.5,
            "truePositiveCount": 1,
            "falsePositiveCount": 1,
            "falseNegativeCount": 1,
            "trueNegativeCount": 1,
            "recallAt1": 0.5,
            "precisionAt1": 0.5,
            "falsePositiveRateAt1": 0.5,
            "f1ScoreAt1": 0.5,
            "confusionMatrix": {
                "rows": [[9, 1], [1, 9]],
                "annotationSpecs": [
                    {"displayName": "cat"},
                    {"displayName": "dog"},
                ],
            },
        }

        assert json.dumps(confidence_metric.to_dict(), sort_keys=True) == json.dumps(
            expected_results, sort_keys=True
        )

    @pytest.mark.usefixtures("create_execution_mock", "get_execution_mock")
    def test_start_execution_method_calls_gapic_library_with_correct_parameters(
        self, create_execution_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        class TestExecution(base_execution.BaseExecutionSchema):
            schema_title = _TEST_SCHEMA_TITLE

        execution = TestExecution(
            state=_TEST_EXECUTION_STATE,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        execution.start_execution()
        create_execution_mock.assert_called_once_with(
            parent=f"{_TEST_PARENT}/metadataStores/default",
            execution=mock.ANY,
            execution_id=None,
        )
        _, _, kwargs = create_execution_mock.mock_calls[0]
        assert kwargs["execution"].schema_title == _TEST_SCHEMA_TITLE
        assert kwargs["execution"].display_name == _TEST_DISPLAY_NAME
        assert kwargs["execution"].description == _TEST_DESCRIPTION
        assert kwargs["execution"].metadata == _TEST_UPDATED_METADATA
