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
from typing import (
    Any,
    Dict,
    Optional,
    List,
    Union,
)

from google.auth import credentials as auth_credentials

from google.cloud import aiplatform
from google.cloud.aiplatform import base, utils, pipeline_jobs
from google.cloud.aiplatform.utils import yaml_utils

from google.cloud.aiplatform.compat.types import (
    pipeline_job as gca_pipeline_job,
    pipeline_state as gca_pipeline_state,
)

import logging

_PIPELINE_COMPLETE_STATES = set(
    [
        gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
        gca_pipeline_state.PipelineState.PIPELINE_STATE_FAILED,
        gca_pipeline_state.PipelineState.PIPELINE_STATE_CANCELLED,
        gca_pipeline_state.PipelineState.PIPELINE_STATE_PAUSED,
    ]
)


class _VertexAiPipelineBasedService(base.VertexAiStatefulResource):
    """Base class for Vertex AI Pipeline based services."""

    client_class = utils.PipelineJobClientWithOverride
    _resource_noun = "pipelineJob"
    _delete_method = "delete_pipeline_job"
    _getter_method = "get_pipeline_job"
    _list_method = "list_pipeline_jobs"
    _parse_resource_name_method = "parse_pipeline_job_path"
    _format_resource_name_method = "pipeline_job_path"

    _valid_done_states = _PIPELINE_COMPLETE_STATES

    @property
    @classmethod
    @abc.abstractmethod
    def _template_ref(self) -> Dict[str, str]:
        """A dictionary of the pipeline template URLs for this servicewhere the key is
        an identifier for that template and the value is the url of that pipeline template.

        For example: {"tabular_classification": "gs://path/to/tabular/pipeline/template.json"}

        """
        pass

    @property
    @classmethod
    @abc.abstractmethod
    def _creation_log_message(self) -> str:
        """A log message to use when the Pipeline-based Service is created, since this class
        supresses logs from PipelineJob creation to avoid duplication.

        For example: 'Created PipelineJob for your Model Evaluation.'

        """
        pass

    # TODO: Consider updating this to return a dict or list in the future to support multiple outputs
    @property
    @abc.abstractmethod
    def _metadata_output_artifact(self) -> Optional[str]:
        """The ML Metadata output artifact resource URI from the completed pipeline run."""
        pass

    @property
    def backing_pipeline_job(self) -> "pipeline_jobs.PipelineJob":
        """The PipelineJob associated with the resource."""
        return pipeline_jobs.PipelineJob.get(resource_name=self.resource_name)

    @property
    def pipeline_console_uri(self) -> Optional[str]:
        """The console URI of the PipelineJob created by the service."""
        if self.backing_pipeline_job:
            return self.backing_pipeline_job._dashboard_uri()

    @property
    def state(self) -> Optional[gca_pipeline_state.PipelineState]:
        """The state of the Pipeline run associated with the service."""
        if self.backing_pipeline_job:
            return self.backing_pipeline_job.state
        return None

    # TODO: expose _template_ref in error message when artifact registry support is added
    def _validate_pipeline_template_matches_service(
        self, pipeline_job: "pipeline_jobs.PipelineJob"
    ):
        """Utility function to validate that the passed in pipeline matches
        the template of the Pipeline Based Service.

        Args:
            pipeline_job (aiplatform.PipelineJob):
                Required. The PipelineJob to validate with this Pipeline Based Service.

        Raises:
            ValueError: if the provided pipeline ID doesn't match the pipeline service.
        """

        pipeline_match = False

        for pipeline_template in self._template_ref.values():
            service_pipeline_json = yaml_utils.load_yaml(pipeline_template)[
                "components"
            ]
            current_pipeline_json = pipeline_job.to_dict()["pipelineSpec"]["components"]

            if service_pipeline_json == current_pipeline_json:
                pipeline_match = True

        if not pipeline_match:
            raise ValueError(
                f"The provided pipeline template is not compatible with {self.__class__.__name__}"
            )

    def __init__(
        self,
        pipeline_job_name: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves an existing Pipeline Based Service given the ID of the pipeline execution.
        Example Usage:
            pipeline_service = aiplatform._pipeline_based_service._VertexAiPipelineBasedService(
                pipeline_job_name = "projects/123/locations/us-central1/pipelinesJobs/456"
            )
            pipeline_service = aiplatform.VertexAiPipelinebasedService(
                pipeline_job_name = "456"
            )
        Args:
            pipeline_job_name (str):
                Required. A fully-qualified pipeline job run.
                Example: "projects/123/locations/us-central1/pipelineJobs/456" or
                "456" when project and location are initialized or passed.
            project (str):
                Optional. Project to retrieve pipeline job from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to retrieve pipeline job from. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to retrieve this pipeline job. Overrides
                credentials set in aiplatform.init.
        Raises:
            ValueError: if the pipeline template used in this PipelineJob is not consistent with the _template_ref defined on the subclass.
        """

        super().__init__(
            project=project,
            location=location,
            credentials=credentials,
            resource_name=pipeline_job_name,
        )

        job_resource = pipeline_jobs.PipelineJob.get(resource_name=pipeline_job_name)

        self._validate_pipeline_template_matches_service(job_resource)

        self._gca_resource = gca_pipeline_job.PipelineJob(name=pipeline_job_name)

    @classmethod
    def _create_and_submit_pipeline_job(
        cls,
        template_params: Dict[str, Any],
        template_path: str,
        pipeline_root: str,
        display_name: Optional[str] = None,
        job_id: Optional[str] = None,
        service_account: Optional[str] = None,
        network: Optional[str] = None,
        encryption_spec_key_name: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        experiment: Optional[Union[str, "aiplatform.Experiment"]] = None,
    ) -> "_VertexAiPipelineBasedService":
        """Create a new PipelineJob using the provided template and parameters.
        Args:
            template_params (Dict[str, Any]):
                Required. The parameters to pass to the given pipeline template.
            template_path (Dict[str, Any]):
                Required. The path of the pipeline template to use for this pipeline run.
            pipeline_root (str)
                Required. The GCS directory to store the pipeline run output.
            display_name (str)
                Optional. The user-defined name of the PipelineJob created by this Pipeline Based Service.
            job_id (str):
                Optional. The unique ID of the job run.
                If not specified, pipeline name + timestamp will be used.
            service_account (str):
                Specifies the service account for workload run-as account.
                Users submitting jobs must have act-as permission on this run-as account.
            network (str):
                The full name of the Compute Engine network to which the job
                should be peered. For example, projects/12345/global/networks/myVPC.
                Private services access must already be configured for the network.
                If left unspecified, the job is not peered with any network.
            project (str):
                Optional. The project to run this PipelineJob in. If not set,
                the project set in aiplatform.init will be used.
            location (str):
                Optional. Location to create PipelineJob. If not set,
                location set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to create the PipelineJob.
                Overrides credentials set in aiplatform.init.
            experiment (Union[str, experiments_resource.Experiment]):
                Optional. The Vertex AI experiment name or instance to associate to the PipelineJob executing
                this model evaluation job.
        Returns:
            (VertexAiPipelineBasedService):
                Instantiated representation of a Vertex AI Pipeline based service.
        """

        if not display_name:
            display_name = cls._generate_display_name()

        self = cls._empty_constructor(
            project=project,
            location=location,
            credentials=credentials,
        )

        service_pipeline_job = pipeline_jobs.PipelineJob(
            display_name=display_name,
            template_path=template_path,
            job_id=job_id,
            pipeline_root=pipeline_root,
            parameter_values=template_params,
            encryption_spec_key_name=encryption_spec_key_name,
            project=project,
            location=location,
            credentials=credentials,
        )

        # Suppresses logs from PipelineJob
        # The class implementing _VertexAiPipelineBasedService should define a custom log message
        logging.getLogger("google.cloud.aiplatform.pipeline_jobs").setLevel(
            logging.WARNING
        )

        service_pipeline_job.submit(
            service_account=service_account,
            network=network,
            experiment=experiment,
        )

        logging.getLogger("google.cloud.aiplatform.pipeline_jobs").setLevel(
            logging.INFO
        )

        self._gca_resource = service_pipeline_job.gca_resource

        return self

    @classmethod
    def list(
        cls,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[str] = None,
    ) -> List["pipeline_jobs.PipelineJob"]:
        """Lists all PipelineJob resources associated with this Pipeline Based service.
        Args:
            project (str):
                Optional. The project to retrieve the Pipeline Based Services from. If not set,
                the project set in aiplatform.init will be used.
            location (str):
                Optional. Location to retrieve the Pipeline Based Services from. If not set,
                location set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to retrieve the Pipeline Based Services from.
                Overrides credentials set in aiplatform.init.
        Returns:
            (List[PipelineJob]):
                A list of PipelineJob resource objects.
        """
        self = cls._empty_constructor(
            project=project,
            location=location,
            credentials=credentials,
        )

        all_pipeline_jobs = pipeline_jobs.PipelineJob.list(
            project=project,
            location=location,
            credentials=credentials,
        )

        service_pipeline_jobs = []

        for job in all_pipeline_jobs:
            try:
                self._validate_pipeline_template_matches_service(job)
                service_pipeline_jobs.append(job)

            except ValueError:
                continue

        return service_pipeline_jobs
