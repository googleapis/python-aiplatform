# -*- coding: utf-8 -*-
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

from vertexai.preview._workflow.serialization_engine import (
    serializers_base,
)


class TestSerializerArgs:
    def test_object_id_is_saved(self):
        class TestClass:
            pass

        test_obj = TestClass()
        serializer_args = serializers_base.SerializerArgs({test_obj: {"a": 1, "b": 2}})
        assert id(test_obj) in serializer_args
        assert test_obj not in serializer_args

    def test_getitem_support_original_object(self):
        class TestClass:
            pass

        test_obj = TestClass()
        serializer_args = serializers_base.SerializerArgs({test_obj: {"a": 1, "b": 2}})
        assert serializer_args[test_obj] == {"a": 1, "b": 2}

    def test_get_support_original_object(self):
        class TestClass:
            pass

        test_obj = TestClass()
        serializer_args = serializers_base.SerializerArgs({test_obj: {"a": 1, "b": 2}})
        assert serializer_args.get(test_obj) == {"a": 1, "b": 2}

    def test_unhashable_obj_saved_successfully(self):
        unhashable = [1, 2, 3]
        serializer_args = serializers_base.SerializerArgs()
        serializer_args[unhashable] = {"a": 1, "b": 2}
        assert id(unhashable) in serializer_args

    def test_getitem_support_original_unhashable(self):
        unhashable = [1, 2, 3]
        serializer_args = serializers_base.SerializerArgs()
        serializer_args[unhashable] = {"a": 1, "b": 2}
        assert serializer_args[unhashable] == {"a": 1, "b": 2}

    def test_get_support_original_unhashable(self):
        unhashable = [1, 2, 3]
        serializers_args = serializers_base.SerializerArgs()
        serializers_args[unhashable] = {"a": 1, "b": 2}
        assert serializers_args.get(unhashable) == {"a": 1, "b": 2}
