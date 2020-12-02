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

def make_parent(parent: str) -> str:
    parent = parent

    return parent

def make_dataset(display_name: str, gcs_uri: str) -> google.cloud.aiplatform_v1alpha1.types.dataset.Dataset:
    metadata_dict = {
        'input_config': {
            'gcs_source': {
                'uri': [gcs_uri]
            }
        }
    }
    metadata = to_protobuf_value(metadata_dict)

    dataset = {
        'display_name': display_name,
        'metadata_schema_uri': "gs://google-cloud-aiplatform/schema/dataset/metadata/tabular_1.0.0.yaml",
        'metadata': metadata
    }

    return dataset