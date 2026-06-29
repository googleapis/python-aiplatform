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

from unittest import mock
from agentplatform._genai import model_garden
from agentplatform._genai import types
from google.genai import client
import pytest

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"


@pytest.fixture
def mock_client():
    mock_api_client = mock.Mock(spec=client.Client)
    mock_api_client.project = _TEST_PROJECT
    mock_api_client.location = _TEST_LOCATION
    mock_api_client.vertexai = True

    return model_garden.ModelGarden(mock_api_client)


def _make_deployable_model(name, version_id="001"):
    """Helper to create a PublisherModel with multi_deploy_vertex support."""
    return types.PublisherModel(
        name=name,
        version_id=version_id,
        supported_actions={
            "multi_deploy_vertex": {
                "multi_deploy_vertex": [{"deploy_task_name": "test-deploy"}]
            }
        },
    )


def test_list_deployable_models_excludes_hf_via_server_filter(mock_client):
    """Tests that is_hf_wildcard(false) is sent to exclude HF models server-side."""
    dummy_response = types.ListPublisherModelsResponse(
        publisher_models=[
            _make_deployable_model("publishers/google/models/gemma-2b"),
        ]
    )

    with mock.patch.object(
        mock_client, "_list_publisher_models", return_value=dummy_response
    ) as mock_list:
        models = mock_client.list_deployable_models(
            config=types.ListDeployableModelsConfig(include_hugging_face_models=False)
        )

        mock_list.assert_called_once()
        api_config = mock_list.call_args.kwargs.get("config")
        assert "is_hf_wildcard(false)" in api_config.filter
        assert len(models) == 1
        assert models[0] == "google/gemma-2b@001"


def test_list_deployable_models_filters_non_deployable(mock_client):
    """Tests that models without multi_deploy_vertex are filtered out."""
    dummy_response = types.ListPublisherModelsResponse(
        publisher_models=[
            _make_deployable_model("publishers/google/models/gemma-2b"),
            # This model has no deploy config
            types.PublisherModel(
                name="publishers/google/models/no-deploy", version_id="001"
            ),
        ]
    )

    with mock.patch.object(
        mock_client, "_list_publisher_models", return_value=dummy_response
    ):
        models = mock_client.list_deployable_models(
            config=types.ListDeployableModelsConfig(include_hugging_face_models=False)
        )

        assert len(models) == 1
        assert models[0] == "google/gemma-2b@001"


def test_list_deployable_models_with_hf(mock_client):
    """Tests format when include_hugging_face_models=True: no @version suffix."""
    dummy_response = types.ListPublisherModelsResponse(
        publisher_models=[
            _make_deployable_model("publishers/google/models/gemma-2b"),
            _make_deployable_model(
                "publishers/hf-meta/models/llama-3", version_id="llama-3"
            ),
        ]
    )

    with mock.patch.object(
        mock_client, "_list_publisher_models", return_value=dummy_response
    ):
        models = mock_client.list_deployable_models(
            config=types.ListDeployableModelsConfig(include_hugging_face_models=True)
        )

        assert len(models) == 2
        # When include_hugging_face_models=True, no @version for any model
        assert models[0] == "google/gemma-2b"
        assert models[1] == "meta/llama-3"


def test_list_deployable_models_default_config(mock_client):
    """Tests list_deployable_models with config=None uses defaults."""
    dummy_response = types.ListPublisherModelsResponse(
        publisher_models=[
            _make_deployable_model("publishers/google/models/gemma-2b"),
        ]
    )

    with mock.patch.object(
        mock_client, "_list_publisher_models", return_value=dummy_response
    ):
        models = mock_client.list_deployable_models()

        assert len(models) == 1
        assert models[0] == "google/gemma-2b@001"


def test_list_deployable_models_dict_config(mock_client):
    """Tests list_deployable_models with config passed as a dict."""
    dummy_response = types.ListPublisherModelsResponse(
        publisher_models=[
            _make_deployable_model("publishers/google/models/gemma-2b"),
        ]
    )

    with mock.patch.object(
        mock_client, "_list_publisher_models", return_value=dummy_response
    ):
        models = mock_client.list_deployable_models(
            config={"include_hugging_face_models": False}
        )

        assert len(models) == 1
        assert models[0] == "google/gemma-2b@001"


