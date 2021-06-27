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

from google.cloud.aiplatform_v1beta1.types import pipeline_job as gca_pipeline_job
from google.cloud.aiplatform_v1beta1.types import (
    training_pipeline as gca_training_pipeline,
)
from google.protobuf import field_mask_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "CreateTrainingPipelineRequest",
        "GetTrainingPipelineRequest",
        "ListTrainingPipelinesRequest",
        "ListTrainingPipelinesResponse",
        "DeleteTrainingPipelineRequest",
        "CancelTrainingPipelineRequest",
        "CreatePipelineJobRequest",
        "GetPipelineJobRequest",
        "ListPipelineJobsRequest",
        "ListPipelineJobsResponse",
        "DeletePipelineJobRequest",
        "CancelPipelineJobRequest",
    },
)


class CreateTrainingPipelineRequest(proto.Message):
    r"""Request message for
    [PipelineService.CreateTrainingPipeline][google.cloud.aiplatform.v1beta1.PipelineService.CreateTrainingPipeline].

    Attributes:
        parent (str):
            Required. The resource name of the Location to create the
            TrainingPipeline in. Format:
            ``projects/{project}/locations/{location}``
        training_pipeline (google.cloud.aiplatform_v1beta1.types.TrainingPipeline):
            Required. The TrainingPipeline to create.
    """

    parent = proto.Field(proto.STRING, number=1,)
    training_pipeline = proto.Field(
        proto.MESSAGE, number=2, message=gca_training_pipeline.TrainingPipeline,
    )


class GetTrainingPipelineRequest(proto.Message):
    r"""Request message for
    [PipelineService.GetTrainingPipeline][google.cloud.aiplatform.v1beta1.PipelineService.GetTrainingPipeline].

    Attributes:
        name (str):
            Required. The name of the TrainingPipeline resource. Format:
            ``projects/{project}/locations/{location}/trainingPipelines/{training_pipeline}``
    """

    name = proto.Field(proto.STRING, number=1,)


class ListTrainingPipelinesRequest(proto.Message):
    r"""Request message for
    [PipelineService.ListTrainingPipelines][google.cloud.aiplatform.v1beta1.PipelineService.ListTrainingPipelines].

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
            [ListTrainingPipelinesResponse.next_page_token][google.cloud.aiplatform.v1beta1.ListTrainingPipelinesResponse.next_page_token]
            of the previous
            [PipelineService.ListTrainingPipelines][google.cloud.aiplatform.v1beta1.PipelineService.ListTrainingPipelines]
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
    [PipelineService.ListTrainingPipelines][google.cloud.aiplatform.v1beta1.PipelineService.ListTrainingPipelines]

    Attributes:
        training_pipelines (Sequence[google.cloud.aiplatform_v1beta1.types.TrainingPipeline]):
            List of TrainingPipelines in the requested
            page.
        next_page_token (str):
            A token to retrieve the next page of results. Pass to
            [ListTrainingPipelinesRequest.page_token][google.cloud.aiplatform.v1beta1.ListTrainingPipelinesRequest.page_token]
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
    [PipelineService.DeleteTrainingPipeline][google.cloud.aiplatform.v1beta1.PipelineService.DeleteTrainingPipeline].

    Attributes:
        name (str):
            Required. The name of the TrainingPipeline resource to be
            deleted. Format:
            ``projects/{project}/locations/{location}/trainingPipelines/{training_pipeline}``
    """

    name = proto.Field(proto.STRING, number=1,)


class CancelTrainingPipelineRequest(proto.Message):
    r"""Request message for
    [PipelineService.CancelTrainingPipeline][google.cloud.aiplatform.v1beta1.PipelineService.CancelTrainingPipeline].

    Attributes:
        name (str):
            Required. The name of the TrainingPipeline to cancel.
            Format:
            ``projects/{project}/locations/{location}/trainingPipelines/{training_pipeline}``
    """

    name = proto.Field(proto.STRING, number=1,)


