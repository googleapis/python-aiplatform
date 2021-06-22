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

import datetime
import time
import re
from typing import Any, Optional, Dict

from google.auth import credentials as auth_credentials
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.utils import json_utils
from google.cloud.aiplatform.utils import pipeline_utils
from google.protobuf import json_format

from google.cloud.aiplatform.compat.types import (
    pipeline_job_v1beta1 as gca_pipeline_job_v1beta1,
    pipeline_state_v1beta1 as gca_pipeline_state_v1beta1,
)

_LOGGER = base.Logger(__name__)

_PIPELINE_COMPLETE_STATES = set(
    [
        gca_pipeline_state_v1beta1.PipelineState.PIPELINE_STATE_SUCCEEDED,
        gca_pipeline_state_v1beta1.PipelineState.PIPELINE_STATE_FAILED,
        gca_pipeline_state_v1beta1.PipelineState.PIPELINE_STATE_CANCELLED,
        gca_pipeline_state_v1beta1.PipelineState.PIPELINE_STATE_PAUSED,
    ]
)

# Vertex AI Pipelines service API job name relative name prefix pattern.
_JOB_NAME_PATTERN = "{parent}/pipelineJobs/{job_id}"

# Pattern for valid names used as a Vertex resource name.
_VALID_NAME_PATTERN = re.compile("^[a-z][-a-z0-9]{0,127}$")


def _get_current_time() -> datetime.datetime:
    """Gets the current timestamp."""
    return datetime.datetime.now()


def _set_enable_caching_value(
    pipeline_spec: Dict[str, Any], enable_caching: bool
) -> None:
    """Sets pipeline tasks caching options.

    Args:
     pipeline_spec (Dict[str, Any]):
          Required. The dictionary of pipeline spec.
     enable_caching (bool):
          Required. Whether to enable caching.
    """
    for component in [pipeline_spec["root"]] + list(
        pipeline_spec["components"].values()
    ):
        if "dag" in component:
            for task in component["dag"]["tasks"].values():
                task["cachingOptions"] = {"enableCache": enable_caching}


