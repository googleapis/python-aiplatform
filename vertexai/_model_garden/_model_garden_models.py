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

import dataclasses
from typing import Dict, Optional, Type, TypeVar

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer as aiplatform_initializer
from google.cloud.aiplatform import models as aiplatform_models
from google.cloud.aiplatform import _publisher_models

from google.cloud.aiplatform.compat.types import (
    publisher_model as gca_publisher_model,
)

_SUPPORTED_PUBLISHERS = ["google"]

_SHORT_MODEL_ID_TO_TUNING_PIPELINE_MAP = {
    "text-bison": "https://us-kfp.pkg.dev/ml-pipeline/large-language-model-pipelines/tune-large-model/v2.0.0",
    "code-bison": "https://us-kfp.pkg.dev/ml-pipeline/large-language-model-pipelines/tune-large-model/v3.0.0",
    "chat-bison": "https://us-kfp.pkg.dev/ml-pipeline/large-language-model-pipelines/tune-large-chat-model/v3.0.0",
    "codechat-bison": "https://us-kfp.pkg.dev/ml-pipeline/large-language-model-pipelines/tune-large-chat-model/v3.0.0",
}

_SDK_PRIVATE_PREVIEW_LAUNCH_STAGE = frozenset(
    [
        gca_publisher_model.PublisherModel.LaunchStage.PRIVATE_PREVIEW,
        gca_publisher_model.PublisherModel.LaunchStage.PUBLIC_PREVIEW,
        gca_publisher_model.PublisherModel.LaunchStage.GA,
    ]
)
_SDK_PUBLIC_PREVIEW_LAUNCH_STAGE = frozenset(
    [
        gca_publisher_model.PublisherModel.LaunchStage.PUBLIC_PREVIEW,
        gca_publisher_model.PublisherModel.LaunchStage.GA,
    ]
)
_SDK_GA_LAUNCH_STAGE = frozenset([gca_publisher_model.PublisherModel.LaunchStage.GA])

_LOGGER = base.Logger(__name__)

T = TypeVar("T", bound="_ModelGardenModel")


@dataclasses.dataclass
class _ModelInfo:
    endpoint_name: str
    interface_class: Type["_ModelGardenModel"]
    publisher_model_resource: _publisher_models._PublisherModel
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
        tuning_model_id = publisher_model_template.rsplit("/", 1)[-1]
    else:
        tuning_pipeline_uri = None
        tuning_model_id = None

    interface_class = schema_to_class_map.get(
        publisher_model_res.predict_schemata.instance_schema_uri
    )

    if not interface_class:
        raise ValueError(
            f"Unknown model {publisher_model_res.name}; {schema_to_class_map}"
        )

    return _ModelInfo(
        endpoint_name=endpoint_name,
        interface_class=interface_class,
        publisher_model_resource=publisher_model_res,
        tuning_pipeline_uri=tuning_pipeline_uri,
        tuning_model_id=tuning_model_id,
    )


class _ModelGardenModel:
    """Base class for shared methods and properties across Model Garden models."""

    _LAUNCH_STAGE: gca_publisher_model.PublisherModel.LaunchStage = (
        _SDK_PUBLIC_PREVIEW_LAUNCH_STAGE
    )

    def _validate_launch_stage(
        self,
        publisher_model_resource: gca_publisher_model.PublisherModel,
    ) -> None:
        """Validates the model class _LAUNCH_STAGE matches the PublisherModel resource's launch stage.

        Args:
            publisher_model_resource (gca_publisher_model.PublisherModel
                The GAPIC PublisherModel resource for this model.
        """

        publisher_launch_stage = publisher_model_resource.launch_stage

        if publisher_launch_stage not in self._LAUNCH_STAGE:
            raise ValueError(
                f"The model you are trying to instantiate does not support the launch stage: {publisher_launch_stage.name}"
            )

    # Subclasses override this attribute to specify their instance schema
    _INSTANCE_SCHEMA_URI: Optional[str] = None

    def __init__(self, model_id: str, endpoint_name: Optional[str] = None):
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
    def from_pretrained(cls: Type[T], model_name: str) -> T:
        """Loads a _ModelGardenModel.

        Args:
            model_name: Name of the model.

        Returns:
            An instance of a class derieved from `_ModelGardenModel`.

        Raises:
            ValueError: If model_name is unknown.
            ValueError: If model does not support this class.
        """

        if not cls._INSTANCE_SCHEMA_URI:
            raise ValueError(
                f"Class {cls} is not a correct model interface class since it does not have an instance schema URI."
            )

        model_info = _get_model_info(
            model_id=model_name, schema_to_class_map={cls._INSTANCE_SCHEMA_URI: cls}
        )

        if not issubclass(model_info.interface_class, cls):
            raise ValueError(
                f"{model_name} is of type {model_info.interface_class.__name__} not of type {cls.__name__}"
            )

        cls._validate_launch_stage(cls, model_info.publisher_model_resource)

        return model_info.interface_class(
            model_id=model_name,
            endpoint_name=model_info.endpoint_name,
        )
