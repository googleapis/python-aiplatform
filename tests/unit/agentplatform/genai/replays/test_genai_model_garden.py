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
import pytest


def test_list_deployable_models(client):
    """Tests listing deployable models in Model Garden."""
    models = client.model_garden.list_deployable_models(
        config=types.ListDeployableModelsConfig(
            include_hugging_face_models=False,
            model_filter="timesfm",
        )
    )
    assert len(models) > 0
    # Returns formatted strings like 'google/timesfm@timesfm-2.0'
    assert isinstance(models[0], str)
    assert "timesfm" in models[0].lower()


def test_list_models(client):
  """Tests listing all baseline models in Model Garden."""
  models = client.model_garden.list_models(
      config=types.ListModelGardenModelsConfig(
          include_hugging_face_models=False,
          model_filter="timesfm",
      )
  )
  assert len(models) > 0
  assert isinstance(models[0], str)
  assert "timesfm" in models[0].lower()


def test_list_publisher_model_deploy_options(client):
  """Tests listing the verified deploy options for an open model."""
  options = client.model_garden.list_publisher_model_deploy_options(
      model="google/gemma3@gemma-3-12b-it"
  )
  assert len(options) > 0
  assert isinstance(options[0], types.DeployOption)
  # Every verified deploy option exposes a serving container image.
  assert options[0].serving_container_image_uri


def test_list_publisher_model_deploy_options_with_filter(client):
  """Tests filtering an open model's deploy options by accelerator type."""
  options = client.model_garden.list_publisher_model_deploy_options(
      model="google/gemma3@gemma-3-12b-it",
      config=types.ListPublisherModelDeployOptionsConfig(
          accelerator_type_filter="NVIDIA"
      ),
  )
  assert len(options) > 0
  for option in options:
    assert "NVIDIA" in (option.accelerator_type or "")


def test_list_publisher_model_deploy_options_concise(client):
  """Tests the concise (human-readable string) output for an open model."""
  options = client.model_garden.list_publisher_model_deploy_options(
      model="google/gemma3@gemma-3-12b-it",
      config=types.ListPublisherModelDeployOptionsConfig(concise=True),
  )
  assert isinstance(options, str)
  assert "[Option 1" in options


def test_list_publisher_model_deploy_options_hugging_face(client):
  """Tests deploy options for a Hugging Face model.

  Exercises the distinct GetPublisherModel request path where
  is_hugging_face_model=True is sent.
  """
  options = client.model_garden.list_publisher_model_deploy_options(
      model="codellama/codellama-7b-hf"
  )
  assert len(options) > 0
  assert isinstance(options[0], types.DeployOption)
  assert options[0].serving_container_image_uri


def test_list_publisher_model_deploy_options_no_deploy_support(client):
  """Tests a model with no verified deployment config raises ValueError."""
  with pytest.raises(ValueError, match="does not support deployment"):
    client.model_garden.list_publisher_model_deploy_options(
        model="google/gemini-embedding-001@default"
    )


# A GCS folder holding a custom model (config.json + a weights file) that
# RecommendSpec maps to a supported base model (gemma-3-1b).
_CUSTOM_MODEL_SRC = "gs://sdk-mg-custom-model-replay/gemma-1b"


def test_list_custom_model_deploy_options(client):
  """Default config: machine availability + user-quota filter.

  Exercises the RecommendSpec backend (distinct from the GetPublisherModel
  path used by publisher models) and the human-readable string return type.
  With ``check_machine_availability`` defaulting to True, the response is
  the per-region ``recommendations`` list, so each option carries a
  ``region``.
  """
  options = client.model_garden.list_custom_model_deploy_options(
      src=_CUSTOM_MODEL_SRC,
  )
  assert isinstance(options, str)
  assert "[Option 1]" in options
  assert "region=" in options


