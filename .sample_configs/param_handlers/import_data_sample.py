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

def make_name(name: str) -> str:
    return name

def make_import_configs(gcs_source_uri: str, import_schema_uri: str) -> typing.Sequence[google.cloud.aiplatform_v1alpha1.types.dataset.ImportDataConfig]:
    # Here we use only one import config with one source
    import_configs = [
        {
            "gcs_source": {
            	"uris": [
            		gcs_source_uri
            	]
            },
            "import_schema_uri": import_schema_uri,
        }
    ]

    return import_configs

