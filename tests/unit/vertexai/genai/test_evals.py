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
# pylint: disable=protected-access,bad-continuation,
import base64
import importlib
import json
import os
import re
import statistics
import sys
import tempfile
import unittest
from unittest import mock

import google.auth.credentials
from google.cloud import aiplatform
import vertexai
from google.cloud.aiplatform import initializer as aiplatform_initializer
from vertexai import _genai
from vertexai._genai import _evals_data_converters
from vertexai._genai import _evals_metric_handlers
from vertexai._genai import _evals_visualization
from vertexai._genai import _evals_metric_loaders
from vertexai._genai import _gcs_utils
from vertexai._genai import _observability_data_converter
from vertexai._genai import _transformers
from vertexai._genai import evals
from vertexai._genai import types as vertexai_genai_types
from vertexai._genai.types import common as common_types
from google.genai import client
from google.genai import errors as genai_errors
from google.genai import types as genai_types
import pandas as pd
import pytest

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"


_evals_common = _genai.evals._evals_common
_evals_utils = _genai._evals_utils

pytestmark = pytest.mark.usefixtures("google_auth_mock")


class TestDropEmptyColumns:
    """Unit tests for the _drop_empty_columns function."""

    def test_drop_empty_columns(self):
        df = pd.DataFrame(
            {
                "col1": [1, 2, 3],
                "col2": [None, None, None],
                "col3": [[], [], []],
                "col4": [{}, {}, {}],
                "col5": [1, None, []],
            }
        )
        result_df = _evals_common._drop_empty_columns(df)
        assert "col1" in result_df.columns
        assert "col2" not in result_df.columns
        assert "col3" not in result_df.columns
        assert "col4" not in result_df.columns
        assert "col5" in result_df.columns

    def test_drop_empty_columns_all_empty(self):
        df = pd.DataFrame(
            {
                "col1": [None, None, None],
                "col2": [[], [], []],
            }
        )
        result_df = _evals_common._drop_empty_columns(df)
        assert result_df.empty

    def test_drop_empty_columns_none_empty(self):
        df = pd.DataFrame(
            {
                "col1": [1, 2, 3],
                "col2": ["a", "b", "c"],
            }
        )
        result_df = _evals_common._drop_empty_columns(df)
        assert list(result_df.columns) == ["col1", "col2"]


def _create_content_dump(text: str) -> dict[str, list[genai_types.Content]]:
    return {
        "contents": [
            genai_types.Content(parts=[genai_types.Part(text=text)]).model_dump(
                mode="json", exclude_none=True
            )
        ]
    }


@pytest.fixture
def mock_api_client_fixture():
    mock_client = mock.Mock(spec=client.Client)
    mock_client.project = _TEST_PROJECT
    mock_client.location = _TEST_LOCATION
    mock_client._credentials = mock.create_autospec(
        google.auth.credentials.Credentials, instance=True
    )
    mock_client._credentials.universe_domain = "googleapis.com"
    mock_client._evals_client = mock.Mock(spec=evals.Evals)
    mock_client._http_options = None
    return mock_client


@pytest.fixture
def mock_eval_dependencies(mock_api_client_fixture):
    with mock.patch("google.cloud.storage.Client") as mock_storage_client, mock.patch(
        "google.cloud.bigquery.Client"
    ) as mock_bq_client, mock.patch(
        "vertexai._genai.evals.Evals.evaluate_instances"
    ) as mock_evaluate_instances, mock.patch(
        "vertexai._genai._gcs_utils.GcsUtils.upload_json_to_prefix"
    ) as mock_upload_to_gcs, mock.patch(
        "vertexai._genai._evals_metric_loaders.LazyLoadedPrebuiltMetric._fetch_and_parse"
    ) as mock_fetch_prebuilt_metric:

        def mock_evaluate_instances_side_effect(*args, **kwargs):
            metric_config = kwargs.get("metric_config", {})
            if "exact_match_input" in metric_config:
                return vertexai_genai_types.EvaluateInstancesResponse(
                    exact_match_results=vertexai_genai_types.ExactMatchResults(
                        exact_match_metric_values=[
                            genai_types.ExactMatchMetricValue(score=1.0)
                        ]
                    )
                )
            elif "rouge_input" in metric_config:
                return vertexai_genai_types.EvaluateInstancesResponse(
                    rouge_results=vertexai_genai_types.RougeResults(
                        rouge_metric_values=[genai_types.RougeMetricValue(score=0.8)]
                    )
                )

            elif "comet_input" in metric_config:
                return vertexai_genai_types.EvaluateInstancesResponse(
                    comet_result=vertexai_genai_types.CometResult(score=0.75)
                )
            return vertexai_genai_types.EvaluateInstancesResponse()

        mock_evaluate_instances.side_effect = mock_evaluate_instances_side_effect
        mock_upload_to_gcs.return_value = (
            "gs://mock-bucket/mock_path/evaluation_result_timestamp.json"
        )
        mock_prebuilt_fluency_metric = vertexai_genai_types.LLMMetric(
            name="fluency", prompt_template="Is this fluent? {response}"
        )
        mock_prebuilt_fluency_metric._is_predefined = True
        mock_prebuilt_fluency_metric._config_source = (
            "gs://mock-metrics/fluency/v1.yaml"
        )
        mock_prebuilt_fluency_metric._version = "v1"

        mock_fetch_prebuilt_metric.return_value = mock_prebuilt_fluency_metric

        yield {
            "mock_storage_client": mock_storage_client,
            "mock_bq_client": mock_bq_client,
            "mock_evaluate_instances": mock_evaluate_instances,
            "mock_upload_to_gcs": mock_upload_to_gcs,
            "mock_fetch_prebuilt_metric": mock_fetch_prebuilt_metric,
            "mock_prebuilt_fluency_metric": mock_prebuilt_fluency_metric,
        }


class TestGetApiClientWithLocation:
    @mock.patch("vertexai._genai._evals_common.vertexai.Client")
    def test_get_api_client_with_location_override(
        self, mock_vertexai_client, mock_api_client_fixture
    ):
        mock_api_client_fixture.location = "us-central1"
        new_location = "europe-west1"
        _evals_common._get_api_client_with_location(
            mock_api_client_fixture, new_location
        )
        mock_vertexai_client.assert_called_once_with(
            project=mock_api_client_fixture.project,
            location=new_location,
            credentials=mock_api_client_fixture._credentials,
            http_options=mock_api_client_fixture._http_options,
        )

    @mock.patch("vertexai._genai._evals_common.vertexai.Client")
    def test_get_api_client_with_same_location(
        self, mock_vertexai_client, mock_api_client_fixture
    ):
        mock_api_client_fixture.location = "us-central1"
        new_location = "us-central1"
        _evals_common._get_api_client_with_location(
            mock_api_client_fixture, new_location
        )
        mock_vertexai_client.assert_not_called()

    @mock.patch("vertexai._genai._evals_common.vertexai.Client")
    def test_get_api_client_with_none_location(
        self, mock_vertexai_client, mock_api_client_fixture
    ):
        mock_api_client_fixture.location = "us-central1"
        new_location = None
        _evals_common._get_api_client_with_location(
            mock_api_client_fixture, new_location
        )
        mock_vertexai_client.assert_not_called()


class TestTransformers:
    """Unit tests for transformers."""

    def test_t_inline_results(self):
        eval_result = common_types.EvaluationResult(
            eval_case_results=[
                common_types.EvalCaseResult(
                    eval_case_index=0,
                    response_candidate_results=[
                        common_types.ResponseCandidateResult(
                            response_index=0,
                            metric_results={
                                "tool_use_quality": common_types.EvalCaseMetricResult(
                                    score=0.0,
                                    explanation="Failed tool use",
                                )
                            },
                        )
                    ],
                )
            ],
            evaluation_dataset=[
                common_types.EvaluationDataset(
                    eval_cases=[
                        common_types.EvalCase(
                            prompt=genai_types.Content(
                                parts=[genai_types.Part(text="test prompt")]
                            )
                        )
                    ]
                )
            ],
            metadata=common_types.EvaluationRunMetadata(candidate_names=["gemini-pro"]),
        )

        payload = _transformers.t_inline_results([eval_result])

        assert len(payload) == 1
        assert payload[0]["metric"] == "tool_use_quality"
        assert payload[0]["request"]["prompt"]["text"] == "test prompt"
        assert len(payload[0]["candidate_results"]) == 1
        assert payload[0]["candidate_results"][0]["candidate"] == "gemini-pro"
        assert payload[0]["candidate_results"][0]["score"] == 0.0

    def test_t_inline_results_sanitizes_agent_data(self):
        """Tests that t_inline_results strips SDK-only fields from agent_data."""
        eval_result = common_types.EvaluationResult(
            eval_case_results=[
                common_types.EvalCaseResult(
                    eval_case_index=0,
                    response_candidate_results=[
                        common_types.ResponseCandidateResult(
                            response_index=0,
                            metric_results={
                                "multi_turn_task_success_v1": common_types.EvalCaseMetricResult(
                                    score=0.0,
                                    explanation="Failed",
                                )
                            },
                        )
                    ],
                )
            ],
            evaluation_dataset=[
                common_types.EvaluationDataset(
                    eval_cases=[
                        common_types.EvalCase(
                            agent_data=vertexai_genai_types.evals.AgentData(
                                turns=[
                                    vertexai_genai_types.evals.ConversationTurn(
                                        turn_index=0,
                                        turn_id="turn_0",
                                        events=[
                                            vertexai_genai_types.evals.AgentEvent(
                                                author="user",
                                                content=genai_types.Content(
                                                    role="user",
                                                    parts=[
                                                        genai_types.Part(text="Hello")
                                                    ],
                                                ),
                                            ),
                                            vertexai_genai_types.evals.AgentEvent(
                                                author="model",
                                                content=genai_types.Content(
                                                    role="model",
                                                    parts=[
                                                        genai_types.Part(
                                                            function_call=genai_types.FunctionCall(
                                                                name="search",
                                                                args={"q": "test"},
                                                            )
                                                        )
                                                    ],
                                                ),
                                            ),
                                            vertexai_genai_types.evals.AgentEvent(
                                                author="model",
                                                content=genai_types.Content(
                                                    role="model",
                                                    parts=[
                                                        genai_types.Part(
                                                            function_response=genai_types.FunctionResponse(
                                                                name="search",
                                                                response={
                                                                    "result": "ok"
                                                                },
                                                            )
                                                        )
                                                    ],
                                                ),
                                            ),
                                        ],
                                    )
                                ]
                            )
                        )
                    ]
                )
            ],
            metadata=common_types.EvaluationRunMetadata(
                candidate_names=["travel-agent"]
            ),
        )

        payload = _transformers.t_inline_results([eval_result])
        assert len(payload) == 1

        agent_data = payload[0]["request"]["prompt"]["agent_data"]
        assert "turns" in agent_data
        events = agent_data["turns"][0]["events"]
        assert len(events) == 3

        # Check text part is preserved
        text_part = events[0]["content"]["parts"][0]
        assert "text" in text_part
        assert text_part["text"] == "Hello"

        # Check function_call is preserved (API-recognized field)
        fc_part = events[1]["content"]["parts"][0]
        assert "function_call" in fc_part
        assert fc_part["function_call"]["name"] == "search"
        # SDK-only fields must NOT be present
        assert "tool_call" not in fc_part
        assert "tool_response" not in fc_part
        assert "part_metadata" not in fc_part

        # Check function_response is preserved but will_continue is stripped
        fr_part = events[2]["content"]["parts"][0]
        assert "function_response" in fr_part
        assert fr_part["function_response"]["name"] == "search"
        assert "will_continue" not in fr_part["function_response"]

    def test_sanitize_agent_data_from_dataframe(self):
        """Tests sanitization when agent_data comes from DataFrame (dict form)."""
        # Simulate agent_data stored in DataFrame with SDK-only fields
        raw_agent_data = {
            "turns": [
                {
                    "turn_index": 0,
                    "turn_id": "turn_0",
                    "events": [
                        {
                            "author": "model",
                            "content": {
                                "role": "model",
                                "parts": [
                                    {
                                        "function_call": {
                                            "name": "find_flights",
                                            "args": {"origin": "NYC"},
                                        },
                                        "tool_call": None,
                                        "tool_response": None,
                                        "part_metadata": None,
                                    }
                                ],
                            },
                        },
                        {
                            "author": "model",
                            "content": {
                                "role": "model",
                                "parts": [
                                    {
                                        "function_response": {
                                            "name": "find_flights",
                                            "response": {"flights": []},
                                            "will_continue": False,
                                            "scheduling": None,
                                        },
                                    }
                                ],
                            },
                        },
                    ],
                }
            ],
        }

        sanitized = _transformers._sanitize_agent_data(raw_agent_data)

        parts_0 = sanitized["turns"][0]["events"][0]["content"]["parts"][0]
        assert "function_call" in parts_0
        assert "tool_call" not in parts_0
        assert "tool_response" not in parts_0
        assert "part_metadata" not in parts_0

        parts_1 = sanitized["turns"][0]["events"][1]["content"]["parts"][0]
        assert "function_response" in parts_1
        assert parts_1["function_response"]["name"] == "find_flights"
        assert "will_continue" not in parts_1["function_response"]
        assert "scheduling" not in parts_1["function_response"]

    def test_sanitize_agent_data_skips_error_payload(self):
        """Tests that error payloads from failed agent runs are stripped."""
        error_data = {"error": "Multi-turn agent run with user simulation failed"}
        sanitized = _transformers._sanitize_agent_data(error_data)
        assert "error" not in sanitized
        assert sanitized == {}

    def test_t_inline_results_skips_error_agent_data_in_df(self):
        """Tests that t_inline_results skips error agent_data from DataFrame."""
        error_json = json.dumps({"error": "Agent run failed"})
        df = pd.DataFrame(
            {
                "prompt": ["test"],
                "agent_data": [error_json],
            }
        )
        eval_result = common_types.EvaluationResult(
            eval_case_results=[
                common_types.EvalCaseResult(
                    eval_case_index=0,
                    response_candidate_results=[
                        common_types.ResponseCandidateResult(
                            response_index=0,
                            metric_results={
                                "metric_v1": common_types.EvalCaseMetricResult(
                                    score=0.0,
                                )
                            },
                        )
                    ],
                )
            ],
            evaluation_dataset=[common_types.EvaluationDataset(eval_dataset_df=df)],
            metadata=common_types.EvaluationRunMetadata(candidate_names=["agent"]),
        )
        payload = _transformers.t_inline_results([eval_result])
        assert len(payload) == 1
        # The prompt should have no agent_data (error was skipped)
        assert "agent_data" not in payload[0]["request"]["prompt"]


class TestLossAnalysis:
    """Unit tests for loss analysis types and visualization."""

    def test_response_structure(self):
        response = common_types.GenerateLossClustersResponse(
            analysis_time="2026-04-01T10:00:00Z",
            results=[
                common_types.LossAnalysisResult(
                    config=common_types.LossAnalysisConfig(
                        metric="multi_turn_task_success_v1",
                        candidate="travel-agent",
                    ),
                    analysis_time="2026-04-01T10:00:00Z",
                    clusters=[
                        common_types.LossCluster(
                            cluster_id="cluster-1",
                            taxonomy_entry=common_types.LossTaxonomyEntry(
                                l1_category="Tool Calling",
                                l2_category="Missing Tool Invocation",
                                description="The agent failed to invoke a required tool.",
                            ),
                            item_count=3,
                        ),
                        common_types.LossCluster(
                            cluster_id="cluster-2",
                            taxonomy_entry=common_types.LossTaxonomyEntry(
                                l1_category="Hallucination",
                                l2_category="Hallucination of Action",
                                description="Verbally confirmed action without tool.",
                            ),
                            item_count=2,
                        ),
                    ],
                )
            ],
        )
        assert len(response.results) == 1
        assert response.analysis_time == "2026-04-01T10:00:00Z"
        result = response.results[0]
        assert result.config.metric == "multi_turn_task_success_v1"
        assert len(result.clusters) == 2
        assert result.clusters[0].cluster_id == "cluster-1"
        assert result.clusters[0].item_count == 3
        assert result.clusters[1].cluster_id == "cluster-2"

    def test_get_loss_analysis_html(self):
        """Tests that _get_loss_analysis_html generates valid HTML with data."""
        from vertexai._genai import _evals_visualization
        import json

        data = {
            "results": [
                {
                    "config": {
                        "metric": "test_metric",
                        "candidate": "test-candidate",
                    },
                    "clusters": [
                        {
                            "cluster_id": "c1",
                            "taxonomy_entry": {
                                "l1_category": "Tool Calling",
                                "l2_category": "Missing Invocation",
                                "description": "Agent failed to call the tool.",
                            },
                            "item_count": 5,
                            "examples": [
                                {
                                    "evaluation_result": {
                                        "request": {
                                            "prompt": {
                                                "agent_data": {
                                                    "turns": [
                                                        {
                                                            "turn_index": 0,
                                                            "events": [
                                                                {
                                                                    "author": "user",
                                                                    "content": {
                                                                        "parts": [
                                                                            {
                                                                                "text": "Find flights to Paris"
                                                                            }
                                                                        ],
                                                                    },
                                                                }
                                                            ],
                                                        }
                                                    ],
                                                },
                                            },
                                        },
                                    },
                                    "failed_rubrics": [
                                        {
                                            "rubric_id": "tool_use",
                                            "classification_rationale": "Did not invoke find_flights.",
                                        }
                                    ],
                                }
                            ],
                        },
                    ],
                }
            ]
        }
        html = _evals_visualization._get_loss_analysis_html(json.dumps(data))
        assert "Loss Pattern Analysis" in html
        assert "test_metric" not in html  # data is Base64-encoded in the HTML
        assert "<!DOCTYPE html>" in html
        assert "extractScenarioPreview" in html
        assert "example-scenario" in html
        assert "DOMPurify" in html  # uses DOMPurify for sanitization
        assert "example-section-label" in html  # labels for scenario/rubrics
        assert "Analysis Summary" in html  # summary heading

    def test_display_loss_clusters_response_no_ipython(self):
        """Tests graceful fallback when not in IPython."""
        from vertexai._genai import _evals_visualization
        from unittest import mock

        response = common_types.GenerateLossClustersResponse(
            results=[
                common_types.LossAnalysisResult(
                    config=common_types.LossAnalysisConfig(
                        metric="test_metric",
                        candidate="test-candidate",
                    ),
                    clusters=[
                        common_types.LossCluster(
                            cluster_id="c1",
                            taxonomy_entry=common_types.LossTaxonomyEntry(
                                l1_category="Cat1",
                                l2_category="SubCat1",
                            ),
                            item_count=5,
                        ),
                    ],
                )
            ],
        )
        with mock.patch.object(
            _evals_visualization, "_is_ipython_env", return_value=False
        ):
            # Should not raise, just log a warning
            response.show()

    def test_display_loss_analysis_result_no_ipython(self):
        """Tests graceful fallback for individual result when not in IPython."""
        from vertexai._genai import _evals_visualization
        from unittest import mock

        result = common_types.LossAnalysisResult(
            config=common_types.LossAnalysisConfig(
                metric="test_metric",
                candidate="test-candidate",
            ),
            clusters=[
                common_types.LossCluster(
                    cluster_id="c1",
                    taxonomy_entry=common_types.LossTaxonomyEntry(
                        l1_category="DirectCat",
                        l2_category="DirectSubCat",
                    ),
                    item_count=7,
                ),
            ],
        )
        with mock.patch.object(
            _evals_visualization, "_is_ipython_env", return_value=False
        ):
            result.show()

    def test_enrich_scenario_from_agent_data_in_eval_cases(self):
        """Tests scenario extraction from agent_data in eval_cases."""
        from vertexai._genai import _evals_utils

        # API response: evaluation_result has NO request (real API behavior)
        api_response = common_types.GenerateLossClustersResponse(
            results=[
                common_types.LossAnalysisResult(
                    config=common_types.LossAnalysisConfig(
                        metric="multi_turn_task_success_v1",
                        candidate="travel-agent",
                    ),
                    clusters=[
                        common_types.LossCluster(
                            cluster_id="c1",
                            taxonomy_entry=common_types.LossTaxonomyEntry(
                                l1_category="Tool Calling",
                                l2_category="Missing Invocation",
                            ),
                            item_count=1,
                            examples=[
                                common_types.LossExample(
                                    evaluation_result={
                                        "candidateResults": [
                                            {
                                                "candidate": "travel-agent",
                                                "metric": "multi_turn_task_success_v1",
                                            }
                                        ]
                                    },
                                    failed_rubrics=[
                                        common_types.FailedRubric(
                                            rubric_id="tool_use",
                                            classification_rationale="Did not call tool.",
                                        )
                                    ],
                                )
                            ],
                        )
                    ],
                )
            ],
        )
        # Original eval_result with agent_data in eval_cases
        eval_result = common_types.EvaluationResult(
            eval_case_results=[
                common_types.EvalCaseResult(
                    eval_case_index=0,
                    response_candidate_results=[
                        common_types.ResponseCandidateResult(
                            response_index=0,
                            metric_results={
                                "multi_turn_task_success_v1": common_types.EvalCaseMetricResult(
                                    score=0.0,
                                ),
                            },
                        )
                    ],
                )
            ],
            evaluation_dataset=[
                common_types.EvaluationDataset(
                    eval_cases=[
                        common_types.EvalCase(
                            agent_data=vertexai_genai_types.evals.AgentData(
                                turns=[
                                    vertexai_genai_types.evals.ConversationTurn(
                                        turn_index=0,
                                        events=[
                                            vertexai_genai_types.evals.AgentEvent(
                                                author="user",
                                                content={
                                                    "parts": [
                                                        {
                                                            "text": "Book a flight to Paris."
                                                        }
                                                    ]
                                                },
                                            ),
                                        ],
                                    )
                                ],
                            )
                        )
                    ]
                )
            ],
            metadata=common_types.EvaluationRunMetadata(
                candidate_names=["travel-agent"]
            ),
        )

        _evals_utils._enrich_loss_response_with_rubric_descriptions(
            api_response, eval_result
        )
        example = api_response.results[0].clusters[0].examples[0]
        assert "scenario_preview" in example.evaluation_result
        assert (
            example.evaluation_result["scenario_preview"] == "Book a flight to Paris."
        )

    def test_enrich_scenario_from_user_scenario_starting_prompt(self):
        """Tests scenario extraction from user_scenario.starting_prompt."""
        from vertexai._genai import _evals_utils

        api_response = common_types.GenerateLossClustersResponse(
            results=[
                common_types.LossAnalysisResult(
                    config=common_types.LossAnalysisConfig(
                        metric="multi_turn_task_success_v1",
                        candidate="travel-agent",
                    ),
                    clusters=[
                        common_types.LossCluster(
                            cluster_id="c1",
                            taxonomy_entry=common_types.LossTaxonomyEntry(
                                l1_category="Tool Calling",
                                l2_category="Missing Invocation",
                            ),
                            item_count=1,
                            examples=[
                                common_types.LossExample(
                                    evaluation_result={
                                        "candidateResults": [
                                            {"candidate": "travel-agent"}
                                        ]
                                    },
                                    failed_rubrics=[
                                        common_types.FailedRubric(rubric_id="t1")
                                    ],
                                )
                            ],
                        )
                    ],
                )
            ],
        )
        # eval_result with user_scenario (from generate_conversation_scenarios)
        eval_result = common_types.EvaluationResult(
            eval_case_results=[
                common_types.EvalCaseResult(
                    eval_case_index=0,
                    response_candidate_results=[
                        common_types.ResponseCandidateResult(
                            response_index=0,
                            metric_results={
                                "multi_turn_task_success_v1": common_types.EvalCaseMetricResult(
                                    score=0.0,
                                ),
                            },
                        )
                    ],
                )
            ],
            evaluation_dataset=[
                common_types.EvaluationDataset(
                    eval_cases=[
                        common_types.EvalCase(
                            user_scenario=vertexai_genai_types.evals.UserScenario(
                                starting_prompt="I want to book a hotel in Tokyo.",
                                conversation_plan="User asks to book a hotel.",
                            )
                        )
                    ]
                )
            ],
            metadata=common_types.EvaluationRunMetadata(
                candidate_names=["travel-agent"]
            ),
        )

        _evals_utils._enrich_loss_response_with_rubric_descriptions(
            api_response, eval_result
        )
        example = api_response.results[0].clusters[0].examples[0]
        assert "scenario_preview" in example.evaluation_result
        assert (
            example.evaluation_result["scenario_preview"]
            == "I want to book a hotel in Tokyo."
        )

    def test_enrich_scenario_from_dataframe_agent_data(self):
        """Tests scenario extraction from DataFrame agent_data column."""
        import pandas as pd
        from vertexai._genai import _evals_utils

        api_response = common_types.GenerateLossClustersResponse(
            results=[
                common_types.LossAnalysisResult(
                    config=common_types.LossAnalysisConfig(
                        metric="multi_turn_task_success_v1",
                        candidate="travel-agent",
                    ),
                    clusters=[
                        common_types.LossCluster(
                            cluster_id="c1",
                            taxonomy_entry=common_types.LossTaxonomyEntry(
                                l1_category="Tool Calling",
                                l2_category="Missing Invocation",
                            ),
                            item_count=1,
                            examples=[
                                common_types.LossExample(
                                    evaluation_result={
                                        "candidateResults": [
                                            {"candidate": "travel-agent"}
                                        ]
                                    },
                                    failed_rubrics=[
                                        common_types.FailedRubric(rubric_id="t1")
                                    ],
                                )
                            ],
                        )
                    ],
                )
            ],
        )
        # eval_result with agent_data in DataFrame (run_inference output)
        agent_data_obj = vertexai_genai_types.evals.AgentData(
            turns=[
                vertexai_genai_types.evals.ConversationTurn(
                    turn_index=0,
                    events=[
                        vertexai_genai_types.evals.AgentEvent(
                            author="user",
                            content={"parts": [{"text": "Find flights to London"}]},
                        ),
                    ],
                )
            ],
        )
        df = pd.DataFrame({"agent_data": [agent_data_obj]})
        eval_result = common_types.EvaluationResult(
            eval_case_results=[
                common_types.EvalCaseResult(
                    eval_case_index=0,
                    response_candidate_results=[
                        common_types.ResponseCandidateResult(
                            response_index=0,
                            metric_results={
                                "multi_turn_task_success_v1": common_types.EvalCaseMetricResult(
                                    score=0.0,
                                ),
                            },
                        )
                    ],
                )
            ],
            evaluation_dataset=[common_types.EvaluationDataset(eval_dataset_df=df)],
            metadata=common_types.EvaluationRunMetadata(
                candidate_names=["travel-agent"]
            ),
        )

        _evals_utils._enrich_loss_response_with_rubric_descriptions(
            api_response, eval_result
        )
        example = api_response.results[0].clusters[0].examples[0]
        assert "scenario_preview" in example.evaluation_result
        assert example.evaluation_result["scenario_preview"] == "Find flights to London"

    def test_enrich_scenario_e2e_simulation(self):
        """Simulates the full e2e flow: generate_scenarios -> run_inference -> evaluate -> loss_clusters."""
        import pandas as pd
        from vertexai._genai import _evals_utils

        # Step 1: Simulate generate_conversation_scenarios output
        # This creates eval_cases with user_scenario but no agent_data
        scenario_dataset = common_types.EvaluationDataset(
            eval_cases=[
                common_types.EvalCase(
                    user_scenario=vertexai_genai_types.evals.UserScenario(
                        starting_prompt="I need to book a flight from NYC to Paris for next Friday.",
                        conversation_plan="User books a flight.",
                    )
                )
            ],
            eval_dataset_df=pd.DataFrame(
                {
                    "starting_prompt": [
                        "I need to book a flight from NYC to Paris for next Friday."
                    ],
                    "conversation_plan": ["User books a flight."],
                }
            ),
        )

        # Step 2: Simulate run_inference output
        # run_inference extracts eval_dataset_df from the input, runs inference,
        # then returns a NEW EvaluationDataset with only eval_dataset_df (no eval_cases)
        agent_data_obj = vertexai_genai_types.evals.AgentData(
            agents={
                "travel_agent": vertexai_genai_types.evals.AgentConfig(
                    agent_id="travel_agent",
                )
            },
            turns=[
                vertexai_genai_types.evals.ConversationTurn(
                    turn_index=0,
                    events=[
                        vertexai_genai_types.evals.AgentEvent(
                            author="user",
                            content=genai_types.Content(
                                parts=[
                                    genai_types.Part(
                                        text="I need to book a flight from NYC to Paris for next Friday."
                                    )
                                ],
                                role="user",
                            ),
                        ),
                        vertexai_genai_types.evals.AgentEvent(
                            author="travel_agent",
                            content=genai_types.Content(
                                parts=[
                                    genai_types.Part(
                                        text="I'll help you book that flight."
                                    )
                                ],
                                role="model",
                            ),
                        ),
                    ],
                ),
            ],
        )
        inference_df = pd.concat(
            [
                scenario_dataset.eval_dataset_df.reset_index(drop=True),
                pd.DataFrame({"agent_data": [agent_data_obj]}).reset_index(drop=True),
            ],
            axis=1,
        )
        inference_dataset = common_types.EvaluationDataset(
            eval_dataset_df=inference_df,
            candidate_name="travel_agent",
        )

        # Step 3: Simulate evaluate() output
        # evaluate() stores the dataset (from step 2) in evaluation_dataset
        eval_result = common_types.EvaluationResult(
            eval_case_results=[
                common_types.EvalCaseResult(
                    eval_case_index=0,
                    response_candidate_results=[
                        common_types.ResponseCandidateResult(
                            response_index=0,
                            metric_results={
                                "multi_turn_task_success_v1": common_types.EvalCaseMetricResult(
                                    score=0.0,
                                    explanation="Failed",
                                ),
                            },
                        )
                    ],
                )
            ],
            evaluation_dataset=[inference_dataset],  # Note: no eval_cases!
            metadata=common_types.EvaluationRunMetadata(
                candidate_names=["travel_agent"]
            ),
        )

        # Step 4: Simulate API response (no request in evaluationResult)
        api_response = common_types.GenerateLossClustersResponse(
            results=[
                common_types.LossAnalysisResult(
                    config=common_types.LossAnalysisConfig(
                        metric="multi_turn_task_success_v1",
                        candidate="travel_agent",
                    ),
                    clusters=[
                        common_types.LossCluster(
                            cluster_id="c1",
                            taxonomy_entry=common_types.LossTaxonomyEntry(
                                l1_category="Tool Calling",
                                l2_category="Missing Invocation",
                                description="Agent failed to invoke the tool.",
                            ),
                            item_count=1,
                            examples=[
                                common_types.LossExample(
                                    evaluation_result={
                                        "candidateResults": [
                                            {
                                                "candidate": "travel_agent",
                                                "metric": "multi_turn_task_success_v1",
                                            }
                                        ]
                                    },
                                    failed_rubrics=[
                                        common_types.FailedRubric(
                                            rubric_id="tool_use",
                                            classification_rationale="Did not call find_flights.",
                                        )
                                    ],
                                )
                            ],
                        )
                    ],
                )
            ],
        )

        # Verify intermediate steps
        scenario_list = _evals_utils._build_scenario_preview_list(eval_result)
        assert len(scenario_list) == 1, f"Expected 1 scenario, got {len(scenario_list)}"
        assert scenario_list[0] is not None, (
            f"Scenario is None. eval_dataset type: {type(eval_result.evaluation_dataset)}, "
            f"eval_cases: {eval_result.evaluation_dataset[0].eval_cases if eval_result.evaluation_dataset else 'N/A'}, "
            f"df columns: {list(eval_result.evaluation_dataset[0].eval_dataset_df.columns) if eval_result.evaluation_dataset and eval_result.evaluation_dataset[0].eval_dataset_df is not None else 'N/A'}"
        )

        # Step 5: Enrich and verify
        _evals_utils._enrich_loss_response_with_rubric_descriptions(
            api_response, eval_result
        )
        example = api_response.results[0].clusters[0].examples[0]
        assert (
            "scenario_preview" in example.evaluation_result
        ), f"scenario_preview not found. evaluation_result keys: {list(example.evaluation_result.keys())}"
        assert (
            "I need to book a flight" in example.evaluation_result["scenario_preview"]
        )

        # Verify the full serialization pipeline (model_dump -> JSON -> parse)
        import json

        result_dump = api_response.model_dump(mode="json", exclude_none=True)
        json_str = json.dumps(result_dump)
        parsed = json.loads(json_str)
        ex_parsed = parsed["results"][0]["clusters"][0]["examples"][0]
        assert "scenario_preview" in ex_parsed.get(
            "evaluation_result", {}
        ), f"scenario_preview missing after serialization. Keys: {list(ex_parsed.get('evaluation_result', {}).keys())}"
        assert (
            "I need to book a flight"
            in ex_parsed["evaluation_result"]["scenario_preview"]
        )

    def test_enrich_scenario_from_dataframe_starting_prompt(self):
        """Tests scenario extraction from DataFrame starting_prompt column."""
        import pandas as pd
        from vertexai._genai import _evals_utils

        api_response = common_types.GenerateLossClustersResponse(
            results=[
                common_types.LossAnalysisResult(
                    config=common_types.LossAnalysisConfig(
                        metric="m1",
                        candidate="c1",
                    ),
                    clusters=[
                        common_types.LossCluster(
                            cluster_id="c1",
                            taxonomy_entry=common_types.LossTaxonomyEntry(
                                l1_category="Cat",
                                l2_category="SubCat",
                            ),
                            item_count=1,
                            examples=[
                                common_types.LossExample(
                                    evaluation_result={"candidateResults": []},
                                    failed_rubrics=[
                                        common_types.FailedRubric(rubric_id="r1")
                                    ],
                                )
                            ],
                        )
                    ],
                )
            ],
        )
        # DataFrame with starting_prompt but no agent_data
        df = pd.DataFrame(
            {
                "starting_prompt": ["Cancel my reservation please"],
                "conversation_plan": ["User wants to cancel."],
            }
        )
        eval_result = common_types.EvaluationResult(
            eval_case_results=[
                common_types.EvalCaseResult(
                    eval_case_index=0,
                    response_candidate_results=[
                        common_types.ResponseCandidateResult(
                            response_index=0,
                            metric_results={
                                "m1": common_types.EvalCaseMetricResult(score=0.0)
                            },
                        )
                    ],
                )
            ],
            evaluation_dataset=[common_types.EvaluationDataset(eval_dataset_df=df)],
        )

        _evals_utils._enrich_loss_response_with_rubric_descriptions(
            api_response, eval_result
        )
        example = api_response.results[0].clusters[0].examples[0]
        assert "scenario_preview" in example.evaluation_result
        assert (
            example.evaluation_result["scenario_preview"]
            == "Cancel my reservation please"
        )


