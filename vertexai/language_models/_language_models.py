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

import dataclasses
import tempfile
from typing import Any, List, Optional, Sequence, Type, Union

from google.cloud import storage

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer as aiplatform_initializer
from google.cloud.aiplatform import models as aiplatform_models
from google.cloud.aiplatform import utils as aiplatform_utils
from google.cloud.aiplatform.preview import _publisher_model
from google.cloud.aiplatform.utils import gcs_utils

try:
    import pandas
except ImportError:
    pandas = None


_LOGGER = base.Logger(__name__)

_TEXT_GENERATION_TUNING_PIPELINE_URI = "https://us-kfp.pkg.dev/vertex-ai/large-language-model-pipelines/tune-large-model/preview"

# Endpoint label/metadata key to preserve the base model ID information
_TUNING_BASE_MODEL_ID_LABEL_KEY = "google-vertex-llm-tuning-base-model-id"

_LLM_TEXT_GENERATION_INSTANCE_SCHEMA_URI = (
    "gs://google-cloud-aiplatform/schema/predict/instance/text_generation_1.0.0.yaml"
)
_LLM_CHAT_GENERATION_INSTANCE_SCHEMA_URI = (
    "gs://google-cloud-aiplatform/schema/predict/instance/chat_generation_1.0.0.yaml"
)
_LLM_TEXT_EMBEDDING_INSTANCE_SCHEMA_URI = (
    "gs://google-cloud-aiplatform/schema/predict/instance/text_embedding_1.0.0.yaml"
)


@dataclasses.dataclass
class _ModelInfo:
    endpoint_name: str
    interface_class: Type["_LanguageModel"]
    tuning_pipeline_uri: Optional[str] = None
    tuning_model_id: Optional[str] = None


def _get_model_info(model_id: str) -> _ModelInfo:
    """Gets the model information by model ID."""

    # The default publisher is Google
    if "/" not in model_id:
        model_id = "publishers/google/models/" + model_id

    publisher_model_res = (
        _publisher_model._PublisherModel(  # pylint: disable=protected-access
            resource_name=model_id
        )._gca_resource
    )

    if not publisher_model_res.name.startswith("publishers/google/models/"):
        raise ValueError(
            f"Only Google models are currently supported. {publisher_model_res.name}"
        )
    short_model_id = publisher_model_res.name.rsplit("/", 1)[-1]

    # == "projects/{project}/locations/{location}/publishers/google/models/text-bison@001"
    publisher_model_template = publisher_model_res.publisher_model_template.replace(
        "{user-project}", "{project}"
    )
    if not publisher_model_template:
        raise RuntimeError(
            f"The model does not have an associated Publisher Model. {publisher_model_res.name}"
        )

    endpoint_name = publisher_model_template.format(
        project=aiplatform_initializer.global_config.project,
        location=aiplatform_initializer.global_config.location,
    )
    if short_model_id == "text-bison":
        tuning_pipeline_uri = _TEXT_GENERATION_TUNING_PIPELINE_URI
        tuning_model_id = short_model_id + "-" + publisher_model_res.version_id
    else:
        tuning_pipeline_uri = None
        tuning_model_id = None

    interface_class_map = {
        _LLM_TEXT_GENERATION_INSTANCE_SCHEMA_URI: TextGenerationModel,
        _LLM_CHAT_GENERATION_INSTANCE_SCHEMA_URI: ChatModel,
        _LLM_TEXT_EMBEDDING_INSTANCE_SCHEMA_URI: TextEmbeddingModel,
    }

    interface_class = interface_class_map.get(
        publisher_model_res.predict_schemata.instance_schema_uri
    )

    if not interface_class:
        raise ValueError(f"Unknown model {publisher_model_res.name}")

    return _ModelInfo(
        endpoint_name=endpoint_name,
        interface_class=interface_class,
        tuning_pipeline_uri=tuning_pipeline_uri,
        tuning_model_id=tuning_model_id,
    )


def _get_model_id_from_tuning_model_id(tuning_model_id: str) -> str:
    """Gets the base model ID for the model ID labels used the tuned models.

    Args:
        tuning_model_id: The model ID used in tuning

    Returns:
        The publisher model ID

    Raises:
        ValueError: If tuning model ID is unsupported
    """
    if tuning_model_id.startswith("text-bison-"):
        return tuning_model_id.replace(
            "text-bison-", "publishers/google/models/text-bison@"
        )
    raise ValueError(f"Unsupported tuning model ID {tuning_model_id}")


