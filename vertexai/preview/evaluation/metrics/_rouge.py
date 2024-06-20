# -*- coding: utf-8 -*-

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
from typing import Literal
from vertexai.preview.evaluation import constants
from vertexai.preview.evaluation.metrics import _base


class Rouge(_base._AutomaticMetric):
    """The ROUGE Metric.

    Calculates the recall of n-grams in prediction as compared to reference and
    returns a score ranging between 0 and 1. Supported rouge types are
    rougen[1-9], rougeL, and rougeLsum.
    """

    _metric_name = constants.Metric.ROUGE

    def __init__(
        self,
        *,
        rouge_type: Literal[
            "rouge1",
            "rouge2",
            "rouge3",
            "rouge4",
            "rouge5",
            "rouge6",
            "rouge7",
            "rouge8",
            "rouge9",
            "rougeL",
            "rougeLsum",
        ],
        use_stemmer: bool = False,
        split_summaries: bool = False
    ):
        super().__init__(
            metric=Rouge._metric_name,
            rouge_type=rouge_type,
            use_stemmer=use_stemmer,
            split_summaries=split_summaries,
        )
