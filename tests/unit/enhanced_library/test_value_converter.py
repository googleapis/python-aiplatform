# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import absolute_import

from google.cloud.aiplatform.utils.enhanced_library import value_converter
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
import proto


class SomeMessage(proto.Message):
    test_str = proto.Field(proto.STRING, number=1)
    test_int64 = proto.Field(proto.INT64, number=2)
    test_bool = proto.Field(proto.BOOL, number=3)


class SomeInType(proto.Message):
    test_map = proto.MapField(proto.STRING, proto.INT32, number=1)


class SomeOutType(proto.Message):
    test_int = proto.Field(proto.INT32, number=1)


input_dict = {
    "test_str": "Omnia Gallia est divisa",
    "test_int64": 3,
    "test_bool": True,
}
input_value = json_format.ParseDict(input_dict, Value())
input_message = SomeMessage(input_dict)


def test_convert_message_to_value():
    actual_to_value_output = value_converter.to_value(input_message)
    expected_type = Value()
    assert isinstance(expected_type, type(actual_to_value_output))

    actual_inner_fields = actual_to_value_output.struct_value.fields

    actual_bool_type = actual_inner_fields["test_bool"]
    assert hasattr(actual_bool_type, "bool_value")

    actual_int64_type = actual_inner_fields["test_int64"]
    assert hasattr(actual_int64_type, "number_value")

    actual_string_type = actual_inner_fields["test_str"]
    assert hasattr(actual_string_type, "string_value")


def test_convert_value_to_message():
    actual_from_value_output = value_converter.from_value(SomeMessage, input_value)
    expected_type = SomeMessage(input_dict)

    assert actual_from_value_output.__class__.__name__ == SomeMessage.__name__

    # Check property-level ("duck-typing") equivalency
    assert actual_from_value_output.test_str == expected_type.test_str
    assert actual_from_value_output.test_bool == expected_type.test_bool
    assert actual_from_value_output.test_int64 == expected_type.test_int64


def test_convert_map_to_message():
    message_with_map = SomeInType()
    message_with_map.test_map["test_int"] = 42
    map_composite = message_with_map.test_map
    actual_output = value_converter.from_map(SomeOutType, map_composite)

    assert actual_output.__class__.__name__ == SomeOutType.__name__

    # Check property-to-key/value equivalency
    assert actual_output.test_int == map_composite["test_int"]
