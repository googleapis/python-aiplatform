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

from google.cloud.aiplatform_v1beta1.services.model_service import client as model_client

from typing import Dict, Optional, Sequence

from google.auth import credentials as auth_credentials
from google.cloud.aiplatform import base
from google.cloud.aiplatform import utils
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform_v1beta1.services.model_service.client import ModelServiceClient
from google.cloud.aiplatform_v1beta1.types import model as gca_model
from google.cloud.aiplatform_v1beta1.types import env_var
        

class Model(base.AiPlatformResourceNoun):
    
    client_class =  ModelServiceClient
    is_prediction_client = False
    
    @property
    def uri(self):
        """Uri of the model."""
        return self._gca_resource.artifact_uri

    @property
    def description(self):
        """Description of the model."""
        return self._gca_model.description
    
    def __init__(self,
                 model_name:str,
                 project: Optional[str]=None,
                 location: Optional[str]=None,
                 credentials: Optional[auth_credentials.Credentials]=None):
        """Retrieves the model resource and instanties it's representation.

        Args:
            model_name (str): The name of the model to retrieve.
            project (str):
                Optional project to retrieve model from. If not set, project set in
                aiplatform.init will be used.
            location (str):
                Optional location to retrieve model from. If not set, location set in
                aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional credentials to use to retrieve the model.
        """
        
        super().__init__(project=project, location=location, credentials=credentials)
        self._gca_resource = self._get_model(model_name)
        
    
    def _get_model(self, model_name:str) -> gca_model.Model:
        """Gets the model from AI Platform.

        Args:
            model_name (str): The name of the model to retrieve.
        Returns:
            model: Managed Model resource.
        """
        resource_name = ModelServiceClient.model_path(self.project, self.location,
                                                      model_name)
        
        # TODO(b/170954330) add optional instantiation if resource path given
        model = self.api_client.get_model(name=resource_name)
        return model
    
    # TODO(b/170979552) Add support for predict schemata
    # TODO(b/170979926) Add support for metadata and metadata schema
    @classmethod
    def upload(cls,
               display_name:str,
               artifact_uri: str,
               serving_container_image_uri: str,
               # TODO (b/162273530) lift requirement for predict/health route when
               # validation lifted and move these args down
               serving_container_predict_route: str,
               serving_container_health_route: str,
               *,
               description:Optional[str]=None,
               serving_container_command: Optional[Sequence[str]]=None,
               serving_container_args: Optional[Sequence[str]]=None,
               serving_container_environment_variables: Optional[Dict[str, str]]=None,
               serving_container_ports: Optional[Sequence[int]]=None,
               project: Optional[str]=None,
               location: Optional[str]=None,
               credentials: Optional[auth_credentials.Credentials]=None,
               ) -> 'Model':
        """Uploads a model and returns a Model representing the uploaded Model resource.

        Example usage:

        my_model = Model.upload(
            display_name='my-model',
            artifact_uri='gs://my-model/saved-model'
            serving_container_image_uri='tensorflow/serving'
        )

        Args:
            display_name (str):
                Required. The display name of the Model. The name can be up to 128
                characters long and can be consist of any UTF-8 characters.
            artifact_uri (str):
                Required. The path to the directory containing the Model artifact and
                any of its supporting files. Not present for AutoML Models.
            serving_container_image_uri (str):
                Required. The URI of the Model serving container.
            serving_container_predict_route (str):
                Required. An HTTP path to send prediction requests to the container, and
                which must be supported by it. If not specified a default HTTP path will
                be used by AI Platform.
            serving_container_health_route (str):
                An HTTP path to send health check requests to the container, and which
                must be supported by it. If not specified a standard HTTP path will be
                used by AI Platform.
            description (str):
                The description of the model.
            serving_container_command: Optional[Sequence[str]]=None,
                The command with which the container is run. Not executed within a
                shell. The Docker image's ENTRYPOINT is used if this is not provided.
                Variable references $(VAR_NAME) are expanded using the container's
                environment. If a variable cannot be resolved, the reference in the
                input string will be unchanged. The $(VAR_NAME) syntax can be escaped
                with a double $$, ie: $$(VAR_NAME). Escaped references will never be
                expanded, regardless of whether the variable exists or not.
            serving_container_args: Optional[Sequence[str]]=None,
                The arguments to the command. The Docker image's CMD is used if this is
                not provided. Variable references $(VAR_NAME) are expanded using the
                container's environment. If a variable cannot be resolved, the reference
                in the input string will be unchanged. The $(VAR_NAME) syntax can be
                escaped with a double $$, ie: $$(VAR_NAME). Escaped references will
                never be expanded, regardless of whether the variable exists or not.
            serving_container_environment_variables: Optional[Dict[str, str]]=None,
                The environment variables that are to be present in the container.
                Should be a dictionary where keys are environment variable names
                and values are environment variable values for those names. 
            serving_container_ports: Optional[Sequence[int]]=None,
                Declaration of ports that are exposed by the container. This field is
                primarily informational, it gives AI Platform information about the
                network connections the container uses. Listing or not a port here has
                no impact on whether the port is actually exposed, any port listening on
                the default "0.0.0.0" address inside a container will be accessible from
                the network.
            project: Optional[str]=None,
                Project to upload this model to. Overrides project set in
                aiplatform.init.
            location: Optional[str]=None,
                Location to upload this model to. Overrides location set in
                aiplatform.init.
            credentials: Optional[auth_credentials.Credentials]=None,
                Custom credentials to use to upload this model. Overrides credentials
                set in aiplatform.init. 
        Returns:
            model: Instantiated representation of the uplaoded model resource.
        """
        
        api_client = cls._instantiate_client(location, credentials)
        env = None
        ports = None
        
        if serving_container_environment_variables:
            env = [env_var.EnvVar(name=str(key), value=str(value))
                    for key, value in serving_container_environment_variables.items()]
        if serving_container_ports:
            ports = [gca_model.Port(container_port=port)
                    for port in serving_container_ports]
        
        container_spec = gca_model.ModelContainerSpec(
            image_uri=serving_container_image_uri,
            command=serving_container_command,
            args=serving_container_args,
            env=env,
            ports=ports,
            predict_route=serving_container_predict_route,
            health_route=serving_container_health_route,
        )

        managed_model = gca_model.Model(
            display_name=display_name,
            description=description,
            artifact_uri=artifact_uri,
            container_spec=container_spec)


        lro = api_client.upload_model(
            parent=initializer.global_config.get_resource_parent(project, location),
            model=managed_model)

        managed_model = lro.result()
        fields = utils.extract_fields_form_resource_name(managed_model.model)
        return cls(model_name=fields.id, project=fields.project,
            location=fields.location)

    # TODO(b/169782716) add support for deployment when Endpoint class complete
    def deploy(self):
        raise NotImplementedError('Deployment not implemented.')
        

class Endpoint:
    pass
