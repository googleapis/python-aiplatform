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
"""Unit tests for generative model tuning."""
# pylint: disable=protected-access,bad-continuation,g-import-not-at-top,reimported

import sys
from unittest import mock

import pytest


def test_vertexai_has_lazy_preview():
    """Tests that `vertexai.preview` works but uis lazy-loaded."""
    # * Cleaning up the `vertexai` module state.
    # Important: If we run this test after some other tests that import the
    # `vertexai.preview` module, then Python's importing mechanism adds the
    # imported module to the `vertexai` as the `preview` attribute,
    # and this prevents the `__getattr__` from being called.
    # So to test that `__getattr__` is actually called, we must delete that
    # attribute (which might or might not exist). Note that using `hasattr`
    # triggers `__getattr__`.
    # Removing the `vertexai.preview` attribute.
    import vertexai as vertexai1

    try:
        delattr(vertexai1, "preview")
    except AttributeError:
        pass

    main_module_name = vertexai1.__name__  # == "vertexai"
    preview_module_name = main_module_name + ".preview"
    del vertexai1

    with mock.patch.dict(sys.modules):
        # First we must remove the cached modules.
        # Otherwise, importing a module is a no-op.
        # https://docs.python.org/3/reference/import.html#the-module-cache
        # Removal is harder due to Copybara transforms.
        # Note that we must delete the entries, not set them to None.
        try:
            del sys.modules[main_module_name]
        except KeyError:
            pass
        try:
            del sys.modules[preview_module_name]
        except KeyError:
            pass

        # * Verifying that importing `vertexai` does not import the `preview` module.
        import vertexai

        assert preview_module_name not in sys.modules

        # * Also verifying that the `preview` attribute does not exist on the module,
        # because if the attribute exists, then accessing `preview` will
        # skip `__getattr__` (and importing).
        # Important: We cannot use `hasattr` to check whether the `preview`
        # attribute exist since that triggers `__getattr__` which creates the attribute.
        # We should use `object.__getattribute__` for checking instead.
        with pytest.raises(AttributeError):
            object.__getattribute__(vertexai, "preview")

        # * Verifying that it's still possible to access `vertexai.preview`
        assert dir(vertexai.preview)

        # * Verifying that accessing `vertexai.preview` caused the module to be loaded.
        assert preview_module_name in sys.modules