def _make_eval_result(
    metrics=None,
    candidate_names=None,
):
    """Helper to create an EvaluationResult with the given metrics and candidates."""
    metrics = metrics or ["task_success_v1"]
    candidate_names = candidate_names or ["agent-1"]

    metric_results = {}
    for m in metrics:
        metric_results[m] = common_types.EvalCaseMetricResult(metric_name=m)

    eval_case_results = [
        common_types.EvalCaseResult(
            eval_case_index=0,
            response_candidate_results=[
                common_types.ResponseCandidateResult(
                    response_index=0,
                    metric_results=metric_results,
                )
            ],
        )
    ]
    metadata = common_types.EvaluationRunMetadata(
        candidate_names=candidate_names,
    )
    return common_types.EvaluationResult(
        eval_case_results=eval_case_results,
        metadata=metadata,
    )


class TestEvalRunLossAnalysis:
    """Tests for loss analysis integration with EvaluationRun."""

    def test_evaluation_run_config_accepts_loss_analysis_config(self):
        """Tests that EvaluationRunConfig can hold loss_analysis_config."""
        config = common_types.EvaluationRunConfig(
            metrics=[],
            loss_analysis_config=[
                common_types.LossAnalysisConfig(
                    metric="multi_turn_task_success_v1",
                    candidate="travel-agent",
                ),
                common_types.LossAnalysisConfig(
                    metric="multi_turn_tool_use_quality_v1",
                    candidate="travel-agent",
                ),
            ],
        )
        assert len(config.loss_analysis_config) == 2
        assert config.loss_analysis_config[0].metric == "multi_turn_task_success_v1"
        assert config.loss_analysis_config[1].metric == "multi_turn_tool_use_quality_v1"

    def test_evaluation_run_config_loss_analysis_config_optional(self):
        """Tests that loss_analysis_config defaults to None when not provided."""
        config = common_types.EvaluationRunConfig(metrics=[])
        assert config.loss_analysis_config is None

    def test_evaluation_run_results_has_loss_analysis_results(self):
        """Tests that EvaluationRunResults can hold loss_analysis_results."""
        results = common_types.EvaluationRunResults(
            evaluation_set="projects/123/locations/global/evaluationSets/456",
            summary_metrics=common_types.SummaryMetric(
                metrics={}, total_items=10, failed_items=0
            ),
            loss_analysis_results=[
                common_types.LossAnalysisResult(
                    config=common_types.LossAnalysisConfig(
                        metric="multi_turn_task_success_v1",
                        candidate="travel-agent",
                    ),
                    clusters=[
                        common_types.LossCluster(
                            cluster_id="c1",
                            taxonomy_entry=common_types.LossTaxonomyEntry(
                                l1_category="Hallucination",
                                l2_category="Hallucination of Action",
                            ),
                            item_count=3,
                        )
                    ],
                )
            ],
        )
        assert len(results.loss_analysis_results) == 1
        assert results.loss_analysis_results[0].clusters[0].item_count == 3

    def test_evaluation_run_results_loss_analysis_results_optional(self):
        """Tests backward compat: loss_analysis_results defaults to None."""
        results = common_types.EvaluationRunResults(
            evaluation_set="projects/123/locations/global/evaluationSets/456",
            summary_metrics=common_types.SummaryMetric(
                metrics={}, total_items=5, failed_items=0
            ),
        )
        assert results.loss_analysis_results is None

    def test_evaluation_run_show_displays_loss_analysis_without_map(self):
        """Tests show() calls display with eval_item_map=None when no map set."""
        eval_run = common_types.EvaluationRun(
            name="projects/123/locations/global/evaluationRuns/test-run",
            state="SUCCEEDED",
            evaluation_run_results=common_types.EvaluationRunResults(
                evaluation_set="projects/123/locations/global/evaluationSets/456",
                summary_metrics=common_types.SummaryMetric(
                    metrics={}, total_items=5, failed_items=0
                ),
                loss_analysis_results=[
                    common_types.LossAnalysisResult(
                        config=common_types.LossAnalysisConfig(
                            metric="multi_turn_task_success_v1",
                            candidate="agent-1",
                        ),
                        clusters=[],
                    )
                ],
            ),
        )
        with mock.patch.object(
            _evals_visualization,
            "display_loss_analysis_results",
        ) as mock_display:
            eval_run.show()
            mock_display.assert_called_once_with(
                eval_run.evaluation_run_results.loss_analysis_results,
                eval_item_map=None,
            )

    def test_evaluation_run_show_passes_eval_item_map(self):
        """Tests show() passes _eval_item_map to display when set via object.__setattr__."""
        eval_run = common_types.EvaluationRun(
            name="projects/123/locations/global/evaluationRuns/test-run",
            state="SUCCEEDED",
            evaluation_run_results=common_types.EvaluationRunResults(
                evaluation_set="projects/123/locations/global/evaluationSets/456",
                summary_metrics=common_types.SummaryMetric(
                    metrics={}, total_items=5, failed_items=0
                ),
                loss_analysis_results=[
                    common_types.LossAnalysisResult(
                        config=common_types.LossAnalysisConfig(
                            metric="multi_turn_task_success_v1",
                            candidate="agent-1",
                        ),
                        clusters=[
                            common_types.LossCluster(
                                cluster_id="c1",
                                item_count=1,
                                examples=[
                                    common_types.LossExample(
                                        evaluation_item="projects/123/locations/global/evaluationItems/item-1",
                                    )
                                ],
                            )
                        ],
                    )
                ],
            ),
        )
        # Simulate what get_evaluation_run does: set _eval_item_map via object.__setattr__
        # to bypass pydantic extra='forbid'
        test_map = {
            "projects/123/locations/global/evaluationItems/item-1": {
                "request": {
                    "prompt": {
                        "agent_data": {
                            "turns": [
                                {
                                    "events": [
                                        {
                                            "author": "user",
                                            "content": {"parts": [{"text": "Hello"}]},
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }
            }
        }
        object.__setattr__(eval_run, "_eval_item_map", test_map)

        # Verify _eval_item_map is accessible via getattr
        assert getattr(eval_run, "_eval_item_map", None) is test_map

        with mock.patch.object(
            _evals_visualization,
            "display_loss_analysis_results",
        ) as mock_display:
            eval_run.show()
            mock_display.assert_called_once_with(
                eval_run.evaluation_run_results.loss_analysis_results,
                eval_item_map=test_map,
            )

    def test_evaluation_run_show_no_loss_analysis_does_not_crash(self):
        """Tests EvaluationRun.show() works when no loss analysis results."""
        eval_run = common_types.EvaluationRun(
            name="projects/123/locations/global/evaluationRuns/test-run",
            state="SUCCEEDED",
            evaluation_run_results=common_types.EvaluationRunResults(
                evaluation_set="projects/123/locations/global/evaluationSets/456",
                summary_metrics=common_types.SummaryMetric(
                    metrics={}, total_items=5, failed_items=0
                ),
            ),
        )
        with mock.patch.object(
            _evals_visualization,
            "display_loss_analysis_results",
        ) as mock_display:
            # Should not crash; loss analysis display should NOT be called
            eval_run.show()
            mock_display.assert_not_called()

    def test_display_loss_analysis_results_html(self):
        """Tests that display_loss_analysis_results produces valid HTML."""
        results = [
            common_types.LossAnalysisResult(
                config=common_types.LossAnalysisConfig(
                    metric="multi_turn_task_success_v1",
                    candidate="agent-1",
                ),
                clusters=[
                    common_types.LossCluster(
                        cluster_id="c1",
                        taxonomy_entry=common_types.LossTaxonomyEntry(
                            l1_category="Tool Calling",
                            l2_category="Missing Invocation",
                            description="Agent failed to call the tool.",
                        ),
                        item_count=5,
                    )
                ],
            )
        ]
        payload_json = json.dumps(
            {
                "results": [
                    r.model_dump(mode="json", exclude_none=True) for r in results
                ]
            },
            ensure_ascii=False,
        )
        html = _evals_visualization._get_loss_analysis_html(payload_json)
        # The HTML is a self-contained report with base64-encoded JSON payload
        # decoded by JavaScript at runtime. Verify structure, not content.
        assert "<!DOCTYPE html>" in html
        assert "Loss Pattern Analysis" in html
        # Verify the payload is embedded as base64 in the HTML
        payload_b64 = base64.b64encode(payload_json.encode("utf-8")).decode("ascii")
        assert payload_b64 in html

    def test_enrich_loss_examples_with_eval_item_map(self):
        """Tests that _enrich_loss_examples_with_eval_items populates evaluation_result."""
        # Create loss results where examples only have evaluation_item (eval run path)
        results = [
            common_types.LossAnalysisResult(
                config=common_types.LossAnalysisConfig(
                    metric="multi_turn_task_success_v1",
                    candidate="agent-1",
                ),
                clusters=[
                    common_types.LossCluster(
                        cluster_id="c1",
                        taxonomy_entry=common_types.LossTaxonomyEntry(
                            l1_category="Tool Calling",
                            l2_category="Missing Invocation",
                        ),
                        item_count=2,
                        examples=[
                            common_types.LossExample(
                                evaluation_item="projects/123/locations/global/evaluationItems/item-1",
                                failed_rubrics=[
                                    common_types.FailedRubric(
                                        rubric_id="tool_invocation"
                                    )
                                ],
                            ),
                            common_types.LossExample(
                                evaluation_item="projects/123/locations/global/evaluationItems/item-2",
                                failed_rubrics=[
                                    common_types.FailedRubric(
                                        rubric_id="tool_invocation"
                                    )
                                ],
                            ),
                        ],
                    )
                ],
            )
        ]

        # Build an eval_item_map matching the actual eval run data shape:
        # - scenario is in prompt.user_scenario.starting_prompt
        # - agent traces are in candidate_responses[].agent_data.turns
        # - rubric verdicts are in candidate_results[].rubric_verdicts
        eval_item_map = {
            "projects/123/locations/global/evaluationItems/item-1": {
                "request": {
                    "prompt": {
                        "user_scenario": {
                            "starting_prompt": "Book a flight to Paris",
                        }
                    },
                    "candidate_responses": [
                        {
                            "candidate": "agent-1",
                            "agent_data": {
                                "turns": [
                                    {
                                        "events": [
                                            {
                                                "author": "user",
                                                "content": {
                                                    "parts": [
                                                        {
                                                            "text": "Book a flight to Paris"
                                                        }
                                                    ]
                                                },
                                            }
                                        ],
                                    }
                                ]
                            },
                        }
                    ],
                },
                "candidate_results": [
                    {
                        "metric": "multi_turn_task_success_v1",
                        "candidate": "agent-1",
                        "rubric_verdicts": [
                            {
                                "evaluated_rubric": {
                                    "rubric_id": "tool_invocation",
                                    "content": {
                                        "property": {
                                            "description": "Agent should call find_flights tool"
                                        }
                                    },
                                },
                                "verdict": False,
                            }
                        ],
                    }
                ],
            },
            "projects/123/locations/global/evaluationItems/item-2": {
                "request": {
                    "prompt": {
                        "user_scenario": {
                            "starting_prompt": "Find hotels in Tokyo",
                        }
                    },
                    "candidate_responses": [
                        {
                            "candidate": "agent-1",
                            "agent_data": {
                                "turns": [
                                    {
                                        "events": [
                                            {
                                                "author": "user",
                                                "content": {
                                                    "parts": [
                                                        {"text": "Find hotels in Tokyo"}
                                                    ]
                                                },
                                            }
                                        ],
                                    }
                                ]
                            },
                        }
                    ],
                },
                "candidate_results": [],
            },
        }

        enriched = _evals_visualization._enrich_loss_examples_with_eval_items(
            results, eval_item_map
        )

        # Verify enrichment happened
        assert len(enriched) == 1
        clusters = enriched[0]["clusters"]
        assert len(clusters) == 1
        examples = clusters[0]["examples"]
        assert len(examples) == 2

        # First example should have evaluation_result with user_scenario
        ex1 = examples[0]
        assert "evaluation_result" in ex1
        er1 = ex1["evaluation_result"]
        assert (
            er1["request"]["prompt"]["user_scenario"]["starting_prompt"]
            == "Book a flight to Paris"
        )
        # Agent data is on candidate_responses (eval run path)
        assert (
            er1["request"]["candidate_responses"][0]["agent_data"]["turns"][0][
                "events"
            ][0]["content"]["parts"][0]["text"]
            == "Book a flight to Paris"
        )
        # Rubric data
        assert (
            er1["candidate_results"][0]["rubric_verdicts"][0]["evaluated_rubric"][
                "content"
            ]["property"]["description"]
            == "Agent should call find_flights tool"
        )

        # Second example should also have evaluation_result
        ex2 = examples[1]
        assert "evaluation_result" in ex2
        er2 = ex2["evaluation_result"]
        assert (
            er2["request"]["prompt"]["user_scenario"]["starting_prompt"]
            == "Find hotels in Tokyo"
        )

    def test_enrich_skips_already_populated_evaluation_result(self):
        """Tests that enrichment skips examples that already have evaluation_result (LRO path)."""
        results = [
            common_types.LossAnalysisResult(
                config=common_types.LossAnalysisConfig(metric="m1", candidate="c1"),
                clusters=[
                    common_types.LossCluster(
                        cluster_id="c1",
                        item_count=1,
                        examples=[
                            common_types.LossExample(
                                evaluation_item="projects/123/locations/global/evaluationItems/item-1",
                                evaluation_result={
                                    "request": {"prompt": {"text": "original"}}
                                },
                            ),
                        ],
                    )
                ],
            )
        ]
        eval_item_map = {
            "projects/123/locations/global/evaluationItems/item-1": {
                "request": {"prompt": {"text": "should-not-replace"}}
            },
        }
        enriched = _evals_visualization._enrich_loss_examples_with_eval_items(
            results, eval_item_map
        )
        # Should keep the original evaluation_result, not replace it
        ex = enriched[0]["clusters"][0]["examples"][0]
        assert ex["evaluation_result"]["request"]["prompt"]["text"] == "original"

    def test_enrich_with_none_map(self):
        """Tests enrichment with no eval_item_map (backward compat)."""
        results = [
            common_types.LossAnalysisResult(
                config=common_types.LossAnalysisConfig(metric="m1", candidate="c1"),
                clusters=[
                    common_types.LossCluster(
                        cluster_id="c1",
                        item_count=1,
                        examples=[
                            common_types.LossExample(
                                evaluation_item="projects/123/evaluationItems/item-1",
                            ),
                        ],
                    )
                ],
            )
        ]
        enriched = _evals_visualization._enrich_loss_examples_with_eval_items(
            results, None
        )
        # Should not crash, evaluation_result stays absent
        ex = enriched[0]["clusters"][0]["examples"][0]
        assert "evaluation_result" not in ex

    def test_evaluation_run_config_serialization_with_loss_analysis(self):
        """Tests that EvaluationRunConfig with loss_analysis_config serializes."""
        config = common_types.EvaluationRunConfig(
            metrics=[],
            loss_analysis_config=[
                common_types.LossAnalysisConfig(
                    metric="multi_turn_task_success_v1",
                    candidate="travel-agent",
                ),
            ],
        )
        dumped = config.model_dump(mode="json", exclude_none=True)
        assert "loss_analysis_config" in dumped
        assert len(dumped["loss_analysis_config"]) == 1
        assert (
            dumped["loss_analysis_config"][0]["metric"] == "multi_turn_task_success_v1"
        )


class TestResolveEvalRunLossConfigs:
    """Unit tests for _resolve_eval_run_loss_configs."""

    def test_none_when_no_args(self):
        result = _evals_utils._resolve_eval_run_loss_configs()
        assert result is None

    def test_loss_analysis_metrics_single_candidate(self):
        """Auto-infers candidate from single-entry inference_configs."""
        result = _evals_utils._resolve_eval_run_loss_configs(
            loss_analysis_metrics=["multi_turn_task_success_v1"],
            inference_configs={"my-agent": {}},
        )
        assert len(result) == 1
        assert result[0].metric == "multi_turn_task_success_v1"
        assert result[0].candidate == "my-agent"

    def test_loss_analysis_metrics_multiple_metrics(self):
        """Creates one config per metric, all with same inferred candidate."""
        result = _evals_utils._resolve_eval_run_loss_configs(
            loss_analysis_metrics=[
                "multi_turn_task_success_v1",
                "multi_turn_tool_use_quality_v1",
            ],
            inference_configs={"travel-agent": {}},
        )
        assert len(result) == 2
        assert result[0].metric == "multi_turn_task_success_v1"
        assert result[0].candidate == "travel-agent"
        assert result[1].metric == "multi_turn_tool_use_quality_v1"
        assert result[1].candidate == "travel-agent"

    def test_loss_analysis_metrics_multi_candidate_raises(self):
        """Raises when multiple candidates and using simplified metrics."""
        with pytest.raises(ValueError, match="multiple candidates"):
            _evals_utils._resolve_eval_run_loss_configs(
                loss_analysis_metrics=["task_success_v1"],
                inference_configs={"agent-a": {}, "agent-b": {}},
            )

    def test_loss_analysis_metrics_no_inference_configs(self):
        """Creates configs with candidate=None when no inference_configs."""
        result = _evals_utils._resolve_eval_run_loss_configs(
            loss_analysis_metrics=["task_success_v1"],
        )
        assert len(result) == 1
        assert result[0].metric == "task_success_v1"
        assert result[0].candidate is None

    def test_loss_analysis_configs_passthrough(self):
        """Explicit configs are passed through without modification."""
        configs = [
            common_types.LossAnalysisConfig(
                metric="task_success_v1",
                candidate="agent-1",
                max_top_cluster_count=5,
            )
        ]
        result = _evals_utils._resolve_eval_run_loss_configs(
            loss_analysis_configs=configs,
        )
        assert len(result) == 1
        assert result[0].metric == "task_success_v1"
        assert result[0].candidate == "agent-1"
        assert result[0].max_top_cluster_count == 5

    def test_loss_analysis_configs_dict_input(self):
        """Dict configs are validated into LossAnalysisConfig objects."""
        result = _evals_utils._resolve_eval_run_loss_configs(
            loss_analysis_configs=[
                {"metric": "task_success_v1", "candidate": "agent-1"}
            ],
        )
        assert len(result) == 1
        assert isinstance(result[0], common_types.LossAnalysisConfig)
        assert result[0].metric == "task_success_v1"

    def test_loss_analysis_metrics_accepts_metric_object(self):
        """Accepts Metric objects in loss_analysis_metrics."""
        metric = common_types.Metric(name="multi_turn_task_success_v1")
        result = _evals_utils._resolve_eval_run_loss_configs(
            loss_analysis_metrics=[metric],
            inference_configs={"agent-1": {}},
        )
        assert len(result) == 1
        assert result[0].metric == "multi_turn_task_success_v1"
        assert result[0].candidate == "agent-1"


class TestResolveMetricName:
    """Unit tests for _resolve_metric_name."""

    def test_none_returns_none(self):
        assert _evals_utils._resolve_metric_name(None) is None

    def test_string_passes_through(self):
        assert _evals_utils._resolve_metric_name("task_success_v1") == "task_success_v1"

    def test_metric_object_extracts_name(self):
        metric = common_types.Metric(name="multi_turn_task_success_v1")
        assert _evals_utils._resolve_metric_name(metric) == "multi_turn_task_success_v1"

    def test_object_with_name_attr(self):
        """Tests that any object with a .name attribute works (e.g., LazyLoadedPrebuiltMetric)."""

        class FakeMetric:
            name = "tool_use_quality_v1"

        assert _evals_utils._resolve_metric_name(FakeMetric()) == "tool_use_quality_v1"

    def test_lazy_loaded_prebuilt_metric_resolves_versioned_name(self):
        """Tests that LazyLoadedPrebuiltMetric resolves to the versioned API spec name."""

        class FakeLazyMetric:
            name = "MULTI_TURN_TASK_SUCCESS"

            def _get_api_metric_spec_name(self):
                return "multi_turn_task_success_v1"

        assert (
            _evals_utils._resolve_metric_name(FakeLazyMetric())
            == "multi_turn_task_success_v1"
        )

    def test_lazy_loaded_prebuilt_metric_falls_back_to_name(self):
        """Tests fallback to .name when _get_api_metric_spec_name returns None."""

        class FakeLazyMetricNoSpec:
            name = "CUSTOM_METRIC"

            def _get_api_metric_spec_name(self):
                return None

        assert (
            _evals_utils._resolve_metric_name(FakeLazyMetricNoSpec()) == "CUSTOM_METRIC"
        )


class TestResolveLossAnalysisConfig:
    """Unit tests for _resolve_loss_analysis_config."""

    def test_auto_infer_single_metric_and_candidate(self):
        eval_result = _make_eval_result(
            metrics=["task_success_v1"], candidate_names=["agent-1"]
        )
        resolved = _evals_utils._resolve_loss_analysis_config(eval_result=eval_result)
        assert resolved.metric == "task_success_v1"
        assert resolved.candidate == "agent-1"

    def test_explicit_metric_and_candidate(self):
        eval_result = _make_eval_result(
            metrics=["m1", "m2"], candidate_names=["c1", "c2"]
        )
        resolved = _evals_utils._resolve_loss_analysis_config(
            eval_result=eval_result, metric="m1", candidate="c2"
        )
        assert resolved.metric == "m1"
        assert resolved.candidate == "c2"

    def test_config_provides_metric_and_candidate(self):
        eval_result = _make_eval_result(metrics=["m1"], candidate_names=["c1"])
        config = common_types.LossAnalysisConfig(
            metric="m1", candidate="c1", predefined_taxonomy="my_taxonomy"
        )
        resolved = _evals_utils._resolve_loss_analysis_config(
            eval_result=eval_result, config=config
        )
        assert resolved.metric == "m1"
        assert resolved.candidate == "c1"
        assert resolved.predefined_taxonomy == "my_taxonomy"

    def test_explicit_args_override_config(self):
        eval_result = _make_eval_result(
            metrics=["m1", "m2"], candidate_names=["c1", "c2"]
        )
        config = common_types.LossAnalysisConfig(metric="m1", candidate="c1")
        resolved = _evals_utils._resolve_loss_analysis_config(
            eval_result=eval_result, config=config, metric="m2", candidate="c2"
        )
        assert resolved.metric == "m2"
        assert resolved.candidate == "c2"

    def test_error_multiple_metrics_no_explicit(self):
        eval_result = _make_eval_result(metrics=["m1", "m2"], candidate_names=["c1"])
        with pytest.raises(ValueError, match="multiple metrics"):
            _evals_utils._resolve_loss_analysis_config(eval_result=eval_result)

    def test_error_multiple_candidates_no_explicit(self):
        eval_result = _make_eval_result(metrics=["m1"], candidate_names=["c1", "c2"])
        with pytest.raises(ValueError, match="multiple candidates"):
            _evals_utils._resolve_loss_analysis_config(eval_result=eval_result)

    def test_error_invalid_metric(self):
        eval_result = _make_eval_result(metrics=["m1"], candidate_names=["c1"])
        with pytest.raises(ValueError, match="not found in eval_result"):
            _evals_utils._resolve_loss_analysis_config(
                eval_result=eval_result, metric="nonexistent"
            )

    def test_error_invalid_candidate(self):
        eval_result = _make_eval_result(metrics=["m1"], candidate_names=["c1"])
        with pytest.raises(ValueError, match="not found in eval_result"):
            _evals_utils._resolve_loss_analysis_config(
                eval_result=eval_result, candidate="nonexistent"
            )

    def test_no_candidates_defaults_to_candidate_1(self):
        eval_result = _make_eval_result(metrics=["m1"], candidate_names=[])
        eval_result = eval_result.model_copy(
            update={"metadata": common_types.EvaluationRunMetadata()}
        )
        resolved = _evals_utils._resolve_loss_analysis_config(eval_result=eval_result)
        assert resolved.metric == "m1"
        assert resolved.candidate == "candidate_1"

    def test_no_eval_case_results_raises(self):
        eval_result = common_types.EvaluationResult()
        with pytest.raises(ValueError, match="no metric results"):
            _evals_utils._resolve_loss_analysis_config(eval_result=eval_result)


class TestEvals:
    """Unit tests for the GenAI client."""

    def setup_method(self):
        importlib.reload(aiplatform_initializer)
        importlib.reload(aiplatform)
        importlib.reload(vertexai)
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        self.client = vertexai.Client(project=_TEST_PROJECT, location=_TEST_LOCATION)

    @pytest.mark.usefixtures("google_auth_mock")
    @mock.patch.object(client.Client, "_get_api_client")
    @mock.patch.object(evals.Evals, "batch_evaluate")
    def test_eval_batch_evaluate(self, mock_evaluate, mock_get_api_client):
        test_client = vertexai.Client(project=_TEST_PROJECT, location=_TEST_LOCATION)
        test_client.evals.batch_evaluate(
            dataset=vertexai_genai_types.EvaluationDataset(),
            metrics=[vertexai_genai_types.Metric(name="test")],
            dest="gs://bucket/output",
            config=vertexai_genai_types.EvaluateDatasetConfig(),
        )
        mock_evaluate.assert_called_once()

    @pytest.mark.usefixtures("google_auth_mock")
    @mock.patch.object(_evals_common, "_execute_evaluation")
    def test_eval_evaluate_with_agent_info(self, mock_execute_evaluation):
        """Tests that agent_info is passed to _execute_evaluation."""
        dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=pd.DataFrame([{"prompt": "p1", "response": "r1"}])
        )
        agent_info = {
            "name": "agent_system",
            "agents": {"agent1": {"agent_id": "agent1", "instruction": "instruction1"}},
        }
        self.client.evals.evaluate(
            dataset=dataset,
            metrics=[vertexai_genai_types.Metric(name="exact_match")],
            agent_info=agent_info,
        )
        mock_execute_evaluation.assert_called_once()
        _, kwargs = mock_execute_evaluation.call_args
        assert "agent_info" in kwargs
        assert kwargs["agent_info"] == agent_info


class TestEvalsVisualization:
    @mock.patch(
        "vertexai._genai._evals_visualization._is_ipython_env",
        return_value=True,
    )
    def test_display_evaluation_result_with_agent_trace_prefixes(self, mock_is_ipython):
        """Tests that agent trace view includes added prefixes."""
        mock_display_module = mock.MagicMock()
        mock_ipython_module = mock.MagicMock()
        mock_ipython_module.display = mock_display_module
        sys.modules["IPython"] = mock_ipython_module
        sys.modules["IPython.display"] = mock_display_module

        intermediate_events_list = [
            {
                "content": {
                    "role": "model",
                    "parts": [
                        {
                            "function_call": {
                                "name": "my_function",
                                "args": {"arg1": "value1"},
                            }
                        }
                    ],
                }
            },
            {
                "content": {
                    "role": "model",
                    "parts": [{"text": "this is model response"}],
                }
            },
        ]
        dataset_df = pd.DataFrame(
            [
                {
                    "prompt": "Test prompt",
                    "response": "Test response",
                    "intermediate_events": intermediate_events_list,
                },
            ]
        )
        eval_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )
        eval_result = vertexai_genai_types.EvaluationResult(
            evaluation_dataset=[eval_dataset],
            agent_info=vertexai_genai_types.evals.AgentInfo(name="test_agent"),
            eval_case_results=[
                vertexai_genai_types.EvalCaseResult(
                    eval_case_index=0,
                    response_candidate_results=[
                        vertexai_genai_types.ResponseCandidateResult(
                            response_index=0, metric_results={}
                        )
                    ],
                )
            ],
        )

        _evals_visualization.display_evaluation_result(eval_result)

        mock_display_module.HTML.assert_called_once()
        html_content = mock_display_module.HTML.call_args[0][0]
        match = re.search(r'atob\("([^"]+)"\)', html_content)
        assert match
        decoded_json = base64.b64decode(match.group(1)).decode("utf-8")
        assert "my_function" in decoded_json
        assert "this is model response" in decoded_json

        del sys.modules["IPython"]
        del sys.modules["IPython.display"]

    @mock.patch(
        "vertexai._genai._evals_visualization._is_ipython_env",
        return_value=True,
    )
    def test_display_evaluation_result_with_non_ascii_character(self, mock_is_ipython):
        """Tests that non-ASCII characters are handled correctly."""
        mock_display_module = mock.MagicMock()
        mock_ipython_module = mock.MagicMock()
        mock_ipython_module.display = mock_display_module
        sys.modules["IPython"] = mock_ipython_module
        sys.modules["IPython.display"] = mock_display_module

        dataset_df = pd.DataFrame(
            [
                {
                    "prompt": "Test prompt with emoji 😊",
                    "response": "Test response with emoji 😊",
                },
            ]
        )
        eval_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )
        eval_result = vertexai_genai_types.EvaluationResult(
            evaluation_dataset=[eval_dataset],
            eval_case_results=[
                vertexai_genai_types.EvalCaseResult(
                    eval_case_index=0,
                    response_candidate_results=[
                        vertexai_genai_types.ResponseCandidateResult(
                            response_index=0, metric_results={}
                        )
                    ],
                )
            ],
        )

        _evals_visualization.display_evaluation_result(eval_result)

        mock_display_module.HTML.assert_called_once()
        html_content = mock_display_module.HTML.call_args[0][0]
        # Verify that the new decoding logic is present in the HTML
        assert "new TextDecoder().decode" in html_content

        match = re.search(r'atob\("([^"]+)"\)', html_content)
        assert match
        decoded_json = base64.b64decode(match.group(1)).decode("utf-8")

        # JSON serialization escapes non-ASCII characters (e.g. \uXXXX), so we
        # parse it back to check for the actual characters.
        parsed_json = json.loads(decoded_json)
        assert "Test prompt with emoji 😊" in json.dumps(
            parsed_json, ensure_ascii=False
        )
        assert "Test response with emoji 😊" in json.dumps(
            parsed_json, ensure_ascii=False
        )

        del sys.modules["IPython"]
        del sys.modules["IPython.display"]


class TestEvalsRunInference:
    """Unit tests for the Evals run_inference method."""

    def setup_method(self):
        importlib.reload(aiplatform_initializer)
        importlib.reload(aiplatform)
        importlib.reload(vertexai)
        importlib.reload(_genai.client)
        importlib.reload(vertexai_genai_types)
        importlib.reload(_evals_utils)
        importlib.reload(_evals_data_converters)
        importlib.reload(_evals_common)
        importlib.reload(_evals_metric_handlers)
        importlib.reload(_genai.evals)

        if hasattr(_evals_common._thread_local_data, "agent_engine_instances"):
            del _evals_common._thread_local_data.agent_engine_instances

        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        self.client = vertexai.Client(project=_TEST_PROJECT, location=_TEST_LOCATION)

    @mock.patch.object(_evals_common, "Models")
    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    def test_inference_drops_empty_columns(self, mock_eval_dataset_loader, mock_models):
        mock_df = pd.DataFrame(
            {
                "prompt": ["test prompt 1", "test prompt 2"],
                "empty_col": [None, None],
                "empty_list_col": [[], []],
            }
        )
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )

        mock_generate_content_response = genai_types.GenerateContentResponse(
            candidates=[
                genai_types.Candidate(
                    content=genai_types.Content(
                        parts=[genai_types.Part(text="test response")]
                    ),
                    finish_reason=genai_types.FinishReason.STOP,
                )
            ],
            prompt_feedback=None,
        )
        mock_models.return_value.generate_content.return_value = (
            mock_generate_content_response
        )

        inference_result = self.client.evals.run_inference(
            model="gemini-pro",
            src=mock_df,
        )

        assert "empty_col" not in inference_result.eval_dataset_df.columns
        assert "empty_list_col" not in inference_result.eval_dataset_df.columns
        assert "prompt" in inference_result.eval_dataset_df.columns
        assert "response" in inference_result.eval_dataset_df.columns

    @mock.patch.object(_evals_common, "Models")
    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    def test_inference_with_string_model_success(
        self, mock_eval_dataset_loader, mock_models
    ):
        mock_df = pd.DataFrame({"prompt": ["test prompt"]})
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )

        mock_generate_content_response = genai_types.GenerateContentResponse(
            candidates=[
                genai_types.Candidate(
                    content=genai_types.Content(
                        parts=[genai_types.Part(text="test response")]
                    ),
                    finish_reason=genai_types.FinishReason.STOP,
                )
            ],
            prompt_feedback=None,
        )
        mock_models.return_value.generate_content.return_value = (
            mock_generate_content_response
        )

        inference_result = self.client.evals.run_inference(
            model="gemini-pro",
            src=mock_df,
        )

        mock_eval_dataset_loader.return_value.load.assert_called_once_with(mock_df)
        mock_models.return_value.generate_content.assert_called_once()
        pd.testing.assert_frame_equal(
            inference_result.eval_dataset_df,
            pd.DataFrame(
                {
                    "prompt": ["test prompt"],
                    "response": ["test response"],
                }
            ),
        )
        assert inference_result.candidate_name == "gemini-pro"
        assert inference_result.gcs_source is None

    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    def test_inference_with_callable_model_sets_candidate_name(
        self, mock_eval_dataset_loader
    ):
        mock_df = pd.DataFrame({"prompt": ["test prompt"]})
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )

        def my_model_fn(contents):
            return "callable response"

        inference_result = self.client.evals.run_inference(
            model=my_model_fn,
            src=mock_df,
        )
        assert inference_result.candidate_name == "my_model_fn"
        assert inference_result.gcs_source is None

    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    def test_inference_with_lambda_model_candidate_name_is_none(
        self, mock_eval_dataset_loader
    ):
        mock_df = pd.DataFrame({"prompt": ["test prompt"]})
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )

        inference_result = self.client.evals.run_inference(
            model=lambda x: "lambda response",  # pylint: disable=unnecessary-lambda
            src=mock_df,
        )
        # Lambdas may or may not have a __name__ depending on Python version/env
        # but it's typically '<lambda>' if it exists.
        # The code under test uses getattr(model, "__name__", None)
        assert (
            inference_result.candidate_name == "<lambda>"
            or inference_result.candidate_name is None
        )
        assert inference_result.gcs_source is None

    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    def test_inference_with_callable_model_success(self, mock_eval_dataset_loader):
        mock_df = pd.DataFrame({"prompt": ["test prompt"]})
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )

        def mock_model_fn(contents):
            return "callable response"

        inference_result = self.client.evals.run_inference(
            model=mock_model_fn,
            src=mock_df,
        )
        mock_eval_dataset_loader.return_value.load.assert_called_once_with(mock_df)
        pd.testing.assert_frame_equal(
            inference_result.eval_dataset_df,
            pd.DataFrame(
                {
                    "prompt": ["test prompt"],
                    "response": ["callable response"],
                }
            ),
        )
        assert inference_result.candidate_name == "mock_model_fn"
        assert inference_result.gcs_source is None

    @mock.patch.object(_evals_common, "Models")
    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    def test_inference_with_prompt_template(
        self, mock_eval_dataset_loader, mock_models
    ):
        mock_df = pd.DataFrame({"text_input": ["world"]})
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )
        mock_generate_content_response = genai_types.GenerateContentResponse(
            candidates=[
                genai_types.Candidate(
                    content=genai_types.Content(
                        parts=[genai_types.Part(text="templated response")]
                    ),
                    finish_reason=genai_types.FinishReason.STOP,
                )
            ],
            prompt_feedback=None,
        )
        mock_models.return_value.generate_content.return_value = (
            mock_generate_content_response
        )

        config = vertexai_genai_types.EvalRunInferenceConfig(
            prompt_template="Hello {text_input}"
        )
        inference_result = self.client.evals.run_inference(
            model="gemini-pro", src=mock_df, config=config
        )
        assert (
            mock_models.return_value.generate_content.call_args[1]["contents"]
            == "Hello world"
        )
        pd.testing.assert_frame_equal(
            inference_result.eval_dataset_df,
            pd.DataFrame(
                {
                    "text_input": ["world"],
                    "request": ["Hello world"],
                    "response": ["templated response"],
                }
            ),
        )
        assert inference_result.candidate_name == "gemini-pro"
        assert inference_result.gcs_source is None

    @mock.patch.object(_evals_common, "Models")
    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    @mock.patch.object(_gcs_utils, "GcsUtils")
    def test_inference_with_gcs_destination(
        self, mock_gcs_utils, mock_eval_dataset_loader, mock_models
    ):
        mock_df = pd.DataFrame({"prompt": ["test prompt"]})
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )
        mock_generate_content_response = genai_types.GenerateContentResponse(
            candidates=[
                genai_types.Candidate(
                    content=genai_types.Content(
                        parts=[genai_types.Part(text="gcs response")]
                    ),
                    finish_reason=genai_types.FinishReason.STOP,
                )
            ],
            prompt_feedback=None,
        )
        mock_models.return_value.generate_content.return_value = (
            mock_generate_content_response
        )

        gcs_dest_dir = "gs://bucket/output"
        config = vertexai_genai_types.EvalRunInferenceConfig(dest=gcs_dest_dir)

        inference_result = self.client.evals.run_inference(
            model="gemini-pro", src=mock_df, config=config
        )

        expected_gcs_path = os.path.join(gcs_dest_dir, "inference_results.jsonl")
        expected_df_to_save = pd.DataFrame(
            {
                "prompt": ["test prompt"],
                "response": ["gcs response"],
            }
        )
        saved_df = mock_gcs_utils.return_value.upload_dataframe.call_args.kwargs["df"]
        pd.testing.assert_frame_equal(saved_df, expected_df_to_save)
        mock_gcs_utils.return_value.upload_dataframe.assert_called_once_with(
            df=mock.ANY,
            gcs_destination_blob_path=expected_gcs_path,
            file_type="jsonl",
        )
        pd.testing.assert_frame_equal(
            inference_result.eval_dataset_df, expected_df_to_save
        )
        assert inference_result.candidate_name == "gemini-pro"
        assert inference_result.gcs_source == genai_types.GcsSource(
            uris=[expected_gcs_path]
        )

    @mock.patch.object(_evals_common, "Models")
    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    @mock.patch("pandas.DataFrame.to_json")
    @mock.patch("os.makedirs")
    def test_inference_with_local_destination(
        self,
        mock_makedirs,
        mock_df_to_json,
        mock_eval_dataset_loader,
        mock_models,
    ):
        mock_df = pd.DataFrame({"prompt": ["local save"]})
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )
        mock_generate_content_response = genai_types.GenerateContentResponse(
            candidates=[
                genai_types.Candidate(
                    content=genai_types.Content(
                        parts=[genai_types.Part(text="local response")]
                    ),
                    finish_reason=genai_types.FinishReason.STOP,
                )
            ],
            prompt_feedback=None,
        )
        mock_models.return_value.generate_content.return_value = (
            mock_generate_content_response
        )

        with tempfile.TemporaryDirectory() as local_dest_dir:
            config = vertexai_genai_types.EvalRunInferenceConfig(dest=local_dest_dir)

            inference_result = self.client.evals.run_inference(
                model="gemini-pro", src=mock_df, config=config
            )

            mock_makedirs.assert_called_once_with(local_dest_dir, exist_ok=True)
            expected_save_path = os.path.join(local_dest_dir, "inference_results.jsonl")
            mock_df_to_json.assert_called_once_with(
                expected_save_path, orient="records", lines=True
            )
            expected_df = pd.DataFrame(
                {
                    "prompt": ["local save"],
                    "response": ["local response"],
                }
            )
            pd.testing.assert_frame_equal(inference_result.eval_dataset_df, expected_df)
            assert inference_result.candidate_name == "gemini-pro"
            assert inference_result.gcs_source is None

    @mock.patch.object(_evals_common, "Models")
    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    def test_inference_from_request_column_save_to_local_dir(
        self, mock_eval_dataset_loader, mock_models
    ):
        mock_df = pd.DataFrame(
            {"prompt": ["prompt 1", "prompt 2"], "request": ["req 1", "req 2"]}
        )
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )
        mock_generate_content_responses = [
            genai_types.GenerateContentResponse(
                candidates=[
                    genai_types.Candidate(
                        content=genai_types.Content(
                            parts=[genai_types.Part(text="resp 1")]
                        ),
                        finish_reason=genai_types.FinishReason.STOP,
                    )
                ],
                prompt_feedback=None,
            ),
            genai_types.GenerateContentResponse(
                candidates=[
                    genai_types.Candidate(
                        content=genai_types.Content(
                            parts=[genai_types.Part(text="resp 2")]
                        ),
                        finish_reason=genai_types.FinishReason.STOP,
                    )
                ],
                prompt_feedback=None,
            ),
        ]
        mock_models.return_value.generate_content.side_effect = (
            mock_generate_content_responses
        )

        with tempfile.TemporaryDirectory() as local_dest_dir:
            config = vertexai_genai_types.EvalRunInferenceConfig(dest=local_dest_dir)

            inference_result = self.client.evals.run_inference(
                model="gemini-pro", src=mock_df, config=config
            )

            mock_models.return_value.generate_content.assert_has_calls(
                [
                    mock.call(
                        model="gemini-pro",
                        contents="req 1",
                        config=genai_types.GenerateContentConfig(),
                    ),
                    mock.call(
                        model="gemini-pro",
                        contents="req 2",
                        config=genai_types.GenerateContentConfig(),
                    ),
                ],
                any_order=True,
            )
            expected_df = pd.DataFrame(
                {
                    "prompt": ["prompt 1", "prompt 2"],
                    "request": ["req 1", "req 2"],
                    "response": ["resp 1", "resp 2"],
                }
            )
            pd.testing.assert_frame_equal(
                inference_result.eval_dataset_df.sort_values(by="request").reset_index(
                    drop=True
                ),
                expected_df.sort_values(by="request").reset_index(drop=True),
            )

            saved_file_path = os.path.join(local_dest_dir, "inference_results.jsonl")
            with open(saved_file_path, "r") as f:
                saved_records = [json.loads(line) for line in f]
            expected_records = expected_df.to_dict(orient="records")
            assert sorted(saved_records, key=lambda x: x["request"]) == sorted(
                expected_records, key=lambda x: x["request"]
            )
            assert inference_result.candidate_name == "gemini-pro"
            assert inference_result.gcs_source is None

    @mock.patch.object(_evals_common, "Models")
    def test_inference_from_local_jsonl_file(self, mock_models):
        with tempfile.TemporaryDirectory() as temp_dir:
            local_src_path = os.path.join(temp_dir, "input.jsonl")
            input_records = [
                {"prompt": "prompt 1", "other_col": "val 1"},
                {"prompt": "prompt 2", "other_col": "val 2"},
            ]
            with open(local_src_path, "w") as f:
                for record in input_records:
                    f.write(json.dumps(record) + "\n")

            mock_generate_content_responses = [
                genai_types.GenerateContentResponse(
                    candidates=[
                        genai_types.Candidate(
                            content=genai_types.Content(
                                parts=[genai_types.Part(text="resp 1")]
                            ),
                            finish_reason=genai_types.FinishReason.STOP,
                        )
                    ],
                    prompt_feedback=None,
                ),
                genai_types.GenerateContentResponse(
                    candidates=[
                        genai_types.Candidate(
                            content=genai_types.Content(
                                parts=[genai_types.Part(text="resp 2")]
                            ),
                            finish_reason=genai_types.FinishReason.STOP,
                        )
                    ],
                    prompt_feedback=None,
                ),
            ]
            mock_models.return_value.generate_content.side_effect = (
                mock_generate_content_responses
            )

            inference_result = self.client.evals.run_inference(
                model="gemini-pro", src=local_src_path
            )

            expected_df = pd.DataFrame(
                {
                    "prompt": ["prompt 1", "prompt 2"],
                    "other_col": ["val 1", "val 2"],
                    "response": ["resp 1", "resp 2"],
                }
            )
            pd.testing.assert_frame_equal(
                inference_result.eval_dataset_df.sort_values(by="prompt").reset_index(
                    drop=True
                ),
                expected_df.sort_values(by="prompt").reset_index(drop=True),
            )
            mock_models.return_value.generate_content.assert_has_calls(
                [
                    mock.call(
                        model="gemini-pro",
                        contents="prompt 1",
                        config=genai_types.GenerateContentConfig(),
                    ),
                    mock.call(
                        model="gemini-pro",
                        contents="prompt 2",
                        config=genai_types.GenerateContentConfig(),
                    ),
                ],
                any_order=True,
            )
            assert inference_result.candidate_name == "gemini-pro"
            assert inference_result.gcs_source is None

    @pytest.mark.skip(reason="currently flakey")
    @mock.patch.object(_evals_common, "Models")
    def test_inference_from_local_csv_file(self, mock_models):
        with tempfile.TemporaryDirectory() as temp_dir:
            local_src_path = os.path.join(temp_dir, "input.csv")
            input_df = pd.DataFrame(
                {"prompt": ["prompt 1", "prompt 2"], "other_col": ["val 1", "val 2"]}
            )
            input_df.to_csv(local_src_path, index=False)

            mock_generate_content_responses = [
                genai_types.GenerateContentResponse(
                    candidates=[
                        genai_types.Candidate(
                            content=genai_types.Content(
                                parts=[genai_types.Part(text="resp 1")]
                            ),
                            finish_reason=genai_types.FinishReason.STOP,
                        )
                    ],
                    prompt_feedback=None,
                ),
                genai_types.GenerateContentResponse(
                    candidates=[
                        genai_types.Candidate(
                            content=genai_types.Content(
                                parts=[genai_types.Part(text="resp 2")]
                            ),
                            finish_reason=genai_types.FinishReason.STOP,
                        )
                    ],
                    prompt_feedback=None,
                ),
            ]
            mock_models.return_value.generate_content.side_effect = (
                mock_generate_content_responses
            )

            inference_result = self.client.evals.run_inference(
                model="gemini-pro", src=local_src_path
            )

            expected_df = pd.DataFrame(
                {
                    "prompt": ["prompt 1", "prompt 2"],
                    "other_col": ["val 1", "val 2"],
                    "response": ["resp 1", "resp 2"],
                }
            )
            pd.testing.assert_frame_equal(
                inference_result.eval_dataset_df.sort_values(by="prompt").reset_index(
                    drop=True
                ),
                expected_df.sort_values(by="prompt").reset_index(drop=True),
            )
            mock_models.return_value.generate_content.assert_has_calls(
                [
                    mock.call(
                        model="gemini-pro",
                        contents="prompt 1",
                        config=genai_types.GenerateContentConfig(),
                    ),
                    mock.call(
                        model="gemini-pro",
                        contents="prompt 2",
                        config=genai_types.GenerateContentConfig(),
                    ),
                ],
                any_order=True,
            )
            assert inference_result.candidate_name == "gemini-pro"
            assert inference_result.gcs_source is None

    @mock.patch.object(_evals_common, "Models")
    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    def test_inference_with_row_level_config_overrides(
        self, mock_eval_dataset_loader, mock_models
    ):
        mock_df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "request": [
                    {
                        "contents": [
                            {
                                "parts": [{"text": "Placeholder prompt 1"}],
                                "role": "user",
                            }
                        ]
                    },
                    {
                        "contents": [
                            {
                                "parts": [{"text": "Placeholder prompt 2.1"}],
                                "role": "user",
                            },
                            {
                                "parts": [{"text": "Placeholder model response 2.1"}],
                                "role": "model",
                            },
                            {
                                "parts": [{"text": "Placeholder prompt 2.2"}],
                                "role": "user",
                            },
                        ],
                        "generation_config": {"temperature": 0.7, "top_k": 5},
                    },
                    {
                        "contents": [
                            {
                                "parts": [{"text": "Placeholder prompt 3"}],
                                "role": "user",
                            }
                        ],
                    },
                ],
            }
        )
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )
        mock_generate_content_responses = [
            genai_types.GenerateContentResponse(
                candidates=[
                    genai_types.Candidate(
                        content=genai_types.Content(
                            parts=[genai_types.Part(text="Placeholder response 1")]
                        ),
                        finish_reason=genai_types.FinishReason.STOP,
                    )
                ],
                prompt_feedback=None,
            ),
            genai_types.GenerateContentResponse(
                candidates=[
                    genai_types.Candidate(
                        content=genai_types.Content(
                            parts=[genai_types.Part(text="Placeholder response 2")]
                        ),
                        finish_reason=genai_types.FinishReason.STOP,
                    )
                ],
                prompt_feedback=None,
            ),
            genai_types.GenerateContentResponse(
                candidates=[
                    genai_types.Candidate(
                        content=genai_types.Content(
                            parts=[genai_types.Part(text="Placeholder response 3")]
                        ),
                        finish_reason=genai_types.FinishReason.STOP,
                    )
                ],
                prompt_feedback=None,
            ),
        ]

        def mock_generate_content_logic(*args, **kwargs):
            contents = kwargs.get("contents")
            first_part_text = contents[0]["parts"][0]["text"]
            if "Placeholder prompt 1" in first_part_text:
                return mock_generate_content_responses[0]
            elif "Placeholder prompt 2.1" in first_part_text:
                return mock_generate_content_responses[1]
            elif "Placeholder prompt 3" in first_part_text:
                return mock_generate_content_responses[2]
            return genai_types.GenerateContentResponse()

        mock_models.return_value.generate_content.side_effect = (
            mock_generate_content_logic
        )

        inference_result = self.client.evals.run_inference(
            model="gemini-pro", src=mock_df
        )

        mock_models.return_value.generate_content.assert_has_calls(
            [
                mock.call(
                    model="gemini-pro",
                    contents=[
                        {
                            "parts": [{"text": "Placeholder prompt 1"}],
                            "role": "user",
                        }
                    ],
                    config=genai_types.GenerateContentConfig(),
                ),
                mock.call(
                    model="gemini-pro",
                    contents=[
                        {
                            "parts": [{"text": "Placeholder prompt 2.1"}],
                            "role": "user",
                        },
                        {
                            "parts": [{"text": "Placeholder model response 2.1"}],
                            "role": "model",
                        },
                        {
                            "parts": [{"text": "Placeholder prompt 2.2"}],
                            "role": "user",
                        },
                    ],
                    config=genai_types.GenerateContentConfig(temperature=0.7, top_k=5),
                ),
                mock.call(
                    model="gemini-pro",
                    contents=[
                        {
                            "parts": [{"text": "Placeholder prompt 3"}],
                            "role": "user",
                        }
                    ],
                    config=genai_types.GenerateContentConfig(),
                ),
            ],
            any_order=True,
        )

        request_obj_1 = {
            "contents": [{"parts": [{"text": "Placeholder prompt 1"}], "role": "user"}]
        }
        request_obj_2 = {
            "contents": [
                {"parts": [{"text": "Placeholder prompt 2.1"}], "role": "user"},
                {
                    "parts": [{"text": "Placeholder model response 2.1"}],
                    "role": "model",
                },
                {"parts": [{"text": "Placeholder prompt 2.2"}], "role": "user"},
            ],
            "generation_config": {"temperature": 0.7, "top_k": 5},
        }
        request_obj_3 = {
            "contents": [{"parts": [{"text": "Placeholder prompt 3"}], "role": "user"}],
        }
        expected_df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "request": [request_obj_1, request_obj_2, request_obj_3],
                "response": [
                    "Placeholder response 1",
                    "Placeholder response 2",
                    "Placeholder response 3",
                ],
            }
        )
        pd.testing.assert_frame_equal(
            inference_result.eval_dataset_df.sort_values(by="id").reset_index(
                drop=True
            ),
            expected_df.sort_values(by="id").reset_index(drop=True),
            check_dtype=False,
        )
        assert inference_result.candidate_name == "gemini-pro"
        assert inference_result.gcs_source is None

    @mock.patch.object(_evals_common, "Models")
    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    def test_inference_with_multimodal_content(
        self, mock_eval_dataset_loader, mock_models
    ):
        mock_media_content_json = genai_types.Content(
            parts=[
                genai_types.Part(
                    file_data=genai_types.FileData(
                        mime_type="image/png",
                        file_uri="gs://fake-bucket/image.png",
                    )
                )
            ]
        ).model_dump_json(exclude_none=True)
        mock_df = pd.DataFrame(
            {
                "text_input": ["hello world"],
                "media_content": [mock_media_content_json],
            }
        )
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )
        mock_generate_content_response = genai_types.GenerateContentResponse(
            candidates=[
                genai_types.Candidate(
                    content=genai_types.Content(
                        parts=[genai_types.Part(text="test response")]
                    ),
                    finish_reason=genai_types.FinishReason.STOP,
                )
            ],
            prompt_feedback=None,
        )
        mock_models.return_value.generate_content.return_value = (
            mock_generate_content_response
        )

        config = vertexai_genai_types.EvalRunInferenceConfig(
            prompt_template="multimodal prompt: {media_content}{text_input}"
        )
        inference_result = self.client.evals.run_inference(
            model="gemini-pro", src=mock_df, config=config
        )
        assembled_prompt_json = genai_types.Content(
            parts=[
                genai_types.Part(text="multimodal prompt: "),
                genai_types.Part(
                    file_data=genai_types.FileData(
                        mime_type="image/png",
                        file_uri="gs://fake-bucket/image.png",
                    )
                ),
                genai_types.Part(text="hello world"),
            ]
        ).model_dump_json(exclude_none=True)

        assert (
            mock_models.return_value.generate_content.call_args[1]["contents"]
            == assembled_prompt_json
        )

        pd.testing.assert_frame_equal(
            inference_result.eval_dataset_df,
            pd.DataFrame(
                {
                    "text_input": ["hello world"],
                    "media_content": [mock_media_content_json],
                    "request": [assembled_prompt_json],
                    "response": ["test response"],
                }
            ),
        )
        assert inference_result.candidate_name == "gemini-pro"
        assert inference_result.gcs_source is None

    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    @mock.patch("vertexai._genai._evals_common.vertexai.Client")
    def test_run_inference_with_agent_engine_and_session_inputs_dict(
        self,
        mock_vertexai_client,
        mock_eval_dataset_loader,
    ):
        mock_df = pd.DataFrame(
            {
                "prompt": ["agent prompt"],
                "session_inputs": [
                    {
                        "user_id": "123",
                        "state": {"a": "1"},
                    }
                ],
            }
        )
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )

        mock_agent_engine = mock.Mock()
        mock_agent_engine.create_session.return_value = {"id": "session1"}
        stream_query_return_value = [
            {
                "id": "1",
                "content": {"parts": [{"text": "intermediate1"}]},
                "timestamp": 123,
                "author": "model",
            },
            {
                "id": "2",
                "content": {"parts": [{"text": "agent response"}]},
                "timestamp": 124,
                "author": "model",
            },
        ]

        mock_agent_engine.stream_query.return_value = iter(stream_query_return_value)
        mock_vertexai_client.return_value.agent_engines.get.return_value = (
            mock_agent_engine
        )

        inference_result = self.client.evals.run_inference(
            agent="projects/test-project/locations/us-central1/reasoningEngines/123",
            src=mock_df,
        )

        mock_eval_dataset_loader.return_value.load.assert_called_once_with(mock_df)
        mock_vertexai_client.return_value.agent_engines.get.assert_called_once_with(
            name="projects/test-project/locations/us-central1/reasoningEngines/123"
        )
        mock_agent_engine.create_session.assert_called_once_with(
            user_id="123", state={"a": "1"}
        )
        mock_agent_engine.stream_query.assert_called_once_with(
            user_id="123", session_id="session1", message="agent prompt"
        )

        pd.testing.assert_frame_equal(
            inference_result.eval_dataset_df,
            pd.DataFrame(
                {
                    "prompt": ["agent prompt"],
                    "session_inputs": [
                        {
                            "user_id": "123",
                            "state": {"a": "1"},
                        }
                    ],
                    "intermediate_events": [
                        [
                            {
                                "event_id": "1",
                                "content": {"parts": [{"text": "intermediate1"}]},
                                "creation_timestamp": 123,
                                "author": "model",
                            }
                        ]
                    ],
                    "response": ["agent response"],
                    "agent_data": [
                        {
                            "agents": None,
                            "turns": [
                                {
                                    "events": [
                                        {
                                            "author": "model",
                                            "content": {
                                                "parts": [{"text": "intermediate1"}]
                                            },
                                        },
                                        {
                                            "author": "model",
                                            "content": {
                                                "parts": [{"text": "agent response"}]
                                            },
                                        },
                                    ],
                                    "turn_id": "turn_0",
                                    "turn_index": 0,
                                }
                            ],
                        }
                    ],
                }
            ),
        )
        assert inference_result.candidate_name == "agent_engine_0"
        assert inference_result.gcs_source is None

    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    @mock.patch("vertexai._genai._evals_common.vertexai.Client")
    def test_run_inference_with_agent_engine_and_session_inputs_literal_string(
        self,
        mock_vertexai_client,
        mock_eval_dataset_loader,
    ):
        session_inputs_str = '{"user_id": "123", "state": {"a": "1"}}'
        mock_df = pd.DataFrame(
            {
                "prompt": ["agent prompt"],
                "session_inputs": [session_inputs_str],
            }
        )
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )

        mock_agent_engine = mock.Mock()
        mock_agent_engine.create_session.return_value = {"id": "session1"}
        stream_query_return_value = [
            {
                "id": "1",
                "content": {"parts": [{"text": "intermediate1"}]},
                "timestamp": 123,
                "author": "model",
            },
            {
                "id": "2",
                "content": {"parts": [{"text": "agent response"}]},
                "timestamp": 124,
                "author": "model",
            },
        ]

        mock_agent_engine.stream_query.return_value = iter(stream_query_return_value)
        mock_vertexai_client.return_value.agent_engines.get.return_value = (
            mock_agent_engine
        )

        inference_result = self.client.evals.run_inference(
            agent="projects/test-project/locations/us-central1/reasoningEngines/123",
            src=mock_df,
        )

        mock_eval_dataset_loader.return_value.load.assert_called_once_with(mock_df)
        mock_vertexai_client.return_value.agent_engines.get.assert_called_once_with(
            name="projects/test-project/locations/us-central1/reasoningEngines/123"
        )
        mock_agent_engine.create_session.assert_called_once_with(
            user_id="123", state={"a": "1"}
        )
        mock_agent_engine.stream_query.assert_called_once_with(
            user_id="123", session_id="session1", message="agent prompt"
        )

        pd.testing.assert_frame_equal(
            inference_result.eval_dataset_df,
            pd.DataFrame(
                {
                    "prompt": ["agent prompt"],
                    "session_inputs": [session_inputs_str],
                    "intermediate_events": [
                        [
                            {
                                "event_id": "1",
                                "content": {"parts": [{"text": "intermediate1"}]},
                                "creation_timestamp": 123,
                                "author": "model",
                            }
                        ]
                    ],
                    "response": ["agent response"],
                    "agent_data": [
                        {
                            "agents": None,
                            "turns": [
                                {
                                    "events": [
                                        {
                                            "author": "model",
                                            "content": {
                                                "parts": [{"text": "intermediate1"}]
                                            },
                                        },
                                        {
                                            "author": "model",
                                            "content": {
                                                "parts": [{"text": "agent response"}]
                                            },
                                        },
                                    ],
                                    "turn_id": "turn_0",
                                    "turn_index": 0,
                                }
                            ],
                        }
                    ],
                }
            ),
        )
        assert inference_result.candidate_name == "agent_engine_0"
        assert inference_result.gcs_source is None

    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    @mock.patch("vertexai._genai._evals_common.vertexai.Client")
    def test_run_inference_with_agent_engine_with_response_column_raises_error(
        self,
        mock_vertexai_client,
        mock_eval_dataset_loader,
    ):
        mock_df = pd.DataFrame(
            {
                "prompt": ["agent prompt"],
                "session_inputs": [
                    {
                        "user_id": "123",
                        "state": {"a": "1"},
                    }
                ],
                "response": ["some response"],
            }
        )
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )

        mock_agent_engine = mock.Mock()
        mock_vertexai_client.return_value.agent_engines.get.return_value = (
            mock_agent_engine
        )

        with pytest.raises(ValueError) as excinfo:
            self.client.evals.run_inference(
                agent="projects/test-project/locations/us-central1/reasoningEngines/123",
                src=mock_df,
            )
        assert (
            "The eval dataset provided for agent run should not contain "
            "'intermediate_events' or 'response' columns"
        ) in str(excinfo.value)

    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    @mock.patch("vertexai._genai._evals_common.vertexai.Client")
    def test_run_inference_with_agent_engine_falls_back_to_managed_sessions_api(
        self,
        mock_vertexai_client,
        mock_eval_dataset_loader,
    ):
        """Tests that run_inference falls back to the managed Sessions API
        when the agent engine does not have create_session registered."""
        mock_df = pd.DataFrame(
            {
                "prompt": ["agent prompt"],
                "session_inputs": [
                    {
                        "user_id": "123",
                        "state": {"a": "1"},
                    }
                ],
            }
        )
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )

        # Create a mock agent engine WITHOUT create_session (simulates agents
        # deployed via Console, gcloud, or source code deployment).
        mock_agent_engine = mock.Mock(
            spec=["api_client", "api_resource", "stream_query"],
        )
        mock_agent_engine.api_resource.name = (
            "projects/test-project/locations/us-central1/reasoningEngines/123"
        )

        # Mock the managed Sessions API to return a session.
        mock_session_operation = mock.Mock()
        mock_session_operation.response.name = (
            "projects/test-project/locations/us-central1"
            "/reasoningEngines/123/sessions/managed-session-1"
        )
        mock_agent_engine.api_client.sessions.create.return_value = (
            mock_session_operation
        )

        stream_query_return_value = [
            {
                "id": "1",
                "content": {"parts": [{"text": "intermediate1"}]},
                "timestamp": 123,
                "author": "model",
            },
            {
                "id": "2",
                "content": {"parts": [{"text": "agent response"}]},
                "timestamp": 124,
                "author": "model",
            },
        ]
        mock_agent_engine.stream_query.return_value = iter(stream_query_return_value)
        mock_vertexai_client.return_value.agent_engines.get.return_value = (
            mock_agent_engine
        )

        inference_result = self.client.evals.run_inference(
            agent="projects/test-project/locations/us-central1/reasoningEngines/123",
            src=mock_df,
        )

        # Verify the managed Sessions API was called as fallback.
        mock_agent_engine.api_client.sessions.create.assert_called_once_with(
            name="projects/test-project/locations/us-central1/reasoningEngines/123",
            user_id="123",
            config=vertexai_genai_types.CreateAgentEngineSessionConfig(
                session_state={"a": "1"},
            ),
        )

        # Verify stream_query was called with the session ID extracted from
        # the managed session's resource name.
        mock_agent_engine.stream_query.assert_called_once_with(
            user_id="123",
            session_id="managed-session-1",
            message="agent prompt",
        )

        # Verify the inference results are correct.
        assert inference_result.eval_dataset_df["response"].iloc[0] == "agent response"
        assert inference_result.candidate_name == "agent_engine_0"

    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    @mock.patch("vertexai._genai._evals_common.InMemorySessionService")  # fmt: skip
    @mock.patch("vertexai._genai._evals_common.Runner")
    @mock.patch("vertexai._genai._evals_common.LlmAgent")
    def test_run_inference_with_local_agent(
        self,
        mock_llm_agent,
        mock_runner,
        mock_session_service,
        mock_eval_dataset_loader,
    ):
        mock_df = pd.DataFrame(
            {
                "prompt": ["agent prompt", "agent prompt 2"],
                "session_inputs": [
                    {
                        "user_id": "123",
                        "state": {"a": "1"},
                    },
                    {
                        "user_id": "456",
                        "state": {"b": "2"},
                    },
                ],
            }
        )
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )

        mock_agent_instance = mock.Mock()
        mock_agent_instance.name = "mock_agent"
        mock_agent_instance.description = "mock description"
        mock_agent_instance.instruction = "mock instruction"
        mock_agent_instance.tools = []
        mock_agent_instance.sub_agents = []
        mock_llm_agent.return_value = mock_agent_instance
        mock_session_service.return_value.create_session = mock.AsyncMock()
        mock_runner_instance = mock_runner.return_value
        stream_run_return_value_1 = [
            mock.Mock(
                model_dump=lambda **kwargs: {
                    "id": "1",
                    "content": {"parts": [{"text": "intermediate1"}]},
                    "timestamp": 123,
                    "author": "model",
                }
            ),
            mock.Mock(
                model_dump=lambda **kwargs: {
                    "id": "2",
                    "content": {"parts": [{"text": "agent response"}]},
                    "timestamp": 124,
                    "author": "model",
                }
            ),
        ]
        stream_run_return_value_2 = [
            mock.Mock(
                model_dump=lambda **kwargs: {
                    "id": "3",
                    "content": {"parts": [{"text": "intermediate2"}]},
                    "timestamp": 125,
                    "author": "model",
                }
            ),
            mock.Mock(
                model_dump=lambda **kwargs: {
                    "id": "4",
                    "content": {"parts": [{"text": "agent response 2"}]},
                    "timestamp": 126,
                    "author": "model",
                }
            ),
        ]

        async def async_iterator(items):
            for item in items:
                yield item

        def run_async_side_effect(*args, **kwargs):
            new_message = kwargs.get("new_message")
            if new_message and new_message.parts[0].text == "agent prompt":
                return async_iterator(stream_run_return_value_1)
            return async_iterator(stream_run_return_value_2)

        mock_runner_instance.run_async.side_effect = run_async_side_effect

        inference_result = self.client.evals.run_inference(
            agent=mock_agent_instance,
            src=mock_df,
        )

        mock_eval_dataset_loader.return_value.load.assert_called_once_with(mock_df)
        assert mock_session_service.call_count == 2
        mock_runner.assert_called_with(
            agent=mock_agent_instance,
            app_name="local agent run",
            session_service=mock_session_service.return_value,
        )
        assert mock_runner.call_count == 2
        assert mock_runner_instance.run_async.call_count == 2

        expected_df = pd.DataFrame(
            {
                "prompt": ["agent prompt", "agent prompt 2"],
                "session_inputs": [
                    {
                        "user_id": "123",
                        "state": {"a": "1"},
                    },
                    {
                        "user_id": "456",
                        "state": {"b": "2"},
                    },
                ],
                "intermediate_events": [
                    [
                        {
                            "event_id": "1",
                            "content": {"parts": [{"text": "intermediate1"}]},
                            "creation_timestamp": 123,
                            "author": "model",
                        }
                    ],
                    [
                        {
                            "event_id": "3",
                            "content": {"parts": [{"text": "intermediate2"}]},
                            "creation_timestamp": 125,
                            "author": "model",
                        }
                    ],
                ],
                "response": ["agent response", "agent response 2"],
                "agent_data": [
                    {
                        "agents": {
                            "mock_agent": {
                                "agent_id": "mock_agent",
                                "agent_type": "Mock",
                                "instruction": "mock instruction",
                                "description": "mock description",
                                "tools": [],
                                "sub_agents": [],
                            }
                        },
                        "turns": [
                            {
                                "events": [
                                    {
                                        "author": "model",
                                        "content": {
                                            "parts": [{"text": "intermediate1"}]
                                        },
                                    },
                                    {
                                        "author": "model",
                                        "content": {
                                            "parts": [{"text": "agent response"}]
                                        },
                                    },
                                ],
                                "turn_id": "turn_0",
                                "turn_index": 0,
                            }
                        ],
                    },
                    {
                        "agents": {
                            "mock_agent": {
                                "agent_id": "mock_agent",
                                "agent_type": "Mock",
                                "instruction": "mock instruction",
                                "description": "mock description",
                                "tools": [],
                                "sub_agents": [],
                            }
                        },
                        "turns": [
                            {
                                "events": [
                                    {
                                        "author": "model",
                                        "content": {
                                            "parts": [{"text": "intermediate2"}]
                                        },
                                    },
                                    {
                                        "author": "model",
                                        "content": {
                                            "parts": [{"text": "agent response 2"}]
                                        },
                                    },
                                ],
                                "turn_id": "turn_0",
                                "turn_index": 0,
                            }
                        ],
                    },
                ],
            }
        )
        pd.testing.assert_frame_equal(
            inference_result.eval_dataset_df.sort_values(by="prompt").reset_index(
                drop=True
            ),
            expected_df.sort_values(by="prompt").reset_index(drop=True),
        )
        assert inference_result.candidate_name == "mock_agent"
        assert inference_result.gcs_source is None

    def test_run_inference_with_litellm_string_prompt_format(
        self,
        mock_api_client_fixture,
    ):
        """Tests inference with LiteLLM using a simple prompt string."""
        with mock.patch(
            "vertexai._genai._evals_common.litellm"
        ) as mock_litellm, mock.patch(
            "vertexai._genai._evals_common._call_litellm_completion"
        ) as mock_call_litellm_completion:
            mock_litellm.utils.get_valid_models.return_value = ["gpt-4o"]
            prompt_df = pd.DataFrame([{"prompt": "What is LiteLLM?"}])
            expected_messages = [{"role": "user", "content": "What is LiteLLM?"}]

            mock_response_dict = {
                "id": "test",
                "created": 123456,
                "model": "gpt-4o",
                "object": "chat.completion",
                "system_fingerprint": "123456",
                "choices": [
                    {
                        "finish_reason": "stop",
                        "index": 0,
                        "message": {
                            "content": "LiteLLM is a library...",
                            "role": "assistant",
                            "annotations": [],
                        },
                        "provider_specific_fields": {},
                    }
                ],
                "usage": {
                    "completion_tokens": 114,
                    "prompt_tokens": 13,
                    "total_tokens": 127,
                },
                "service_tier": "default",
            }
            mock_call_litellm_completion.return_value = mock_response_dict
            evals_module = evals.Evals(api_client_=mock_api_client_fixture)

            result_dataset = evals_module.run_inference(
                model="gpt-4o",
                src=prompt_df,
            )

            mock_call_litellm_completion.assert_called_once()
            _, call_kwargs = mock_call_litellm_completion.call_args

            assert call_kwargs["model"] == "gpt-4o"
            assert call_kwargs["messages"] == expected_messages
            assert "response" in result_dataset.eval_dataset_df.columns
            response_content = result_dataset.eval_dataset_df["response"][0]
            assert response_content == "LiteLLM is a library..."

    def test_run_inference_with_litellm_openai_request_format(
        self,
        mock_api_client_fixture,
    ):
        """Tests inference with LiteLLM where the row contains a chat completion request body."""
        with mock.patch(
            "vertexai._genai._evals_common.litellm"
        ) as mock_litellm, mock.patch(
            "vertexai._genai._evals_common._call_litellm_completion"
        ) as mock_call_litellm_completion:
            mock_litellm.utils.get_valid_models.return_value = ["gpt-4o"]
            prompt_df = pd.DataFrame(
                [
                    {
                        "model": "gpt-4o",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a helpful assistant.",
                            },
                            {"role": "user", "content": "Hello!"},
                        ],
                    }
                ]
            )
            expected_messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
            ]

            mock_response_dict = {
                "id": "test",
                "created": 123456,
                "model": "gpt-4o",
                "object": "chat.completion",
                "system_fingerprint": "123456",
                "choices": [
                    {
                        "finish_reason": "stop",
                        "index": 0,
                        "message": {
                            "content": "Hello there",
                            "role": "assistant",
                            "annotations": [],
                        },
                        "provider_specific_fields": {},
                    }
                ],
                "usage": {
                    "completion_tokens": 114,
                    "prompt_tokens": 13,
                    "total_tokens": 127,
                },
                "service_tier": "default",
            }
            mock_call_litellm_completion.return_value = mock_response_dict
            evals_module = evals.Evals(api_client_=mock_api_client_fixture)

            result_dataset = evals_module.run_inference(
                model="gpt-4o",
                src=prompt_df,
            )

            mock_call_litellm_completion.assert_called_once()
            _, call_kwargs = mock_call_litellm_completion.call_args

            assert call_kwargs["model"] == "gpt-4o"
            assert call_kwargs["messages"] == expected_messages
            assert "response" in result_dataset.eval_dataset_df.columns
            response_content = result_dataset.eval_dataset_df["response"][0]
            assert response_content == "Hello there"

    def test_run_inference_with_unsupported_model_string(
        self,
        mock_api_client_fixture,
    ):
        with mock.patch(
            "vertexai._genai._evals_common.litellm"
        ) as mock_litellm_package:
            mock_litellm_package.utils.get_valid_models.return_value = []
            evals_module = evals.Evals(api_client_=mock_api_client_fixture)
            prompt_df = pd.DataFrame([{"prompt": "test"}])

            with pytest.raises(TypeError, match="Unsupported string model name"):
                evals_module.run_inference(
                    model="some-random-model/name", src=prompt_df
                )

    @mock.patch("vertexai._genai._evals_common.litellm", None)
    def test_run_inference_with_litellm_import_error(self, mock_api_client_fixture):
        evals_module = evals.Evals(api_client_=mock_api_client_fixture)
        prompt_df = pd.DataFrame([{"prompt": "test"}])
        with pytest.raises(
            ImportError,
            match="The 'litellm' library is required to use this model.",
        ):
            evals_module.run_inference(model="gpt-4o", src=prompt_df)

    @mock.patch.object(_evals_common, "_run_litellm_inference")
    @mock.patch.object(_evals_common, "_is_gemini_model")
    @mock.patch.object(_evals_common, "_is_litellm_model")
    @mock.patch.object(_evals_common, "_is_litellm_vertex_maas_model")
    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    def test_run_inference_with_litellm_parsing(
        self,
        mock_eval_dataset_loader,
        mock_is_litellm_vertex_maas_model,
        mock_is_litellm_model,
        mock_is_gemini_model,
        mock_run_litellm_inference,
    ):
        """Tests the parsing logic for LiteLLM responses within _run_inference_internal."""
        mock_is_gemini_model.return_value = False
        mock_is_litellm_model.return_value = True
        mock_is_litellm_vertex_maas_model.return_value = False

        mock_df = pd.DataFrame(
            {
                "prompt": [
                    "prompt1",
                    "prompt2",
                    "prompt3",
                    "prompt4",
                    "prompt5",
                    "prompt6",
                ]
            }
        )
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )

        raw_responses = [
            {  # Successful response
                "choices": [{"message": {"content": "LiteLLM response 1"}}]
            },
            {"error": "LiteLLM call failed: API key error"},  # Response with error key
            {"id": "test-id-3"},  # Missing choices
            {"choices": [{"index": 0}]},  # Missing message
            {"choices": [{"message": {"role": "assistant"}}]},  # Missing content
            "Invalid JSON string",  # Non-dict response
        ]
        mock_run_litellm_inference.return_value = raw_responses
        # fmt: off
        with mock.patch("vertexai._genai._evals_common.litellm") as mock_litellm:
            # fmt: on
            mock_litellm.utils.get_valid_models.return_value = ["gpt-4o"]
            inference_result = self.client.evals.run_inference(
                model="gpt-4o",
                src=mock_df,
            )

        expected_responses = [
            "LiteLLM response 1",
            json.dumps({"error": "LiteLLM call failed: API key error"}),
            json.dumps(
                {
                    "error": "LiteLLM response missing 'choices'",
                    "details": {"id": "test-id-3"},
                }
            ),
            json.dumps(
                {
                    "error": "LiteLLM response missing 'message' in first choice",
                    "details": {"choices": [{"index": 0}]},
                }
            ),
            json.dumps(
                {
                    "error": "LiteLLM response missing 'content' in message",
                    "details": {"choices": [{"message": {"role": "assistant"}}]},
                }
            ),
            json.dumps(
                {
                    "error": "Invalid LiteLLM response format",
                    "details": "Invalid JSON string",
                }
            ),
        ]

        expected_df = pd.DataFrame(
            {
                "prompt": [
                    "prompt1",
                    "prompt2",
                    "prompt3",
                    "prompt4",
                    "prompt5",
                    "prompt6",
                ],
                "response": expected_responses,
            }
        )

        pd.testing.assert_frame_equal(
            inference_result.eval_dataset_df.reset_index(drop=True),
            expected_df.reset_index(drop=True),
            check_dtype=False,
        )
        mock_run_litellm_inference.assert_called_once()
        _, call_kwargs = mock_run_litellm_inference.call_args
        assert call_kwargs["model"] == "gpt-4o"
        pd.testing.assert_frame_equal(call_kwargs["prompt_dataset"], mock_df)


