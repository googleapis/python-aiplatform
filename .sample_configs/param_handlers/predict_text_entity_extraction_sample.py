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

def make_endpoint(endpoint: str) -> str:
    endpoint = endpoint
    return endpoint

def make_instances(content: str) -> typing.Sequence[google.protobuf.struct_pb2.Value]:
    # The format of each instance should conform to the deployed model's prediction input schema
    instance_dict = {'content': content}
    instance = to_protobuf_value(instance_dict)
    instances = [instance]

    return instances

def make_parameters() -> google.protobuf.struct_pb2.Value:
    parameters_dict = {}
    parameters = to_protobuf_value(parameters_dict)

    return parameters