def test_list_custom_model_deploy_options_check_machine_availability_false(
    client,
):
  """check_machine_availability=False -> RecommendSpec 'specs' path (no region field)."""
  options = client.model_garden.list_custom_model_deploy_options(
      src=_CUSTOM_MODEL_SRC,
      config=types.ListCustomModelDeployOptionsConfig(
          check_machine_availability=False
      ),
  )
  assert isinstance(options, str)
  assert "[Option 1]" in options
  assert "region=" not in options


def test_list_custom_model_deploy_options_no_user_quota_filter(client):
  """filter_by_user_quota=False -> recommendations returned without quota filtering."""
  options = client.model_garden.list_custom_model_deploy_options(
      src=_CUSTOM_MODEL_SRC,
      config=types.ListCustomModelDeployOptionsConfig(
          filter_by_user_quota=False
      ),
  )
  assert isinstance(options, str)
  assert "[Option 1]" in options
  assert "region=" in options


def test_list_custom_model_deploy_options_dict_config(client):
  """The config may be passed as a plain dict instead of the typed config."""
  options = client.model_garden.list_custom_model_deploy_options(
      src=_CUSTOM_MODEL_SRC,
      config={"check_machine_availability": False},
  )
  assert isinstance(options, str)
  assert "[Option 1]" in options
  assert "region=" not in options


def test_export_open_model_wait_for_completion(client):
  """Default wait_for_completion=True path: blocks on the LRO, returns URI.

  End-to-end coverage of the polling loop -- records the initial POST plus
  every GET on the operation until it's done, so recording takes as long as
  the export itself (~2h for Gemma-2-2B). Once recorded, replaying is
  instant. Skip this filter when iterating on unrelated changes.
  """
  destination_uri = client.model_garden.export_open_model(
      model="google/gemma2@gemma-2-2b-it",
      output_gcs_uri="gs://mg-sdk-model-export-testing/gemma-2-2b-it/",
  )
  assert isinstance(destination_uri, str)
  assert destination_uri.startswith("gs://")


def test_export_open_model_no_wait_returns_operation(client):
  """wait_for_completion=False returns the ExportModelOperation immediately.

  Records only the initial ExportPublisherModel POST (no LRO polling), so
  this is cheap to record (seconds).
  """
  operation = client.model_garden.export_open_model(
      model="google/gemma2@gemma-2-2b-it",
      output_gcs_uri="gs://mg-sdk-model-export-testing/gemma-2-2b-it-no-wait/",
      config=types.ExportOpenModelConfig(wait_for_completion=False),
  )
  assert isinstance(operation, types.ExportModelOperation)
  assert operation.name
  assert "/operations/" in operation.name


def test_export_open_model_no_wait_dict_config(client):
  """The config may be passed as a plain dict; wait_for_completion=False path."""
  operation = client.model_garden.export_open_model(
      model="google/gemma2@gemma-2-2b-it",
      output_gcs_uri=(
          "gs://mg-sdk-model-export-testing/gemma-2-2b-it-dict-no-wait/"
      ),
      config={"wait_for_completion": False},
  )
  assert isinstance(operation, types.ExportModelOperation)
  assert operation.name


def test_get_export_publisher_model_operation(client):
  """Public getter returns an ExportModelOperation for a running export LRO.

  Chains a wait_for_completion=False export with an explicit poll via the
  public getter -- exercises the same call users doing their own polling
  (custom backoff, cancellation, etc.) will make.
  """
  op = client.model_garden.export_open_model(
      model="google/gemma2@gemma-2-2b-it",
      output_gcs_uri="gs://mg-sdk-model-export-testing/gemma-2-2b-it-poll/",
      config=types.ExportOpenModelConfig(wait_for_completion=False),
  )
  polled = client.model_garden.get_export_publisher_model_operation(
      operation_name=op.name,
  )
  assert isinstance(polled, types.ExportModelOperation)
  assert polled.name == op.name


