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
    # Sample function parameter parent in create_data_labeling_job_specialist_pool_sample
    parent = parent

    return parent


def make_data_labeling_job(
    display_name: str,
    dataset: str,
    specialist_pool: str,
    instruction_uri: str,
    inputs_schema_uri: str,
    annotation_spec: str,
) -> google.cloud.aiplatform_v1beta1.types.data_labeling_job.DataLabelingJob:
    inputs_dict = {"annotation_specs": [annotation_spec]}
    inputs = to_protobuf_value(inputs_dict)

    data_labeling_job = {
        "display_name": display_name,
        # Full resource name: projects/{project}/locations/{location}/datasets/{dataset_id}
        "datasets": [dataset],
        "labeler_count": 1,
        "instruction_uri": instruction_uri,
        "inputs_schema_uri": inputs_schema_uri,
        "inputs": inputs,
        "annotation_labels": {
            "aiplatform.googleapis.com/annotation_set_name": "data_labeling_job_specialist_pool"
        },
        # Full resource name: projects/{project}/locations/{location}/specialistPools/{specialist_pool_id}
        "specialist_pools": [specialist_pool],
    }

    return data_labeling_job
