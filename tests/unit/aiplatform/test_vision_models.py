# -*- coding: utf-8 -*-

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
"""Unit tests for the vision models."""

# pylint: disable=protected-access,bad-continuation

import importlib
import os
import tempfile
from unittest import mock

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.compat.services import (
    model_garden_service_client,
)
from google.cloud.aiplatform.compat.services import prediction_service_client
from google.cloud.aiplatform.compat.types import (
    prediction_service as gca_prediction_service,
)
from google.cloud.aiplatform.compat.types import (
    publisher_model as gca_publisher_model,
)
from vertexai.preview import vision_models

from PIL import Image as PIL_Image
import pytest

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"

_IMAGE_TEXT_PUBLISHER_MODEL_DICT = {
    "name": "publishers/google/models/imagetext",
    "version_id": "001",
    "open_source_category": "PROPRIETARY",
    "launch_stage": gca_publisher_model.PublisherModel.LaunchStage.GA,
    "publisher_model_template": "projects/{project}/locations/{location}/publishers/google/models/imagetext@001",
    "predict_schemata": {
        "instance_schema_uri": "gs://google-cloud-aiplatform/schema/predict/instance/vision_reasoning_model_1.0.0.yaml",
        "parameters_schema_uri": "gs://google-cloud-aiplatfrom/schema/predict/params/vision_reasoning_model_1.0.0.yaml",
        "prediction_schema_uri": "gs://google-cloud-aiplatform/schema/predict/prediction/vision_reasoning_model_1.0.0.yaml",
    },
}

_IMAGE_EMBEDDING_PUBLISHER_MODEL_DICT = {
    "name": "publishers/google/models/multimodalembedding",
    "version_id": "001",
    "open_source_category": "PROPRIETARY",
    "launch_stage": gca_publisher_model.PublisherModel.LaunchStage.GA,
    "publisher_model_template": "projects/{project}/locations/{location}/publishers/google/models/multimodalembedding@001",
    "predict_schemata": {
        "instance_schema_uri": "gs://google-cloud-aiplatform/schema/predict/instance/vision_embedding_model_1.0.0.yaml",
        "parameters_schema_uri": "gs://google-cloud-aiplatfrom/schema/predict/params/vision_embedding_model_1.0.0.yaml",
        "prediction_schema_uri": "gs://google-cloud-aiplatform/schema/predict/prediction/vision_embedding_model_1.0.0.yaml",
    },
}


def generate_image_from_file(
    width: int = 100, height: int = 100
) -> vision_models.Image:
    with tempfile.TemporaryDirectory() as temp_dir:
        image_path = os.path.join(temp_dir, "image.png")
        pil_image = PIL_Image.new(mode="RGB", size=(width, height))
        pil_image.save(image_path, format="PNG")
        return vision_models.Image.load_from_file(image_path)


@pytest.mark.usefixtures("google_auth_mock")
class ImageCaptioningModelTests:
    """Unit tests for the image captioning models."""

    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_get_captions(self):
        """Tests the image captioning model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model(_IMAGE_TEXT_PUBLISHER_MODEL_DICT),
        ):
            model = vision_models.ImageCaptioningModel.from_pretrained("imagetext@001")

        image_captions = [
            "Caption 1",
            "Caption 2",
        ]
        gca_predict_response = gca_prediction_service.PredictResponse()
        gca_predict_response.predictions.extend(image_captions)

        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = os.path.join(temp_dir, "image.png")
            pil_image = PIL_Image.new(mode="RGB", size=(100, 100))
            pil_image.save(image_path, format="PNG")
            image = vision_models.Image.load_from_file(image_path)

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response,
        ):
            actual_captions = model.get_captions(image=image, number_of_results=2)
            assert actual_captions == image_captions


@pytest.mark.usefixtures("google_auth_mock")
class ImageQnAModelTests:
    """Unit tests for the image to text models."""

    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_get_captions(self):
        """Tests the image captioning model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _IMAGE_TEXT_PUBLISHER_MODEL_DICT
            ),
        ) as mock_get_publisher_model:
            model = vision_models.ImageQnAModel.from_pretrained("imagetext@001")

        mock_get_publisher_model.assert_called_once_with(
            name="publishers/google/models/imagetext@001",
            retry=base._DEFAULT_RETRY,
        )

        image_answers = [
            "Black square",
            "Black Square by Malevich",
        ]
        gca_predict_response = gca_prediction_service.PredictResponse()
        gca_predict_response.predictions.extend(image_answers)

        image = generate_image_from_file()

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response,
        ):
            actual_answers = model.ask_question(
                image=image,
                question="What is this painting?",
                number_of_results=2,
            )
            assert actual_answers == image_answers


@pytest.mark.usefixtures("google_auth_mock")
class TestMultiModalEmbeddingModels:
    """Unit tests for the image generation models."""

    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_image_embedding_model_with_only_image(self):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _IMAGE_EMBEDDING_PUBLISHER_MODEL_DICT
            ),
        ) as mock_get_publisher_model:
            model = vision_models.MultiModalEmbeddingModel.from_pretrained(
                "multimodalembedding@001"
            )

            mock_get_publisher_model.assert_called_once_with(
                name="publishers/google/models/multimodalembedding@001",
                retry=base._DEFAULT_RETRY,
            )

        test_image_embeddings = [0, 0]
        gca_predict_response = gca_prediction_service.PredictResponse()
        gca_predict_response.predictions.append(
            {"imageEmbedding": test_image_embeddings}
        )

        image = generate_image_from_file()

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response,
        ):
            embedding_response = model.get_embeddings(image=image)

        assert embedding_response.image_embedding == test_image_embeddings
        assert not embedding_response.text_embedding

    def test_image_embedding_model_with_image_and_text(self):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _IMAGE_EMBEDDING_PUBLISHER_MODEL_DICT
            ),
        ):
            model = vision_models.MultiModalEmbeddingModel.from_pretrained(
                "multimodalembedding@001"
            )

        test_embeddings = [0, 0]
        gca_predict_response = gca_prediction_service.PredictResponse()
        gca_predict_response.predictions.append(
            {"imageEmbedding": test_embeddings, "textEmbedding": test_embeddings}
        )

        image = generate_image_from_file()

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response,
        ):
            embedding_response = model.get_embeddings(
                image=image, contextual_text="hello world"
            )

        assert embedding_response.image_embedding == test_embeddings
        assert embedding_response.text_embedding == test_embeddings

    def test_image_embedding_model_with_only_text(self):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _IMAGE_EMBEDDING_PUBLISHER_MODEL_DICT
            ),
        ):
            model = vision_models.MultiModalEmbeddingModel.from_pretrained(
                "multimodalembedding@001"
            )

        test_embeddings = [0, 0]
        gca_predict_response = gca_prediction_service.PredictResponse()
        gca_predict_response.predictions.append({"textEmbedding": test_embeddings})

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response,
        ):
            embedding_response = model.get_embeddings(contextual_text="hello world")

        assert not embedding_response.image_embedding
        assert embedding_response.text_embedding == test_embeddings
