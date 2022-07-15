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

import distutils.dir_util
import inspect
import logging
import os
from pathlib import Path
import re
import textwrap
from typing import Any, Optional, Sequence, Tuple, Type

from google.cloud import storage
from google.cloud.aiplatform.constants import prediction
from google.cloud.aiplatform.prediction.handler import Handler
from google.cloud.aiplatform.prediction.handler import PredictionHandler
from google.cloud.aiplatform.prediction.predictor import Predictor
from google.cloud.aiplatform.utils import path_utils

_logger = logging.getLogger(__name__)


REGISTRY_REGEX = re.compile(r"^([\w\-]+\-docker\.pkg\.dev|([\w]+\.|)gcr\.io)")
GCS_URI_PREFIX = "gs://"


def _inspect_source_from_class(
    custom_class: Type[Any],
    src_dir: str,
) -> Tuple[str, str]:
    """Inspects the source file from a custom class and returns its import path.

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


def populate_model_server_if_not_exists(
    src_dir: str,
    filename: str,
    predictor: Optional[Type[Predictor]] = None,
    handler: Type[Handler] = PredictionHandler,
) -> None:
    """Populates an entrypoint file in the provided directory if it doesn't exist.

    Args:
        src_dir (str):
            Required. The path to the local directory including all needed files such as
            predictor. The whole directory will be copied to the image.
        filename (str):
            Required. The stored model server file name.
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

    model_server_path = src_dir_path.joinpath(filename)
    if model_server_path.exists():
        _logger.info(
            f'"{model_server_path.as_posix()}" already exists, skip '
            f'generating "{filename}" in "{src_dir}".'
        )
        return

    predictor_import_line = ""
    predictor_name = None
    if predictor is not None:
        predictor_import, predictor_name = _inspect_source_from_class(
            predictor, src_dir
        )
        predictor_import_line = (
            "from {predictor_import_file} import {predictor_class}".format(
                predictor_import_file=predictor_import,
                predictor_class=predictor_name,
            )
        )

    handler_import_line = "from google.cloud.aiplatform import prediction"
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
        handler_import_line = (
            "from {handler_import_file} import {handler_class}".format(
                handler_import_file=handler_import,
                handler_class=handler_name,
            )
        )

    model_server_content = textwrap.dedent(
        '''
        import logging
        import os
        import traceback

        from fastapi import FastAPI
        from fastapi import HTTPException
        from fastapi import Request
        from fastapi import Response
        import uvicorn

        {predictor_import_line}
        {handler_import_line}

        class ModelServer:
            """Model server to do custom prediction routines."""

            def __init__(self):
                """Initializes a fastapi application and sets the configs.

                Args:
                    handler (Handler):
                        Required. The handler to handle requests.
                """
                self._init_logging()

                self.handler = {handler_class}(
                    os.environ.get("AIP_STORAGE_URI"), predictor={predictor_class},
                )

                if "AIP_HTTP_PORT" not in os.environ:
                    raise ValueError(
                        "The environment variable AIP_HTTP_PORT needs to be specified."
                    )
                if (
                    "AIP_HEALTH_ROUTE" not in os.environ
                    or "AIP_PREDICT_ROUTE" not in os.environ
                ):
                    raise ValueError(
                        "Both of the environment variables AIP_HEALTH_ROUTE and "
                        "AIP_PREDICT_ROUTE need to be specified."
                    )
                self.http_port = int(os.environ.get("AIP_HTTP_PORT"))
                self.health_route = os.environ.get("AIP_HEALTH_ROUTE")
                self.predict_route = os.environ.get("AIP_PREDICT_ROUTE")

                self.app = FastAPI()
                self.app.add_api_route(
                    path=self.health_route, endpoint=self.health, methods=["GET"],
                )
                self.app.add_api_route(
                    path=self.predict_route, endpoint=self.predict, methods=["POST"],
                )

            async def __call__(self, scope, receive, send):
                await self.app(scope, receive, send)

            def _init_logging(self):
                """Initializes the logging config."""
                logging.basicConfig(
                    format="%(asctime)s: %(message)s",
                    datefmt="%m/%d/%Y %I:%M:%S %p",
                    level=logging.INFO,
                )

            def health(self):
                """Executes a health check."""
                return {{}}

            async def predict(self, request: Request) -> Response:
                """Executes a prediction.

                Args:
                    request (Request):
                        Required. The prediction request.

                Returns:
                    The response containing prediction results.
                """
                try:
                    return await self.handler.handle(request)
                except HTTPException:
                    # Raises exception if it's a HTTPException.
                    raise
                except Exception as exception:
                    error_message = "An exception {{}} occurred. Arguments: {{}}.".format(
                        type(exception).__name__, exception.args
                    )
                    logging.info(
                        "{{}}\\nTraceback: {{}}".format(error_message, traceback.format_exc())
                    )

                    # Converts all other exceptions to HTTPException.
                    raise HTTPException(status_code=500, detail=error_message)
        '''.format(
            predictor_import_line=predictor_import_line,
            predictor_class=predictor_name,
            handler_import_line=handler_import_line,
            handler_class=handler_name,
        )
    )

    model_server_path.write_text(model_server_content)