@pytest.mark.usefixtures("google_auth_mock")
class TestEvalsMetricHandlers:
    """Unit tests for utility functions in _evals_metric_handlers."""

    def test_has_tool_call_with_tool_call(self):
        events = [
            vertexai_genai_types.evals.Event(
                event_id="1",
                content=genai_types.Content(
                    parts=[
                        genai_types.Part(
                            function_call=genai_types.FunctionCall(
                                name="search", args={}
                            )
                        )
                    ]
                ),
            )
        ]
        assert _evals_metric_handlers._has_tool_call(events)

    def test_has_tool_call_no_tool_call(self):
        events = [
            vertexai_genai_types.evals.Event(
                event_id="1",
                content=genai_types.Content(parts=[genai_types.Part(text="hello")]),
            )
        ]
        assert not _evals_metric_handlers._has_tool_call(events)

    def test_has_tool_call_empty_events(self):
        assert not _evals_metric_handlers._has_tool_call([])

    def test_has_tool_call_none_events(self):
        assert not _evals_metric_handlers._has_tool_call(None)

    def test_has_tool_call_mixed_events(self):
        events = [
            vertexai_genai_types.evals.Event(
                event_id="1",
                content=genai_types.Content(parts=[genai_types.Part(text="hello")]),
            ),
            vertexai_genai_types.evals.Event(
                event_id="2",
                content=genai_types.Content(
                    parts=[
                        genai_types.Part(
                            function_call=genai_types.FunctionCall(
                                name="search", args={}
                            )
                        )
                    ]
                ),
            ),
        ]
        assert _evals_metric_handlers._has_tool_call(events)

    def test_has_tool_call_with_agent_event(self):
        events = [
            vertexai_genai_types.evals.AgentEvent(
                author="model",
                content=genai_types.Content(
                    parts=[
                        genai_types.Part(
                            function_call=genai_types.FunctionCall(
                                name="search", args={}
                            )
                        )
                    ]
                ),
            )
        ]
        assert _evals_metric_handlers._has_tool_call(events)


