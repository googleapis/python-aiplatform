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

from typing import List, Union

from google.cloud import aiplatform


#  [START aiplatform_sdk_import_data_video_classification_sample]
def import_data_video_classification_sample(
    project: str,
    location: str,
    dataset_name: str,
    src_uris: Union[str, List[str]],
    sync: bool = True,
):
    aiplatform.init(project=project, location=location)

    ds = aiplatform.VideoDataset(dataset_name=dataset_name)

    print(ds.display_name)
    print(ds.resource_name)

    ds.import_data(
        gcs_source=src_uris,
        import_schema_uri=aiplatform.schema.dataset.ioformat.video.classification,
        sync=sync,
    )

    ds.wait()

    return ds


#  [END aiplatform_sdk_import_data_video_classification_sample]
