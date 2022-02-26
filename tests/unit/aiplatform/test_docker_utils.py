# -*- coding: utf-8 -*-

# Copyright 2022 Google LLC
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

import pytest
import textwrap

from google.cloud.aiplatform.docker_utils import errors


class TestErrors:
    def test_raise_docker_error_with_command(self):
        command = ["ls", "-l"]
        return_code = 1
        expected_message = textwrap.dedent(
            """
            Docker failed with error code {return_code}.
            Command: {command}
            """.format(
                return_code=return_code, command=" ".join(command)
            )
        )

        with pytest.raises(errors.DockerError) as exception:
            errors.raise_docker_error_with_command(command, return_code)

        assert exception.value.message == expected_message
        assert exception.value.cmd == command
        assert exception.value.exit_code == return_code
