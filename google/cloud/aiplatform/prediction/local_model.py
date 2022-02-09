# -*- coding: utf-8 -*-

# Copyright 2022 Google LLC
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

from pathlib import Path
from typing import Optional, Type

from google.cloud import aiplatform

from google.cloud.aiplatform import helpers
from google.cloud.aiplatform.compat.types import model as gca_model_compat
from google.cloud.aiplatform.docker_utils import build
from google.cloud.aiplatform.prediction.handler import Handler
from google.cloud.aiplatform.prediction.handler import PredictionHandler
from google.cloud.aiplatform.prediction.predictor import Predictor
from google.cloud.aiplatform.utils import prediction_utils

DEFAULT_PREDICT_ROUTE = "/predict"
DEFAULT_HEALTH_ROUTE = "/health"
DEFAULT_HTTP_PORT = 8080


class LocalModel:
    """Class that represents a local model."""

    def __init__(
        self, serving_container_spec: aiplatform.gapic.ModelContainerSpec,
    ):
        """Creates a local model instance.

        Args:
            serving_container_spec (aiplatform.gapic.ModelContainerSpec):
                Required. The container spec of the LocalModel instance.
        """
        self.serving_container_spec = serving_container_spec

    @classmethod
    def create_cpr_model(
        cls,
        src_dir: str,
        output_image: str,
        predictor: Optional[Type[Predictor]] = None,
        handler: Type[Handler] = PredictionHandler,
        base_image: str = "python:3.7",
        requirements_path: Optional[str] = None,
    ) -> "LocalModel":
        """Creates a local model from a custom predictor.

        This method creates a docker image to include user-provided predictor, serializer, and
        model server. It populates the entrypoint, entrypoint.py, right under the specified
        directory, src_dir, if it doesn't exist and generates a Dockerfile to build the image.

        Args:
            src_dir (str):
                Required. The path to the local directory including all needed files such as
                predictor. The whole directory will be copied to the image.
            output_image (str):
                Required. The image name of the built image.
            predictor (Type[Predictor]):
                Optional. The custom predictor consumed by handler to do prediction.
            handler (Type[Handler]):
                Required. The handler to handle requests in the model server.
            base_image (str):
                Required. The base image used to build the custom images.
            requirements_path (str):
                Optional. The path to the local requirements.txt file. This file will be copied
                to the image and the needed packages listed in it will be installed.

        Returns:
            local model: Instantiated representation of the local model.
        """
        entrypoint_file = "entrypoint.py"

        prediction_utils.populate_entrypoint_if_not_exists(
            src_dir, entrypoint_file, predictor=predictor, handler=handler,
        )

        is_prebuilt_prediction_image = helpers.is_prebuilt_prediction_container_uri(
            base_image
        )
        _ = build.build_image(
            base_image,
            src_dir,
            Path(src_dir).joinpath(entrypoint_file).as_posix(),
            output_image,
            requirements_path=requirements_path,
            exposed_ports=[DEFAULT_HTTP_PORT],
            pip_command="pip3" if is_prebuilt_prediction_image else "pip",
            python_command="python3" if is_prebuilt_prediction_image else "python",
        )

        container_spec = gca_model_compat.ModelContainerSpec(
            image_uri=output_image,
            predict_route=DEFAULT_PREDICT_ROUTE,
            health_route=DEFAULT_HEALTH_ROUTE,
        )

        return cls(container_spec)
