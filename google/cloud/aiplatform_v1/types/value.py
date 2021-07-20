# -*- coding: utf-8 -*-
# Copyright 2020 Google LLC
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
import proto  # type: ignore


__protobuf__ = proto.module(package="google.cloud.aiplatform.v1", manifest={"Value",},)


class Value(proto.Message):
    r"""Value is the value of the field.
    Attributes:
        int_value (int):
            An integer value.
        double_value (float):
            A double value.
        string_value (str):
            A string value.
    """

    int_value = proto.Field(proto.INT64, number=1, oneof="value",)
    double_value = proto.Field(proto.DOUBLE, number=2, oneof="value",)
    string_value = proto.Field(proto.STRING, number=3, oneof="value",)


__all__ = tuple(sorted(__protobuf__.manifest))
