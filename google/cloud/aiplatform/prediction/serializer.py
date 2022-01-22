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
from typing import Any, Dict, Optional

try:
    from fastapi import HTTPException
except ImportError:
    raise ImportError(
        "FastAPI is not installed and is required to build model servers. "
        'Please install the SDK using "pip install python-aiplatform[prediction]"'
    )


class Serializer:
    """Interface to implement serialization and deserialization for prediction."""

    @staticmethod
    def deserialize(data: Any, content_type: Optional[str],) -> Any:
        """Deserializes the request data. Invoked before predict.

        Args:
            data (Any):
                Required. The request data sent to the application.
            content_type (Optional[str]):
                Optional. The specified content type of the request.
        """
        pass

    @staticmethod
    def serialize(prediction: Dict, accept: Optional[str],) -> Any:
        """Serializes the prediction results. Invoked after predict.

        Args:
            prediction (Dict):
                Required. The generated prediction to be sent back to clients.
            accept (Optional[str]):
                Optional. The specified content type of the response.
        """
        pass


class DefaultSerializer(Serializer):
    """Default serializer for serialization and deserialization for prediction."""

    @staticmethod
    def deserialize(data: Any, content_type: Optional[str],) -> Any:
        """Deserializes the request data. Invoked before predict.

        Args:
            data (Any):
                Required. The request data sent to the application.
            content_type (Optional[str]):
                Optional. The specified content type of the request.
        """
        if content_type == "application/json":
            return json.loads(data)
        else:
            raise HTTPException(
                status_code=400,
                detail=("Unsupported content type of the request: %s." % content_type),
            )

    @staticmethod
    def serialize(prediction: Dict, accept: Optional[str],) -> Any:
        """Serializes the prediction results. Invoked after predict.

        Args:
            prediction (Dict):
                Required. The generated prediction to be sent back to clients.
            accept (Optional[str]):
                Optional. The specified content type of the response.
        """
        if accept == "application/json":
            return json.dumps(prediction)
        else:
            raise HTTPException(
                status_code=400,
                detail=("Unsupported content type of the response: %s." % accept),
            )