def populate_entrypoint_if_not_exists(
    src_dir: str,
    filename: str,
) -> None:
    """Populates an entrypoint file in the provided directory if it doesn't exist.

    Args:
        src_dir (str):
            Required. The path to the local directory including all needed files such as
            predictor. The whole directory will be copied to the image.
        filename (str):
            Required. The stored entrypoint file name.

    Raises:
        ValueError: If the source directory is not a valid path.
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

    entrypoint_content = textwrap.dedent(
        """
        import multiprocessing
        import os

        import uvicorn


        if __name__ == "__main__":
            workers_per_core_str = os.getenv("WORKERS_PER_CORE", "1")
            max_workers_str = os.getenv("MAX_WORKERS")
            use_max_workers = None
            if max_workers_str:
                use_max_workers = int(max_workers_str)
            web_concurrency_str = os.getenv("WEB_CONCURRENCY")

            if not web_concurrency_str:
                cores = multiprocessing.cpu_count()
                workers_per_core = float(workers_per_core_str)
                default_web_concurrency = workers_per_core * cores
                web_concurrency = max(int(default_web_concurrency), 2)
                if use_max_workers:
                    web_concurrency = min(web_concurrency, use_max_workers)
                os.environ["WEB_CONCURRENCY"] = str(web_concurrency)

            uvicorn.run("cpr_model_server:ModelServer", host="0.0.0.0", port=int(os.environ.get("AIP_HTTP_PORT")), factory=True)
        """
    )

    entrypoint_path.write_text(entrypoint_content)


def is_registry_uri(image_uri: str) -> bool:
    """Checks whether the image uri is in container registry or artifact registry.

    Args:
        image_uri (str):
            The image uri to check if it is in container registry or artifact registry.

    Returns:
        True if the image uri is in container registry or artifact registry.
    """
    return REGISTRY_REGEX.match(image_uri) is not None


def get_prediction_aip_http_port(
    serving_container_ports: Optional[Sequence[int]] = None,
) -> int:
    """Gets the used prediction container port from serving container ports.

    If containerSpec.ports is specified during Model or LocalModel creation time, retrieve
    the first entry in this field. Otherwise use the default value of 8080. The environment
    variable AIP_HTTP_PORT will be set to this value.
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

    Returns:
        The first element in the serving_container_ports. If there is no any values in it,
        return the default http port.
    """
    return (
        serving_container_ports[0]
        if serving_container_ports is not None and len(serving_container_ports) > 0
        else prediction.DEFAULT_AIP_HTTP_PORT
    )


def download_model_artifacts(artifact_uri: str) -> None:
    """Prepares model artifacts in the current working directory.

    If artifact_uri is a GCS uri, the model artifacts will be downloaded to the current
    working directory.
    If artifact_uri is a local directory, the model artifacts will be copied to the current
    working directory.

    Args:
        artifact_uri (str):
            Required. The artifact uri that includes model artifacts.
    """
    if artifact_uri.startswith(GCS_URI_PREFIX):
        matches = re.match(f"{GCS_URI_PREFIX}(.*?)/(.*)", artifact_uri)
        bucket_name, prefix = matches.groups()

        gcs_client = storage.Client()
        bucket = gcs_client.get_bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=prefix)
        for blob in blobs:
            name_without_prefix = blob.name[len(prefix) :]
            name_without_prefix = (
                name_without_prefix[1:]
                if name_without_prefix.startswith("/")
                else name_without_prefix
            )
            file_split = name_without_prefix.split("/")
            directory = "/".join(file_split[0:-1])
            Path(directory).mkdir(parents=True, exist_ok=True)
            if name_without_prefix and not name_without_prefix.endswith("/"):
                blob.download_to_filename(name_without_prefix)
    else:
        # Copy files to the current working directory.
        distutils.dir_util.copy_tree(artifact_uri, ".")
