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
"""Classes for working with vision models."""

import base64
import dataclasses
import io
import pathlib
from typing import Any, List, Optional

from vertexai._model_garden import _model_garden_models

# pylint: disable=g-import-not-at-top
try:
    from IPython import display as IPython_display
except ImportError:
    IPython_display = None

try:
    from PIL import Image as PIL_Image
except ImportError:
    PIL_Image = None


class Image:
    """Image."""

    _image_bytes: bytes
    _loaded_image: Optional["PIL_Image.Image"] = None

    def __init__(self, image_bytes: bytes):
        """Creates an `Image` object.

        Args:
            image_bytes: Image file bytes. Image can be in PNG or JPEG format.
        """
        self._image_bytes = image_bytes

    @staticmethod
    def load_from_file(location: str) -> "Image":
        """Loads image from file.

        Args:
            location: Local path from where to load the image.

        Returns:
            Loaded image as an `Image` object.
        """
        image_bytes = pathlib.Path(location).read_bytes()
        image = Image(image_bytes=image_bytes)
        return image

    @property
    def _pil_image(self) -> "PIL_Image.Image":
        if self._loaded_image is None:
            self._loaded_image = PIL_Image.open(io.BytesIO(self._image_bytes))
        return self._loaded_image

    @property
    def _size(self):
        return self._pil_image.size

    def show(self):
        """Shows the image.

        This method only works when in a notebook environment.
        """
        if PIL_Image and IPython_display:
            IPython_display.display(self._pil_image)

    def save(self, location: str):
        """Saves image to a file.

        Args:
            location: Local path where to save the image.
        """
        pathlib.Path(location).write_bytes(self._image_bytes)

    def _as_base64_string(self) -> str:
        """Encodes image using the base64 encoding.

        Returns:
            Base64 encoding of the image as a string.
        """
        # ! b64encode returns `bytes` object, not ``str.
        # We need to convert `bytes` to `str`, otherwise we get service error:
        # "received initial metadata size exceeds limit"
        return base64.b64encode(self._image_bytes).decode("ascii")


class ImageCaptioningModel(
    _model_garden_models._ModelGardenModel  # pylint: disable=protected-access
):
    """Generates captions from image.

    Examples::

        model = ImageCaptioningModel.from_pretrained("imagetext@001")
        image = Image.load_from_file("image.png")
        captions = model.get_captions(
            image=image,
            # Optional:
            number_of_results=1,
            language="en",
        )
    """

    _INSTANCE_SCHEMA_URI = "gs://google-cloud-aiplatform/schema/predict/instance/vision_reasoning_model_1.0.0.yaml"
    _LAUNCH_STAGE = (
        _model_garden_models._SDK_GA_LAUNCH_STAGE  # pylint: disable=protected-access
    )

    def get_captions(
        self,
        image: Image,
        *,
        number_of_results: int = 1,
        language: str = "en",
    ) -> List[str]:
        """Generates captions for a given image.

        Args:
            image: The image to get captions for. Size limit: 10 MB.
            number_of_results: Number of captions to produce. Range: 1-3.
            language: Language to use for captions.
                Supported languages: "en", "fr", "de", "it", "es"

        Returns:
            A list of image caption strings.
        """
        instance = {
            "image": {
                "bytesBase64Encoded": image._as_base64_string()  # pylint: disable=protected-access
            }
        }
        parameters = {
            "sampleCount": number_of_results,
            "language": language,
        }
        response = self._endpoint.predict(
            instances=[instance],
            parameters=parameters,
        )
        return response.predictions


class ImageQnAModel(
    _model_garden_models._ModelGardenModel  # pylint: disable=protected-access
):
    """Answers questions about an image.

    Examples::

        model = ImageQnAModel.from_pretrained("imagetext@001")
        image = Image.load_from_file("image.png")
        answers = model.ask_question(
            image=image,
            question="What color is the car in this image?",
            # Optional:
            number_of_results=1,
        )
    """

    _INSTANCE_SCHEMA_URI = "gs://google-cloud-aiplatform/schema/predict/instance/vision_reasoning_model_1.0.0.yaml"
    _LAUNCH_STAGE = (
        _model_garden_models._SDK_GA_LAUNCH_STAGE  # pylint: disable=protected-access
    )

    def ask_question(
        self,
        image: Image,
        question: str,
        *,
        number_of_results: int = 1,
    ) -> List[str]:
        """Answers questions about an image.

        Args:
            image: The image to get captions for. Size limit: 10 MB.
            question: Question to ask about the image.
            number_of_results: Number of captions to produce. Range: 1-3.

        Returns:
            A list of answers.
        """
        instance = {
            "prompt": question,
            "image": {
                "bytesBase64Encoded": image._as_base64_string()  # pylint: disable=protected-access
            },
        }
        parameters = {
            "sampleCount": number_of_results,
        }
        response = self._endpoint.predict(
            instances=[instance],
            parameters=parameters,
        )
        return response.predictions


class MultiModalEmbeddingModel(_model_garden_models._ModelGardenModel):
    """Generates embedding vectors from images.

    Examples::

        model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding@001")
        image = Image.load_from_file("image.png")

        embeddings = model.get_embeddings(
            image=image,
            contextual_text="Hello world",
        )
        image_embedding = embeddings.image_embedding
        text_embedding = embeddings.text_embedding
    """

    _INSTANCE_SCHEMA_URI = "gs://google-cloud-aiplatform/schema/predict/instance/vision_embedding_model_1.0.0.yaml"

    _LAUNCH_STAGE = (
        _model_garden_models._SDK_GA_LAUNCH_STAGE  # pylint: disable=protected-access
    )

    def get_embeddings(
        self, image: Image, contextual_text: Optional[str] = None
    ) -> "MultiModalEmbeddingResponse":
        """Gets embedding vectors from the provided image.

        Args:
            image (Image):
                The image to generate embeddings for.
            contextual_text (str):
                Optional. Contextual text for your input image. If provided, the model will also
                generate an embedding vector for the provided contextual text. The returned image
                and text embedding vectors are in the same semantic space with the same dimensionality,
                and the vectors can be used interchangeably for use cases like searching image by text
                or searching text by image.

        Returns:
            ImageEmbeddingResponse:
                The image and text embedding vectors.
        """

        instance = {
            "image": {"bytesBase64Encoded": image._as_base64_string()},
            "features": [{"type": "IMAGE_EMBEDDING"}],
        }

        if contextual_text:
            instance["text"] = contextual_text

        response = self._endpoint.predict(instances=[instance])
        image_embedding = response.predictions[0].get("imageEmbedding")
        text_embedding = (
            response.predictions[0].get("textEmbedding")
            if "textEmbedding" in response.predictions[0]
            else None
        )
        return MultiModalEmbeddingResponse(
            image_embedding=image_embedding,
            _prediction_response=response,
            text_embedding=text_embedding,
        )


@dataclasses.dataclass
class MultiModalEmbeddingResponse:
    """The image embedding response.

    Attributes:
        image_embedding (List[float]):
            The emebedding vector generated from your image.
        text_embedding (List[float]):
            Optional. The embedding vector generated from the contextual text provided for your image.
    """

    image_embedding: List[float]
    _prediction_response: Any
    text_embedding: Optional[List[float]] = None
