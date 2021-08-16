# Copyright 2020 Google LLC
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

import os


import predict_tabular_regression_sample

ENDPOINT_ID = "1014154341088493568"  # bq all
PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")

INSTANCE = {
    "BOOLEAN_2unique_NULLABLE": False,
    "DATETIME_1unique_NULLABLE": "2019-01-01 00:00:00",
    "DATE_1unique_NULLABLE": "2019-01-01",
    "FLOAT_5000unique_NULLABLE": 1611,
    "FLOAT_5000unique_REPEATED": [2320, 1192],
    "INTEGER_5000unique_NULLABLE": "8",
    "NUMERIC_5000unique_NULLABLE": 16,
    "STRING_5000unique_NULLABLE": "str-2",
    "STRUCT_NULLABLE": {
        "BOOLEAN_2unique_NULLABLE": False,
        "DATE_1unique_NULLABLE": "2019-01-01",
        "DATETIME_1unique_NULLABLE": "2019-01-01 00:00:00",
        "FLOAT_5000unique_NULLABLE": 1308,
        "FLOAT_5000unique_REPEATED": [2323, 1178],
        "FLOAT_5000unique_REQUIRED": 3089,
        "INTEGER_5000unique_NULLABLE": "1777",
        "NUMERIC_5000unique_NULLABLE": 3323,
        "TIME_1unique_NULLABLE": "23:59:59.999999",
        "STRING_5000unique_NULLABLE": "str-49",
        "TIMESTAMP_1unique_NULLABLE": "1546387199999999",
    },
    "TIMESTAMP_1unique_NULLABLE": "1546387199999999",
    "TIME_1unique_NULLABLE": "23:59:59.999999",
}


def test_ucaip_generated_predict_tabular_regression_sample(capsys):

    predict_tabular_regression_sample.predict_tabular_regression_sample(
        instance_dict=INSTANCE, project=PROJECT_ID, endpoint_id=ENDPOINT_ID
    )

    out, _ = capsys.readouterr()
    assert "prediction:" in out
