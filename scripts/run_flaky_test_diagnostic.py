# Copyright 2022 Google LLC
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

import os
import pathlib
import sys

# Run test in snippets directory:
dir_of_curr_file = os.path.dirname(__file__)
helper_filepath = pathlib.Path(dir_of_curr_file).parent / 'samples' / 'snippets'
sys.path.append(helper_filepath.resolve().as_posix())
os.chdir(helper_filepath.resolve())
from helpers import flaky_test_diagnostic

# Settings:
file_name = 'pipeline_service/create_training_pipeline_tabular_regression_sample_test.py'
test_name = 'test_ucaip_generated_create_training_pipeline_sample'
timing_dict = flaky_test_diagnostic(file_name, test_name, N=1)

for key, delta_list in timing_dict.items():
    mean_time = sum(delta_list)/len(delta_list)
    max_time = max(delta_list)
    min_time = min(delta_list)
    report_string = f'Result: {key}, mean={mean_time:3.2f}, min={min_time:3.2f}, max={max_time:3.2f}, count={len(delta_list)}'
    print(report_string)
