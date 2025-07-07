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
"""Utility functions for prompt optimizer."""

from . import types


def _get_service_account(
    config: types.PromptOptimizerVAPOConfigOrDict,
) -> str:
    """Get the service account from the config for the custom job."""
    if hasattr(config, "service_account") and config.service_account:
        if (
            hasattr(config, "service_account_project_number")
            and config.service_account_project_number
        ):
            raise ValueError(
                "Only one of service_account or service_account_project_number "
                "can be provided."
            )
        return config.service_account
    elif (
        hasattr(config, "service_account_project_number")
        and config.service_account_project_number
    ):
        return f"{config.service_account_project_number}-compute@developer.gserviceaccount.com"
    else:
        raise ValueError(
            "Either service_account or service_account_project_number is required."
        )
