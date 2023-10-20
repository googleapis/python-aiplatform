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

import base64
import importlib
import io
import os
import tempfile
from typing import Any, Dict
import unittest
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
import vertexai
from vertexai import vision_models as ga_vision_models
from vertexai.preview import (
    vision_models as preview_vision_models,
)

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


_IMAGE_GENERATION_PUBLISHER_MODEL_DICT = {
    "name": "publishers/google/models/imagegeneration",
    "version_id": "002",
    "open_source_category": "PROPRIETARY",
    "launch_stage": gca_publisher_model.PublisherModel.LaunchStage.GA,
    "publisher_model_template": "projects/{project}/locations/{location}/publishers/google/models/imagegeneration@002",
    "predict_schemata": {
        "instance_schema_uri": "gs://google-cloud-aiplatform/schema/predict/instance/vision_generative_model_1.0.0.yaml",
        "parameters_schema_uri": "gs://google-cloud-aiplatfrom/schema/predict/params/vision_generative_model_1.0.0.yaml",
        "prediction_schema_uri": "gs://google-cloud-aiplatform/schema/predict/prediction/vision_generative_model_1.0.0.yaml",
    },
}


def make_image_base64(width: int, height: int) -> str:
    image: PIL_Image.Image = PIL_Image.new(mode="RGB", size=(width, height))
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="PNG")
    image_b64 = base64.b64encode(image_bytes.getvalue()).decode("utf-8")
    return image_b64


def make_image_generation_response(
    width: int, height: int, count: int = 1
) -> Dict[str, Any]:
    predictions = []
    for _ in range(count):
        predictions.append(
            {
                "bytesBase64Encoded": make_image_base64(width, height),
                "mimeType": "image/png",
            }
        )
    return {"predictions": predictions}


def make_image_upscale_response(upscale_size: int) -> Dict[str, Any]:
    predictions = {
        "bytesBase64Encoded": make_image_base64(upscale_size, upscale_size),
        "mimeType": "image/png",
    }
    return {"predictions": [predictions]}


def generate_image_from_file(
    width: int = 100, height: int = 100
) -> ga_vision_models.Image:
    with tempfile.TemporaryDirectory() as temp_dir:
        image_path = os.path.join(temp_dir, "image.png")
        pil_image = PIL_Image.new(mode="RGB", size=(width, height))
        pil_image.save(image_path, format="PNG")
        return ga_vision_models.Image.load_from_file(image_path)


