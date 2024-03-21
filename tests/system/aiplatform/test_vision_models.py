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


def _load_image_from_gcs(
    gcs_uri: str = "gs://cloud-samples-data/vertex-ai/llm/prompts/landmark1.png",
) -> vision_models.Image:
    return vision_models.Image.load_from_file(gcs_uri)


def _load_video_from_gcs(
    gcs_uri: str = "gs://cloud-samples-data/vertex-ai-vision/highway_vehicles.mp4",
) -> vision_models.Video:
    return vision_models.Video.load_from_file(gcs_uri)


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

    def test_multi_modal_embedding_model_with_gcs_uri(self):
        aiplatform.init(project=e2e_base._PROJECT, location=e2e_base._LOCATION)

        model = ga_vision_models.MultiModalEmbeddingModel.from_pretrained(
            "multimodalembedding@001"
        )
        image = _load_image_from_gcs()
        video = _load_video_from_gcs()
        video_segment_config = vision_models.VideoSegmentConfig()
        embeddings = model.get_embeddings(
            image=image,
            video=video,
            # Optional:
            contextual_text="this is a car",
            video_segment_config=video_segment_config,
        )
        # The service is expected to return the embeddings of size 1408
        assert len(embeddings.image_embedding) == 1408
        assert len(embeddings.video_embeddings[0].embedding) == 1408
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
        language = "en"

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
            language=language,
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
            assert image.generation_parameters["language"] == language

        for width, height in [(1, 1), (9, 16), (16, 9), (4, 3), (3, 4)]:
            prompt_aspect_ratio = "A street lit up on a rainy night"
            model = vision_models.ImageGenerationModel.from_pretrained(
                "imagegeneration@006"
            )

            number_of_images = 4
            seed = 1
            guidance_scale = 15
            language = "en"
            aspect_ratio = f"{width}:{height}"

            image_response = model.generate_images(
                prompt=prompt_aspect_ratio,
                number_of_images=number_of_images,
                aspect_ratio=aspect_ratio,
                seed=seed,
                guidance_scale=guidance_scale,
                language=language,
            )

        assert len(image_response.images) == number_of_images
        for idx, image in enumerate(image_response):
            assert image.generation_parameters
            assert image.generation_parameters["prompt"] == prompt_aspect_ratio
            assert image.generation_parameters["aspect_ratio"] == aspect_ratio
            assert image.generation_parameters["seed"] == seed
            assert image.generation_parameters["guidance_scale"] == guidance_scale
            assert image.generation_parameters["index_of_image_in_batch"] == idx
            assert image.generation_parameters["language"] == language
            assert (
                abs(
                    float(image.size[0]) / float(image.size[1])
                    - float(width) / float(height)
                )
                <= 0.001
            )

        person_generation_prompts = [
            "A street lit up on a rainy night",
            "A woman walking down a street lit up on a rainy night",
            "A child walking down a street lit up on a rainy night",
            "A man walking down a street lit up on a rainy night",
        ]

        person_generation_levels = ["dont_allow", "allow_adult", "allow_all"]

        for i in range(0, 3):
            for j in range(0, i + 1):
                image_response = model.generate_images(
                    prompt=person_generation_prompts[j],
                    number_of_images=number_of_images,
                    seed=seed,
                    guidance_scale=guidance_scale,
                    language=language,
                    person_generation=person_generation_levels[j],
                )
                if i == j:
                    assert len(image_response.images) == number_of_images
                else:
                    assert len(image_response.images) < number_of_images
                for idx, image in enumerate(image_response):
                    assert (
                        image.generation_parameters["person_generation"]
                        == person_generation_levels[j]
                    )
                    assert (
                        image.generation_parameters["prompt"]
                        == person_generation_prompts[j]
                    )
                    assert image.generation_parameters["seed"] == seed
                    assert (
                        image.generation_parameters["guidance_scale"] == guidance_scale
                    )
                    assert image.generation_parameters["index_of_image_in_batch"] == idx
                    assert image.generation_parameters["language"] == language

        # Test saving and loading images
        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = os.path.join(temp_dir, "image.png")
            image_response[0].save(location=image_path)
            image1 = vision_models.GeneratedImage.load_from_file(image_path)
            # assert image1._pil_image.size == (width, height)
            assert image1.generation_parameters
            assert image1.generation_parameters["prompt"] == prompt1
            assert image1.generation_parameters["language"] == language

            # Preparing mask
            mask_path = os.path.join(temp_dir, "mask.png")
            mask_pil_image = PIL_Image.new(mode="RGB", size=image1._pil_image.size)
            mask_pil_image.save(mask_path, format="PNG")
            mask_image = vision_models.Image.load_from_file(mask_path)

            # Test generating image from base image
        prompt2 = "Ancient book style"
        edit_mode = "inpainting-insert"
        mask_mode = "foreground"
        mask_dilation = 0.06
        product_position = "fixed"
        output_mime_type = "image/jpeg"
        compression_quality = 0.90
        image_response2 = model.edit_image(
            prompt=prompt2,
            # Optional:
            number_of_images=number_of_images,
            seed=seed,
            guidance_scale=guidance_scale,
            base_image=image1,
            mask=mask_image,
            edit_mode=edit_mode,
            mask_mode=mask_mode,
            mask_dilation=mask_dilation,
            product_position=product_position,
            output_mime_type=output_mime_type,
            compression_quality=compression_quality,
            language=language,
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
            assert image.generation_parameters["edit_mode"] == edit_mode
            assert image.generation_parameters["mask_mode"] == mask_mode
            assert image.generation_parameters["mask_dilation"] == mask_dilation
            assert image.generation_parameters["product_position"] == product_position
            assert image.generation_parameters["mime_type"] == output_mime_type
            assert (
                image.generation_parameters["compression_quality"]
                == compression_quality
            )
            assert image.generation_parameters["language"] == language
            assert "base_image_hash" in image.generation_parameters
            assert "mask_hash" in image.generation_parameters

        prompt3 = "Chocolate chip cookies"
        edit_mode = "inpainting-insert"
        mask_mode = "semantic"
        segmentation_classes = [1, 13, 17, 9, 18]
        product_position = "fixed"
        output_mime_type = "image/png"

        image_response3 = model.edit_image(
            prompt=prompt3,
            number_of_images=number_of_images,
            seed=seed,
            guidance_scale=guidance_scale,
            base_image=image1,
            mask=mask_image,
            edit_mode=edit_mode,
            mask_mode=mask_mode,
            segmentation_classes=segmentation_classes,
            product_position=product_position,
            output_mime_type=output_mime_type,
            language=language,
        )

        assert len(image_response3.images) == number_of_images
        for idx, image in enumerate(image_response3):
            assert image.generation_parameters
            assert image.generation_parameters["prompt"] == prompt3
            assert image.generation_parameters["seed"] == seed
            assert image.generation_parameters["guidance_scale"] == guidance_scale
            assert image.generation_parameters["index_of_image_in_batch"] == idx
            assert image.generation_parameters["edit_mode"] == edit_mode
            assert image.generation_parameters["mask_mode"] == mask_mode
            assert (
                image.generation_parameters["segmentation_classes"]
                == segmentation_classes
            )
            assert image.generation_parameters["product_position"] == product_position
            assert image.generation_parameters["mime_type"] == output_mime_type
            assert image.generation_parameters["language"] == language
            assert "base_image_hash" in image.generation_parameters
            assert "mask_hash" in image.generation_parameters

    def test_image_verification_model_verify_image(self):
        """Tests the image verification model verifying watermark presence in an image."""
        verification_model = vision_models.ImageVerificationModel.from_pretrained(
            "imageverification@001"
        )
        model = vision_models.ImageGenerationModel.from_pretrained(
            "imagegeneration@005"
        )
        seed = 1
        guidance_scale = 15
        language = "en"
        image_verification_response = verification_model.verify_image(
            image=_create_blank_image()
        )
        assert image_verification_response["decision"] == "REJECT"

        prompt = "A street lit up on a rainy night"
        image_response = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            seed=seed,
            guidance_scale=guidance_scale,
            language=language,
            add_watermark=True,
        )
        assert len(image_response.images) == 1

        image_with_watermark = vision_models.Image(image_response.images[0].image_bytes)

        image_verification_response = verification_model.verify_image(
            image_with_watermark
        )
        assert image_verification_response["decision"] == "ACCEPT"
