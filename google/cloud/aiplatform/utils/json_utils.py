# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
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

import json
from typing import Any, Dict, Optional

from google.auth import credentials as auth_credentials
from google.cloud import storage


def load_json(
    path: str,
    project: Optional[str] = None,
    credentials: Optional[auth_credentials.Credentials] = None,
) -> Dict[str, Any]:
    """Loads data from a JSON document.

    Args:
      path (str):
          Required. The path of the JSON document in Google Cloud Storage or
          local.
      project (str):
          Optional. Project to initiate the Storage client with.
      credentials (auth_credentials.Credentials):
          Optional. Credentials to use with Storage Client.

    Returns:
      A Dict object representing the JSON document.
    """
    if path.startswith("gs://"):
        return _load_json_from_gs_uri(path, project, credentials)
    else:
        return _load_json_from_local_file(path)


def _load_json_from_gs_uri(
    uri: str,
    project: Optional[str] = None,
    credentials: Optional[auth_credentials.Credentials] = None,
) -> Dict[str, Any]:
    """Loads data from a JSON document referenced by a GCS URI.

    Args:
      path (str):
          Required. GCS URI for JSON document.
      project (str):
          Optional. Project to initiate the Storage client with.
      credentials (auth_credentials.Credentials):
          Optional. Credentials to use with Storage Client.

    Returns:
      A Dict object representing the JSON document.
    """
    storage_client = storage.Client(project=project, credentials=credentials)
    blob = storage.Blob.from_string(uri, storage_client)
    return json.loads(blob.download_as_bytes())


def _load_json_from_local_file(file_path: str) -> Dict[str, Any]:
    """Loads data from a JSON local file.

    Args:
      file_path (str):
          Required. The local file path of the JSON document.

    Returns:
      A Dict object representing the JSON document.
    """
    with open(file_path) as f:
        return json.load(f)
