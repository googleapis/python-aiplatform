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

def read_file(filename):
    with open(filename, 'rb') as f:
        file_content = f.read()
    return file_content


def b64_encode(content):
    return base64.b64encode(content).decode("utf-8")


def to_protobuf_value(d):
    return json_format.ParseDict(d, Value())
