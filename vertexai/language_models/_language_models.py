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
"""Classes for working with language models."""

import abc
import dataclasses
from typing import (
    Any,
    AsyncIterator,
    Dict,
    Iterator,
    List,
    Literal,
    Optional,
    Sequence,
    Union,
)
import warnings

from google.cloud import aiplatform
from google.cloud.aiplatform import _streaming_prediction
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer as aiplatform_initializer
from google.cloud.aiplatform import utils as aiplatform_utils
from google.cloud.aiplatform.compat import types as aiplatform_types
from google.cloud.aiplatform.utils import gcs_utils
from vertexai._model_garden import _model_garden_models
from vertexai.language_models import (
    _evaluatable_language_models,
)

try:
    import pandas
except ImportError:
    pandas = None


_LOGGER = base.Logger(__name__)


# Endpoint label/metadata key to preserve the base model ID information
_TUNING_BASE_MODEL_ID_LABEL_KEY = "google-vertex-llm-tuning-base-model-id"

_ACCELERATOR_TYPES = ["TPU", "GPU"]
_ACCELERATOR_TYPE_TYPE = Literal["TPU", "GPU"]


def _get_model_id_from_tuning_model_id(tuning_model_id: str) -> str:
    """Gets the base model ID for the model ID labels used the tuned models.

    Args:
        tuning_model_id: The model ID used in tuning. E.g. `text-bison-001`

    Returns:
        The publisher model ID

    Raises:
        ValueError: If tuning model ID is unsupported
    """
    model_name, _, version = tuning_model_id.rpartition("-")
    # "publishers/google/models/text-bison@001"
    return f"publishers/google/models/{model_name}@{version}"


class _LanguageModel(_model_garden_models._ModelGardenModel):
    """_LanguageModel is a base class for all language models."""

    def __init__(self, model_id: str, endpoint_name: Optional[str] = None):
        """Creates a LanguageModel.

        This constructor should not be called directly.
        Use `LanguageModel.from_pretrained(model_name=...)` instead.

        Args:
            model_id: Identifier of a Vertex LLM. Example: "text-bison@001"
            endpoint_name: Vertex Endpoint resource name for the model
        """

        super().__init__(
            model_id=model_id,
            endpoint_name=endpoint_name,
        )

    @property
    def _model_resource_name(self) -> str:
        """Full resource name of the model."""
        if "publishers/" in self._endpoint_name:
            return self._endpoint_name
        else:
            # This is a ModelRegistry resource name
            return self._endpoint.list_models()[0].model


@dataclasses.dataclass
class _PredictionRequest:
    """A single-instance prediction request."""

    instance: Dict[str, Any]
    parameters: Optional[Dict[str, Any]] = None


@dataclasses.dataclass
class _MultiInstancePredictionRequest:
    """A multi-instance prediction request."""

    instances: List[Dict[str, Any]]
    parameters: Optional[Dict[str, Any]] = None


class _TunableModelMixin(_LanguageModel):
    """Model that can be tuned."""

    def list_tuned_model_names(self) -> Sequence[str]:
        """Lists the names of tuned models.

        Returns:
            A list of tuned models that can be used with the `get_tuned_model` method.
        """
        model_info = _model_garden_models._get_model_info(
            model_id=self._model_id,
            schema_to_class_map={self._INSTANCE_SCHEMA_URI: type(self)},
        )
        return _list_tuned_model_names(model_id=model_info.tuning_model_id)

    @classmethod
    def get_tuned_model(cls, tuned_model_name: str) -> "_LanguageModel":
        """Loads the specified tuned language model."""

        tuned_vertex_model = aiplatform.Model(tuned_model_name)
        tuned_model_labels = tuned_vertex_model.labels

        if _TUNING_BASE_MODEL_ID_LABEL_KEY not in tuned_model_labels:
            raise ValueError(
                f"The provided model {tuned_model_name} does not have a base model ID."
            )

        tuning_model_id = tuned_vertex_model.labels[_TUNING_BASE_MODEL_ID_LABEL_KEY]

        tuned_model_deployments = tuned_vertex_model.gca_resource.deployed_models
        if len(tuned_model_deployments) == 0:
            # Deploying the model
            endpoint_name = tuned_vertex_model.deploy().resource_name
        else:
            endpoint_name = tuned_model_deployments[0].endpoint

        base_model_id = _get_model_id_from_tuning_model_id(tuning_model_id)
        model_info = _model_garden_models._get_model_info(
            model_id=base_model_id,
            schema_to_class_map={cls._INSTANCE_SCHEMA_URI: cls},
        )
        cls._validate_launch_stage(cls, model_info.publisher_model_resource)

        model = model_info.interface_class(
            model_id=base_model_id,
            endpoint_name=endpoint_name,
        )
        return model

    def tune_model(
        self,
        training_data: Union[str, "pandas.core.frame.DataFrame"],
        *,
        train_steps: Optional[int] = None,
        learning_rate: Optional[float] = None,
        learning_rate_multiplier: Optional[float] = None,
        tuning_job_location: Optional[str] = None,
        tuned_model_location: Optional[str] = None,
        model_display_name: Optional[str] = None,
        tuning_evaluation_spec: Optional["TuningEvaluationSpec"] = None,
        default_context: Optional[str] = None,
        accelerator_type: Optional[_ACCELERATOR_TYPE_TYPE] = None,
    ) -> "_LanguageModelTuningJob":
        """Tunes a model based on training data.

        This method launches and returns an asynchronous model tuning job.
        Usage:
        ```
        tuning_job = model.tune_model(...)
        ... do some other work
        tuned_model = tuning_job.get_tuned_model()  # Blocks until tuning is complete
        ```

        Args:
            training_data: A Pandas DataFrame or a URI pointing to data in JSON lines format.
                The dataset schema is model-specific.
                See https://cloud.google.com/vertex-ai/docs/generative-ai/models/tune-models#dataset_format
            train_steps: Number of training batches to tune on (batch size is 8 samples).
            learning_rate: Deprecated. Use learning_rate_multiplier instead.
                Learning rate to use in tuning.
            learning_rate_multiplier: Learning rate multiplier to use in tuning.
            tuning_job_location: GCP location where the tuning job should be run.
            tuned_model_location: GCP location where the tuned model should be deployed.
            model_display_name: Custom display name for the tuned model.
            tuning_evaluation_spec: Specification for the model evaluation during tuning.
            default_context: The context to use for all training samples by default.
            accelerator_type: Type of accelerator to use. Can be "TPU" or "GPU".

        Returns:
            A `LanguageModelTuningJob` object that represents the tuning job.
            Calling `job.result()` blocks until the tuning is complete and returns a `LanguageModel` object.

        Raises:
            ValueError: If the "tuning_job_location" value is not supported
            ValueError: If the "tuned_model_location" value is not supported
            RuntimeError: If the model does not support tuning
        """
        tuning_parameters = {}
        if train_steps is not None:
            tuning_parameters["train_steps"] = train_steps
        if learning_rate is not None:
            _LOGGER.warning(
                "The learning_rate parameter is deprecated."
                "Use the learning_rate_multiplier parameter instead."
            )
            tuning_parameters["learning_rate"] = learning_rate
        if learning_rate_multiplier is not None:
            tuning_parameters["learning_rate_multiplier"] = learning_rate_multiplier
        eval_spec = tuning_evaluation_spec
        if eval_spec is not None:
            if eval_spec.evaluation_data:
                if isinstance(eval_spec.evaluation_data, str):
                    if eval_spec.evaluation_data.startswith("gs://"):
                        tuning_parameters[
                            "evaluation_data_uri"
                        ] = eval_spec.evaluation_data
                    else:
                        raise ValueError("evaluation_data should be a GCS URI")
                else:
                    raise TypeError("evaluation_data should be a URI string")
            if eval_spec.evaluation_interval is not None:
                tuning_parameters["evaluation_interval"] = eval_spec.evaluation_interval
            if eval_spec.enable_early_stopping is not None:
                tuning_parameters[
                    "enable_early_stopping"
                ] = eval_spec.enable_early_stopping
            if eval_spec.tensorboard is not None:
                if isinstance(eval_spec.tensorboard, aiplatform.Tensorboard):
                    if eval_spec.tensorboard.location != tuning_job_location:
                        raise ValueError(
                            "The Tensorboard must be in the same location as the tuning job."
                        )
                    tuning_parameters[
                        "tensorboard_resource_id"
                    ] = eval_spec.tensorboard.resource_name
                elif isinstance(eval_spec.tensorboard, str):
                    resource_name_parts = aiplatform.Tensorboard._parse_resource_name(
                        eval_spec.tensorboard
                    )
                    if resource_name_parts["location"] != tuning_job_location:
                        raise ValueError(
                            "The Tensorboard must be in the same location as the tuning job."
                        )
                    tuning_parameters["tensorboard_resource_id"] = eval_spec.tensorboard
                else:
                    raise TypeError("tensorboard should be a URI string")

        if default_context:
            tuning_parameters["default_context"] = default_context

        if accelerator_type:
            if accelerator_type not in _ACCELERATOR_TYPES:
                raise ValueError(
                    f"Unsupported accelerator type: {accelerator_type}."
                    f" Supported types: {_ACCELERATOR_TYPES}"
                )
            tuning_parameters["accelerator_type"] = accelerator_type

        return self._tune_model(
            training_data=training_data,
            tuning_parameters=tuning_parameters,
            tuning_job_location=tuning_job_location,
            tuned_model_location=tuned_model_location,
            model_display_name=model_display_name,
        )

    def _tune_model(
        self,
        training_data: Union[str, "pandas.core.frame.DataFrame"],
        *,
        tuning_parameters: Dict[str, Any],
        tuning_job_location: Optional[str] = None,
        tuned_model_location: Optional[str] = None,
        model_display_name: Optional[str] = None,
    ):
        """Tunes a model based on training data.

        This method launches a model tuning job that can take some time.

        Args:
            training_data: A Pandas DataFrame or a URI pointing to data in JSON lines format.
                The dataset schema is model-specific.
                See https://cloud.google.com/vertex-ai/docs/generative-ai/models/tune-models#dataset_format
            tuning_parameters: Tuning pipeline parameter values.
            tuning_job_location: GCP location where the tuning job should be run.
            tuned_model_location: GCP location where the tuned model should be deployed.
            model_display_name: Custom display name for the tuned model.

        Returns:
            A `LanguageModelTuningJob` object that represents the tuning job.
            Calling `job.result()` blocks until the tuning is complete and returns a `LanguageModel` object.

        Raises:
            ValueError: If the "tuning_job_location" value is not supported
            ValueError: If the "tuned_model_location" value is not supported
            RuntimeError: If the model does not support tuning
        """
        if tuning_job_location not in _TUNING_LOCATIONS:
            raise ValueError(
                "Please specify the tuning job location (`tuning_job_location`)."
                f"Tuning is supported in the following locations: {_TUNING_LOCATIONS}"
            )
        if tuned_model_location not in _TUNED_MODEL_LOCATIONS:
            raise ValueError(
                "Tuned model deployment is only supported in the following locations: "
                f"{_TUNED_MODEL_LOCATIONS}"
            )
        model_info = _model_garden_models._get_model_info(
            model_id=self._model_id,
            schema_to_class_map={self._INSTANCE_SCHEMA_URI: type(self)},
        )
        if not model_info.tuning_pipeline_uri:
            raise RuntimeError(f"The {self._model_id} model does not support tuning")
        pipeline_job = _launch_tuning_job(
            training_data=training_data,
            model_id=model_info.tuning_model_id,
            tuning_pipeline_uri=model_info.tuning_pipeline_uri,
            tuning_parameters=tuning_parameters,
            model_display_name=model_display_name,
            tuning_job_location=tuning_job_location,
            tuned_model_location=tuned_model_location,
        )

        job = _LanguageModelTuningJob(
            base_model=self,
            job=pipeline_job,
        )
        return job


