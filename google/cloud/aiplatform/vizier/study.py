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
import copy

from typing import Dict, List, Optional, Sequence, Tuple
from typing import Optional, Collection, Type, TypeVar, Mapping, Any
from google.cloud.aiplatform.vizier.client_abc import StudyInterface
from google.cloud.aiplatform.vizier.client_abc import TrialInterface

from google.api_core import exceptions
from google.auth import credentials as auth_credentials
from google.cloud.aiplatform import base
from google.cloud.aiplatform import utils
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.vizier import study
from google.cloud.aiplatform.vizier.trial import Trial
from google.cloud.aiplatform.vizier import pyvizier as vz

from google.cloud.aiplatform.compat.services import vizier_service_client_v1
from google.cloud.aiplatform.compat.types import (
    study as gca_study,
    vizier_service as gca_vizier_service,
)


_T = TypeVar("_T")
_LOGGER = base.Logger(__name__)


class Study(base.VertexAiResourceNounWithFutureManager, StudyInterface):
    """Manage Study resource for Vertex Vizier."""

    client_class = utils.VizierClientWithOverride

    _resource_noun = "study"
    _getter_method = "get_study"
    _list_method = "list_studies"
    _delete_method = "delete_study"
    _parse_resource_name_method = "parse_study_path"
    _format_resource_name_method = "study_path"

    def __init__(
        self,
        study_id: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves an existing managed study given a study resource name or a study id.

        Example Usage:
            study = aiplatform.Study(study_id = '12345678')
            or
            study = aiplatform.Study(study_id = 'projects/123/locations/us-central1/studies/12345678')

        Args:
            study_id (str):
                Required. A fully-qualified study resource name or a study ID.
                Example: "projects/123/locations/us-central1/studies/12345678" or "12345678" when
                project and location are initialized or passed.
            project (str):
                Optional. Project to retrieve feature from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to retrieve feature from. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to retrieve this Feature. Overrides
                credentials set in aiplatform.init.
        """
        base.VertexAiResourceNounWithFutureManager.__init__(
            self,
            project=project,
            location=location,
            credentials=credentials,
            resource_name=study_id,
        )
        self._gca_resource = self._get_gca_resource(resource_name=study_id)

    @classmethod
    @base.optional_sync()
    def create_or_load(
        cls, display_name: str, problem: vz.ProblemStatement
    ) -> StudyInterface:
        """Creates a Study resource.

        Example Usage:
            sc = pyvizier.StudyConfig()
            sc.algorithm = pyvizier.Algorithm.RANDOM_SEARCH
            sc.metric_information.append(
                pyvizier.MetricInformation(
                    name='pr-auc', goal=pyvizier.ObjectiveMetricGoal.MAXIMIZE))
            root = sc.search_space.select_root()
            root.add_float_param(
                'learning_rate', 0.00001, 1.0, scale_type=pyvizier.ScaleType.LINEAR)
            root.add_categorical_param('optimizer', ['adagrad', 'adam', 'experimental'])
            study = aiplatform.Study.create_or_load(display_name='display_name', problem=sc)

        Args:
            display_name (str):
                A name to describe the Study.
            problem (vz.ProblemStatement):
                Configurations of the study. It defines the problem to create the study.
        """
        api_client = cls._instantiate_client(
            location=initializer.global_config.location,
            credentials=initializer.global_config.credentials,
        )
        study = gca_study.Study(
            display_name=display_name, study_spec=problem.to_proto()
        )

        try:
            study = api_client.create_study(
                parent=initializer.global_config.common_location_path(
                    initializer.global_config.project,
                    initializer.global_config.location,
                ),
                study=study,
            )
        except exceptions.AlreadyExists:
            _LOGGER.info("The study is aleady created. Using existing study.")
            study = api_client.lookup_study(
                request={
                    "parent": initializer.global_config.common_location_path(
                        initializer.global_config.project,
                        initializer.global_config.location,
                    ),
                    "display_name": display_name,
                }
            )

        return Study(study.name)

    def get_trial(self, uid: int) -> TrialInterface:
        """Retrieves the trial under the study by given trial id."""
        study_path_components = self._parse_resource_name(self.resource_name)
        _LOGGER.info(study_path_components)
        return Trial(
            Trial._format_resource_name(
                project=study_path_components["project"],
                location=study_path_components["location"],
                study=study_path_components["study"],
                trial=uid,
            )
        )

    def trials(
        self, trial_filter: Optional[vz.TrialFilter] = None
    ) -> Collection[TrialInterface]:
        """Fetches a collection of trials."""
        list_trials_request = {"parent": self.resource_name}
        trials_response = self.api_client.list_trials(request=list_trials_request)
        return [Trial(trial.name) for trial in trials_response.trials]

    def optimal_trials(self) -> Collection[TrialInterface]:
        """Returns optimal trial(s)."""
        list_optimal_trials_request = {"parent": self.resource_name}
        optimal_trials_response = self.api_client.list_optimal_trials(
            request=list_optimal_trials_request
        )
        return [Trial(trial.name) for trial in optimal_trials_response.optimal_trials]

    def materialize_study_config(self) -> vz.StudyConfig:
        """#Materializes the study config."""
        study = self.api_client.get_study(name=self.resource_name)
        return copy.deepcopy(vz.StudyConfig.from_proto(study.study_spec))

    @classmethod
    def from_uid(cls: Type[_T], uid: str) -> _T:
        """Fetches an existing study from the Vizier service.

        Args:
          uid: Unique identifier of the study.
        """
        return Study(study_id=uid)

    def suggest(
        self, *, count: Optional[int] = None, worker: str = ""
    ) -> Collection[TrialInterface]:
        """Returns Trials to be evaluated by worker.

        Args:
          count: Number of suggestions.
          worker: When new Trials are generated, their `assigned_worker` field is
            populated with this worker. suggest() first looks for existing Trials
            that are assigned to `worker`, before generating new ones.
        """
        suggest_trials_lro = self.api_client.suggest_trials(
            request={
                "parent": self.resource_name,
                "suggestion_count": count,
                "client_id": worker,
            }
        )
        _LOGGER.log_action_started_against_resource_with_lro(
            "Suggest", "study", self.__class__, suggest_trials_lro
        )
        _LOGGER.info(self.client_class.get_gapic_client_class())
        trials = suggest_trials_lro.result()
        _LOGGER.log_action_completed_against_resource("study", "suggested", self)
        return [Trial(trial.name) for trial in trials.trials]

    def delete(self) -> None:
        """Deletes the study."""
        self.api_client.delete_study(name=self.resource_name)
