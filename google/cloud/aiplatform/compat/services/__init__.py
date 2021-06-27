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

from google.cloud.aiplatform_v1beta1.services.dataset_service import (
    client as dataset_service_client_v1beta1,
)
from google.cloud.aiplatform_v1beta1.services.endpoint_service import (
    client as endpoint_service_client_v1beta1,
)
from google.cloud.aiplatform_v1beta1.services.job_service import (
    client as job_service_client_v1beta1,
)
from google.cloud.aiplatform_v1beta1.services.model_service import (
    client as model_service_client_v1beta1,
)
from google.cloud.aiplatform_v1beta1.services.pipeline_service import (
    client as pipeline_service_client_v1beta1,
)
from google.cloud.aiplatform_v1beta1.services.prediction_service import (
    client as prediction_service_client_v1beta1,
)
from google.cloud.aiplatform_v1beta1.services.specialist_pool_service import (
    client as specialist_pool_service_client_v1beta1,
)
from google.cloud.aiplatform_v1beta1.services.metadata_service import (
    client as metadata_service_client_v1beta1,
)
from google.cloud.aiplatform_v1beta1.services.tensorboard_service import (
    client as tensorboard_service_client_v1beta1,
)

from google.cloud.aiplatform_v1.services.dataset_service import (
    client as dataset_service_client_v1,
)
from google.cloud.aiplatform_v1.services.endpoint_service import (
    client as endpoint_service_client_v1,
)
from google.cloud.aiplatform_v1.services.job_service import (
    client as job_service_client_v1,
)
from google.cloud.aiplatform_v1.services.model_service import (
    client as model_service_client_v1,
)
from google.cloud.aiplatform_v1.services.pipeline_service import (
    client as pipeline_service_client_v1,
)
from google.cloud.aiplatform_v1.services.prediction_service import (
    client as prediction_service_client_v1,
)
from google.cloud.aiplatform_v1.services.specialist_pool_service import (
    client as specialist_pool_service_client_v1,
)

__all__ = (
    # v1
    dataset_service_client_v1,
    endpoint_service_client_v1,
    job_service_client_v1,
    model_service_client_v1,
    pipeline_service_client_v1,
    prediction_service_client_v1,
    specialist_pool_service_client_v1,
    # v1beta1
    dataset_service_client_v1beta1,
    endpoint_service_client_v1beta1,
    job_service_client_v1beta1,
    model_service_client_v1beta1,
    pipeline_service_client_v1beta1,
    prediction_service_client_v1beta1,
    specialist_pool_service_client_v1beta1,
    metadata_service_client_v1beta1,
    tensorboard_service_client_v1beta1,
)