@pytest.mark.usefixtures("google_auth_mock")
class TestRunAgent:
    """Unit tests for the _run_agent function."""

    @mock.patch.object(_evals_common, "_execute_inference_concurrently")
    def test_run_agent_rewrites_gemini_3_model_name(
        self, mock_execute_inference_concurrently, mock_api_client_fixture
    ):
        mock_execute_inference_concurrently.return_value = []
        user_simulator_config = vertexai_genai_types.evals.UserSimulatorConfig(
            model_name="gemini-3-preview"
        )
        prompt_dataset = pd.DataFrame({"prompt": ["prompt1"]})
        with mock.patch.dict(os.environ, clear=True):
            os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

            def mock_execute(*args, **kwargs):
                assert os.environ["GOOGLE_CLOUD_LOCATION"] == "global"
                return []

            mock_execute_inference_concurrently.side_effect = mock_execute

            _evals_common._run_agent(
                api_client=mock_api_client_fixture,
                agent_engine=mock.Mock(),
                agent=None,
                prompt_dataset=prompt_dataset,
                user_simulator_config=user_simulator_config,
                allow_cross_region_model=True,
            )

            assert (
                user_simulator_config.model_name
                == f"projects/{mock_api_client_fixture.project}/locations/global/publishers/google/models/gemini-3-preview"
            )
            assert os.environ.get("GOOGLE_CLOUD_LOCATION") == "us-central1"

    @mock.patch.object(_evals_common, "_execute_inference_concurrently")
    def test_run_agent_raises_error_if_gemini_3_and_allow_cross_region_model_false(
        self, mock_execute_inference_concurrently, mock_api_client_fixture
    ):
        user_simulator_config = vertexai_genai_types.evals.UserSimulatorConfig(
            model_name="gemini-3-preview"
        )
        prompt_dataset = pd.DataFrame({"prompt": ["prompt1"]})
        with mock.patch.dict(os.environ, clear=True):
            os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

            with pytest.raises(
                ValueError,
                match="The model 'gemini-3-preview' is currently only available in the 'global' region.",
            ):
                _evals_common._run_agent(
                    api_client=mock_api_client_fixture,
                    agent_engine=mock.Mock(),
                    agent=None,
                    prompt_dataset=prompt_dataset,
                    user_simulator_config=user_simulator_config,
                    allow_cross_region_model=False,
                )

    @mock.patch.object(_evals_common, "_execute_inference_concurrently")
    def test_run_agent_rewrites_gemini_3_model_name_empty_env(
        self, mock_execute_inference_concurrently, mock_api_client_fixture
    ):
        mock_execute_inference_concurrently.return_value = []
        user_simulator_config = vertexai_genai_types.evals.UserSimulatorConfig(
            model_name="gemini-3-preview"
        )
        prompt_dataset = pd.DataFrame({"prompt": ["prompt1"]})
        with mock.patch.dict(os.environ, clear=True):

            def mock_execute(*args, **kwargs):
                assert os.environ["GOOGLE_CLOUD_LOCATION"] == "global"
                return []

            mock_execute_inference_concurrently.side_effect = mock_execute

            _evals_common._run_agent(
                api_client=mock_api_client_fixture,
                agent_engine=mock.Mock(),
                agent=None,
                prompt_dataset=prompt_dataset,
                user_simulator_config=user_simulator_config,
                allow_cross_region_model=True,
            )

            assert (
                user_simulator_config.model_name
                == f"projects/{mock_api_client_fixture.project}/locations/global/publishers/google/models/gemini-3-preview"
            )
            assert "GOOGLE_CLOUD_LOCATION" not in os.environ


class TestRunAgentInternal:
    """Unit tests for the _run_agent_internal function."""

    def setup_method(self):
        importlib.reload(vertexai_genai_types)
        importlib.reload(_evals_common)

    @mock.patch.object(_evals_common, "_run_agent")
    def test_run_agent_internal_success(self, mock_run_agent):
        mock_run_agent.return_value = [
            [
                {
                    "id": "1",
                    "content": {"parts": [{"text": "intermediate1"}]},
                    "timestamp": 123,
                    "author": "model",
                },
                {
                    "id": "2",
                    "content": {"parts": [{"text": "final response"}]},
                    "timestamp": 124,
                    "author": "model",
                },
            ]
        ]
        prompt_dataset = pd.DataFrame({"prompt": ["prompt1"]})
        mock_agent_engine = mock.Mock()
        mock_api_client = mock.Mock()
        result_df = _evals_common._run_agent_internal(
            api_client=mock_api_client,
            agent_engine=mock_agent_engine,
            agent=None,
            prompt_dataset=prompt_dataset,
        )

        expected_df = pd.DataFrame(
            {
                "prompt": ["prompt1"],
                "intermediate_events": [
                    [
                        {
                            "event_id": "1",
                            "content": {"parts": [{"text": "intermediate1"}]},
                            "creation_timestamp": 123,
                            "author": "model",
                        }
                    ]
                ],
                "response": ["final response"],
                "agent_data": [
                    {
                        "agents": None,
                        "turns": [
                            {
                                "events": [
                                    {
                                        "author": "model",
                                        "content": {
                                            "parts": [{"text": "intermediate1"}]
                                        },
                                    },
                                    {
                                        "author": "model",
                                        "content": {
                                            "parts": [{"text": "final response"}]
                                        },
                                    },
                                ],
                                "turn_id": "turn_0",
                                "turn_index": 0,
                            }
                        ],
                    }
                ],
            }
        )
        pd.testing.assert_frame_equal(result_df, expected_df)

    @mock.patch.object(_evals_common, "_run_agent")
    def test_run_agent_internal_error_response(self, mock_run_agent):
        mock_run_agent.return_value = [{"error": "agent run failed"}]
        prompt_dataset = pd.DataFrame({"prompt": ["prompt1"]})
        mock_agent_engine = mock.Mock()
        mock_api_client = mock.Mock()
        result_df = _evals_common._run_agent_internal(
            api_client=mock_api_client,
            agent_engine=mock_agent_engine,
            agent=None,
            prompt_dataset=prompt_dataset,
        )

        assert "response" in result_df.columns
        response_content = result_df["response"][0]
        assert "agent run failed" in response_content
        assert not result_df["intermediate_events"][0]

    @mock.patch.object(_evals_common, "_run_agent")
    def test_run_agent_internal_multi_turn_success(self, mock_run_agent):
        mock_run_agent.return_value = [
            [
                {"turn_index": 0, "turn_id": "t1", "events": []},
                {"turn_index": 1, "turn_id": "t2", "events": []},
            ]
        ]
        prompt_dataset = pd.DataFrame({"prompt": ["p1"], "conversation_plan": ["plan"]})
        mock_agent_engine = mock.Mock()
        mock_api_client = mock.Mock()
        result_df = _evals_common._run_agent_internal(
            api_client=mock_api_client,
            agent_engine=mock_agent_engine,
            agent=None,
            prompt_dataset=prompt_dataset,
        )

        assert "agent_data" in result_df.columns
        agent_data = result_df["agent_data"][0]
        assert agent_data["turns"] == [
            {"turn_index": 0, "turn_id": "t1", "events": []},
            {"turn_index": 1, "turn_id": "t2", "events": []},
        ]

    @mock.patch.object(_evals_common, "_run_agent")
    def test_run_agent_internal_multi_turn_with_agent(self, mock_run_agent):
        mock_run_agent.return_value = [
            [
                {"turn_index": 0, "turn_id": "t1", "events": []},
            ]
        ]
        prompt_dataset = pd.DataFrame({"prompt": ["p1"], "conversation_plan": ["plan"]})
        mock_agent = mock.Mock()
        mock_agent.name = "mock_agent"
        mock_agent.description = "mock description"
        mock_agent.instruction = "mock instruction"
        mock_agent.tools = []
        mock_agent.sub_agents = []
        mock_api_client = mock.Mock()
        result_df = _evals_common._run_agent_internal(
            api_client=mock_api_client,
            agent_engine=None,
            agent=mock_agent,
            prompt_dataset=prompt_dataset,
        )

        assert "agent_data" in result_df.columns
        agent_data = result_df["agent_data"][0]
        assert agent_data["turns"] == [
            {"turn_index": 0, "turn_id": "t1", "events": []},
        ]
        assert "mock_agent" in agent_data["agents"]

    @mock.patch("vertexai._genai._evals_common.ADK_SessionInput")  # fmt: skip
    @mock.patch("vertexai._genai._evals_common.EvaluationGenerator")  # fmt: skip
    @mock.patch("vertexai._genai._evals_common.LlmBackedUserSimulator")  # fmt: skip
    @mock.patch("vertexai._genai._evals_common.ConversationScenario")  # fmt: skip
    @mock.patch("vertexai._genai._evals_common.LlmBackedUserSimulatorConfig")  # fmt: skip
    @pytest.mark.asyncio
    async def test_run_adk_user_simulation_with_intermediate_events(
        self,
        mock_config,
        mock_scenario,
        mock_simulator,
        mock_generator,
        mock_session_input,
    ):
        """Tests that intermediate invocation events (e.g. tool calls) are parsed successfully."""
        row = pd.Series(
            {
                "starting_prompt": "I want a laptop.",
                "conversation_plan": "Ask for a laptop",
                "session_inputs": json.dumps({"user_id": "u1"}),
            }
        )
        mock_agent = mock.Mock()

        mock_invocation = mock.Mock()
        mock_invocation.invocation_id = "turn_123"
        mock_invocation.creation_timestamp = 1771811084.88
        mock_invocation.user_content.model_dump.return_value = {
            "parts": [{"text": "I want a laptop."}],
            "role": "user",
        }
        mock_event_1 = mock.Mock()
        mock_event_1.author = "ecommerce_agent"
        mock_event_1.content.model_dump.return_value = {
            "parts": [
                {
                    "function_call": {
                        "name": "search_products",
                        "args": {"query": "laptop"},
                    }
                }
            ]
        }
        mock_event_2 = mock.Mock()
        mock_event_2.author = "ecommerce_agent"
        mock_event_2.content.model_dump.return_value = {
            "parts": [
                {
                    "function_response": {
                        "name": "search_products",
                        "response": {"products": []},
                    }
                }
            ]
        }

        mock_invocation.intermediate_data.invocation_events = [
            mock_event_1,
            mock_event_2,
        ]
        mock_invocation.final_response.model_dump.return_value = {
            "parts": [{"text": "There are no laptops matching your search."}],
            "role": "model",
        }
        mock_generator._generate_inferences_from_root_agent = mock.AsyncMock(
            return_value=[mock_invocation]
        )
        turns = await _evals_common._run_adk_user_simulation(row, mock_agent)

        assert len(turns) == 1
        turn = turns[0]
        assert turn["turn_index"] == 0
        assert turn["turn_id"] == "turn_123"
        assert len(turn["events"]) == 4
        assert turn["events"][0]["author"] == "user"
        assert turn["events"][0]["content"]["parts"][0]["text"] == "I want a laptop."
        assert turn["events"][1]["author"] == "ecommerce_agent"
        assert "function_call" in turn["events"][1]["content"]["parts"][0]
        assert turn["events"][2]["author"] == "ecommerce_agent"
        assert "function_response" in turn["events"][2]["content"]["parts"][0]
        assert turn["events"][3]["author"] == "agent"
        assert (
            turn["events"][3]["content"]["parts"][0]["text"]
            == "There are no laptops matching your search."
        )
        mock_invocation.user_content.model_dump.assert_called_with(
            mode="json", exclude_none=True
        )
        mock_event_1.content.model_dump.assert_called_with(
            mode="json", exclude_none=True
        )
        mock_invocation.final_response.model_dump.assert_called_with(
            mode="json", exclude_none=True
        )

    @mock.patch.object(_evals_common, "_run_agent")
    def test_run_agent_internal_malformed_event(self, mock_run_agent):
        mock_run_agent.return_value = [
            [
                {
                    "id": "1",
                    "content": {"parts1": [{"text123": "final response"}]},
                    "timestamp": 124,
                    "author": "model",
                },
            ]
        ]
        prompt_dataset = pd.DataFrame({"prompt": ["prompt1"]})
        mock_agent_engine = mock.Mock()
        mock_api_client = mock.Mock()
        result_df = _evals_common._run_agent_internal(
            api_client=mock_api_client,
            agent_engine=mock_agent_engine,
            agent=None,
            prompt_dataset=prompt_dataset,
        )
        assert "response" in result_df.columns
        response_content = result_df["response"][0]
        assert "Failed to parse agent run response" in response_content
        assert not result_df["intermediate_events"][0]


class TestIsMultiTurnAgentSimulation:
    """Unit tests for the _is_multi_turn_agent_simulation function."""

    def test_is_multi_turn_agent_simulation_with_config(self):
        config = vertexai_genai_types.evals.UserSimulatorConfig(model_name="gemini-pro")
        assert _evals_common._is_multi_turn_agent_simulation(
            user_simulator_config=config, prompt_dataset=pd.DataFrame()
        )

    def test_is_multi_turn_agent_simulation_with_conversation_plan(self):
        prompt_dataset = pd.DataFrame({"conversation_plan": ["plan"]})
        assert _evals_common._is_multi_turn_agent_simulation(
            user_simulator_config=None, prompt_dataset=prompt_dataset
        )

    def test_is_multi_turn_agent_simulation_false(self):
        prompt_dataset = pd.DataFrame({"prompt": ["prompt"]})
        assert not _evals_common._is_multi_turn_agent_simulation(
            user_simulator_config=None, prompt_dataset=prompt_dataset
        )


class TestMetricPromptBuilder:
    """Unit tests for the MetricPromptBuilder class."""

    def test_metric_prompt_builder_minimal_fields(self):
        criteria = {"criterion1": "definition1"}
        rating_scores = {"score1": "description1"}
        builder = vertexai_genai_types.MetricPromptBuilder(
            criteria=criteria,
            rating_scores=rating_scores,
            metric_definition=None,
            few_shot_examples=None,
        )
        assert builder.criteria == criteria
        assert builder.rating_scores == rating_scores
        expected_instruction = (
            "You are an expert evaluator. Your task is to evaluate the quality"
            " of the responses generated by AI models. We will provide you with"
            " the user prompt and an AI-generated responses.\nYou should first"
            " read the user input carefully for analyzing the task, and then"
            " evaluate the quality of the responses based on the Criteria"
            " provided in the Evaluation section below.\nYou will assign the"
            " response a rating following the Rating Scores and Evaluation"
            " Steps. Give step by step explanations for your rating, and only"
            " choose ratings from the Rating Scores."
        )
        expected_evaluation_steps = {
            "Step 1": (
                "Assess the response in aspects of all criteria provided. Provide"
                " assessment according to each criterion."
            ),
            "Step 2": (
                "Score based on the Rating Scores. Give a brief rationale to"
                " explain your evaluation considering each individual criterion."
            ),
        }
        assert builder.instruction == expected_instruction
        assert builder.evaluation_steps == expected_evaluation_steps
        assert "{response}" in builder.text

    def test_metric_prompt_builder_all_fields(self):
        criteria = {"criterion1": "definition1"}
        rating_scores = {"score1": "description1"}
        instruction = "Custom instruction."
        metric_definition = "Custom metric definition."
        evaluation_steps = {"step1": "custom step 1"}
        few_shot_examples = ["example1", "example2"]
        builder = vertexai_genai_types.MetricPromptBuilder(
            criteria=criteria,
            rating_scores=rating_scores,
            instruction=instruction,
            metric_definition=metric_definition,
            evaluation_steps=evaluation_steps,
            few_shot_examples=few_shot_examples,
        )
        assert builder.criteria == criteria
        assert builder.rating_scores == rating_scores
        assert builder.instruction == instruction
        assert builder.metric_definition == metric_definition
        assert builder.evaluation_steps == evaluation_steps
        assert builder.few_shot_examples == few_shot_examples
        assert instruction in builder.text
        assert metric_definition in builder.text
        assert "custom step 1" in builder.text
        assert "example1" in builder.text

    def test_metric_prompt_builder_default_instruction_and_steps_in_text(self):
        criteria = {"c1": "v1"}
        rating_scores = {"s1": "d1"}
        builder = vertexai_genai_types.MetricPromptBuilder(
            criteria=criteria,
            rating_scores=rating_scores,
            metric_definition=None,
            few_shot_examples=None,
        )
        expected_instruction = (
            "You are an expert evaluator. Your task is to evaluate the quality"
            " of the responses generated by AI models. We will provide you with"
            " the user prompt and an AI-generated responses.\nYou should first"
            " read the user input carefully for analyzing the task, and then"
            " evaluate the quality of the responses based on the Criteria"
            " provided in the Evaluation section below.\nYou will assign the"
            " response a rating following the Rating Scores and Evaluation"
            " Steps. Give step by step explanations for your rating, and only"
            " choose ratings from the Rating Scores."
        )
        expected_evaluation_steps = {
            "Step 1": (
                "Assess the response in aspects of all criteria provided. Provide"
                " assessment according to each criterion."
            ),
            "Step 2": (
                "Score based on the Rating Scores. Give a brief rationale to"
                " explain your evaluation considering each individual criterion."
            ),
        }
        assert expected_instruction in builder.text
        for step_desc in expected_evaluation_steps.values():
            assert step_desc in builder.text

    def test_metric_prompt_builder_custom_instruction_and_steps_in_text(self):
        criteria = {"c1": "v1"}
        rating_scores = {"s1": "d1"}
        custom_instruction = "My custom instructions."
        custom_steps = {"Step 1": "Do this first.", "Step 2": "Then do that."}
        builder = vertexai_genai_types.MetricPromptBuilder(
            criteria=criteria,
            rating_scores=rating_scores,
            instruction=custom_instruction,
            evaluation_steps=custom_steps,
            metric_definition=None,
            few_shot_examples=None,
        )
        assert custom_instruction in builder.text
        for step_desc in custom_steps.values():
            assert step_desc in builder.text

    def test_metric_prompt_builder_missing_criteria_raises_error(self):
        with pytest.raises(
            ValueError,
            match="Both 'criteria' and 'rating_scores' are required",
        ):
            vertexai_genai_types.MetricPromptBuilder(
                rating_scores={"score1": "description1"},
                criteria=None,
                metric_definition=None,
                few_shot_examples=None,
            )

    def test_metric_prompt_builder_missing_rating_scores_raises_error(self):
        with pytest.raises(
            ValueError,
            match="Both 'criteria' and 'rating_scores' are required",
        ):
            vertexai_genai_types.MetricPromptBuilder(
                criteria={"criterion1": "definition1"},
                rating_scores=None,
                metric_definition=None,
                few_shot_examples=None,
            )


class TestPromptTemplate:
    """Unit tests for the PromptTemplate class."""

    def test_prompt_template_variables(self):
        template = vertexai_genai_types.PromptTemplate(
            text="Hello {name}, welcome to {place}!"
        )
        assert template.variables == {"name", "place"}

    def test_prompt_template_assemble_simple(self):
        template = vertexai_genai_types.PromptTemplate(text="Hello {name}.")
        assert template.assemble(name="World") == "Hello World."

    def test_prompt_template_assemble_missing_variable_raises_error(self):
        template = vertexai_genai_types.PromptTemplate(text="Hello {name}.")
        with pytest.raises(
            ValueError, match="Missing value for template variable 'name'"
        ):
            template.assemble()

    def test_prompt_template_assemble_extra_variable_raises_error(self):
        template = vertexai_genai_types.PromptTemplate(text="Hello {name}.")
        with pytest.raises(
            ValueError, match="Invalid variable name 'extra_var' provided"
        ):
            template.assemble(name="Test", extra_var="unused")

    def test_prompt_template_text_must_not_be_empty(self):
        with pytest.raises(ValueError, match="Prompt template text cannot be empty"):
            vertexai_genai_types.PromptTemplate(text=" ")

    def test_prompt_template_assemble_all_text_single_part_returns_string(self):
        template = vertexai_genai_types.PromptTemplate(text="{greeting}, {name}.")
        result = template.assemble(greeting="Hi", name="There")
        assert result == "Hi, There."

    def test_prompt_template_str_representation(self):
        template_text = "This is a template: {var}"
        template = vertexai_genai_types.PromptTemplate(text=template_text)
        assert str(template) == template_text

    def test_prompt_template_repr_representation(self):
        template_text = "Test {repr}"
        template = vertexai_genai_types.PromptTemplate(text=template_text)
        assert repr(template) == f"PromptTemplate(text='{template_text}')"

    def test_prompt_template_assemble_multimodal_output(self):
        template = vertexai_genai_types.PromptTemplate(
            text="Context: {image_data} Question: {query}"
        )
        image_content_json = genai_types.Content(
            parts=[
                genai_types.Part(
                    file_data=genai_types.FileData(
                        mime_type="image/png", file_uri="gs://fake-bucket/image.png"
                    )
                ),
            ]
        ).model_dump_json(exclude_none=True)

        result = template.assemble(image_data=image_content_json, query="What is this?")
        expected_parts = [
            genai_types.Part(text="Context: "),
            genai_types.Part(
                file_data=genai_types.FileData(
                    mime_type="image/png", file_uri="gs://fake-bucket/image.png"
                )
            ),
            genai_types.Part(text=" Question: What is this?"),
        ]
        expected_content_json = genai_types.Content(
            parts=expected_parts
        ).model_dump_json(exclude_none=True)

        assert json.loads(result) == json.loads(expected_content_json)

    def test_prompt_template_assemble_multimodal_variable_integration(self):
        template_str = "Observe: {media_part} and then answer: {txt_part}"
        template = vertexai_genai_types.PromptTemplate(text=template_str)

        media_var_value = genai_types.Content(
            parts=[
                genai_types.Part(
                    file_data=genai_types.FileData(
                        mime_type="video/mp4", file_uri="gs://fake-bucket/video.mp4"
                    )
                )
            ]
        ).model_dump_json(exclude_none=True)

        txt_var_value = "This is a simple text."

        assembled_prompt_json = template.assemble(
            media_part=media_var_value, txt_part=txt_var_value
        )

        assembled_content = genai_types.Content.model_validate_json(
            assembled_prompt_json
        )

        assert len(assembled_content.parts) == 3
        assert assembled_content.parts[0].text == "Observe: "
        assert assembled_content.parts[1].file_data.mime_type == "video/mp4"
        assert (
            assembled_content.parts[1].file_data.file_uri
            == "gs://fake-bucket/video.mp4"
        )
        assert (
            assembled_content.parts[2].text
            == " and then answer: This is a simple text."
        )