class _LanguageModel:
    """_LanguageModel is a base class for all language models."""

    def __init__(self, model_id: str, endpoint_name: Optional[str] = None):
        """Creates a LanguageModel.

        This constructor should not be called directly.
        Use `LanguageModel.from_pretrained(model_name=...)` instead.

        Args:
            model_id: Identifier of a Vertex LLM. Example: "text-bison@001"
            endpoint_name: Vertex Endpoint resource name for the model
        """
        self._model_id = model_id
        self._endpoint_name = endpoint_name
        # TODO(b/280879204)
        # A workaround for not being able to directly instantiate the
        # high-level Endpoint with the PublisherModel resource name.
        self._endpoint = aiplatform.Endpoint._construct_sdk_resource_from_gapic(
            aiplatform_models.gca_endpoint_compat.Endpoint(name=endpoint_name)
        )

    @classmethod
    def from_pretrained(cls, model_name: str) -> "_LanguageModel":
        """Loads a LanguageModel.

        Args:
            model_name: Name of the model.

        Returns:
            An instance of a class derieved from `_LanguageModel`.

        Raises:
            ValueError: If model_name is unknown.
            ValueError: If model does not support this class.
        """
        model_info = _get_model_info(model_id=model_name)

        if not issubclass(model_info.interface_class, cls):
            raise ValueError(
                f"{model_name} is of type {model_info.interface_class.__name__} not of type {cls.__name__}"
            )

        return model_info.interface_class(
            model_id=model_name,
            endpoint_name=model_info.endpoint_name,
        )

    def list_tuned_model_names(self) -> Sequence[str]:
        """Lists the names of tuned models.

        Returns:
            A list of tuned models that can be used with the `get_tuned_model` method.
        """
        model_info = _get_model_info(model_id=self._model_id)
        return _list_tuned_model_names(model_id=model_info.tuning_model_id)

    @staticmethod
    def get_tuned_model(tuned_model_name: str) -> "_LanguageModel":
        """Loads the specified tuned language model."""

        tuned_vertex_model = aiplatform.Model(tuned_model_name)
        tuned_model_deployments = tuned_vertex_model.gca_resource.deployed_models
        if len(tuned_model_deployments) == 0:
            # Deploying the model
            endpoint_name = tuned_vertex_model.deploy().resource_name
        else:
            endpoint_name = tuned_model_deployments[0].endpoint

        tuning_model_id = tuned_vertex_model.labels[_TUNING_BASE_MODEL_ID_LABEL_KEY]
        base_model_id = _get_model_id_from_tuning_model_id(tuning_model_id)
        model_info = _get_model_info(model_id=base_model_id)
        model = model_info.interface_class(
            model_id=base_model_id,
            endpoint_name=endpoint_name,
        )
        return model

    def tune_model(
        self,
        training_data: Union[str, "pandas.core.frame.DataFrame"],
        *,
        train_steps: int = 1000,
        tuning_job_location: Optional[str] = None,
        tuned_model_location: Optional[str] = None,
        model_display_name: Optional[str] = None,
    ):
        """Tunes a model based on training data.

        This method launches a model tuning job that can take some time.

        Args:
            training_data: A Pandas DataFrame of a URI pointing to data in JSON lines format.
                The dataset must have the "input_text" and "output_text" columns.
            train_steps: Number of training steps to perform.
            tuning_job_location: GCP location where the tuning job should be run. Only "europe-west4" is supported for now.
            tuned_model_location: GCP location where the tuned model should be deployed. Only "us-central1" is supported for now.
            model_display_name: Custom display name for the tuned model.

        Returns:
            A `LanguageModelTuningJob` object that represents the tuning job.
            Calling `job.result()` blocks until the tuning is complete and returns a `LanguageModel` object.

        Raises:
            ValueError: If the "tuning_job_location" value is not supported
            ValueError: If the "tuned_model_location" value is not supported
            RuntimeError: If the model does not support tuning
        """
        if tuning_job_location != _TUNING_LOCATION:
            raise ValueError(
                f'Tuning is only supported in the following locations: tuning_job_location="{_TUNING_LOCATION}"'
            )
        if tuned_model_location != _TUNED_MODEL_LOCATION:
            raise ValueError(
                f'Model deployment is only supported in the following locations: tuned_model_location="{_TUNED_MODEL_LOCATION}"'
            )
        model_info = _get_model_info(model_id=self._model_id)
        if not model_info.tuning_pipeline_uri:
            raise RuntimeError(f"The {self._model_id} model does not support tuning")
        pipeline_job = _launch_tuning_job(
            training_data=training_data,
            train_steps=train_steps,
            model_id=model_info.tuning_model_id,
            tuning_pipeline_uri=model_info.tuning_pipeline_uri,
            model_display_name=model_display_name,
        )

        job = _LanguageModelTuningJob(
            base_model=self,
            job=pipeline_job,
        )
        self._job = job
        tuned_model = job.result()
        # The UXR study attendees preferred to tune model in place
        self._endpoint = tuned_model._endpoint


