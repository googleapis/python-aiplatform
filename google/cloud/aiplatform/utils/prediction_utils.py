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

REGISTRY_REGEX = re.compile(r"^([\w\-]+\-docker\.pkg\.dev|([\w]+\.|)gcr\.io)")


def is_registry_uri(image_uri: str) -> bool:
    """Checks whether the image uri is in container registry or artifact registry.

    Args:
        image_uri (str):
            The image uri to check if it is in container registry or artifact registry.

    Returns:
        True if the image uri is in container registry or artifact registry.
    """
    return REGISTRY_REGEX.match(image_uri) is not None
