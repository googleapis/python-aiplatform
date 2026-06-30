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

import asyncio
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


@pytest.fixture
def mock_async_client():
    mock_api_client = mock.Mock(spec=client.Client)
    mock_api_client.project = _TEST_PROJECT
    mock_api_client.location = _TEST_LOCATION
    mock_api_client.vertexai = True

    return model_garden.AsyncModelGarden(mock_api_client)


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


# ---- list_publisher_model_deploy_options tests ----


def _make_deploy_option(
    deploy_task_name="option-1",
    machine_type="g2-standard-12",
    accelerator_type="NVIDIA_L4",
    accelerator_count=1,
    image_uri="us-docker.pkg.dev/vertex-ai/vertex-vision-model-garden-dockers/vllm",
):
    """Builds a single PublisherModelCallToActionDeploy option."""
    return types.PublisherModelCallToActionDeploy(
        deploy_task_name=deploy_task_name,
        dedicated_resources=types.DedicatedResources(
            machine_spec=types.MachineSpec(
                machine_type=machine_type,
                accelerator_type=accelerator_type,
                accelerator_count=accelerator_count,
            )
        ),
        container_spec=types.ModelContainerSpec(image_uri=image_uri),
    )


def _make_model_with_deploy_options(
    options, name="publishers/google/models/gemma-2b"
):
  """Builds a PublisherModel exposing the given deploy options."""
  return types.PublisherModel(
        name=name,
        supported_actions=types.PublisherModelCallToAction(
            multi_deploy_vertex=types.PublisherModelCallToActionDeployVertex(
                multi_deploy_vertex=options,
            )
        ),
    )


def test_list_publisher_model_deploy_options_basic(mock_client):
  """Tests extraction of a single deploy option into a DeployOption."""
  dummy_model = _make_model_with_deploy_options([_make_deploy_option()])

  with mock.patch.object(
        mock_client, "_get_publisher_model", return_value=dummy_model
    ) as mock_get:
    # A simplified name is reconciled to the full publisher resource name.
    options = mock_client.list_publisher_model_deploy_options(
        model="google/gemma3@gemma-3-12b-it"
    )

    # The GetPublisherModel call must use the reconciled name, flag the model
    # as non-Hugging-Face (it has an @version), and request equivalent
    # deployment configs.
    mock_get.assert_called_once_with(
        name="publishers/google/models/gemma3@gemma-3-12b-it",
        config=types.GetPublisherModelConfig(
            is_hugging_face_model=False,
            include_equivalent_model_garden_model_deployment_configs=True,
        ),
    )
    assert len(options) == 1
    assert isinstance(options[0], types.DeployOption)
    assert options[0].option_name == "option-1"
    assert options[0].machine_type == "g2-standard-12"
    # accelerator_type is returned as the enum's string value (legacy parity).
    assert options[0].accelerator_type == "NVIDIA_L4"
    assert options[0].accelerator_count == 1
    assert "vllm" in options[0].serving_container_image_uri


def test_list_publisher_model_deploy_options_multiple(mock_client):
  """Tests that all deploy options are returned when no filters are set."""
  dummy_model = _make_model_with_deploy_options(
        [
            _make_deploy_option(deploy_task_name="g2", machine_type="g2-standard-12"),
            _make_deploy_option(deploy_task_name="a3", machine_type="a3-highgpu-8g"),
        ]
    )

  with mock.patch.object(
      mock_client, "_get_publisher_model", return_value=dummy_model
  ):
    options = mock_client.list_publisher_model_deploy_options(
        model="publishers/google/models/gemma-2b@001"
    )

    assert [o.option_name for o in options] == ["g2", "a3"]


def test_list_publisher_model_deploy_options_machine_type_filter(mock_client):
  """Tests machine_type_filter is a case-insensitive substring match."""
  dummy_model = _make_model_with_deploy_options(
        [
            _make_deploy_option(deploy_task_name="g2", machine_type="g2-standard-12"),
            _make_deploy_option(deploy_task_name="a3", machine_type="a3-highgpu-8g"),
        ]
    )

  with mock.patch.object(
      mock_client, "_get_publisher_model", return_value=dummy_model
  ):
    options = mock_client.list_publisher_model_deploy_options(
        model="publishers/google/models/gemma-2b@001",
        config=types.ListPublisherModelDeployOptionsConfig(
            machine_type_filter="G2"
        ),
    )

    assert len(options) == 1
    assert options[0].option_name == "g2"


