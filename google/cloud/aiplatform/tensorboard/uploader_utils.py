
# -*- coding: utf-8 -*-

# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Shared utils for tensorboard log uploader."""
import uuid

from google.cloud.aiplatform.compat.types import (
    tensorboard_run_v1beta1 as tensorboard_run,
)
from google.cloud.aiplatform.compat.services import tensorboard_service_client_v1beta1

TensorboardServiceClient = tensorboard_service_client_v1beta1.TensorboardServiceClient

class RunResourceManager():
    def __init__(
        self,
        api: TensorboardServiceClient,
        experiment_resource_name: str
    ):
        self._api = api
        self._experiment_resource_name = experiment_resource_name

        self._run_to_run_resource: Dict[str, tensorboard_run.TensorboardRun] = {}

    def create_or_get_run_resource(self, run_name: str):
        """Creates a new Run Resource in current Tensorboard Experiment resource.

        Args:
          run_name: The display name of this run.
        """

        if run_name in self._run_to_run_resource:
            return self._run_to_run_resource[run_name]

        tb_run = tensorboard_run.TensorboardRun()
        tb_run.display_name = run_name
        try:
            tb_run = self._api.create_tensorboard_run(
                parent=self._experiment_resource_name,
                tensorboard_run=tb_run,
                tensorboard_run_id=str(uuid.uuid4()),
            )
        except exceptions.InvalidArgument as e:
            # If the run name already exists then retrieve it
            if "already exist" in e.message:
                runs_pages = self._api.list_tensorboard_runs(
                    parent=self._experiment_resource_name
                )
                for tb_run in runs_pages:
                    if tb_run.display_name == run_name:
                        break

                if tb_run.display_name != run_name:
                    raise ExistingResourceNotFoundError(
                        "Run with name %s already exists but is not resource list."
                        % run_name
                    )
            else:
                raise

        self._run_to_run_resource[run_name] = tb_run
        return tb_run
