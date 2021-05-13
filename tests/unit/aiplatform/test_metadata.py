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
from unittest.mock import patch, call

import pytest
from google.api_core import exceptions

from google.cloud import aiplatform
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.metadata import constants
from google.cloud.aiplatform.metadata import metadata
from google.cloud.aiplatform_v1beta1 import (
    AddContextArtifactsAndExecutionsResponse,
    Event,
    LineageSubgraph,
    ListExecutionsRequest,
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
_TEST_OTHER_PROJECT = "test-project-1"
_TEST_LOCATION = "us-central1"
_TEST_PARENT = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/metadataStores/default"
)
_TEST_EXPERIMENT = "test-experiment"
_TEST_EXPERIMENT_DESCRIPTION = "test-experiment-description"
_TEST_OTHER_EXPERIMENT_DESCRIPTION = "test-other-experiment-description"
_TEST_PIPELINE = _TEST_EXPERIMENT
_TEST_RUN = "run-1"
_TEST_OTHER_RUN = "run-2"

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
_TEST_OTHER_EXECUTION_ID = f"{_TEST_EXPERIMENT}-{_TEST_OTHER_RUN}"
_TEST_OTHER_EXECUTION_NAME = f"{_TEST_PARENT}/executions/{_TEST_OTHER_EXECUTION_ID}"

# artifact
_TEST_ARTIFACT_ID = f"{_TEST_EXPERIMENT}-{_TEST_RUN}-metrics"
_TEST_ARTIFACT_NAME = f"{_TEST_PARENT}/artifacts/{_TEST_ARTIFACT_ID}"
_TEST_OTHER_ARTIFACT_ID = f"{_TEST_EXPERIMENT}-{_TEST_OTHER_RUN}-metrics"
_TEST_OTHER_ARTIFACT_NAME = f"{_TEST_PARENT}/artifacts/{_TEST_OTHER_ARTIFACT_ID}"

# parameters
_TEST_PARAM_KEY_1 = "learning_rate"
_TEST_PARAM_KEY_2 = "dropout"
_TEST_PARAMS = {_TEST_PARAM_KEY_1: 0.01, _TEST_PARAM_KEY_2: 0.2}
_TEST_OTHER_PARAMS = {_TEST_PARAM_KEY_1: 0.02, _TEST_PARAM_KEY_2: 0.3}

# metrics
_TEST_METRIC_KEY_1 = "rmse"
_TEST_METRIC_KEY_2 = "accuracy"
_TEST_METRICS = {_TEST_METRIC_KEY_1: 222, _TEST_METRIC_KEY_2: 1}
_TEST_OTHER_METRICS = {_TEST_METRIC_KEY_2: 0.9}

# schema
_TEST_WRONG_SCHEMA_TITLE = "system.WrongSchema"


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
            description=_TEST_EXPERIMENT_DESCRIPTION,
            schema_title=constants.SYSTEM_EXPERIMENT,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_EXPERIMENT],
            metadata=constants.EXPERIMENT_METADATA,
        )
        yield get_context_mock


@pytest.fixture
def get_context_wrong_schema_mock():
    with patch.object(
        MetadataServiceClient, "get_context"
    ) as get_context_wrong_schema_mock:
        get_context_wrong_schema_mock.return_value = GapicContext(
            name=_TEST_CONTEXT_NAME,
            display_name=_TEST_EXPERIMENT,
            schema_title=_TEST_WRONG_SCHEMA_TITLE,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_EXPERIMENT],
            metadata=constants.EXPERIMENT_METADATA,
        )
        yield get_context_wrong_schema_mock


@pytest.fixture
def get_pipeline_context_mock():
    with patch.object(
        MetadataServiceClient, "get_context"
    ) as get_pipeline_context_mock:
        get_pipeline_context_mock.return_value = GapicContext(
            name=_TEST_CONTEXT_NAME,
            display_name=_TEST_EXPERIMENT,
            schema_title=constants.SYSTEM_PIPELINE,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_PIPELINE],
            metadata=constants.EXPERIMENT_METADATA,
        )
        yield get_pipeline_context_mock


@pytest.fixture
def get_context_not_found_mock():
    with patch.object(
        MetadataServiceClient, "get_context"
    ) as get_context_not_found_mock:
        get_context_not_found_mock.side_effect = exceptions.NotFound("test: not found")
        yield get_context_not_found_mock


