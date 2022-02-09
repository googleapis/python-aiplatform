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
                return value

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
                if value == ANY:
                    return DEFAULT_ACCEPT
                return value

    return DEFAULT_ACCEPT