@dataclasses.dataclass
class TextGenerationResponse:
    """TextGenerationResponse represents a response of a language model."""

    text: str
    _prediction_response: Any

    def __repr__(self):
        return self.text


class TextGenerationModel(_LanguageModel):
    """TextGenerationModel represents a general language model.

    Examples:

        # Getting answers:
        model = TextGenerationModel.from_pretrained("text-bison@001")
        model.predict("What is life?")
    """

    _DEFAULT_TEMPERATURE = 0.0
    _DEFAULT_MAX_OUTPUT_TOKENS = 128
    _DEFAULT_TOP_P = 0.95
    _DEFAULT_TOP_K = 40

    def predict(
        self,
        prompt: str,
        *,
        max_output_tokens: int = _DEFAULT_MAX_OUTPUT_TOKENS,
        temperature: float = _DEFAULT_TEMPERATURE,
        top_k: int = _DEFAULT_TOP_K,
        top_p: float = _DEFAULT_TOP_P,
    ) -> "TextGenerationResponse":
        """Gets model response for a single prompt.

        Args:
            prompt: Question to ask the model.
            max_output_tokens: Max length of the output text in tokens.
            temperature: Controls the randomness of predictions. Range: [0, 1].
            top_k: The number of highest probability vocabulary tokens to keep for top-k-filtering.
            top_p: The cumulative probability of parameter highest probability vocabulary tokens to keep for nucleus sampling. Range: [0, 1].

        Returns:
            A `TextGenerationResponse` object that contains the text produced by the model.
        """

        return self._batch_predict(
            prompts=[prompt],
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
        )[0]

    def _batch_predict(
        self,
        prompts: List[str],
        max_output_tokens: int = _DEFAULT_MAX_OUTPUT_TOKENS,
        temperature: float = _DEFAULT_TEMPERATURE,
        top_k: int = _DEFAULT_TOP_K,
        top_p: float = _DEFAULT_TOP_P,
    ) -> List["TextGenerationResponse"]:
        """Gets model response for a single prompt.

        Args:
            prompts: Questions to ask the model.
            max_output_tokens: Max length of the output text in tokens.
            temperature: Controls the randomness of predictions. Range: [0, 1].
            top_k: The number of highest probability vocabulary tokens to keep for top-k-filtering.
            top_p: The cumulative probability of parameter highest probability vocabulary tokens to keep for nucleus sampling. Range: [0, 1].

        Returns:
            A list of `TextGenerationResponse` objects that contain the texts produced by the model.
        """
        instances = [{"content": str(prompt)} for prompt in prompts]
        prediction_parameters = {
            "temperature": temperature,
            "maxDecodeSteps": max_output_tokens,
            "topP": top_p,
            "topK": top_k,
        }

        prediction_response = self._endpoint.predict(
            instances=instances,
            parameters=prediction_parameters,
        )

        return [
            TextGenerationResponse(
                text=prediction["content"],
                _prediction_response=prediction_response,
            )
            for prediction in prediction_response.predictions
        ]