def test_list_publisher_model_deploy_options_accelerator_type_filter(
    mock_client,
):
  """Tests accelerator_type_filter is a case-insensitive substring match."""
  dummy_model = _make_model_with_deploy_options([
      _make_deploy_option(deploy_task_name="l4", accelerator_type="NVIDIA_L4"),
      _make_deploy_option(
          deploy_task_name="h100", accelerator_type="NVIDIA_H100_80GB"
      ),
  ])

  with mock.patch.object(
      mock_client, "_get_publisher_model", return_value=dummy_model
  ):
    options = mock_client.list_publisher_model_deploy_options(
        model="publishers/google/models/gemma-2b@001",
        config=types.ListPublisherModelDeployOptionsConfig(
            accelerator_type_filter="h100"
        ),
    )

    assert len(options) == 1
    assert options[0].option_name == "h100"


def test_list_publisher_model_deploy_options_image_uri_filter(mock_client):
  """Tests serving_container_image_uri_filter is a case-insensitive match."""
  dummy_model = _make_model_with_deploy_options(
        [
            _make_deploy_option(deploy_task_name="vllm", image_uri="docker/vllm"),
            _make_deploy_option(deploy_task_name="tgi", image_uri="docker/tgi"),
        ]
    )

  with mock.patch.object(
      mock_client, "_get_publisher_model", return_value=dummy_model
  ):
    options = mock_client.list_publisher_model_deploy_options(
        model="publishers/google/models/gemma-2b@001",
        config=types.ListPublisherModelDeployOptionsConfig(
            serving_container_image_uri_filter="VLLM"
        ),
    )

    assert len(options) == 1
    assert options[0].option_name == "vllm"


def test_list_publisher_model_deploy_options_machine_type_filter_list(
    mock_client,
):
  """Tests a list of keywords matches options containing ANY of them (legacy parity)."""
  dummy_model = _make_model_with_deploy_options([
      _make_deploy_option(deploy_task_name="g2", machine_type="g2-standard-12"),
      _make_deploy_option(deploy_task_name="a3", machine_type="a3-highgpu-8g"),
      _make_deploy_option(deploy_task_name="n1", machine_type="n1-standard-8"),
  ])

  with mock.patch.object(
      mock_client, "_get_publisher_model", return_value=dummy_model
  ):
    options = mock_client.list_publisher_model_deploy_options(
        model="publishers/google/models/gemma-2b@001",
        config=types.ListPublisherModelDeployOptionsConfig(
            machine_type_filter=["A3", "n1"]
        ),
    )

    assert [o.option_name for o in options] == ["a3", "n1"]


def test_list_publisher_model_deploy_options_accelerator_type_filter_list(
    mock_client,
):
  """Tests a list accelerator filter matches options containing ANY keyword."""
  dummy_model = _make_model_with_deploy_options([
      _make_deploy_option(deploy_task_name="l4", accelerator_type="NVIDIA_L4"),
      _make_deploy_option(
          deploy_task_name="t4", accelerator_type="NVIDIA_TESLA_T4"
      ),
      _make_deploy_option(
          deploy_task_name="h100", accelerator_type="NVIDIA_H100_80GB"
      ),
  ])

  with mock.patch.object(
      mock_client, "_get_publisher_model", return_value=dummy_model
  ):
    options = mock_client.list_publisher_model_deploy_options(
        model="publishers/google/models/gemma-2b@001",
        config=types.ListPublisherModelDeployOptionsConfig(
            accelerator_type_filter=["T4", "L4"]
        ),
    )

    assert [o.option_name for o in options] == ["l4", "t4"]


def test_list_publisher_model_deploy_options_image_uri_filter_list(mock_client):
  """Tests a list image-uri filter matches any keyword."""
  dummy_model = _make_model_with_deploy_options(
        [
            _make_deploy_option(deploy_task_name="vllm", image_uri="docker/vllm"),
            _make_deploy_option(deploy_task_name="tgi", image_uri="docker/tgi"),
            _make_deploy_option(deploy_task_name="sglang", image_uri="docker/sglang"),
        ]
    )

  with mock.patch.object(
      mock_client, "_get_publisher_model", return_value=dummy_model
  ):
    options = mock_client.list_publisher_model_deploy_options(
        model="publishers/google/models/gemma-2b@001",
        config=types.ListPublisherModelDeployOptionsConfig(
            serving_container_image_uri_filter=["vllm", "tgi"]
        ),
    )

    assert [o.option_name for o in options] == ["vllm", "tgi"]


