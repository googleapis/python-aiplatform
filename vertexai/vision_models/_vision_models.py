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
import hashlib
import io
import json
import pathlib
import typing
from typing import Any, Dict, List, Optional, Union

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


_SUPPORTED_UPSCALING_SIZES = [2048, 4096]


class Image:
    """Image."""

    __module__ = "vertexai.vision_models"

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


class ImageGenerationModel(
    _model_garden_models._ModelGardenModel  # pylint: disable=protected-access
):
    """Generates images from text prompt.

    Examples::

        model = ImageGenerationModel.from_pretrained("imagegeneration@002")
        response = model.generate_images(
            prompt="Astronaut riding a horse",
            # Optional:
            number_of_images=1,
            seed=0,
        )
        response[0].show()
        response[0].save("image1.png")
    """

    __module__ = "vertexai.preview.vision_models"

    _INSTANCE_SCHEMA_URI = "gs://google-cloud-aiplatform/schema/predict/instance/vision_generative_model_1.0.0.yaml"

    def _generate_images(
        self,
        prompt: str,
        *,
        negative_prompt: Optional[str] = None,
        number_of_images: int = 1,
        width: Optional[int] = None,
        height: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        seed: Optional[int] = None,
        base_image: Optional["Image"] = None,
        mask: Optional["Image"] = None,
    ) -> "ImageGenerationResponse":
        """Generates images from text prompt.

        Args:
            prompt: Text prompt for the image.
            negative_prompt: A description of what you want to omit in
                the generated images.
            number_of_images: Number of images to generate. Range: 1..8.
            width: Width of the image. One of the sizes must be 256 or 1024.
            height: Height of the image. One of the sizes must be 256 or 1024.
            guidance_scale: Controls the strength of the prompt.
                Suggested values are:
                * 0-9 (low strength)
                * 10-20 (medium strength)
                * 21+ (high strength)
            seed: Image generation random seed.
            base_image: Base image to use for the image generation.
            mask: Mask for the base image.

        Returns:
            An `ImageGenerationResponse` object.
        """
        # Note: Only a single prompt is supported by the service.
        instance = {"prompt": prompt}
        shared_generation_parameters = {
            "prompt": prompt,
            # b/295946075 The service stopped supporting image sizes.
            # "width": width,
            # "height": height,
            "number_of_images_in_batch": number_of_images,
        }

        if base_image:
            base_image_base64 = (
                base_image._as_base64_string()
            )  # pylint: disable=protected-access
            instance["image"] = {"bytesBase64Encoded": base_image_base64}
            base_image_hash_hex = hashlib.sha1(
                base_image._image_bytes  # pylint: disable=protected-access
            ).hexdigest()
            shared_generation_parameters["base_image_hash"] = base_image_hash_hex

        if mask:
            mask_image_base64 = (
                mask._as_base64_string()
            )  # pylint: disable=protected-access
            instance["mask"] = {"image": {"bytesBase64Encoded": mask_image_base64}}
            mask_image_hash_hex = hashlib.sha1(
                mask._image_bytes  # pylint: disable=protected-access
            ).hexdigest()
            shared_generation_parameters["mask_hash"] = mask_image_hash_hex

        parameters = {}
        max_size = max(width or 0, height or 0) or None
        if max_size:
            # Note: The size needs to be a string
            parameters["sampleImageSize"] = str(max_size)
            if height is not None and width is not None and height != width:
                parameters["aspectRatio"] = f"{width}:{height}"

        parameters["sampleCount"] = number_of_images
        if negative_prompt:
            parameters["negativePrompt"] = negative_prompt
            shared_generation_parameters["negative_prompt"] = negative_prompt

        if seed is not None:
            # Note: String seed and numerical seed give different results
            parameters["seed"] = seed
            shared_generation_parameters["seed"] = seed

        if guidance_scale is not None:
            parameters["guidanceScale"] = guidance_scale
            shared_generation_parameters["guidance_scale"] = guidance_scale

        response = self._endpoint.predict(
            instances=[instance],
            parameters=parameters,
        )

        generated_images: List["GeneratedImage"] = []
        for idx, prediction in enumerate(response.predictions):
            image_bytes = base64.b64decode(prediction["bytesBase64Encoded"])
            generation_parameters = dict(shared_generation_parameters)
            generation_parameters["index_of_image_in_batch"] = idx
            generated_image = GeneratedImage(
                image_bytes=image_bytes,
                generation_parameters=generation_parameters,
            )
            generated_images.append(generated_image)

        return ImageGenerationResponse(images=generated_images)

    def generate_images(
        self,
        prompt: str,
        *,
        negative_prompt: Optional[str] = None,
        number_of_images: int = 1,
        guidance_scale: Optional[float] = None,
        seed: Optional[int] = None,
    ) -> "ImageGenerationResponse":
        """Generates images from text prompt.

        Args:
            prompt: Text prompt for the image.
            negative_prompt: A description of what you want to omit in
                the generated images.
            number_of_images: Number of images to generate. Range: 1..8.
            guidance_scale: Controls the strength of the prompt.
                Suggested values are:
                * 0-9 (low strength)
                * 10-20 (medium strength)
                * 21+ (high strength)
            seed: Image generation random seed.

        Returns:
            An `ImageGenerationResponse` object.
        """
        return self._generate_images(
            prompt=prompt,
            negative_prompt=negative_prompt,
            number_of_images=number_of_images,
            # b/295946075 The service stopped supporting image sizes.
            width=None,
            height=None,
            guidance_scale=guidance_scale,
            seed=seed,
        )

    def edit_image(
        self,
        *,
        prompt: str,
        base_image: "Image",
        mask: Optional["Image"] = None,
        negative_prompt: Optional[str] = None,
        number_of_images: int = 1,
        guidance_scale: Optional[float] = None,
        seed: Optional[int] = None,
    ) -> "ImageGenerationResponse":
        """Edits an existing image based on text prompt.

        Args:
            prompt: Text prompt for the image.
            base_image: Base image from which to generate the new image.
            mask: Mask for the base image.
            negative_prompt: A description of what you want to omit in
                the generated images.
            number_of_images: Number of images to generate. Range: 1..8.
            guidance_scale: Controls the strength of the prompt.
                Suggested values are:
                * 0-9 (low strength)
                * 10-20 (medium strength)
                * 21+ (high strength)
            seed: Image generation random seed.

        Returns:
            An `ImageGenerationResponse` object.
        """
        return self._generate_images(
            prompt=prompt,
            negative_prompt=negative_prompt,
            number_of_images=number_of_images,
            guidance_scale=guidance_scale,
            seed=seed,
            base_image=base_image,
            mask=mask,
        )

    def upscale_image(
        self,
        image: Union["Image", "GeneratedImage"],
        new_size: Optional[int] = 2048,
    ) -> "Image":
        """Upscales an image.

        This supports upscaling images generated through the `generate_images()` method,
        or upscaling a new image that is 1024x1024.

        Examples::

            # Upscale a generated image
            model = ImageGenerationModel.from_pretrained("imagegeneration@002")
            response = model.generate_images(
                prompt="Astronaut riding a horse",
            )
            model.upscale_image(image=response[0])

            # Upscale a new 1024x1024 image
            my_image = Image.load_from_file("my-image.png")
            model.upscale_image(image=my_image)

        Args:
            image (Union[GeneratedImage, Image]):
                Required. The generated image to upscale.
            new_size (int):
                The size of the biggest dimension of the upscaled image. Only 2048 and 4096 are currently
                supported. Results in a 2048x2048 or 4096x4096 image. Defaults to 2048 if not provided.

        Returns:
            An `Image` object.
        """

        # Currently this method only supports 1024x1024 images
        if image._size[0] != 1024 and image._size[1] != 1024:
            raise ValueError(
                "Upscaling is currently only supported on images that are 1024x1024."
            )

        if new_size not in _SUPPORTED_UPSCALING_SIZES:
            raise ValueError(
                f"Only the folowing square upscaling sizes are currently supported: {_SUPPORTED_UPSCALING_SIZES}."
            )

        instance = {
            "prompt": "",
            "image": {"bytesBase64Encoded": image._as_base64_string()},
        }

        parameters = {
            "sampleImageSize": str(new_size),
            "sampleCount": 1,
            "mode": "upscale",
        }

        response = self._endpoint.predict(
            instances=[instance],
            parameters=parameters,
        )

        upscaled_image = response.predictions[0]

        if isinstance(image, GeneratedImage):
            generation_parameters = image.generation_parameters

        else:
            generation_parameters = {}

        generation_parameters["upscaled_image_size"] = new_size

        return GeneratedImage(
            image_bytes=base64.b64decode(upscaled_image["bytesBase64Encoded"]),
            generation_parameters=generation_parameters,
        )