class _ChatModel(TextGenerationModel):
    """ChatModel represents a language model that is capable of chat.

    Examples:

        # Getting answers:
        model = ChatModel.from_pretrained("chat-bison@001")
        model.predict("What is life?")

        # Chat:
        chat = model.start_chat()

        chat.send_message("Do you know any cool events this weekend?")
    """

    def start_chat(
        self,
        max_output_tokens: int = TextGenerationModel._DEFAULT_MAX_OUTPUT_TOKENS,
        temperature: float = TextGenerationModel._DEFAULT_TEMPERATURE,
        top_k: int = TextGenerationModel._DEFAULT_TOP_K,
        top_p: float = TextGenerationModel._DEFAULT_TOP_P,
    ) -> "_ChatSession":
        """Starts a chat session with the model.

        Args:
            max_output_tokens: Max length of the output text in tokens.
            temperature: Controls the randomness of predictions. Range: [0, 1].
            top_k: The number of highest probability vocabulary tokens to keep for top-k-filtering.
            top_p: The cumulative probability of parameter highest probability vocabulary tokens to keep for nucleus sampling. Range: [0, 1].

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
        max_output_tokens: int = TextGenerationModel._DEFAULT_MAX_OUTPUT_TOKENS,
        temperature: float = TextGenerationModel._DEFAULT_TEMPERATURE,
        top_k: int = TextGenerationModel._DEFAULT_TOP_K,
        top_p: float = TextGenerationModel._DEFAULT_TOP_P,
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
        max_output_tokens: int = TextGenerationModel._DEFAULT_MAX_OUTPUT_TOKENS,
        temperature: float = TextGenerationModel._DEFAULT_TEMPERATURE,
        top_k: int = TextGenerationModel._DEFAULT_TOP_K,
        top_p: float = TextGenerationModel._DEFAULT_TOP_P,
    ) -> "TextGenerationResponse":
        """Sends message to the language model and gets a response.

        Args:
            message: Message to send to the model
            max_output_tokens: Max length of the output text in tokens.
            temperature: Controls the randomness of predictions. Range: [0, 1].
            top_k: The number of highest probability vocabulary tokens to keep for top-k-filtering.
            top_p: The cumulative probability of parameter highest probability vocabulary tokens to keep for nucleus sampling. Range: [0, 1].

        Returns:
            A `TextGenerationResponse` object that contains the text produced by the model.
        """
        new_history_text = ""
        if self._history_text:
            new_history_text = self._history_text.rstrip("\n") + "\n\n"
        new_history_text += message.rstrip("\n") + "\n"

        response_obj = self._model.predict(
            prompt=new_history_text,
            max_output_tokens=max_output_tokens or self._max_output_tokens,
            temperature=temperature or self._temperature,
            top_k=top_k or self._top_k,
            top_p=top_p or self._top_p,
        )
        response_text = response_obj.text

        self._history.append((message, response_text))
        new_history_text += response_text.rstrip("\n") + "\n"
        self._history_text = new_history_text
        return response_obj


class TextEmbeddingModel(_LanguageModel):
    """TextEmbeddingModel converts text into a vector of floating-point numbers.

    Examples:

        # Getting embedding:
        model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
        embeddings = model.get_embeddings(["What is life?"])
        for embedding in embeddings:
            vector = embedding.values
            print(len(vector))
    """

    def get_embeddings(self, texts: List[str]) -> List["TextEmbedding"]:
        instances = [{"content": str(text)} for text in texts]

        prediction_response = self._endpoint.predict(
            instances=instances,
        )

        return [
            TextEmbedding(
                values=prediction["embeddings"]["values"],
                _prediction_response=prediction_response,
            )
            for prediction in prediction_response.predictions
        ]


class TextEmbedding:
    """Contains text embedding vector."""

    def __init__(
        self,
        values: List[float],
        _prediction_response: Any = None,
    ):
        self.values = values
        self._prediction_response = _prediction_response


@dataclasses.dataclass
class InputOutputTextPair:
    """InputOutputTextPair represents a pair of input and output texts."""

    input_text: str
    output_text: str


class ChatModel(_LanguageModel):
    """ChatModel represents a language model that is capable of chat.

    Examples:

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

    def start_chat(
        self,
        *,
        context: Optional[str] = None,
        examples: Optional[List[InputOutputTextPair]] = None,
        max_output_tokens: int = TextGenerationModel._DEFAULT_MAX_OUTPUT_TOKENS,
        temperature: float = TextGenerationModel._DEFAULT_TEMPERATURE,
        top_k: int = TextGenerationModel._DEFAULT_TOP_K,
        top_p: float = TextGenerationModel._DEFAULT_TOP_P,
    ) -> "ChatSession":
        """Starts a chat session with the model.

        Args:
            context: Context shapes how the model responds throughout the conversation.
                For example, you can use context to specify words the model can or cannot use, topics to focus on or avoid, or the response format or style
            examples: List of structured messages to the model to learn how to respond to the conversation.
                A list of `InputOutputTextPair` objects.
            max_output_tokens: Max length of the output text in tokens.
            temperature: Controls the randomness of predictions. Range: [0, 1].
            top_k: The number of highest probability vocabulary tokens to keep for top-k-filtering. Range: [1, 40]
            top_p: The cumulative probability of parameter highest probability vocabulary tokens to keep for nucleus sampling. Range: [0, 1].

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
        )


class ChatSession:
    """ChatSession represents a chat session with a language model.

    Within a chat session, the model keeps context and remembers the previous conversation.
    """

    def __init__(
        self,
        model: ChatModel,
        context: Optional[str] = None,
        examples: Optional[List[InputOutputTextPair]] = None,
        max_output_tokens: int = TextGenerationModel._DEFAULT_MAX_OUTPUT_TOKENS,
        temperature: float = TextGenerationModel._DEFAULT_TEMPERATURE,
        top_k: int = TextGenerationModel._DEFAULT_TOP_K,
        top_p: float = TextGenerationModel._DEFAULT_TOP_P,
    ):
        self._model = model
        self._context = context
        self._examples = examples
        self._history = []
        self._max_output_tokens = max_output_tokens
        self._temperature = temperature
        self._top_k = top_k
        self._top_p = top_p

    def send_message(
        self,
        message: str,
        *,
        max_output_tokens: int = TextGenerationModel._DEFAULT_MAX_OUTPUT_TOKENS,
        temperature: float = TextGenerationModel._DEFAULT_TEMPERATURE,
        top_k: int = TextGenerationModel._DEFAULT_TOP_K,
        top_p: float = TextGenerationModel._DEFAULT_TOP_P,
    ) -> "TextGenerationResponse":
        """Sends message to the language model and gets a response.

        Args:
            message: Message to send to the model
            max_output_tokens: Max length of the output text in tokens.
            temperature: Controls the randomness of predictions. Range: [0, 1].
            top_k: The number of highest probability vocabulary tokens to keep for top-k-filtering.
            top_p: The cumulative probability of parameter highest probability vocabulary tokens to keep for nucleus sampling. Range: [0, 1].

        Returns:
            A `TextGenerationResponse` object that contains the text produced by the model.
        """
        prediction_parameters = {
            "temperature": temperature,
            "maxDecodeSteps": max_output_tokens,
            "topP": top_p,
            "topK": top_k,
        }
        messages = []
        for input_text, output_text in self._history:
            messages.append(
                {
                    "author": "user",
                    "content": input_text,
                }
            )
            messages.append(
                {
                    "author": "bot",
                    "content": output_text,
                }
            )

        messages.append(
            {
                "author": "user",
                "content": message,
            }
        )

        prediction_instance = {"messages": messages}
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

        prediction_response = self._model._endpoint.predict(
            instances=[prediction_instance],
            parameters=prediction_parameters,
        )

        response_obj = TextGenerationResponse(
            text=prediction_response.predictions[0]["candidates"][0]["content"],
            _prediction_response=prediction_response,
        )
        response_text = response_obj.text

        self._history.append((message, response_text))
        return response_obj


###### Model tuning
# Currently, tuning can only work in this location
_TUNING_LOCATION = "europe-west4"
# Currently, deployment can only work in this location
_TUNED_MODEL_LOCATION = "us-central1"


class _LanguageModelTuningJob:
    """LanguageModelTuningJob represents a fine-tuning job."""

    def __init__(
        self,
        base_model: _LanguageModel,
        job: aiplatform.PipelineJob,
    ):
        self._base_model = base_model
        self._job = job
        self._model: Optional[_LanguageModel] = None

    def result(self) -> "_LanguageModel":
        """Blocks until the tuning is complete and returns a `LanguageModel` object."""
        if self._model:
            return self._model
        self._job.wait()
        upload_model_tasks = [
            task_info
            for task_info in self._job.gca_resource.job_detail.task_details
            if task_info.task_name == "upload-llm-model"
        ]
        if len(upload_model_tasks) != 1:
            raise RuntimeError(
                f"Failed to get the model name from the tuning pipeline: {self._job.name}"
            )
        upload_model_task = upload_model_tasks[0]

        # Trying to get model name from output parameter
        vertex_model_name = upload_model_task.execution.metadata[
            "output:model_resource_name"
        ].strip()
        _LOGGER.info(f"Tuning has completed. Created Vertex Model: {vertex_model_name}")
        self._model = type(self._base_model).get_tuned_model(
            tuned_model_name=vertex_model_name
        )
        return self._model

    @property
    def status(self):
        """Job status"""
        return self._job.state

    def cancel(self):
        self._job.cancel()


def _get_tuned_models_dir_uri(model_id: str) -> str:
    staging_gcs_bucket = (
        gcs_utils.create_gcs_bucket_for_pipeline_artifacts_if_it_does_not_exist()
    )
    return (
        staging_gcs_bucket.replace("/output_artifacts/", "/tuned_language_models/")
        + model_id
    )


def _list_tuned_model_names(model_id: str) -> List[str]:
    tuned_models = aiplatform.Model.list(
        filter=f'labels.{_TUNING_BASE_MODEL_ID_LABEL_KEY}="{model_id}"',
        # TODO(b/275444096): Remove the explicit location once models are deployed to the user's selected location
        location=_TUNED_MODEL_LOCATION,
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
    train_steps: Optional[int] = None,
    model_display_name: Optional[str] = None,
) -> aiplatform.PipelineJob:
    output_dir_uri = _generate_tuned_model_dir_uri(model_id=model_id)
    if isinstance(training_data, str):
        dataset_uri = training_data
    elif pandas and isinstance(training_data, pandas.DataFrame):
        dataset_uri = _uri_join(output_dir_uri, "training_data.jsonl")

        with tempfile.NamedTemporaryFile() as temp_file:
            dataset_path = temp_file.name
            df = training_data
            df = df[["input_text", "output_text"]]
            df.to_json(path_or_buf=dataset_path, orient="records", lines=True)
            storage_client = storage.Client(
                credentials=aiplatform_initializer.global_config.credentials
            )
            storage.Blob.from_string(
                uri=dataset_uri, client=storage_client
            ).upload_from_filename(filename=dataset_path)
    else:
        raise TypeError(f"Unsupported training_data type: {type(training_data)}")

    job = _launch_tuning_job_on_jsonl_data(
        model_id=model_id,
        dataset_name_or_uri=dataset_uri,
        train_steps=train_steps,
        tuning_pipeline_uri=tuning_pipeline_uri,
        model_display_name=model_display_name,
    )
    return job


def _launch_tuning_job_on_jsonl_data(
    model_id: str,
    dataset_name_or_uri: str,
    tuning_pipeline_uri: str,
    train_steps: Optional[int] = None,
    model_display_name: Optional[str] = None,
) -> aiplatform.PipelineJob:
    if not model_display_name:
        # Creating a human-readable model display name
        name = f"{model_id} tuned for {train_steps} steps on "
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
        "train_steps": train_steps,
        "project": aiplatform_initializer.global_config.project,
        # TODO(b/275444096): Remove the explicit location once tuning can happen in all regions
        # "location": aiplatform_initializer.global_config.location,
        "location": _TUNED_MODEL_LOCATION,
        "large_model_reference": model_id,
        "model_display_name": model_display_name,
    }

    if dataset_name_or_uri.startswith("projects/"):
        pipeline_arguments["dataset_name"] = dataset_name_or_uri
    if dataset_name_or_uri.startswith("gs://"):
        pipeline_arguments["dataset_uri"] = dataset_name_or_uri
    job = aiplatform.PipelineJob(
        template_path=tuning_pipeline_uri,
        display_name=None,
        parameter_values=pipeline_arguments,
        # TODO(b/275444101): Remove the explicit location once model can be deployed in all regions
        location=_TUNING_LOCATION,
    )
    job.submit()
    return job


def _uri_join(uri: str, path_fragment: str) -> str:
    """Appends path fragment to URI.

    urllib.parse.urljoin only works on URLs, not URIs
    """

    return uri.rstrip("/") + "/" + path_fragment.lstrip("/")