class _TunableTextModelMixin(_TunableModelMixin):
    """Text model that can be tuned."""

    def tune_model(
        self,
        training_data: Union[str, "pandas.core.frame.DataFrame"],
        *,
        train_steps: Optional[int] = None,
        learning_rate_multiplier: Optional[float] = None,
        tuning_job_location: Optional[str] = None,
        tuned_model_location: Optional[str] = None,
        model_display_name: Optional[str] = None,
        tuning_evaluation_spec: Optional["TuningEvaluationSpec"] = None,
        accelerator_type: Optional[_ACCELERATOR_TYPE_TYPE] = None,
    ) -> "_LanguageModelTuningJob":
        """Tunes a model based on training data.

        This method launches and returns an asynchronous model tuning job.
        Usage:
        ```
        tuning_job = model.tune_model(...)
        ... do some other work
        tuned_model = tuning_job.get_tuned_model()  # Blocks until tuning is complete

        Args:
            training_data: A Pandas DataFrame or a URI pointing to data in JSON lines format.
                The dataset schema is model-specific.
                See https://cloud.google.com/vertex-ai/docs/generative-ai/models/tune-models#dataset_format
            train_steps: Number of training batches to tune on (batch size is 8 samples).
            learning_rate_multiplier: Learning rate multiplier to use in tuning.
            tuning_job_location: GCP location where the tuning job should be run.
            tuned_model_location: GCP location where the tuned model should be deployed.
            model_display_name: Custom display name for the tuned model.
            tuning_evaluation_spec: Specification for the model evaluation during tuning.
            accelerator_type: Type of accelerator to use. Can be "TPU" or "GPU".

        Returns:
            A `LanguageModelTuningJob` object that represents the tuning job.
            Calling `job.result()` blocks until the tuning is complete and returns a `LanguageModel` object.

        Raises:
            ValueError: If the "tuning_job_location" value is not supported
            ValueError: If the "tuned_model_location" value is not supported
            RuntimeError: If the model does not support tuning
        """
        # Note: Chat models do not support default_context
        return super().tune_model(
            training_data=training_data,
            train_steps=train_steps,
            learning_rate_multiplier=learning_rate_multiplier,
            tuning_job_location=tuning_job_location,
            tuned_model_location=tuned_model_location,
            model_display_name=model_display_name,
            tuning_evaluation_spec=tuning_evaluation_spec,
            accelerator_type=accelerator_type,
        )


class _PreviewTunableTextModelMixin(_TunableModelMixin):
    """Text model that can be tuned."""

    def tune_model(
        self,
        training_data: Union[str, "pandas.core.frame.DataFrame"],
        *,
        train_steps: int = 1000,
        learning_rate: Optional[float] = None,
        learning_rate_multiplier: Optional[float] = None,
        tuning_job_location: Optional[str] = None,
        tuned_model_location: Optional[str] = None,
        model_display_name: Optional[str] = None,
        tuning_evaluation_spec: Optional["TuningEvaluationSpec"] = None,
        accelerator_type: Optional[_ACCELERATOR_TYPE_TYPE] = None,
    ) -> "_LanguageModelTuningJob":
        """Tunes a model based on training data.

        This method launches a model tuning job, waits for completion,
        updates the model in-place. This method returns job object for forward
        compatibility.
        In the future (GA), this method will become asynchronous and will stop
        updating the model in-place.

        Usage:
        ```
        tuning_job = model.tune_model(...)  # Blocks until tuning is complete
        tuned_model = tuning_job.get_tuned_model()  # Blocks until tuning is complete
        ```

        Args:
            training_data: A Pandas DataFrame or a URI pointing to data in JSON lines format.
                The dataset schema is model-specific.
                See https://cloud.google.com/vertex-ai/docs/generative-ai/models/tune-models#dataset_format
            train_steps: Number of training batches to tune on (batch size is 8 samples).
            learning_rate: Deprecated. Use learning_rate_multiplier instead.
                Learning rate to use in tuning.
            learning_rate_multiplier: Learning rate multiplier to use in tuning.
            tuning_job_location: GCP location where the tuning job should be run.
            tuned_model_location: GCP location where the tuned model should be deployed.
            model_display_name: Custom display name for the tuned model.
            tuning_evaluation_spec: Specification for the model evaluation during tuning.
            accelerator_type: Type of accelerator to use. Can be "TPU" or "GPU".

        Returns:
            A `LanguageModelTuningJob` object that represents the tuning job.
            Calling `job.result()` blocks until the tuning is complete and returns a `LanguageModel` object.

        Raises:
            ValueError: If the "tuning_job_location" value is not supported
            ValueError: If the "tuned_model_location" value is not supported
            RuntimeError: If the model does not support tuning
        """
        # Note: Chat models do not support default_context
        job = super().tune_model(
            training_data=training_data,
            train_steps=train_steps,
            learning_rate=learning_rate,
            learning_rate_multiplier=learning_rate_multiplier,
            tuning_job_location=tuning_job_location,
            tuned_model_location=tuned_model_location,
            model_display_name=model_display_name,
            tuning_evaluation_spec=tuning_evaluation_spec,
            accelerator_type=accelerator_type,
        )
        tuned_model = job.get_tuned_model()
        self._endpoint = tuned_model._endpoint
        self._endpoint_name = tuned_model._endpoint_name
        return job


class _TunableChatModelMixin(_TunableModelMixin):
    """Chat model that can be tuned."""

    def tune_model(
        self,
        training_data: Union[str, "pandas.core.frame.DataFrame"],
        *,
        train_steps: Optional[int] = None,
        learning_rate_multiplier: Optional[float] = None,
        tuning_job_location: Optional[str] = None,
        tuned_model_location: Optional[str] = None,
        model_display_name: Optional[str] = None,
        default_context: Optional[str] = None,
        accelerator_type: Optional[_ACCELERATOR_TYPE_TYPE] = None,
    ) -> "_LanguageModelTuningJob":
        """Tunes a model based on training data.

        This method launches and returns an asynchronous model tuning job.
        Usage:
        ```
        tuning_job = model.tune_model(...)
        ... do some other work
        tuned_model = tuning_job.get_tuned_model()  # Blocks until tuning is complete
        ```

        Args:
            training_data: A Pandas DataFrame or a URI pointing to data in JSON lines format.
                The dataset schema is model-specific.
                See https://cloud.google.com/vertex-ai/docs/generative-ai/models/tune-models#dataset_format
            train_steps: Number of training batches to tune on (batch size is 8 samples).
            learning_rate: Deprecated. Use learning_rate_multiplier instead.
                Learning rate to use in tuning.
            learning_rate_multiplier: Learning rate multiplier to use in tuning.
            tuning_job_location: GCP location where the tuning job should be run.
            tuned_model_location: GCP location where the tuned model should be deployed.
            model_display_name: Custom display name for the tuned model.
            default_context: The context to use for all training samples by default.
            accelerator_type: Type of accelerator to use. Can be "TPU" or "GPU".

        Returns:
            A `LanguageModelTuningJob` object that represents the tuning job.
            Calling `job.result()` blocks until the tuning is complete and returns a `LanguageModel` object.

        Raises:
            ValueError: If the "tuning_job_location" value is not supported
            ValueError: If the "tuned_model_location" value is not supported
            RuntimeError: If the model does not support tuning
        """
        # Note: Chat models do not support tuning_evaluation_spec
        return super().tune_model(
            training_data=training_data,
            train_steps=train_steps,
            learning_rate_multiplier=learning_rate_multiplier,
            tuning_job_location=tuning_job_location,
            tuned_model_location=tuned_model_location,
            model_display_name=model_display_name,
            default_context=default_context,
            accelerator_type=accelerator_type,
        )


class _PreviewTunableChatModelMixin(_TunableModelMixin):
    """Chat model that can be tuned."""

    def tune_model(
        self,
        training_data: Union[str, "pandas.core.frame.DataFrame"],
        *,
        train_steps: int = 1000,
        learning_rate: Optional[float] = None,
        learning_rate_multiplier: Optional[float] = None,
        tuning_job_location: Optional[str] = None,
        tuned_model_location: Optional[str] = None,
        model_display_name: Optional[str] = None,
        default_context: Optional[str] = None,
        accelerator_type: Optional[_ACCELERATOR_TYPE_TYPE] = None,
    ) -> "_LanguageModelTuningJob":
        """Tunes a model based on training data.

        This method launches a model tuning job, waits for completion,
        updates the model in-place. This method returns job object for forward
        compatibility.
        In the future (GA), this method will become asynchronous and will stop
        updating the model in-place.

        Usage:
        ```
        tuning_job = model.tune_model(...)  # Blocks until tuning is complete
        tuned_model = tuning_job.get_tuned_model()  # Blocks until tuning is complete
        ```

        Args:
            training_data: A Pandas DataFrame or a URI pointing to data in JSON lines format.
                The dataset schema is model-specific.
                See https://cloud.google.com/vertex-ai/docs/generative-ai/models/tune-models#dataset_format
            train_steps: Number of training batches to tune on (batch size is 8 samples).
            learning_rate: Deprecated. Use learning_rate_multiplier instead.
                Learning rate to use in tuning.
            learning_rate_multiplier: Learning rate multiplier to use in tuning.
            tuning_job_location: GCP location where the tuning job should be run.
            tuned_model_location: GCP location where the tuned model should be deployed.
            model_display_name: Custom display name for the tuned model.
            default_context: The context to use for all training samples by default.
            accelerator_type: Type of accelerator to use. Can be "TPU" or "GPU".

        Returns:
            A `LanguageModelTuningJob` object that represents the tuning job.
            Calling `job.result()` blocks until the tuning is complete and returns a `LanguageModel` object.

        Raises:
            ValueError: If the "tuning_job_location" value is not supported
            ValueError: If the "tuned_model_location" value is not supported
            RuntimeError: If the model does not support tuning
        """
        # Note: Chat models do not support tuning_evaluation_spec
        job = super().tune_model(
            training_data=training_data,
            train_steps=train_steps,
            learning_rate=learning_rate,
            learning_rate_multiplier=learning_rate_multiplier,
            tuning_job_location=tuning_job_location,
            tuned_model_location=tuned_model_location,
            model_display_name=model_display_name,
            default_context=default_context,
            accelerator_type=accelerator_type,
        )
        tuned_model = job.get_tuned_model()
        self._endpoint = tuned_model._endpoint
        self._endpoint_name = tuned_model._endpoint_name
        return job


@dataclasses.dataclass
class CountTokensResponse:
    """The response from a count_tokens request.
    Attributes:
        total_tokens (int):
            The total number of tokens counted across all
            instances passed to the request.
        total_billable_characters (int):
            The total number of billable characters
            counted across all instances from the request.
    """

    total_tokens: int
    total_billable_characters: int
    _count_tokens_response: Any


class _CountTokensMixin(_LanguageModel):
    """Mixin for models that support the CountTokens API"""

    def count_tokens(
        self,
        prompts: List[str],
    ) -> CountTokensResponse:
        """Counts the tokens and billable characters for a given prompt.

        Note: this does not make a prediction request to the model, it only counts the tokens
        in the request.

        Args:
            prompts (List[str]):
                Required. A list of prompts to ask the model. For example: ["What should I do today?", "How's it going?"]

        Returns:
            A `CountTokensResponse` object that contains the number of tokens
            in the text and the number of billable characters.
        """
        instances = []

        for prompt in prompts:
            instances.append({"content": prompt})

        count_tokens_response = self._endpoint._prediction_client.select_version(
            "v1beta1"
        ).count_tokens(
            endpoint=self._endpoint_name,
            instances=instances,
        )

        return CountTokensResponse(
            total_tokens=count_tokens_response.total_tokens,
            total_billable_characters=count_tokens_response.total_billable_characters,
            _count_tokens_response=count_tokens_response,
        )


