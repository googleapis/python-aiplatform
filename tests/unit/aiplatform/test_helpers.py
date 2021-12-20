# -*- coding: utf-8 -*-

# Copyright 2021 Google LLC
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

import importlib
import pytest

from typing import Sequence

from google.cloud import aiplatform
from google.cloud.aiplatform import helpers
from google.cloud.aiplatform import initializer


class TestContainerUriHelpers:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def _build_predict_uri_kwargs(self, args: Sequence[str]) -> dict:
        """
        Takes list of values for all method parameters and return dict of kwargs,
        dropping keywords that were set as None.
        """
        func = helpers.get_prebuilt_prediction_container_uri
        arg_names = func.__code__.co_varnames[: func.__code__.co_argcount]
        return {k: v for k, v in dict(zip(arg_names, args)).items() if v is not None}

    @pytest.mark.parametrize(
        "args, expected_uri",
        [
            (
                ("tensorflow", "2.6", None, None),
                "us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-6:latest",
            ),
            (
                ("tensorflow", "1.15", "europe-west4", None),
                "europe-docker.pkg.dev/vertex-ai/prediction/tf-cpu.1-15:latest",
            ),
            (
                ("tensorflow", "2.2", None, "gpu"),
                "us-docker.pkg.dev/vertex-ai/prediction/tf2-gpu.2-2:latest",
            ),
            (
                ("sklearn", "0.24", "asia", "cpu"),
                "asia-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.0-24:latest",
            ),
            (
                ("sklearn", "0.20", None, None),
                "us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.0-20:latest",
            ),
            (
                ("xgboost", "1.3", None, None),
                "us-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.1-3:latest",
            ),
            (
                ("xgboost", "0.90", "europe", None),
                "europe-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.0-90:latest",
            ),
        ],
    )
    def test_correct_prediction_uri_args(self, args, expected_uri):
        uri = helpers.get_prebuilt_prediction_container_uri(
            **self._build_predict_uri_kwargs(args)
        )

        assert uri == expected_uri

    def test_correct_prediction_uri_args_with_init_location(self):
        """
        Ensure that aiplatform.init location is used when region
        is not provided
        """
        uri = aiplatform.helpers.get_prebuilt_prediction_container_uri(
            "tensorflow", "2.6"
        )
        # SDK default location is us-central1
        assert uri.startswith("us-docker.pkg.dev")

        aiplatform.init(location="asia-northeast3")
        uri = aiplatform.helpers.get_prebuilt_prediction_container_uri(
            "tensorflow", "2.6"
        )
        assert uri.startswith("asia-docker.pkg.dev")

        aiplatform.init(location="europe-west2")
        uri = aiplatform.helpers.get_prebuilt_prediction_container_uri(
            "xgboost", "0.90"
        )
        assert uri.startswith("europe-docker.pkg.dev")

    @pytest.mark.parametrize(
        "args, expected_error_msg",
        [
            (
                ("pytorch", "1.10", None, None),
                "No containers found for framework `pytorch`. Supported frameworks are",
            ),
            (
                ("tensorflow", "9.15", None, None),
                (
                    "No serving container for `tensorflow` version `9.15` with accelerator "
                    "`cpu` found. Supported versions include"
                ),
            ),
            (
                # Make sure region error supercedes version error
                ("tensorflow", "9.15", "pluto", None),
                "Unsupported container region `pluto`, supported regions are ",
            ),
            (
                ("tensorflow", "2.2", "narnia", None),
                "Unsupported container region `narnia`, supported regions are ",
            ),
            (
                ("sklearn", "0.24", "asia", "gpu"),
                "sklearn containers do not support `gpu` accelerator. Supported accelerators are cpu.",
            ),
            (
                # Make sure framework error supercedes accelerator error
                ("onnx", "1.9", None, "gpu"),
                "No containers found for framework `onnx`. Supported frameworks are",
            ),
        ],
    )
    def test_invalid_prediction_uri_args(self, args, expected_error_msg):

        with pytest.raises(ValueError) as err:
            helpers.get_prebuilt_prediction_container_uri(
                **self._build_predict_uri_kwargs(args)
            )

        assert err.match(expected_error_msg)
