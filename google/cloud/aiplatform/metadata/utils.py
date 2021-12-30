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

from google.cloud.aiplatform import base
from google.cloud.aiplatform.constants import base as constants

def make_gcp_resource_url(resource: base.VertexAiResourceNoun) -> str:
	resource_name = resource.resource_name
	location = resource.location
	version = resource.api_client._default_version
	api_uri = resource.api_client.api_endpoint

	return f'https://{api_uri}/{version}/{resource_name}'