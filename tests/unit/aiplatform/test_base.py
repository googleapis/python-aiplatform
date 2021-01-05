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

from importlib import reload
import pytest
import time
from typing import Optional

from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer


class _TestClass(base.FutureManager):
    def __init__(self, x):
        self.x = x
        super().__init__()

    @classmethod
    def _empty_constructor(cls):
        self = cls.__new__(cls)
        base.FutureManager.__init__(self)
        self.x = None
        return self

    def _sync_object_with_future_result(self, result):
        self.x = result.x

    @classmethod
    @base.optional_sync()
    def create(cls, x: int, sync=True) -> "_TestClass":
        time.sleep(1)
        return cls(x)

    @base.optional_sync()
    def add(self, a: "_TestClass", sync=True) -> None:
        time.sleep(1)
        return self._add(a=a, sync=sync)

    def _add(self, a: "_TestClass", sync=True) -> None:
        self.x = self.x + a.x


class _TestClassDownStream(_TestClass):
    @base.optional_sync(construct_object_on_arg="a")
    def add_and_create_new(
        self, a: Optional["_TestClass"] = None, sync=True
    ) -> _TestClass:
        time.sleep(1)
        if a:
            return _TestClass(self.x + a.x)
        return None

    @base.optional_sync(return_input_arg="a", bind_future_to_self=False)
    def add_to_input_arg(self, a: "_TestClass", sync=True) -> _TestClass:
        time.sleep(1)
        a._add(self)
        return a


class TestFutureManager:
    def setup_method(self):
        reload(initializer)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @pytest.mark.parametrize("sync", [True, False])
    def test_create_task(self, sync):
        a = _TestClass.create(10, sync=sync)
        if not sync:
            assert a.x is None
            assert a._latest_future is not None
            a.wait()
        assert a._latest_future is None
        assert a.x == 10
        assert isinstance(a, _TestClass)

    @pytest.mark.parametrize("sync", [True, False])
    def test_create_and_add_task(self, sync):
        _latest_future = None

        a = _TestClass.create(10, sync=sync)
        b = _TestClass.create(7, sync=sync)
        if not sync:
            assert a.x is None
            assert a._latest_future is not None
            assert b.x is None
            assert b._latest_future is not None
            _latest_future = b._latest_future

        b.add(a, sync=sync)

        if not sync:
            assert b._latest_future is not _latest_future
            b.wait()

        assert a._latest_future is None
        assert a.x == 10
        assert b._latest_future is None
        assert b.x == 17
        assert isinstance(a, _TestClass)
        assert isinstance(b, _TestClass)

    @pytest.mark.parametrize("sync", [True, False])
    def test_create_and_add_and_create_new_task(self, sync):
        _latest_future = None

        a = _TestClass.create(10, sync=sync)
        b = _TestClassDownStream.create(7, sync=sync)
        if not sync:
            assert a.x is None
            assert a._latest_future is not None
            assert b.x is None
            assert b._latest_future is not None
            _latest_future = b._latest_future

        c = b.add_and_create_new(a, sync=sync)

        if not sync:
            assert b._latest_future is not _latest_future
            assert c.x is None
            assert c._latest_future is not None
            c.wait()

        assert a._latest_future is None
        assert a.x == 10
        assert b._latest_future is None
        assert b.x == 7
        assert c._latest_future is None
        assert c.x == 17
        assert isinstance(a, _TestClass)
        assert isinstance(b, _TestClassDownStream)
        assert isinstance(c, _TestClass)

    @pytest.mark.parametrize("sync", [True, False])
    def test_create_and_add_and_not_create_new_task(self, sync):
        _latest_future = None

        b = _TestClassDownStream.create(7, sync=sync)
        if not sync:
            assert b.x is None
            assert b._latest_future is not None
            _latest_future = b._latest_future

        c = b.add_and_create_new(None, sync=sync)

        if not sync:
            assert b._latest_future is not _latest_future
            b.wait()

        assert c is None

        assert b._latest_future is None
        assert b.x == 7
        assert isinstance(b, _TestClassDownStream)

    @pytest.mark.parametrize("sync", [True, False])
    def test_create_and_add_return_arg(self, sync):
        _latest_future = None

        a = _TestClass.create(10, sync=sync)
        b = _TestClassDownStream.create(7, sync=sync)
        if not sync:
            assert a.x is None
            assert a._latest_future is not None
            assert b.x is None
            assert b._latest_future is not None
            _latest_future = b._latest_future

        c = b.add_to_input_arg(a, sync=sync)

        if not sync:
            assert b._latest_future is _latest_future
            assert c.x is None
            assert c._latest_future is not None
            assert c is a
            c.wait()

        assert a._latest_future is None
        assert a.x == 17
        assert b._latest_future is None
        assert b.x == 7
        assert c._latest_future is None
        assert c.x == 17
        assert isinstance(a, _TestClass)
        assert isinstance(b, _TestClassDownStream)
        assert isinstance(c, _TestClass)
