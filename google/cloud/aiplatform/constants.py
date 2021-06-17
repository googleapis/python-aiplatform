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

DEFAULT_REGION = "us-central1"
SUPPORTED_REGIONS = {
    "asia-east1",
    "asia-northeast1",
    "asia-northeast3",
    "asia-southeast1",
    "australia-southeast1",
    "europe-west1",
    "europe-west2",
    "europe-west4",
    "northamerica-northeast1",
    "us-central1",
    "us-east1",
    "us-east4",
    "us-west1",
}

API_BASE_PATH = "aiplatform.googleapis.com"
PREDICTION_API_BASE_PATH = API_BASE_PATH

# Batch Prediction
BATCH_PREDICTION_INPUT_STORAGE_FORMATS = (
    "jsonl",
    "csv",
    "tf-record",
    "tf-record-gzip",
    "bigquery",
    "file-list",
)
BATCH_PREDICTION_OUTPUT_STORAGE_FORMATS = ("jsonl", "csv", "bigquery")

MOBILE_TF_MODEL_TYPES = {
    "MOBILE_TF_LOW_LATENCY_1",
    "MOBILE_TF_VERSATILE_1",
    "MOBILE_TF_HIGH_ACCURACY_1",
}

# TODO(b/177079208): Use EPCL Enums for validating Model Types
# Defined by gs://google-cloud-aiplatform/schema/trainingjob/definition/automl_image_*
# Format: "prediction_type": set() of model_type's
#
# NOTE: When adding a new prediction_type's, ensure it fits the pattern
#       "automl_image_{prediction_type}_*" used by the YAML schemas on GCS
AUTOML_IMAGE_PREDICTION_MODEL_TYPES = {
    "classification": {"CLOUD"} | MOBILE_TF_MODEL_TYPES,
    "object_detection": {"CLOUD_HIGH_ACCURACY_1", "CLOUD_LOW_LATENCY_1"}
    | MOBILE_TF_MODEL_TYPES,
}

AUTOML_VIDEO_PREDICTION_MODEL_TYPES = {
    "classification": {"CLOUD"} | {"MOBILE_VERSATILE_1"},
    "action_recognition": {"CLOUD"} | {"MOBILE_VERSATILE_1"},
    "object_tracking": {"CLOUD"}
    | {
        "MOBILE_VERSATILE_1",
        "MOBILE_CORAL_VERSATILE_1",
        "MOBILE_CORAL_LOW_LATENCY_1",
        "MOBILE_JETSON_VERSATILE_1",
        "MOBILE_JETSON_LOW_LATENCY_1",
    },
}

# Used in constructing the requests user_agent header for metrics reporting.
USER_AGENT_PRODUCT = "model-builder"