class TestGeminiEvalDataConverter:
    """Unit tests for the _GeminiEvalDataConverter class."""

    def setup_method(self):
        self.converter = _evals_data_converters._GeminiEvalDataConverter()

    def test_convert_simple_prompt_response(self):
        raw_data = [
            {
                "request": {
                    "contents": [{"role": "user", "parts": [{"text": "Hello"}]}]
                },
                "response": {
                    "candidates": [
                        {
                            "content": {"role": "model", "parts": [{"text": "Hi"}]},
                            "finish_reason": "STOP",
                        }
                    ],
                    "usage_metadata": {
                        "prompt_token_count": 1,
                        "candidates_token_count": 1,
                        "total_token_count": 2,
                    },
                },
            }
        ]
        result_dataset = self.converter.convert(raw_data)
        assert isinstance(result_dataset, vertexai_genai_types.EvaluationDataset)
        assert len(result_dataset.eval_cases) == 1
        eval_case = result_dataset.eval_cases[0]

        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Hello")], role="user"
        )
        assert len(eval_case.responses) == 1
        assert eval_case.responses[0].response == genai_types.Content(
            parts=[genai_types.Part(text="Hi")], role="model"
        )
        assert eval_case.reference.response is None
        assert eval_case.system_instruction.parts is None
        assert eval_case.conversation_history == []

    def test_convert_with_system_instruction(self):
        raw_data = [
            {
                "request": {
                    "system_instruction": {
                        "role": "system",
                        "parts": [{"text": "Be nice."}],
                    },
                    "contents": [{"role": "user", "parts": [{"text": "Hello"}]}],
                },
                "response": {
                    "candidates": [
                        {
                            "content": {
                                "role": "model",
                                "parts": [{"text": "Hi there!"}],
                            }
                        }
                    ]
                },
            }
        ]
        result_dataset = self.converter.convert(raw_data)
        eval_case = result_dataset.eval_cases[0]
        assert eval_case.system_instruction == genai_types.Content(
            parts=[genai_types.Part(text="Be nice.")], role="system"
        )
        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Hello")], role="user"
        )

    def test_convert_with_conversation_history_and_reference(self):
        raw_data_for_reference = [
            {
                "request": {
                    "contents": [
                        {
                            "role": "user",
                            "parts": [{"text": "Initial user"}],
                        },
                        {
                            "role": "model",
                            "parts": [{"text": "Initial model"}],
                        },
                        {
                            "role": "user",
                            "parts": [{"text": "Actual prompt"}],
                        },
                        {
                            "role": "model",
                            "parts": [{"text": "This is reference"}],
                        },
                    ]
                },
                "response": {
                    "candidates": [
                        {
                            "content": {
                                "role": "model",
                                "parts": [{"text": "Actual response"}],
                            }
                        }
                    ]
                },
            }
        ]
        result_dataset = self.converter.convert(raw_data_for_reference)
        eval_case = result_dataset.eval_cases[0]

        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Actual prompt")], role="user"
        )
        assert eval_case.reference.response == genai_types.Content(
            parts=[genai_types.Part(text="This is reference")], role="model"
        )
        assert len(eval_case.conversation_history) == 2
        assert eval_case.conversation_history[0].content == genai_types.Content(
            parts=[genai_types.Part(text="Initial user")], role="user"
        )
        assert eval_case.conversation_history[1].content == genai_types.Content(
            parts=[genai_types.Part(text="Initial model")], role="model"
        )
        assert eval_case.responses[0].response == genai_types.Content(
            parts=[genai_types.Part(text="Actual response")], role="model"
        )

    def test_convert_with_conversation_history_no_reference(self):
        raw_data = [
            {
                "request": {
                    "contents": [
                        {"role": "user", "parts": [{"text": "Old user msg"}]},
                        {"role": "model", "parts": [{"text": "Old model msg"}]},
                        {"role": "user", "parts": [{"text": "Current prompt"}]},
                    ]
                },
                "response": {
                    "candidates": [
                        {
                            "content": {
                                "role": "model",
                                "parts": [{"text": "A response"}],
                            }
                        }
                    ]
                },
            }
        ]
        result_dataset = self.converter.convert(raw_data)
        eval_case = result_dataset.eval_cases[0]

        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Current prompt")], role="user"
        )
        assert eval_case.reference.response is None
        assert len(eval_case.conversation_history) == 2
        assert eval_case.conversation_history[0].content.parts[0].text == "Old user msg"
        assert (
            eval_case.conversation_history[1].content.parts[0].text == "Old model msg"
        )

    def test_convert_no_candidates_in_response(self):
        raw_data = [
            {
                "request": {
                    "contents": [{"role": "user", "parts": [{"text": "Hello"}]}]
                },
                "response": {
                    "candidates": [],
                    "prompt_feedback": {"block_reason": "SAFETY"},
                },
            }
        ]
        result_dataset = self.converter.convert(raw_data)
        eval_case = result_dataset.eval_cases[0]
        assert len(eval_case.responses) == 1
        assert (
            eval_case.responses[0].response.parts[0].text
            == _evals_data_converters._PLACEHOLDER_RESPONSE_TEXT
        )

    def test_convert_invalid_content_structure_raises_value_error(self):
        raw_data = [
            {
                "request": {"contents": ["not a dict"]},
                "response": {
                    "candidates": [
                        {"content": {"role": "model", "parts": [{"text": "Hi"}]}}
                    ]
                },
            }
        ]
        with pytest.raises(
            TypeError, match="Expected a dictionary for content at turn 0"
        ):
            self.converter.convert(raw_data)

        raw_data_missing_parts = [
            {
                "request": {"contents": [{"role": "user"}]},  # Missing 'parts'
                "response": {
                    "candidates": [
                        {"content": {"role": "model", "parts": [{"text": "Hi"}]}}
                    ]
                },
            }
        ]
        with pytest.raises(
            ValueError, match="Missing 'parts' key in content structure at turn 0"
        ):
            self.converter.convert(raw_data_missing_parts)

    def test_convert_multiple_items(self):
        raw_data = [
            {
                "request": {
                    "contents": [{"role": "user", "parts": [{"text": "Item 1"}]}]
                },
                "response": {
                    "candidates": [
                        {
                            "content": {
                                "role": "model",
                                "parts": [{"text": "Resp 1"}],
                            }
                        }
                    ]
                },
            },
            {
                "request": {
                    "contents": [{"role": "user", "parts": [{"text": "Item 2"}]}]
                },
                "response": {
                    "candidates": [
                        {
                            "content": {
                                "role": "model",
                                "parts": [{"text": "Resp 2"}],
                            }
                        }
                    ]
                },
            },
        ]
        result_dataset = self.converter.convert(raw_data)
        assert len(result_dataset.eval_cases) == 2
        assert result_dataset.eval_cases[0].prompt.parts[0].text == "Item 1"
        assert result_dataset.eval_cases[1].prompt.parts[0].text == "Item 2"

    def test_convert_with_raw_string_response(self):
        """Tests conversion when the response is a raw string."""
        raw_data = [
            {
                "request": {
                    "contents": [{"role": "user", "parts": [{"text": "Hello"}]}]
                },
                "response": "Hi from a raw string",
            }
        ]
        result_dataset = self.converter.convert(raw_data)
        assert isinstance(result_dataset, vertexai_genai_types.EvaluationDataset)
        assert len(result_dataset.eval_cases) == 1
        eval_case = result_dataset.eval_cases[0]

        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Hello")], role="user"
        )
        assert len(eval_case.responses) == 1
        assert eval_case.responses[0].response == genai_types.Content(
            parts=[genai_types.Part(text="Hi from a raw string")],
        )


class TestFlattenEvalDataConverter:
    """Unit tests for the _FlattenEvalDataConverter class."""

    def setup_method(self):
        self.converter = _evals_data_converters._FlattenEvalDataConverter()

    def test_convert_simple_prompt_response(self):
        raw_data_df = pd.DataFrame(
            {
                "prompt": ["Hello"],
                "response": ["Hi"],
            }
        )
        raw_data = raw_data_df.to_dict(orient="records")
        result_dataset = self.converter.convert(raw_data)
        assert isinstance(result_dataset, vertexai_genai_types.EvaluationDataset)
        assert len(result_dataset.eval_cases) == 1
        eval_case = result_dataset.eval_cases[0]

        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Hello")]
        )
        assert len(eval_case.responses) == 1
        assert eval_case.responses[0].response == genai_types.Content(
            parts=[genai_types.Part(text="Hi")]
        )
        assert eval_case.reference is None
        assert eval_case.system_instruction is None
        assert eval_case.conversation_history is None

    def test_convert_with_system_instruction_and_reference(self):
        raw_data_df = pd.DataFrame(
            {
                "prompt": ["Hello"],
                "response": ["Hi there!"],
                "instruction": ["Be nice."],
                "reference": ["Hey"],
            }
        )
        raw_data = raw_data_df.to_dict(orient="records")
        result_dataset = self.converter.convert(raw_data)
        eval_case = result_dataset.eval_cases[0]
        assert eval_case.system_instruction == genai_types.Content(
            parts=[genai_types.Part(text="Be nice.")]
        )
        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Hello")]
        )
        assert eval_case.reference.response == genai_types.Content(
            parts=[genai_types.Part(text="Hey")]
        )

    def test_convert_with_conversation_history(self):
        raw_data_df = pd.DataFrame(
            {
                "prompt": ["Current prompt"],
                "response": ["A response"],
                "history": [
                    [
                        {"role": "user", "parts": [{"text": "Old user msg"}]},
                        {"role": "model", "parts": [{"text": "Old model msg"}]},
                    ]
                ],
            }
        )
        raw_data = raw_data_df.to_dict(orient="records")
        result_dataset = self.converter.convert(raw_data)
        eval_case = result_dataset.eval_cases[0]

        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Current prompt")]
        )
        assert eval_case.reference is None
        assert len(eval_case.conversation_history) == 2
        assert eval_case.conversation_history[0].content.parts[0].text == "Old user msg"
        assert (
            eval_case.conversation_history[1].content.parts[0].text == "Old model msg"
        )

    def test_convert_with_conversation_history_column_name(self):
        """Tests that 'conversation_history' is accepted as a column name alias for 'history'."""
        raw_data_df = pd.DataFrame(
            {
                "prompt": ["Current prompt"],
                "response": ["A response"],
                "conversation_history": [
                    [
                        {"role": "user", "parts": [{"text": "Old user msg"}]},
                        {"role": "model", "parts": [{"text": "Old model msg"}]},
                    ]
                ],
            }
        )
        raw_data = raw_data_df.to_dict(orient="records")
        result_dataset = self.converter.convert(raw_data)
        eval_case = result_dataset.eval_cases[0]

        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Current prompt")]
        )
        assert eval_case.reference is None
        assert len(eval_case.conversation_history) == 2
        assert eval_case.conversation_history[0].content.parts[0].text == "Old user msg"
        assert (
            eval_case.conversation_history[1].content.parts[0].text == "Old model msg"
        )

    def test_convert_missing_response_raises_value_error(self):
        raw_data_df = pd.DataFrame({"prompt": ["Hello"]})  # Missing response
        raw_data = raw_data_df.to_dict(orient="records")
        with pytest.raises(
            ValueError, match="Response is required but missing for eval_case_0"
        ):
            self.converter.convert(raw_data)

    def test_convert_missing_prompt_raises_value_error(self):
        raw_data_df = pd.DataFrame({"response": ["Hi"]})  # Missing prompt
        raw_data = raw_data_df.to_dict(orient="records")
        with pytest.raises(
            ValueError, match="Prompt is required but missing for eval_case_0"
        ):
            self.converter.convert(raw_data)

    def test_convert_invalid_prompt_type_raises_value_error(self):
        raw_data_df = pd.DataFrame(
            {
                "prompt": [123],  # Invalid prompt type
                "response": ["Hi"],
            }
        )
        raw_data = raw_data_df.to_dict(orient="records")
        with pytest.raises(ValueError, match="Invalid prompt type for case 0"):
            self.converter.convert(raw_data)

    def test_convert_invalid_response_type_raises_value_error(self):
        raw_data_df = pd.DataFrame(
            {
                "prompt": ["Hello"],
                "response": [123],  # Invalid response type
            }
        )
        raw_data = raw_data_df.to_dict(orient="records")
        with pytest.raises(ValueError, match="Invalid response type for case 0"):
            self.converter.convert(raw_data)

    def test_convert_multiple_items(self):
        raw_data_df = pd.DataFrame(
            {
                "prompt": ["Item 1", "Item 2"],
                "response": ["Resp 1", "Resp 2"],
            }
        )
        raw_data = raw_data_df.to_dict(orient="records")
        result_dataset = self.converter.convert(raw_data)
        assert len(result_dataset.eval_cases) == 2
        assert result_dataset.eval_cases[0].prompt.parts[0].text == "Item 1"
        assert result_dataset.eval_cases[1].prompt.parts[0].text == "Item 2"

    def test_convert_with_additional_columns(self):
        raw_data_df = pd.DataFrame(
            {
                "prompt": ["Hello"],
                "response": ["Hi"],
                "custom_column": ["custom_value"],
            }
        )
        raw_data = raw_data_df.to_dict(orient="records")
        result_dataset = self.converter.convert(raw_data)
        eval_case = result_dataset.eval_cases[0]
        assert eval_case.custom_column == "custom_value"

    def test_convert_with_agent_eval_fields(self):
        """Tests that agent eval data is converted correctly from a flattened format."""
        raw_data_df = pd.DataFrame(
            {
                "prompt": ["Hello"],
                "response": ["Hi"],
                "intermediate_events": [
                    [
                        {
                            "event_id": "event1",
                            "content": {"parts": [{"text": "intermediate event"}]},
                        }
                    ]
                ],
            }
        )
        raw_data = raw_data_df.to_dict(orient="records")
        result_dataset = self.converter.convert(raw_data)
        assert len(result_dataset.eval_cases) == 1
        eval_case = result_dataset.eval_cases[0]
        assert eval_case.intermediate_events[0].event_id == "event1"

    def test_convert_with_intermediate_events_as_event_objects(self):
        """Tests that agent eval data is converted correctly when intermediate_events are Event objects."""
        raw_data_df = pd.DataFrame(
            {
                "prompt": ["Hello"],
                "response": ["Hi"],
                "intermediate_events": [
                    [
                        vertexai_genai_types.evals.Event(
                            event_id="event1",
                            content=genai_types.Content(
                                parts=[genai_types.Part(text="intermediate event")]
                            ),
                        )
                    ]
                ],
            }
        )
        raw_data = raw_data_df.to_dict(orient="records")
        result_dataset = self.converter.convert(raw_data)
        assert len(result_dataset.eval_cases) == 1
        eval_case = result_dataset.eval_cases[0]
        assert eval_case.intermediate_events[0].event_id == "event1"
        assert (
            eval_case.intermediate_events[0].content.parts[0].text
            == "intermediate event"
        )


class TestOpenAIDataConverter:
    """Unit tests for the _OpenAIDataConverter class."""

    def setup_method(self):
        self.converter = _evals_data_converters._OpenAIDataConverter()

    def test_convert_simple_prompt_response(self):
        raw_data = [
            {
                "request": {"messages": [{"role": "user", "content": "Hello"}]},
                "response": {
                    "choices": [{"message": {"role": "assistant", "content": "Hi"}}]
                },
            }
        ]
        result_dataset = self.converter.convert(raw_data)
        assert isinstance(result_dataset, vertexai_genai_types.EvaluationDataset)
        assert len(result_dataset.eval_cases) == 1
        eval_case = result_dataset.eval_cases[0]

        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Hello")], role="user"
        )
        assert len(eval_case.responses) == 1
        assert eval_case.responses[0].response == genai_types.Content(
            parts=[genai_types.Part(text="Hi")]
        )
        assert eval_case.reference is None
        assert eval_case.system_instruction is None
        assert eval_case.conversation_history == []

    def test_convert_with_system_instruction(self):
        raw_data = [
            {
                "request": {
                    "messages": [
                        {"role": "system", "content": "Be helpful."},
                        {"role": "user", "content": "Hello"},
                    ]
                },
                "response": {
                    "choices": [{"message": {"role": "assistant", "content": "Hi"}}]
                },
            }
        ]
        result_dataset = self.converter.convert(raw_data)
        eval_case = result_dataset.eval_cases[0]
        assert eval_case.system_instruction == genai_types.Content(
            parts=[genai_types.Part(text="Be helpful.")]
        )
        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Hello")], role="user"
        )

    def test_convert_with_conversation_history_and_reference(self):
        raw_data = [
            {
                "request": {
                    "messages": [
                        {"role": "user", "content": "Initial user"},
                        {"role": "assistant", "content": "Initial model (ref)"},
                    ]
                },
                "response": {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": "Actual response",
                            }
                        }
                    ]
                },
            }
        ]
        result_dataset = self.converter.convert(raw_data)
        eval_case = result_dataset.eval_cases[0]

        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Initial user")], role="user"
        )
        assert eval_case.reference.response == genai_types.Content(
            parts=[genai_types.Part(text="Initial model (ref)")], role="assistant"
        )
        assert len(eval_case.conversation_history) == 0  # History before prompt and ref
        assert eval_case.responses[0].response == genai_types.Content(
            parts=[genai_types.Part(text="Actual response")]
        )

    def test_convert_with_conversation_history_no_reference(self):
        raw_data = [
            {
                "request": {
                    "messages": [
                        {"role": "user", "content": "Old user msg"},
                        {"role": "assistant", "content": "Old model msg"},
                        {"role": "user", "content": "Current prompt"},
                    ]
                },
                "response": {
                    "choices": [
                        {"message": {"role": "assistant", "content": "A response"}}
                    ]
                },
            }
        ]
        result_dataset = self.converter.convert(raw_data)
        eval_case = result_dataset.eval_cases[0]

        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Current prompt")], role="user"
        )
        assert eval_case.reference is None
        assert len(eval_case.conversation_history) == 2
        assert eval_case.conversation_history[0].content.parts[0].text == "Old user msg"
        assert (
            eval_case.conversation_history[1].content.parts[0].text == "Old model msg"
        )

    def test_convert_empty_choices_uses_placeholder(self):
        raw_data = [
            {
                "request": {"messages": [{"role": "user", "content": "Hello"}]},
                "response": {"choices": []},
            }
        ]
        result_dataset = self.converter.convert(raw_data)
        eval_case = result_dataset.eval_cases[0]
        assert len(eval_case.responses) == 1
        assert (
            eval_case.responses[0].response.parts[0].text
            == _evals_data_converters._PLACEHOLDER_RESPONSE_TEXT
        )

    def test_convert_skips_missing_request_or_response(self):
        raw_data = [{"response": {"choices": []}}, {"request": {"messages": []}}]
        result_dataset = self.converter.convert(raw_data)
        assert len(result_dataset.eval_cases) == 0


class TestObservabilityDataConverter:
    """Unit tests for the ObservabilityDataConverter class."""

    def setup_method(self):
        self.converter = _observability_data_converter.ObservabilityDataConverter()

    def test_convert_simple_request_response(self):
        raw_data = [
            {
                "format": "observability",
                "request": json.dumps(
                    {"role": "user", "parts": [{"content": "Hello", "type": "text"}]}
                ),
                "response": json.dumps(
                    {
                        "role": "system",
                        "parts": [{"content": "Hi", "type": "text"}],
                    }
                ),
            }
        ]
        result_dataset = self.converter.convert(raw_data)

        assert isinstance(result_dataset, vertexai_genai_types.EvaluationDataset)
        assert len(result_dataset.eval_cases) == 1

        eval_case = result_dataset.eval_cases[0]
        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Hello")], role="user"
        )
        assert len(eval_case.responses) == 1
        assert eval_case.responses[0].response == genai_types.Content(
            parts=[genai_types.Part(text="Hi")], role="system"
        )
        assert eval_case.reference is None
        assert eval_case.system_instruction is None
        assert not eval_case.conversation_history

    def test_convert_with_system_instruction(self):
        raw_data = [
            {
                "format": "observability",
                "request": json.dumps(
                    {"role": "user", "parts": [{"content": "Hello", "type": "text"}]}
                ),
                "response": json.dumps(
                    {
                        "role": "system",
                        "parts": [{"content": "Hi", "type": "text"}],
                    }
                ),
                "system_instruction": json.dumps(
                    {
                        "role": "user",
                        "parts": [{"content": "Be helpful", "type": "text"}],
                    }
                ),
            }
        ]
        result_dataset = self.converter.convert(raw_data)
        eval_case = result_dataset.eval_cases[0]
        assert eval_case.system_instruction == genai_types.Content(
            parts=[genai_types.Part(text="Be helpful")], role="user"
        )

    def test_convert_with_conversation_history(self):
        raw_data = [
            {
                "format": "observability",
                "request": json.dumps(
                    {"role": "user", "parts": [{"content": "Hello", "type": "text"}]}
                )
                + "\n"
                + json.dumps(
                    {"role": "system", "parts": [{"content": "Hi", "type": "text"}]}
                )
                + "\n"
                + json.dumps(
                    {
                        "role": "user",
                        "parts": [
                            {"content": "What's the meaning of life?", "type": "text"}
                        ],
                    }
                ),
                "response": json.dumps(
                    {
                        "role": "system",
                        "parts": [{"content": "42.", "type": "text"}],
                    }
                ),
            }
        ]

        result_dataset = self.converter.convert(raw_data)
        eval_case = result_dataset.eval_cases[0]

        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="What's the meaning of life?")], role="user"
        )

        assert len(eval_case.conversation_history) == 2
        assert eval_case.conversation_history[0] == vertexai_genai_types.evals.Message(
            content=genai_types.Content(
                parts=[genai_types.Part(text="Hello")], role="user"
            ),
            turn_id="0",
            author="user",
        )
        assert eval_case.conversation_history[1] == vertexai_genai_types.evals.Message(
            content=genai_types.Content(
                parts=[genai_types.Part(text="Hi")], role="system"
            ),
            turn_id="1",
            author="system",
        )

    def test_convert_multiple_request_response(self):
        raw_data = [
            {
                "format": "observability",
                "request": json.dumps(
                    {"role": "user", "parts": [{"content": "Hello", "type": "text"}]}
                ),
                "response": json.dumps(
                    {
                        "role": "system",
                        "parts": [{"content": "Hi", "type": "text"}],
                    }
                ),
            },
            {
                "format": "observability",
                "request": json.dumps(
                    {"role": "user", "parts": [{"content": "Goodbye", "type": "text"}]}
                ),
                "response": json.dumps(
                    {
                        "role": "system",
                        "parts": [{"content": "Bye", "type": "text"}],
                    }
                ),
            },
        ]
        result_dataset = self.converter.convert(raw_data)

        assert isinstance(result_dataset, vertexai_genai_types.EvaluationDataset)
        assert len(result_dataset.eval_cases) == 2

        eval_case = result_dataset.eval_cases[0]
        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Hello")], role="user"
        )
        assert eval_case.responses[0].response == genai_types.Content(
            parts=[genai_types.Part(text="Hi")], role="system"
        )

        eval_case = result_dataset.eval_cases[1]
        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Goodbye")], role="user"
        )
        assert eval_case.responses[0].response == genai_types.Content(
            parts=[genai_types.Part(text="Bye")], role="system"
        )

    def test_convert_skips_unknown_part_type(self):
        raw_data = [
            {
                "format": "observability",
                "request": json.dumps(
                    {
                        "role": "user",
                        "parts": [
                            {"content": 123, "type": ""},
                            {"content": 456},
                            {"content": "Hello", "type": "text"},
                        ],
                    }
                ),
                "response": json.dumps(
                    {
                        "role": "system",
                        "parts": [{"content": "Hi", "type": "text"}],
                    }
                ),
            }
        ]

        result_dataset = self.converter.convert(raw_data)
        eval_case = result_dataset.eval_cases[0]

        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Hello")], role="user"
        )

    def test_convert_skips_missing_request(self):
        raw_data = [
            {
                "format": "observability",
                "response": json.dumps(
                    {
                        "role": "system",
                        "parts": [{"content": "Hi", "type": "text"}],
                    }
                ),
            }
        ]
        result_dataset = self.converter.convert(raw_data)
        assert not result_dataset.eval_cases

    def test_convert_skips_missing_response(self):
        raw_data = [
            {
                "format": "observability",
                "request": json.dumps(
                    {"role": "user", "parts": [{"content": "Hello", "type": "text"}]}
                ),
            }
        ]
        result_dataset = self.converter.convert(raw_data)
        assert not result_dataset.eval_cases

    def test_convert_tool_call_parts(self):
        raw_data = [
            {
                "format": "observability",
                "request": json.dumps(
                    {
                        "role": "user",
                        "parts": [
                            {
                                "type": "tool_call",
                                "id": "tool_id",
                                "name": "tool_name",
                                "arguments": {"param": "1"},
                            }
                        ],
                    }
                ),
                "response": json.dumps(
                    {
                        "role": "system",
                        "parts": [
                            {
                                "type": "tool_call_response",
                                "id": "tool_id",
                                "result": {"field": "2"},
                            }
                        ],
                    }
                ),
            }
        ]
        result_dataset = self.converter.convert(raw_data)

        eval_case = result_dataset.eval_cases[0]
        assert eval_case.prompt == genai_types.Content(
            parts=[
                genai_types.Part(
                    function_call=genai_types.FunctionCall(
                        id="tool_id", name="tool_id", args={"param": "1"}
                    )
                )
            ],
            role="user",
        )
        assert len(eval_case.responses) == 1
        assert eval_case.responses[0].response == genai_types.Content(
            parts=[
                genai_types.Part(
                    function_response=genai_types.FunctionResponse(
                        id="tool_id", name="tool_id", response={"field": "2"}
                    )
                )
            ],
            role="system",
        )


class TestAgentInfo:
    """Unit tests for the AgentInfo class."""

    def test_agent_info_creation(self):
        tool = genai_types.Tool(
            function_declarations=[
                genai_types.FunctionDeclaration(
                    name="get_weather",
                    description="Get weather in a location",
                    parameters={
                        "type": "object",
                        "properties": {"location": {"type": "string"}},
                    },
                )
            ]
        )
        agent_info = vertexai_genai_types.evals.AgentInfo(
            name="agent_system",
            agents={
                "agent1": vertexai_genai_types.evals.AgentConfig(
                    agent_id="agent1",
                    instruction="instruction1",
                    description="description1",
                    tools=[tool],
                )
            },
        )
        assert agent_info.name == "agent_system"
        assert "agent1" in agent_info.agents
        assert agent_info.agents["agent1"].instruction == "instruction1"
        assert agent_info.agents["agent1"].description == "description1"
        assert agent_info.agents["agent1"].tools == [tool]

    @mock.patch.object(genai_types.FunctionDeclaration, "from_callable_with_api_option")
    def test_load_from_agent(self, mock_from_callable):
        def my_search_tool(query: str) -> str:
            """Searches for information."""
            return f"search result for {query}"

        mock_function_declaration = mock.Mock(spec=genai_types.FunctionDeclaration)
        mock_from_callable.return_value = mock_function_declaration

        mock_agent = mock.Mock()
        mock_agent.name = "mock_agent"
        mock_agent.instruction = "mock instruction"
        mock_agent.description = "mock description"
        mock_agent.tools = [my_search_tool]
        mock_agent.sub_agents = []

        agent_info = vertexai_genai_types.evals.AgentInfo.load_from_agent(
            agent=mock_agent,
        )

        assert agent_info.name == "mock_agent"
        assert agent_info.agents["mock_agent"].instruction == "mock instruction"
        assert agent_info.agents["mock_agent"].description == "mock description"
        assert len(agent_info.agents["mock_agent"].tools) == 1
        assert isinstance(agent_info.agents["mock_agent"].tools[0], genai_types.Tool)
        assert agent_info.agents["mock_agent"].tools[0].function_declarations == [
            mock_function_declaration
        ]
        mock_from_callable.assert_called_once_with(callable=my_search_tool)

    def test_load_from_agent_with_get_declaration_tool(self):
        """Tests that tools with _get_declaration() use it instead of from_callable."""
        mock_declaration = mock.Mock(spec=genai_types.FunctionDeclaration)

        mock_tool = mock.Mock()
        mock_tool._get_declaration = mock.Mock(return_value=mock_declaration)

        mock_agent = mock.Mock()
        mock_agent.name = "mock_agent"
        mock_agent.instruction = "mock instruction"
        mock_agent.description = "mock description"
        mock_agent.tools = [mock_tool]
        mock_agent.sub_agents = []

        agent_info = vertexai_genai_types.evals.AgentInfo.load_from_agent(
            agent=mock_agent,
        )

        assert agent_info.name == "mock_agent"
        assert len(agent_info.agents["mock_agent"].tools) == 1
        assert isinstance(agent_info.agents["mock_agent"].tools[0], genai_types.Tool)
        assert agent_info.agents["mock_agent"].tools[0].function_declarations == [
            mock_declaration
        ]
        mock_tool._get_declaration.assert_called_once()

    @mock.patch.object(genai_types.FunctionDeclaration, "from_callable_with_api_option")
    def test_load_from_agent_with_mixed_tools(self, mock_from_callable):
        """Tests agents with both _get_declaration tools and plain callables."""

        def my_plain_tool(query: str) -> str:
            """A plain callable tool."""
            return query

        mock_adk_declaration = mock.Mock(spec=genai_types.FunctionDeclaration)
        mock_adk_tool = mock.Mock()
        mock_adk_tool._get_declaration = mock.Mock(return_value=mock_adk_declaration)

        mock_callable_declaration = mock.Mock(spec=genai_types.FunctionDeclaration)
        mock_from_callable.return_value = mock_callable_declaration

        mock_agent = mock.Mock()
        mock_agent.name = "mock_agent"
        mock_agent.instruction = "mock instruction"
        mock_agent.description = "mock description"
        mock_agent.tools = [mock_adk_tool, my_plain_tool]
        mock_agent.sub_agents = []

        agent_info = vertexai_genai_types.evals.AgentInfo.load_from_agent(
            agent=mock_agent,
        )

        assert len(agent_info.agents["mock_agent"].tools) == 2
        # First tool: ADK tool with _get_declaration
        assert agent_info.agents["mock_agent"].tools[0].function_declarations == [
            mock_adk_declaration
        ]
        mock_adk_tool._get_declaration.assert_called_once()
        # Second tool: plain callable via from_callable_with_api_option
        assert agent_info.agents["mock_agent"].tools[1].function_declarations == [
            mock_callable_declaration
        ]
        mock_from_callable.assert_called_once_with(callable=my_plain_tool)

    def test_load_from_agent_with_none_declaration_falls_back(self):
        """Tests that tools returning None from _get_declaration fall back to from_callable."""
        mock_tool = mock.Mock()
        mock_tool._get_declaration = mock.Mock(return_value=None)
        mock_tool.__name__ = "mock_tool"
        mock_tool.__doc__ = "A mock tool."

        mock_agent = mock.Mock()
        mock_agent.name = "mock_agent"
        mock_agent.instruction = "mock instruction"
        mock_agent.description = "mock description"
        mock_agent.tools = [mock_tool]
        mock_agent.sub_agents = []

        with mock.patch.object(
            genai_types.FunctionDeclaration, "from_callable_with_api_option"
        ) as mock_from_callable:
            mock_callable_declaration = mock.Mock(spec=genai_types.FunctionDeclaration)
            mock_from_callable.return_value = mock_callable_declaration

            agent_info = vertexai_genai_types.evals.AgentInfo.load_from_agent(
                agent=mock_agent,
            )

            assert len(agent_info.agents["mock_agent"].tools) == 1
            assert agent_info.agents["mock_agent"].tools[0].function_declarations == [
                mock_callable_declaration
            ]
            mock_tool._get_declaration.assert_called_once()
            mock_from_callable.assert_called_once_with(callable=mock_tool)


class TestValidateDatasetAgentData:
    """Unit tests for the _validate_dataset_agent_data function."""

    def test_valid_agent_data_in_df(self):
        dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=pd.DataFrame(
                [
                    {
                        "agent_data": {
                            "turns": [{"turn_index": 0, "turn_id": "1", "events": []}]
                        }
                    },
                    {
                        "agent_data": '{"turns": [{"turn_index": 0, "turn_id": "2", "events": []}]}'
                    },
                    {
                        "agent_data": vertexai_genai_types.evals.AgentData(
                            turns=[{"turn_index": 0, "turn_id": "3", "events": []}]
                        )
                    },
                ]
            )
        )
        _evals_utils._validate_dataset_agent_data(dataset)

    def test_valid_agent_data_in_eval_cases(self):
        dataset = vertexai_genai_types.EvaluationDataset(
            eval_cases=[
                vertexai_genai_types.EvalCase(
                    agent_data={
                        "turns": [{"turn_index": 0, "turn_id": "1", "events": []}]
                    }
                ),
                vertexai_genai_types.EvalCase(
                    agent_data=json.loads(
                        '{"turns": [{"turn_index": 0, "turn_id": "2", "events": []}]}'
                    )
                ),
                vertexai_genai_types.EvalCase(
                    agent_data=vertexai_genai_types.evals.AgentData(
                        turns=[{"turn_index": 0, "turn_id": "3", "events": []}]
                    )
                ),
            ]
        )
        _evals_utils._validate_dataset_agent_data(dataset)

    def test_invalid_json_string_raises_error(self):
        dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=pd.DataFrame([{"agent_data": '{"turns":'}])
        )
        with pytest.raises(ValueError, match="is not valid JSON"):
            _evals_utils._validate_dataset_agent_data(dataset)

    def test_invalid_dict_raises_error(self):
        dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=pd.DataFrame([{"agent_data": {"agents": 123}}])
        )
        with pytest.raises(ValueError, match="is inconsistent with AgentData type"):
            _evals_utils._validate_dataset_agent_data(dataset)

    def test_valid_agent_data_with_error_in_dict(self):
        dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=pd.DataFrame(
                [{"agent_data": {"error": "some error message"}}]
            )
        )
        _evals_utils._validate_dataset_agent_data(dataset)

    def test_valid_agent_data_with_error_in_string(self):
        dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=pd.DataFrame(
                [{"agent_data": '{"error": "some error message"}'}]
            )
        )
        _evals_utils._validate_dataset_agent_data(dataset)

    def test_invalid_agent_data_type_raises_error(self):
        dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=pd.DataFrame([{"agent_data": 123}])
        )
        with pytest.raises(ValueError, match="is inconsistent with AgentData type"):
            _evals_utils._validate_dataset_agent_data(dataset)

    def test_conflict_with_inference_configs_raises_error(self):
        dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=pd.DataFrame(
                [
                    {
                        "agent_data": {
                            "agents": {"agent1": {"agent_id": "agent1"}},
                            "turns": [],
                        }
                    }
                ]
            )
        )
        inference_configs = {
            "cand1": {"agent_configs": {"agent1": {"agent_id": "agent1"}}}
        }
        with pytest.raises(
            ValueError,
            match="Cannot provide 'agents' in the dataset's 'agent_data'",
        ):
            _evals_utils._validate_dataset_agent_data(dataset, inference_configs)

    def test_no_conflict_with_inference_configs(self):
        dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=pd.DataFrame([{"agent_data": {"turns": []}}])
        )
        inference_configs = {
            "cand1": {"agent_configs": {"agent1": {"agent_id": "agent1"}}}
        }
        _evals_utils._validate_dataset_agent_data(dataset, inference_configs)

    def test_no_conflict_if_inference_configs_has_no_agent_configs(self):
        dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=pd.DataFrame(
                [
                    {
                        "agent_data": {
                            "agents": {"agent1": {"agent_id": "agent1"}},
                            "turns": [],
                        }
                    }
                ]
            )
        )
        inference_configs = {"cand1": {"model": "gemini-pro"}}
        _evals_utils._validate_dataset_agent_data(dataset, inference_configs)


