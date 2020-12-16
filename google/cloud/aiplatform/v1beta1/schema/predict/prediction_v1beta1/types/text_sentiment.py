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

import proto  # type: ignore

# DO NOT OVERWRITE FOLLOWING LINE: it was manually edited.
from google.cloud.aiplatform.v1beta1.schema.predict.instance import (
    TextSentimentPredictionInstance,
)


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1.schema.predict.prediction",
    manifest={"TextSentimentPredictionResult",},
)


class TextSentimentPredictionResult(proto.Message):
    r"""Represents a line of JSONL in the text sentiment batch
    prediction output file. This is a hack to allow printing of
    integer values.

    Attributes:
        instance (~.gcaspi_text_sentiment.TextSentimentPredictionInstance):
            User's input instance.
        prediction (~.gcaspp_text_sentiment.TextSentimentPredictionResult.Prediction):
            The prediction result.
    """

    class Prediction(proto.Message):
        r"""Prediction output format for Text Sentiment.

        Attributes:
            sentiment (int):
                The integer sentiment labels between 0
                (inclusive) and sentimentMax label (inclusive),
                while 0 maps to the least positive sentiment and
                sentimentMax maps to the most positive one. The
                higher the score is, the more positive the
                sentiment in the text snippet is. Note:
                sentimentMax is an integer value between 1
                (inclusive) and 10 (inclusive).
        """

        sentiment = proto.Field(proto.INT32, number=1)

    instance = proto.Field(
        proto.MESSAGE, number=1, message=TextSentimentPredictionInstance,
    )

    prediction = proto.Field(proto.MESSAGE, number=2, message=Prediction,)


__all__ = tuple(sorted(__protobuf__.manifest))
