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
#

import functools
from typing import Any, Callable
from google.genai import _common
import warnings


def show_deprecation_warning_once(
    message: str,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to show a deprecation warning once for a function."""

    def decorator(func: Any) -> Any:
        warning_done = False

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal warning_done
            if not warning_done:
                warning_done = True
                warnings.warn(message, DeprecationWarning, stacklevel=2)

            # Suppress ExperimentalWarning while executing the deprecated wrapper
            with warnings.catch_warnings():
                # We ignore ExperimentalWarning because the user will see it
                # when they migrate to the new prompts module
                warnings.simplefilter("ignore", category=_common.ExperimentalWarning)
                return func(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper

    return decorator
