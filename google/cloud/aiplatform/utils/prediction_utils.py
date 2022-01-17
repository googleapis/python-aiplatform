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
from pathlib import Path
import textwrap

from google.cloud.aiplatform.utils import path_utils

_logger = logging.getLogger(__name__)


def populate_entrypoint_if_not_exists(
    predictor, src_dir: str, filename: str,  # TODO: add Type[Predictor]
):
    """Populates an entrypoint file in the provided directory if it doesn't exist.

    Args:
        predictor (Type[Predictor]):
            Required. The custom predictor used to do prediction in the model server.
        src_dir (str):
            Required. The path to the local directory including all needed files such as
            predictor. The whole directory will be copied to the image.
        filename (str):
            Required. The stored entrypoint file name.
    """
    src_dir_path = Path(src_dir).expanduser()
    if not src_dir_path.exists():
        raise ValueError(
            f'"{src_dir}" is not a valid path to a directory. '
            f"Please specify a path to a directory which contains all your "
            f"code that needs to be copied to the docker image."
        )

    src_dir_abs_path = src_dir_path.resolve()

    entrypoint_path = src_dir_path.joinpath(filename)
    if entrypoint_path.exists():
        _logger.info(
            f'"{entrypoint_path.as_posix()}" already exists, skip '
            f'generating "{filename}" in "{src_dir}".'
        )
        return

    predictor_path = Path(inspect.getsourcefile(predictor)).resolve()
    if not path_utils._is_relative_to(predictor_path, src_dir_abs_path):
        raise ValueError(
            f'The file implementing "{predictor.__name__}" must be in "{src_dir}".'
        )

    predictor_import_path = predictor_path.relative_to(src_dir_abs_path)
    predictor_import_path = predictor_import_path.with_name(predictor_import_path.stem)
    predictor_import = predictor_import_path.as_posix().replace(os.sep, ".")

    entrypoint_content = textwrap.dedent(
        """
        from google.cloud.aiplatform import prediction
        from typing import Type
        from {predictor_import_file} import {predictor_class}

        def main(
            predictor: Type[prediction.predictor.Predictor],
            model_server: Type[prediction.model_server.ModelServer] = prediction.model_server.ModelServer,
            handler: Type[prediction.handler.Handler] = prediction.handler.DefaultHandler
        ):
            return model_server(predictor(), handler_class=handler).start()

        if __name__ == "__main__":
            main({predictor_class})
        """.format(
            predictor_import_file=predictor_import, predictor_class=predictor.__name__,
        )
    )

    entrypoint_path.write_text(entrypoint_content)
