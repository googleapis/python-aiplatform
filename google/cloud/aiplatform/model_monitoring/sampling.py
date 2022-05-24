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

import abc
from typing import Optional
from google.cloud.aiplatform.compat.types import model_monitoring as gca_model_monitoring

class _SamplingStrategy(abc.ABC):
    """An abstract class for setting sampling strategy for model monitoring"""

class RandomSampleConfig(_SamplingStrategy):
    def __init__(
        self, 
        sample_rate: Optional[float] = None
    ):
        """Initializer for RandomSampleConfig

            Args:
            sample_rate (float):
                Optional. Sets the sampling rate for model monitoring logs.
                If not set, all logs are processed.
            Returns:
                An instance of RandomSampleConfig
        """
        super().__init()
        self.sample_rate = sample_rate

    def as_proto(self):
        return gca_model_monitoring.SamplingStrategy(
            random_sample_config = gca_model_monitoring.SamplingStrategy.RandomSampleConfig(
                sample_rate = self.sample_rate
            )
        )