@dataclasses.dataclass
class TuningEvaluationSpec:
    """Specification for model evaluation to perform during tuning.

    Attributes:
        evaluation_data: GCS URI of the evaluation dataset. This will run
            model evaluation as part of the tuning job.
        evaluation_interval: The evaluation will run at every
            evaluation_interval tuning steps. Default: 20.
        enable_early_stopping: If True, the tuning may stop early before
            completing all the tuning steps. Requires evaluation_data.
        tensorboard: Vertex Tensorboard where to write the evaluation metrics.
            The Tensorboard must be in the same location as the tuning job.
    """

    __module__ = "vertexai.language_models"

    evaluation_data: Optional[str] = None
    evaluation_interval: Optional[int] = None
    enable_early_stopping: Optional[bool] = None
    tensorboard: Optional[Union[aiplatform.Tensorboard, str]] = None


class _GroundingSourceBase(abc.ABC):
    """Interface of grounding source dataclass for grounding."""

    @abc.abstractmethod
    def _to_grounding_source_dict(self) -> Dict[str, Any]:
        """construct grounding source into dictionary"""
        pass


@dataclasses.dataclass
class WebSearch(_GroundingSourceBase):
    """WebSearch represents a grounding source using public web search."""

    _type: str = "WEB"

    def _to_grounding_source_dict(self) -> Dict[str, Any]:
        return {"type": self._type}


@dataclasses.dataclass
class VertexAISearch(_GroundingSourceBase):
    """VertexAISearchDatastore represents a grounding source using Vertex AI Search datastore
    Attributes:
        data_store_id: Data store ID of the Vertex AI Search datastore.
        location: GCP multi region where you have set up your Vertex AI Search data store. Possible values can be `global`, `us`, `eu`, etc.
        Learn more about Vertex AI Search location here:
        https://cloud.google.com/generative-ai-app-builder/docs/locations
        project: The project where you have set up your Vertex AI Search.
        If not specified, will assume that your Vertex AI Search is within your current project.
    """

    _data_store_id: str
    _location: str
    _type: str = "ENTERPRISE"

    def __init__(
        self, data_store_id: str, location: str, project: Optional[str] = None
    ):
        self._data_store_id = data_store_id
        self._location = location
        self._project = project

    def _get_datastore_path(self) -> str:
        _project = self._project or aiplatform_initializer.global_config.project
        return (
            f"projects/{_project}/locations/{self._location}"
            f"/collections/default_collection/dataStores/{self._data_store_id}"
        )

    def _to_grounding_source_dict(self) -> Dict[str, Any]:
        return {"type": self._type, "enterpriseDatastore": self._get_datastore_path()}


@dataclasses.dataclass
class GroundingSource:

    WebSearch = WebSearch
    VertexAISearch = VertexAISearch


@dataclasses.dataclass
class GroundingCitation:
    """Citaion used from grounding.
    Attributes:
        start_index: Index in the prediction output where the citation starts
            (inclusive). Must be >= 0 and < end_index.
        end_index: Index in the prediction output where the citation ends
            (exclusive). Must be > start_index and < len(output).
        url: URL associated with this citation. If present, this URL links to the
            webpage of the source of this citation. Possible URLs include news
            websites, GitHub repos, etc.
        title: Title associated with this citation. If present, it refers to the title
            of the source of this citation. Possible titles include
            news titles, book titles, etc.
        license: License associated with this citation. If present, it refers to the
            license of the source of this citation. Possible licenses include code
            licenses, e.g., mit license.
        publication_date: Publication date associated with this citation. If present, it refers to
            the date at which the source of this citation was published.
            Possible formats are YYYY, YYYY-MM, YYYY-MM-DD.
    """

    start_index: Optional[int] = None
    end_index: Optional[int] = None
    url: Optional[str] = None
    title: Optional[str] = None
    license: Optional[str] = None
    publication_date: Optional[str] = None


@dataclasses.dataclass
class GroundingMetadata:
    """Metadata for grounding.
    Attributes:
        citations: List of grounding citations.
    """

    citations: Optional[List[GroundingCitation]] = None

    def _parse_citation_from_dict(
        self, citation_dict_camel: Dict[str, Any]
    ) -> GroundingCitation:
        _start_index = citation_dict_camel.get("startIndex")
        _end_index = citation_dict_camel.get("endIndex")
        if _start_index is not None:
            _start_index = int(_start_index)
        if _end_index is not None:
            _end_index = int(_end_index)
        _url = citation_dict_camel.get("url")
        _title = citation_dict_camel.get("title")
        _license = citation_dict_camel.get("license")
        _publication_date = citation_dict_camel.get("publicationDate")

        return GroundingCitation(
            start_index=_start_index,
            end_index=_end_index,
            url=_url,
            title=_title,
            license=_license,
            publication_date=_publication_date,
        )

    def __init__(self, response: Optional[Dict[str, Any]] = {}):
        self.citations = [
            self._parse_citation_from_dict(citation)
            for citation in response.get("citations", [])
        ]


@dataclasses.dataclass
class TextGenerationResponse:
    """TextGenerationResponse represents a response of a language model.
    Attributes:
        text: The generated text
        is_blocked: Whether the the request was blocked.
        safety_attributes: Scores for safety attributes.
            Learn more about the safety attributes here:
            https://cloud.google.com/vertex-ai/docs/generative-ai/learn/responsible-ai#safety_attribute_descriptions
        grounding_metadata: Metadata for grounding.
    """

    __module__ = "vertexai.language_models"

    text: str
    _prediction_response: Any
    is_blocked: bool = False
    safety_attributes: Dict[str, float] = dataclasses.field(default_factory=dict)
    grounding_metadata: Optional[GroundingMetadata] = None

    def __repr__(self):
        if self.text:
            return self.text
        # Falling back to the full representation
        elif self.grounding_metadata is not None:
            return (
                "TextGenerationResponse("
                f"text={self.text!r}"
                f", is_blocked={self.is_blocked!r}"
                f", safety_attributes={self.safety_attributes!r}"
                f", grounding_metadata={self.grounding_metadata!r}"
                ")"
            )
        else:
            return (
                "TextGenerationResponse("
                f"text={self.text!r}"
                f", is_blocked={self.is_blocked!r}"
                f", safety_attributes={self.safety_attributes!r}"
                ")"
            )

    @property
    def raw_prediction_response(self) -> aiplatform.models.Prediction:
        """Raw prediction response."""
        return self._prediction_response


@dataclasses.dataclass
class MultiCandidateTextGenerationResponse(TextGenerationResponse):
    """Represents a multi-candidate response of a language model.

    Attributes:
        text: The generated text for the first candidate.
        is_blocked: Whether the first candidate response was blocked.
        safety_attributes: Scores for safety attributes for the first candidate.
            Learn more about the safety attributes here:
            https://cloud.google.com/vertex-ai/docs/generative-ai/learn/responsible-ai#safety_attribute_descriptions
        grounding_metadata: Grounding metadata for the first candidate.
        candidates: The candidate responses.
            Usually contains a single candidate unless `candidate_count` is used.
    """

    __module__ = "vertexai.language_models"

    candidates: List[TextGenerationResponse] = dataclasses.field(default_factory=list)

    def _repr_pretty_(self, p, cycle):
        """Pretty prints self in IPython environments."""
        if cycle:
            p.text(f"{self.__class__.__name__}(...)")
        else:
            if len(self.candidates) == 1:
                p.text(repr(self.candidates[0]))
            else:
                p.text(repr(self))


