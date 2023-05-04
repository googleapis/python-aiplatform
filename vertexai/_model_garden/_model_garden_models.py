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

"""Base class for working with Model Garden models."""

import abc
import dataclasses
from typing import Dict, Optional, Type

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer as aiplatform_initializer
from google.cloud.aiplatform import models as aiplatform_models
from google.cloud.aiplatform import _publisher_models


_SUPPORTED_PUBLISHERS = ["google"]

_SHORT_MODEL_ID_TO_TUNING_PIPELINE_MAP = {
    "text-bison": "https://us-kfp.pkg.dev/vertex-ai/large-language-model-pipelines/tune-large-model/sdk-1-25"
}

_LOGGER = base.Logger(__name__)


@dataclasses.dataclass
class _ModelInfo:
    endpoint_name: str
    interface_class: Type["_ModelGardenModel"]
    tuning_pipeline_uri: Optional[str] = None
    tuning_model_id: Optional[str] = None


def _get_model_info(
    model_id: str, schema_to_class_map: Dict[str, "_ModelGardenModel"]
) -> _ModelInfo:
    """Gets the model information by model ID.

    Args:
        model_id (str):
            Identifier of a Model Garden Model. Example: "text-bison@001"
        schema_to_class_map (Dict[str, "_ModelGardenModel"]):
            Mapping of schema URI to model class.

    Returns:
        _ModelInfo:
            Instance of _ModelInfo with details on the provided model_id.

    Raises:
        ValueError:
            If a publisher other than Google is provided in the publisher resource name
            If the provided model doesn't have an associated Publisher Model
            If the model's schema uri is not in the provided schema_to_class_map
    """

    # The default publisher is Google
    if "/" not in model_id:
        model_id = "publishers/google/models/" + model_id

    publisher_model_res = (
        _publisher_models._PublisherModel(  # pylint: disable=protected-access
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

    if short_model_id in _SHORT_MODEL_ID_TO_TUNING_PIPELINE_MAP:
        tuning_pipeline_uri = _SHORT_MODEL_ID_TO_TUNING_PIPELINE_MAP[short_model_id]
        tuning_model_id = short_model_id + "-" + publisher_model_res.version_id
    else:
        tuning_pipeline_uri = None
        tuning_model_id = None

    interface_class = schema_to_class_map.get(
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


class _ModelGardenModel:
    """Base class for shared methods and properties across Model Garden models."""

    _model_id: str
    _endpoint_name: str
    _endpoint: aiplatform.Endpoint


    @staticmethod
    @abc.abstractmethod
    def _get_public_preview_class_map() -> Dict[str, Type["_ModelGardenModel"]]:
        """Returns a Dict mapping schema URI to model class.

        Subclasses should implement this method. Example mapping:

            {
                "gs://google-cloud-aiplatform/schema/predict/instance/text_generation_1.0.0.yaml": TextGenerationModel
            }
        """
        pass

    def _construct(self, model_id: str, endpoint_name: Optional[str] = None):
        """Creates a _ModelGardenModel.

        This constructor should not be called directly.
        Use `{model_class}.from_pretrained(model_name=...)` instead.

        Args:
            model_id: Identifier of a Model Garden Model. Example: "text-bison@001"
            endpoint_name: Vertex Endpoint resource name for the model
        """

        self._model_id = model_id
        self._endpoint_name = endpoint_name
        # TODO(b/280879204)
        # A workaround for not being able to directly instantiate the
        # high-level Endpoint with the PublisherModel resource name.
        self._endpoint = aiplatform.Endpoint._construct_sdk_resource_from_gapic(
            aiplatform_models.gca_endpoint_compat.Endpoint(name=endpoint_name),
        )

    @classmethod
    def from_pretrained(cls, model_name: str) -> "_ModelGardenModel":
        """Loads a _ModelGardenModel.

        Args:
            model_name: Name of the model.

        Returns:
            An instance of a class derieved from `_ModelGardenModel`.

        Raises:
            ValueError: If model_name is unknown.
            ValueError: If model does not support this class.
        """

        model_info = _get_model_info(
            model_id=model_name, schema_to_class_map=cls._get_public_preview_class_map()
        )

        if not issubclass(model_info.interface_class, cls):
            raise ValueError(
                f"{model_name} is of type {model_info.interface_class.__name__} not of type {cls.__name__}"
            )

        return model_info.interface_class()._construct(
            model_id=model_name,
            endpoint_name=model_info.endpoint_name,
        )
