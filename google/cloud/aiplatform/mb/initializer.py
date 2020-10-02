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

from typing import Optional

class Init:

	def __init__(self):
		self.project = None
		self.experiment = None
		self.location = None
		self.staging_bucket = None

	def init(self, project: Optional[str] = None, location: Optional[str] = None,
		experiment: Optional[str] = None, staging_bucket: Optional[str] = None):
		if project:
			self.project=project
		if location:
			self.location=location
		if experiment:
			self.experiment=experiment
		if staging_bucket:
			self.staging_bucket=staging_bucket

# singleton to store init parameters: ie, aiplatform.init(project=..., location=...)
singleton = Init()