class _TextGenerationModel(_LanguageModel):
    """TextGenerationModel represents a general language model.

    Examples::

        # Getting answers:
        model = TextGenerationModel.from_pretrained("text-bison@001")
        model.predict("What is life?")
    """

    _LAUNCH_STAGE = _model_garden_models._SDK_GA_LAUNCH_STAGE

    _INSTANCE_SCHEMA_URI = "gs://google-cloud-aiplatform/schema/predict/instance/text_generation_1.0.0.yaml"

    _DEFAULT_MAX_OUTPUT_TOKENS = 128

    def predict(
        self,
        prompt: str,
        *,
        max_output_tokens: Optional[int] = _DEFAULT_MAX_OUTPUT_TOKENS,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
        candidate_count: Optional[int] = None,
        grounding_source: Optional[
            Union[GroundingSource.WebSearch, GroundingSource.VertexAISearch]
        ] = None,
    ) -> "MultiCandidateTextGenerationResponse":
        """Gets model response for a single prompt.

        Args:
            prompt: Question to ask the model.
            max_output_tokens: Max length of the output text in tokens. Range: [1, 1024].
            temperature: Controls the randomness of predictions. Range: [0, 1]. Default: 0.
            top_k: The number of highest probability vocabulary tokens to keep for top-k-filtering. Range: [1, 40]. Default: 40.
            top_p: The cumulative probability of parameter highest probability vocabulary tokens to keep for nucleus sampling. Range: [0, 1]. Default: 0.95.
            stop_sequences: Customized stop sequences to stop the decoding process.
            candidate_count: Number of response candidates to return.
            grounding_source: If specified, grounding feature will be enabled using the grounding source. Default: None.

        Returns:
            A `MultiCandidateTextGenerationResponse` object that contains the text produced by the model.
        """
        prediction_request = _create_text_generation_prediction_request(
            prompt=prompt,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            stop_sequences=stop_sequences,
            candidate_count=candidate_count,
            grounding_source=grounding_source,
        )

        prediction_response = self._endpoint.predict(
            instances=[prediction_request.instance],
            parameters=prediction_request.parameters,
        )

        return _parse_text_generation_model_multi_candidate_response(
            prediction_response
        )

    async def predict_async(
        self,
        prompt: str,
        *,
        max_output_tokens: Optional[int] = _DEFAULT_MAX_OUTPUT_TOKENS,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
        candidate_count: Optional[int] = None,
        grounding_source: Optional[
            Union[GroundingSource.WebSearch, GroundingSource.VertexAISearch]
        ] = None,
    ) -> "MultiCandidateTextGenerationResponse":
        """Asynchronously gets model response for a single prompt.

        Args:
            prompt: Question to ask the model.
            max_output_tokens: Max length of the output text in tokens. Range: [1, 1024].
            temperature: Controls the randomness of predictions. Range: [0, 1]. Default: 0.
            top_k: The number of highest probability vocabulary tokens to keep for top-k-filtering. Range: [1, 40]. Default: 40.
            top_p: The cumulative probability of parameter highest probability vocabulary tokens to keep for nucleus sampling. Range: [0, 1]. Default: 0.95.
            stop_sequences: Customized stop sequences to stop the decoding process.
            candidate_count: Number of response candidates to return.
            grounding_source: If specified, grounding feature will be enabled using the grounding source. Default: None.

        Returns:
            A `MultiCandidateTextGenerationResponse` object that contains the text produced by the model.
        """
        prediction_request = _create_text_generation_prediction_request(
            prompt=prompt,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            stop_sequences=stop_sequences,
            candidate_count=candidate_count,
            grounding_source=grounding_source,
        )

        prediction_response = await self._endpoint.predict_async(
            instances=[prediction_request.instance],
            parameters=prediction_request.parameters,
        )

        return _parse_text_generation_model_multi_candidate_response(
            prediction_response
        )

    def predict_streaming(
        self,
        prompt: str,
        *,
        max_output_tokens: int = _DEFAULT_MAX_OUTPUT_TOKENS,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> Iterator[TextGenerationResponse]:
        """Gets a streaming model response for a single prompt.

        The result is a stream (generator) of partial responses.

        Args:
            prompt: Question to ask the model.
            max_output_tokens: Max length of the output text in tokens. Range: [1, 1024].
            temperature: Controls the randomness of predictions. Range: [0, 1]. Default: 0.
            top_k: The number of highest probability vocabulary tokens to keep for top-k-filtering. Range: [1, 40]. Default: 40.
            top_p: The cumulative probability of parameter highest probability vocabulary tokens to keep for nucleus sampling. Range: [0, 1]. Default: 0.95.
            stop_sequences: Customized stop sequences to stop the decoding process.

        Yields:
            A stream of `TextGenerationResponse` objects that contain partial
            responses produced by the model.
        """
        prediction_request = _create_text_generation_prediction_request(
            prompt=prompt,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            stop_sequences=stop_sequences,
        )

        prediction_service_client = self._endpoint._prediction_client
        for (
            prediction_dict
        ) in _streaming_prediction.predict_stream_of_dicts_from_single_dict(
            prediction_service_client=prediction_service_client,
            endpoint_name=self._endpoint_name,
            instance=prediction_request.instance,
            parameters=prediction_request.parameters,
        ):
            prediction_obj = aiplatform.models.Prediction(
                predictions=[prediction_dict],
                deployed_model_id="",
            )
            yield _parse_text_generation_model_response(prediction_obj)

    async def predict_streaming_async(
        self,
        prompt: str,
        *,
        max_output_tokens: int = _DEFAULT_MAX_OUTPUT_TOKENS,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> AsyncIterator[TextGenerationResponse]:
        """Asynchronously gets a streaming model response for a single prompt.

        The result is a stream (generator) of partial responses.

        Args:
            prompt: Question to ask the model.
            max_output_tokens: Max length of the output text in tokens. Range: [1, 1024].
            temperature: Controls the randomness of predictions. Range: [0, 1]. Default: 0.
            top_k: The number of highest probability vocabulary tokens to keep for top-k-filtering. Range: [1, 40]. Default: 40.
            top_p: The cumulative probability of parameter highest probability vocabulary tokens to keep for nucleus sampling. Range: [0, 1]. Default: 0.95.
            stop_sequences: Customized stop sequences to stop the decoding process.

        Yields:
            A stream of `TextGenerationResponse` objects that contain partial
            responses produced by the model.
        """
        prediction_request = _create_text_generation_prediction_request(
            prompt=prompt,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            stop_sequences=stop_sequences,
        )

        prediction_service_async_client = self._endpoint._prediction_async_client
        async for prediction_dict in _streaming_prediction.predict_stream_of_dicts_from_single_dict_async(
            prediction_service_async_client=prediction_service_async_client,
            endpoint_name=self._endpoint_name,
            instance=prediction_request.instance,
            parameters=prediction_request.parameters,
        ):
            prediction_obj = aiplatform.models.Prediction(
                predictions=[prediction_dict],
                deployed_model_id="",
            )
            yield _parse_text_generation_model_response(prediction_obj)


def _create_text_generation_prediction_request(
    prompt: str,
    *,
    max_output_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    top_k: Optional[int] = None,
    top_p: Optional[float] = None,
    stop_sequences: Optional[List[str]] = None,
    candidate_count: Optional[int] = None,
    grounding_source: Optional[
        Union[GroundingSource.WebSearch, GroundingSource.VertexAISearch]
    ] = None,
) -> "_PredictionRequest":
    """Prepares the text generation request for a single prompt.

    Args:
        prompt: Question to ask the model.
        max_output_tokens: Max length of the output text in tokens. Range: [1, 1024].
        temperature: Controls the randomness of predictions. Range: [0, 1]. Default: 0.
        top_k: The number of highest probability vocabulary tokens to keep for top-k-filtering. Range: [1, 40]. Default: 40.
        top_p: The cumulative probability of parameter highest probability vocabulary tokens to keep for nucleus sampling. Range: [0, 1]. Default: 0.95.
        stop_sequences: Customized stop sequences to stop the decoding process.
        candidate_count: Number of candidates to return.
        grounding_source: If specified, grounding feature will be enabled using the grounding source. Default: None.


    Returns:
        A `_PredictionRequest` object that contains prediction instance and parameters.
    """
    instance = {"content": prompt}
    prediction_parameters = {}

    if max_output_tokens:
        prediction_parameters["maxDecodeSteps"] = max_output_tokens

    if temperature is not None:
        if isinstance(temperature, int):
            temperature = float(temperature)
        prediction_parameters["temperature"] = temperature

    if top_p:
        if isinstance(top_p, int):
            top_p = float(top_p)
        prediction_parameters["topP"] = top_p

    if top_k:
        prediction_parameters["topK"] = top_k

    if stop_sequences:
        prediction_parameters["stopSequences"] = stop_sequences

    if candidate_count is not None:
        prediction_parameters["candidateCount"] = candidate_count

    if grounding_source is not None:
        sources = [grounding_source._to_grounding_source_dict()]
        prediction_parameters["groundingConfig"] = {"sources": sources}

    return _PredictionRequest(
        instance=instance,
        parameters=prediction_parameters,
    )


def _parse_text_generation_model_response(
    prediction_response: aiplatform.models.Prediction,
    prediction_idx: int = 0,
) -> TextGenerationResponse:
    """Converts the raw text_generation model response to `TextGenerationResponse`."""
    prediction = prediction_response.predictions[prediction_idx]
    safety_attributes_dict = prediction.get("safetyAttributes", {})
    grounding_metadata_dict = prediction.get("groundingMetadata", {})
    return TextGenerationResponse(
        text=prediction["content"],
        _prediction_response=prediction_response,
        is_blocked=safety_attributes_dict.get("blocked", False),
        safety_attributes=dict(
            zip(
                safety_attributes_dict.get("categories") or [],
                safety_attributes_dict.get("scores") or [],
            )
        ),
        grounding_metadata=GroundingMetadata(grounding_metadata_dict),
    )


def _parse_text_generation_model_multi_candidate_response(
    prediction_response: aiplatform.models.Prediction,
) -> MultiCandidateTextGenerationResponse:
    """Converts the raw text_generation model response to `MultiCandidateTextGenerationResponse`."""
    # The contract for the PredictionService is that there is a 1:1 mapping
    # between request `instances` and response `predictions`.
    # Unfortunetely, the text-bison models violate this contract.

    prediction_count = len(prediction_response.predictions)
    candidates = []
    for prediction_idx in range(prediction_count):
        candidate = _parse_text_generation_model_response(
            prediction_response=prediction_response,
            prediction_idx=prediction_idx,
        )
        candidates.append(candidate)

    return MultiCandidateTextGenerationResponse(
        text=candidates[0].text,
        _prediction_response=prediction_response,
        is_blocked=candidates[0].is_blocked,
        safety_attributes=candidates[0].safety_attributes,
        grounding_metadata=candidates[0].grounding_metadata,
        candidates=candidates,
    )


class _ModelWithBatchPredict(_LanguageModel):
    """Model that supports batch prediction."""

    def batch_predict(
        self,
        *,
        dataset: Union[str, List[str]],
        destination_uri_prefix: str,
        model_parameters: Optional[Dict] = None,
    ) -> aiplatform.BatchPredictionJob:
        """Starts a batch prediction job with the model.

        Args:
            dataset: The location of the dataset.
                `gs://` and `bq://` URIs are supported.
            destination_uri_prefix: The URI prefix for the prediction.
                `gs://` and `bq://` URIs are supported.
            model_parameters: Model-specific parameters to send to the model.

        Returns:
            A `BatchPredictionJob` object
        Raises:
            ValueError: When source or destination URI is not supported.
        """
        arguments = {}
        first_source_uri = dataset if isinstance(dataset, str) else dataset[0]
        if first_source_uri.startswith("gs://"):
            if not isinstance(dataset, str):
                if not all(uri.startswith("gs://") for uri in dataset):
                    raise ValueError(
                        f"All URIs in the list must start with 'gs://': {dataset}"
                    )
            arguments["gcs_source"] = dataset
        elif first_source_uri.startswith("bq://"):
            if not isinstance(dataset, str):
                raise ValueError(
                    f"Only single BigQuery source can be specified: {dataset}"
                )
            arguments["bigquery_source"] = dataset
        else:
            raise ValueError(f"Unsupported source_uri: {dataset}")

        if destination_uri_prefix.startswith("gs://"):
            arguments["gcs_destination_prefix"] = destination_uri_prefix
        elif destination_uri_prefix.startswith("bq://"):
            arguments["bigquery_destination_prefix"] = destination_uri_prefix
        else:
            raise ValueError(f"Unsupported destination_uri: {destination_uri_prefix}")

        model_name = self._model_resource_name

        job = aiplatform.BatchPredictionJob.create(
            model_name=model_name,
            job_display_name=None,
            **arguments,
            model_parameters=model_parameters,
        )
        return job


class _PreviewModelWithBatchPredict(_ModelWithBatchPredict):
    """Model that supports batch prediction."""

    def batch_predict(
        self,
        *,
        destination_uri_prefix: str,
        dataset: Optional[Union[str, List[str]]] = None,
        model_parameters: Optional[Dict] = None,
        **_kwargs: Optional[Dict[str, Any]],
    ) -> aiplatform.BatchPredictionJob:
        """Starts a batch prediction job with the model.

        Args:
            dataset: Required. The location of the dataset.
                `gs://` and `bq://` URIs are supported.
            destination_uri_prefix: The URI prefix for the prediction.
                `gs://` and `bq://` URIs are supported.
            model_parameters: Model-specific parameters to send to the model.
            **_kwargs: Deprecated.

        Returns:
            A `BatchPredictionJob` object
        Raises:
            ValueError: When source or destination URI is not supported.
        """
        if "source_uri" in _kwargs:
            warnings.warn("source_uri is deprecated, use dataset instead.")
            if dataset:
                raise ValueError("source_uri is deprecated, use dataset instead.")
            dataset = _kwargs["source_uri"]
        if not dataset:
            raise ValueError("dataset must be specified")
        return super().batch_predict(
            dataset=dataset,
            destination_uri_prefix=destination_uri_prefix,
            model_parameters=model_parameters,
        )


class TextGenerationModel(
    _TextGenerationModel, _TunableTextModelMixin, _ModelWithBatchPredict
):
    __module__ = "vertexai.language_models"


class _PreviewTextGenerationModel(
    _TextGenerationModel,
    _PreviewTunableTextModelMixin,
    _PreviewModelWithBatchPredict,
    _evaluatable_language_models._EvaluatableLanguageModel,
    _CountTokensMixin,
):
    # Do not add docstring so that it's inherited from the base class.
    __name__ = "TextGenerationModel"
    __module__ = "vertexai.preview.language_models"

    _LAUNCH_STAGE = _model_garden_models._SDK_PUBLIC_PREVIEW_LAUNCH_STAGE


class _ChatModel(_TextGenerationModel):
    """ChatModel represents a language model that is capable of chat.

    Examples::

        # Getting answers:
        model = ChatModel.from_pretrained("chat-bison@001")
        model.predict("What is life?")

        # Chat:
        chat = model.start_chat()

        chat.send_message("Do you know any cool events this weekend?")
    """

    def start_chat(
        self,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
    ) -> "_ChatSession":
        """Starts a chat session with the model.

        Args:
            max_output_tokens: Max length of the output text in tokens. Range: [1, 1024].
            temperature: Controls the randomness of predictions. Range: [0, 1]. Default: 0.
            top_k: The number of highest probability vocabulary tokens to keep for top-k-filtering. Range: [1, 40]. Default: 40.
            top_p: The cumulative probability of parameter highest probability vocabulary tokens to keep for nucleus sampling. Range: [0, 1]. Default: 0.95.

        Returns:
            A `ChatSession` object.
        """
        return _ChatSession(
            model=self,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
        )


class _ChatSession:
    """ChatSession represents a chat session with a language model.

    Within a chat session, the model keeps context and remembers the previous conversation.
    """

    def __init__(
        self,
        model: _ChatModel,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
    ):
        self._model = model
        self._history = []
        self._history_text = ""
        self._max_output_tokens = max_output_tokens
        self._temperature = temperature
        self._top_k = top_k
        self._top_p = top_p

    def send_message(
        self,
        message: str,
        *,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
    ) -> "TextGenerationResponse":
        """Sends message to the language model and gets a response.

        Args:
            message: Message to send to the model
            max_output_tokens: Max length of the output text in tokens. Range: [1, 1024].
                Uses the value specified when calling `ChatModel.start_chat` by default.
            temperature: Controls the randomness of predictions. Range: [0, 1]. Default: 0.
                Uses the value specified when calling `ChatModel.start_chat` by default.
            top_k: The number of highest probability vocabulary tokens to keep for top-k-filtering. Range: [1, 40]. Default: 40.
                Uses the value specified when calling `ChatModel.start_chat` by default.
            top_p: The cumulative probability of parameter highest probability vocabulary tokens to keep for nucleus sampling. Range: [0, 1]. Default: 0.95.
                Uses the value specified when calling `ChatModel.start_chat` by default.

        Returns:
            A `TextGenerationResponse` object that contains the text produced by the model.
        """
        new_history_text = ""
        if self._history_text:
            new_history_text = self._history_text.rstrip("\n") + "\n\n"
        new_history_text += message.rstrip("\n") + "\n"

        response_obj = self._model.predict(
            prompt=new_history_text,
            max_output_tokens=max_output_tokens
            if max_output_tokens is not None
            else self._max_output_tokens,
            temperature=temperature if temperature is not None else self._temperature,
            top_k=top_k if top_k is not None else self._top_k,
            top_p=top_p if top_p is not None else self._top_p,
        )
        response_text = response_obj.text

        self._history.append((message, response_text))
        new_history_text += response_text.rstrip("\n") + "\n"
        self._history_text = new_history_text
        return response_obj


@dataclasses.dataclass
class TextEmbeddingInput:
    """Structural text embedding input.

    Attributes:
        text: The main text content to embed.
        task_type: The name of the downstream task the embeddings will be used for.
            Valid values:
            RETRIEVAL_QUERY
                Specifies the given text is a query in a search/retrieval setting.
            RETRIEVAL_DOCUMENT
                Specifies the given text is a document from the corpus being searched.
            SEMANTIC_SIMILARITY
                Specifies the given text will be used for STS.
            CLASSIFICATION
                Specifies that the given text will be classified.
            CLUSTERING
                Specifies that the embeddings will be used for clustering.
        title: Optional identifier of the text content.
    """

    __module__ = "vertexai.language_models"

    text: str
    task_type: Optional[str] = None
    title: Optional[str] = None


class TextEmbeddingModel(_LanguageModel):
    """TextEmbeddingModel class calculates embeddings for the given texts.

    Examples::

        # Getting embedding:
        model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
        embeddings = model.get_embeddings(["What is life?"])
        for embedding in embeddings:
            vector = embedding.values
            print(len(vector))
    """

    __module__ = "vertexai.language_models"

    _LAUNCH_STAGE = _model_garden_models._SDK_GA_LAUNCH_STAGE

    _INSTANCE_SCHEMA_URI = (
        "gs://google-cloud-aiplatform/schema/predict/instance/text_embedding_1.0.0.yaml"
    )

    def _prepare_text_embedding_request(
        self,
        texts: List[Union[str, TextEmbeddingInput]],
        *,
        auto_truncate: bool = True,
    ) -> _MultiInstancePredictionRequest:
        """Asynchronously calculates embeddings for the given texts.

        Args:
            texts(str): A list of texts or `TextEmbeddingInput` objects to embed.
            auto_truncate(bool): Whether to automatically truncate long texts. Default: True.

        Returns:
            A `_MultiInstancePredictionRequest` object.
        """
        instances = []
        for text in texts:
            if isinstance(text, TextEmbeddingInput):
                instance = {"content": text.text}
                if text.task_type:
                    instance["task_type"] = text.task_type
                if text.title:
                    instance["title"] = text.title
            elif isinstance(text, str):
                instance = {"content": text}
            else:
                raise TypeError(f"Unsupported text embedding input type: {text}.")
            instances.append(instance)
        parameters = {"autoTruncate": auto_truncate}
        return _MultiInstancePredictionRequest(
            instances=instances,
            parameters=parameters,
        )

    def _parse_text_embedding_response(
        self,
        prediction_response: aiplatform.models.Prediction,
        prediction_idx: int = 0,
    ) -> "TextEmbedding":
        """Parses the text embedding model response."""
        prediction = prediction_response.predictions[prediction_idx]
        embeddings = prediction["embeddings"]
        statistics = embeddings["statistics"]
        return TextEmbedding(
            values=embeddings["values"],
            statistics=TextEmbeddingStatistics(
                token_count=statistics["token_count"],
                truncated=statistics["truncated"],
            ),
            _prediction_response=prediction_response,
        )

    def get_embeddings(
        self,
        texts: List[Union[str, TextEmbeddingInput]],
        *,
        auto_truncate: bool = True,
    ) -> List["TextEmbedding"]:
        """Calculates embeddings for the given texts.

        Args:
            texts(str): A list of texts or `TextEmbeddingInput` objects to embed.
            auto_truncate(bool): Whether to automatically truncate long texts. Default: True.

        Returns:
            A list of `TextEmbedding` objects.
        """
        prediction_request = self._prepare_text_embedding_request(
            texts=texts,
            auto_truncate=auto_truncate,
        )

        prediction_response = self._endpoint.predict(
            instances=prediction_request.instances,
            parameters=prediction_request.parameters,
        )

        results = []
        for prediction_idx in range(len(prediction_response.predictions)):
            result = self._parse_text_embedding_response(
                prediction_response=prediction_response,
                prediction_idx=prediction_idx,
            )
            results.append(result)

        return results

    async def get_embeddings_async(
        self,
        texts: List[Union[str, TextEmbeddingInput]],
        *,
        auto_truncate: bool = True,
    ) -> List["TextEmbedding"]:
        """Asynchronously calculates embeddings for the given texts.

        Args:
            texts(str): A list of texts or `TextEmbeddingInput` objects to embed.
            auto_truncate(bool): Whether to automatically truncate long texts. Default: True.

        Returns:
            A list of `TextEmbedding` objects.
        """
        prediction_request = self._prepare_text_embedding_request(
            texts=texts,
            auto_truncate=auto_truncate,
        )

        prediction_response = await self._endpoint.predict_async(
            instances=prediction_request.instances,
            parameters=prediction_request.parameters,
        )

        results = []
        for prediction_idx in range(len(prediction_response.predictions)):
            result = self._parse_text_embedding_response(
                prediction_response=prediction_response,
                prediction_idx=prediction_idx,
            )
            results.append(result)

        return results


class _PreviewTextEmbeddingModel(
    TextEmbeddingModel, _ModelWithBatchPredict, _CountTokensMixin
):
    __name__ = "TextEmbeddingModel"
    __module__ = "vertexai.preview.language_models"

    _LAUNCH_STAGE = _model_garden_models._SDK_PUBLIC_PREVIEW_LAUNCH_STAGE


@dataclasses.dataclass
class TextEmbeddingStatistics:
    """Text embedding statistics."""

    __module__ = "vertexai.language_models"

    token_count: int
    truncated: bool


@dataclasses.dataclass
class TextEmbedding:
    """Text embedding vector and statistics."""

    __module__ = "vertexai.language_models"

    values: List[float]
    statistics: Optional[TextEmbeddingStatistics] = None
    _prediction_response: Optional[aiplatform.models.Prediction] = None


@dataclasses.dataclass
class InputOutputTextPair:
    """InputOutputTextPair represents a pair of input and output texts."""

    __module__ = "vertexai.language_models"

    input_text: str
    output_text: str


@dataclasses.dataclass
class ChatMessage:
    """A chat message.

    Attributes:
        content: Content of the message.
        author: Author of the message.
    """

    __module__ = "vertexai.language_models"

    content: str
    author: str


class _ChatModelBase(_LanguageModel):
    """_ChatModelBase is a base class for chat models."""

    _LAUNCH_STAGE = _model_garden_models._SDK_GA_LAUNCH_STAGE

    def start_chat(
        self,
        *,
        context: Optional[str] = None,
        examples: Optional[List[InputOutputTextPair]] = None,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        message_history: Optional[List[ChatMessage]] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> "ChatSession":
        """Starts a chat session with the model.

        Args:
            context: Context shapes how the model responds throughout the conversation.
                For example, you can use context to specify words the model can or cannot use, topics to focus on or avoid, or the response format or style
            examples: List of structured messages to the model to learn how to respond to the conversation.
                A list of `InputOutputTextPair` objects.
            max_output_tokens: Max length of the output text in tokens. Range: [1, 1024].
            temperature: Controls the randomness of predictions. Range: [0, 1]. Default: 0.
            top_k: The number of highest probability vocabulary tokens to keep for top-k-filtering. Range: [1, 40]. Default: 40.
            top_p: The cumulative probability of parameter highest probability vocabulary tokens to keep for nucleus sampling. Range: [0, 1]. Default: 0.95.
            message_history: A list of previously sent and received messages.
            stop_sequences: Customized stop sequences to stop the decoding process.

        Returns:
            A `ChatSession` object.
        """
        return ChatSession(
            model=self,
            context=context,
            examples=examples,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            message_history=message_history,
            stop_sequences=stop_sequences,
        )


class ChatModel(_ChatModelBase, _TunableChatModelMixin):
    """ChatModel represents a language model that is capable of chat.

    Examples::

        chat_model = ChatModel.from_pretrained("chat-bison@001")

        chat = chat_model.start_chat(
            context="My name is Ned. You are my personal assistant. My favorite movies are Lord of the Rings and Hobbit.",
            examples=[
                InputOutputTextPair(
                    input_text="Who do you work for?",
                    output_text="I work for Ned.",
                ),
                InputOutputTextPair(
                    input_text="What do I like?",
                    output_text="Ned likes watching movies.",
                ),
            ],
            temperature=0.3,
        )

        chat.send_message("Do you know any cool events this weekend?")
    """

    __module__ = "vertexai.language_models"

    _INSTANCE_SCHEMA_URI = "gs://google-cloud-aiplatform/schema/predict/instance/chat_generation_1.0.0.yaml"


class _PreviewChatModel(ChatModel, _PreviewTunableChatModelMixin):
    __name__ = "ChatModel"
    __module__ = "vertexai.preview.language_models"

    _LAUNCH_STAGE = _model_garden_models._SDK_PUBLIC_PREVIEW_LAUNCH_STAGE

    def start_chat(
        self,
        *,
        context: Optional[str] = None,
        examples: Optional[List[InputOutputTextPair]] = None,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        message_history: Optional[List[ChatMessage]] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> "_PreviewChatSession":
        """Starts a chat session with the model.

        Args:
            context: Context shapes how the model responds throughout the conversation.
                For example, you can use context to specify words the model can or cannot use, topics to focus on or avoid, or the response format or style
            examples: List of structured messages to the model to learn how to respond to the conversation.
                A list of `InputOutputTextPair` objects.
            max_output_tokens: Max length of the output text in tokens. Range: [1, 1024].
            temperature: Controls the randomness of predictions. Range: [0, 1]. Default: 0.
            top_k: The number of highest probability vocabulary tokens to keep for top-k-filtering. Range: [1, 40]. Default: 40.
            top_p: The cumulative probability of parameter highest probability vocabulary tokens to keep for nucleus sampling. Range: [0, 1]. Default: 0.95.
            message_history: A list of previously sent and received messages.
            stop_sequences: Customized stop sequences to stop the decoding process.

        Returns:
            A `ChatSession` object.
        """
        return _PreviewChatSession(
            model=self,
            context=context,
            examples=examples,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            message_history=message_history,
            stop_sequences=stop_sequences,
        )

class CodeChatModel(_ChatModelBase, _TunableChatModelMixin):
    """CodeChatModel represents a model that is capable of completing code.

    Examples:
        code_chat_model = CodeChatModel.from_pretrained("codechat-bison@001")

        code_chat = code_chat_model.start_chat(
            context="I'm writing a large-scale enterprise application.",
            max_output_tokens=128,
            temperature=0.2,
        )

        code_chat.send_message("Please help write a function to calculate the min of two numbers")
    """

    __module__ = "vertexai.language_models"

    _INSTANCE_SCHEMA_URI = "gs://google-cloud-aiplatform/schema/predict/instance/codechat_generation_1.0.0.yaml"
    _LAUNCH_STAGE = _model_garden_models._SDK_GA_LAUNCH_STAGE

    def start_chat(
        self,
        *,
        context: Optional[str] = None,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        message_history: Optional[List[ChatMessage]] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> "CodeChatSession":
        """Starts a chat session with the code chat model.

        Args:
            context: Context shapes how the model responds throughout the conversation.
                For example, you can use context to specify words the model can or
                cannot use, topics to focus on or avoid, or the response format or style.
            max_output_tokens: Max length of the output text in tokens. Range: [1, 1000].
            temperature: Controls the randomness of predictions. Range: [0, 1].
            stop_sequences: Customized stop sequences to stop the decoding process.

        Returns:
            A `ChatSession` object.
        """
        return CodeChatSession(
            model=self,
            context=context,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            message_history=message_history,
            stop_sequences=stop_sequences,
        )


class _PreviewCodeChatModel(CodeChatModel):
    __name__ = "CodeChatModel"
    __module__ = "vertexai.preview.language_models"

    _LAUNCH_STAGE = _model_garden_models._SDK_PUBLIC_PREVIEW_LAUNCH_STAGE

    def start_chat(
        self,
        *,
        context: Optional[str] = None,
        examples: Optional[List[InputOutputTextPair]] = None,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        message_history: Optional[List[ChatMessage]] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> "_PreviewCodeChatSession":
        """Starts a chat session with the model.

        Args:
            context: Context shapes how the model responds throughout the conversation.
                For example, you can use context to specify words the model can or cannot use, topics to focus on or avoid, or the response format or style
            examples: List of structured messages to the model to learn how to respond to the conversation.
                A list of `InputOutputTextPair` objects.
            max_output_tokens: Max length of the output text in tokens. Range: [1, 1024].
            temperature: Controls the randomness of predictions. Range: [0, 1]. Default: 0.
            message_history: A list of previously sent and received messages.
            stop_sequences: Customized stop sequences to stop the decoding process.

        Returns:
            A `ChatSession` object.
        """
        return _PreviewCodeChatSession(
            model=self,
            context=context,
            examples=examples,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            message_history=message_history,
            stop_sequences=stop_sequences,
        )


class _ChatSessionBase:
    """_ChatSessionBase is a base class for all chat sessions."""

    USER_AUTHOR = "user"
    MODEL_AUTHOR = "bot"

    def __init__(
        self,
        model: _ChatModelBase,
        context: Optional[str] = None,
        examples: Optional[List[InputOutputTextPair]] = None,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        message_history: Optional[List[ChatMessage]] = None,
        stop_sequences: Optional[List[str]] = None,
    ):
        self._model = model
        self._context = context
        self._examples = examples
        self._max_output_tokens = max_output_tokens
        self._temperature = temperature
        self._top_k = top_k
        self._top_p = top_p
        self._message_history: List[ChatMessage] = message_history or []
        self._stop_sequences = stop_sequences

    @property
    def message_history(self) -> List[ChatMessage]:
        """List of previous messages."""
        return self._message_history

    def _prepare_request(
        self,
        message: str,
        *,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
        candidate_count: Optional[int] = None,
    ) -> _PredictionRequest:
        """Prepares a request for the language model.

        Args:
            message: Message to send to the model
            max_output_tokens: Max length of the output text in tokens. Range: [1, 1024].
                Uses the value specified when calling `ChatModel.start_chat` by default.
            temperature: Controls the randomness of predictions. Range: [0, 1]. Default: 0.
                Uses the value specified when calling `ChatModel.start_chat` by default.
            top_k: The number of highest probability vocabulary tokens to keep for top-k-filtering. Range: [1, 40]. Default: 40.
                Uses the value specified when calling `ChatModel.start_chat` by default.
            top_p: The cumulative probability of parameter highest probability vocabulary tokens to keep for nucleus sampling. Range: [0, 1]. Default: 0.95.
                Uses the value specified when calling `ChatModel.start_chat` by default.
            stop_sequences: Customized stop sequences to stop the decoding process.
            candidate_count: Number of candidates to return.

        Returns:
            A `_PredictionRequest` object.
        """
        prediction_parameters = {}

        max_output_tokens = max_output_tokens or self._max_output_tokens
        if max_output_tokens:
            prediction_parameters["maxDecodeSteps"] = max_output_tokens

        if temperature is None:
            temperature = self._temperature
        if temperature is not None:
            if isinstance(temperature, int):
                temperature = float(temperature)
            prediction_parameters["temperature"] = temperature

        top_p = top_p or self._top_p
        if top_p:
            if isinstance(top_p, int):
                top_p = float(top_p)
            prediction_parameters["topP"] = top_p

        top_k = top_k or self._top_k
        if top_k:
            prediction_parameters["topK"] = top_k

        stop_sequences = stop_sequences or self._stop_sequences
        if stop_sequences:
            prediction_parameters["stopSequences"] = stop_sequences

        if candidate_count is not None:
            prediction_parameters["candidateCount"] = candidate_count

        message_structs = []
        for past_message in self._message_history:
            message_structs.append(
                {
                    "author": past_message.author,
                    "content": past_message.content,
                }
            )
        message_structs.append(
            {
                "author": self.USER_AUTHOR,
                "content": message,
            }
        )

        prediction_instance = {"messages": message_structs}
        if self._context:
            prediction_instance["context"] = self._context
        if self._examples:
            prediction_instance["examples"] = [
                {
                    "input": {"content": example.input_text},
                    "output": {"content": example.output_text},
                }
                for example in self._examples
            ]

        return _PredictionRequest(
            instance=prediction_instance,
            parameters=prediction_parameters,
        )

    @classmethod
    def _parse_chat_prediction_response(
        cls,
        prediction_response: aiplatform.models.Prediction,
        prediction_idx: int = 0,
    ) -> MultiCandidateTextGenerationResponse:
        """Parses prediction response for chat models.

        Args:
            prediction_response: Prediction response received from the model
            prediction_idx: Index of the prediction to parse.
            candidate_idx: Index of the candidate to parse.

        Returns:
            A `MultiCandidateTextGenerationResponse` object.
        """
        prediction = prediction_response.predictions[prediction_idx]
        candidate_count = len(prediction["candidates"])
        candidates = []
        for candidate_idx in range(candidate_count):
            safety_attributes = prediction["safetyAttributes"][candidate_idx]
            candidate_response = TextGenerationResponse(
                text=prediction["candidates"][candidate_idx]["content"],
                _prediction_response=prediction_response,
                is_blocked=safety_attributes.get("blocked", False),
                safety_attributes=dict(
                    zip(
                        # Unlike with normal prediction, in streaming prediction
                        # categories and scores can be None
                        safety_attributes.get("categories") or [],
                        safety_attributes.get("scores") or [],
                    )
                ),
            )
            candidates.append(candidate_response)
        return MultiCandidateTextGenerationResponse(
            text=candidates[0].text,
            _prediction_response=prediction_response,
            is_blocked=candidates[0].is_blocked,
            safety_attributes=candidates[0].safety_attributes,
            candidates=candidates,
        )

    def send_message(
        self,
        message: str,
        *,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
        candidate_count: Optional[int] = None,
    ) -> "MultiCandidateTextGenerationResponse":
        """Sends message to the language model and gets a response.

        Args:
            message: Message to send to the model
            max_output_tokens: Max length of the output text in tokens. Range: [1, 1024].
                Uses the value specified when calling `ChatModel.start_chat` by default.
            temperature: Controls the randomness of predictions. Range: [0, 1]. Default: 0.
                Uses the value specified when calling `ChatModel.start_chat` by default.
            top_k: The number of highest probability vocabulary tokens to keep for top-k-filtering. Range: [1, 40]. Default: 40.
                Uses the value specified when calling `ChatModel.start_chat` by default.
            top_p: The cumulative probability of parameter highest probability vocabulary tokens to keep for nucleus sampling. Range: [0, 1]. Default: 0.95.
                Uses the value specified when calling `ChatModel.start_chat` by default.
            stop_sequences: Customized stop sequences to stop the decoding process.
            candidate_count: Number of candidates to return.

        Returns:
            A `MultiCandidateTextGenerationResponse` object that contains the
            text produced by the model.
        """
        prediction_request = self._prepare_request(
            message=message,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            stop_sequences=stop_sequences,
            candidate_count=candidate_count,
        )

        prediction_response = self._model._endpoint.predict(
            instances=[prediction_request.instance],
            parameters=prediction_request.parameters,
        )
        response_obj = self._parse_chat_prediction_response(
            prediction_response=prediction_response
        )
        response_text = response_obj.text

        self._message_history.append(
            ChatMessage(content=message, author=self.USER_AUTHOR)
        )
        self._message_history.append(
            ChatMessage(content=response_text, author=self.MODEL_AUTHOR)
        )

        return response_obj

    async def send_message_async(
        self,
        message: str,
        *,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
        candidate_count: Optional[int] = None,
    ) -> "MultiCandidateTextGenerationResponse":
        """Asynchronously sends message to the language model and gets a response.

        Args:
            message: Message to send to the model
            max_output_tokens: Max length of the output text in tokens. Range: [1, 1024].
                Uses the value specified when calling `ChatModel.start_chat` by default.
            temperature: Controls the randomness of predictions. Range: [0, 1]. Default: 0.
                Uses the value specified when calling `ChatModel.start_chat` by default.
            top_k: The number of highest probability vocabulary tokens to keep for top-k-filtering. Range: [1, 40]. Default: 40.
                Uses the value specified when calling `ChatModel.start_chat` by default.
            top_p: The cumulative probability of parameter highest probability vocabulary tokens to keep for nucleus sampling. Range: [0, 1]. Default: 0.95.
                Uses the value specified when calling `ChatModel.start_chat` by default.
            stop_sequences: Customized stop sequences to stop the decoding process.
            candidate_count: Number of candidates to return.

        Returns:
            A `MultiCandidateTextGenerationResponse` object that contains
            the text produced by the model.
        """
        prediction_request = self._prepare_request(
            message=message,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            stop_sequences=stop_sequences,
            candidate_count=candidate_count,
        )

        prediction_response = await self._model._endpoint.predict_async(
            instances=[prediction_request.instance],
            parameters=prediction_request.parameters,
        )
        response_obj = self._parse_chat_prediction_response(
            prediction_response=prediction_response
        )
        response_text = response_obj.text

        self._message_history.append(
            ChatMessage(content=message, author=self.USER_AUTHOR)
        )
        self._message_history.append(
            ChatMessage(content=response_text, author=self.MODEL_AUTHOR)
        )

        return response_obj

    def send_message_streaming(
        self,
        message: str,
        *,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> Iterator[TextGenerationResponse]:
        """Sends message to the language model and gets a streamed response.

        The response is only added to the history once it's fully read.

        Args:
            message: Message to send to the model
            max_output_tokens: Max length of the output text in tokens. Range: [1, 1024].
                Uses the value specified when calling `ChatModel.start_chat` by default.
            temperature: Controls the randomness of predictions. Range: [0, 1]. Default: 0.
                Uses the value specified when calling `ChatModel.start_chat` by default.
            top_k: The number of highest probability vocabulary tokens to keep for top-k-filtering. Range: [1, 40]. Default: 40.
                Uses the value specified when calling `ChatModel.start_chat` by default.
            top_p: The cumulative probability of parameter highest probability vocabulary tokens to keep for nucleus sampling. Range: [0, 1]. Default: 0.95.
                Uses the value specified when calling `ChatModel.start_chat` by default.
            stop_sequences: Customized stop sequences to stop the decoding process.
                Uses the value specified when calling `ChatModel.start_chat` by default.

        Yields:
            A stream of `TextGenerationResponse` objects that contain partial
            responses produced by the model.
        """
        prediction_request = self._prepare_request(
            message=message,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            stop_sequences=stop_sequences,
        )

        prediction_service_client = self._model._endpoint._prediction_client

        full_response_text = ""

        for (
            prediction_dict
        ) in _streaming_prediction.predict_stream_of_dicts_from_single_dict(
            prediction_service_client=prediction_service_client,
            endpoint_name=self._model._endpoint_name,
            instance=prediction_request.instance,
            parameters=prediction_request.parameters,
        ):
            prediction_response = aiplatform.models.Prediction(
                predictions=[prediction_dict],
                deployed_model_id="",
            )
            text_generation_response = self._parse_chat_prediction_response(
                prediction_response=prediction_response
            )
            full_response_text += text_generation_response.text
            yield text_generation_response

        # We only add the question and answer to the history if/when the answer
        # was read fully. Otherwise, the answer would have been truncated.
        self._message_history.append(
            ChatMessage(content=message, author=self.USER_AUTHOR)
        )
        self._message_history.append(
            ChatMessage(content=full_response_text, author=self.MODEL_AUTHOR)
        )

    async def send_message_streaming_async(
        self,
        message: str,
        *,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> AsyncIterator[TextGenerationResponse]:
        """Asynchronously sends message to the language model and gets a streamed response.

        The response is only added to the history once it's fully read.

        Args:
            message: Message to send to the model
            max_output_tokens: Max length of the output text in tokens. Range: [1, 1024].
                Uses the value specified when calling `ChatModel.start_chat` by default.
            temperature: Controls the randomness of predictions. Range: [0, 1]. Default: 0.
                Uses the value specified when calling `ChatModel.start_chat` by default.
            top_k: The number of highest probability vocabulary tokens to keep for top-k-filtering. Range: [1, 40]. Default: 40.
                Uses the value specified when calling `ChatModel.start_chat` by default.
            top_p: The cumulative probability of parameter highest probability vocabulary tokens to keep for nucleus sampling. Range: [0, 1]. Default: 0.95.
                Uses the value specified when calling `ChatModel.start_chat` by default.
            stop_sequences: Customized stop sequences to stop the decoding process.
                Uses the value specified when calling `ChatModel.start_chat` by default.

        Yields:
            A stream of `TextGenerationResponse` objects that contain partial
            responses produced by the model.
        """
        prediction_request = self._prepare_request(
            message=message,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            stop_sequences=stop_sequences,
        )

        prediction_service_async_client = self._model._endpoint._prediction_async_client

        full_response_text = ""

        async for prediction_dict in _streaming_prediction.predict_stream_of_dicts_from_single_dict_async(
            prediction_service_async_client=prediction_service_async_client,
            endpoint_name=self._model._endpoint_name,
            instance=prediction_request.instance,
            parameters=prediction_request.parameters,
        ):
            prediction_response = aiplatform.models.Prediction(
                predictions=[prediction_dict],
                deployed_model_id="",
            )
            text_generation_response = self._parse_chat_prediction_response(
                prediction_response=prediction_response
            )
            full_response_text += text_generation_response.text
            yield text_generation_response

        # We only add the question and answer to the history if/when the answer
        # was read fully. Otherwise, the answer would have been truncated.
        self._message_history.append(
            ChatMessage(content=message, author=self.USER_AUTHOR)
        )
        self._message_history.append(
            ChatMessage(content=full_response_text, author=self.MODEL_AUTHOR)
        )


class _ChatSessionBaseWithCountTokensMixin(_ChatSessionBase):
    """A mixin class for adding count_tokens to ChatSession."""

    def count_tokens(
        self,
        message: str,
    ) -> CountTokensResponse:
        """Counts the tokens and billable characters for the provided chat message and any message history,
        context, or examples set on the chat session.

        If you've called `send_message()` in the current chat session before calling `count_tokens()`, the
        response will include the total tokens and characters for the previously sent message and the one in the
        `count_tokens()` request. To count the tokens for a single message, call `count_tokens()` right after
        calling `start_chat()` before calling `send_message()`.

        Note: this does not make a prediction request to the model, it only counts the tokens
        in the request.

        Examples::

        model = ChatModel.from_pretrained("chat-bison@001")
        chat_session = model.start_chat()
        count_tokens_response = chat_session.count_tokens("How's it going?")

        count_tokens_response.total_tokens
        count_tokens_response.total_billable_characters

        Args:
            message (str):
                Required. A chat message to count tokens or. For example: "How's it going?"
        Returns:
            A `CountTokensResponse` object that contains the number of tokens
            in the text and the number of billable characters.
        """

        count_tokens_request = self._prepare_request(message=message)

        count_tokens_response = self._model._endpoint._prediction_client.select_version(
            "v1beta1"
        ).count_tokens(
            endpoint=self._model._endpoint_name,
            instances=[count_tokens_request.instance],
        )

        return CountTokensResponse(
            total_tokens=count_tokens_response.total_tokens,
            total_billable_characters=count_tokens_response.total_billable_characters,
            _count_tokens_response=count_tokens_response,
        )


class _PreviewChatSession(_ChatSessionBaseWithCountTokensMixin):

    __module__ = "vertexai.preview.language_models"


class _PreviewCodeChatSession(_ChatSessionBaseWithCountTokensMixin):

    __module__ = "vertexai.preview.language_models"


class ChatSession(_ChatSessionBase):
    """ChatSession represents a chat session with a language model.

    Within a chat session, the model keeps context and remembers the previous conversation.
    """

    __module__ = "vertexai.language_models"

    def __init__(
        self,
        model: ChatModel,
        context: Optional[str] = None,
        examples: Optional[List[InputOutputTextPair]] = None,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        message_history: Optional[List[ChatMessage]] = None,
        stop_sequences: Optional[List[str]] = None,
    ):
        super().__init__(
            model=model,
            context=context,
            examples=examples,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            message_history=message_history,
            stop_sequences=stop_sequences,
        )


class CodeChatSession(_ChatSessionBase):
    """CodeChatSession represents a chat session with code chat language model.

    Within a code chat session, the model keeps context and remembers the previous converstion.
    """

    __module__ = "vertexai.language_models"

    def __init__(
        self,
        model: CodeChatModel,
        context: Optional[str] = None,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        message_history: Optional[List[ChatMessage]] = None,
        stop_sequences: Optional[List[str]] = None,
    ):
        super().__init__(
            model=model,
            context=context,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            message_history=message_history,
            stop_sequences=stop_sequences,
        )

    def send_message(
        self,
        message: str,
        *,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
        candidate_count: Optional[int] = None,
    ) -> "MultiCandidateTextGenerationResponse":
        """Sends message to the code chat model and gets a response.

        Args:
            message: Message to send to the model
            max_output_tokens: Max length of the output text in tokens. Range: [1, 1000].
                Uses the value specified when calling `CodeChatModel.start_chat` by default.
            temperature: Controls the randomness of predictions. Range: [0, 1].
                 Uses the value specified when calling `CodeChatModel.start_chat` by default.
            stop_sequences: Customized stop sequences to stop the decoding process.
            candidate_count: Number of candidates to return.

        Returns:
            A `MultiCandidateTextGenerationResponse` object that contains the
            text produced by the model.
        """
        return super().send_message(
            message=message,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            stop_sequences=stop_sequences,
            candidate_count=candidate_count,
        )

    async def send_message_async(
        self,
        message: str,
        *,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        candidate_count: Optional[int] = None,
    ) -> "MultiCandidateTextGenerationResponse":
        """Asynchronously sends message to the code chat model and gets a response.

        Args:
            message: Message to send to the model
            max_output_tokens: Max length of the output text in tokens. Range: [1, 1000].
                Uses the value specified when calling `CodeChatModel.start_chat` by default.
            temperature: Controls the randomness of predictions. Range: [0, 1].
                 Uses the value specified when calling `CodeChatModel.start_chat` by default.
            candidate_count: Number of candidates to return.

        Returns:
            A `MultiCandidateTextGenerationResponse` object that contains the
            text produced by the model.
        """
        return super().send_message_async(
            message=message,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            candidate_count=candidate_count,
        )

    def send_message_streaming(
        self,
        message: str,
        *,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> Iterator[TextGenerationResponse]:
        """Sends message to the language model and gets a streamed response.

        The response is only added to the history once it's fully read.

        Args:
            message: Message to send to the model
            max_output_tokens: Max length of the output text in tokens. Range: [1, 1024].
                Uses the value specified when calling `ChatModel.start_chat` by default.
            temperature: Controls the randomness of predictions. Range: [0, 1]. Default: 0.
                Uses the value specified when calling `ChatModel.start_chat` by default.
            stop_sequences: Customized stop sequences to stop the decoding process.
                Uses the value specified when calling `ChatModel.start_chat` by default.

        Returns:
            A stream of `TextGenerationResponse` objects that contain partial
            responses produced by the model.
        """
        return super().send_message_streaming(
            message=message,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            stop_sequences=stop_sequences,
        )

    def send_message_streaming_async(
        self,
        message: str,
        *,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> AsyncIterator[TextGenerationResponse]:
        """Asynchronously sends message to the language model and gets a streamed response.

        The response is only added to the history once it's fully read.

        Args:
            message: Message to send to the model
            max_output_tokens: Max length of the output text in tokens. Range: [1, 1024].
                Uses the value specified when calling `ChatModel.start_chat` by default.
            temperature: Controls the randomness of predictions. Range: [0, 1]. Default: 0.
                Uses the value specified when calling `ChatModel.start_chat` by default.
            stop_sequences: Customized stop sequences to stop the decoding process.
                Uses the value specified when calling `ChatModel.start_chat` by default.

        Returns:
            A stream of `TextGenerationResponse` objects that contain partial
            responses produced by the model.
        """
        return super().send_message_streaming_async(
            message=message,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            stop_sequences=stop_sequences,
        )


class _CodeGenerationModel(_LanguageModel):
    """A language model that generates code.

    Examples:

        # Getting answers:
        generation_model = CodeGenerationModel.from_pretrained("code-bison@001")
        print(generation_model.predict(
            prefix="Write a function that checks if a year is a leap year.",
        ))

        completion_model = CodeGenerationModel.from_pretrained("code-gecko@001")
        print(completion_model.predict(
            prefix="def reverse_string(s):",
        ))
    """

    __module__ = "vertexai.language_models"

    _INSTANCE_SCHEMA_URI = "gs://google-cloud-aiplatform/schema/predict/instance/code_generation_1.0.0.yaml"

    _LAUNCH_STAGE = _model_garden_models._SDK_GA_LAUNCH_STAGE

    def _create_prediction_request(
        self,
        prefix: str,
        suffix: Optional[str] = None,
        *,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
        candidate_count: Optional[int] = None,
    ) -> _PredictionRequest:
        """Creates a code generation prediction request.

        Args:
            prefix: Code before the current point.
            suffix: Code after the current point.
            max_output_tokens: Max length of the output text in tokens. Range: [1, 1000].
            temperature: Controls the randomness of predictions. Range: [0, 1].
            stop_sequences: Customized stop sequences to stop the decoding process.
            candidate_count: Number of response candidates to return.

        Returns:
            A `TextGenerationResponse` object that contains the text produced by the model.
        """
        instance = {"prefix": prefix}
        if suffix:
            instance["suffix"] = suffix

        prediction_parameters = {}

        if temperature is not None:
            if isinstance(temperature, int):
                temperature = float(temperature)
            prediction_parameters["temperature"] = temperature

        if max_output_tokens:
            prediction_parameters["maxOutputTokens"] = max_output_tokens

        if stop_sequences:
            prediction_parameters["stopSequences"] = stop_sequences

        if candidate_count is not None:
            prediction_parameters["candidateCount"] = candidate_count

        return _PredictionRequest(instance=instance, parameters=prediction_parameters)

    def predict(
        self,
        prefix: str,
        suffix: Optional[str] = None,
        *,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
        candidate_count: Optional[int] = None,
    ) -> "TextGenerationResponse":
        """Gets model response for a single prompt.

        Args:
            prefix: Code before the current point.
            suffix: Code after the current point.
            max_output_tokens: Max length of the output text in tokens. Range: [1, 1000].
            temperature: Controls the randomness of predictions. Range: [0, 1].
            stop_sequences: Customized stop sequences to stop the decoding process.
            candidate_count: Number of response candidates to return.

        Returns:
            A `MultiCandidateTextGenerationResponse` object that contains the
            text produced by the model.
        """
        prediction_request = self._create_prediction_request(
            prefix=prefix,
            suffix=suffix,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            stop_sequences=stop_sequences,
            candidate_count=candidate_count,
        )

        prediction_response = self._endpoint.predict(
            instances=[prediction_request.instance],
            parameters=prediction_request.parameters,
        )
        return _parse_text_generation_model_multi_candidate_response(
            prediction_response
        )

    async def predict_async(
        self,
        prefix: str,
        suffix: Optional[str] = None,
        *,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
        candidate_count: Optional[int] = None,
    ) -> "TextGenerationResponse":
        """Asynchronously gets model response for a single prompt.

        Args:
            prefix: Code before the current point.
            suffix: Code after the current point.
            max_output_tokens: Max length of the output text in tokens. Range: [1, 1000].
            temperature: Controls the randomness of predictions. Range: [0, 1].
            stop_sequences: Customized stop sequences to stop the decoding process.
            candidate_count: Number of response candidates to return.

        Returns:
            A `MultiCandidateTextGenerationResponse` object that contains the
            text produced by the model.
        """
        prediction_request = self._create_prediction_request(
            prefix=prefix,
            suffix=suffix,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            stop_sequences=stop_sequences,
            candidate_count=candidate_count,
        )

        prediction_response = await self._endpoint.predict_async(
            instances=[prediction_request.instance],
            parameters=prediction_request.parameters,
        )
        return _parse_text_generation_model_multi_candidate_response(
            prediction_response
        )

    def predict_streaming(
        self,
        prefix: str,
        suffix: Optional[str] = None,
        *,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> Iterator[TextGenerationResponse]:
        """Predicts the code based on previous code.

        The result is a stream (generator) of partial responses.

        Args:
            prefix: Code before the current point.
            suffix: Code after the current point.
            max_output_tokens: Max length of the output text in tokens. Range: [1, 1000].
            temperature: Controls the randomness of predictions. Range: [0, 1].
            stop_sequences: Customized stop sequences to stop the decoding process.

        Yields:
            A stream of `TextGenerationResponse` objects that contain partial
            responses produced by the model.
        """
        prediction_request = self._create_prediction_request(
            prefix=prefix,
            suffix=suffix,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            stop_sequences=stop_sequences,
        )

        prediction_service_client = self._endpoint._prediction_client
        for (
            prediction_dict
        ) in _streaming_prediction.predict_stream_of_dicts_from_single_dict(
            prediction_service_client=prediction_service_client,
            endpoint_name=self._endpoint_name,
            instance=prediction_request.instance,
            parameters=prediction_request.parameters,
        ):
            prediction_obj = aiplatform.models.Prediction(
                predictions=[prediction_dict],
                deployed_model_id="",
            )
            yield _parse_text_generation_model_response(prediction_obj)

    async def predict_streaming_async(
        self,
        prefix: str,
        suffix: Optional[str] = None,
        *,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> AsyncIterator[TextGenerationResponse]:
        """Asynchronously predicts the code based on previous code.

        The result is a stream (generator) of partial responses.

        Args:
            prefix: Code before the current point.
            suffix: Code after the current point.
            max_output_tokens: Max length of the output text in tokens. Range: [1, 1000].
            temperature: Controls the randomness of predictions. Range: [0, 1].
            stop_sequences: Customized stop sequences to stop the decoding process.

        Yields:
            A stream of `TextGenerationResponse` objects that contain partial
            responses produced by the model.
        """
        prediction_request = self._create_prediction_request(
            prefix=prefix,
            suffix=suffix,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            stop_sequences=stop_sequences,
        )

        prediction_service_async_client = self._endpoint._prediction_async_client
        async for prediction_dict in _streaming_prediction.predict_stream_of_dicts_from_single_dict_async(
            prediction_service_async_client=prediction_service_async_client,
            endpoint_name=self._endpoint_name,
            instance=prediction_request.instance,
            parameters=prediction_request.parameters,
        ):
            prediction_obj = aiplatform.models.Prediction(
                predictions=[prediction_dict],
                deployed_model_id="",
            )
            yield _parse_text_generation_model_response(prediction_obj)


class _CountTokensCodeGenerationMixin(_LanguageModel):
    """Mixin for code generation models that support the CountTokens API"""

    def count_tokens(
        self,
        prefix: str,
        *,
        suffix: Optional[str] = None,
    ) -> CountTokensResponse:
        """Counts the tokens and billable characters for a given code generation prompt.

        Note: this does not make a prediction request to the model, it only counts the tokens
        in the request.

        Args:
            prefix (str): Code before the current point.
            suffix (str): Code after the current point.

        Returns:
            A `CountTokensResponse` object that contains the number of tokens
            in the text and the number of billable characters.
        """
        prediction_request = {"prefix": prefix, "suffix": suffix}

        count_tokens_response = self._endpoint._prediction_client.select_version(
            "v1beta1"
        ).count_tokens(
            endpoint=self._endpoint_name,
            instances=[prediction_request],
        )

        return CountTokensResponse(
            total_tokens=count_tokens_response.total_tokens,
            total_billable_characters=count_tokens_response.total_billable_characters,
            _count_tokens_response=count_tokens_response,
        )


class CodeGenerationModel(_CodeGenerationModel, _TunableTextModelMixin):
    pass


class _PreviewCodeGenerationModel(CodeGenerationModel, _CountTokensCodeGenerationMixin):
    __name__ = "CodeGenerationModel"
    __module__ = "vertexai.preview.language_models"

    _LAUNCH_STAGE = _model_garden_models._SDK_PUBLIC_PREVIEW_LAUNCH_STAGE


###### Model tuning
# Currently, tuning can only work in this location

_SUPPORTED_LOCATIONS = [
    # 1
    "us-central1",
    "europe-west4",
    "asia-southeast1",
    # 2
    "us-west1",
    "europe-west3",
    "europe-west2",
    "asia-northeast1",
    # 3
    "us-east4",
    "us-west4",
    "northamerica-northeast1",
    "europe-west9",
    "europe-west1",
    "asia-northeast3",
]

_TUNING_LOCATIONS = _SUPPORTED_LOCATIONS
# Currently, deployment can only work in these locations
_TUNED_MODEL_LOCATIONS = _SUPPORTED_LOCATIONS


class _LanguageModelTuningJob:
    """LanguageModelTuningJob represents a fine-tuning job."""

    def __init__(
        self,
        base_model: _LanguageModel,
        job: aiplatform.PipelineJob,
    ):
        """Internal constructor. Do not call directly."""
        self._base_model = base_model
        self._job = job
        self._model: Optional[_LanguageModel] = None

    def get_tuned_model(self) -> "_LanguageModel":
        """Blocks until the tuning is complete and returns a `LanguageModel` object."""
        if self._model:
            return self._model
        self._job.wait()
        root_pipeline_tasks = [
            task_detail
            for task_detail in self._job.gca_resource.job_detail.task_details
            if task_detail.execution.schema_title == "system.Run"
        ]
        if len(root_pipeline_tasks) != 1:
            raise RuntimeError(
                f"Failed to get the model name from the tuning pipeline: {self._job.name}"
            )
        root_pipeline_task = root_pipeline_tasks[0]

        # Trying to get model name from output parameter
        vertex_model_name = root_pipeline_task.execution.metadata[
            "output:model_resource_name"
        ].strip()
        _LOGGER.info(f"Tuning has completed. Created Vertex Model: {vertex_model_name}")
        self._model = type(self._base_model).get_tuned_model(
            tuned_model_name=vertex_model_name
        )
        return self._model

    @property
    def _status(self) -> Optional[aiplatform_types.pipeline_state.PipelineState]:
        """Job status."""
        return self._job.state

    def _cancel(self):
        """Cancels the job."""
        self._job.cancel()


def _get_tuned_models_dir_uri(model_id: str) -> str:
    if aiplatform_initializer.global_config.staging_bucket:
        return (
            aiplatform_initializer.global_config.staging_bucket
            + "/tuned_language_models/"
            + model_id
        )
    staging_gcs_bucket = (
        gcs_utils.create_gcs_bucket_for_pipeline_artifacts_if_it_does_not_exist()
    )
    return (
        staging_gcs_bucket.replace("/output_artifacts/", "/tuned_language_models/")
        + model_id
    )


def _list_tuned_model_names(model_id: str) -> List[str]:
    tuned_models = aiplatform.Model.list(
        filter=f'labels.{_TUNING_BASE_MODEL_ID_LABEL_KEY}="{model_id.replace("@", "-")}"',
        # TODO(b/275444096): Remove the explicit location once models are deployed to the user's selected location
        location=aiplatform_initializer.global_config.location,
    )
    model_names = [model.resource_name for model in tuned_models]
    return model_names


def _generate_tuned_model_dir_uri(model_id: str) -> str:
    tuned_model_id = "tuned_model_" + aiplatform_utils.timestamped_unique_name()
    tuned_models_dir_uri = _get_tuned_models_dir_uri(model_id=model_id)
    tuned_model_dir_uri = _uri_join(tuned_models_dir_uri, tuned_model_id)
    return tuned_model_dir_uri


def _launch_tuning_job(
    training_data: Union[str, "pandas.core.frame.DataFrame"],
    model_id: str,
    tuning_pipeline_uri: str,
    tuning_parameters: Dict[str, Any],
    tuning_job_location: str,
    tuned_model_location: str,
    model_display_name: Optional[str] = None,
) -> aiplatform.PipelineJob:
    output_dir_uri = _generate_tuned_model_dir_uri(model_id=model_id)
    if isinstance(training_data, str):
        dataset_name_or_uri = training_data
    elif pandas and isinstance(training_data, pandas.DataFrame):
        dataset_uri = _uri_join(output_dir_uri, "training_data.jsonl")

        gcs_utils._upload_pandas_df_to_gcs(
            df=training_data, upload_gcs_path=dataset_uri
        )
        dataset_name_or_uri = dataset_uri
    else:
        raise TypeError(f"Unsupported training_data type: {type(training_data)}")

    if not model_display_name:
        # Creating a human-readable model display name
        name = f"{model_id} tuned"

        train_steps = tuning_parameters.get("train_steps")
        if train_steps:
            name += f" for {train_steps} steps"

        learning_rate = tuning_parameters.get("learning_rate")
        if learning_rate:
            name += f" with learning rate {learning_rate}"

        learning_rate_multiplier = tuning_parameters.get("learning_rate_multiplier")
        if learning_rate_multiplier:
            name += f" with learning_rate_multiplier={learning_rate_multiplier}"

        name += " on "
        # Truncating the start of the dataset URI to keep total length <= 128.
        max_display_name_length = 128
        if len(dataset_name_or_uri + name) <= max_display_name_length:
            name += dataset_name_or_uri
        else:
            name += "..."
            remaining_length = max_display_name_length - len(name)
            name += dataset_name_or_uri[-remaining_length:]
        model_display_name = name[:max_display_name_length]

    pipeline_arguments = {
        "project": aiplatform_initializer.global_config.project,
        # TODO(b/275444096): Remove the explicit location once tuning can happen in all regions
        # "location": aiplatform_initializer.global_config.location,
        "location": tuned_model_location,
        "large_model_reference": model_id,
        "model_display_name": model_display_name,
    }

    if dataset_name_or_uri.startswith("projects/"):
        pipeline_arguments["dataset_name"] = dataset_name_or_uri
    if dataset_name_or_uri.startswith("gs://"):
        pipeline_arguments["dataset_uri"] = dataset_name_or_uri
    if aiplatform_initializer.global_config.encryption_spec_key_name:
        pipeline_arguments[
            "encryption_spec_key_name"
        ] = aiplatform_initializer.global_config.encryption_spec_key_name
    pipeline_arguments.update(tuning_parameters)
    job = aiplatform.PipelineJob(
        template_path=tuning_pipeline_uri,
        display_name=None,
        parameter_values=pipeline_arguments,
        # TODO(b/275444101): Remove the explicit location once model can be deployed in all regions
        location=tuning_job_location,
    )
    job.submit()
    return job


def _uri_join(uri: str, path_fragment: str) -> str:
    """Appends path fragment to URI.

    urllib.parse.urljoin only works on URLs, not URIs
    """

    return uri.rstrip("/") + "/" + path_fragment.lstrip("/")