def test_matches_filter():
  """Tests the keyword-filter helper (single keyword, list, None, misses)."""
  matches = model_garden.ModelGarden._matches_filter
  # No filter -> always matches.
  assert matches("g2-standard-12", None) is True
  assert matches(None, None) is True
  # Single keyword, case-insensitive substring.
  assert matches("g2-standard-12", "G2") is True
  assert matches("g2-standard-12", "n1") is False
  # List of keywords -> match if ANY is contained.
  assert matches("a3-highgpu-8g", ["n1", "a3"]) is True
  assert matches("a3-highgpu-8g", ["n1", "g2"]) is False
  # A missing (None) value never matches a non-empty filter.
  assert matches(None, "g2") is False
  # An empty list filter behaves like "no filter".
  assert matches("anything", []) is True


def test_list_publisher_model_deploy_options_dict_config(mock_client):
  """Tests config passed as a dict is validated and applied."""
  dummy_model = _make_model_with_deploy_options(
        [
            _make_deploy_option(deploy_task_name="g2", machine_type="g2-standard-12"),
            _make_deploy_option(deploy_task_name="a3", machine_type="a3-highgpu-8g"),
        ]
    )

  with mock.patch.object(
      mock_client, "_get_publisher_model", return_value=dummy_model
  ):
    options = mock_client.list_publisher_model_deploy_options(
        model="publishers/google/models/gemma-2b@001",
        config={"machine_type_filter": "a3"},
    )

    assert len(options) == 1
    assert options[0].option_name == "a3"


def test_list_publisher_model_deploy_options_default_config(mock_client):
  """Tests config=None returns all options."""
  dummy_model = _make_model_with_deploy_options([_make_deploy_option()])

  with mock.patch.object(
      mock_client, "_get_publisher_model", return_value=dummy_model
  ):
    options = mock_client.list_publisher_model_deploy_options(
        model="publishers/google/models/gemma-2b@001"
    )

    assert len(options) == 1


def test_list_publisher_model_deploy_options_no_deploy_support_raises(
    mock_client,
):
  """Tests ValueError when the model does not support deployment (legacy parity)."""
  dummy_model = types.PublisherModel(name="publishers/google/models/bert-base")

  with mock.patch.object(
      mock_client, "_get_publisher_model", return_value=dummy_model
  ):
    with pytest.raises(ValueError, match="does not support deployment"):
      mock_client.list_publisher_model_deploy_options(
          model="publishers/google/models/bert-base@001"
      )


def test_list_publisher_model_deploy_options_no_match_raises(mock_client):
  """Tests ValueError when filters exclude every option (legacy parity)."""
  dummy_model = _make_model_with_deploy_options([_make_deploy_option()])

  with mock.patch.object(
      mock_client, "_get_publisher_model", return_value=dummy_model
  ):
    with pytest.raises(ValueError, match="No deploy options found."):
      mock_client.list_publisher_model_deploy_options(
          model="publishers/google/models/gemma-2b@001",
          config=types.ListPublisherModelDeployOptionsConfig(
              machine_type_filter="does-not-exist"
          ),
      )


def test_reconcile_model_name_simplified_with_version():
    """Tests a simplified name with a version is expanded to the full name."""
    reconcile = model_garden.ModelGarden._reconcile_model_name
    assert (
        reconcile("google/gemma3@gemma-3-12b-it")
        == "publishers/google/models/gemma3@gemma-3-12b-it"
    )


def test_reconcile_model_name_simplified_without_version():
    """Tests a simplified name without a version is expanded to the full name."""
    reconcile = model_garden.ModelGarden._reconcile_model_name
    assert reconcile("google/gemma3") == "publishers/google/models/gemma3"


def test_reconcile_model_name_full_resource_name():
    """Tests a full resource name (with version) is returned normalized."""
    reconcile = model_garden.ModelGarden._reconcile_model_name
    assert (
        reconcile("publishers/google/models/gemma3@gemma-3-12b-it")
        == "publishers/google/models/gemma3@gemma-3-12b-it"
    )


