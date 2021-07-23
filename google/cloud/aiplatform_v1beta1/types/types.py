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


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={"BoolArray", "DoubleArray", "Int64Array", "StringArray",},
)


class BoolArray(proto.Message):
    r"""A list of boolean values.
    Attributes:
        values (Sequence[bool]):
            A list of bool values.
    """

    values = proto.RepeatedField(proto.BOOL, number=1,)


class DoubleArray(proto.Message):
    r"""A list of double values.
    Attributes:
        values (Sequence[float]):
            A list of bool values.
    """

    values = proto.RepeatedField(proto.DOUBLE, number=1,)


class Int64Array(proto.Message):
    r"""A list of int64 values.
    Attributes:
        values (Sequence[int]):
            A list of int64 values.
    """

    values = proto.RepeatedField(proto.INT64, number=1,)


class StringArray(proto.Message):
    r"""A list of string values.
    Attributes:
        values (Sequence[str]):
            A list of string values.
    """

    values = proto.RepeatedField(proto.STRING, number=1,)


__all__ = tuple(sorted(__protobuf__.manifest))
