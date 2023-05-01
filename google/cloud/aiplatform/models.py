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
from google.cloud.aiplatform import _models
from google.cloud.aiplatform import base
from google.cloud.aiplatform.preview import models as preview_models


class ModelRegistry(_models.ModelRegistry):
    """Public managed ModelRegistry resource for Vertex AI."""

    pass


class PrivateEndpoint(_models.PrivateEndpoint):
    """Public managed PrivateEdnpoint resource for Vertex AI."""

    pass


class VersionInfo(_models.VersionInfo):
    """Public managed VersionInfo resource for Vertex AI."""

    pass


class Prediction(_models.Prediction):
    """Public managed Prediction resource for Vertex AI."""

    pass


class Endpoint(_models._Endpoint, base.PreviewMixin):
    """Public managed Endpoint resource for Vertex AI."""

    _preview_class = preview_models.Endpoint


class Model(_models._Model, base.PreviewMixin):
    """Public managed Model resource for Vertex AI."""

    _preview_class = preview_models.Model
