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
    # Sample function parameter parent in batch_delete_data_items_sample
    parent = parent

    return parent

def make_names(data_item_name_1: str, data_item_name_2: str) -> typing.Sequence[str]:
    # The list of full name of data items in the same dataset to be deleted.
    names = [data_item_name_1, data_item_name_2]

    return names

