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
"""Evaluation Metrics Module."""

from vertexai.preview.evaluation.metrics import _base
from vertexai.preview.evaluation.metrics import _coherence
from vertexai.preview.evaluation.metrics import _fluency
from vertexai.preview.evaluation.metrics import _fulfillment
from vertexai.preview.evaluation.metrics import _groundedness
from vertexai.preview.evaluation.metrics import (
    _pairwise_question_answering_quality,
)
from vertexai.preview.evaluation.metrics import (
    _pairwise_summarization_quality,
)
from vertexai.preview.evaluation.metrics import (
    _question_answering_correctness,
)
from vertexai.preview.evaluation.metrics import (
    _question_answering_helpfulness,
)
from vertexai.preview.evaluation.metrics import (
    _question_answering_quality,
)
from vertexai.preview.evaluation.metrics import (
    _question_answering_relevance,
)
from vertexai.preview.evaluation.metrics import _safety
from vertexai.preview.evaluation.metrics import (
    _summarization_helpfulness,
)
from vertexai.preview.evaluation.metrics import (
    _summarization_quality,
)
from vertexai.preview.evaluation.metrics import (
    _summarization_verbosity,
)
from vertexai.preview.evaluation.metrics import (
    _rouge,
)


CustomMetric = _base.CustomMetric
PairwiseMetric = _base.PairwiseMetric
make_metric = _base.make_metric

Rouge = _rouge.Rouge
Coherence = _coherence.Coherence
Fluency = _fluency.Fluency
Safety = _safety.Safety
Groundedness = _groundedness.Groundedness
Fulfillment = _fulfillment.Fulfillment
SummarizationQuality = _summarization_quality.SummarizationQuality
SummarizationHelpfulness = _summarization_helpfulness.SummarizationHelpfulness
SummarizationVerbosity = _summarization_verbosity.SummarizationVerbosity
QuestionAnsweringQuality = _question_answering_quality.QuestionAnsweringQuality
QuestionAnsweringRelevance = _question_answering_relevance.QuestionAnsweringRelevance
QuestionAnsweringHelpfulness = (
    _question_answering_helpfulness.QuestionAnsweringHelpfulness
)
QuestionAnsweringCorrectness = (
    _question_answering_correctness.QuestionAnsweringCorrectness
)
PairwiseSummarizationQuality = (
    _pairwise_summarization_quality.PairwiseSummarizationQuality
)
PairwiseQuestionAnsweringQuality = (
    _pairwise_question_answering_quality.PairwiseQuestionAnsweringQuality
)

__all__ = [
    "CustomMetric",
    "PairwiseMetric",
    "make_metric",
    "Rouge",
    "Coherence",
    "Fluency",
    "Safety",
    "Groundedness",
    "Fulfillment",
    "SummarizationQuality",
    "SummarizationHelpfulness",
    "SummarizationVerbosity",
    "QuestionAnsweringQuality",
    "QuestionAnsweringRelevance",
    "QuestionAnsweringHelpfulness",
    "QuestionAnsweringCorrectness",
    "PairwiseSummarizationQuality",
    "PairwiseQuestionAnsweringQuality",
]