class CreatePipelineJobRequest(proto.Message):
    r"""Request message for
    [PipelineService.CreatePipelineJob][google.cloud.aiplatform.v1beta1.PipelineService.CreatePipelineJob].

    Attributes:
        parent (str):
            Required. The resource name of the Location to create the
            PipelineJob in. Format:
            ``projects/{project}/locations/{location}``
        pipeline_job (google.cloud.aiplatform_v1beta1.types.PipelineJob):
            Required. The PipelineJob to create.
        pipeline_job_id (str):
            The ID to use for the PipelineJob, which will become the
            final component of the PipelineJob name. If not provided, an
            ID will be automatically generated.

            This value should be less than 128 characters, and valid
            characters are /[a-z][0-9]-/.
    """

    parent = proto.Field(proto.STRING, number=1,)
    pipeline_job = proto.Field(
        proto.MESSAGE, number=2, message=gca_pipeline_job.PipelineJob,
    )
    pipeline_job_id = proto.Field(proto.STRING, number=3,)


class GetPipelineJobRequest(proto.Message):
    r"""Request message for
    [PipelineService.GetPipelineJob][google.cloud.aiplatform.v1beta1.PipelineService.GetPipelineJob].

    Attributes:
        name (str):
            Required. The name of the PipelineJob resource. Format:
            ``projects/{project}/locations/{location}/pipelineJobs/{pipeline_job}``
    """

    name = proto.Field(proto.STRING, number=1,)


class ListPipelineJobsRequest(proto.Message):
    r"""Request message for
    [PipelineService.ListPipelineJobs][google.cloud.aiplatform.v1beta1.PipelineService.ListPipelineJobs].

    Attributes:
        parent (str):
            Required. The resource name of the Location to list the
            PipelineJobs from. Format:
            ``projects/{project}/locations/{location}``
        filter (str):
            The standard list filter. Supported fields:

            -  ``display_name`` supports ``=`` and ``!=``.
            -  ``state`` supports ``=`` and ``!=``.

            The following examples demonstrate how to filter the list of
            PipelineJobs:

            -  ``state="PIPELINE_STATE_SUCCEEDED" AND display_name="my_pipeline"``
            -  ``state="PIPELINE_STATE_RUNNING" OR display_name="my_pipeline"``
            -  ``NOT display_name="my_pipeline"``
            -  ``state="PIPELINE_STATE_FAILED"``
        page_size (int):
            The standard list page size.
        page_token (str):
            The standard list page token. Typically obtained via
            [ListPipelineJobsResponse.next_page_token][google.cloud.aiplatform.v1beta1.ListPipelineJobsResponse.next_page_token]
            of the previous
            [PipelineService.ListPipelineJobs][google.cloud.aiplatform.v1beta1.PipelineService.ListPipelineJobs]
            call.
    """

    parent = proto.Field(proto.STRING, number=1,)
    filter = proto.Field(proto.STRING, number=2,)
    page_size = proto.Field(proto.INT32, number=3,)
    page_token = proto.Field(proto.STRING, number=4,)


class ListPipelineJobsResponse(proto.Message):
    r"""Response message for
    [PipelineService.ListPipelineJobs][google.cloud.aiplatform.v1beta1.PipelineService.ListPipelineJobs]

    Attributes:
        pipeline_jobs (Sequence[google.cloud.aiplatform_v1beta1.types.PipelineJob]):
            List of PipelineJobs in the requested page.
        next_page_token (str):
            A token to retrieve the next page of results. Pass to
            [ListPipelineJobsRequest.page_token][google.cloud.aiplatform.v1beta1.ListPipelineJobsRequest.page_token]
            to obtain that page.
    """

    @property
    def raw_page(self):
        return self

    pipeline_jobs = proto.RepeatedField(
        proto.MESSAGE, number=1, message=gca_pipeline_job.PipelineJob,
    )
    next_page_token = proto.Field(proto.STRING, number=2,)


class DeletePipelineJobRequest(proto.Message):
    r"""Request message for
    [PipelineService.DeletePipelineJob][google.cloud.aiplatform.v1beta1.PipelineService.DeletePipelineJob].

    Attributes:
        name (str):
            Required. The name of the PipelineJob resource to be
            deleted. Format:
            ``projects/{project}/locations/{location}/pipelineJobs/{pipeline_job}``
    """

    name = proto.Field(proto.STRING, number=1,)


class CancelPipelineJobRequest(proto.Message):
    r"""Request message for
    [PipelineService.CancelPipelineJob][google.cloud.aiplatform.v1beta1.PipelineService.CancelPipelineJob].

    Attributes:
        name (str):
            Required. The name of the PipelineJob to cancel. Format:
            ``projects/{project}/locations/{location}/pipelineJobs/{pipeline_job}``
    """

    name = proto.Field(proto.STRING, number=1,)


__all__ = tuple(sorted(__protobuf__.manifest))
