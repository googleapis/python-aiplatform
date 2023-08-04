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

        model = vision_models.ImageCaptioningModel.from_pretrained("imagetext")
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

        model = vision_models.ImageQnAModel.from_pretrained("imagetext")
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

        model = vision_models.MultiModalEmbeddingModel.from_pretrained(
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
