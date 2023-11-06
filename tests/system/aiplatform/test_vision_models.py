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
#

# pylint: disable=protected-access

import os
import tempfile

from google.cloud import aiplatform
from tests.system.aiplatform import e2e_base
from vertexai import vision_models as ga_vision_models
from vertexai.preview import vision_models
from PIL import Image as PIL_Image


def _create_blank_image(
    width: int = 100,
    height: int = 100,
) -> vision_models.Image:
    with tempfile.TemporaryDirectory() as temp_dir:
        image_path = os.path.join(temp_dir, "image.png")
        pil_image = PIL_Image.new(mode="RGB", size=(width, height))
        pil_image.save(image_path, format="PNG")
        return vision_models.Image.load_from_file(image_path)


class VisionModelTestSuite(e2e_base.TestEndToEnd):
    """System tests for vision models."""

    _temp_prefix = "temp_vision_models_test_"

    def test_image_captioning_model_get_captions(self):
        aiplatform.init(project=e2e_base._PROJECT, location=e2e_base._LOCATION)

        model = ga_vision_models.ImageCaptioningModel.from_pretrained("imagetext")
        image = _create_blank_image()
        captions = model.get_captions(
            image=image,
            # Optional:
            number_of_results=2,
            language="en",
        )
        assert len(captions) == 2

    def test_image_q_and_a_model_ask_question(self):
        aiplatform.init(project=e2e_base._PROJECT, location=e2e_base._LOCATION)

        model = ga_vision_models.ImageQnAModel.from_pretrained("imagetext")
        image = _create_blank_image()
        answers = model.ask_question(
            image=image,
            question="What color is the car in this image?",
            # Optional:
            number_of_results=2,
        )
        assert len(answers) == 2

    def test_multi_modal_embedding_model(self):
        aiplatform.init(project=e2e_base._PROJECT, location=e2e_base._LOCATION)

        model = ga_vision_models.MultiModalEmbeddingModel.from_pretrained(
            "multimodalembedding@001"
        )
        image = _create_blank_image()
        embeddings = model.get_embeddings(
            image=image,
            # Optional:
            contextual_text="this is a car",
        )
        # The service is expected to return the embeddings of size 1408
        assert len(embeddings.image_embedding) == 1408
        assert len(embeddings.text_embedding) == 1408

    def test_image_generation_model_generate_images(self):
        """Tests the image generation model generating images."""
        model = vision_models.ImageGenerationModel.from_pretrained(
            "imagegeneration@001"
        )

        # TODO(b/295946075): The service stopped supporting image sizes.
        # width = 1024
        # height = 768
        number_of_images = 4
        seed = 1
        guidance_scale = 15

        prompt1 = "Astronaut riding a horse"
        negative_prompt1 = "bad quality"
        image_response = model.generate_images(
            prompt=prompt1,
            # Optional:
            negative_prompt=negative_prompt1,
            number_of_images=number_of_images,
            # TODO(b/295946075): The service stopped supporting image sizes.
            # width=width,
            # height=height,
            seed=seed,
            guidance_scale=guidance_scale,
        )

        assert len(image_response.images) == number_of_images
        for idx, image in enumerate(image_response):
            # TODO(b/295946075): The service stopped supporting image sizes.
            # assert image._pil_image.size == (width, height)
            assert image.generation_parameters
            assert image.generation_parameters["prompt"] == prompt1
            assert image.generation_parameters["negative_prompt"] == negative_prompt1
            # TODO(b/295946075): The service stopped supporting image sizes.
            # assert image.generation_parameters["width"] == width
            # assert image.generation_parameters["height"] == height
            assert image.generation_parameters["seed"] == seed
            assert image.generation_parameters["guidance_scale"] == guidance_scale
            assert image.generation_parameters["index_of_image_in_batch"] == idx

        # Test saving and loading images
        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = os.path.join(temp_dir, "image.png")
            image_response[0].save(location=image_path)
            image1 = vision_models.GeneratedImage.load_from_file(image_path)
            # assert image1._pil_image.size == (width, height)
            assert image1.generation_parameters
            assert image1.generation_parameters["prompt"] == prompt1

            # Preparing mask
            mask_path = os.path.join(temp_dir, "mask.png")
            mask_pil_image = PIL_Image.new(mode="RGB", size=image1._pil_image.size)
            mask_pil_image.save(mask_path, format="PNG")
            mask_image = vision_models.Image.load_from_file(mask_path)

        # Test generating image from base image
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
        assert len(image_response2.images) == number_of_images
        for idx, image in enumerate(image_response2):
            # TODO(b/295946075): The service stopped supporting image sizes.
            # assert image._pil_image.size == (width, height)
            assert image.generation_parameters
            assert image.generation_parameters["prompt"] == prompt2
            assert image.generation_parameters["seed"] == seed
            assert image.generation_parameters["guidance_scale"] == guidance_scale
            assert image.generation_parameters["index_of_image_in_batch"] == idx
            assert "base_image_hash" in image.generation_parameters
            assert "mask_hash" in image.generation_parameters
