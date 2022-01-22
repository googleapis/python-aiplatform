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

try:
    from fastapi import Request
    from fastapi import Response
except ImportError:
    raise ImportError(
        "FastAPI is not installed and is required to build model servers. "
        'Please install the SDK using "pip install python-aiplatform[prediction]"'
    )

from google.cloud.aiplatform.prediction.predictor import Predictor
from google.cloud.aiplatform.prediction.serializer import DefaultSerializer


class Handler:
    """Interface for Handler class to handle prediction requests."""

    def __init__(self, predictor: Predictor):
        """Initializes a Handler instance.

        Args:
            predictor (Predictor):
                Required. The Predictor instance this handler consumes.
        """
        pass

    def handle(self, request: Request) -> Response:
        """Handles a prediction request.

        Args:
            request (Request):
                The request sent to the application.

        Returns:
            The response of the prediction request.
        """
        pass


class DefaultHandler(Handler):
    """Default handler for handling the requests sent to the application."""

    def __init__(self, predictor: Predictor):
        """Initializes a DefaultHandler instance.

        Args:
            predictor (Predictor):
                Required. The Predictor instance this handler consumes.
        """
        self._predictor = predictor

    async def handle(self, request: Request) -> Response:
        """Handles a prediction request.

        Args:
            request (Request):
                Required. The request sent to the application.

        Returns:
            The response of the prediction request.
        """
        request_body = await request.body()
        prediction_input = DefaultSerializer.deserialize(
            request_body, request.headers.get("content-type")
        )
        prediction_results = self._predictor.postprocess(
            self._predictor.predict(self._predictor.preprocess(prediction_input))
        )
        data = DefaultSerializer.serialize(
            prediction_results, request.headers.get("accept")
        )
        return Response(content=data, media_type=request.headers.get("accept"))
