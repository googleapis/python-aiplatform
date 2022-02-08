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

import json
from typing import Any, Optional

try:
    from fastapi import HTTPException
except ImportError:
    raise ImportError(
        "FastAPI is not installed and is required to build model servers. "
        'Please install the SDK using "pip install python-aiplatform[prediction]"'
    )


APPLICATOIN_JSON = "application/json"


class Serializer:
    """Interface to implement serialization and deserialization for prediction."""

    @staticmethod
    def deserialize(data: Any, content_type: Optional[str]) -> Any:
        """Deserializes the request data. Invoked before predict.

        Args:
            data (Any):
                Required. The request data sent to the application.
            content_type (str):
                Optional. The specified content type of the request.
        """
        raise NotImplementedError(
            "Serializer.deserialize has not been implemented yet."
        )

    @staticmethod
    def serialize(prediction: Any, accept: Optional[str]) -> Any:
        """Serializes the prediction results. Invoked after predict.

        Args:
            prediction (Any):
                Required. The generated prediction to be sent back to clients.
            accept (str):
                Optional. The specified content type of the response.
        """
        pass
        raise NotImplementedError("Serializer.serialize has not been implemented yet.")


class DefaultSerializer(Serializer):
    """Default serializer for serialization and deserialization for prediction."""

    @staticmethod
    def deserialize(data: Any, content_type: Optional[str]) -> Any:
        """Deserializes the request data. Invoked before predict.

        Args:
            data (Any):
                Required. The request data sent to the application.
            content_type (str):
                Optional. The specified content type of the request.
        """
        if content_type == APPLICATOIN_JSON:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"JSON deserialization failed for the request data: {data}.\n"
                        'To specify a different type, please set the "content-type" header '
                        "in the request.\nCurrently supported content-type in DefaultSerializer: "
                        f'"{APPLICATOIN_JSON}".'
                    ),
                )
        else:
            raise HTTPException(
                status_code=400,
                detail=("Unsupported content type of the request: %s." % content_type),
            )

    @staticmethod
    def serialize(prediction: Any, accept: Optional[str]) -> Any:
        """Serializes the prediction results. Invoked after predict.

        Args:
            prediction (Any):
                Required. The generated prediction to be sent back to clients.
            accept (str):
                Optional. The specified content type of the response.
        """
        if accept == APPLICATOIN_JSON:
            try:
                return json.dumps(prediction)
            except TypeError:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"JSON serialization failed for the prediction result: {prediction}.\n"
                        'To specify a different type, please set the "accept" header '
                        "in the request.\nCurrently supported accept in DefaultSerializer: "
                        f'"{APPLICATOIN_JSON}".'
                    ),
                )
        else:
            raise HTTPException(
                status_code=400,
                detail=("Unsupported content type of the response: %s." % accept),
            )
