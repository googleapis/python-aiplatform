# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


#  [START aiplatform_sdk_create_and_import_dataset_image_sample]
from typing import List, Union

from google.cloud import aiplatform


def create_and_import_dataset_image_sample(
    project: str,
    location: str,
    display_name: str,
    src_uris: Union[str, List[str]],
    sync: bool = True,
):
    """
    src_uris -- a string or list of strings, e.g.
        ["gs://bucket1/source1.jsonl", "gs://bucket7/source4.jsonl"]
    """

    aiplatform.init(project=project, location=location)

    ds = aiplatform.ImageDataset.create(
        display_name=display_name,
        gcs_source=src_uris,
        import_schema_uri=aiplatform.schema.dataset.ioformat.image.single_label_classification,
        sync=sync,
    )

    ds.wait()

    print(ds.display_name)
    print(ds.resource_name)
    return ds


#  [END aiplatform_sdk_create_and_import_dataset_image_sample]