def test_export_open_model_empty_uri_raises(client):
  """Empty output_gcs_uri is rejected client-side; no RPC needed."""
  with pytest.raises(ValueError, match="output_gcs_uri must be a non-empty"):
    client.model_garden.export_open_model(
        model="google/gemma3@gemma-3-12b-it", output_gcs_uri=""
    )


def test_export_open_model_hf_model_id_raises(client):
  """Hugging Face model IDs are rejected client-side; no RPC needed."""
  with pytest.raises(ValueError, match="does not support Hugging Face"):
    client.model_garden.export_open_model(
        model="meta-llama/Llama-3.3-70B-Instruct",
        output_gcs_uri="gs://mg-sdk-model-export-testing/hf-should-not-record/",
    )


def test_export_open_model_invalid_name_raises(client):
  """Invalid model name is rejected client-side; no RPC needed."""
  with pytest.raises(ValueError, match="not a valid publisher model name"):
    client.model_garden.export_open_model(
        model="not-a-valid-name", output_gcs_uri="gs://b/out/"
    )


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_list_deployable_models_async(client):
    """Tests listing deployable models asynchronously."""
    models = await client.aio.model_garden.list_deployable_models(
        config=types.ListDeployableModelsConfig(
            include_hugging_face_models=False,
            model_filter="timesfm",
        )
    )
    assert len(models) > 0
    assert isinstance(models[0], str)
    assert "timesfm" in models[0].lower()


@pytest.mark.asyncio
async def test_list_models_async(client):
    """Tests listing all baseline models asynchronously."""
    models = await client.aio.model_garden.list_models(
        config=types.ListModelGardenModelsConfig(
            include_hugging_face_models=False,
            model_filter="timesfm",
        )
    )
    assert len(models) > 0
    assert isinstance(models[0], str)
    assert "timesfm" in models[0].lower()


@pytest.mark.asyncio
async def test_list_publisher_model_deploy_options_async(client):
  """Tests listing the deploy options for an open model asynchronously."""
  options = await client.aio.model_garden.list_publisher_model_deploy_options(
      model="google/gemma3@gemma-3-12b-it"
  )
  assert len(options) > 0
  assert isinstance(options[0], types.DeployOption)
  assert options[0].serving_container_image_uri


@pytest.mark.asyncio
async def test_list_custom_model_deploy_options_async(client):
  """Tests listing the recommended deploy options for a custom model async."""
  options = await client.aio.model_garden.list_custom_model_deploy_options(
      src=_CUSTOM_MODEL_SRC,
      config=types.ListCustomModelDeployOptionsConfig(
          filter_by_user_quota=False,
      ),
  )
  assert isinstance(options, str)
  assert "[Option 1]" in options
  assert "region=" in options


@pytest.mark.asyncio
async def test_export_open_model_async_no_wait_returns_operation(client):
  """Async wait_for_completion=False returns the ExportModelOperation immediately."""
  operation = await client.aio.model_garden.export_open_model(
      model="google/gemma2@gemma-2-2b-it",
      output_gcs_uri=(
          "gs://mg-sdk-model-export-testing/gemma-2-2b-it-async-no-wait/"
      ),
      config=types.ExportOpenModelConfig(wait_for_completion=False),
  )
  assert isinstance(operation, types.ExportModelOperation)
  assert operation.name


@pytest.mark.asyncio
async def test_get_export_publisher_model_operation_async(client):
  """Public async getter returns an ExportModelOperation for an in-flight LRO."""
  op = await client.aio.model_garden.export_open_model(
      model="google/gemma2@gemma-2-2b-it",
      output_gcs_uri=(
          "gs://mg-sdk-model-export-testing/gemma-2-2b-it-async-poll/"
      ),
      config=types.ExportOpenModelConfig(wait_for_completion=False),
  )
  polled = await client.aio.model_garden.get_export_publisher_model_operation(
      operation_name=op.name,
  )
  assert isinstance(polled, types.ExportModelOperation)
  assert polled.name == op.name
