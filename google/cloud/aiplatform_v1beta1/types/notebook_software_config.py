# -*- coding: utf-8 -*-
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
from __future__ import annotations

from typing import MutableMapping, MutableSequence

import proto  # type: ignore

from google.cloud.aiplatform_v1beta1.types import env_var


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "PostStartupScriptConfig",
        "NotebookSoftwareConfig",
    },
)


class PostStartupScriptConfig(proto.Message):
    r"""

    Attributes:
        post_startup_script (str):

        post_startup_script_url (str):

        post_startup_script_behavior (google.cloud.aiplatform_v1beta1.types.PostStartupScriptConfig.PostStartupScriptBehavior):

    """

    class PostStartupScriptBehavior(proto.Enum):
        r"""

        Values:
            POST_STARTUP_SCRIPT_BEHAVIOR_UNSPECIFIED (0):
                No description available.
            RUN_ONCE (1):
                No description available.
            RUN_EVERY_START (2):
                No description available.
            DOWNLOAD_AND_RUN_EVERY_START (3):
                No description available.
        """
        POST_STARTUP_SCRIPT_BEHAVIOR_UNSPECIFIED = 0
        RUN_ONCE = 1
        RUN_EVERY_START = 2
        DOWNLOAD_AND_RUN_EVERY_START = 3

    post_startup_script: str = proto.Field(
        proto.STRING,
        number=1,
    )
    post_startup_script_url: str = proto.Field(
        proto.STRING,
        number=2,
    )
    post_startup_script_behavior: PostStartupScriptBehavior = proto.Field(
        proto.ENUM,
        number=3,
        enum=PostStartupScriptBehavior,
    )


class NotebookSoftwareConfig(proto.Message):
    r"""

    Attributes:
        env (MutableSequence[google.cloud.aiplatform_v1beta1.types.EnvVar]):
            Optional. Environment variables to be passed
            to the container. Maximum limit is 100.
        post_startup_script_config (google.cloud.aiplatform_v1beta1.types.PostStartupScriptConfig):

    """

    env: MutableSequence[env_var.EnvVar] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message=env_var.EnvVar,
    )
    post_startup_script_config: "PostStartupScriptConfig" = proto.Field(
        proto.MESSAGE,
        number=2,
        message="PostStartupScriptConfig",
    )


__all__ = tuple(sorted(__protobuf__.manifest))
