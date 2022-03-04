# Copyright 2022 Google LLC
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


#  [START aiplatform_sdk_import_feature_values_sample]
import datetime
from typing import List, Union

from google.cloud import aiplatform


def import_feature_values_sample(
    project: str,
    location: str,
    entity_type_id: str,
    featurestore_id: str,
    feature_ids: List[str],
    feature_time: Union[str, datetime.datetime],
    gcs_source_uris: Union[str, List[str]],
    gcs_source_type: str,
):

    aiplatform.init(project=project, location=location)

    my_entity_type = aiplatform.featurestore.EntityType(
        entity_type_name=entity_type_id, featurestore_id=featurestore_id
    )

    my_entity_type.ingest_from_gcs(
        feature_ids=feature_ids,
        feature_time=feature_time,
        gcs_source_uris=gcs_source_uris,
        gcs_source_type=gcs_source_type,
    )


#  [END aiplatform_sdk_import_feature_values_sample]
