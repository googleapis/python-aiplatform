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

import re
from typing import Optional


CONTENT_TYPE_HEADER_REGEX = re.compile("^[Cc]ontent-?[Tt]ype")
ACCEPT_HEADER_REGEX = re.compile("^[Aa]ccept")
ANY = "*/*"
DEFAULT_ACCEPT = "application/json"


def _remove_parameter(value: Optional[str]):
    """Removes the parameter part from the header value.

    Referring to https://www.w3.org/Protocols/rfc2616/rfc2616-sec3.html#sec3.7.

    Args:
        value (str):
            Optional. The original full header value.

    Returns:
        The value without the parameter or None.
    """
    if value is None:
        return None

    return value.split(";")[0]


def get_content_type_from_headers(
    headers: Optional["starlette.datastructures.Headers"],  # noqa: F821
) -> Optional[str]:
    """Gets content type from headers.

    Args:
        headers (starlette.datastructures.Headers):
            Optional. The headers that the content type is retrived from.

    Returns:
        The content type or None.
    """
    if headers is not None:
        for key, value in headers.items():
            if CONTENT_TYPE_HEADER_REGEX.match(key):
                return _remove_parameter(value)

    return None


def get_accept_from_headers(
    headers: Optional["starlette.datastructures.Headers"],  # noqa: F821
) -> str:
    """Gets accept from headers.

    Default to "application/json" if it is "*/*" (any) or unset.

    Args:
        headers (starlette.datastructures.Headers):
            Optional. The headers that the accept is retrived from.

    Returns:
        The accept.
    """
    if headers is not None:
        for key, value in headers.items():
            if ACCEPT_HEADER_REGEX.match(key):
                return _remove_parameter(value) if value != ANY else DEFAULT_ACCEPT

    return DEFAULT_ACCEPT
