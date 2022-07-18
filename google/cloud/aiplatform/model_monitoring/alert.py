# -*- coding: utf-8 -*-

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

from typing import Optional, List
from google.cloud.aiplatform_v1.types import (
    model_monitoring as gca_model_monitoring,
)


class EmailAlertConfig:
    def __init__(
        self, user_emails: List[str] = [], enable_logging: Optional[bool] = False
    ):
        """Initializer for EmailAlertConfig.

        Args:
            user_emails (List[str]):
                The email addresses to send the alert to.
            enable_logging (bool):
                Optional. Defaults to False. Streams detected anomalies to Cloud Logging. The anomalies will be
                put into json payload encoded from proto
                [google.cloud.aiplatform.logging.ModelMonitoringAnomaliesLogEntry][].
                This can be further sync'd to Pub/Sub or any other services
                supported by Cloud Logging.
        """
        self.enable_logging = enable_logging
        self.user_emails = user_emails

    def as_proto(self):
        """Returns EmailAlertConfig as a proto message."""
        user_email_alert_config = (
            gca_model_monitoring.ModelMonitoringAlertConfig.EmailAlertConfig(
                user_emails=self.user_emails
            )
        )
        return gca_model_monitoring.ModelMonitoringAlertConfig(
            email_alert_config=user_email_alert_config,
            enable_logging=self.enable_logging,
        )
