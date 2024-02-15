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
# pylint: disable=protected-access, g-multiple-import
"""System tests for generative models."""

import pytest

# Google imports
from google import auth
from google.cloud import aiplatform
from tests.system.aiplatform import e2e_base
from vertexai import generative_models
from vertexai.preview import generative_models as preview_generative_models


class TestGenerativeModels(e2e_base.TestEndToEnd):
    """System tests for generative models."""

    _temp_prefix = "temp_generative_models_test_"

    def setup_method(self):
        super().setup_method()
        credentials, _ = auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            credentials=credentials,
        )

    def test_generate_content_from_text(self):
        model = generative_models.GenerativeModel("gemini-pro")
        response = model.generate_content("Why is sky blue?")
        assert response.text

    @pytest.mark.asyncio
    async def test_generate_content_async(self):
        model = generative_models.GenerativeModel("gemini-pro")
        response = await model.generate_content_async("Why is sky blue?")
        assert response.text

    def test_generate_content_streaming(self):
        model = generative_models.GenerativeModel("gemini-pro")
        stream = model.generate_content("Why is sky blue?", stream=True)
        for chunk in stream:
            assert chunk.text

    @pytest.mark.asyncio
    async def test_generate_content_streaming_async(self):
        model = generative_models.GenerativeModel("gemini-pro")
        async_stream = await model.generate_content_async(
            "Why is sky blue?",
            stream=True,
        )
        async for chunk in async_stream:
            assert chunk.text

    def test_generate_content_with_parameters(self):
        model = generative_models.GenerativeModel("gemini-pro")
        response = model.generate_content(
            contents="Why is sky blue?",
            generation_config=generative_models.GenerationConfig(
                temperature=0.1,
                top_p=0.95,
                top_k=20,
                candidate_count=1,
                max_output_tokens=100,
                stop_sequences=["STOP!"],
            ),
            safety_settings={
                generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
            },
        )
        assert response.text

    def test_generate_content_from_list_of_content_dict(self):
        model = generative_models.GenerativeModel("gemini-pro")
        response = model.generate_content(
            contents=[{"role": "user", "parts": [{"text": "Why is sky blue?"}]}]
        )
        assert response.text

    @pytest.mark.skip(
        reason="Breaking change in the gemini-pro-vision model. See b/315803556#comment3"
    )
    def test_generate_content_from_remote_image(self):
        vision_model = generative_models.GenerativeModel("gemini-pro-vision")
        image_part = generative_models.Part.from_uri(
            uri="gs://download.tensorflow.org/example_images/320px-Felis_catus-cat_on_snow.jpg",
            mime_type="image/jpeg",
        )
        response = vision_model.generate_content(image_part)
        assert response.text
        assert "cat" in response.text

    def test_generate_content_from_text_and_remote_image(self):
        vision_model = generative_models.GenerativeModel("gemini-pro-vision")
        image_part = generative_models.Part.from_uri(
            uri="gs://download.tensorflow.org/example_images/320px-Felis_catus-cat_on_snow.jpg",
            mime_type="image/jpeg",
        )
        response = vision_model.generate_content(
            contents=["What is shown in this image?", image_part],
        )
        assert response.text
        assert "cat" in response.text

    def test_generate_content_from_text_and_remote_video(self):
        vision_model = generative_models.GenerativeModel("gemini-pro-vision")
        video_part = generative_models.Part.from_uri(
            uri="gs://cloud-samples-data/video/animals.mp4",
            mime_type="video/mp4",
        )
        response = vision_model.generate_content(
            contents=["What is in the video?", video_part],
        )
        assert response.text
        assert "Zootopia" in response.text

    def test_grounding_google_search_retriever(self):
        model = preview_generative_models.GenerativeModel("gemini-pro")
        google_search_retriever_tool = (
            preview_generative_models.Tool.from_google_search_retrieval(
                preview_generative_models.grounding.GoogleSearchRetrieval(
                    disable_attribution=False
                )
            )
        )
        response = model.generate_content(
            "Why is sky blue?", tools=[google_search_retriever_tool]
        )
        assert response.text

    # Chat

    def test_send_message_from_text(self):
        model = generative_models.GenerativeModel("gemini-pro")
        chat = model.start_chat()
        response1 = chat.send_message("I really like fantasy books.")
        assert response1.text
        assert len(chat.history) == 2

        response2 = chat.send_message("What things do I like?.")
        assert response2.text
        assert len(chat.history) == 4
