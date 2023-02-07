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

from google.cloud.aiplatform import base
import logging
import pytest
import sys


class TestLogging:
    @pytest.mark.skipif(
        sys.version_info < (3, 8),
        reason="requires python3.8 or higher to work with MLFlow",
    )
    def test_no_root_logging_handler_override(self, caplog):
        # Users should be able to control the root logger in their apps
        # The aiplatform module import should not override their root logger config
        caplog.set_level(logging.DEBUG)

        logging.debug("Debug level")
        logging.info("Info level")
        logging.critical("Critical level")

        assert "Debug level\n" in caplog.text
        assert "Info level\n" in caplog.text
        assert "Critical level\n" in caplog.text

    @pytest.mark.skipif(
        sys.version_info < (3, 8),
        reason="requires python3.8 or higher to work with MLFlow",
    )
    def test_log_level_coexistance(self, caplog):
        # The aiplatform module and the root logger can have different log levels.
        aip_logger = base.Logger(__name__)

        caplog.set_level(logging.DEBUG)

        logging.debug("This should exist")
        logging.info("This should too")

        aip_logger.info("This should also exist")
        aip_logger.debug("This should NOT exist")

        assert "This should exist\n" in caplog.text
        assert "This should too\n" in caplog.text
        assert "This should also exist\n" in caplog.text
        assert "This should NOT exist\n" not in caplog.text