@pytest.mark.usefixtures("google_auth_mock")
class TestImageGenerationModels:
    """Unit tests for the image generation models."""

    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def _get_image_generation_model(self) -> preview_vision_models.ImageGenerationModel:
        """Gets the image generation model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _IMAGE_GENERATION_PUBLISHER_MODEL_DICT
            ),
        ) as mock_get_publisher_model:
            model = preview_vision_models.ImageGenerationModel.from_pretrained(
                "imagegeneration@002"
            )

        mock_get_publisher_model.assert_called_once_with(
            name="publishers/google/models/imagegeneration@002",
            retry=base._DEFAULT_RETRY,
        )

        return model

    def _get_preview_image_generation_model_top_level_from_pretrained(
        self,
    ) -> preview_vision_models.ImageGenerationModel:
        """Gets the image generation model from the top-level vertexai.preview.from_pretrained method."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _IMAGE_GENERATION_PUBLISHER_MODEL_DICT
            ),
        ) as mock_get_publisher_model:
            model = vertexai.preview.from_pretrained(
                foundation_model_name="imagegeneration@002"
            )

        mock_get_publisher_model.assert_called_with(
            name="publishers/google/models/imagegeneration@002",
            retry=base._DEFAULT_RETRY,
        )

        assert mock_get_publisher_model.call_count == 1

        return model

    def test_from_pretrained(self):
        model = self._get_image_generation_model()
        assert (
            model._endpoint_name
            == f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/publishers/google/models/imagegeneration@002"
        )

    def test_top_level_from_pretrained_preview(self):
        model = self._get_preview_image_generation_model_top_level_from_pretrained()
        assert (
            model._endpoint_name
            == f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/publishers/google/models/imagegeneration@002"
        )

    def test_generate_images(self):
        """Tests the image generation model."""
        model = self._get_image_generation_model()

        width = 1024
        # TODO(b/295946075) The service stopped supporting image sizes.
        # height = 768
        height = 1024
        number_of_images = 4
        seed = 1
        guidance_scale = 15

        image_generation_response = make_image_generation_response(
            width=width, height=height, count=number_of_images
        )
        gca_predict_response = gca_prediction_service.PredictResponse()
        gca_predict_response.predictions.extend(
            image_generation_response["predictions"]
        )

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response,
        ) as mock_predict:
            prompt1 = "Astronaut riding a horse"
            negative_prompt1 = "bad quality"
            image_response = model.generate_images(
                prompt=prompt1,
                # Optional:
                negative_prompt=negative_prompt1,
                number_of_images=number_of_images,
                # TODO(b/295946075) The service stopped supporting image sizes.
                # width=width,
                # height=height,
                seed=seed,
                guidance_scale=guidance_scale,
            )
            predict_kwargs = mock_predict.call_args[1]
            actual_parameters = predict_kwargs["parameters"]
            actual_instance = predict_kwargs["instances"][0]
            assert actual_instance["prompt"] == prompt1
            assert actual_parameters["negativePrompt"] == negative_prompt1
            # TODO(b/295946075) The service stopped supporting image sizes.
            # assert actual_parameters["sampleImageSize"] == str(max(width, height))
            # assert actual_parameters["aspectRatio"] == f"{width}:{height}"
            assert actual_parameters["seed"] == seed
            assert actual_parameters["guidanceScale"] == guidance_scale

        assert len(image_response.images) == number_of_images
        for idx, image in enumerate(image_response):
            assert image._pil_image.size == (width, height)
            assert image.generation_parameters
            assert image.generation_parameters["prompt"] == prompt1
            assert image.generation_parameters["negative_prompt"] == negative_prompt1
            # TODO(b/295946075) The service stopped supporting image sizes.
            # assert image.generation_parameters["width"] == width
            # assert image.generation_parameters["height"] == height
            assert image.generation_parameters["seed"] == seed
            assert image.generation_parameters["guidance_scale"] == guidance_scale
            assert image.generation_parameters["index_of_image_in_batch"] == idx
            image.show()

        # Test saving and loading images
        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = os.path.join(temp_dir, "image.png")
            image_response[0].save(location=image_path)
            image1 = preview_vision_models.GeneratedImage.load_from_file(image_path)
            # assert image1._pil_image.size == (width, height)
            assert image1.generation_parameters
            assert image1.generation_parameters["prompt"] == prompt1

            # Preparing mask
            mask_path = os.path.join(temp_dir, "mask.png")
            mask_pil_image = PIL_Image.new(mode="RGB", size=image1._pil_image.size)
            mask_pil_image.save(mask_path, format="PNG")
            mask_image = preview_vision_models.Image.load_from_file(mask_path)

        # Test generating image from base image
        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response,
        ) as mock_predict:
            prompt2 = "Ancient book style"
            image_response2 = model.edit_image(
                prompt=prompt2,
                # Optional:
                number_of_images=number_of_images,
                seed=seed,
                guidance_scale=guidance_scale,
                base_image=image1,
                mask=mask_image,
            )
            predict_kwargs = mock_predict.call_args[1]
            actual_instance = predict_kwargs["instances"][0]
            assert actual_instance["prompt"] == prompt2
            assert actual_instance["image"]["bytesBase64Encoded"]
            assert actual_instance["mask"]["image"]["bytesBase64Encoded"]

        assert len(image_response2.images) == number_of_images
        for image in image_response2:
            assert image._pil_image.size == (width, height)
            assert image.generation_parameters
            assert image.generation_parameters["prompt"] == prompt2
            assert image.generation_parameters["base_image_hash"]
            assert image.generation_parameters["mask_hash"]

    @unittest.skip(reason="b/295946075 The service stopped supporting image sizes.")
    def test_generate_images_requests_square_images_by_default(self):
        """Tests that the model class generates square image by default."""
        model = self._get_image_generation_model()

        image_size = 1024

        # No height specified
        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
        ) as mock_predict:
            model.generate_images(
                prompt="test",
                width=image_size,
            )
            predict_kwargs = mock_predict.call_args[1]
            actual_parameters = predict_kwargs["parameters"]
            assert actual_parameters["sampleImageSize"] == str(image_size)
            assert "aspectRatio" not in actual_parameters

        # No width specified
        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
        ) as mock_predict:
            model.generate_images(
                prompt="test",
                height=image_size,
            )
            predict_kwargs = mock_predict.call_args[1]
            actual_parameters = predict_kwargs["parameters"]
            assert actual_parameters["sampleImageSize"] == str(image_size)
            assert "aspectRatio" not in actual_parameters

        # No width or height specified
        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
        ) as mock_predict:
            model.generate_images(prompt="test")
            predict_kwargs = mock_predict.call_args[1]
            actual_parameters = predict_kwargs["parameters"]
            assert "sampleImageSize" not in actual_parameters

    def test_upscale_image_on_generated_image(self):
        """Tests image upscaling on generated images."""
        model = self._get_image_generation_model()

        image_generation_response = make_image_generation_response(
            count=1, height=1024, width=1024
        )
        gca_generation_response = gca_prediction_service.PredictResponse()
        gca_generation_response.predictions.extend(
            image_generation_response["predictions"]
        )

        image_upscale_response = make_image_upscale_response(upscale_size=2048)
        gca_upscale_response = gca_prediction_service.PredictResponse()
        gca_upscale_response.predictions.extend(image_upscale_response["predictions"])

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_generation_response,
        ):
            prompt = "Ancient book style"
            image_generation_response = model.generate_images(
                prompt=prompt,
            )

            with mock.patch.object(
                target=prediction_service_client.PredictionServiceClient,
                attribute="predict",
                return_value=gca_upscale_response,
            ) as mock_upscale:
                upscaled_image = model.upscale_image(image=image_generation_response[0])

                predict_kwargs = mock_upscale.call_args[1]
                actual_instance = predict_kwargs["instances"][0]
                assert actual_instance["image"]["bytesBase64Encoded"]

                image_upscale_parameters = predict_kwargs["parameters"]
                assert image_upscale_parameters["sampleImageSize"] == str(
                    upscaled_image._size[0]
                )
                assert image_upscale_parameters["mode"] == "upscale"

                assert upscaled_image._image_bytes
                assert upscaled_image.generation_parameters["prompt"] == prompt

    def test_upscale_image_on_provided_image(self):
        """Tests image upscaling on generated images."""
        model = self._get_image_generation_model()

        image_generation_response = make_image_generation_response(
            count=1, height=1024, width=1024
        )
        gca_generation_response = gca_prediction_service.PredictResponse()
        gca_generation_response.predictions.extend(
            image_generation_response["predictions"]
        )

        image_upscale_response = make_image_upscale_response(upscale_size=4096)
        gca_upscale_response = gca_prediction_service.PredictResponse()
        gca_upscale_response.predictions.extend(image_upscale_response["predictions"])

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_upscale_response,
        ) as mock_upscale:
            test_image = generate_image_from_file(height=1024, width=1024)

            upscaled_image = model.upscale_image(image=test_image, new_size=4096)

            predict_kwargs = mock_upscale.call_args[1]
            actual_instance = predict_kwargs["instances"][0]
            assert actual_instance["image"]["bytesBase64Encoded"]

            image_upscale_parameters = predict_kwargs["parameters"]
            assert (
                image_upscale_parameters["sampleImageSize"]
                == str(upscaled_image._size[0])
                == str(upscaled_image.generation_parameters["upscaled_image_size"])
            )
            assert image_upscale_parameters["mode"] == "upscale"

            assert upscaled_image._image_bytes
            assert isinstance(upscaled_image, preview_vision_models.GeneratedImage)

    def test_upscale_image_raises_if_not_1024x1024(self):
        """Tests image upscaling on generated images."""
        model = self._get_image_generation_model()

        test_image = generate_image_from_file(height=100, width=100)

        with pytest.raises(ValueError):
            model.upscale_image(image=test_image)


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
            model = ga_vision_models.ImageCaptioningModel.from_pretrained(
                "imagetext@001"
            )

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
            image = preview_vision_models.Image.load_from_file(image_path)

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

    def test_ask_question(self):
        """Tests the image Q&A model."""
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
            model = ga_vision_models.ImageQnAModel.from_pretrained("imagetext@001")

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
            model = preview_vision_models.MultiModalEmbeddingModel.from_pretrained(
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
            model = preview_vision_models.MultiModalEmbeddingModel.from_pretrained(
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
            model = ga_vision_models.MultiModalEmbeddingModel.from_pretrained(
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


@pytest.mark.usefixtures("google_auth_mock")
class ImageTextModelTests:
    """Unit tests for the image to text models."""

    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_ask_question(self):
        """Tests question answering with ImageTextModel."""
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
            model = ga_vision_models.ImageTextModel.from_pretrained("imagetext@001")

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

    def test_get_captions(self):
        """Tests image captioning with ImageTextModel."""

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model(_IMAGE_TEXT_PUBLISHER_MODEL_DICT),
        ):
            model = ga_vision_models.ImageTextModel.from_pretrained("imagetext@001")

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
            image = preview_vision_models.Image.load_from_file(image_path)

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response,
        ):
            actual_captions = model.get_captions(image=image, number_of_results=2)
            assert actual_captions == image_captions
