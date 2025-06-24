# Copyright 2025 Google LLC
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

import functools
from typing import Any, Callable, Optional
import warnings

BASE_WARNING_MESSAGE = (
    "This feature is deprecated as of June 24, 2025 and will be removed on June"
    " 24, 2026. For details, see"
    " https://cloud.google.com/vertex-ai/generative-ai/docs/deprecations/genai-vertexai-sdk."
)


class DeprecationWarning(Warning):
    """A warning that a feature is deprecated."""


def genai_class_deprecation_warning(
    message: Optional[str] = BASE_WARNING_MESSAGE,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Deprecation warning decorator."""

    def decorator(cls) -> Any:

        original_class_init = cls.__init__

        @functools.wraps(original_class_init)
        def wrapper(self, *args: Any, **kwargs: Any) -> Any:
            warnings.warn(
                message=message,
                category=DeprecationWarning,
                stacklevel=2,
            )
            original_class_init(self, *args, **kwargs)

        cls.__init__ = wrapper
        return cls

    return decorator
