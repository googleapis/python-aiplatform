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

import json
import re
from google.auth import credentials as auth_credentials
from google.protobuf import json_format
from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import jobs
from google.cloud.aiplatform import pipeline_jobs
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.preview import models
from typing import Dict, Optional
from google.cloud.aiplatform.compat.types import (
    model_service as gca_model_service_compat,
)

_LOGGER = base.Logger(__name__)


class ModelEvaluation(base.VertexAiResourceNounWithFutureManager):
    client_class = utils.ModelClientWithOverride
    _resource_noun = "evaluations"
    _delete_method = None
    _getter_method = "get_model_evaluation"
    _list_method = "list_model_evaluations"
    _parse_resource_name_method = "parse_model_evaluation_path"
    _format_resource_name_method = "model_evaluation_path"

    @property
    def metrics(self) -> Dict:
        """Gets the evaluation metrics from the Model Evaluation.
        Returns:
            A dict with model metrics created from the Model Evaluation or
            None if the metrics for this evaluation are empty.
        Raises:
            ValueError: If the Model Evaluation doesn't have metrics.
        """
        if self._gca_resource.metrics:
            return self.to_dict()["metrics"]
        raise ValueError(
            "This ModelEvaluation does not have any metrics, this could be because the Evaluation job failed. Check the logs for details."
        )

    @property
    def backing_pipeline_job(self) -> Optional["pipeline_jobs.PipelineJob"]:
        """The managed pipeline for this model evaluation job.
        Returns:
            The PipelineJob resource if this evaluation ran from a managed pipeline or None.
        """
        if (
            "metadata" in self._gca_resource
            and "pipeline_job_resource_name" in self._gca_resource.metadata
        ):
            return aiplatform.PipelineJob.get(
                resource_name=self._gca_resource.metadata["pipeline_job_resource_name"]
            )

    @property
    def batch_prediction_job(self) -> Optional[jobs.BatchPredictionJob]:
        """The batch prediction job used for this evaluation if this ran as a
        Model Evaluation pipeline.
        Returns:
            An instantiated representation of the Batch Prediction Job if it exists.
        """
        if self.backing_pipeline_job is not None:
            for component in self.backing_pipeline_job.task_details:
                for metadata_key in component.execution.metadata:
                    if (
                        metadata_key == "output:gcp_resources"
                        and json.loads(component.execution.metadata[metadata_key])[
                            "resources"
                        ][0]["resourceType"]
                        == "BatchPredictionJob"
                    ):
                        bp_job_resource_uri = json.loads(
                            component.execution.metadata[metadata_key]
                        )["resources"][0]["resourceUri"]
                        bp_job_resource_name = bp_job_resource_uri.split("v1/")[1]
                        bp_resource = aiplatform.BatchPredictionJob(
                            batch_prediction_job_name=bp_job_resource_name
                        )
                        bp_resource._gca_resource = bp_resource._get_gca_resource(
                            resource_name=bp_job_resource_name
                        )
                        return bp_resource

    @property
    def metadata_output_artifact(self) -> Optional["aiplatform.Artifact"]:
        """The MLMD Artifact created by the Model Evaluation pipeline.
        Returns:
            The MLMD Artifact resource if this Model Evaluation was created from a pipeline run.
        """
        if self.backing_pipeline_job is not None:
            for component in self.backing_pipeline_job.task_details:
                for output_name in component.outputs:
                    if output_name == "evaluation_metrics":
                        for artifact in component.outputs[output_name].artifacts:
                            if artifact.display_name == "evaluation_metrics":
                                return aiplatform.Artifact.get(
                                    resource_id=artifact.name
                                )

    def get_model_evaluation_slices(
        self,
    ) -> Optional[Dict]:
        """Returns the metric slices associated with a ModelEvaluation if a
        sliced metrics config was provided when the evaluation was created.
        Example usage:
            my_eval = my_model.get_model_evaluation()
            my_evaluation_slices = my_eval.get_model_evaluation_slices(
                model_evaluation=my_eval
            )
        Args:
            model_evaluation (model_evaluation.ModelEvaluation):
                Required. The ModelEvaluation to get the sliced metrics from.
        Returns:
            Dict:
                If slices were generated on the Model Evaluation, this returns a
                dict where the keys are the names of the slices and the values are
                a dict of the metrics for that slice.
        """
        request = gca_model_service_compat.ListModelEvaluationSlicesRequest(
            parent=self.resource_name
        )
        api_client = self._instantiate_client(
            location=self.location, credentials=self.credentials
        )
        slices = api_client.list_model_evaluation_slices(request=request)
        if slices:
            slices_dict = {"overall": {}}
            for metric_slice in slices:
                slice_dict = json_format.MessageToDict(metric_slice._pb)
                if "slice" in slice_dict and "dimension" in slice_dict["slice"]:
                    if slice_dict["slice"]["dimension"] == "annotationSpec":
                        # When dimension is "annotationSpec", they are not part of the "Sliced Metrics", they are the positive target class labels (that already exist in Vertex).
                        slice_key = str(slice_dict["slice"]["value"])
                        slices_dict["overall"][slice_key] = slice_dict["metrics"]
                    if slice_dict["slice"]["dimension"] == "slice":
                        if "value" in slice_dict["slice"]:
                            slice_key = str(slice_dict["slice"]["value"])
                            slices_dict[slice_key] = slice_dict["metrics"]
                        # range slice
                        elif "sliceSpec" in slice_dict["slice"]:
                            alphanumeric_filter = re.compile("[^a-zA-Z0-9_]")
                            slice_key = str(
                                slice_dict["slice"]["sliceSpec"]["configs"]
                            ).split("{")[1]
                            slice_key = alphanumeric_filter.sub("", slice_key)
                            slices_dict[f"{slice_key}_range"] = slice_dict["metrics"]
            return slices_dict

    def __init__(
        self,
        evaluation_name: str,
        model_id: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves the ModelEvaluation resource and instantiates its representation.

        Args:
            evaluation_name (str):
                Required. A fully-qualified model evaluation resource name or evaluation ID.
                Example: "projects/123/locations/us-central1/models/456/evaluations/789" or
                "789". If passing only the evaluation ID, model_id must be provided.
            model_id (str):
                Optional. The ID of the model to retrieve this evaluation from. If passing
                only the evaluation ID as evaluation_name, model_id must be provided.
            project (str):
                Optional project to retrieve model evaluation from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional location to retrieve model evaluation from. If not set, location
                set in aiplatform.init will be used.
            credentials: Optional[auth_credentials.Credentials]=None,
                Custom credentials to use to retrieve this model evaluation. If not set,
                credentials set in aiplatform.init will be used.
        """

        super().__init__(
            project=project,
            location=location,
            credentials=credentials,
            resource_name=evaluation_name,
        )

        self._gca_resource = self._get_gca_resource(
            resource_name=evaluation_name,
            parent_resource_name_fields={models.Model._resource_noun: model_id}
            if model_id
            else model_id,
        )

    def delete(self):
        raise NotImplementedError(
            "Deleting a model evaluation has not been implemented yet."
        )
