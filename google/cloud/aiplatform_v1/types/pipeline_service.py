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

from google.cloud.aiplatform_v1.types import training_pipeline as gca_training_pipeline
from google.protobuf import field_mask_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1",
    manifest={
        "CreateTrainingPipelineRequest",
        "GetTrainingPipelineRequest",
        "ListTrainingPipelinesRequest",
        "ListTrainingPipelinesResponse",
        "DeleteTrainingPipelineRequest",
        "CancelTrainingPipelineRequest",
    },
)


class CreateTrainingPipelineRequest(proto.Message):
    r"""Request message for
    [PipelineService.CreateTrainingPipeline][google.cloud.aiplatform.v1.PipelineService.CreateTrainingPipeline].

    Attributes:
        parent (str):
            Required. The resource name of the Location to create the
            TrainingPipeline in. Format:
            ``projects/{project}/locations/{location}``
        training_pipeline (google.cloud.aiplatform_v1.types.TrainingPipeline):
            Required. The TrainingPipeline to create.
    """

    parent = proto.Field(proto.STRING, number=1,)
    training_pipeline = proto.Field(
        proto.MESSAGE, number=2, message=gca_training_pipeline.TrainingPipeline,
    )


class GetTrainingPipelineRequest(proto.Message):
    r"""Request message for
    [PipelineService.GetTrainingPipeline][google.cloud.aiplatform.v1.PipelineService.GetTrainingPipeline].

    Attributes:
        name (str):
            Required. The name of the TrainingPipeline resource. Format:
            ``projects/{project}/locations/{location}/trainingPipelines/{training_pipeline}``
    """

    name = proto.Field(proto.STRING, number=1,)


class ListTrainingPipelinesRequest(proto.Message):
    r"""Request message for
    [PipelineService.ListTrainingPipelines][google.cloud.aiplatform.v1.PipelineService.ListTrainingPipelines].

    Attributes:
        parent (str):
            Required. The resource name of the Location to list the
            TrainingPipelines from. Format:
            ``projects/{project}/locations/{location}``
        filter (str):
            The standard list filter. Supported fields:

            -  ``display_name`` supports = and !=.

            -  ``state`` supports = and !=.

            Some examples of using the filter are:

            -  ``state="PIPELINE_STATE_SUCCEEDED" AND display_name="my_pipeline"``

            -  ``state="PIPELINE_STATE_RUNNING" OR display_name="my_pipeline"``

            -  ``NOT display_name="my_pipeline"``

            -  ``state="PIPELINE_STATE_FAILED"``
        page_size (int):
            The standard list page size.
        page_token (str):
            The standard list page token. Typically obtained via
            [ListTrainingPipelinesResponse.next_page_token][google.cloud.aiplatform.v1.ListTrainingPipelinesResponse.next_page_token]
            of the previous
            [PipelineService.ListTrainingPipelines][google.cloud.aiplatform.v1.PipelineService.ListTrainingPipelines]
            call.
        read_mask (google.protobuf.field_mask_pb2.FieldMask):
            Mask specifying which fields to read.
    """

    parent = proto.Field(proto.STRING, number=1,)
    filter = proto.Field(proto.STRING, number=2,)
    page_size = proto.Field(proto.INT32, number=3,)
    page_token = proto.Field(proto.STRING, number=4,)
    read_mask = proto.Field(proto.MESSAGE, number=5, message=field_mask_pb2.FieldMask,)


class ListTrainingPipelinesResponse(proto.Message):
    r"""Response message for
    [PipelineService.ListTrainingPipelines][google.cloud.aiplatform.v1.PipelineService.ListTrainingPipelines]

    Attributes:
        training_pipelines (Sequence[google.cloud.aiplatform_v1.types.TrainingPipeline]):
            List of TrainingPipelines in the requested
            page.
        next_page_token (str):
            A token to retrieve the next page of results. Pass to
            [ListTrainingPipelinesRequest.page_token][google.cloud.aiplatform.v1.ListTrainingPipelinesRequest.page_token]
            to obtain that page.
    """

    @property
    def raw_page(self):
        return self

    training_pipelines = proto.RepeatedField(
        proto.MESSAGE, number=1, message=gca_training_pipeline.TrainingPipeline,
    )
    next_page_token = proto.Field(proto.STRING, number=2,)


class DeleteTrainingPipelineRequest(proto.Message):
    r"""Request message for
    [PipelineService.DeleteTrainingPipeline][google.cloud.aiplatform.v1.PipelineService.DeleteTrainingPipeline].

    Attributes:
        name (str):
            Required. The name of the TrainingPipeline resource to be
            deleted. Format:
            ``projects/{project}/locations/{location}/trainingPipelines/{training_pipeline}``
    """

    name = proto.Field(proto.STRING, number=1,)


class CancelTrainingPipelineRequest(proto.Message):
    r"""Request message for
    [PipelineService.CancelTrainingPipeline][google.cloud.aiplatform.v1.PipelineService.CancelTrainingPipeline].

    Attributes:
        name (str):
            Required. The name of the TrainingPipeline to cancel.
            Format:
            ``projects/{project}/locations/{location}/trainingPipelines/{training_pipeline}``
    """

    name = proto.Field(proto.STRING, number=1,)


__all__ = tuple(sorted(__protobuf__.manifest))