@pytest.fixture
def update_context_mock():
    with patch.object(MetadataServiceClient, "update_context") as update_context_mock:
        update_context_mock.return_value = GapicContext(
            name=_TEST_CONTEXT_NAME,
            display_name=_TEST_EXPERIMENT,
            description=_TEST_OTHER_EXPERIMENT_DESCRIPTION,
            schema_title=constants.SYSTEM_EXPERIMENT,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_EXPERIMENT],
            metadata=constants.EXPERIMENT_METADATA,
        )
        yield update_context_mock


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
def get_execution_wrong_schema_mock():
    with patch.object(
        MetadataServiceClient, "get_execution"
    ) as get_execution_wrong_schema_mock:
        get_execution_wrong_schema_mock.return_value = GapicExecution(
            name=_TEST_EXECUTION_NAME,
            display_name=_TEST_RUN,
            schema_title=_TEST_WRONG_SCHEMA_TITLE,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_RUN],
        )
        yield get_execution_wrong_schema_mock


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
def list_executions_mock():
    with patch.object(MetadataServiceClient, "list_executions") as list_executions_mock:
        list_executions_mock.return_value = [
            GapicExecution(
                name=_TEST_EXECUTION_NAME,
                display_name=_TEST_RUN,
                schema_title=constants.SYSTEM_RUN,
                schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_RUN],
                metadata=_TEST_PARAMS,
            ),
            GapicExecution(
                name=_TEST_OTHER_EXECUTION_NAME,
                display_name=_TEST_OTHER_RUN,
                schema_title=constants.SYSTEM_RUN,
                schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_RUN],
                metadata=_TEST_OTHER_PARAMS,
            ),
        ]
        yield list_executions_mock


@pytest.fixture
def query_execution_inputs_and_outputs_mock():
    with patch.object(
        MetadataServiceClient, "query_execution_inputs_and_outputs"
    ) as query_execution_inputs_and_outputs_mock:
        query_execution_inputs_and_outputs_mock.side_effect = [
            LineageSubgraph(
                artifacts=[
                    GapicArtifact(
                        name=_TEST_ARTIFACT_NAME,
                        display_name=_TEST_ARTIFACT_ID,
                        schema_title=constants.SYSTEM_METRICS,
                        schema_version=constants.SCHEMA_VERSIONS[
                            constants.SYSTEM_METRICS
                        ],
                        metadata=_TEST_METRICS,
                    ),
                ],
            ),
            LineageSubgraph(
                artifacts=[
                    GapicArtifact(
                        name=_TEST_OTHER_ARTIFACT_NAME,
                        display_name=_TEST_OTHER_ARTIFACT_ID,
                        schema_title=constants.SYSTEM_METRICS,
                        schema_version=constants.SCHEMA_VERSIONS[
                            constants.SYSTEM_METRICS
                        ],
                        metadata=_TEST_OTHER_METRICS,
                    ),
                ],
            ),
        ]
        yield query_execution_inputs_and_outputs_mock


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
def get_artifact_wrong_schema_mock():
    with patch.object(
        MetadataServiceClient, "get_artifact"
    ) as get_artifact_wrong_schema_mock:
        get_artifact_wrong_schema_mock.return_value = GapicArtifact(
            name=_TEST_ARTIFACT_NAME,
            display_name=_TEST_ARTIFACT_ID,
            schema_title=_TEST_WRONG_SCHEMA_TITLE,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_METRICS],
        )
        yield get_artifact_wrong_schema_mock


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


def _assert_frame_equal_with_sorted_columns(dataframe_1, dataframe_2):
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "Pandas is not installed and is required to test the get_experiment_df/pipeline_df method. "
            'Please install the SDK using "pip install python-aiplatform[full]"'
        )

    pd.testing.assert_frame_equal(
        dataframe_1.sort_index(axis=1), dataframe_2.sort_index(axis=1), check_names=True
    )


