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
SUPPORTED_REGIONS = ("us-central1", "europe-west4", "asia-east1")
PROD_API_ENDPOINT = "aiplatform.googleapis.com"

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