def test_reconcile_model_name_lowercases():
    """Tests names are lowercased (Hugging Face parity with legacy SDK)."""
    reconcile = model_garden.ModelGarden._reconcile_model_name
    assert (
        reconcile("Meta-Llama/Llama-3.3-70B-Instruct")
        == "publishers/meta-llama/models/llama-3.3-70b-instruct"
    )


def test_reconcile_model_name_invalid_raises():
  """Tests an invalid name raises ValueError."""
  reconcile = model_garden.ModelGarden._reconcile_model_name
  with pytest.raises(ValueError, match="not a valid publisher model name"):
    reconcile("invalid-name-without-slash")


def test_reconcile_model_name_model_registry_raises():
  """Tests a Model Registry resource name raises ValueError.

  Without an explicit guard, ``projects/.../locations/.../models/...`` would
  match the simplified ``{publisher}/{model}`` regex and be silently mangled
  into ``publishers/projects/models/.../locations/.../models/...``. The guard
  rejects it loudly with the same ``not a valid publisher model name``
  message used for any other unsupported input.
  """
  reconcile = model_garden.ModelGarden._reconcile_model_name
  for name in (
      "projects/123/locations/us-central1/models/456",
      "projects/my-project/locations/europe-west1/models/9876543210@1",
      "projects/p/locations/l/models/m",
  ):
    with pytest.raises(ValueError, match="not a valid publisher model name"):
      reconcile(name)


def test_is_hugging_face_model():
  """Tests the Hugging Face model heuristic."""
  is_hf = model_garden.ModelGarden._is_hugging_face_model
  # Bare org/model (single slash, no @version) -> Hugging Face.
  assert is_hf("meta-llama/Llama-3.3-70B-Instruct") is True
  # Simplified native names without @version also match (handled
  # correctly by _reconcile_model_name).
  assert is_hf("google/gemma3") is True
  # Names with @version or a publishers/ prefix are not Hugging Face.
  assert is_hf("google/gemma3@gemma-3-12b-it") is False
  assert is_hf("publishers/google/models/gemma3@gemma-3-12b-it") is False
  assert is_hf("publishers/hf-meta-llama/models/llama-3.3") is False


def test_list_publisher_model_deploy_options_hugging_face_model(mock_client):
  """Tests an HF model name sends is_hugging_face_model=True (legacy parity)."""
  dummy_model = _make_model_with_deploy_options([_make_deploy_option()])

  with mock.patch.object(
        mock_client, "_get_publisher_model", return_value=dummy_model
    ) as mock_get:
    mock_client.list_publisher_model_deploy_options(
        model="meta-llama/Llama-3.3-70B-Instruct"
    )

    mock_get.assert_called_once_with(
        name="publishers/meta-llama/models/llama-3.3-70b-instruct",
        config=types.GetPublisherModelConfig(
            is_hugging_face_model=True,
            include_equivalent_model_garden_model_deployment_configs=True,
        ),
    )


def test_list_publisher_model_deploy_options_async(mock_async_client):
  """Tests the async client returns deploy options."""
  dummy_model = _make_model_with_deploy_options([_make_deploy_option()])

  with mock.patch.object(
        mock_async_client,
        "_get_publisher_model",
        new=mock.AsyncMock(return_value=dummy_model),
    ):
    options = asyncio.run(
        mock_async_client.list_publisher_model_deploy_options(
            model="publishers/google/models/gemma-2b@001"
        )
    )

    assert len(options) == 1
    assert options[0].option_name == "option-1"
    assert options[0].machine_type == "g2-standard-12"


def test_list_publisher_model_deploy_options_async_no_deploy_support_raises(
    mock_async_client,
):
  """Tests the async client raises when deployment is unsupported."""
  dummy_model = types.PublisherModel(name="publishers/google/models/bert-base")

  with mock.patch.object(
        mock_async_client,
        "_get_publisher_model",
        new=mock.AsyncMock(return_value=dummy_model),
    ):
    with pytest.raises(ValueError, match="does not support deployment"):
      asyncio.run(
          mock_async_client.list_publisher_model_deploy_options(
              model="publishers/google/models/bert-base@001"
          )
      )


