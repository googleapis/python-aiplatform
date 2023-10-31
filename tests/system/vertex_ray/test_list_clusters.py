# -*- coding: utf-8 -*-

# Copyright 2023 Google LLC
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

from google.cloud import aiplatform
from google.cloud.aiplatform.preview import vertex_ray
import ray

print(ray.__version__)

aiplatform.init(project='tangmatthew-dev', location='us-central1')

from vertex_ray import Resources

# CPU default cluster
head_node_type = Resources()
worker_node_types = [Resources()]

print(vertex_ray.list_ray_clusters())