def test_list_deployable_models_empty_response(mock_client):
    """Tests list_deployable_models with no models returned."""
    dummy_response = types.ListPublisherModelsResponse(publisher_models=[])

    with mock.patch.object(
        mock_client, "_list_publisher_models", return_value=dummy_response
    ):
        models = mock_client.list_deployable_models()

        assert models == []


def test_list_deployable_models_filter_string(mock_client):
    """Tests that model_filter is passed to the API filter."""
    dummy_response = types.ListPublisherModelsResponse(publisher_models=[])

    with mock.patch.object(
        mock_client, "_list_publisher_models", return_value=dummy_response
    ) as mock_list:
        mock_client.list_deployable_models(
            config=types.ListDeployableModelsConfig(model_filter="gemma")
        )

        call_args = mock_list.call_args
        api_config = call_args.kwargs.get("config") or call_args[1].get("config")
        assert "gemma" in api_config.filter
        assert "is_hf_wildcard(false)" in api_config.filter
        # VERIFIED_DEPLOYMENT_SUCCEED only added when include_hf=True
        # When include_hf=False, deploy filtering is done client-side
        # via _has_deploy_config


def test_list_deployable_models_hf_filter_string(mock_client):
    """Tests that HF deployable filter includes VERIFIED_DEPLOYMENT_SUCCEED."""
    dummy_response = types.ListPublisherModelsResponse(publisher_models=[])

    with mock.patch.object(
        mock_client, "_list_publisher_models", return_value=dummy_response
    ) as mock_list:
        mock_client.list_deployable_models(
            config=types.ListDeployableModelsConfig(
                include_hugging_face_models=True, model_filter="gemma"
            )
        )

        call_args = mock_list.call_args
        api_config = call_args.kwargs.get("config") or call_args[1].get("config")
        assert "gemma" in api_config.filter
        assert "is_hf_wildcard(true)" in api_config.filter
        assert "VERIFIED_DEPLOYMENT_SUCCEED" in api_config.filter


# ---- list_models tests ----


def test_list_models_excludes_hf_via_server_filter(mock_client):
    """Tests that is_hf_wildcard(false) is sent to exclude HF models server-side."""
    dummy_response = types.ListPublisherModelsResponse(
        publisher_models=[
            types.PublisherModel(
                name="publishers/google/models/gemma-2b", version_id="001"
            ),
        ]
    )

    with mock.patch.object(
        mock_client, "_list_publisher_models", return_value=dummy_response
    ) as mock_list:
        models = mock_client.list_models(
            config=types.ListModelGardenModelsConfig(
                include_hugging_face_models=False
            )
        )

        api_config = mock_list.call_args.kwargs.get("config")
        assert "is_hf_wildcard(false)" in api_config.filter
        assert len(models) == 1
        assert models[0] == "google/gemma-2b@001"


def test_list_models_with_hf(mock_client):
    """Tests list_models with include_hugging_face_models=True."""
    dummy_response = types.ListPublisherModelsResponse(
        publisher_models=[
            types.PublisherModel(
                name="publishers/google/models/gemma-2b", version_id="001"
            ),
            types.PublisherModel(
                name="publishers/hf-meta/models/llama-3", version_id="llama-3"
            ),
        ]
    )

    with mock.patch.object(
        mock_client, "_list_publisher_models", return_value=dummy_response
    ):
        models = mock_client.list_models(
            config=types.ListModelGardenModelsConfig(
                include_hugging_face_models=True
            )
        )

        assert len(models) == 2
        assert models[0] == "google/gemma-2b"
        assert models[1] == "meta/llama-3"


def test_list_models_includes_non_deployable(mock_client):
    """Tests that list_models includes models without deploy configs.

    Unlike list_deployable_models, list_models should return ALL models
    regardless of whether they have multi_deploy_vertex configurations.
    """
    dummy_response = types.ListPublisherModelsResponse(
        publisher_models=[
            _make_deployable_model("publishers/google/models/gemma-2b"),
            # This model has no deploy config -- should still be included
            types.PublisherModel(
                name="publishers/google/models/bert-base", version_id="001"
            ),
        ]
    )

    with mock.patch.object(
        mock_client, "_list_publisher_models", return_value=dummy_response
    ):
        models = mock_client.list_models(
            config=types.ListModelGardenModelsConfig(
                include_hugging_face_models=False
            )
        )

        assert len(models) == 2
        assert models[0] == "google/gemma-2b@001"
        assert models[1] == "google/bert-base@001"