class TestEvent:
    """Unit tests for the Event class."""

    def test_event_creation(self):
        event = vertexai_genai_types.evals.Event(
            event_id="event1",
            content=genai_types.Content(
                parts=[genai_types.Part(text="intermediate event")]
            ),
            author="user",
        )
        assert event.event_id == "event1"
        assert event.content.parts[0].text == "intermediate event"
        assert event.author == "user"


class TestEvalCase:
    """Unit tests for the EvalCase class."""

    def test_eval_case_with_agent_eval_fields(self):
        tool = genai_types.Tool(
            function_declarations=[
                genai_types.FunctionDeclaration(
                    name="get_weather",
                    description="Get weather in a location",
                    parameters={
                        "type": "object",
                        "properties": {"location": {"type": "string"}},
                    },
                )
            ]
        )
        agent_info = vertexai_genai_types.evals.AgentInfo(
            name="agent_system",
            agents={
                "agent1": vertexai_genai_types.evals.AgentConfig(
                    agent_id="agent1",
                    instruction="instruction1",
                    tools=[tool],
                )
            },
        )
        intermediate_events = [
            vertexai_genai_types.evals.Event(
                event_id="event1",
                content=genai_types.Content(
                    parts=[genai_types.Part(text="intermediate event")]
                ),
            )
        ]
        eval_case = vertexai_genai_types.EvalCase(
            prompt=genai_types.Content(parts=[genai_types.Part(text="Hello")]),
            responses=[
                vertexai_genai_types.ResponseCandidate(
                    response=genai_types.Content(parts=[genai_types.Part(text="Hi")])
                )
            ],
            agent_info=agent_info,
            intermediate_events=intermediate_events,
        )

        assert eval_case.agent_info == agent_info
        assert eval_case.intermediate_events == intermediate_events


class TestSessionInput:
    """Unit tests for the SessionInput class."""

    def test_session_input_creation(self):
        session_input = vertexai_genai_types.evals.SessionInput(
            user_id="user1",
            state={"key": "value"},
        )
        assert session_input.user_id == "user1"
        assert session_input.state == {"key": "value"}


@pytest.mark.usefixtures("google_auth_mock")
class TestBuildEvaluationInstance:
    def setup_method(self):
        importlib.reload(aiplatform_initializer)
        importlib.reload(aiplatform)
        importlib.reload(vertexai)
        importlib.reload(vertexai_genai_types)
        importlib.reload(_evals_data_converters)
        importlib.reload(_evals_metric_handlers)

        vertexai.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        self.mock_api_client = mock.Mock(spec=client.Client)
        self.mock_evals_module = evals.Evals(api_client_=self.mock_api_client)

    def test_build_evaluation_instance_basic_filtering_and_fields(self):
        metric = vertexai_genai_types.LLMMetric(
            name="test_quality",
            prompt_template="Eval: {prompt} with {response}. Context: {custom_context}. Ref: {reference}",
        )
        eval_case = vertexai_genai_types.EvalCase(
            prompt=genai_types.Content(
                parts=[genai_types.Part(text="User prompt text")]
            ),
            responses=[
                vertexai_genai_types.ResponseCandidate(
                    response=genai_types.Content(
                        parts=[genai_types.Part(text="Model response text")]
                    )
                )
            ],
            reference=vertexai_genai_types.ResponseCandidate(
                response=genai_types.Content(
                    parts=[genai_types.Part(text="Ground truth text")]
                )
            ),
            custom_context="Custom context value.",
            extra_field_not_in_template="This should be excluded.",
            eval_case_id="case-123",
        )

        response_content = _evals_metric_handlers._get_response_from_eval_case(
            eval_case, 0, metric.name
        )
        instance = _evals_metric_handlers._build_evaluation_instance(
            eval_case, response_content, prompt_template=metric.prompt_template
        )

        assert instance.prompt.contents.contents[0].parts[0].text == "User prompt text"
        assert (
            instance.response.contents.contents[0].parts[0].text
            == "Model response text"
        )
        assert (
            instance.reference.contents.contents[0].parts[0].text == "Ground truth text"
        )
        assert (
            instance.other_data.map_instance["custom_context"]
            .contents.contents[0]
            .parts[0]
            .text
            == "Custom context value."
        )
        assert "extra_field_not_in_template" not in instance.other_data.map_instance

    def test_build_evaluation_instance_various_field_types(self):
        metric = vertexai_genai_types.LLMMetric(
            name="test_various_fields",
            prompt_template="{prompt}{response}{conversation_history}{system_instruction}{dict_field}{list_field}{int_field}{bool_field}",
        )
        eval_case = vertexai_genai_types.EvalCase(
            prompt=genai_types.Content(parts=[genai_types.Part(text="The Prompt")]),
            responses=[
                vertexai_genai_types.ResponseCandidate(
                    response=genai_types.Content(
                        parts=[genai_types.Part(text="The Response")]
                    )
                )
            ],
            conversation_history=[
                vertexai_genai_types.evals.Message(
                    content=genai_types.Content(
                        parts=[genai_types.Part(text="Turn 1 user")], role="user"
                    )
                ),
                vertexai_genai_types.evals.Message(
                    content=genai_types.Content(
                        parts=[genai_types.Part(text="Turn 1 model")], role="model"
                    )
                ),
            ],
            system_instruction=genai_types.Content(
                parts=[genai_types.Part(text="System instructions here.")],
                role="system",
            ),
            dict_field={"key1": "val1", "key2": [1, 2]},
            list_field=["a", "b", {"c": 3}],
            int_field=42,
            bool_field=True,
        )

        response_content = _evals_metric_handlers._get_response_from_eval_case(
            eval_case, 0, metric.name
        )
        instance = _evals_metric_handlers._build_evaluation_instance(
            eval_case, response_content, prompt_template=metric.prompt_template
        )

        other_data = instance.other_data.map_instance
        assert (
            other_data["dict_field"].contents.contents[0].parts[0].text
            == '{"key1": "val1", "key2": [1, 2]}'
        )
        assert (
            other_data["list_field"].contents.contents[0].parts[0].text
            == '["a", "b", {"c": 3}]'
        )
        assert other_data["int_field"].contents.contents[0].parts[0].text == "42"
        assert other_data["bool_field"].contents.contents[0].parts[0].text == "True"
        assert (
            other_data["conversation_history"].contents.contents[0].parts[0].text
            == "user: Turn 1 user\nmodel: Turn 1 model"
        )
        assert (
            other_data["system_instruction"].contents.contents[0].parts[0].text
            == "System instructions here."
        )


class TestMetric:
    """Unit tests for the Metric class."""

    def test_metric_creation_success(self):
        metric = vertexai_genai_types.Metric(name="TestMetric")
        assert metric.name == "testmetric"
        assert metric.custom_function is None

    def test_metric_creation_with_custom_function(self):
        def my_custom_function(data: dict):
            return 1.0

        metric = vertexai_genai_types.Metric(
            name="custom_metric", custom_function=my_custom_function
        )
        assert metric.name == "custom_metric"
        assert metric.custom_function == my_custom_function

    def test_metric_name_validation_empty_raises_error(self):
        with pytest.raises(ValueError, match="Metric name cannot be empty."):
            vertexai_genai_types.Metric(name="")
        with pytest.raises(ValueError, match="Metric name cannot be empty."):
            vertexai_genai_types.Metric(name=None)

    def test_llm_metric_prompt_template_validation_empty_raises_error(self):
        with pytest.raises(ValueError, match="Prompt template cannot be empty."):
            vertexai_genai_types.LLMMetric(name="test_metric", prompt_template=None)
        with pytest.raises(
            ValueError, match="Prompt template cannot be an empty string."
        ):
            vertexai_genai_types.LLMMetric(name="test_metric", prompt_template="")
        with pytest.raises(
            ValueError, match="Prompt template cannot be an empty string."
        ):
            vertexai_genai_types.LLMMetric(name="test_metric", prompt_template="  ")

    def test_llm_metric_sampling_count_validation_raise_errors(self):
        with pytest.raises(
            ValueError, match="judge_model_sampling_count must be between 1 and 32."
        ):
            vertexai_genai_types.LLMMetric(
                name="test_metric",
                prompt_template="test_prompt_template",
                judge_model_sampling_count=0,
            )
        with pytest.raises(
            ValueError, match="judge_model_sampling_count must be between 1 and 32."
        ):
            vertexai_genai_types.LLMMetric(
                name="test_metric",
                prompt_template="test_prompt_template",
                judge_model_sampling_count=-1,
            )
        with pytest.raises(
            ValueError, match="judge_model_sampling_count must be between 1 and 32."
        ):
            vertexai_genai_types.LLMMetric(
                name="test_metric",
                prompt_template="test_prompt_template",
                judge_model_sampling_count=100,
            )

    def test_metric_name_validation_lowercase(self):
        metric = vertexai_genai_types.Metric(name="UPPERCASEMetric")
        assert metric.name == "uppercasemetric"

    @mock.patch("vertexai._genai.types.common.yaml.dump")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_metric_to_yaml_file_with_version_and_set_fields(
        self, mock_open_file, mock_yaml_dump
    ):
        metric_obj = vertexai_genai_types.Metric(
            name="MyMetricToDump",
            prompt_template="Evaluate: {input}",
            judge_model="gemini-1.5-pro",
            judge_model_sampling_count=5,
            return_raw_output=False,
            custom_function=lambda x: x,
            judge_model_system_instruction=None,
        )
        test_file_path = "/fake/path/metric_output.yaml"
        test_version = "v1.0.1"

        metric_obj.to_yaml_file(test_file_path, version=test_version)

        mock_open_file.assert_called_once_with(test_file_path, "w", encoding="utf-8")

        expected_data_to_dump = {
            "name": "mymetrictodump",
            "prompt_template": "Evaluate: {input}",
            "judge_model": "gemini-1.5-pro",
            "judge_model_sampling_count": 5,
            "return_raw_output": False,
            "version": test_version,
        }

        mock_yaml_dump.assert_called_once_with(
            expected_data_to_dump,
            mock_open_file(),
            sort_keys=False,
            allow_unicode=True,
        )

    @mock.patch("vertexai._genai.types.common.yaml.dump")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_metric_to_yaml_file_without_version_minimal_fields(
        self, mock_open_file, mock_yaml_dump
    ):
        metric_obj = vertexai_genai_types.Metric(name="MinimalMetric")
        test_file_path = "/fake/path/minimal_metric.yaml"

        metric_obj.to_yaml_file(test_file_path)

        mock_open_file.assert_called_once_with(test_file_path, "w", encoding="utf-8")
        expected_data_to_dump = {
            "name": "minimalmetric",
        }
        mock_yaml_dump.assert_called_once_with(
            expected_data_to_dump,
            mock_open_file(),
            sort_keys=False,
            allow_unicode=True,
        )

    @mock.patch("vertexai._genai.types.common.yaml", None)
    def test_metric_to_yaml_file_raises_importerror_if_yaml_is_none(self):
        metric_obj = vertexai_genai_types.Metric(name="ErrorMetric")
        with pytest.raises(
            ImportError, match="YAML serialization requires the pyyaml library"
        ):
            metric_obj.to_yaml_file("/fake/path/error.yaml")


class TestMergeResponseDatasets:
    """Unit tests for the merge_response_datasets_into_canonical_format function."""

    def test_merge_two_flatten_datasets(self):
        raw_dataset_1 = [
            {"prompt": "Prompt 1", "response": "Response 1a"},
            {"prompt": "Prompt 2", "response": "Response 2a"},
        ]
        raw_dataset_2 = [
            {"prompt": "Prompt 1", "response": "Response 1b"},
            {"prompt": "Prompt 2", "response": "Response 2b"},
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
        ]

        merged_dataset = (
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1, raw_dataset_2], schemas=schemas
            )
        )

        assert len(merged_dataset.eval_cases) == 2
        assert merged_dataset.eval_cases[0].prompt == genai_types.Content(
            parts=[genai_types.Part(text="Prompt 1")]
        )
        assert len(merged_dataset.eval_cases[0].responses) == 2
        assert merged_dataset.eval_cases[0].responses[
            0
        ].response == genai_types.Content(parts=[genai_types.Part(text="Response 1a")])
        assert merged_dataset.eval_cases[0].responses[
            1
        ].response == genai_types.Content(parts=[genai_types.Part(text="Response 1b")])
        assert merged_dataset.eval_cases[1].prompt == genai_types.Content(
            parts=[genai_types.Part(text="Prompt 2")]
        )
        assert len(merged_dataset.eval_cases[1].responses) == 2
        assert merged_dataset.eval_cases[1].responses[
            0
        ].response == genai_types.Content(parts=[genai_types.Part(text="Response 2a")])
        assert merged_dataset.eval_cases[1].responses[
            1
        ].response == genai_types.Content(parts=[genai_types.Part(text="Response 2b")])

    def test_merge_flatten_and_openai_datasets(self):
        raw_dataset_flatten = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1 Flatten",
                "reference": "Ref 1",
            },
        ]
        raw_dataset_openai = [
            {
                "request": {
                    "messages": [
                        {"role": "user", "content": "Prompt 1"},
                        {"role": "assistant", "content": "Ref 1"},
                    ]
                },
                "response": {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": "Response 1 OpenAI",
                            }
                        }
                    ]
                },
            }
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.OPENAI,
        ]

        merged_dataset = (
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_flatten, raw_dataset_openai], schemas=schemas
            )
        )
        assert len(merged_dataset.eval_cases) == 1
        case0 = merged_dataset.eval_cases[0]
        assert case0.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Prompt 1")]
        )
        assert case0.reference.response == genai_types.Content(
            parts=[genai_types.Part(text="Ref 1")]
        )
        assert len(case0.responses) == 2
        assert case0.responses[0].response == genai_types.Content(
            parts=[genai_types.Part(text="Response 1 Flatten")]
        )
        assert case0.responses[1].response == genai_types.Content(
            parts=[genai_types.Part(text="Response 1 OpenAI")]
        )

    def test_merge_two_openai_datasets(self):
        raw_dataset_openai_1 = [
            {
                "request": {
                    "messages": [
                        {"role": "developer", "content": "Sys1"},
                        {"role": "user", "content": "P1"},
                    ]
                },
                "response": {
                    "choices": [{"message": {"role": "assistant", "content": "R1a"}}]
                },
            }
        ]
        raw_dataset_openai_2 = [
            {
                "request": {
                    "messages": [
                        {"role": "system", "content": "Sys1"},
                        {"role": "user", "content": "P1"},
                    ]
                },
                "response": {
                    "choices": [{"message": {"role": "assistant", "content": "R1b"}}]
                },
            }
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.OPENAI,
            _evals_data_converters.EvalDatasetSchema.OPENAI,
        ]

        merged_dataset = (
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_openai_1, raw_dataset_openai_2], schemas=schemas
            )
        )
        assert len(merged_dataset.eval_cases) == 1
        case0 = merged_dataset.eval_cases[0]
        assert case0.prompt == genai_types.Content(
            parts=[genai_types.Part(text="P1")], role="user"
        )
        assert case0.system_instruction == genai_types.Content(
            parts=[genai_types.Part(text="Sys1")]
        )
        assert len(case0.responses) == 2
        assert case0.responses[0].response == genai_types.Content(
            parts=[genai_types.Part(text="R1a")]
        )
        assert case0.responses[1].response == genai_types.Content(
            parts=[genai_types.Part(text="R1b")]
        )

    def test_merge_flatten_and_gemini_datasets(self):
        raw_dataset_1 = [
            {"prompt": "Prompt 1", "response": "Response 1a"},
            {"prompt": "Prompt 2", "response": "Response 2a"},
        ]
        raw_dataset_2 = [
            {
                "request": {
                    "contents": [{"role": "user", "parts": [{"text": "Prompt 1"}]}]
                },
                "response": {
                    "candidates": [
                        {
                            "content": {
                                "role": "model",
                                "parts": [{"text": "Response 1b"}],
                            }
                        }
                    ]
                },
            },
            {
                "request": {
                    "contents": [{"role": "user", "parts": [{"text": "Prompt 2"}]}]
                },
                "response": {
                    "candidates": [
                        {
                            "content": {
                                "role": "model",
                                "parts": [{"text": "Response 2b"}],
                            }
                        }
                    ]
                },
            },
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.GEMINI,
        ]

        merged_dataset = (
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1, raw_dataset_2], schemas=schemas
            )
        )

        assert len(merged_dataset.eval_cases) == 2
        assert merged_dataset.eval_cases[0].prompt == genai_types.Content(
            parts=[genai_types.Part(text="Prompt 1")]
        )
        assert len(merged_dataset.eval_cases[0].responses) == 2
        assert merged_dataset.eval_cases[0].responses[
            0
        ].response == genai_types.Content(parts=[genai_types.Part(text="Response 1a")])
        assert merged_dataset.eval_cases[0].responses[
            1
        ].response == genai_types.Content(
            parts=[genai_types.Part(text="Response 1b")], role="model"
        )
        assert merged_dataset.eval_cases[1].prompt == genai_types.Content(
            parts=[genai_types.Part(text="Prompt 2")]
        )
        assert len(merged_dataset.eval_cases[1].responses) == 2
        assert merged_dataset.eval_cases[1].responses[
            0
        ].response == genai_types.Content(parts=[genai_types.Part(text="Response 2a")])
        assert merged_dataset.eval_cases[1].responses[
            1
        ].response == genai_types.Content(
            parts=[genai_types.Part(text="Response 2b")], role="model"
        )

    def test_merge_empty_input_list(self):
        with pytest.raises(
            ValueError,
            match="Input 'raw_datasets' cannot be empty and must be a list of lists.",
        ):
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                raw_datasets=[], schemas=[]
            )

    def test_merge_mismatched_number_of_eval_cases(self):
        raw_dataset_1 = [
            {"prompt": "Prompt 1", "response": "Response 1a"},
            {"prompt": "Prompt 2", "response": "Response 2a"},
        ]
        raw_dataset_2 = [
            {"prompt": "Prompt 1", "response": "Response 1b"},
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
        ]

        with pytest.raises(
            ValueError,
            match="All datasets must have the same number of evaluation cases",
        ):
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1, raw_dataset_2], schemas=schemas
            )

    def test_merge_mismatched_schemas_list_length(self):
        raw_dataset_1 = [
            {"prompt": "Prompt 1", "response": "Response 1a"},
            {"prompt": "Prompt 2", "response": "Response 2a"},
        ]
        raw_dataset_2 = [
            {"prompt": "Prompt 1", "response": "Response 1b"},
            {"prompt": "Prompt 2", "response": "Response 2b"},
        ]
        raw_dataset_3 = [
            {"prompt": "Prompt 1", "response": "Response 1c"},
            {"prompt": "Prompt 2", "response": "Response 2c"},
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.GEMINI,
        ]
        with pytest.raises(
            ValueError,
            match=(
                "A list of schemas must be provided, one for each raw dataset. Got 2"
                " schemas for 3 datasets."
            ),
        ):
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1, raw_dataset_2, raw_dataset_3],
                schemas=schemas,
            )

    def test_merge_empty_schemas_list(self):
        raw_dataset_1 = [
            {"prompt": "Prompt 1", "response": "Response 1a"},
            {"prompt": "Prompt 2", "response": "Response 2a"},
        ]
        with pytest.raises(
            ValueError,
            match=(
                "A list of schemas must be provided, one for each raw dataset. Got 0"
                " schemas for 1 datasets."
            ),
        ):
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1], schemas=[]
            )

    def test_merge_with_custom_columns(self):
        raw_dataset_1 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1a",
                "custom_col_1": "value_1_1",
            },
            {
                "prompt": "Prompt 2",
                "response": "Response 2a",
                "custom_col_1": "value_2_1",
            },
        ]
        raw_dataset_2 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1b",
                "custom_col_2": "value_1_2",
            },
            {
                "prompt": "Prompt 2",
                "response": "Response 2b",
                "custom_col_2": "value_2_2",
            },
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
        ]

        merged_dataset = (
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1, raw_dataset_2], schemas=schemas
            )
        )

        assert len(merged_dataset.eval_cases) == 2
        assert merged_dataset.eval_cases[0].custom_col_1 == "value_1_1"
        assert merged_dataset.eval_cases[0].custom_col_2 == "value_1_2"
        assert merged_dataset.eval_cases[1].custom_col_1 == "value_2_1"
        assert merged_dataset.eval_cases[1].custom_col_2 == "value_2_2"

    def test_merge_with_different_custom_columns(self):
        raw_dataset_1 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1a",
                "custom_col_1": "value_1_1",
            },
            {
                "prompt": "Prompt 2",
                "response": "Response 2a",
                "custom_col_1": "value_2_1",
            },
        ]
        raw_dataset_2 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1b",
                "custom_col_2": "value_1_2",
                "custom_col_3": "value_1_3",
            },
            {
                "prompt": "Prompt 2",
                "response": "Response 2b",
                "custom_col_2": "value_2_2",
                "custom_col_3": "value_2_3",
            },
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
        ]

        merged_dataset = (
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1, raw_dataset_2], schemas=schemas
            )
        )

        assert len(merged_dataset.eval_cases) == 2
        assert merged_dataset.eval_cases[0].custom_col_1 == "value_1_1"
        assert merged_dataset.eval_cases[0].custom_col_2 == "value_1_2"
        assert merged_dataset.eval_cases[0].custom_col_3 == "value_1_3"
        assert merged_dataset.eval_cases[1].custom_col_1 == "value_2_1"
        assert merged_dataset.eval_cases[1].custom_col_2 == "value_2_2"
        assert merged_dataset.eval_cases[1].custom_col_3 == "value_2_3"

    def test_merge_with_intermediate_events(self):
        raw_dataset_1 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1a",
                "intermediate_events": [
                    {
                        "event_id": "event1",
                        "content": {"parts": [{"text": "intermediate event"}]},
                    }
                ],
            }
        ]
        raw_dataset_2 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1b",
                "intermediate_events": [
                    {
                        "event_id": "event2",
                        "content": {"parts": [{"text": "intermediate event 2"}]},
                    }
                ],
            }
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
        ]

        merged_dataset = (
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1, raw_dataset_2], schemas=schemas
            )
        )

        assert len(merged_dataset.eval_cases) == 1
        assert len(merged_dataset.eval_cases[0].intermediate_events) == 1
        assert merged_dataset.eval_cases[0].intermediate_events[0].event_id == "event1"

    def test_merge_with_metadata(self):
        raw_dataset_1 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1a",
                "metadata": {"model": "model_1"},
            }
        ]
        raw_dataset_2 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1b",
            }
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
        ]

        merged_dataset = (
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1, raw_dataset_2], schemas=schemas
            )
        )

        assert len(merged_dataset.eval_cases) == 1

    def test_merge_with_different_number_of_responses(self):
        raw_dataset_1 = [{"prompt": "Prompt 1", "response": "Response 1a"}]
        raw_dataset_2 = [
            {
                # Gemini schema
                "request": {
                    "contents": [{"role": "user", "parts": [{"text": "Prompt 1"}]}]
                },
                "response": {
                    "candidates": [
                        {
                            "content": {
                                "role": "model",
                                "parts": [{"text": "Response 1b"}],
                            }
                        },
                        {
                            "content": {
                                "role": "model",
                                "parts": [{"text": "Response 1c"}],
                            }
                        },
                    ]
                },
            }
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.GEMINI,
        ]

        merged_dataset = (
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1, raw_dataset_2], schemas=schemas
            )
        )

        assert len(merged_dataset.eval_cases) == 1
        assert len(merged_dataset.eval_cases[0].responses) == 2
        assert merged_dataset.eval_cases[0].responses[
            0
        ].response == genai_types.Content(parts=[genai_types.Part(text="Response 1a")])
        assert merged_dataset.eval_cases[0].responses[
            1
        ].response == genai_types.Content(
            parts=[genai_types.Part(text="Response 1b")], role="model"
        )

    def test_merge_with_conversation_history(self):
        raw_dataset_1 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1a",
                "history": [
                    {"role": "user", "parts": [{"text": "Old user msg 1"}]},
                    {"role": "model", "parts": [{"text": "Old model msg 1"}]},
                ],
            }
        ]
        raw_dataset_2 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1b",
                "history": [
                    {"role": "user", "parts": [{"text": "Old user msg 2"}]},
                    {"role": "model", "parts": [{"text": "Old model msg 2"}]},
                ],
            }
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
        ]

        merged_dataset = (
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1, raw_dataset_2], schemas=schemas
            )
        )

        assert len(merged_dataset.eval_cases) == 1
        assert len(merged_dataset.eval_cases[0].conversation_history) == 2
        assert (
            merged_dataset.eval_cases[0].conversation_history[0].content.parts[0].text
            == "Old user msg 1"
        )
        assert (
            merged_dataset.eval_cases[0].conversation_history[1].content.parts[0].text
            == "Old model msg 1"
        )

    def test_merge_with_empty_conversation_history(self):
        raw_dataset_1 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1a",
                "history": [],
            }
        ]
        raw_dataset_2 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1b",
                "history": [],
            }
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
        ]

        merged_dataset = (
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1, raw_dataset_2], schemas=schemas
            )
        )

        assert len(merged_dataset.eval_cases) == 1
        assert len(merged_dataset.eval_cases[0].conversation_history) == 0

    def test_merge_with_reference(self):
        raw_dataset_1 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1a",
                "reference": "Reference 1",
            }
        ]
        raw_dataset_2 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1b",
                "reference": "Reference 2",
            }
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
        ]

        merged_dataset = (
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1, raw_dataset_2], schemas=schemas
            )
        )

        assert len(merged_dataset.eval_cases) == 1
        assert merged_dataset.eval_cases[0].reference.response == genai_types.Content(
            parts=[genai_types.Part(text="Reference 1")]
        )

    def test_merge_with_system_instruction(self):
        raw_dataset_1 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1a",
                "instruction": "Instruction 1",
            }
        ]
        raw_dataset_2 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1b",
                "instruction": "Instruction 2",
            }
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
        ]

        merged_dataset = (
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1, raw_dataset_2], schemas=schemas
            )
        )

        assert len(merged_dataset.eval_cases) == 1
        assert merged_dataset.eval_cases[0].system_instruction == genai_types.Content(
            parts=[genai_types.Part(text="Instruction 1")]
        )

    def test_merge_with_invalid_schema_type(self):
        raw_dataset_1 = [
            {"prompt": "Prompt 1", "response": "Response 1a"},
        ]
        with pytest.raises(
            ValueError,
            match="Unsupported dataset schema: invalid_schema",
        ):
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                raw_datasets=[raw_dataset_1], schemas=["invalid_schema"]
            )

    def test_merge_with_invalid_raw_dataset_type(self):
        with pytest.raises(
            TypeError,
            match="Input 'raw_datasets' must be a list",
        ):
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                raw_datasets="invalid_dataset",
                schemas=[_evals_data_converters.EvalDatasetSchema.FLATTEN],
            )
        with pytest.raises(
            ValueError,
            match=("Input 'raw_datasets' cannot be empty and must be a list of lists"),
        ):
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                raw_datasets=["invalid_dataset"],
                schemas=[_evals_data_converters.EvalDatasetSchema.FLATTEN],
            )

    def test_merge_with_invalid_eval_case_type(self):
        raw_dataset_1 = [
            "invalid_eval_case",
        ]
        with pytest.raises(
            TypeError,
            match="Expected a dictionary for item at index 0",
        ):
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                raw_datasets=[raw_dataset_1],
                schemas=[_evals_data_converters.EvalDatasetSchema.FLATTEN],
            )


@pytest.mark.usefixtures("google_auth_mock")
class TestPredefinedMetricHandler:
    """Unit tests for the PredefinedMetricHandler class."""

    def test_eval_case_to_agent_data(self):
        tool = genai_types.Tool(
            function_declarations=[
                genai_types.FunctionDeclaration(
                    name="get_weather",
                    description="Get weather in a location",
                    parameters={
                        "type": "object",
                        "properties": {"location": {"type": "string"}},
                    },
                )
            ]
        )
        agent_info = vertexai_genai_types.evals.AgentInfo(
            name="agent_system",
            agents={
                "agent1": vertexai_genai_types.evals.AgentConfig(
                    agent_id="agent1",
                    instruction="instruction1",
                    tools=[tool],
                )
            },
        )
        intermediate_events = [
            vertexai_genai_types.evals.Event(
                event_id="event1",
                content=genai_types.Content(
                    parts=[genai_types.Part(text="intermediate event")]
                ),
                author="agent1",
            )
        ]
        eval_case = vertexai_genai_types.EvalCase(
            prompt=genai_types.Content(parts=[genai_types.Part(text="Hello")]),
            responses=[
                vertexai_genai_types.ResponseCandidate(
                    response=genai_types.Content(parts=[genai_types.Part(text="Hi")])
                )
            ],
            agent_info=agent_info,
            intermediate_events=intermediate_events,
        )

        agent_data = _evals_metric_handlers._eval_case_to_agent_data(
            eval_case,
            eval_case.prompt,
            eval_case.responses[0].response,
        )

        assert "agent1" in agent_data.agents
        assert agent_data.agents["agent1"].instruction == "instruction1"
        assert agent_data.agents["agent1"].tools == [tool]
        assert len(agent_data.turns[0].events) == 3
        assert (
            agent_data.turns[0].events[1].content.parts[0].text == "intermediate event"
        )

    def test_eval_case_to_agent_data_events_only(self):
        intermediate_events = [
            vertexai_genai_types.evals.Event(
                event_id="event1",
                content=genai_types.Content(
                    parts=[genai_types.Part(text="intermediate event")]
                ),
            )
        ]
        eval_case = vertexai_genai_types.EvalCase(
            prompt=genai_types.Content(parts=[genai_types.Part(text="Hello")]),
            responses=[
                vertexai_genai_types.ResponseCandidate(
                    response=genai_types.Content(parts=[genai_types.Part(text="Hi")])
                )
            ],
            agent_info=None,
            intermediate_events=intermediate_events,
        )

        agent_data = _evals_metric_handlers._eval_case_to_agent_data(eval_case)

        assert agent_data.agents is None
        assert (
            agent_data.turns[0].events[0].content.parts[0].text == "intermediate event"
        )

    def test_eval_case_to_agent_data_empty_event_content(self):
        intermediate_events = [
            vertexai_genai_types.evals.Event(
                event_id="event1",
                content=None,
            )
        ]
        eval_case = vertexai_genai_types.EvalCase(
            prompt=genai_types.Content(parts=[genai_types.Part(text="Hello")]),
            responses=[
                vertexai_genai_types.ResponseCandidate(
                    response=genai_types.Content(parts=[genai_types.Part(text="Hi")])
                )
            ],
            agent_info=None,
            intermediate_events=intermediate_events,
        )

        agent_data = _evals_metric_handlers._eval_case_to_agent_data(eval_case)

        assert agent_data.agents is None
        assert agent_data.turns[0].events[0].content is None

    def test_eval_case_to_agent_data_empty_intermediate_events_list(self):
        agent_info = vertexai_genai_types.evals.AgentInfo(
            name="agent_system",
            agents={
                "agent1": vertexai_genai_types.evals.AgentConfig(
                    agent_id="agent1",
                    instruction="instruction1",
                    tools=[],
                )
            },
        )

        eval_case = vertexai_genai_types.EvalCase(
            prompt=genai_types.Content(parts=[genai_types.Part(text="Hello")]),
            responses=[
                vertexai_genai_types.ResponseCandidate(
                    response=genai_types.Content(parts=[genai_types.Part(text="Hi")])
                )
            ],
            agent_info=agent_info,
        )

        agent_data = _evals_metric_handlers._eval_case_to_agent_data(
            eval_case,
            eval_case.prompt,
            eval_case.responses[0].response,
        )

        assert len(agent_data.turns[0].events) == 2

    def test_eval_case_to_agent_data_agent_info_empty_tools(self):
        agent_info = vertexai_genai_types.evals.AgentInfo(
            name="agent_system",
            agents={
                "agent1": vertexai_genai_types.evals.AgentConfig(
                    agent_id="agent1",
                    instruction="instruction1",
                    tools=[],
                )
            },
        )
        eval_case = vertexai_genai_types.EvalCase(
            prompt=genai_types.Content(parts=[genai_types.Part(text="Hello")]),
            responses=[
                vertexai_genai_types.ResponseCandidate(
                    response=genai_types.Content(parts=[genai_types.Part(text="Hi")])
                )
            ],
            agent_info=agent_info,
            intermediate_events=None,
        )

        agent_data = _evals_metric_handlers._eval_case_to_agent_data(
            eval_case,
            eval_case.prompt,
            eval_case.responses[0].response,
        )

        assert agent_data.agents["agent1"].instruction == "instruction1"
        assert not agent_data.agents["agent1"].tools

    def test_eval_case_to_agent_data_agent_info_empty(self):
        intermediate_events = [
            vertexai_genai_types.Event(
                event_id="event1",
                content=genai_types.Content(
                    parts=[genai_types.Part(text="intermediate event")]
                ),
            )
        ]
        eval_case = vertexai_genai_types.EvalCase(
            prompt=genai_types.Content(parts=[genai_types.Part(text="Hello")]),
            responses=[
                vertexai_genai_types.ResponseCandidate(
                    response=genai_types.Content(parts=[genai_types.Part(text="Hi")])
                )
            ],
            agent_info=None,
            intermediate_events=intermediate_events,
        )

        agent_data = _evals_metric_handlers._eval_case_to_agent_data(
            eval_case,
            eval_case.prompt,
            eval_case.responses[0].response,
        )

        assert agent_data.agents is None

    @mock.patch.object(_evals_metric_handlers.logger, "warning")
    def test_tool_use_quality_metric_no_tool_call_logs_warning(
        self, mock_warning, mock_api_client_fixture
    ):
        """Tests that PredefinedMetricHandler warns for tool_use_quality_v1 if no tool call."""
        metric = vertexai_genai_types.Metric(name="tool_use_quality_v1")
        handler = _evals_metric_handlers.PredefinedMetricHandler(
            module=evals.Evals(api_client_=mock_api_client_fixture), metric=metric
        )
        eval_case = vertexai_genai_types.EvalCase(
            eval_case_id="case-no-tool-call",
            prompt=genai_types.Content(parts=[genai_types.Part(text="Hello")]),
            responses=[
                vertexai_genai_types.ResponseCandidate(
                    response=genai_types.Content(parts=[genai_types.Part(text="Hi")])
                )
            ],
            intermediate_events=[
                vertexai_genai_types.evals.Event(
                    event_id="event1",
                    content=genai_types.Content(
                        parts=[genai_types.Part(text="intermediate event")]
                    ),
                )
            ],
        )
        handler._build_request_payload(eval_case, response_index=0)
        mock_warning.assert_called_once_with(
            "Metric 'tool_use_quality_v1' requires tool usage in "
            "'intermediate_events' or 'agent_data', but no tool usage was found for case %s.",
            "case-no-tool-call",
        )

    @mock.patch.object(_evals_metric_handlers.logger, "warning")
    def test_build_request_payload_tool_use_quality_v1_with_agent_data_tool_call(
        self, mock_warning, mock_api_client_fixture
    ):
        """Tests that PredefinedMetricHandler does not warn if tool call is in agent_data."""
        metric = vertexai_genai_types.Metric(name="tool_use_quality_v1")
        handler = _evals_metric_handlers.PredefinedMetricHandler(
            module=evals.Evals(api_client_=mock_api_client_fixture), metric=metric
        )
        eval_case = vertexai_genai_types.EvalCase(
            eval_case_id="case-with-agent-data-tool-call",
            prompt=genai_types.Content(parts=[genai_types.Part(text="Hello")]),
            responses=[
                vertexai_genai_types.ResponseCandidate(
                    response=genai_types.Content(parts=[genai_types.Part(text="Hi")])
                )
            ],
            agent_data=vertexai_genai_types.evals.AgentData(
                turns=[
                    vertexai_genai_types.evals.ConversationTurn(
                        turn_index=0,
                        turn_id="turn_0",
                        events=[
                            vertexai_genai_types.evals.AgentEvent(
                                author="model",
                                content=genai_types.Content(
                                    parts=[
                                        genai_types.Part(
                                            function_call=genai_types.FunctionCall(
                                                name="search", args={}
                                            )
                                        )
                                    ]
                                ),
                            )
                        ],
                    )
                ]
            ),
        )
        handler._build_request_payload(eval_case, response_index=0)
        mock_warning.assert_not_called()