class PipelineJob(base.VertexAiResourceNounWithFutureManager):

    client_class = utils.PipelineJobClientWithOverride
    _is_client_prediction_client = False

    _resource_noun = "pipelineJobs"
    _delete_method = "delete_pipeline_job"
    _getter_method = "get_pipeline_job"
    _list_method = "list_pipeline_jobs"

    def __init__(
        self,
        display_name: str,
        template_path: str,
        job_id: Optional[str] = None,
        pipeline_root: Optional[str] = None,
        parameter_values: Optional[Dict[str, Any]] = None,
        enable_caching: Optional[bool] = True,
        encryption_spec_key_name: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
    ):
        """Retrieves a PipelineJob resource and instantiates its
        representation.

        Args:
            display_name (str):
                Required. The user-defined name of this Pipeline.
            template_path (str):
                Required. The path of PipelineJob JSON file. It can be a local path or a
                Google Cloud Storage URI. Example: "gs://project.name"
            job_id (str):
                Optional. The unique ID of the job run.
                If not specified, pipeline name + timestamp will be used.
            pipeline_root (str):
                Optional. The root of the pipeline outputs. Default to be staging bucket.
            parameter_values (Dict[str, Any]):
                Optional. The mapping from runtime parameter names to its values that
                control the pipeline run.
            enable_caching (bool):
                Optional. Whether to turn on caching for the run. Defaults to True.
            encryption_spec_key_name (str):
                Optional. The Cloud KMS resource identifier of the customer
                managed encryption key used to protect the job. Has the
                form:
                ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                The key needs to be in the same region as where the compute
                resource is created.

                If this is set, then all
                resources created by the BatchPredictionJob will
                be encrypted with the provided encryption key.

                Overrides encryption_spec_key_name set in aiplatform.init.
            labels (Dict[str,str]):
                Optional. The user defined metadata to organize PipelineJob.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to create this batch prediction
                job. Overrides credentials set in aiplatform.init.
            project (str),
                Optional. Project to retrieve PipelineJob from. If not set,
                project set in aiplatform.init will be used.
            location (str),
                Optional. Location to create PipelineJob. If not set,
                location set in aiplatform.init will be used.

        Raises:
            ValueError: If job_id or labels have incorrect format.
        """
        utils.validate_display_name(display_name)

        if labels:
            for k, v in labels.items():
                if not isinstance(k, str) or not isinstance(v, str):
                    raise ValueError(
                        "Expect labels to be a mapping of string key value pairs. "
                        'Got "{}".'.format(labels)
                    )

        super().__init__(project=project, location=location, credentials=credentials)

        self._parent = initializer.global_config.common_location_path(
            project=project, location=location
        )
        pipeline_job = json_utils.load_json(
            template_path, self.project, self.credentials
        )
        pipeline_root = (
            pipeline_root
            or pipeline_job["runtimeConfig"].get("gcsOutputDirectory")
            or initializer.global_config.staging_bucket
        )

        pipeline_name = pipeline_job["pipelineSpec"]["pipelineInfo"]["name"]
        job_id = job_id or "{pipeline_name}-{timestamp}".format(
            pipeline_name=re.sub("[^-0-9a-z]+", "-", pipeline_name.lower())
            .lstrip("-")
            .rstrip("-"),
            timestamp=_get_current_time().strftime("%Y%m%d%H%M%S"),
        )
        if not _VALID_NAME_PATTERN.match(job_id):
            raise ValueError(
                "Generated job ID: {} is illegal as a Vertex pipelines job ID. "
                "Expecting an ID following the regex pattern "
                '"[a-z][-a-z0-9]{{0,127}}"'.format(job_id)
            )
        job_name = _JOB_NAME_PATTERN.format(parent=self._parent, job_id=job_id)

        builder = pipeline_utils.PipelineRuntimeConfigBuilder.from_job_spec_json(
            pipeline_job
        )
        builder.update_pipeline_root(pipeline_root)
        builder.update_runtime_parameters(parameter_values)
        runtime_config_dict = builder.build()
        runtime_config = gca_pipeline_job_v1beta1.PipelineJob.RuntimeConfig()._pb
        json_format.ParseDict(runtime_config_dict, runtime_config)

        _set_enable_caching_value(pipeline_job["pipelineSpec"], enable_caching)

        self._gca_resource = gca_pipeline_job_v1beta1.PipelineJob(
            display_name=display_name,
            name=job_name,
            pipeline_spec=pipeline_job["pipelineSpec"],
            labels=labels,
            runtime_config=runtime_config,
            encryption_spec=initializer.global_config.get_encryption_spec(
                encryption_spec_key_name=encryption_spec_key_name
            ),
        )

    @base.optional_sync()
    def run(
        self,
        service_account: Optional[str] = None,
        network: Optional[str] = None,
        sync: Optional[bool] = True,
    ) -> None:
        """Run this configured PipelineJob.

        Args:
            service_account (str):
                Optional. Specifies the service account for workload run-as account.
                Users submitting jobs must have act-as permission on this run-as account.
            network (str):
                Optional. The full name of the Compute Engine network to which the job
                should be peered. For example, projects/12345/global/networks/myVPC.
                Private services access must already be configured for the network.
                If left unspecified, the job is not peered with any network.
            sync (bool):
                Optional. Whether to execute this method synchronously. If False, this method will unblock and it will be executed in a concurrent Future.
        """
        if service_account:
            self._gca_resource.pipeline_spec.service_account = service_account

        if network:
            self._gca_resource.pipeline_spec.network = network

        _LOGGER.log_create_with_lro(self.__class__)

        self._gca_resource = self.api_client.create_pipeline_job(
            parent=self._parent, pipeline_job=self._gca_resource
        )

        _LOGGER.log_create_complete_with_getter(
            self.__class__, self._gca_resource, "pipeline_job"
        )

        _LOGGER.info("View Pipeline Job:\n%s" % self._dashboard_uri())

        self._block_until_complete()

    @property
    def pipeline_spec(self):
        return self._gca_resource.pipeline_spec

    @property
    def state(self) -> Optional[gca_pipeline_state_v1beta1.PipelineState]:
        """Current pipeline state."""
        if not self._has_run:
            raise RuntimeError("Job has not run. No state available.")

        self._sync_gca_resource()
        return self._gca_resource.state

    @property
    def _has_run(self) -> bool:
        """Helper property to check if this pipeline job has been run."""
        return bool(self._gca_resource.create_time)

    @property
    def has_failed(self) -> bool:
        """Returns True if pipeline has failed.

        False otherwise.
        """
        return (
            self.state == gca_pipeline_state_v1beta1.PipelineState.PIPELINE_STATE_FAILED
        )

    def _dashboard_uri(self) -> str:
        """Helper method to compose the dashboard uri where pipeline can be
        viewed."""
        fields = utils.extract_fields_from_resource_name(self.resource_name)
        url = f"https://console.cloud.google.com/vertex-ai/locations/{fields.location}/pipelines/runs/{fields.id}?project={fields.project}"
        return url

    def _sync_gca_resource(self):
        """Helper method to sync the local gca_source against the service."""
        self._gca_resource = self.api_client.get_pipeline_job(name=self.resource_name)

    def _block_until_complete(self):
        """Helper method to block and check on job until complete."""
        # Used these numbers so failures surface fast
        wait = 5  # start at five seconds
        log_wait = 5
        max_wait = 60 * 5  # 5 minute wait
        multiplier = 2  # scale wait by 2 every iteration

        previous_time = time.time()
        while self.state not in _PIPELINE_COMPLETE_STATES:
            current_time = time.time()
            if current_time - previous_time >= log_wait:
                _LOGGER.info(
                    "%s %s current state:\n%s"
                    % (
                        self.__class__.__name__,
                        self._gca_resource.name,
                        self._gca_resource.state,
                    )
                )
                log_wait = min(log_wait * multiplier, max_wait)
                previous_time = current_time
            time.sleep(wait)

    def cancel(self) -> None:
        """Starts asynchronous cancellation on the PipelineJob. The server
        makes a best effort to cancel the job, but success is not guaranteed.
        On successful cancellation, the PipelineJob is not deleted; instead it
        becomes a job with state set to `CANCELLED`.

        Raises:
            RuntimeError: If this PipelineJob has not started running.
        """
        if not self._has_run:
            raise RuntimeError(
                "This PipelineJob has not been launched, use the `run()` method "
                "to start. `cancel()` can only be called on a job that is running."
            )
        self.api_client.cancel_pipeline_job(name=self.resource_name)
