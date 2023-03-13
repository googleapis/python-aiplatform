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

import os
import tempfile
from typing import Any
import cloudpickle

from google.cloud.aiplatform.utils import gcs_utils


def _cpkl_serializer(obj_name: str, obj_value: Any, target_dir: str):
    """Use cloudpickle to serialize a python object to the target directory."""

    if target_dir.startswith("gs://"):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_name = f"{obj_name}.cpkl"
            file_path = os.path.join(temp_dir, file_name)

            with open(file_path, mode="wb") as f:
                cloudpickle.dump(obj_value, f)

            gcs_uri = os.path.join(target_dir, file_name)
            gcs_utils.upload_to_gcs(file_path, gcs_uri)
    else:
        file_path = os.path.join(target_dir, f"{obj_name}.cpkl")
        with open(file_path, mode="wb") as f:
            cloudpickle.dump(obj_value, f)


def _cpkl_deserializer(obj_name: str, target_dir: str) -> Any:
    """Use cloudpickle to deserialize a python object given the object name and directory."""

    file_path = os.path.join(target_dir, f"{obj_name}.cpkl")

    if file_path.startswith("gs://"):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, f"{obj_name}.cpkl")
            gcs_utils.download_file_from_gcs(file_path, temp_file)
            with open(temp_file, mode="rb") as f:
                obj = cloudpickle.load(f)

    else:
        with open(file_path, mode="rb") as f:
            obj = cloudpickle.load(f)

    return obj