@pytest.mark.usefixtures("google_auth_mock")
class TestRunAdkUserSimulation:
    """Unit tests for the _run_adk_user_simulation function."""

    @mock.patch("vertexai._genai._evals_common.ADK_SessionInput")  # fmt: skip
    @mock.patch("vertexai._genai._evals_common.EvaluationGenerator")  # fmt: skip
    @mock.patch("vertexai._genai._evals_common.LlmBackedUserSimulator")  # fmt: skip
    @mock.patch("vertexai._genai._evals_common.ConversationScenario")  # fmt: skip
    @mock.patch("vertexai._genai._evals_common.LlmBackedUserSimulatorConfig")  # fmt: skip
    @pytest.mark.asyncio
    async def test_run_adk_user_simulation_success(
        self,
        mock_config_cls,
        mock_scenario_cls,
        mock_simulator_cls,
        mock_generator_cls,
        mock_session_input_cls,
    ):
        row = pd.Series(
            {
                "starting_prompt": "start",
                "conversation_plan": "plan",
                "session_inputs": json.dumps({"user_id": "u1"}),
            }
        )
        mock_agent = mock.Mock()
        mock_invocation = mock.Mock()
        mock_invocation.user_content.model_dump.return_value = {"text": "user msg"}
        mock_invocation.final_response.model_dump.return_value = {"text": "agent msg"}
        mock_invocation.intermediate_data = None
        mock_invocation.creation_timestamp = 12345
        mock_invocation.invocation_id = "turn1"

        mock_generator_cls._generate_inferences_from_root_agent = mock.AsyncMock(
            return_value=[mock_invocation]
        )

        turns = await _evals_common._run_adk_user_simulation(row, mock_agent)

        assert len(turns) == 1
        turn = turns[0]
        assert turn["turn_index"] == 0
        assert turn["turn_id"] == "turn1"
        assert len(turn["events"]) == 2
        assert turn["events"][0]["author"] == "user"
        assert turn["events"][0]["content"] == {"text": "user msg"}
        assert turn["events"][1]["author"] == "agent"
        assert turn["events"][1]["content"] == {"text": "agent msg"}

        mock_scenario_cls.assert_called_once_with(
            starting_prompt="start",
            conversation_plan="plan",
            user_persona="EVALUATOR",
        )
        mock_session_input_cls.assert_called_once()

    @mock.patch("vertexai._genai._evals_common.ADK_SessionInput")  # fmt: skip
    @mock.patch("vertexai._genai._evals_common.EvaluationGenerator")  # fmt: skip
    @mock.patch("vertexai._genai._evals_common.LlmBackedUserSimulator")  # fmt: skip
    @mock.patch("vertexai._genai._evals_common.ConversationScenario")  # fmt: skip
    @mock.patch("vertexai._genai._evals_common.LlmBackedUserSimulatorConfig")  # fmt: skip
    @pytest.mark.asyncio
    async def test_run_adk_user_simulation_missing_columns(
        self,
        mock_config_cls,
        mock_scenario_cls,
        mock_simulator_cls,
        mock_generator_cls,
        mock_session_input_cls,
    ):
        row = pd.Series({"conversation_plan": "plan"})
        mock_agent = mock.Mock()

        with pytest.raises(ValueError, match="User simulation requires"):
            await _evals_common._run_adk_user_simulation(row, mock_agent)

    @mock.patch("vertexai._genai._evals_common.ADK_SessionInput")  # fmt: skip
    @mock.patch("vertexai._genai._evals_common.EvaluationGenerator")  # fmt: skip
    @mock.patch("vertexai._genai._evals_common.LlmBackedUserSimulator")  # fmt: skip
    @mock.patch("vertexai._genai._evals_common.ConversationScenario")  # fmt: skip
    @mock.patch("vertexai._genai._evals_common.LlmBackedUserSimulatorConfig")  # fmt: skip
    @pytest.mark.asyncio
    async def test_run_adk_user_simulation_missing_session_inputs(
        self,
        mock_config_cls,
        mock_scenario_cls,
        mock_simulator_cls,
        mock_generator_cls,
        mock_session_input_cls,
    ):
        row = pd.Series(
            {
                "starting_prompt": "start",
                "conversation_plan": "plan",
            }
        )
        mock_agent = mock.Mock()
        mock_invocation = mock.Mock()
        mock_invocation.user_content.model_dump.return_value = {"text": "user msg"}
        mock_invocation.final_response.model_dump.return_value = {"text": "agent msg"}
        mock_invocation.intermediate_data = None
        mock_invocation.creation_timestamp = 12345
        mock_invocation.invocation_id = "turn1"

        mock_generator_cls._generate_inferences_from_root_agent = mock.AsyncMock(
            return_value=[mock_invocation]
        )

        await _evals_common._run_adk_user_simulation(row, mock_agent)

        mock_scenario_cls.assert_called_once_with(
            starting_prompt="start",
            conversation_plan="plan",
            user_persona="EVALUATOR",
        )
        mock_session_input_cls.assert_called_once_with(
            app_name="user_simulation_app",
            user_id="user_simulation_default_user",
            state={},
        )

    def test_merge_with_invalid_prompt_type(self):
        raw_dataset_1 = [
            {
                "prompt": 123,
                "response": "Response 1a",
            },
        ]
        with pytest.raises(
            ValueError,
            match="Invalid prompt type for case 0",
        ):
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                raw_datasets=[raw_dataset_1],
                schemas=[_evals_data_converters.EvalDatasetSchema.FLATTEN],
            )

    def test_merge_with_invalid_response_type(self):
        raw_dataset_1 = [
            {
                "prompt": "Prompt 1",
                "response": 123,
            },
        ]
        with pytest.raises(
            ValueError,
            match="Invalid response type",
        ):
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                raw_datasets=[raw_dataset_1],
                schemas=[_evals_data_converters.EvalDatasetSchema.FLATTEN],
            )

    def test_merge_with_missing_prompt(self):
        raw_dataset_1 = [
            {
                "response": "Response 1a",
            },
        ]
        with pytest.raises(
            ValueError,
            match="Prompt is required but missing for eval_case_0",
        ):
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                raw_datasets=[raw_dataset_1],
                schemas=[_evals_data_converters.EvalDatasetSchema.FLATTEN],
            )

    def test_merge_with_missing_response(self):
        raw_dataset_1 = [
            {
                "prompt": "Prompt 1",
            },
        ]
        with pytest.raises(
            ValueError,
            match="Response is required but missing for eval_case_0",
        ):
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                raw_datasets=[raw_dataset_1],
                schemas=[_evals_data_converters.EvalDatasetSchema.FLATTEN],
            )


@pytest.mark.usefixtures("google_auth_mock")
class TestAutoDetectDatasetSchema:
    def test_auto_detect_gemini_schema(self):
        raw_data = [
            {
                "request": {
                    "contents": [{"role": "user", "parts": [{"text": "Hello"}]}]
                },
                "response": {
                    "candidates": [
                        {"content": {"role": "model", "parts": [{"text": "Hi"}]}}
                    ]
                },
            }
        ]
        assert (
            _evals_data_converters.auto_detect_dataset_schema(raw_data)
            == _evals_data_converters.EvalDatasetSchema.GEMINI
        )

    def test_auto_detect_flatten_schema(self):
        raw_data = [{"prompt": "Hello", "response": "Hi"}]
        assert (
            _evals_data_converters.auto_detect_dataset_schema(raw_data)
            == _evals_data_converters.EvalDatasetSchema.FLATTEN
        )

    def test_auto_detect_openai_schema(self):
        raw_data = [
            {
                "request": {"messages": [{"role": "user", "content": "Hello"}]},
                "response": {
                    "choices": [{"message": {"role": "assistant", "content": "Hi"}}]
                },
            }
        ]
        assert (
            _evals_data_converters.auto_detect_dataset_schema(raw_data)
            == _evals_data_converters.EvalDatasetSchema.OPENAI
        )

    def test_auto_detect_observability_schema(self):
        raw_data = [
            {
                "format": "observability",
                "request": json.dumps(
                    {"role": "user", "parts": [{"content": "Hello", "type": "text"}]}
                ),
                "response": json.dumps(
                    {
                        "role": "system",
                        "parts": [{"content": "Hi", "type": "text"}],
                    }
                ),
            }
        ]
        assert (
            _evals_data_converters.auto_detect_dataset_schema(raw_data)
            == _evals_data_converters.EvalDatasetSchema.OBSERVABILITY
        )

    def test_auto_detect_unknown_schema(self):
        raw_data = [{"foo": "bar"}]
        assert (
            _evals_data_converters.auto_detect_dataset_schema(raw_data)
            == _evals_data_converters.EvalDatasetSchema.UNKNOWN
        )

    def test_auto_detect_empty_dataset(self):
        assert (
            _evals_data_converters.auto_detect_dataset_schema([])
            == _evals_data_converters.EvalDatasetSchema.UNKNOWN
        )


