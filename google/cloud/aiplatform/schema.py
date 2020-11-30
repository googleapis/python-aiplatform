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

"""Namespaced AI Platform Schemas."""


class training_job:
    class definition:
        custom_task = "gs://google-cloud-aiplatform/schema/trainingjob/definition/custom_task_1.0.0.yaml"
        tabular_task = "gs://google-cloud-aiplatform/schema/trainingjob/definition/automl_tabular_1.0.0.yaml"


class dataset:
    class metadata:
        tabular = (
            "gs://google-cloud-aiplatform/schema/dataset/metadata/tabular_1.0.0.yaml"
        )
        image = "gs://google-cloud-aiplatform/schema/dataset/metadata/image_1.0.0.yaml"
