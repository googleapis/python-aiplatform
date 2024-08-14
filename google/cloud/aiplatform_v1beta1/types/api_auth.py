# -*- coding: utf-8 -*-
# Copyright 2024 Google LLC
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


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "ApiAuth",
    },
)


class ApiAuth(proto.Message):
    r"""The generic reusable api auth config."""

    class ApiKeyConfig(proto.Message):
        r"""The API secret.

        Attributes:
            api_key_secret_version (str):
                Required. The SecretManager secret version
                resource name storing API key. e.g.
                projects/{project}/secrets/{secret}/versions/{version}
        """

        api_key_secret_version: str = proto.Field(
            proto.STRING,
            number=1,
        )


__all__ = tuple(sorted(__protobuf__.manifest))