class TestEvalsRunEvaluation:
    """Unit tests for the evaluate method."""

    def test_execute_evaluation_computation_metric(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        dataset_df = pd.DataFrame(
            [
                {
                    "prompt": "Test prompt",
                    "response": "Test response",
                    "reference": "Test reference",
                }
            ]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )
        computation_metric = vertexai_genai_types.Metric(name="exact_match")

        result = _evals_common._execute_evaluation(
            api_client=mock_api_client_fixture,
            dataset=input_dataset,
            metrics=[computation_metric],
        )

        assert isinstance(result, vertexai_genai_types.EvaluationResult)
        assert result.evaluation_dataset == [input_dataset]
        assert len(result.summary_metrics) == 1
        summary_metric = result.summary_metrics[0]
        assert summary_metric.metric_name == "exact_match"
        assert summary_metric.mean_score == 1.0
        assert summary_metric.num_cases_total == 1
        assert summary_metric.num_cases_valid == 1
        assert len(result.eval_case_results) == 1
        case_result = result.eval_case_results[0]
        assert case_result.eval_case_index == 0
        assert len(case_result.response_candidate_results) == 1
        candidate_result = case_result.response_candidate_results[0]
        assert candidate_result.metric_results["exact_match"].score == 1.0

        mock_eval_dependencies["mock_evaluate_instances"].assert_called_once()
        call_args = mock_eval_dependencies["mock_evaluate_instances"].call_args
        assert "exact_match_input" in call_args[1]["metric_config"]

    def test_execute_evaluation_with_agent_info(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        dataset_df = pd.DataFrame(
            [
                {
                    "prompt": "Test prompt",
                    "response": "Test response",
                    "reference": "Test reference",
                }
            ]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )
        predefined_metric = genai_types.PredefinedMetricSpec(
            metric_spec_name="tool_search_validity"
        )
        tool = {
            "function_declarations": [
                {
                    "name": "get_weather",
                    "description": "Get weather in a location",
                    "parameters": {
                        "type": "object",
                        "properties": {"location": {"type": "string"}},
                    },
                }
            ]
        }
        agent_info = {
            "name": "agent_system",
            "agents": {
                "agent1": {
                    "agent_id": "agent1",
                    "instruction": "instruction1",
                    "description": "description1",
                    "tools": [tool],
                }
            },
        }

        result = _evals_common._execute_evaluation(
            api_client=mock_api_client_fixture,
            dataset=input_dataset,
            metrics=[predefined_metric],
            agent_info=agent_info,
        )

        assert isinstance(result, vertexai_genai_types.EvaluationResult)
        assert len(result.eval_case_results) == 1
        assert result.agent_info.name == "agent_system"
        assert "agent1" in result.agent_info.agents
        assert result.agent_info.agents["agent1"].instruction == "instruction1"
        assert result.agent_info.agents["agent1"].tools == [
            genai_types.Tool(
                function_declarations=[
                    genai_types.FunctionDeclaration(
                        name="get_weather",
                        description="Get weather in a location",
                        parameters={
                            "type": "object",
                            "properties": {"location": {"type": "string"}},
                        },
                    )
                ]
            )
        ]

    def test_execute_evaluation_translation_metric(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        dataset_df = pd.DataFrame(
            [
                {
                    "prompt": "src lang",
                    "response": "tgt lang",
                    "reference": "ref lang",
                }
            ]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )
        translation_metric = vertexai_genai_types.Metric(name="comet")

        result = _evals_common._execute_evaluation(
            api_client=mock_api_client_fixture,
            dataset=input_dataset,
            metrics=[translation_metric],
        )
        assert isinstance(result, vertexai_genai_types.EvaluationResult)
        assert result.evaluation_dataset == [input_dataset]
        assert len(result.summary_metrics) == 1
        summary_metric = result.summary_metrics[0]
        assert summary_metric.metric_name == "comet"
        assert summary_metric.mean_score == 0.75
        mock_eval_dependencies["mock_evaluate_instances"].assert_called_once()
        call_args = mock_eval_dependencies["mock_evaluate_instances"].call_args
        assert "comet_input" in call_args[1]["metric_config"]

    def test_execute_evaluation_llm_metric(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        dataset_df = pd.DataFrame(
            [{"prompt": "Test prompt", "response": "Test response"}]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )
        llm_metric = vertexai_genai_types.LLMMetric(
            name="text_quality", prompt_template="Evaluate: {response}"
        )

        with mock.patch(
            "vertexai._genai.evals.Evals._evaluate_instances"
        ) as mock_evaluate_instances_unified:
            mock_evaluate_instances_unified.return_value = (
                vertexai_genai_types.EvaluateInstancesResponse(
                    metric_results=[
                        vertexai_genai_types.MetricResult(
                            score=0.9,
                            explanation="Mocked LLM explanation",
                            error=None,
                            rubric_verdicts=[],
                        )
                    ]
                )
            )

            result = _evals_common._execute_evaluation(
                api_client=mock_api_client_fixture,
                dataset=input_dataset,
                metrics=[llm_metric],
            )
            assert isinstance(result, vertexai_genai_types.EvaluationResult)
            assert result.evaluation_dataset == [input_dataset]
            assert len(result.summary_metrics) == 1
            summary_metric = result.summary_metrics[0]
            assert summary_metric.metric_name == "text_quality"
            assert summary_metric.mean_score == 0.9
            case_result = result.eval_case_results[0]
            candidate_result = case_result.response_candidate_results[0]
            assert (
                candidate_result.metric_results["text_quality"].explanation
                == "Mocked LLM explanation"
            )

            mock_evaluate_instances_unified.assert_called_once()
            mock_eval_dependencies["mock_evaluate_instances"].assert_not_called()

    def test_execute_evaluation_hallucination_metric(self, mock_api_client_fixture):
        dataset_df = pd.DataFrame(
            [{"prompt": "Test prompt", "response": "Test response"}]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )

        result = _evals_common._execute_evaluation(
            api_client=mock_api_client_fixture,
            dataset=input_dataset,
            metrics=[
                vertexai_genai_types.RubricMetric.HALLUCINATION,
                vertexai_genai_types.RubricMetric.TOOL_USE_QUALITY,
            ],
        )
        assert isinstance(result, vertexai_genai_types.EvaluationResult)
        assert result.evaluation_dataset == [input_dataset]
        assert len(result.summary_metrics) == 2
        assert result.summary_metrics[0].metric_name == "hallucination_v1"
        assert result.summary_metrics[1].metric_name == "tool_use_quality_v1"

    @mock.patch.object(_evals_data_converters, "get_dataset_converter")
    def test_execute_evaluation_with_openai_schema(
        self,
        mock_get_converter,
        mock_api_client_fixture,
        mock_eval_dependencies,
    ):
        mock_openai_raw_data = [
            {
                "request": {"messages": [{"role": "user", "content": "OpenAI Prompt"}]},
                "response": {
                    "choices": [
                        {
                            "message": {
                                "index": 0,
                                "message": {
                                    "role": "assistant",
                                    "content": "OpenAI Response",
                                    "refusal": None,
                                    "annotations": [],
                                },
                                "logprobs": None,
                                "finish_reason": "stop",
                            }
                        }
                    ]
                },
            }
        ]
        converted_eval_case = vertexai_genai_types.EvalCase(
            prompt=genai_types.Content(
                parts=[genai_types.Part(text="OpenAI Prompt")], role="user"
            ),
            responses=[
                vertexai_genai_types.ResponseCandidate(
                    response=genai_types.Content(
                        parts=[genai_types.Part(text="Candidate Response")]
                    )
                )
            ],
        )
        mock_converted_dataset = vertexai_genai_types.EvaluationDataset(
            eval_cases=[converted_eval_case]
        )

        mock_converter_instance = mock.Mock(
            spec=_evals_data_converters._OpenAIDataConverter
        )
        mock_converter_instance.convert.return_value = mock_converted_dataset
        mock_get_converter.return_value = mock_converter_instance

        input_dataset_for_loader = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=pd.DataFrame(mock_openai_raw_data)
        )
        llm_metric = vertexai_genai_types.LLMMetric(
            name="test_metric", prompt_template="Evaluate: {response}"
        )

        with mock.patch.object(_evals_utils, "EvalDatasetLoader") as mock_loader_class:
            mock_loader_instance = mock_loader_class.return_value
            mock_loader_instance.load.return_value = mock_openai_raw_data

            with mock.patch.object(
                _evals_metric_handlers.LLMMetricHandler, "get_metric_result"
            ) as mock_llm_process:
                mock_llm_process.return_value = (
                    vertexai_genai_types.EvalCaseMetricResult(
                        metric_name="test_metric", score=0.75
                    )
                )

                result = _evals_common._execute_evaluation(
                    api_client=mock_api_client_fixture,
                    dataset=input_dataset_for_loader,
                    metrics=[llm_metric],
                    dataset_schema="OPENAI",
                )

        mock_loader_instance.load.assert_called_once_with(
            input_dataset_for_loader.eval_dataset_df
        )
        mock_get_converter.assert_called_with(
            _evals_data_converters.EvalDatasetSchema.OPENAI
        )
        mock_converter_instance.convert.assert_called_once_with(mock_openai_raw_data)

        assert isinstance(result, vertexai_genai_types.EvaluationResult)
        assert len(result.summary_metrics) == 1
        summary_metric = result.summary_metrics[0]
        assert summary_metric.metric_name == "test_metric"
        assert summary_metric.mean_score == 0.75

    def test_execute_evaluation_custom_metric(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        dataset_df = pd.DataFrame(
            [{"prompt": "Test prompt", "response": "Test response"}]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )

        def my_custom_metric_fn(data: dict):
            return 0.5

        custom_metric = vertexai_genai_types.Metric(
            name="my_custom", custom_function=my_custom_metric_fn
        )

        result = _evals_common._execute_evaluation(
            api_client=mock_api_client_fixture,
            dataset=input_dataset,
            metrics=[custom_metric],
        )
        assert isinstance(result, vertexai_genai_types.EvaluationResult)
        assert result.evaluation_dataset == [input_dataset]
        assert len(result.summary_metrics) == 1
        summary_metric = result.summary_metrics[0]
        assert summary_metric.metric_name == "my_custom"
        assert summary_metric.mean_score == 0.5
        mock_eval_dependencies["mock_evaluate_instances"].assert_not_called()

    def test_llm_metric_default_aggregation_mixed_results(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        dataset_df = pd.DataFrame(
            [
                {"prompt": "P1", "response": "R1"},
                {"prompt": "P2", "response": "R2"},
                {"prompt": "P3", "response": "R3"},
            ]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )
        llm_metric = vertexai_genai_types.LLMMetric(
            name="quality", prompt_template="Rate: {response}"
        )

        with mock.patch(
            "vertexai._genai._evals_metric_handlers.LLMMetricHandler.get_metric_result"
        ) as mock_llm_process:
            mock_llm_process.side_effect = [
                vertexai_genai_types.EvalCaseMetricResult(
                    metric_name="quality", score=0.8, explanation="Good"
                ),
                vertexai_genai_types.EvalCaseMetricResult(
                    metric_name="quality", score=0.6, explanation="Okay"
                ),
                vertexai_genai_types.EvalCaseMetricResult(
                    metric_name="quality", error_message="Processing failed"
                ),
            ]

            result = _evals_common._execute_evaluation(
                api_client=mock_api_client_fixture,
                dataset=input_dataset,
                metrics=[llm_metric],
            )

            assert mock_llm_process.call_count == 3
            assert result.evaluation_dataset == [input_dataset]
            assert len(result.summary_metrics) == 1
            summary = result.summary_metrics[0]
            assert summary.metric_name == "quality"
            assert summary.num_cases_total == 3
            assert summary.num_cases_valid == 2
            assert summary.num_cases_error == 1
            assert summary.mean_score == pytest.approx(0.7)
            assert summary.stdev_score == pytest.approx(statistics.stdev([0.8, 0.6]))

    def test_llm_metric_custom_aggregation_success(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        dataset_df = pd.DataFrame(
            [{"prompt": "P1", "response": "R1"}, {"prompt": "P2", "response": "R2"}]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )

        def custom_agg_fn(results: list[vertexai_genai_types.EvalCaseMetricResult]):
            return {
                "my_custom_stat": 123,
                "mean_score": 0.75,
                "num_cases_valid": len(results),
            }

        llm_metric = vertexai_genai_types.LLMMetric(
            name="custom_quality",
            prompt_template="Rate: {response}",
            aggregate_summary_fn=custom_agg_fn,
        )

        with mock.patch(
            "vertexai._genai._evals_metric_handlers.LLMMetricHandler.get_metric_result"
        ) as mock_llm_process:
            mock_llm_process.side_effect = [
                vertexai_genai_types.EvalCaseMetricResult(
                    metric_name="custom_quality", score=0.8
                ),
                vertexai_genai_types.EvalCaseMetricResult(
                    metric_name="custom_quality", score=0.7
                ),
            ]

            result = _evals_common._execute_evaluation(
                api_client=mock_api_client_fixture,
                dataset=input_dataset,
                metrics=[llm_metric],
            )
            assert mock_llm_process.call_count == 2
            assert result.evaluation_dataset == [input_dataset]
            assert len(result.summary_metrics) == 1
            summary = result.summary_metrics[0]
            assert summary.metric_name == "custom_quality"
            assert summary.num_cases_total == 2
            assert summary.num_cases_valid == 2
            assert summary.mean_score == 0.75
            assert summary.model_dump(exclude_none=True)["my_custom_stat"] == 123

    def test_llm_metric_custom_aggregation_error_fallback(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        dataset_df = pd.DataFrame(
            [{"prompt": "P1", "response": "R1"}, {"prompt": "P2", "response": "R2"}]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )

        def custom_agg_fn_error(
            results: list[vertexai_genai_types.EvalCaseMetricResult],
        ):
            raise ValueError("Custom aggregation failed")

        llm_metric = vertexai_genai_types.LLMMetric(
            name="error_fallback_quality",
            prompt_template="Rate: {response}",
            aggregate_summary_fn=custom_agg_fn_error,
        )
        with mock.patch(
            "vertexai._genai._evals_metric_handlers.LLMMetricHandler.get_metric_result"
        ) as mock_llm_process:
            mock_llm_process.side_effect = [
                vertexai_genai_types.EvalCaseMetricResult(
                    metric_name="error_fallback_quality", score=0.9
                ),
                vertexai_genai_types.EvalCaseMetricResult(
                    metric_name="error_fallback_quality", score=0.5
                ),
            ]
            result = _evals_common._execute_evaluation(
                api_client=mock_api_client_fixture,
                dataset=input_dataset,
                metrics=[llm_metric],
            )
            assert mock_llm_process.call_count == 2
            assert result.evaluation_dataset == [input_dataset]
            summary = result.summary_metrics[0]
            assert summary.metric_name == "error_fallback_quality"
            assert summary.num_cases_total == 2
            assert summary.num_cases_valid == 2
            assert summary.num_cases_error == 0
            assert summary.mean_score == pytest.approx(0.7)
            assert summary.stdev_score == pytest.approx(statistics.stdev([0.9, 0.5]))

    def test_llm_metric_custom_aggregation_invalid_return_type_fallback(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        dataset_df = pd.DataFrame([{"prompt": "P1", "response": "R1"}])
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )

        def custom_agg_fn_invalid_type(
            results: list[vertexai_genai_types.EvalCaseMetricResult],
        ):
            return "not a dict"

        llm_metric = vertexai_genai_types.LLMMetric(
            name="invalid_type_fallback",
            prompt_template="Rate: {response}",
            aggregate_summary_fn=custom_agg_fn_invalid_type,
        )
        with mock.patch(
            "vertexai._genai._evals_metric_handlers.LLMMetricHandler.get_metric_result"
        ) as mock_llm_process:
            mock_llm_process.return_value = vertexai_genai_types.EvalCaseMetricResult(
                metric_name="invalid_type_fallback", score=0.8
            )
            result = _evals_common._execute_evaluation(
                api_client=mock_api_client_fixture,
                dataset=input_dataset,
                metrics=[llm_metric],
            )
            assert result.evaluation_dataset == [input_dataset]
            summary = result.summary_metrics[0]
            assert summary.mean_score == 0.8
            assert summary.num_cases_valid == 1

    def test_execute_evaluation_lazy_loaded_prebuilt_metric_instance(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        dataset_df = pd.DataFrame(
            [{"prompt": "Test prompt", "response": "Test response"}]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )

        lazy_metric_instance = _evals_metric_loaders.LazyLoadedPrebuiltMetric(
            name="fluency", version="v1"
        )

        with mock.patch(
            "vertexai._genai.evals.Evals._evaluate_instances"
        ) as mock_evaluate_instances_unified:
            mock_evaluate_instances_unified.return_value = (
                vertexai_genai_types.EvaluateInstancesResponse(
                    metric_results=[
                        vertexai_genai_types.MetricResult(
                            score=0.9,
                            explanation="Mocked LLM explanation",
                            error=None,
                            rubric_verdicts=[],
                        )
                    ]
                )
            )

            result = _evals_common._execute_evaluation(
                api_client=mock_api_client_fixture,
                dataset=input_dataset,
                metrics=[lazy_metric_instance],
            )

            mock_eval_dependencies[
                "mock_fetch_prebuilt_metric"
            ].assert_called_once_with(mock_api_client_fixture)
            assert isinstance(result, vertexai_genai_types.EvaluationResult)
            assert result.evaluation_dataset == [input_dataset]
            assert len(result.summary_metrics) == 1
            summary_metric = result.summary_metrics[0]
            assert summary_metric.metric_name == "fluency"
            assert summary_metric.mean_score == 0.9

    def test_execute_evaluation_prebuilt_metric_via_loader(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        dataset_df = pd.DataFrame(
            [{"prompt": "Test prompt", "response": "Test response"}]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )

        prebuilt_metric = vertexai_genai_types.RubricMetric.FLUENCY

        with mock.patch(
            "vertexai._genai.evals.Evals._evaluate_instances"
        ) as mock_evaluate_instances_unified:
            mock_evaluate_instances_unified.return_value = (
                vertexai_genai_types.EvaluateInstancesResponse(
                    metric_results=[
                        vertexai_genai_types.MetricResult(
                            score=0.9,
                            explanation="Mocked LLM explanation",
                            error=None,
                            rubric_verdicts=[],
                        )
                    ]
                )
            )

            result = _evals_common._execute_evaluation(
                api_client=mock_api_client_fixture,
                dataset=input_dataset,
                metrics=[prebuilt_metric],
            )

            mock_eval_dependencies[
                "mock_fetch_prebuilt_metric"
            ].assert_called_once_with(mock_api_client_fixture)
            assert isinstance(result, vertexai_genai_types.EvaluationResult)
            assert result.evaluation_dataset == [input_dataset]
            assert len(result.summary_metrics) == 1
            summary_metric = result.summary_metrics[0]
            assert summary_metric.metric_name == "fluency"
            assert summary_metric.mean_score == 0.9

    def test_execute_evaluation_with_gcs_destination(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        dataset_df = pd.DataFrame(
            [
                {
                    "prompt": "Test prompt",
                    "response": "Test response",
                    "reference": "Test response",
                }
            ]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )
        metric = vertexai_genai_types.Metric(name="exact_match")
        gcs_dest = "gs://my-bucket/eval_results/"

        result = _evals_common._execute_evaluation(
            api_client=mock_api_client_fixture,
            dataset=input_dataset,
            metrics=[metric],
            dest=gcs_dest,
        )

        mock_eval_dependencies["mock_upload_to_gcs"].assert_called_once_with(
            data=result.model_dump(
                mode="json", exclude_none=True, exclude={"evaluation_dataset"}
            ),
            gcs_dest_prefix=gcs_dest,
            filename_prefix="evaluation_result",
        )

    def test_execute_evaluation_multiple_datasets(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        df1 = pd.DataFrame([{"prompt": "p1", "response": "r1a", "reference": "ref1"}])
        df2 = pd.DataFrame([{"prompt": "p1", "response": "r1b", "reference": "ref1"}])
        dataset1 = vertexai_genai_types.EvaluationDataset(eval_dataset_df=df1)
        dataset2 = vertexai_genai_types.EvaluationDataset(eval_dataset_df=df2)
        metric = vertexai_genai_types.Metric(name="exact_match")

        result = _evals_common._execute_evaluation(
            api_client=mock_api_client_fixture,
            dataset=[dataset1, dataset2],
            metrics=[metric],
        )

        assert isinstance(result, vertexai_genai_types.EvaluationResult)
        assert len(result.eval_case_results) == 1
        case_result = result.eval_case_results[0]
        assert len(case_result.response_candidate_results) == 2
        assert case_result.response_candidate_results[0].response_index == 0
        assert (
            case_result.response_candidate_results[0]
            .metric_results["exact_match"]
            .score
            == 1.0
        )
        assert case_result.response_candidate_results[1].response_index == 1
        assert (
            case_result.response_candidate_results[1]
            .metric_results["exact_match"]
            .score
            == 1.0
        )

        assert len(result.summary_metrics) == 1
        summary_metric = result.summary_metrics[0]
        assert summary_metric.metric_name == "exact_match"
        assert summary_metric.num_cases_total == 2
        assert summary_metric.mean_score == 1.0

        assert mock_eval_dependencies["mock_evaluate_instances"].call_count == 2

    def test_execute_evaluation_deduplicates_candidate_names(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        """Tests that duplicate candidate names are indexed."""
        dataset1 = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=pd.DataFrame(
                [{"prompt": "p1", "response": "r1", "reference": "ref1"}]
            ),
            candidate_name="gemini-pro",
        )
        dataset2 = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=pd.DataFrame(
                [{"prompt": "p1", "response": "r2", "reference": "ref1"}]
            ),
            candidate_name="gemini-flash",
        )
        dataset3 = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=pd.DataFrame(
                [{"prompt": "p1", "response": "r3", "reference": "ref1"}]
            ),
            candidate_name="gemini-pro",
        )

        mock_eval_dependencies["mock_evaluate_instances"].return_value = (
            vertexai_genai_types.EvaluateInstancesResponse(
                exact_match_results=vertexai_genai_types.ExactMatchResults(
                    exact_match_metric_values=[
                        genai_types.ExactMatchMetricValue(score=1.0)
                    ]
                )
            )
        )

        result = _evals_common._execute_evaluation(
            api_client=mock_api_client_fixture,
            dataset=[dataset1, dataset2, dataset3],
            metrics=[vertexai_genai_types.Metric(name="exact_match")],
        )

        assert result.metadata.candidate_names == [
            "gemini-pro #1",
            "gemini-flash",
            "gemini-pro #2",
        ]

    @mock.patch("vertexai._genai._evals_common.datetime")
    def test_execute_evaluation_adds_creation_timestamp(
        self, mock_datetime, mock_api_client_fixture, mock_eval_dependencies
    ):
        """Tests that creation_timestamp is added to the result metadata."""
        import datetime

        mock_now = datetime.datetime(
            2025, 6, 18, 12, 0, 0, tzinfo=datetime.timezone.utc
        )
        mock_datetime.datetime.now.return_value = mock_now

        dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=pd.DataFrame(
                [{"prompt": "p", "response": "r", "reference": "r"}]
            )
        )
        metric = vertexai_genai_types.Metric(name="exact_match")

        result = _evals_common._execute_evaluation(
            api_client=mock_api_client_fixture,
            dataset=dataset,
            metrics=[metric],
        )

        assert result.metadata is not None
        assert result.metadata.creation_timestamp == mock_now

    @mock.patch(
        "vertexai._genai._evals_metric_handlers._evals_constant.SUPPORTED_PREDEFINED_METRICS",
        frozenset(["summarization_quality"]),
    )
    @mock.patch("time.sleep", return_value=None)
    @mock.patch("vertexai._genai.evals.Evals._evaluate_instances")  # fmt: skip
    def test_predefined_metric_retry_on_resource_exhausted(
        self,
        mock_private_evaluate_instances,
        mock_sleep,
        mock_api_client_fixture,
    ):
        dataset_df = pd.DataFrame(
            [{"prompt": "Test prompt", "response": "Test response"}]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )
        metric = vertexai_genai_types.Metric(name="summarization_quality")
        metric_result = vertexai_genai_types.MetricResult(
            score=0.9,
            explanation="Mocked predefined explanation",
            rubric_verdicts=[],
            error=None,
        )
        error_response_json = {
            "error": {
                "code": 429,
                "message": ("Judge model resource exhausted. Please try again later."),
                "status": "RESOURCE_EXHAUSTED",
            }
        }
        mock_private_evaluate_instances.side_effect = [
            genai_errors.ClientError(code=429, response_json=error_response_json),
            genai_errors.ClientError(code=429, response_json=error_response_json),
            vertexai_genai_types.EvaluateInstancesResponse(
                metric_results=[metric_result]
            ),
        ]

        result = _evals_common._execute_evaluation(
            api_client=mock_api_client_fixture,
            dataset=input_dataset,
            metrics=[metric],
        )

        assert mock_private_evaluate_instances.call_count == 3
        assert mock_sleep.call_count == 2
        assert len(result.summary_metrics) == 1
        summary_metric = result.summary_metrics[0]
        assert summary_metric.metric_name == "summarization_quality"
        assert summary_metric.mean_score == 0.9

    @mock.patch(
        "vertexai._genai._evals_metric_handlers._evals_constant.SUPPORTED_PREDEFINED_METRICS",
        frozenset(["summarization_quality"]),
    )
    @mock.patch("time.sleep", return_value=None)
    @mock.patch("vertexai._genai.evals.Evals._evaluate_instances")  # fmt: skip
    def test_predefined_metric_retry_fail_on_resource_exhausted(
        self,
        mock_private_evaluate_instances,
        mock_sleep,
        mock_api_client_fixture,
    ):
        dataset_df = pd.DataFrame(
            [{"prompt": "Test prompt", "response": "Test response"}]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )
        error_response_json = {
            "error": {
                "code": 429,
                "message": ("Judge model resource exhausted. Please try again later."),
                "status": "RESOURCE_EXHAUSTED",
            }
        }
        metric = vertexai_genai_types.Metric(name="summarization_quality")
        mock_private_evaluate_instances.side_effect = [
            genai_errors.ClientError(code=429, response_json=error_response_json),
            genai_errors.ClientError(code=429, response_json=error_response_json),
            genai_errors.ClientError(code=429, response_json=error_response_json),
            genai_errors.ClientError(code=429, response_json=error_response_json),
            genai_errors.ClientError(code=429, response_json=error_response_json),
        ]

        result = _evals_common._execute_evaluation(
            api_client=mock_api_client_fixture,
            dataset=input_dataset,
            metrics=[metric],
        )

        assert mock_private_evaluate_instances.call_count == 5
        assert mock_sleep.call_count == 4
        assert len(result.summary_metrics) == 1
        summary_metric = result.summary_metrics[0]
        assert summary_metric.metric_name == "summarization_quality"
        assert summary_metric.mean_score is None
        assert summary_metric.num_cases_error == 1


class TestEvaluationDataset:
    """Contains set of tests for the EvaluationDataset class methods."""

    @mock.patch.object(_gcs_utils, "GcsUtils")
    def test_load_from_observability_eval_cases(self, mock_gcs_utils):
        """Tests that load_from_observability_eval_cases reads data from GCS."""

        def read_file_contents_side_effect(src: str) -> str:
            if src == "gs://project/input.json":
                return "input"
            elif src == "gs://project/output.json":
                return "output"
            elif src == "gs://project/system_instruction.json":
                return "system_instruction"
            else:
                return ""

        mock_gcs_utils.return_value.read_file_contents.side_effect = (
            read_file_contents_side_effect
        )

        eval_cases = [
            vertexai_genai_types.ObservabilityEvalCase(
                input_src="gs://project/input.json",
                output_src="gs://project/output.json",
                system_instruction_src="gs://project/system_instruction.json",
            )
        ]
        result = (
            vertexai_genai_types.EvaluationDataset.load_from_observability_eval_cases(
                eval_cases
            )
        )

        mock_gcs_utils.return_value.read_file_contents.assert_has_calls(
            [
                mock.call("gs://project/input.json"),
                mock.call("gs://project/output.json"),
                mock.call("gs://project/system_instruction.json"),
            ],
            any_order=True,
        )
        assert result.eval_dataset_df is not None
        pd.testing.assert_frame_equal(
            result.eval_dataset_df,
            pd.DataFrame(
                {
                    "format": ["observability"],
                    "request": ["input"],
                    "response": ["output"],
                    "system_instruction": ["system_instruction"],
                }
            ),
        )

    @mock.patch.object(_gcs_utils, "GcsUtils")
    def test_load_from_observability_eval_cases_no_system_instruction(
        self, mock_gcs_utils
    ):
        """Tests load_from_observability_eval_cases works without system_instruction."""

        def read_file_contents_side_effect(src: str) -> str:
            if src == "gs://project/input.json":
                return "input"
            elif src == "gs://project/output.json":
                return "output"
            elif src == "gs://project/system_instruction.json":
                return "system_instruction"
            else:
                return ""

        mock_gcs_utils.return_value.read_file_contents.side_effect = (
            read_file_contents_side_effect
        )

        eval_cases = [
            vertexai_genai_types.ObservabilityEvalCase(
                input_src="gs://project/input.json",
                output_src="gs://project/output.json",
            )
        ]
        result = (
            vertexai_genai_types.EvaluationDataset.load_from_observability_eval_cases(
                eval_cases
            )
        )

        mock_gcs_utils.return_value.read_file_contents.assert_has_calls(
            [
                mock.call("gs://project/input.json"),
                mock.call("gs://project/output.json"),
            ],
            any_order=True,
        )
        assert result.eval_dataset_df is not None
        pd.testing.assert_frame_equal(
            result.eval_dataset_df,
            pd.DataFrame(
                {
                    "format": ["observability"],
                    "request": ["input"],
                    "response": ["output"],
                    "system_instruction": [""],
                }
            ),
        )

    @mock.patch.object(_gcs_utils, "GcsUtils")
    def test_load_from_observability_eval_cases_multiple_cases(self, mock_gcs_utils):
        """Test load_from_observability_eval_cases can handle multiple cases."""

        def read_file_contents_side_effect(src: str) -> str:
            if src == "gs://project/input_1.json":
                return "input_1"
            elif src == "gs://project/input_2.json":
                return "input_2"
            elif src == "gs://project/output_1.json":
                return "output_1"
            elif src == "gs://project/output_2.json":
                return "output_2"
            elif src == "gs://project/system_instruction_1.json":
                return "system_instruction_1"
            elif src == "gs://project/system_instruction_2.json":
                return "system_instruction_2"
            else:
                return ""

        mock_gcs_utils.return_value.read_file_contents.side_effect = (
            read_file_contents_side_effect
        )

        eval_cases = [
            vertexai_genai_types.ObservabilityEvalCase(
                input_src="gs://project/input_1.json",
                output_src="gs://project/output_1.json",
                system_instruction_src="gs://project/system_instruction_1.json",
            ),
            vertexai_genai_types.ObservabilityEvalCase(
                input_src="gs://project/input_2.json",
                output_src="gs://project/output_2.json",
                system_instruction_src="gs://project/system_instruction_2.json",
            ),
        ]
        result = (
            vertexai_genai_types.EvaluationDataset.load_from_observability_eval_cases(
                eval_cases
            )
        )

        assert result.eval_dataset_df is not None
        pd.testing.assert_frame_equal(
            result.eval_dataset_df,
            pd.DataFrame(
                {
                    "format": ["observability", "observability"],
                    "request": ["input_1", "input_2"],
                    "response": ["output_1", "output_2"],
                    "system_instruction": [
                        "system_instruction_1",
                        "system_instruction_2",
                    ],
                }
            ),
        )


class TestEvalsGenerateConversationScenarios(unittest.TestCase):
    """Unit tests for the Evals generate_conversation_scenarios method."""

    def setUp(self):
        self.addCleanup(mock.patch.stopall)
        self.mock_client = mock.MagicMock(spec=client.Client)
        self.mock_client.vertexai = True
        self.mock_api_client = mock.MagicMock()
        self.mock_client._api_client = self.mock_api_client

        self.mock_response = mock.MagicMock()
        self.mock_response.body = json.dumps(
            {
                "userScenarios": [
                    {"startingPrompt": "Prompt 1", "conversationPlan": "Plan 1"},
                    {"startingPrompt": "Prompt 2", "conversationPlan": "Plan 2"},
                ]
            }
        )
        self.mock_api_client.request.return_value = self.mock_response

    def test_generate_conversation_scenarios(self):
        """Tests that generate_conversation_scenarios correctly calls the API and parses the response."""
        evals_module = evals.Evals(api_client_=self.mock_api_client)

        eval_dataset = evals_module.generate_conversation_scenarios(
            agent_info=vertexai_genai_types.evals.AgentInfo(
                agents={"agent_1": {}},
                root_agent_id="agent_1",
            ),
            config={"count": 2},
        )
        assert isinstance(eval_dataset, vertexai_genai_types.EvaluationDataset)
        assert len(eval_dataset.eval_cases) == 2
        assert eval_dataset.eval_cases[0].user_scenario.starting_prompt == "Prompt 1"
        assert eval_dataset.eval_cases[0].user_scenario.conversation_plan == "Plan 1"
        assert eval_dataset.eval_cases[1].user_scenario.starting_prompt == "Prompt 2"
        assert eval_dataset.eval_cases[1].user_scenario.conversation_plan == "Plan 2"

        assert eval_dataset.eval_dataset_df is not None
        assert len(eval_dataset.eval_dataset_df) == 2
        assert eval_dataset.eval_dataset_df.iloc[0]["starting_prompt"] == "Prompt 1"
        assert eval_dataset.eval_dataset_df.iloc[0]["conversation_plan"] == "Plan 1"
        assert eval_dataset.eval_dataset_df.iloc[1]["starting_prompt"] == "Prompt 2"
        assert eval_dataset.eval_dataset_df.iloc[1]["conversation_plan"] == "Plan 2"

        self.mock_api_client.request.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_generate_conversation_scenarios(self):
        """Tests that async generate_conversation_scenarios correctly calls the API and parses the response."""

        self.mock_api_client.async_request = mock.AsyncMock(
            return_value=self.mock_response
        )
        async_evals_module = evals.AsyncEvals(api_client_=self.mock_api_client)

        eval_dataset = await async_evals_module.generate_conversation_scenarios(
            agent_info=vertexai_genai_types.evals.AgentInfo(
                agents={"agent_1": {}},
                root_agent_id="agent_1",
            ),
            config={"count": 2},
        )
        assert isinstance(eval_dataset, vertexai_genai_types.EvaluationDataset)
        assert len(eval_dataset.eval_cases) == 2
        assert eval_dataset.eval_cases[0].user_scenario.starting_prompt == "Prompt 1"

        assert eval_dataset.eval_dataset_df is not None
        assert len(eval_dataset.eval_dataset_df) == 2
        assert eval_dataset.eval_dataset_df.iloc[0]["starting_prompt"] == "Prompt 1"
        assert eval_dataset.eval_dataset_df.iloc[0]["conversation_plan"] == "Plan 1"
        assert eval_dataset.eval_dataset_df.iloc[1]["starting_prompt"] == "Prompt 2"
        assert eval_dataset.eval_dataset_df.iloc[1]["conversation_plan"] == "Plan 2"

        self.mock_api_client.async_request.assert_called_once()


class TestTransformDataframe:
    """Unit tests for the _transform_dataframe function."""

    def test_transform_dataframe_drops_empty_columns(self):
        rows = [
            {
                "prompt": "test prompt",
                "reference": None,
                "intermediate_events": [],
                "agent_data": None,
                "candidate1": "test response",
            }
        ]
        eval_dfs = _evals_common._transform_dataframe(rows)
        assert len(eval_dfs) == 1
        df = eval_dfs[0].eval_dataset_df
        assert "prompt" in df.columns
        assert "response" in df.columns
        assert "reference" not in df.columns
        assert "intermediate_events" not in df.columns
        assert "agent_data" not in df.columns

    def test_transform_dataframe_drops_empty_prompt_and_response(self):
        rows = [
            {
                "prompt": None,
                "candidate1": None,
            }
        ]
        eval_dfs = _evals_common._transform_dataframe(rows)
        assert len(eval_dfs) == 1
        df = eval_dfs[0].eval_dataset_df
        assert "prompt" not in df.columns
        assert "response" not in df.columns


class TestConvertRequestToDatasetRow:
    """Unit tests for the _convert_request_to_dataset_row function."""

    def test_convert_request_to_dataset_row_with_prompt_and_golden(self):
        request = vertexai_genai_types.EvaluationItemRequest(
            prompt=vertexai_genai_types.EvaluationPrompt(text="test prompt"),
            golden_response=vertexai_genai_types.CandidateResponse(
                text="golden response"
            ),
        )
        result = _evals_common._convert_request_to_dataset_row(request)
        assert result["prompt"] == "test prompt"
        assert result["reference"] == vertexai_genai_types.CandidateResponse(
            text="golden response"
        )
        assert result["intermediate_events"] == []
        assert result["agent_data"] is None

    def test_convert_request_to_dataset_row_with_user_scenario(self):
        request = vertexai_genai_types.EvaluationItemRequest(
            prompt=vertexai_genai_types.EvaluationPrompt(
                user_scenario=vertexai_genai_types.evals.UserScenario(
                    starting_prompt="start prompt", conversation_plan="convo plan"
                )
            )
        )
        result = _evals_common._convert_request_to_dataset_row(request)
        assert result["starting_prompt"] == "start prompt"
        assert result["conversation_plan"] == "convo plan"
        assert result["prompt"] is None

    def test_convert_request_to_dataset_row_with_candidate_events(self):
        request = vertexai_genai_types.EvaluationItemRequest(
            candidate_responses=[
                vertexai_genai_types.CandidateResponse(
                    candidate="test-candidate",
                    text="candidate text",
                    events=[
                        genai_types.Content(
                            parts=[genai_types.Part(text="event part")], role="model"
                        )
                    ],
                )
            ]
        )
        result = _evals_common._convert_request_to_dataset_row(request)
        assert result["test-candidate"] == "candidate text"
        assert result["intermediate_events"] == [
            {
                "event_id": "test-candidate",
                "content": {
                    "parts": [genai_types.Part(text="event part")],
                    "role": "model",
                },
            }
        ]
        assert result["agent_data"] is None

    def test_convert_request_to_dataset_row_with_agent_data(self):
        mock_agent_data = {"turns": []}
        request = vertexai_genai_types.EvaluationItemRequest(
            candidate_responses=[
                vertexai_genai_types.CandidateResponse(
                    candidate="test-candidate", agent_data=mock_agent_data
                )
            ]
        )
        result = _evals_common._convert_request_to_dataset_row(request)
        assert result["test-candidate"] is None
        assert result["agent_data"]["turns"] == mock_agent_data["turns"]
        assert result["intermediate_events"] == []


class TestCreateEvaluationSetFromDataFrame:
    """Unit tests for the _create_evaluation_set_from_dataframe function."""

    def setup_method(self):
        self.mock_api_client = mock.Mock(spec=client.Client)
        self.mock_api_client.project = "test-project"
        self.mock_api_client.location = "us-central1"

    @mock.patch.object(_evals_common, "evals")
    @mock.patch.object(_evals_common, "_gcs_utils")
    def test_create_evaluation_set_with_intermediate_events(
        self, mock_gcs_utils, mock_evals_module
    ):
        intermediate_events = [
            {
                "content": {"parts": [{"text": "thought 1"}]},
                "timestamp": "2024-01-01T00:00:00Z",
            },
            {
                "content": {"parts": [{"functionCall": {"name": "foo"}}]},
                "timestamp": "2024-01-01T00:00:01Z",
            },
        ]

        eval_df = pd.DataFrame(
            [
                {
                    "prompt": "test prompt",
                    "response": "test response",
                    "intermediate_events": intermediate_events,
                }
            ]
        )

        mock_gcs_instance = mock_gcs_utils.GcsUtils.return_value
        mock_gcs_instance.upload_json_to_prefix.return_value = (
            "gs://bucket/path/request.json"
        )

        mock_evals_instance = mock_evals_module.Evals.return_value
        mock_eval_item = mock.Mock()
        mock_eval_item.name = "eval_item_1"
        mock_evals_instance.create_evaluation_item.return_value = mock_eval_item

        mock_eval_set = mock.Mock()
        mock_evals_instance.create_evaluation_set.return_value = mock_eval_set

        result = _evals_common._create_evaluation_set_from_dataframe(
            api_client=self.mock_api_client,
            gcs_dest_prefix="gs://bucket/prefix",
            eval_df=eval_df,
            candidate_name="test-candidate",
        )

        assert result == mock_eval_set

        mock_gcs_instance.upload_json_to_prefix.assert_called_once()
        call_args = mock_gcs_instance.upload_json_to_prefix.call_args
        uploaded_data = call_args.kwargs["data"]

        candidate_responses = uploaded_data["candidate_responses"]
        assert len(candidate_responses) == 1
        candidate_response = candidate_responses[0]
        assert candidate_response["candidate"] == "test-candidate"
        assert candidate_response["text"] == "test response"

        expected_events = [
            {"parts": [{"text": "thought 1"}]},
            {"parts": [{"function_call": {"name": "foo"}}]},
        ]
        assert candidate_response["events"] == expected_events

    @mock.patch.object(_evals_common, "evals")
    @mock.patch.object(_evals_common, "_gcs_utils")
    def test_create_evaluation_set_with_user_scenario(
        self, mock_gcs_utils, mock_evals_module
    ):
        eval_df = pd.DataFrame(
            [
                {
                    "starting_prompt": "test starting prompt",
                    "conversation_plan": "test conversation plan",
                }
            ]
        )

        mock_gcs_instance = mock_gcs_utils.GcsUtils.return_value
        mock_gcs_instance.upload_json_to_prefix.return_value = (
            "gs://bucket/path/request.json"
        )

        mock_evals_instance = mock_evals_module.Evals.return_value
        mock_eval_item = mock.Mock()
        mock_eval_item.name = "eval_item_1"
        mock_evals_instance.create_evaluation_item.return_value = mock_eval_item

        mock_eval_set = mock.Mock()
        mock_evals_instance.create_evaluation_set.return_value = mock_eval_set

        result = _evals_common._create_evaluation_set_from_dataframe(
            api_client=self.mock_api_client,
            gcs_dest_prefix="gs://bucket/prefix",
            eval_df=eval_df,
            candidate_name="test-candidate",
        )

        assert result == mock_eval_set

        mock_gcs_instance.upload_json_to_prefix.assert_called_once()
        call_args = mock_gcs_instance.upload_json_to_prefix.call_args
        uploaded_data = call_args.kwargs["data"]

        assert uploaded_data.get("candidate_responses") is None
        assert uploaded_data["prompt"]["user_scenario"] == {
            "starting_prompt": "test starting prompt",
            "conversation_plan": "test conversation plan",
        }

    @mock.patch.object(_evals_common, "evals")
    @mock.patch.object(_evals_common, "_gcs_utils")
    def test_create_evaluation_set_with_agent_data(
        self, mock_gcs_utils, mock_evals_module
    ):
        agent_data = {"turns": [{"turn_id": "turn1", "events": []}]}
        eval_df = pd.DataFrame(
            [
                {
                    "prompt": "test prompt",
                    "agent_data": agent_data,
                }
            ]
        )

        mock_gcs_instance = mock_gcs_utils.GcsUtils.return_value
        mock_gcs_instance.upload_json_to_prefix.return_value = (
            "gs://bucket/path/request.json"
        )

        mock_evals_instance = mock_evals_module.Evals.return_value
        mock_eval_item = mock.Mock()
        mock_eval_item.name = "eval_item_1"
        mock_evals_instance.create_evaluation_item.return_value = mock_eval_item

        mock_eval_set = mock.Mock()
        mock_evals_instance.create_evaluation_set.return_value = mock_eval_set

        result = _evals_common._create_evaluation_set_from_dataframe(
            api_client=self.mock_api_client,
            gcs_dest_prefix="gs://bucket/prefix",
            eval_df=eval_df,
            candidate_name="test-candidate",
        )

        assert result == mock_eval_set

        mock_gcs_instance.upload_json_to_prefix.assert_called_once()
        call_args = mock_gcs_instance.upload_json_to_prefix.call_args
        uploaded_data = call_args.kwargs["data"]

        assert uploaded_data["prompt"]["text"] == "test prompt"
        candidate_responses = uploaded_data["candidate_responses"]
        assert len(candidate_responses) == 1
        candidate_response = candidate_responses[0]
        assert candidate_response["candidate"] == "test-candidate"
        assert candidate_response["agent_data"] == agent_data

    @mock.patch.object(_evals_common, "evals")
    @mock.patch.object(_evals_common, "_gcs_utils")
    def test_create_evaluation_set_with_history_column(
        self, mock_gcs_utils, mock_evals_module
    ):
        """Tests that 'history' column is accepted and mapped to prompt_template_data."""
        eval_df = pd.DataFrame(
            [
                {
                    "prompt": "test prompt",
                    "response": "test response",
                    "history": "previous conversation",
                }
            ]
        )

        mock_gcs_instance = mock_gcs_utils.GcsUtils.return_value
        mock_gcs_instance.upload_json_to_prefix.return_value = (
            "gs://bucket/path/request.json"
        )

        mock_evals_instance = mock_evals_module.Evals.return_value
        mock_eval_item = mock.Mock()
        mock_eval_item.name = "eval_item_1"
        mock_evals_instance.create_evaluation_item.return_value = mock_eval_item

        mock_eval_set = mock.Mock()
        mock_evals_instance.create_evaluation_set.return_value = mock_eval_set

        result = _evals_common._create_evaluation_set_from_dataframe(
            api_client=self.mock_api_client,
            gcs_dest_prefix="gs://bucket/prefix",
            eval_df=eval_df,
            candidate_name="test-candidate",
        )

        assert result == mock_eval_set

        mock_gcs_instance.upload_json_to_prefix.assert_called_once()
        call_args = mock_gcs_instance.upload_json_to_prefix.call_args
        uploaded_data = call_args.kwargs["data"]

        assert "prompt_template_data" in uploaded_data["prompt"]
        ptd_values = uploaded_data["prompt"]["prompt_template_data"]["values"]
        assert "conversation_history" in ptd_values

    @mock.patch.object(_evals_common, "evals")
    @mock.patch.object(_evals_common, "_gcs_utils")
    def test_create_evaluation_set_with_conversation_history_column(
        self, mock_gcs_utils, mock_evals_module
    ):
        """Tests that 'conversation_history' column is accepted and mapped to prompt_template_data."""
        eval_df = pd.DataFrame(
            [
                {
                    "prompt": "test prompt",
                    "response": "test response",
                    "conversation_history": "previous conversation",
                }
            ]
        )

        mock_gcs_instance = mock_gcs_utils.GcsUtils.return_value
        mock_gcs_instance.upload_json_to_prefix.return_value = (
            "gs://bucket/path/request.json"
        )

        mock_evals_instance = mock_evals_module.Evals.return_value
        mock_eval_item = mock.Mock()
        mock_eval_item.name = "eval_item_1"
        mock_evals_instance.create_evaluation_item.return_value = mock_eval_item

        mock_eval_set = mock.Mock()
        mock_evals_instance.create_evaluation_set.return_value = mock_eval_set

        result = _evals_common._create_evaluation_set_from_dataframe(
            api_client=self.mock_api_client,
            gcs_dest_prefix="gs://bucket/prefix",
            eval_df=eval_df,
            candidate_name="test-candidate",
        )

        assert result == mock_eval_set

        mock_gcs_instance.upload_json_to_prefix.assert_called_once()
        call_args = mock_gcs_instance.upload_json_to_prefix.call_args
        uploaded_data = call_args.kwargs["data"]

        assert "prompt_template_data" in uploaded_data["prompt"]
        ptd_values = uploaded_data["prompt"]["prompt_template_data"]["values"]
        assert "conversation_history" in ptd_values


class TestResolveDataset:
    """Unit tests for the _resolve_dataset function."""

    def setup_method(self):
        self.mock_api_client = mock.Mock(spec=client.Client)
        self.mock_api_client.project = "test-project"
        self.mock_api_client.location = "us-central1"

    @mock.patch.object(_evals_common, "evals")
    @mock.patch.object(_evals_common, "_gcs_utils")
    def test_resolve_dataset_preserves_conversation_history(
        self, mock_gcs_utils, mock_evals_module
    ):
        """Tests that conversation_history from EvalCase is included in the DataFrame."""
        mock_gcs_instance = mock_gcs_utils.GcsUtils.return_value
        mock_gcs_instance.upload_json_to_prefix.return_value = (
            "gs://bucket/path/request.json"
        )

        mock_evals_instance = mock_evals_module.Evals.return_value
        mock_eval_item = mock.Mock()
        mock_eval_item.name = "eval_item_1"
        mock_evals_instance.create_evaluation_item.return_value = mock_eval_item

        mock_eval_set = mock.Mock()
        mock_eval_set.name = "eval_set_1"
        mock_evals_instance.create_evaluation_set.return_value = mock_eval_set

        history_content_1 = genai_types.Content(
            role="user", parts=[genai_types.Part(text="Old user msg")]
        )
        history_content_2 = genai_types.Content(
            role="model", parts=[genai_types.Part(text="Old model msg")]
        )

        dataset = vertexai_genai_types.EvaluationDataset(
            eval_cases=[
                vertexai_genai_types.EvalCase(
                    prompt=genai_types.Content(
                        parts=[genai_types.Part(text="test prompt")]
                    ),
                    responses=[
                        vertexai_genai_types.ResponseCandidate(
                            response=genai_types.Content(
                                parts=[genai_types.Part(text="test response")]
                            )
                        )
                    ],
                    conversation_history=[
                        vertexai_genai_types.evals.Message(
                            turn_id="0", content=history_content_1
                        ),
                        vertexai_genai_types.evals.Message(
                            turn_id="1", content=history_content_2
                        ),
                    ],
                )
            ]
        )

        result = _evals_common._resolve_dataset(
            api_client=self.mock_api_client,
            dataset=dataset,
            dest="gs://bucket/prefix",
        )

        assert result.evaluation_set == "eval_set_1"

        # Verify that conversation_history was passed through to the GCS upload
        mock_gcs_instance.upload_json_to_prefix.assert_called_once()
        call_args = mock_gcs_instance.upload_json_to_prefix.call_args
        uploaded_data = call_args.kwargs["data"]

        assert "prompt_template_data" in uploaded_data["prompt"]
        ptd_values = uploaded_data["prompt"]["prompt_template_data"]["values"]
        assert "conversation_history" in ptd_values


class TestRateLimiter:
    """Tests for the RateLimiter class in _evals_utils."""

    def test_rate_limiter_init(self):
        """Tests that RateLimiter initializes correctly."""
        limiter = _evals_utils.RateLimiter(rate=10.0)
        assert limiter.seconds_per_event == pytest.approx(0.1)

    def test_rate_limiter_invalid_rate(self):
        """Tests that RateLimiter raises ValueError for non-positive rate."""
        with pytest.raises(ValueError, match="Rate must be a positive number"):
            _evals_utils.RateLimiter(rate=0)
        with pytest.raises(ValueError, match="Rate must be a positive number"):
            _evals_utils.RateLimiter(rate=-1)

    @mock.patch("time.sleep", return_value=None)
    @mock.patch("time.monotonic")
    def test_rate_limiter_sleep_and_advance(self, mock_monotonic, mock_sleep):
        """Tests that sleep_and_advance properly throttles calls."""
        # With rate=10 (0.1s interval):
        # - __init__ at t=0: _next_allowed = 0.0
        # - first call at t=0: no delay, _next_allowed = 0.1
        # - second call at t=0.01: delay = 0.1 - 0.01 = 0.09
        mock_monotonic.side_effect = [
            0.0,  # __init__: time.monotonic()
            0.0,  # first sleep_and_advance: now
            0.01,  # second sleep_and_advance: now
        ]
        limiter = _evals_utils.RateLimiter(rate=10.0)
        limiter.sleep_and_advance()  # First call - should not sleep
        limiter.sleep_and_advance()  # Second call - should sleep
        assert mock_sleep.call_count == 1
        # Verify sleep was called with approximately the right delay
        sleep_delay = mock_sleep.call_args[0][0]
        assert 0.08 < sleep_delay <= 0.1

    def test_rate_limiter_no_sleep_when_enough_time_passed(self):
        """Tests that no sleep occurs when enough time has passed."""
        import time as real_time

        limiter = _evals_utils.RateLimiter(rate=1000.0)  # Very high rate
        # With rate=1000, interval is 0.001s - should not sleep
        start = real_time.time()
        for _ in range(5):
            limiter.sleep_and_advance()
        elapsed = real_time.time() - start
        # 5 calls at 1000 QPS should take ~0.005s, certainly under 1s
        assert elapsed < 1.0


class TestCallWithRetry:
    """Tests for the shared _call_with_retry helper."""

    @mock.patch("time.sleep", return_value=None)
    def test_call_with_retry_success_on_first_try(self, mock_sleep):
        """Tests that _call_with_retry returns immediately on success."""
        fn = mock.Mock(return_value="success")
        result = _evals_metric_handlers._call_with_retry(fn, "test_metric")
        assert result == "success"
        assert fn.call_count == 1
        assert mock_sleep.call_count == 0

    @mock.patch("time.sleep", return_value=None)
    def test_call_with_retry_success_after_retries(self, mock_sleep):
        """Tests that _call_with_retry succeeds after transient failures."""
        error_json = {"error": {"code": 429, "message": "exhausted"}}
        fn = mock.Mock(
            side_effect=[
                genai_errors.ClientError(code=429, response_json=error_json),
                genai_errors.ClientError(code=429, response_json=error_json),
                "success",
            ]
        )
        result = _evals_metric_handlers._call_with_retry(fn, "test_metric")
        assert result == "success"
        assert fn.call_count == 3
        assert mock_sleep.call_count == 2

    @mock.patch("time.sleep", return_value=None)
    def test_call_with_retry_raises_after_max_retries(self, mock_sleep):
        """Tests that _call_with_retry raises after exhausting retries."""
        error_json = {"error": {"code": 429, "message": "exhausted"}}
        fn = mock.Mock(
            side_effect=genai_errors.ClientError(code=429, response_json=error_json)
        )
        with pytest.raises(genai_errors.ClientError):
            _evals_metric_handlers._call_with_retry(fn, "test_metric")
        assert fn.call_count == 5  # _MAX_RETRIES
        assert mock_sleep.call_count == 4

    @mock.patch("time.sleep", return_value=None)
    def test_call_with_retry_retries_on_server_error(self, mock_sleep):
        """Tests retry on 503 ServiceUnavailable (ServerError)."""
        error_json = {"error": {"code": 503, "message": "unavailable"}}
        fn = mock.Mock(
            side_effect=[
                genai_errors.ServerError(code=503, response_json=error_json),
                "success",
            ]
        )
        result = _evals_metric_handlers._call_with_retry(fn, "test_metric")
        assert result == "success"
        assert fn.call_count == 2

    @mock.patch("time.sleep", return_value=None)
    def test_call_with_retry_no_retry_on_non_retryable(self, mock_sleep):
        """Tests that non-retryable errors are raised immediately."""
        error_json = {"error": {"code": 400, "message": "bad request"}}
        fn = mock.Mock(
            side_effect=genai_errors.ClientError(code=400, response_json=error_json)
        )
        with pytest.raises(genai_errors.ClientError):
            _evals_metric_handlers._call_with_retry(fn, "test_metric")
        assert fn.call_count == 1
        assert mock_sleep.call_count == 0


class TestComputationMetricRetry:
    """Tests for retry behavior in ComputationMetricHandler."""

    @mock.patch.object(
        _evals_metric_handlers.ComputationMetricHandler,
        "SUPPORTED_COMPUTATION_METRICS",
        frozenset(["bleu"]),
    )
    @mock.patch("time.sleep", return_value=None)
    # fmt: off
    @mock.patch(
        "vertexai._genai.evals.Evals.evaluate_instances"
    )
    # fmt: on
    def test_computation_metric_retry_on_resource_exhausted(
        self,
        mock_evaluate_instances,
        mock_sleep,
        mock_api_client_fixture,
    ):
        """Tests that ComputationMetricHandler retries on 429."""
        dataset_df = pd.DataFrame(
            [
                {
                    "prompt": "Test prompt",
                    "response": "Test response",
                    "reference": "Test reference",
                }
            ]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )
        metric = vertexai_genai_types.Metric(name="bleu")
        error_response_json = {
            "error": {
                "code": 429,
                "message": "Resource exhausted.",
                "status": "RESOURCE_EXHAUSTED",
            }
        }
        mock_bleu_result = mock.MagicMock()
        mock_bleu_result.model_dump.return_value = {
            "bleu_results": {"bleu_metric_values": [{"score": 0.85}]}
        }
        mock_evaluate_instances.side_effect = [
            genai_errors.ClientError(code=429, response_json=error_response_json),
            genai_errors.ClientError(code=429, response_json=error_response_json),
            mock_bleu_result,
        ]

        result = _evals_common._execute_evaluation(
            api_client=mock_api_client_fixture,
            dataset=input_dataset,
            metrics=[metric],
        )

        assert mock_evaluate_instances.call_count == 3
        assert mock_sleep.call_count == 2
        summary_metric = result.summary_metrics[0]
        assert summary_metric.metric_name == "bleu"
        assert summary_metric.mean_score == 0.85
