# -*- coding: utf-8 -*-
# Copyright 2025 Google LLC
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
import json  # type: ignore
from google.api_core import path_template
from google.api_core import gapic_v1

from google.protobuf import json_format
from google.iam.v1 import iam_policy_pb2  # type: ignore
from google.iam.v1 import policy_pb2  # type: ignore
from google.cloud.location import locations_pb2  # type: ignore
from .base import NotebookServiceTransport, DEFAULT_CLIENT_INFO

import re
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union


from google.cloud.aiplatform_v1beta1.types import notebook_execution_job
from google.cloud.aiplatform_v1beta1.types import notebook_runtime
from google.cloud.aiplatform_v1beta1.types import notebook_service
from google.longrunning import operations_pb2  # type: ignore


class _BaseNotebookServiceRestTransport(NotebookServiceTransport):
    """Base REST backend transport for NotebookService.

    Note: This class is not meant to be used directly. Use its sync and
    async sub-classes instead.

    This class defines the same methods as the primary client, so the
    primary client can load the underlying transport implementation
    and call it.

    It sends JSON representations of protocol buffers over HTTP/1.1
    """

    def __init__(
        self,
        *,
        host: str = "aiplatform.googleapis.com",
        credentials: Optional[Any] = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
        always_use_jwt_access: Optional[bool] = False,
        url_scheme: str = "https",
        api_audience: Optional[str] = None,
    ) -> None:
        """Instantiate the transport.
        Args:
            host (Optional[str]):
                 The hostname to connect to (default: 'aiplatform.googleapis.com').
            credentials (Optional[Any]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            client_info (google.api_core.gapic_v1.client_info.ClientInfo):
                The client info used to send a user-agent string along with
                API requests. If ``None``, then default info will be used.
                Generally, you only need to set this if you are developing
                your own client library.
            always_use_jwt_access (Optional[bool]): Whether self signed JWT should
                be used for service account credentials.
            url_scheme: the protocol scheme for the API endpoint.  Normally
                "https", but for testing or local servers,
                "http" can be specified.
        """
        # Run the base constructor
        maybe_url_match = re.match("^(?P<scheme>http(?:s)?://)?(?P<host>.*)$", host)
        if maybe_url_match is None:
            raise ValueError(
                f"Unexpected hostname structure: {host}"
            )  # pragma: NO COVER

        url_match_items = maybe_url_match.groupdict()

        host = f"{url_scheme}://{host}" if not url_match_items["scheme"] else host

        super().__init__(
            host=host,
            credentials=credentials,
            client_info=client_info,
            always_use_jwt_access=always_use_jwt_access,
            api_audience=api_audience,
        )

    class _BaseAssignNotebookRuntime:
        def __hash__(self):  # pragma: NO COVER
            return NotImplementedError("__hash__ must be implemented.")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        @staticmethod
        def _get_http_options():
            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/v1beta1/{parent=projects/*/locations/*}/notebookRuntimes:assign",
                    "body": "*",
                },
            ]
            return http_options

        @staticmethod
        def _get_transcoded_request(http_options, request):
            pb_request = notebook_service.AssignNotebookRuntimeRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)
            return transcoded_request

        @staticmethod
        def _get_request_body_json(transcoded_request):
            # Jsonify the request body

            body = json_format.MessageToJson(
                transcoded_request["body"], use_integers_for_enums=True
            )
            return body

        @staticmethod
        def _get_query_params_json(transcoded_request):
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=True,
                )
            )
            query_params.update(
                _BaseNotebookServiceRestTransport._BaseAssignNotebookRuntime._get_unset_required_fields(
                    query_params
                )
            )

            query_params["$alt"] = "json;enum-encoding=int"
            return query_params

    class _BaseCreateNotebookExecutionJob:
        def __hash__(self):  # pragma: NO COVER
            return NotImplementedError("__hash__ must be implemented.")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        @staticmethod
        def _get_http_options():
            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/v1beta1/{parent=projects/*/locations/*}/notebookExecutionJobs",
                    "body": "notebook_execution_job",
                },
            ]
            return http_options

        @staticmethod
        def _get_transcoded_request(http_options, request):
            pb_request = notebook_service.CreateNotebookExecutionJobRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)
            return transcoded_request

        @staticmethod
        def _get_request_body_json(transcoded_request):
            # Jsonify the request body

            body = json_format.MessageToJson(
                transcoded_request["body"], use_integers_for_enums=True
            )
            return body

        @staticmethod
        def _get_query_params_json(transcoded_request):
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=True,
                )
            )
            query_params.update(
                _BaseNotebookServiceRestTransport._BaseCreateNotebookExecutionJob._get_unset_required_fields(
                    query_params
                )
            )

            query_params["$alt"] = "json;enum-encoding=int"
            return query_params

    class _BaseCreateNotebookRuntimeTemplate:
        def __hash__(self):  # pragma: NO COVER
            return NotImplementedError("__hash__ must be implemented.")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        @staticmethod
        def _get_http_options():
            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/v1beta1/{parent=projects/*/locations/*}/notebookRuntimeTemplates",
                    "body": "notebook_runtime_template",
                },
            ]
            return http_options

        @staticmethod
        def _get_transcoded_request(http_options, request):
            pb_request = notebook_service.CreateNotebookRuntimeTemplateRequest.pb(
                request
            )
            transcoded_request = path_template.transcode(http_options, pb_request)
            return transcoded_request

        @staticmethod
        def _get_request_body_json(transcoded_request):
            # Jsonify the request body

            body = json_format.MessageToJson(
                transcoded_request["body"], use_integers_for_enums=True
            )
            return body

        @staticmethod
        def _get_query_params_json(transcoded_request):
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=True,
                )
            )
            query_params.update(
                _BaseNotebookServiceRestTransport._BaseCreateNotebookRuntimeTemplate._get_unset_required_fields(
                    query_params
                )
            )

            query_params["$alt"] = "json;enum-encoding=int"
            return query_params

    class _BaseDeleteNotebookExecutionJob:
        def __hash__(self):  # pragma: NO COVER
            return NotImplementedError("__hash__ must be implemented.")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        @staticmethod
        def _get_http_options():
            http_options: List[Dict[str, str]] = [
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/notebookExecutionJobs/*}",
                },
            ]
            return http_options

        @staticmethod
        def _get_transcoded_request(http_options, request):
            pb_request = notebook_service.DeleteNotebookExecutionJobRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)
            return transcoded_request

        @staticmethod
        def _get_query_params_json(transcoded_request):
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=True,
                )
            )
            query_params.update(
                _BaseNotebookServiceRestTransport._BaseDeleteNotebookExecutionJob._get_unset_required_fields(
                    query_params
                )
            )

            query_params["$alt"] = "json;enum-encoding=int"
            return query_params

    class _BaseDeleteNotebookRuntime:
        def __hash__(self):  # pragma: NO COVER
            return NotImplementedError("__hash__ must be implemented.")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        @staticmethod
        def _get_http_options():
            http_options: List[Dict[str, str]] = [
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/notebookRuntimes/*}",
                },
            ]
            return http_options

        @staticmethod
        def _get_transcoded_request(http_options, request):
            pb_request = notebook_service.DeleteNotebookRuntimeRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)
            return transcoded_request

        @staticmethod
        def _get_query_params_json(transcoded_request):
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=True,
                )
            )
            query_params.update(
                _BaseNotebookServiceRestTransport._BaseDeleteNotebookRuntime._get_unset_required_fields(
                    query_params
                )
            )

            query_params["$alt"] = "json;enum-encoding=int"
            return query_params

    class _BaseDeleteNotebookRuntimeTemplate:
        def __hash__(self):  # pragma: NO COVER
            return NotImplementedError("__hash__ must be implemented.")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        @staticmethod
        def _get_http_options():
            http_options: List[Dict[str, str]] = [
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/notebookRuntimeTemplates/*}",
                },
            ]
            return http_options

        @staticmethod
        def _get_transcoded_request(http_options, request):
            pb_request = notebook_service.DeleteNotebookRuntimeTemplateRequest.pb(
                request
            )
            transcoded_request = path_template.transcode(http_options, pb_request)
            return transcoded_request

        @staticmethod
        def _get_query_params_json(transcoded_request):
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=True,
                )
            )
            query_params.update(
                _BaseNotebookServiceRestTransport._BaseDeleteNotebookRuntimeTemplate._get_unset_required_fields(
                    query_params
                )
            )

            query_params["$alt"] = "json;enum-encoding=int"
            return query_params

    class _BaseGetNotebookExecutionJob:
        def __hash__(self):  # pragma: NO COVER
            return NotImplementedError("__hash__ must be implemented.")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        @staticmethod
        def _get_http_options():
            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/notebookExecutionJobs/*}",
                },
            ]
            return http_options

        @staticmethod
        def _get_transcoded_request(http_options, request):
            pb_request = notebook_service.GetNotebookExecutionJobRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)
            return transcoded_request

        @staticmethod
        def _get_query_params_json(transcoded_request):
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=True,
                )
            )
            query_params.update(
                _BaseNotebookServiceRestTransport._BaseGetNotebookExecutionJob._get_unset_required_fields(
                    query_params
                )
            )

            query_params["$alt"] = "json;enum-encoding=int"
            return query_params

    class _BaseGetNotebookRuntime:
        def __hash__(self):  # pragma: NO COVER
            return NotImplementedError("__hash__ must be implemented.")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        @staticmethod
        def _get_http_options():
            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/notebookRuntimes/*}",
                },
            ]
            return http_options

        @staticmethod
        def _get_transcoded_request(http_options, request):
            pb_request = notebook_service.GetNotebookRuntimeRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)
            return transcoded_request

        @staticmethod
        def _get_query_params_json(transcoded_request):
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=True,
                )
            )
            query_params.update(
                _BaseNotebookServiceRestTransport._BaseGetNotebookRuntime._get_unset_required_fields(
                    query_params
                )
            )

            query_params["$alt"] = "json;enum-encoding=int"
            return query_params

    class _BaseGetNotebookRuntimeTemplate:
        def __hash__(self):  # pragma: NO COVER
            return NotImplementedError("__hash__ must be implemented.")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        @staticmethod
        def _get_http_options():
            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/notebookRuntimeTemplates/*}",
                },
            ]
            return http_options

        @staticmethod
        def _get_transcoded_request(http_options, request):
            pb_request = notebook_service.GetNotebookRuntimeTemplateRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)
            return transcoded_request

        @staticmethod
        def _get_query_params_json(transcoded_request):
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=True,
                )
            )
            query_params.update(
                _BaseNotebookServiceRestTransport._BaseGetNotebookRuntimeTemplate._get_unset_required_fields(
                    query_params
                )
            )

            query_params["$alt"] = "json;enum-encoding=int"
            return query_params

    class _BaseListNotebookExecutionJobs:
        def __hash__(self):  # pragma: NO COVER
            return NotImplementedError("__hash__ must be implemented.")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        @staticmethod
        def _get_http_options():
            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/v1beta1/{parent=projects/*/locations/*}/notebookExecutionJobs",
                },
            ]
            return http_options

        @staticmethod
        def _get_transcoded_request(http_options, request):
            pb_request = notebook_service.ListNotebookExecutionJobsRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)
            return transcoded_request

        @staticmethod
        def _get_query_params_json(transcoded_request):
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=True,
                )
            )
            query_params.update(
                _BaseNotebookServiceRestTransport._BaseListNotebookExecutionJobs._get_unset_required_fields(
                    query_params
                )
            )

            query_params["$alt"] = "json;enum-encoding=int"
            return query_params

    class _BaseListNotebookRuntimes:
        def __hash__(self):  # pragma: NO COVER
            return NotImplementedError("__hash__ must be implemented.")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        @staticmethod
        def _get_http_options():
            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/v1beta1/{parent=projects/*/locations/*}/notebookRuntimes",
                },
            ]
            return http_options

        @staticmethod
        def _get_transcoded_request(http_options, request):
            pb_request = notebook_service.ListNotebookRuntimesRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)
            return transcoded_request

        @staticmethod
        def _get_query_params_json(transcoded_request):
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=True,
                )
            )
            query_params.update(
                _BaseNotebookServiceRestTransport._BaseListNotebookRuntimes._get_unset_required_fields(
                    query_params
                )
            )

            query_params["$alt"] = "json;enum-encoding=int"
            return query_params

    class _BaseListNotebookRuntimeTemplates:
        def __hash__(self):  # pragma: NO COVER
            return NotImplementedError("__hash__ must be implemented.")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        @staticmethod
        def _get_http_options():
            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/v1beta1/{parent=projects/*/locations/*}/notebookRuntimeTemplates",
                },
            ]
            return http_options

        @staticmethod
        def _get_transcoded_request(http_options, request):
            pb_request = notebook_service.ListNotebookRuntimeTemplatesRequest.pb(
                request
            )
            transcoded_request = path_template.transcode(http_options, pb_request)
            return transcoded_request

        @staticmethod
        def _get_query_params_json(transcoded_request):
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=True,
                )
            )
            query_params.update(
                _BaseNotebookServiceRestTransport._BaseListNotebookRuntimeTemplates._get_unset_required_fields(
                    query_params
                )
            )

            query_params["$alt"] = "json;enum-encoding=int"
            return query_params

    class _BaseStartNotebookRuntime:
        def __hash__(self):  # pragma: NO COVER
            return NotImplementedError("__hash__ must be implemented.")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        @staticmethod
        def _get_http_options():
            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/notebookRuntimes/*}:start",
                    "body": "*",
                },
            ]
            return http_options

        @staticmethod
        def _get_transcoded_request(http_options, request):
            pb_request = notebook_service.StartNotebookRuntimeRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)
            return transcoded_request

        @staticmethod
        def _get_request_body_json(transcoded_request):
            # Jsonify the request body

            body = json_format.MessageToJson(
                transcoded_request["body"], use_integers_for_enums=True
            )
            return body

        @staticmethod
        def _get_query_params_json(transcoded_request):
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=True,
                )
            )
            query_params.update(
                _BaseNotebookServiceRestTransport._BaseStartNotebookRuntime._get_unset_required_fields(
                    query_params
                )
            )

            query_params["$alt"] = "json;enum-encoding=int"
            return query_params

    class _BaseStopNotebookRuntime:
        def __hash__(self):  # pragma: NO COVER
            return NotImplementedError("__hash__ must be implemented.")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        @staticmethod
        def _get_http_options():
            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/notebookRuntimes/*}:stop",
                    "body": "*",
                },
            ]
            return http_options

        @staticmethod
        def _get_transcoded_request(http_options, request):
            pb_request = notebook_service.StopNotebookRuntimeRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)
            return transcoded_request

        @staticmethod
        def _get_request_body_json(transcoded_request):
            # Jsonify the request body

            body = json_format.MessageToJson(
                transcoded_request["body"], use_integers_for_enums=True
            )
            return body

        @staticmethod
        def _get_query_params_json(transcoded_request):
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=True,
                )
            )
            query_params.update(
                _BaseNotebookServiceRestTransport._BaseStopNotebookRuntime._get_unset_required_fields(
                    query_params
                )
            )

            query_params["$alt"] = "json;enum-encoding=int"
            return query_params

    class _BaseUpdateNotebookRuntimeTemplate:
        def __hash__(self):  # pragma: NO COVER
            return NotImplementedError("__hash__ must be implemented.")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {
            "updateMask": {},
        }

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        @staticmethod
        def _get_http_options():
            http_options: List[Dict[str, str]] = [
                {
                    "method": "patch",
                    "uri": "/v1beta1/{notebook_runtime_template.name=projects/*/locations/*/notebookRuntimeTemplates/*}",
                    "body": "notebook_runtime_template",
                },
            ]
            return http_options

        @staticmethod
        def _get_transcoded_request(http_options, request):
            pb_request = notebook_service.UpdateNotebookRuntimeTemplateRequest.pb(
                request
            )
            transcoded_request = path_template.transcode(http_options, pb_request)
            return transcoded_request

        @staticmethod
        def _get_request_body_json(transcoded_request):
            # Jsonify the request body

            body = json_format.MessageToJson(
                transcoded_request["body"], use_integers_for_enums=True
            )
            return body

        @staticmethod
        def _get_query_params_json(transcoded_request):
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=True,
                )
            )
            query_params.update(
                _BaseNotebookServiceRestTransport._BaseUpdateNotebookRuntimeTemplate._get_unset_required_fields(
                    query_params
                )
            )

            query_params["$alt"] = "json;enum-encoding=int"
            return query_params

    class _BaseUpgradeNotebookRuntime:
        def __hash__(self):  # pragma: NO COVER
            return NotImplementedError("__hash__ must be implemented.")

        __REQUIRED_FIELDS_DEFAULT_VALUES: Dict[str, Any] = {}

        @classmethod
        def _get_unset_required_fields(cls, message_dict):
            return {
                k: v
                for k, v in cls.__REQUIRED_FIELDS_DEFAULT_VALUES.items()
                if k not in message_dict
            }

        @staticmethod
        def _get_http_options():
            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/notebookRuntimes/*}:upgrade",
                    "body": "*",
                },
            ]
            return http_options

        @staticmethod
        def _get_transcoded_request(http_options, request):
            pb_request = notebook_service.UpgradeNotebookRuntimeRequest.pb(request)
            transcoded_request = path_template.transcode(http_options, pb_request)
            return transcoded_request

        @staticmethod
        def _get_request_body_json(transcoded_request):
            # Jsonify the request body

            body = json_format.MessageToJson(
                transcoded_request["body"], use_integers_for_enums=True
            )
            return body

        @staticmethod
        def _get_query_params_json(transcoded_request):
            query_params = json.loads(
                json_format.MessageToJson(
                    transcoded_request["query_params"],
                    use_integers_for_enums=True,
                )
            )
            query_params.update(
                _BaseNotebookServiceRestTransport._BaseUpgradeNotebookRuntime._get_unset_required_fields(
                    query_params
                )
            )

            query_params["$alt"] = "json;enum-encoding=int"
            return query_params

    class _BaseGetLocation:
        def __hash__(self):  # pragma: NO COVER
            return NotImplementedError("__hash__ must be implemented.")

        @staticmethod
        def _get_http_options():
            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*}",
                },
            ]
            return http_options

        @staticmethod
        def _get_transcoded_request(http_options, request):
            request_kwargs = json_format.MessageToDict(request)
            transcoded_request = path_template.transcode(http_options, **request_kwargs)
            return transcoded_request

        @staticmethod
        def _get_query_params_json(transcoded_request):
            query_params = json.loads(json.dumps(transcoded_request["query_params"]))
            return query_params

    class _BaseListLocations:
        def __hash__(self):  # pragma: NO COVER
            return NotImplementedError("__hash__ must be implemented.")

        @staticmethod
        def _get_http_options():
            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*}/locations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*}/locations",
                },
            ]
            return http_options

        @staticmethod
        def _get_transcoded_request(http_options, request):
            request_kwargs = json_format.MessageToDict(request)
            transcoded_request = path_template.transcode(http_options, **request_kwargs)
            return transcoded_request

        @staticmethod
        def _get_query_params_json(transcoded_request):
            query_params = json.loads(json.dumps(transcoded_request["query_params"]))
            return query_params

    class _BaseGetIamPolicy:
        def __hash__(self):  # pragma: NO COVER
            return NotImplementedError("__hash__ must be implemented.")

        @staticmethod
        def _get_http_options():
            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/v1beta1/{resource=projects/*/locations/*/featurestores/*}:getIamPolicy",
                    "body": "*",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{resource=projects/*/locations/*/featurestores/*/entityTypes/*}:getIamPolicy",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{resource=projects/*/locations/*/models/*}:getIamPolicy",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{resource=projects/*/locations/*/endpoints/*}:getIamPolicy",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{resource=projects/*/locations/*/notebookRuntimeTemplates/*}:getIamPolicy",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{resource=projects/*/locations/*/publishers/*/models/*}:getIamPolicy",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{resource=projects/*/locations/*/featureOnlineStores/*}:getIamPolicy",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{resource=projects/*/locations/*/featureOnlineStores/*/featureViews/*}:getIamPolicy",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{resource=projects/*/locations/*/featureGroups/*}:getIamPolicy",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/featurestores/*}:getIamPolicy",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/featurestores/*/entityTypes/*}:getIamPolicy",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/models/*}:getIamPolicy",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/endpoints/*}:getIamPolicy",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/notebookRuntimeTemplates/*}:getIamPolicy",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/publishers/*/models/*}:getIamPolicy",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/featureOnlineStores/*}:getIamPolicy",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/featureOnlineStores/*/featureViews/*}:getIamPolicy",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/featureGroups/*}:getIamPolicy",
                },
            ]
            return http_options

        @staticmethod
        def _get_transcoded_request(http_options, request):
            request_kwargs = json_format.MessageToDict(request)
            transcoded_request = path_template.transcode(http_options, **request_kwargs)
            return transcoded_request

        @staticmethod
        def _get_request_body_json(transcoded_request):
            body = json.dumps(transcoded_request["body"])
            return body

        @staticmethod
        def _get_query_params_json(transcoded_request):
            query_params = json.loads(json.dumps(transcoded_request["query_params"]))
            return query_params

    class _BaseSetIamPolicy:
        def __hash__(self):  # pragma: NO COVER
            return NotImplementedError("__hash__ must be implemented.")

        @staticmethod
        def _get_http_options():
            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/v1beta1/{resource=projects/*/locations/*/featurestores/*}:setIamPolicy",
                    "body": "*",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{resource=projects/*/locations/*/featurestores/*/entityTypes/*}:setIamPolicy",
                    "body": "*",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{resource=projects/*/locations/*/models/*}:setIamPolicy",
                    "body": "*",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{resource=projects/*/locations/*/endpoints/*}:setIamPolicy",
                    "body": "*",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{resource=projects/*/locations/*/notebookRuntimeTemplates/*}:setIamPolicy",
                    "body": "*",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{resource=projects/*/locations/*/featureOnlineStores/*}:setIamPolicy",
                    "body": "*",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{resource=projects/*/locations/*/featureOnlineStores/*/featureViews/*}:setIamPolicy",
                    "body": "*",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{resource=projects/*/locations/*/featureGroups/*}:setIamPolicy",
                    "body": "*",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/featurestores/*}:setIamPolicy",
                    "body": "*",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/featurestores/*/entityTypes/*}:setIamPolicy",
                    "body": "*",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/models/*}:setIamPolicy",
                    "body": "*",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/endpoints/*}:setIamPolicy",
                    "body": "*",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/notebookRuntimeTemplates/*}:setIamPolicy",
                    "body": "*",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/featureOnlineStores/*}:setIamPolicy",
                    "body": "*",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/featureOnlineStores/*/featureViews/*}:setIamPolicy",
                    "body": "*",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/featureGroups/*}:setIamPolicy",
                    "body": "*",
                },
            ]
            return http_options

        @staticmethod
        def _get_transcoded_request(http_options, request):
            request_kwargs = json_format.MessageToDict(request)
            transcoded_request = path_template.transcode(http_options, **request_kwargs)
            return transcoded_request

        @staticmethod
        def _get_request_body_json(transcoded_request):
            body = json.dumps(transcoded_request["body"])
            return body

        @staticmethod
        def _get_query_params_json(transcoded_request):
            query_params = json.loads(json.dumps(transcoded_request["query_params"]))
            return query_params

    class _BaseTestIamPermissions:
        def __hash__(self):  # pragma: NO COVER
            return NotImplementedError("__hash__ must be implemented.")

        @staticmethod
        def _get_http_options():
            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/v1beta1/{resource=projects/*/locations/*/featurestores/*}:testIamPermissions",
                    "body": "*",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{resource=projects/*/locations/*/featurestores/*/entityTypes/*}:testIamPermissions",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{resource=projects/*/locations/*/models/*}:testIamPermissions",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{resource=projects/*/locations/*/endpoints/*}:testIamPermissions",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{resource=projects/*/locations/*/notebookRuntimeTemplates/*}:testIamPermissions",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{resource=projects/*/locations/*/featureOnlineStores/*}:testIamPermissions",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{resource=projects/*/locations/*/featureOnlineStores/*/featureViews/*}:testIamPermissions",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{resource=projects/*/locations/*/featureGroups/*}:testIamPermissions",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/featurestores/*}:testIamPermissions",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/featurestores/*/entityTypes/*}:testIamPermissions",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/models/*}:testIamPermissions",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/endpoints/*}:testIamPermissions",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/notebookRuntimeTemplates/*}:testIamPermissions",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/featureOnlineStores/*}:testIamPermissions",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/featureOnlineStores/*/featureViews/*}:testIamPermissions",
                },
                {
                    "method": "post",
                    "uri": "/ui/{resource=projects/*/locations/*/featureGroups/*}:testIamPermissions",
                },
            ]
            return http_options

        @staticmethod
        def _get_transcoded_request(http_options, request):
            request_kwargs = json_format.MessageToDict(request)
            transcoded_request = path_template.transcode(http_options, **request_kwargs)
            return transcoded_request

        @staticmethod
        def _get_request_body_json(transcoded_request):
            body = json.dumps(transcoded_request["body"])
            return body

        @staticmethod
        def _get_query_params_json(transcoded_request):
            query_params = json.loads(json.dumps(transcoded_request["query_params"]))
            return query_params

    class _BaseCancelOperation:
        def __hash__(self):  # pragma: NO COVER
            return NotImplementedError("__hash__ must be implemented.")

        @staticmethod
        def _get_http_options():
            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/agents/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/apps/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/edgeDevices/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/endpoints/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/extensionControllers/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/extensions/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/customJobs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/tuningJobs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/indexes/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/indexEndpoints/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/modelMonitors/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/migratableResources/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/models/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/persistentResources/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/studies/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/studies/*/trials/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/trainingPipelines/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/pipelineJobs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/schedules/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/ragEngineConfig/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/specialistPools/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/agents/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/apps/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/datasets/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/edgeDevices/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/endpoints/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/exampleStores/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/extensionControllers/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/extensions/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featurestores/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/customJobs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/indexes/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/indexEndpoints/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/metadataStores/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/modelMonitors/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/migratableResources/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/models/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/persistentResources/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/ragEngineConfig/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/ragCorpora/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/ragCorpora/*/ragFiles/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/studies/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/studies/*/trials/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/trainingPipelines/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/pipelineJobs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/reasoningEngines/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/reasoningEngines/*/memories/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/reasoningEngines/*/sessions/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/schedules/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/specialistPools/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/tensorboards/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}:cancel",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}:cancel",
                },
            ]
            return http_options

        @staticmethod
        def _get_transcoded_request(http_options, request):
            request_kwargs = json_format.MessageToDict(request)
            transcoded_request = path_template.transcode(http_options, **request_kwargs)
            return transcoded_request

        @staticmethod
        def _get_query_params_json(transcoded_request):
            query_params = json.loads(json.dumps(transcoded_request["query_params"]))
            return query_params

    class _BaseDeleteOperation:
        def __hash__(self):  # pragma: NO COVER
            return NotImplementedError("__hash__ must be implemented.")

        @staticmethod
        def _get_http_options():
            http_options: List[Dict[str, str]] = [
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/agents/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/apps/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/edgeDevices/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/endpoints/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/extensionControllers/*}/operations",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/extensions/*}/operations",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/customJobs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/indexes/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/indexEndpoints/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/modelMonitors/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/migratableResources/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/models/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/persistentResources/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/studies/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/studies/*/trials/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/trainingPipelines/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/pipelineJobs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/schedules/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/specialistPools/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/ragEngineConfig/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/featureMonitors/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/agents/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/apps/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/datasets/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/edgeDevices/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/endpoints/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featurestores/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/customJobs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/evaluationTasks/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/exampleStores/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/extensionControllers/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/extensions/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/indexes/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/indexEndpoints/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/metadataStores/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/modelMonitors/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/migratableResources/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/models/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/persistentResources/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/ragEngineConfig/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/ragCorpora/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/ragCorpora/*/ragFiles/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/reasoningEngines/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/reasoningEngines/*/memories/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/reasoningEngines/*/sessions/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/solvers/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/studies/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/studies/*/trials/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/trainingPipelines/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/pipelineJobs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/schedules/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/specialistPools/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/tensorboards/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featureGroups/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featureGroups/*/featureMonitors/*/operations/*}",
                },
                {
                    "method": "delete",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}",
                },
            ]
            return http_options

        @staticmethod
        def _get_transcoded_request(http_options, request):
            request_kwargs = json_format.MessageToDict(request)
            transcoded_request = path_template.transcode(http_options, **request_kwargs)
            return transcoded_request

        @staticmethod
        def _get_query_params_json(transcoded_request):
            query_params = json.loads(json.dumps(transcoded_request["query_params"]))
            return query_params

    class _BaseGetOperation:
        def __hash__(self):  # pragma: NO COVER
            return NotImplementedError("__hash__ must be implemented.")

        @staticmethod
        def _get_http_options():
            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/agents/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/apps/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/edgeDeploymentJobs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/edgeDevices/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/endpoints/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/extensionControllers/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/extensions/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/customJobs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/tuningJobs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/indexes/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/indexEndpoints/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/modelMonitors/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/migratableResources/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/models/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/persistentResources/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/studies/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/studies/*/trials/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/trainingPipelines/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/pipelineJobs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/ragEngineConfig/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/schedules/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/specialistPools/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/featureMonitors/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/agents/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/apps/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/datasets/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/edgeDevices/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/endpoints/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/evaluationTasks/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/exampleStores/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/extensionControllers/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/extensions/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featurestores/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/customJobs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/indexes/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/indexEndpoints/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/metadataStores/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/modelMonitors/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/migratableResources/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/models/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/persistentResources/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/ragEngineConfig/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/ragCorpora/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/ragCorpora/*/ragFiles/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/reasoningEngines/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/reasoningEngines/*/memories/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/reasoningEngines/*/sessions/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/solvers/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/studies/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/studies/*/trials/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/trainingPipelines/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/pipelineJobs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/schedules/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/specialistPools/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/tensorboards/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featureGroups/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featureGroups/*/featureMonitors/*/operations/*}",
                },
            ]
            return http_options

        @staticmethod
        def _get_transcoded_request(http_options, request):
            request_kwargs = json_format.MessageToDict(request)
            transcoded_request = path_template.transcode(http_options, **request_kwargs)
            return transcoded_request

        @staticmethod
        def _get_query_params_json(transcoded_request):
            query_params = json.loads(json.dumps(transcoded_request["query_params"]))
            return query_params

    class _BaseListOperations:
        def __hash__(self):  # pragma: NO COVER
            return NotImplementedError("__hash__ must be implemented.")

        @staticmethod
        def _get_http_options():
            http_options: List[Dict[str, str]] = [
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/agents/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/apps/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/savedQueries/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/annotationSpecs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/deploymentResourcePools/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/edgeDevices/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/endpoints/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/extensionControllers/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/extensions/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/customJobs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/dataLabelingJobs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/hyperparameterTuningJobs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/tuningJobs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/indexes/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/indexEndpoints/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/artifacts/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/contexts/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/executions/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/modelMonitors/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/migratableResources/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/models/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/models/*/evaluations/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/notebookExecutionJobs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/notebookRuntimes/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/notebookRuntimeTemplates/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/studies/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/studies/*/trials/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/trainingPipelines/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/persistentResources/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/pipelineJobs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/ragEngineConfig}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/schedules/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/specialistPools/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}:wait",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}:wait",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/operations/*}:wait",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}:wait",
                },
                {
                    "method": "get",
                    "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/featureMonitors/*/operations/*}:wait",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/agents/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/apps/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/datasets/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/datasets/*/dataItems/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/datasets/*/savedQueries/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/datasets/*/annotationSpecs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/deploymentResourcePools/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/edgeDevices/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/endpoints/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/evaluationTasks/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/exampleStores/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/extensionControllers/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/extensions/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featurestores/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featurestores/*/entityTypes/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/customJobs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/dataLabelingJobs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/hyperparameterTuningJobs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/indexes/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/indexEndpoints/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/metadataStores/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/metadataStores/*/artifacts/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/metadataStores/*/contexts/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/metadataStores/*/executions/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/modelMonitors/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/migratableResources/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/models/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/models/*/evaluations/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/notebookExecutionJobs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/notebookRuntimes/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/notebookRuntimeTemplates/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/persistentResources/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/ragEngineConfig}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/ragCorpora/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/ragCorpora/*/ragFiles/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/reasoningEngines/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/reasoningEngines/*/memories/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/reasoningEngines/*/sessions/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/solvers/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/studies/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/studies/*/trials/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/trainingPipelines/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/pipelineJobs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/schedules/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/specialistPools/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/tensorboards/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/tensorboards/*/experiments/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featureOnlineStores/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featureGroups/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featureGroups/*/features/*}/operations",
                },
                {
                    "method": "get",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featureGroups/*/featureMonitors/*}/operations",
                },
            ]
            return http_options

        @staticmethod
        def _get_transcoded_request(http_options, request):
            request_kwargs = json_format.MessageToDict(request)
            transcoded_request = path_template.transcode(http_options, **request_kwargs)
            return transcoded_request

        @staticmethod
        def _get_query_params_json(transcoded_request):
            query_params = json.loads(json.dumps(transcoded_request["query_params"]))
            return query_params

    class _BaseWaitOperation:
        def __hash__(self):  # pragma: NO COVER
            return NotImplementedError("__hash__ must be implemented.")

        @staticmethod
        def _get_http_options():
            http_options: List[Dict[str, str]] = [
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/agents/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/apps/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/edgeDevices/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/endpoints/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/extensionControllers/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/extensions/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/customJobs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/tuningJobs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/indexes/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/indexEndpoints/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/modelMonitors/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/migratableResources/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/models/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/studies/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/studies/*/trials/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/trainingPipelines/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/persistentResources/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/pipelineJobs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/schedules/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/specialistPools/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/ragEngineConfig/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/featureMonitors/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/agents/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/apps/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/datasets/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/edgeDevices/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/endpoints/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/evaluationTasks/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/exampleStores/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/extensionControllers/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/extensions/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featurestores/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/customJobs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/indexes/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/indexEndpoints/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/metadataStores/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/modelMonitors/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/migratableResources/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/models/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/persistentResources/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/ragEngineConfig/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/ragCorpora/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/ragCorpora/*/ragFiles/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/reasoningEngines/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/reasoningEngines/*/memories/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/reasoningEngines/*/sessions/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/studies/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/studies/*/trials/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/trainingPipelines/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/pipelineJobs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/schedules/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/specialistPools/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/tensorboards/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featureGroups/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}:wait",
                },
                {
                    "method": "post",
                    "uri": "/v1beta1/{name=projects/*/locations/*/featureGroups/*/featureMonitors/*/operations/*}:wait",
                },
            ]
            return http_options

        @staticmethod
        def _get_transcoded_request(http_options, request):
            request_kwargs = json_format.MessageToDict(request)
            transcoded_request = path_template.transcode(http_options, **request_kwargs)
            return transcoded_request

        @staticmethod
        def _get_query_params_json(transcoded_request):
            query_params = json.loads(json.dumps(transcoded_request["query_params"]))
            return query_params


__all__ = ("_BaseNotebookServiceRestTransport",)
