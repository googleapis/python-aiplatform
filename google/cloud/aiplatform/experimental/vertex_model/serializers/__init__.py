# -*- coding: utf-8 -*-

# Copyright 2021 Google LLC
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

import importlib
import sys

MODULE_NAMES = ["pandas", "pytorch"]


def build_map_safe():
    """ Fetches default serialization methods while catching any possible import
        errors that could be raised due to users failing to install external
        libraries.

    Returns:
        A dictionary mapping data types to tuples of deserialization and serialization
        methods that can be added to the user-defined data serialization library.

    Raises:
        ImportError should the user lack any necessary Python libraries
    """

    serializer_map = {}

    for module_name in MODULE_NAMES:
        try:
            full_module_name = f"google.cloud.aiplatform.experimental.vertex_model.serializers.{module_name}"
            importlib.import_module(full_module_name)

            module = sys.modules.get(
                f"google.cloud.aiplatform.experimental.vertex_model.serializers.{module_name}"
            )
            serializer_map.update(module._DATA_SERIALIZER_MAP)
        except ImportError:
            pass

    return serializer_map