class TestMetadata:
    def setup_method(self):
        reload(initializer)
        reload(metadata)
        reload(aiplatform)

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

    def test_init_experiment_with_existing_description(
        self, get_metadata_store_mock, get_context_mock
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
            experiment_description=_TEST_EXPERIMENT_DESCRIPTION,
        )

        get_metadata_store_mock.assert_called_once_with(name=_TEST_METADATASTORE)
        get_context_mock.assert_called_once_with(name=_TEST_CONTEXT_NAME)

    @pytest.mark.usefixtures("get_metadata_store_mock")
    @pytest.mark.usefixtures("get_context_mock")
    def test_init_experiment_without_existing_description(self, update_context_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
            experiment_description=_TEST_OTHER_EXPERIMENT_DESCRIPTION,
        )

        experiment_context = GapicContext(
            name=_TEST_CONTEXT_NAME,
            display_name=_TEST_EXPERIMENT,
            description=_TEST_OTHER_EXPERIMENT_DESCRIPTION,
            schema_title=constants.SYSTEM_EXPERIMENT,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_EXPERIMENT],
            metadata=constants.EXPERIMENT_METADATA,
        )

        update_context_mock.assert_called_once_with(context=experiment_context)

    @pytest.mark.usefixtures("get_metadata_store_mock")
    @pytest.mark.usefixtures("get_context_wrong_schema_mock")
    def test_init_experiment_wrong_schema(self):
        with pytest.raises(ValueError):
            aiplatform.init(
                project=_TEST_PROJECT,
                location=_TEST_LOCATION,
                experiment=_TEST_EXPERIMENT,
            )

    @pytest.mark.usefixtures("get_metadata_store_mock")
    @pytest.mark.usefixtures("get_context_mock")
    @pytest.mark.usefixtures("get_execution_mock")
    @pytest.mark.usefixtures("add_context_artifacts_and_executions_mock")
    @pytest.mark.usefixtures("get_artifact_mock")
    @pytest.mark.usefixtures("add_execution_events_mock")
    def test_init_experiment_reset(self):
        aiplatform.init(
            project=_TEST_PROJECT, location=_TEST_LOCATION, experiment=_TEST_EXPERIMENT
        )
        aiplatform.start_run(_TEST_RUN)

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        assert metadata.metadata_service.experiment_name == _TEST_EXPERIMENT
        assert metadata.metadata_service.run_name == _TEST_RUN

        aiplatform.init(project=_TEST_OTHER_PROJECT, location=_TEST_LOCATION)

        assert metadata.metadata_service.experiment_name is None
        assert metadata.metadata_service.run_name is None

    @pytest.mark.usefixtures("get_metadata_store_mock")
    @pytest.mark.usefixtures("get_context_mock")
    def test_start_run_with_existing_execution_and_artifact(
        self,
        get_execution_mock,
        add_context_artifacts_and_executions_mock,
        get_artifact_mock,
        add_execution_events_mock,
    ):
        aiplatform.init(
            project=_TEST_PROJECT, location=_TEST_LOCATION, experiment=_TEST_EXPERIMENT
        )
        aiplatform.start_run(_TEST_RUN)

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
    @pytest.mark.usefixtures("get_execution_wrong_schema_mock")
    def test_start_run_with_wrong_run_execution_schema(self,):
        aiplatform.init(
            project=_TEST_PROJECT, location=_TEST_LOCATION, experiment=_TEST_EXPERIMENT
        )
        with pytest.raises(ValueError):
            aiplatform.start_run(_TEST_RUN)

    @pytest.mark.usefixtures("get_metadata_store_mock")
    @pytest.mark.usefixtures("get_context_mock")
    @pytest.mark.usefixtures("get_execution_mock")
    @pytest.mark.usefixtures("add_context_artifacts_and_executions_mock")
    @pytest.mark.usefixtures("get_artifact_wrong_schema_mock")
    def test_start_run_with_wrong_metrics_artifact_schema(self,):
        aiplatform.init(
            project=_TEST_PROJECT, location=_TEST_LOCATION, experiment=_TEST_EXPERIMENT
        )
        with pytest.raises(ValueError):
            aiplatform.start_run(_TEST_RUN)

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
        aiplatform.start_run(_TEST_RUN)
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
        aiplatform.start_run(_TEST_RUN)
        aiplatform.log_metrics(_TEST_METRICS)

        updated_artifact = GapicArtifact(
            name=_TEST_ARTIFACT_NAME,
            display_name=_TEST_ARTIFACT_ID,
            schema_title=constants.SYSTEM_METRICS,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_METRICS],
            metadata=_TEST_METRICS,
        )

        update_artifact_mock.assert_called_once_with(artifact=updated_artifact)

    @pytest.mark.usefixtures("get_metadata_store_mock")
    @pytest.mark.usefixtures("get_context_mock")
    @pytest.mark.usefixtures("get_execution_mock")
    @pytest.mark.usefixtures("add_context_artifacts_and_executions_mock")
    @pytest.mark.usefixtures("get_artifact_mock")
    @pytest.mark.usefixtures("add_execution_events_mock")
    def test_log_metrics_string_value_raise_error(self):
        aiplatform.init(
            project=_TEST_PROJECT, location=_TEST_LOCATION, experiment=_TEST_EXPERIMENT
        )
        aiplatform.start_run(_TEST_RUN)
        with pytest.raises(TypeError):
            aiplatform.log_metrics({"test": "string"})

    @pytest.mark.usefixtures("get_context_mock")
    def test_get_experiment_df(
        self, list_executions_mock, query_execution_inputs_and_outputs_mock
    ):
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "Pandas is not installed and is required to test the get_experiment_df method. "
                'Please install the SDK using "pip install python-aiplatform[full]"'
            )
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        experiment_df = aiplatform.get_experiment_df(_TEST_EXPERIMENT)

        expected_filter = f'schema_title="{constants.SYSTEM_RUN}" AND in_context("{_TEST_CONTEXT_NAME}")'
        list_executions_mock.assert_called_once_with(
            request=ListExecutionsRequest(parent=_TEST_PARENT, filter=expected_filter,)
        )
        query_execution_inputs_and_outputs_mock.assert_has_calls(
            [
                call(execution=_TEST_EXECUTION_NAME),
                call(execution=_TEST_OTHER_EXECUTION_NAME),
            ]
        )
        experiment_df_truth = pd.DataFrame(
            [
                {
                    "experiment_name": _TEST_EXPERIMENT,
                    "run_name": _TEST_RUN,
                    "param.%s" % _TEST_PARAM_KEY_1: 0.01,
                    "param.%s" % _TEST_PARAM_KEY_2: 0.2,
                    "metric.%s" % _TEST_METRIC_KEY_1: 222,
                    "metric.%s" % _TEST_METRIC_KEY_2: 1,
                },
                {
                    "experiment_name": _TEST_EXPERIMENT,
                    "run_name": _TEST_OTHER_RUN,
                    "param.%s" % _TEST_PARAM_KEY_1: 0.02,
                    "param.%s" % _TEST_PARAM_KEY_2: 0.3,
                    "metric.%s" % _TEST_METRIC_KEY_2: 0.9,
                },
            ]
        )

        _assert_frame_equal_with_sorted_columns(experiment_df, experiment_df_truth)

    @pytest.mark.usefixtures("get_context_not_found_mock")
    def test_get_experiment_df_not_exist(self):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with pytest.raises(exceptions.NotFound):
            aiplatform.get_experiment_df(_TEST_EXPERIMENT)

    @pytest.mark.usefixtures("get_pipeline_context_mock")
    def test_get_experiment_df_wrong_schema(self):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with pytest.raises(ValueError):
            aiplatform.get_experiment_df(_TEST_EXPERIMENT)

    @pytest.mark.usefixtures("get_pipeline_context_mock")
    def test_get_pipeline_df(
        self, list_executions_mock, query_execution_inputs_and_outputs_mock
    ):
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "Pandas is not installed and is required to test the get_pipeline_df method. "
                'Please install the SDK using "pip install python-aiplatform[full]"'
            )
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        pipeline_df = aiplatform.get_pipeline_df(_TEST_PIPELINE)

        expected_filter = f'schema_title="{constants.SYSTEM_RUN}" AND in_context("{_TEST_CONTEXT_NAME}")'
        list_executions_mock.assert_called_once_with(
            request=ListExecutionsRequest(parent=_TEST_PARENT, filter=expected_filter,)
        )
        query_execution_inputs_and_outputs_mock.assert_has_calls(
            [
                call(execution=_TEST_EXECUTION_NAME),
                call(execution=_TEST_OTHER_EXECUTION_NAME),
            ]
        )
        pipeline_df_truth = pd.DataFrame(
            [
                {
                    "pipeline_name": _TEST_PIPELINE,
                    "run_name": _TEST_RUN,
                    "param.%s" % _TEST_PARAM_KEY_1: 0.01,
                    "param.%s" % _TEST_PARAM_KEY_2: 0.2,
                    "metric.%s" % _TEST_METRIC_KEY_1: 222,
                    "metric.%s" % _TEST_METRIC_KEY_2: 1,
                },
                {
                    "pipeline_name": _TEST_PIPELINE,
                    "run_name": _TEST_OTHER_RUN,
                    "param.%s" % _TEST_PARAM_KEY_1: 0.02,
                    "param.%s" % _TEST_PARAM_KEY_2: 0.3,
                    "metric.%s" % _TEST_METRIC_KEY_2: 0.9,
                },
            ]
        )

        _assert_frame_equal_with_sorted_columns(pipeline_df, pipeline_df_truth)

    @pytest.mark.usefixtures("get_context_not_found_mock")
    def test_get_pipeline_df_not_exist(self):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with pytest.raises(exceptions.NotFound):
            aiplatform.get_pipeline_df(_TEST_PIPELINE)

    @pytest.mark.usefixtures("get_context_mock")
    def test_get_pipeline_df_wrong_schema(self):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with pytest.raises(ValueError):
            aiplatform.get_pipeline_df(_TEST_PIPELINE)
