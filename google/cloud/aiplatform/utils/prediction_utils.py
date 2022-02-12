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

import inspect
import logging
import os
import re
from pathlib import Path
import textwrap
from typing import Any, Optional, Sequence, Type

from google.cloud.aiplatform.constants import prediction
from google.cloud.aiplatform.prediction.handler import Handler
from google.cloud.aiplatform.prediction.handler import PredictionHandler
from google.cloud.aiplatform.prediction.predictor import Predictor
from google.cloud.aiplatform.utils import path_utils

_logger = logging.getLogger(__name__)

REGISTRY_REGEX = re.compile(r"^([\w\-]+\-docker\.pkg\.dev|([\w]+\.|)gcr\.io)")


def _inspect_source_from_class(
    custom_class: Type[Any], src_dir: str,
):
    """Inspects the source file from a custom class and retruns its import path.

    Args:
        custom_class (Type[Any]):
            Required. The custom class needs to be inspected for the source file.
        src_dir (str):
            Required. The path to the local directory including all needed files.
            The source file of the custom class must be in this directory.

    Returns:
        (import_from, class_name): the source file path in python import format
            and the custom class name.

    Raises:
        ValueError: If the source file of the custom class is not in the source
            directory.
    """
    src_dir_abs_path = Path(src_dir).expanduser().resolve()

    custom_class_name = custom_class.__name__

    custom_class_path = Path(inspect.getsourcefile(custom_class)).resolve()
    if not path_utils._is_relative_to(custom_class_path, src_dir_abs_path):
        raise ValueError(
            f'The file implementing "{custom_class_name}" must be in "{src_dir}".'
        )

    custom_class_import_path = custom_class_path.relative_to(src_dir_abs_path)
    custom_class_import_path = custom_class_import_path.with_name(
        custom_class_import_path.stem
    )
    custom_class_import = custom_class_import_path.as_posix().replace(os.sep, ".")

    return custom_class_import, custom_class_name


def populate_entrypoint_if_not_exists(
    src_dir: str,
    filename: str,
    predictor: Optional[Type[Predictor]] = None,
    handler: Type[Handler] = PredictionHandler,
):
    """Populates an entrypoint file in the provided directory if it doesn't exist.

    Args:
        src_dir (str):
            Required. The path to the local directory including all needed files such as
            predictor. The whole directory will be copied to the image.
        filename (str):
            Required. The stored entrypoint file name.
        predictor (Type[Predictor]):
            Optional. The custom predictor consumed by handler to do prediction.
        handler (Type[Handler]):
            Required. The handler to handle requests in the model server.

    Raises:
        ValueError: If the source directory is not a valid path, if the source file
            of the predictor is not in the source directory, if handler is None, or
            if the source file of the custom handler is not in the source directory.
    """
    src_dir_path = Path(src_dir).expanduser()
    if not src_dir_path.exists():
        raise ValueError(
            f'"{src_dir}" is not a valid path to a directory. '
            f"Please specify a path to a directory which contains all your "
            f"code that needs to be copied to the docker image."
        )

    entrypoint_path = src_dir_path.joinpath(filename)
    if entrypoint_path.exists():
        _logger.info(
            f'"{entrypoint_path.as_posix()}" already exists, skip '
            f'generating "{filename}" in "{src_dir}".'
        )
        return

    predictor_import_line = ""
    predictor_name = None
    if predictor is not None:
        predictor_import, predictor_name = _inspect_source_from_class(
            predictor, src_dir
        )
        predictor_import_line = "from {predictor_import_file} import {predictor_class}".format(
            predictor_import_file=predictor_import, predictor_class=predictor_name,
        )

    handler_import_line = ""
    handler_name = "prediction.handler.PredictionHandler"

    if handler is None:
        raise ValueError("A handler must be provided but handler is None.")
    elif handler == PredictionHandler:
        if predictor is None:
            raise ValueError(
                "PredictionHandler must have a predictor class but predictor is None."
            )
    else:
        handler_import, handler_name = _inspect_source_from_class(handler, src_dir)
        handler_import_line = "from {handler_import_file} import {handler_class}".format(
            handler_import_file=handler_import, handler_class=handler_name,
        )

    entrypoint_content = textwrap.dedent(
        """
        import os
        from typing import Optional, Type

        from google.cloud.aiplatform import prediction

        {predictor_import_line}
        {handler_import_line}

        def main(
            predictor_class: Optional[Type[prediction.predictor.Predictor]] = None,
            handler_class: Type[prediction.handler.Handler] = prediction.handler.PredictionHandler
            model_server_class: Type[prediction.model_server.ModelServer] = prediction.model_server.ModelServer,
        ):
            handler = handler_class(
                os.environ.get("AIP_STORAGE_URI"), predictor=predictor_class
            )

            return model_server_class(handler).start()

        if __name__ == "__main__":
            main(
                predictor_class={predictor_class},
                handler_class={handler_class},
            )
        """.format(
            predictor_import_line=predictor_import_line,
            predictor_class=predictor_name,
            handler_import_line=handler_import_line,
            handler_class=handler_name,
        )
    )

    entrypoint_path.write_text(entrypoint_content)


def get_prediction_aip_http_port(
    serving_container_ports: Optional[Sequence[int]] = None,
):
    """Gets the used prediction container port from serving container ports.

    When you create a Model, set the containerSpec.ports field. The first entry in this
    field becomes the value of AIP_HTTP_PORT. Default value is 8080.
    See https://cloud.google.com/vertex-ai/docs/predictions/custom-container-requirements
    for more details.

    Args:
        serving_container_ports (Sequence[int]):
            Optional. Declaration of ports that are exposed by the container. This field is
            primarily informational, it gives Vertex AI information about the
            network connections the container uses. Listing or not a port here has
            no impact on whether the port is actually exposed, any port listening on
            the default "0.0.0.0" address inside a container will be accessible from
            the network.
    """
    return (
        serving_container_ports[0]
        if serving_container_ports is not None and len(serving_container_ports) > 0
        else prediction.DEFAULT_AIP_HTTP_PORT
    )


def is_registry_uri(image_uri: str) -> bool:
    """Checks whether the image uri is in container registry or artifact registry.

    Args:
        image_uri (str):
            The image uri to check if it is in container registry or artifact registry.

    Returns:
        True if the image uri is in container registry or artifact registry.
    """
    return REGISTRY_REGEX.match(image_uri) is not None