@dataclasses.dataclass
class ImageGenerationResponse:
    """Image generation response.

    Attributes:
        images: The list of generated images.
    """

    __module__ = "vertexai.preview.vision_models"

    images: List["GeneratedImage"]

    def __iter__(self) -> typing.Iterator["GeneratedImage"]:
        """Iterates through the generated images."""
        yield from self.images

    def __getitem__(self, idx: int) -> "GeneratedImage":
        """Gets the generated image by index."""
        return self.images[idx]


_EXIF_USER_COMMENT_TAG_IDX = 0x9286
_IMAGE_GENERATION_PARAMETERS_EXIF_KEY = (
    "google.cloud.vertexai.image_generation.image_generation_parameters"
)


class GeneratedImage(Image):
    """Generated image."""

    __module__ = "vertexai.preview.vision_models"

    def __init__(
        self,
        image_bytes: bytes,
        generation_parameters: Dict[str, Any],
    ):
        """Creates a `GeneratedImage` object.

        Args:
            image_bytes: Image file bytes. Image can be in PNG or JPEG format.
            generation_parameters: Image generation parameter values.
        """
        super().__init__(image_bytes=image_bytes)
        self._generation_parameters = generation_parameters

    @property
    def generation_parameters(self):
        """Image generation parameters as a dictionary."""
        return self._generation_parameters

    @staticmethod
    def load_from_file(location: str) -> "GeneratedImage":
        """Loads image from file.

        Args:
            location: Local path from where to load the image.

        Returns:
            Loaded image as a `GeneratedImage` object.
        """
        base_image = Image.load_from_file(location=location)
        exif = base_image._pil_image.getexif()  # pylint: disable=protected-access
        exif_comment_dict = json.loads(exif[_EXIF_USER_COMMENT_TAG_IDX])
        generation_parameters = exif_comment_dict[_IMAGE_GENERATION_PARAMETERS_EXIF_KEY]
        return GeneratedImage(
            image_bytes=base_image._image_bytes,  # pylint: disable=protected-access
            generation_parameters=generation_parameters,
        )

    def save(self, location: str, include_generation_parameters: bool = True):
        """Saves image to a file.

        Args:
            location: Local path where to save the image.
            include_generation_parameters: Whether to include the image
                generation parameters in the image's EXIF metadata.
        """
        if include_generation_parameters:
            if not self._generation_parameters:
                raise ValueError("Image does not have generation parameters.")
            if not PIL_Image:
                raise ValueError(
                    "The PIL module is required for saving generation parameters."
                )

            exif = self._pil_image.getexif()
            exif[_EXIF_USER_COMMENT_TAG_IDX] = json.dumps(
                {_IMAGE_GENERATION_PARAMETERS_EXIF_KEY: self._generation_parameters}
            )
            self._pil_image.save(location, exif=exif)
        else:
            super().save(location=location)


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

    __module__ = "vertexai.vision_models"

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

    __module__ = "vertexai.vision_models"

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

    __module__ = "vertexai.vision_models"

    _INSTANCE_SCHEMA_URI = "gs://google-cloud-aiplatform/schema/predict/instance/vision_embedding_model_1.0.0.yaml"

    _LAUNCH_STAGE = (
        _model_garden_models._SDK_GA_LAUNCH_STAGE  # pylint: disable=protected-access
    )

    def get_embeddings(
        self, image: Optional[Image] = None, contextual_text: Optional[str] = None
    ) -> "MultiModalEmbeddingResponse":
        """Gets embedding vectors from the provided image.

        Args:
            image (Image):
                Optional. The image to generate embeddings for. One of `image` or `contextual_text` is required.
            contextual_text (str):
                Optional. Contextual text for your input image. If provided, the model will also
                generate an embedding vector for the provided contextual text. The returned image
                and text embedding vectors are in the same semantic space with the same dimensionality,
                and the vectors can be used interchangeably for use cases like searching image by text
                or searching text by image. One of `image` or `contextual_text` is required.

        Returns:
            ImageEmbeddingResponse:
                The image and text embedding vectors.
        """

        if not image and not contextual_text:
            raise ValueError("One of `image` or `contextual_text` is required.")

        instance = {}

        if image:
            instance["image"] = {"bytesBase64Encoded": image._as_base64_string()}

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
            Optional. The embedding vector generated from your image.
        text_embedding (List[float]):
            Optional. The embedding vector generated from the contextual text provided for your image.
    """

    __module__ = "vertexai.vision_models"

    _prediction_response: Any
    image_embedding: Optional[List[float]] = None
    text_embedding: Optional[List[float]] = None


class ImageTextModel(ImageCaptioningModel, ImageQnAModel):
    """Generates text from images.

    Examples::

        model = ImageTextModel.from_pretrained("imagetext@001")
        image = Image.load_from_file("image.png")

        captions = model.get_captions(
            image=image,
            # Optional:
            number_of_results=1,
            language="en",
        )

        answers = model.ask_question(
            image=image,
            question="What color is the car in this image?",
            # Optional:
            number_of_results=1,
        )
    """

    __module__ = "vertexai.vision_models"

    # NOTE: Using this ImageTextModel class is recommended over using ImageQnAModel or ImageCaptioningModel,
    # since SDK Model Garden classes should follow the design pattern of exactly 1 SDK class to 1 Model Garden schema URI

    _INSTANCE_SCHEMA_URI = "gs://google-cloud-aiplatform/schema/predict/instance/vision_reasoning_model_1.0.0.yaml"
    _LAUNCH_STAGE = (
        _model_garden_models._SDK_GA_LAUNCH_STAGE  # pylint: disable=protected-access
    )


class _PreviewImageTextModel(ImageTextModel):

    __module__ = "vertexai.preview.vision_models"

    _LAUNCH_STAGE = _model_garden_models._SDK_PUBLIC_PREVIEW_LAUNCH_STAGE
