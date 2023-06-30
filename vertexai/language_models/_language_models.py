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
from typing import Any, Dict, List, Optional, Sequence, Union

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer as aiplatform_initializer
from google.cloud.aiplatform import utils as aiplatform_utils
from google.cloud.aiplatform.utils import gcs_utils
from vertexai._model_garden import _model_garden_models

try:
    import pandas
except ImportError:
    pandas = None


_LOGGER = base.Logger(__name__)


# Endpoint label/metadata key to preserve the base model ID information
_TUNING_BASE_MODEL_ID_LABEL_KEY = "google-vertex-llm-tuning-base-model-id"


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
        train_steps: int = 1000,
        learning_rate: Optional[float] = None,
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
            learning_rate: Learning rate for the tuning
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
        model_info = _model_garden_models._get_model_info(
            model_id=self._model_id,
            schema_to_class_map={self._INSTANCE_SCHEMA_URI: type(self)},
        )
        if not model_info.tuning_pipeline_uri:
            raise RuntimeError(f"The {self._model_id} model does not support tuning")
        pipeline_job = _launch_tuning_job(
            training_data=training_data,
            train_steps=train_steps,
            model_id=model_info.tuning_model_id,
            tuning_pipeline_uri=model_info.tuning_pipeline_uri,
            model_display_name=model_display_name,
            learning_rate=learning_rate,
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
    """TextGenerationResponse represents a response of a language model.
    Attributes:
        text: The generated text
        is_blocked: Whether the the request was blocked.
        safety_attributes: Scores for safety attributes.
            Learn more about the safety attributes here:
            https://cloud.google.com/vertex-ai/docs/generative-ai/learn/responsible-ai#safety_attribute_descriptions
    """

    text: str
    _prediction_response: Any
    is_blocked: bool = False
    safety_attributes: Dict[str, float] = dataclasses.field(default_factory=dict)

    def __repr__(self):
        return self.text


class TextGenerationModel(_LanguageModel):
    """TextGenerationModel represents a general language model.

    Examples::

        # Getting answers:
        model = TextGenerationModel.from_pretrained("text-bison@001")
        model.predict("What is life?")
    """

    _LAUNCH_STAGE = _model_garden_models._SDK_GA_LAUNCH_STAGE

    _INSTANCE_SCHEMA_URI = "gs://google-cloud-aiplatform/schema/predict/instance/text_generation_1.0.0.yaml"

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

        results = []
        for prediction in prediction_response.predictions:
            safety_attributes_dict = prediction.get("safetyAttributes", {})
            results.append(
                TextGenerationResponse(
                    text=prediction["content"],
                    _prediction_response=prediction_response,
                    is_blocked=safety_attributes_dict.get("blocked", False),
                    safety_attributes=dict(
                        zip(
                            safety_attributes_dict.get("categories", []),
                            safety_attributes_dict.get("scores", []),
                        )
                    ),
                )
            )
        return results


_TextGenerationModel = TextGenerationModel


class _ModelWithBatchPredict(_LanguageModel):
    """Model that supports batch prediction."""

    def batch_predict(
        self,
        *,
        source_uri: Union[str, List[str]],
        destination_uri_prefix: str,
        model_parameters: Optional[Dict] = None,
    ) -> aiplatform.BatchPredictionJob:
        """Starts a batch prediction job with the model.

        Args:
            source_uri: The location of the dataset.
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
        first_source_uri = source_uri if isinstance(source_uri, str) else source_uri[0]
        if first_source_uri.startswith("gs://"):
            if not isinstance(source_uri, str):
                if not all(uri.startswith("gs://") for uri in source_uri):
                    raise ValueError(
                        f"All URIs in the list must start with 'gs://': {source_uri}"
                    )
            arguments["gcs_source"] = source_uri
        elif first_source_uri.startswith("bq://"):
            if not isinstance(source_uri, str):
                raise ValueError(
                    f"Only single BigQuery source can be specified: {source_uri}"
                )
            arguments["bigquery_source"] = source_uri
        else:
            raise ValueError(f"Unsupported source_uri: {source_uri}")

        if destination_uri_prefix.startswith("gs://"):
            arguments["gcs_destination_prefix"] = destination_uri_prefix
        elif destination_uri_prefix.startswith("bq://"):
            arguments["bigquery_destination_prefix"] = destination_uri_prefix
        else:
            raise ValueError(f"Unsupported destination_uri: {destination_uri_prefix}")

        model_name = self._model_resource_name
        # TODO(b/284512065): Batch prediction service does not support
        # fully qualified publisher model names yet
        publishers_index = model_name.index("/publishers/")
        if publishers_index > 0:
            model_name = model_name[publishers_index + 1 :]

        job = aiplatform.BatchPredictionJob.create(
            model_name=model_name,
            job_display_name=None,
            **arguments,
            model_parameters=model_parameters,
        )
        return job


class _PreviewTextGenerationModel(
    TextGenerationModel, _TunableModelMixin, _ModelWithBatchPredict
):
    """Preview text generation model."""

    _LAUNCH_STAGE = _model_garden_models._SDK_PUBLIC_PREVIEW_LAUNCH_STAGE


class _ChatModel(TextGenerationModel):
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
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
    ) -> "TextGenerationResponse":
        """Sends message to the language model and gets a response.

        Args:
            message: Message to send to the model
            max_output_tokens: Max length of the output text in tokens.
                Uses the value specified when calling `ChatModel.start_chat` by default.
            temperature: Controls the randomness of predictions. Range: [0, 1].
                Uses the value specified when calling `ChatModel.start_chat` by default.
            top_k: The number of highest probability vocabulary tokens to keep for top-k-filtering.
                Uses the value specified when calling `ChatModel.start_chat` by default.
            top_p: The cumulative probability of parameter highest probability vocabulary tokens to keep for nucleus sampling. Range: [0, 1].
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


class TextEmbeddingModel(_LanguageModel):
    """TextEmbeddingModel converts text into a vector of floating-point numbers.

    Examples::

        # Getting embedding:
        model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
        embeddings = model.get_embeddings(["What is life?"])
        for embedding in embeddings:
            vector = embedding.values
            print(len(vector))
    """

    _LAUNCH_STAGE = _model_garden_models._SDK_GA_LAUNCH_STAGE

    _INSTANCE_SCHEMA_URI = (
        "gs://google-cloud-aiplatform/schema/predict/instance/text_embedding_1.0.0.yaml"
    )

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


class _PreviewTextEmbeddingModel(TextEmbeddingModel):
    """Preview text embedding model."""

    _LAUNCH_STAGE = _model_garden_models._SDK_PUBLIC_PREVIEW_LAUNCH_STAGE


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


@dataclasses.dataclass
class ChatMessage:
    """A chat message.

    Attributes:
        content: Content of the message.
        author: Author of the message.
    """

    content: str
    author: str


class _ChatModelBase(_LanguageModel):
    """_ChatModelBase is a base class for chat models."""

    _LAUNCH_STAGE = _model_garden_models._SDK_PUBLIC_PREVIEW_LAUNCH_STAGE

    def start_chat(
        self,
        *,
        context: Optional[str] = None,
        examples: Optional[List[InputOutputTextPair]] = None,
        max_output_tokens: int = TextGenerationModel._DEFAULT_MAX_OUTPUT_TOKENS,
        temperature: float = TextGenerationModel._DEFAULT_TEMPERATURE,
        top_k: int = TextGenerationModel._DEFAULT_TOP_K,
        top_p: float = TextGenerationModel._DEFAULT_TOP_P,
        message_history: Optional[List[ChatMessage]] = None,
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
            message_history: A list of previously sent and received messages.

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
        )


class ChatModel(_ChatModelBase):
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

    _INSTANCE_SCHEMA_URI = "gs://google-cloud-aiplatform/schema/predict/instance/chat_generation_1.0.0.yaml"


class CodeChatModel(_ChatModelBase):
    """CodeChatModel represents a model that is capable of completing code.

    Examples:
        code_chat_model = CodeChatModel.from_pretrained("codechat-bison@001")

        code_chat = code_chat_model.start_chat(
            max_output_tokens=128,
            temperature=0.2,
        )

        code_chat.send_message("Please help write a function to calculate the min of two numbers")
    """

    _INSTANCE_SCHEMA_URI = "gs://google-cloud-aiplatform/schema/predict/instance/codechat_generation_1.0.0.yaml"
    _LAUNCH_STAGE = _model_garden_models._SDK_GA_LAUNCH_STAGE

    _DEFAULT_MAX_OUTPUT_TOKENS = 128
    _DEFAULT_TEMPERATURE = 0.5

    def start_chat(
        self,
        *,
        max_output_tokens: int = _DEFAULT_MAX_OUTPUT_TOKENS,
        temperature: float = _DEFAULT_TEMPERATURE,
    ) -> "CodeChatSession":
        """Starts a chat session with the code chat model.

        Args:
            max_output_tokens: Max length of the output text in tokens.
            temperature: Controls the randomness of predictions. Range: [0, 1].

        Returns:
            A `ChatSession` object.
        """
        return CodeChatSession(
            model=self,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
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
        max_output_tokens: int = TextGenerationModel._DEFAULT_MAX_OUTPUT_TOKENS,
        temperature: float = TextGenerationModel._DEFAULT_TEMPERATURE,
        top_k: int = TextGenerationModel._DEFAULT_TOP_K,
        top_p: float = TextGenerationModel._DEFAULT_TOP_P,
        is_code_chat_session: bool = False,
        message_history: Optional[List[ChatMessage]] = None,
    ):
        self._model = model
        self._context = context
        self._examples = examples
        self._max_output_tokens = max_output_tokens
        self._temperature = temperature
        self._top_k = top_k
        self._top_p = top_p
        self._is_code_chat_session = is_code_chat_session
        self._message_history: List[ChatMessage] = message_history or []

    @property
    def message_history(self) -> List[ChatMessage]:
        """List of previous messages."""
        return self._message_history

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
            max_output_tokens: Max length of the output text in tokens.
                Uses the value specified when calling `ChatModel.start_chat` by default.
            temperature: Controls the randomness of predictions. Range: [0, 1].
                Uses the value specified when calling `ChatModel.start_chat` by default.
            top_k: The number of highest probability vocabulary tokens to keep for top-k-filtering.
                Uses the value specified when calling `ChatModel.start_chat` by default.
            top_p: The cumulative probability of parameter highest probability vocabulary tokens to keep for nucleus sampling. Range: [0, 1].
                Uses the value specified when calling `ChatModel.start_chat` by default.

        Returns:
            A `TextGenerationResponse` object that contains the text produced by the model.
        """
        prediction_parameters = {
            "temperature": temperature
            if temperature is not None
            else self._temperature,
            "maxDecodeSteps": max_output_tokens
            if max_output_tokens is not None
            else self._max_output_tokens,
        }

        if not self._is_code_chat_session:
            prediction_parameters["topP"] = top_p if top_p is not None else self._top_p
            prediction_parameters["topK"] = top_k if top_k is not None else self._top_k

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
        if not self._is_code_chat_session and self._context:
            prediction_instance["context"] = self._context
        if not self._is_code_chat_session and self._examples:
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

        prediction = prediction_response.predictions[0]
        # ! Note: For chat models, the safetyAttributes is a list.
        safety_attributes = prediction["safetyAttributes"][0]
        response_obj = TextGenerationResponse(
            text=prediction["candidates"][0]["content"]
            if prediction.get("candidates")
            else None,
            _prediction_response=prediction_response,
            is_blocked=safety_attributes.get("blocked", False),
            safety_attributes=dict(
                zip(
                    safety_attributes.get("categories", []),
                    safety_attributes.get("scores", []),
                )
            ),
        )
        response_text = response_obj.text

        self._message_history.append(
            ChatMessage(content=message, author=self.USER_AUTHOR)
        )
        self._message_history.append(
            ChatMessage(content=response_text, author=self.MODEL_AUTHOR)
        )

        return response_obj


class ChatSession(_ChatSessionBase):
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
        message_history: Optional[List[ChatMessage]] = None,
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
        )


class CodeChatSession(_ChatSessionBase):
    """CodeChatSession represents a chat session with code chat language model.

    Within a code chat session, the model keeps context and remembers the previous converstion.
    """

    def __init__(
        self,
        model: CodeChatModel,
        max_output_tokens: int = CodeChatModel._DEFAULT_MAX_OUTPUT_TOKENS,
        temperature: float = CodeChatModel._DEFAULT_TEMPERATURE,
    ):
        super().__init__(
            model=model,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            is_code_chat_session=True,
        )

    def send_message(
        self,
        message: str,
        *,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> "TextGenerationResponse":
        """Sends message to the code chat model and gets a response.

        Args:
            message: Message to send to the model
            max_output_tokens: Max length of the output text in tokens.
                Uses the value specified when calling `CodeChatModel.start_chat` by default.
            temperature: Controls the randomness of predictions. Range: [0, 1].
                 Uses the value specified when calling `CodeChatModel.start_chat` by default.

        Returns:
            A `TextGenerationResponse` object that contains the text produced by the model.
        """
        return super().send_message(
            message=message,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
        )


class CodeGenerationModel(_LanguageModel):
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

    _INSTANCE_SCHEMA_URI = "gs://google-cloud-aiplatform/schema/predict/instance/code_generation_1.0.0.yaml"

    _LAUNCH_STAGE = _model_garden_models._SDK_GA_LAUNCH_STAGE
    _DEFAULT_TEMPERATURE = 0.0
    _DEFAULT_MAX_OUTPUT_TOKENS = 128

    def predict(
        self,
        prefix: str,
        suffix: Optional[str] = "",
        *,
        max_output_tokens: int = _DEFAULT_MAX_OUTPUT_TOKENS,
        temperature: float = _DEFAULT_TEMPERATURE,
    ) -> "TextGenerationResponse":
        """Gets model response for a single prompt.

        Args:
            prefix: Code before the current point.
            suffix: Code after the current point.
            max_output_tokens: Max length of the output text in tokens.
            temperature: Controls the randomness of predictions. Range: [0, 1].

        Returns:
            A `TextGenerationResponse` object that contains the text produced by the model.
        """
        instance = {"prefix": prefix, "suffix": suffix}
        prediction_parameters = {
            "temperature": temperature,
            "maxOutputTokens": max_output_tokens,
        }

        prediction_response = self._endpoint.predict(
            instances=[instance],
            parameters=prediction_parameters,
        )

        return TextGenerationResponse(
            text=prediction_response.predictions[0]["content"],
            _prediction_response=prediction_response,
        )


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
    learning_rate: Optional[float] = None,
) -> aiplatform.PipelineJob:
    output_dir_uri = _generate_tuned_model_dir_uri(model_id=model_id)
    if isinstance(training_data, str):
        dataset_uri = training_data
    elif pandas and isinstance(training_data, pandas.DataFrame):
        dataset_uri = _uri_join(output_dir_uri, "training_data.jsonl")
        training_data = training_data[["input_text", "output_text"]]

        gcs_utils._upload_pandas_df_to_gcs(
            df=training_data, upload_gcs_path=dataset_uri
        )

    else:
        raise TypeError(f"Unsupported training_data type: {type(training_data)}")

    job = _launch_tuning_job_on_jsonl_data(
        model_id=model_id,
        dataset_name_or_uri=dataset_uri,
        train_steps=train_steps,
        tuning_pipeline_uri=tuning_pipeline_uri,
        model_display_name=model_display_name,
        learning_rate=learning_rate,
    )
    return job


def _launch_tuning_job_on_jsonl_data(
    model_id: str,
    dataset_name_or_uri: str,
    tuning_pipeline_uri: str,
    train_steps: Optional[int] = None,
    learning_rate: Optional[float] = None,
    model_display_name: Optional[str] = None,
) -> aiplatform.PipelineJob:
    if not model_display_name:
        # Creating a human-readable model display name
        name = f"{model_id} tuned for {train_steps} steps"
        if learning_rate:
            name += f" with learning rate {learning_rate}"
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
        "train_steps": train_steps,
        "project": aiplatform_initializer.global_config.project,
        # TODO(b/275444096): Remove the explicit location once tuning can happen in all regions
        # "location": aiplatform_initializer.global_config.location,
        "location": _TUNED_MODEL_LOCATION,
        "large_model_reference": model_id,
        "model_display_name": model_display_name,
    }
    if learning_rate:
        pipeline_arguments["learning_rate"] = learning_rate

    if dataset_name_or_uri.startswith("projects/"):
        pipeline_arguments["dataset_name"] = dataset_name_or_uri
    if dataset_name_or_uri.startswith("gs://"):
        pipeline_arguments["dataset_uri"] = dataset_name_or_uri
    if aiplatform_initializer.global_config.encryption_spec_key_name:
        pipeline_arguments[
            "encryption_spec_key_name"
        ] = aiplatform_initializer.global_config.encryption_spec_key_name
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
