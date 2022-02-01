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

import os
from typing import Type

try:
    from fastapi import FastAPI
    from fastapi import Request
    from fastapi import Response
except ImportError:
    raise ImportError(
        "FastAPI is not installed and is required to build model servers. "
        'Please install the SDK using "pip install python-aiplatform[prediction]"'
    )

try:
    import uvicorn
except ImportError:
    raise ImportError(
        "Uvicorn is not installed and is required to run fastapi application. "
        'Please install the SDK using "pip install python-aiplatform[prediction]"'
    )

from google.cloud.aiplatform.prediction.handler import Handler
from google.cloud.aiplatform.prediction.handler import PredictionHandler
from google.cloud.aiplatform.prediction.predictor import Predictor


class ModelServer:
    """Base model server to do custom prediction routines."""

    def __init__(
        self, predictor: Predictor, handler_class: Type[Handler] = PredictionHandler
    ):
        """Initializes a fastapi application and sets the configs.

        Args:
            predictor (Predictor):
                Required. The predictor to be used to generate predictions.
            handler_class (Type[Handler]):
                Required. The handler class to handle requests with the given predictor.
        """
        self.predictor = predictor
        self.predictor.load(os.environ.get("AIP_STORAGE_URI"))

        self.handler = handler_class(self.predictor)

        if "AIP_HTTP_PORT" not in os.environ:
            raise ValueError(
                "The environment variable AIP_HTTP_PORT needs to be specified."
            )
        if (
            "AIP_HEALTH_ROUTE" not in os.environ
            or "AIP_PREDICT_ROUTE" not in os.environ
        ):
            raise ValueError(
                "Both of the environment variables AIP_HEALTH_ROUTE and "
                "AIP_PREDICT_ROUTE need to be specified."
            )
        self.http_port = int(os.environ.get("AIP_HTTP_PORT"))
        self.health_route = os.environ.get("AIP_HEALTH_ROUTE")
        self.predict_route = os.environ.get("AIP_PREDICT_ROUTE")

        self.app = FastAPI()
        self.app.add_api_route(
            path=self.health_route, endpoint=self.health, methods=["GET"],
        )
        self.app.add_api_route(
            path=self.predict_route, endpoint=self.predict, methods=["POST"],
        )

    def health(self):
        """Executes a health check."""
        return {}

    async def predict(self, request: Request) -> Response:
        """Executes a prediction.

        Args:
            request (Request):
                Required. The prediction request.

        Returns:
            The response containing prediction results.
        """
        return await self.handler.handle(request)

    def start(self):
        """Starts the fastapi application."""
        uvicorn.run(self.app, host="0.0.0.0", port=self.http_port)
