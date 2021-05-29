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


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1.schema.trainingjob.definition",
    manifest={
        "AutoMlImageSegmentation",
        "AutoMlImageSegmentationInputs",
        "AutoMlImageSegmentationMetadata",
    },
)


class AutoMlImageSegmentation(proto.Message):
    r"""A TrainingJob that trains and uploads an AutoML Image
    Segmentation Model.

    Attributes:
        inputs (google.cloud.aiplatform.v1beta1.schema.trainingjob.definition_v1beta1.types.AutoMlImageSegmentationInputs):
            The input parameters of this TrainingJob.
        metadata (google.cloud.aiplatform.v1beta1.schema.trainingjob.definition_v1beta1.types.AutoMlImageSegmentationMetadata):
            The metadata information.
    """

    inputs = proto.Field(
        proto.MESSAGE, number=1, message="AutoMlImageSegmentationInputs",
    )
    metadata = proto.Field(
        proto.MESSAGE, number=2, message="AutoMlImageSegmentationMetadata",
    )


class AutoMlImageSegmentationInputs(proto.Message):
    r"""
    Attributes:
        model_type (google.cloud.aiplatform.v1beta1.schema.trainingjob.definition_v1beta1.types.AutoMlImageSegmentationInputs.ModelType):

        budget_milli_node_hours (int):
            The training budget of creating this model, expressed in
            milli node hours i.e. 1,000 value in this field means 1 node
            hour. The actual metadata.costMilliNodeHours will be equal
            or less than this value. If further model training ceases to
            provide any improvements, it will stop without using the
            full budget and the metadata.successfulStopReason will be
            ``model-converged``. Note, node_hour = actual_hour \*
            number_of_nodes_involved. Or actaul_wall_clock_hours =
            train_budget_milli_node_hours / (number_of_nodes_involved \*
            1000) For modelType ``cloud-high-accuracy-1``\ (default),
            the budget must be between 20,000 and 2,000,000 milli node
            hours, inclusive. The default value is 192,000 which
            represents one day in wall time (1000 milli \* 24 hours \* 8
            nodes).
        base_model_id (str):
            The ID of the ``base`` model. If it is specified, the new
            model will be trained based on the ``base`` model.
            Otherwise, the new model will be trained from scratch. The
            ``base`` model must be in the same Project and Location as
            the new Model to train, and have the same modelType.
    """

    class ModelType(proto.Enum):
        r""""""
        MODEL_TYPE_UNSPECIFIED = 0
        CLOUD_HIGH_ACCURACY_1 = 1
        CLOUD_LOW_ACCURACY_1 = 2
        MOBILE_TF_LOW_LATENCY_1 = 3

    model_type = proto.Field(proto.ENUM, number=1, enum=ModelType,)
    budget_milli_node_hours = proto.Field(proto.INT64, number=2,)
    base_model_id = proto.Field(proto.STRING, number=3,)


class AutoMlImageSegmentationMetadata(proto.Message):
    r"""
    Attributes:
        cost_milli_node_hours (int):
            The actual training cost of creating this
            model, expressed in milli node hours, i.e. 1,000
            value in this field means 1 node hour.
            Guaranteed to not exceed
            inputs.budgetMilliNodeHours.
        successful_stop_reason (google.cloud.aiplatform.v1beta1.schema.trainingjob.definition_v1beta1.types.AutoMlImageSegmentationMetadata.SuccessfulStopReason):
            For successful job completions, this is the
            reason why the job has finished.
    """

    class SuccessfulStopReason(proto.Enum):
        r""""""
        SUCCESSFUL_STOP_REASON_UNSPECIFIED = 0
        BUDGET_REACHED = 1
        MODEL_CONVERGED = 2

    cost_milli_node_hours = proto.Field(proto.INT64, number=1,)
    successful_stop_reason = proto.Field(
        proto.ENUM, number=2, enum=SuccessfulStopReason,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