def test_list_models_default_config(mock_client):
    """Tests list_models with config=None uses defaults."""
    dummy_response = types.ListPublisherModelsResponse(
        publisher_models=[
            types.PublisherModel(
                name="publishers/google/models/gemma-2b", version_id="001"
            ),
        ]
    )

    with mock.patch.object(
        mock_client, "_list_publisher_models", return_value=dummy_response
    ):
        models = mock_client.list_models()

        assert len(models) == 1
        assert models[0] == "google/gemma-2b@001"


def test_list_models_dict_config(mock_client):
    """Tests list_models with config passed as a dict."""
    dummy_response = types.ListPublisherModelsResponse(
        publisher_models=[
            types.PublisherModel(
                name="publishers/google/models/gemma-2b", version_id="001"
            ),
        ]
    )

    with mock.patch.object(
        mock_client, "_list_publisher_models", return_value=dummy_response
    ):
        models = mock_client.list_models(
            config={"include_hugging_face_models": False, "model_filter": "gemma"}
        )

        assert len(models) == 1
        assert models[0] == "google/gemma-2b@001"


def test_list_models_empty_response(mock_client):
    """Tests list_models with no models returned."""
    dummy_response = types.ListPublisherModelsResponse(publisher_models=[])

    with mock.patch.object(
        mock_client, "_list_publisher_models", return_value=dummy_response
    ):
        models = mock_client.list_models()

        assert models == []


def test_list_models_filter_string_no_deploy_filter(mock_client):
    """Tests that list_models does NOT add VERIFIED_DEPLOYMENT filter."""
    dummy_response = types.ListPublisherModelsResponse(publisher_models=[])

    with mock.patch.object(
        mock_client, "_list_publisher_models", return_value=dummy_response
    ) as mock_list:
        mock_client.list_models(
            config=types.ListModelGardenModelsConfig(model_filter="llama")
        )

        call_args = mock_list.call_args
        api_config = call_args.kwargs.get("config") or call_args[1].get("config")
        assert "llama" in api_config.filter
        assert "is_hf_wildcard(false)" in api_config.filter
        # list_models should NOT have the deployable-only filter
        assert "VERIFIED_DEPLOYMENT_SUCCEED" not in api_config.filter


# ---- _build_filter_str tests ----


def test_build_filter_str_native_deployable():
    """Tests filter string for native deployable models."""
    build_filter = model_garden.ModelGarden._build_filter_str
    result = build_filter(
        model_filter=None, include_hugging_face_models=False, deployable_only=True
    )
    assert result == "is_hf_wildcard(false)"


def test_build_filter_str_hf_deployable():
    """Tests filter string for HF deployable models."""
    build_filter = model_garden.ModelGarden._build_filter_str
    result = build_filter(
        model_filter=None, include_hugging_face_models=True, deployable_only=True
    )
    assert "is_hf_wildcard(true)" in result
    assert "VERIFIED_DEPLOYMENT_SUCCEED" in result


def test_build_filter_str_hf_all():
    """Tests filter string for HF all models (not deployable only)."""
    build_filter = model_garden.ModelGarden._build_filter_str
    result = build_filter(
        model_filter=None, include_hugging_face_models=True, deployable_only=False
    )
    assert result == "is_hf_wildcard(true)"
    assert "VERIFIED_DEPLOYMENT_SUCCEED" not in result


def test_build_filter_str_with_model_filter():
    """Tests filter string includes model_filter substring."""
    build_filter = model_garden.ModelGarden._build_filter_str
    result = build_filter(
        model_filter="gemma", include_hugging_face_models=False, deployable_only=False
    )
    assert "is_hf_wildcard(false)" in result
    assert "gemma" in result
    assert "model_user_id" in result
    assert "display_name" in result


def test_build_filter_str_escapes_special_chars():
    """Tests that special regex characters in model_filter are escaped."""
    build_filter = model_garden.ModelGarden._build_filter_str
    result = build_filter(
        model_filter="model.v2+", include_hugging_face_models=False, deployable_only=False
    )
    # re.escape turns '.' into '\\.' and '+' into '\\+'
    assert r"model\.v2\+" in result
