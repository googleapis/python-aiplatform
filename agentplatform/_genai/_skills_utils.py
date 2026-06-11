# Copyright 2026 Google LLC
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
"""Utility functions for Skills."""

import base64
import io
import os
import pathlib
import zipfile


def zip_directory(directory_path: pathlib.Path | str) -> bytes:
    """Zips a directory into memory and returns the bytes.

    Args:
        directory_path (pathlib.Path | str): Required. The local path to the
          directory.

    Returns:
        bytes: The zipped directory content.
    """
    directory_str = os.fspath(directory_path)
    if not os.path.isdir(directory_str):
        raise ValueError(f"Path is not a directory: {directory_str}")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(directory_str):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, directory_str)

                # Read actual file data
                with open(file_path, "rb") as f:
                    file_data = f.read()

                # Use deterministic ZipInfo (mtime: 1980-01-01 00:00:00)
                zinfo = zipfile.ZipInfo(arcname, date_time=(1980, 1, 1, 0, 0, 0))
                zinfo.compress_type = zipfile.ZIP_DEFLATED
                zinfo.external_attr = 0o644 << 16  # Constant file permissions

                zip_file.writestr(zinfo, file_data)
    return zip_buffer.getvalue()


def get_zipped_filesystem_payload(directory_path: pathlib.Path | str) -> str:
    """Zips a directory and base64-encodes the result to a UTF-8 string.

    Args:
        directory_path (pathlib.Path | str): Required. The local path to the
          directory.

    Returns:
        str: The base64-encoded zipped directory.
    """
    zip_bytes = zip_directory(directory_path)
    return base64.b64encode(zip_bytes).decode("utf-8")
