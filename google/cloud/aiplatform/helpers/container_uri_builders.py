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

import re

from google.cloud.aiplatform.constants import prediction
from google.cloud.aiplatform.initializer import global_config


def get_prediction_container_uri(
    framework: str,
    framework_version: str,
    region: str = None,
    with_accelerator: bool = False,
) -> str:
    """
    Get a Vertex AI pre-built prediction Docker container URI for
    a given framework, version, region, and accelerator use.

    Example usage:
    ```
        uri = aiplatform.helpers.get_prediction_container_uri(
                framework="tensorflow",
                framework_version="2.6",
                with_accelerator=True
        )

        model = aiplatform.Model.upload(
            display_name="boston_housing_",
            artifact_uri="gs://my-bucket/my-model/",
            serving_container_image_uri=uri
        )
    ```

    Args:
        framework (str):
            The ML framework of the pre-built container. For example,
            "tensorflow", "xgboost", or "sklearn"
        framework_version (str):
            The version of the specified ML framework as a string.
        region (str):
            A Vertex AI region or multi-region. Used to select the correct
            Artifact Registry multi-region repository and reduce latency.
            Must start with "us", "asia" or "europe". If not set, defaults
            to location set by `aiplatform.init()`.
        with_accelerator (bool):
            If set to `True`, return container URI that supports GPU usage.
            Default is `False`.

    Returns:
        uri (str):
            A Vertex AI prediction container URI

    Raises:
        ValueError: If containers for provided framework are unavailable,
        the container does not support accelerators, or is not available
        in the specified version or region.
    """

    DOCS_URI_MESSAGE = (
        f"See {prediction._SERVING_CONTAINER_DOCUMENTATION_URL} "
        "for complete list of supported containers"
    )
    alt_versions = []  # Alternative framework versions if provided does not exist

    # Validate provided framework
    try:
        framework = framework.lower()
        framework = prediction._FRAMEWORK_TO_URI_REF[framework]
    except KeyError:
        raise ValueError(
            f"No containers found for framework `{framework}`. {DOCS_URI_MESSAGE}"
        )

    version = framework_version.replace(".", "-")

    # Tensorflow 2.x is has a different framework name in URI
    if framework == prediction.TF and version.startswith("2"):
        framework = prediction.TF2

    accelerator = prediction._ACCELERATOR_TO_URI_REF[framework][
        0 if with_accelerator else 1
    ]

    if accelerator is None:
        raise ValueError(
            f"{framework} containers do not support accelerators. "
            f"Please set `with_accelerator` to False. {DOCS_URI_MESSAGE}"
        )

    # If region not provided, use initializer location
    region = region or global_config.location
    region = region.split("-", 1)[0]

    for uri in re.finditer(
        prediction.CONTAINER_URI_PATTERN, prediction._SERVING_CONTAINER_URIS_STR
    ):
        match = uri.groups()
        if framework == match[1] and region == match[0] and accelerator == match[2]:
            if version != match[3]:
                # If URI matches all but version, add to alternative suggestion
                alt_versions.append(match[3].replace("-", "."))
            else:
                return uri.group()

    ALTERNATE_VERSIONS_MESSAGE = (
        f"Supported versions for {framework} include {', '.join(alt_versions)}. "
        if alt_versions
        else ""
    )

    raise ValueError(
        f"No serving container for {framework} {framework_version} "
        f"{'with accelerator ' if with_accelerator else ''}found. "
        f"{ALTERNATE_VERSIONS_MESSAGE}{DOCS_URI_MESSAGE}"
    )


def get_training_container_uri(
    framework: str,
    framework_version: str,
    region: str = None,
    with_accelerator: bool = False,
):
    raise NotImplementedError()
