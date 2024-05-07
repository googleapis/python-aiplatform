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

"""Constants used by vertexai."""

PICKLE_PROTOCOL = 4

_START_EXECUTION_MSG = "Start remote execution on Vertex..."
_END_EXECUTION_MSG = "Remote execution is completed."

_V2_0_WARNING_MSG = """
After May 30, 2024, importing any code below will result in an error.
Please verify that you are explicitly pinning to a version of `google-cloud-aiplatform`
(e.g., google-cloud-aiplatform==[1.32.0, 1.49.0]) if you need to continue using this
library.

from vertexai.preview import (
    init,
    remote,
    VertexModel,
    register,
    from_pretrained,
    developer,
    hyperparameter_tuning,
    tabular_models,
)
"""