def _make_deploy_option_no_accelerator(
    deploy_task_name="tpu",
    machine_type="ct5lp-hightpu-1t",
    image_uri="docker/hexllm",
):
  """Builds a deploy option whose machine has no GPU accelerator (e.g. TPU)."""
  return types.PublisherModelCallToActionDeploy(
        deploy_task_name=deploy_task_name,
        dedicated_resources=types.DedicatedResources(
            machine_spec=types.MachineSpec(machine_type=machine_type)
        ),
        container_spec=types.ModelContainerSpec(image_uri=image_uri),
    )


def test_list_publisher_model_deploy_options_no_accelerator_defaults(
    mock_client,
):
  """Tests no-accelerator machines report UNSPECIFIED/0 (legacy proto parity)."""
  dummy_model = _make_model_with_deploy_options(
      [_make_deploy_option_no_accelerator()]
  )

  with mock.patch.object(
      mock_client, "_get_publisher_model", return_value=dummy_model
  ):
    options = mock_client.list_publisher_model_deploy_options(
        model="publishers/google/models/gemma-2b@001"
    )

    assert options[0].machine_type == "ct5lp-hightpu-1t"
    # Over gRPC the legacy SDK surfaces these proto3 defaults; we match them.
    assert options[0].accelerator_type == "ACCELERATOR_TYPE_UNSPECIFIED"
    assert options[0].accelerator_count == 0


def test_list_publisher_model_deploy_options_no_accelerator_concise(
    mock_client,
):
  """Tests concise output for a no-accelerator machine matches legacy."""
  dummy_model = _make_model_with_deploy_options(
      [_make_deploy_option_no_accelerator()]
  )

  with mock.patch.object(
      mock_client, "_get_publisher_model", return_value=dummy_model
  ):
    result = mock_client.list_publisher_model_deploy_options(
        model="publishers/google/models/gemma-2b@001",
        config=types.ListPublisherModelDeployOptionsConfig(concise=True),
    )

    expected = (
        "[Option 1: tpu]\n"
        '    serving_container_image_uri="docker/hexllm",\n'
        '    machine_type="ct5lp-hightpu-1t",\n'
        '    accelerator_type="ACCELERATOR_TYPE_UNSPECIFIED",\n'
        "    accelerator_count=0,"
    )
    assert result == expected


def test_list_publisher_model_deploy_options_accelerator_filter_excludes_unspecified(
    mock_client,
):
  """Tests accelerator_type_filter excludes no-accelerator options (legacy parity)."""
  dummy_model = _make_model_with_deploy_options(
        [
            _make_deploy_option_no_accelerator(deploy_task_name="tpu"),
            _make_deploy_option(deploy_task_name="gpu", accelerator_type="NVIDIA_L4"),
        ]
    )

  with mock.patch.object(
      mock_client, "_get_publisher_model", return_value=dummy_model
  ):
    options = mock_client.list_publisher_model_deploy_options(
        model="publishers/google/models/gemma-2b@001",
        config=types.ListPublisherModelDeployOptionsConfig(
            accelerator_type_filter="NVIDIA"
        ),
    )

    assert [o.option_name for o in options] == ["gpu"]


# ---- concise option tests ----


def test_list_publisher_model_deploy_options_not_concise_returns_list(
    mock_client,
):
  """Tests that without concise the method returns a list of DeployOption."""
  dummy_model = _make_model_with_deploy_options([_make_deploy_option()])

  with mock.patch.object(
      mock_client, "_get_publisher_model", return_value=dummy_model
  ):
    result = mock_client.list_publisher_model_deploy_options(
        model="publishers/google/models/gemma-2b@001",
        config=types.ListPublisherModelDeployOptionsConfig(concise=False),
    )

    assert isinstance(result, list)
    assert isinstance(result[0], types.DeployOption)


def test_list_publisher_model_deploy_options_concise_returns_string(
    mock_client,
):
  """Tests concise=True returns the legacy-format human-readable string."""
  dummy_model = _make_model_with_deploy_options([
      _make_deploy_option(
          deploy_task_name="option-1",
          machine_type="g2-standard-12",
          accelerator_type="NVIDIA_L4",
          accelerator_count=1,
          image_uri="docker/vllm",
      )
  ])

  with mock.patch.object(
      mock_client, "_get_publisher_model", return_value=dummy_model
  ):
    result = mock_client.list_publisher_model_deploy_options(
        model="publishers/google/models/gemma-2b@001",
        config=types.ListPublisherModelDeployOptionsConfig(concise=True),
    )

    # Matches the legacy SDK's concise formatting exactly.
    expected = (
        "[Option 1: option-1]\n"
        '    serving_container_image_uri="docker/vllm",\n'
        '    machine_type="g2-standard-12",\n'
        '    accelerator_type="NVIDIA_L4",\n'
        "    accelerator_count=1,"
    )
    assert isinstance(result, str)
    assert result == expected


