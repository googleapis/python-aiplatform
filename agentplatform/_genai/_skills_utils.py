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

import asyncio
import base64
import datetime
import io
import os
import pathlib
import time
from typing import Any, Awaitable, Callable
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


def await_operation(
    *,
    operation_name: str,
    get_operation_fn: Callable[..., Any],
    poll_interval: datetime.timedelta | float = 10.0,
    timeout_seconds: float = 300.0,
) -> Any:
    """Waits for a long running operation to complete.

    Args:
        operation_name (str): Required. The name of the operation.
        get_operation_fn (Callable): Required. Function to get the operation
          status.
        poll_interval (datetime.timedelta | float): The interval between polls.
        timeout_seconds (float): The maximum wait duration in seconds.

    Returns:
        Any: The completed operation.
    """
    if isinstance(poll_interval, datetime.timedelta):
        poll_seconds = poll_interval.total_seconds()
    else:
        poll_seconds = float(poll_interval)

    start_time = time.time()
    operation = get_operation_fn(operation_name=operation_name)
    while not operation.done:
        if (time.time() - start_time) > timeout_seconds:
            raise TimeoutError(
                f"Operation {operation_name} did not complete within the timeout "
                f"of {timeout_seconds} seconds."
            )
        time.sleep(poll_seconds)
        operation = get_operation_fn(operation_name=operation.name)
    return operation


async def await_operation_async(
    *,
    operation_name: str,
    get_operation_fn: Callable[..., Awaitable[Any]],
    poll_interval: datetime.timedelta | float = 10.0,
    timeout_seconds: float = 300.0,
) -> Any:
    """Waits for a long running operation to complete asynchronously.

    Args:
        operation_name (str): Required. The name of the operation.
        get_operation_fn (Callable): Required. Async function to get the operation
          status.
        poll_interval (datetime.timedelta | float): The interval between polls.
        timeout_seconds (float): The maximum wait duration in seconds.

    Returns:
        Any: The completed operation.
    """
    if isinstance(poll_interval, datetime.timedelta):
        poll_seconds = poll_interval.total_seconds()
    else:
        poll_seconds = float(poll_interval)

    start_time = time.time()
    operation = await get_operation_fn(operation_name=operation_name)
    while not operation.done:
        if (time.time() - start_time) > timeout_seconds:
            raise TimeoutError(
                f"Operation {operation_name} did not complete within the timeout "
                f"of {timeout_seconds} seconds."
            )
        await asyncio.sleep(poll_seconds)
        operation = await get_operation_fn(operation_name=operation.name)
    return operation