def test_list_publisher_model_deploy_options_concise_multiple(mock_client):
  """Tests concise formatting of multiple options separated by a blank line."""
  dummy_model = _make_model_with_deploy_options(
        [
            _make_deploy_option(
                deploy_task_name="g2",
                machine_type="g2-standard-12",
                accelerator_type="NVIDIA_L4",
                accelerator_count=1,
                image_uri="docker/vllm",
            ),
            _make_deploy_option(
                deploy_task_name="a3",
                machine_type="a3-highgpu-8g",
                accelerator_type="NVIDIA_H100_80GB",
                accelerator_count=8,
                image_uri="docker/hexllm",
            ),
        ]
    )

  with mock.patch.object(
      mock_client, "_get_publisher_model", return_value=dummy_model
  ):
    result = mock_client.list_publisher_model_deploy_options(
        model="publishers/google/models/gemma-2b@001",
        config=types.ListPublisherModelDeployOptionsConfig(concise=True),
    )

    expected = (
        "[Option 1: g2]\n"
        '    serving_container_image_uri="docker/vllm",\n'
        '    machine_type="g2-standard-12",\n'
        '    accelerator_type="NVIDIA_L4",\n'
        "    accelerator_count=1,"
        "\n\n"
        "[Option 2: a3]\n"
        '    serving_container_image_uri="docker/hexllm",\n'
        '    machine_type="a3-highgpu-8g",\n'
        '    accelerator_type="NVIDIA_H100_80GB",\n'
        "    accelerator_count=8,"
    )
    assert result == expected


def test_list_publisher_model_deploy_options_concise_with_filter(mock_client):
  """Tests concise output honors filters before formatting."""
  dummy_model = _make_model_with_deploy_options(
        [
            _make_deploy_option(deploy_task_name="g2", machine_type="g2-standard-12"),
            _make_deploy_option(deploy_task_name="a3", machine_type="a3-highgpu-8g"),
        ]
    )

  with mock.patch.object(
      mock_client, "_get_publisher_model", return_value=dummy_model
  ):
    result = mock_client.list_publisher_model_deploy_options(
        model="publishers/google/models/gemma-2b@001",
        config=types.ListPublisherModelDeployOptionsConfig(
            machine_type_filter="a3", concise=True
        ),
    )

    assert result.startswith("[Option 1: a3]")
    assert "a3-highgpu-8g" in result
    assert "g2-standard-12" not in result


def test_format_concise_deploy_options_omits_none_fields():
  """Tests that None fields are omitted and the header has no name if unset."""
  options = [
        types.DeployOption(
            machine_type="g2-standard-12",
            accelerator_count=1,
        )
    ]
  result = model_garden.ModelGarden._format_concise_deploy_options(options)
  expected = (
        "[Option 1]\n"
        '    machine_type="g2-standard-12",\n'
        "    accelerator_count=1,"
    )
  assert result == expected


def test_list_publisher_model_deploy_options_concise_async(mock_async_client):
  """Tests the async client returns a concise string when requested."""
  dummy_model = _make_model_with_deploy_options(
        [
            _make_deploy_option(
                deploy_task_name="option-1",
                machine_type="g2-standard-12",
                accelerator_type="NVIDIA_L4",
                accelerator_count=1,
                image_uri="docker/vllm",
            )
        ]
    )

  with mock.patch.object(
        mock_async_client,
        "_get_publisher_model",
        new=mock.AsyncMock(return_value=dummy_model),
    ):
    result = asyncio.run(
        mock_async_client.list_publisher_model_deploy_options(
            model="publishers/google/models/gemma-2b@001",
            config=types.ListPublisherModelDeployOptionsConfig(concise=True),
        )
    )

    assert isinstance(result, str)
    assert result.startswith("[Option 1: option-1]")
