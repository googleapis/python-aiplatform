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

import pytest
import requests
from unittest import mock

from google.cloud.aiplatform.compat.types import model as gca_model_compat
from google.cloud.aiplatform.constants import prediction
from google.cloud.aiplatform.docker_utils import run
from google.cloud.aiplatform.prediction import LocalModel
from google.cloud.aiplatform.prediction import LocalEndpoint


_TEST_IMAGE_URI = "test_image:latest"
_TEST_PREDICT_RESPONSE_CONTENT = b'{"x": [[1]]}'
_TEST_HEALTH_CHECK_RESPONSE_CONTENT = b"{}"
_TEST_HTTP_ERROR_MESSAGE = "HTTP Error Occurred."
_TEST_CONTAINER_LOGS_LEN = 5
_CONTAINER_RUNNING_STATUS = "running"
_CONTAINER_EXITED_STATUS = "exited"


@pytest.fixture
def local_endpoint_init_mock():
    with mock.patch.object(LocalEndpoint, "__init__") as local_endpoint_init_mock:
        local_endpoint_init_mock.return_value = None
        yield local_endpoint_init_mock


@pytest.fixture
def local_endpoint_enter_mock():
    with mock.patch.object(LocalEndpoint, "__enter__") as local_endpoint_enter_mock:
        yield local_endpoint_enter_mock


@pytest.fixture
def local_endpoint_exit_mock():
    with mock.patch.object(LocalEndpoint, "__exit__") as local_endpoint_exit_mock:
        yield local_endpoint_exit_mock


def get_docker_container_mock():
    container = mock.MagicMock()
    return container


@pytest.fixture
def run_prediction_container_mock():
    with mock.patch.object(
        run, "run_prediction_container"
    ) as run_prediction_container_mock:
        run_prediction_container_mock.return_value = get_docker_container_mock()
        yield run_prediction_container_mock


@pytest.fixture
def run_prediction_container_with_running_status_mock():
    with mock.patch.object(
        run, "run_prediction_container"
    ) as run_prediction_container_with_running_status_mock:
        run_prediction_container_with_running_status_mock.return_value = (
            get_docker_container_mock()
        )
        run_prediction_container_with_running_status_mock().status = (
            _CONTAINER_RUNNING_STATUS
        )
        yield run_prediction_container_with_running_status_mock


@pytest.fixture
def run_print_container_logs_mock():
    with mock.patch.object(
        run, "print_container_logs"
    ) as run_print_container_logs_mock:
        run_print_container_logs_mock.return_value = _TEST_CONTAINER_LOGS_LEN
        yield run_print_container_logs_mock


@pytest.fixture
def get_container_status_running_mock():
    with mock.patch.object(
        LocalEndpoint, "get_container_status"
    ) as get_container_status_running_mock:
        get_container_status_running_mock.return_value = _CONTAINER_RUNNING_STATUS
        yield get_container_status_running_mock


@pytest.fixture
def get_container_status_exited_mock():
    with mock.patch.object(
        LocalEndpoint, "get_container_status"
    ) as get_container_status_exited_mock:
        get_container_status_exited_mock.return_value = _CONTAINER_EXITED_STATUS
        yield get_container_status_exited_mock


@pytest.fixture
def local_endpoint_print_container_logs_mock():
    with mock.patch.object(
        LocalEndpoint, "print_container_logs"
    ) as local_endpoint_print_container_logs_mock:
        yield local_endpoint_print_container_logs_mock


@pytest.fixture
def wait_until_container_runs_mock():
    with mock.patch.object(
        LocalEndpoint, "_wait_until_container_runs"
    ) as wait_until_container_runs_mock:
        yield wait_until_container_runs_mock


@pytest.fixture
def wait_until_health_check_succeeds_mock():
    with mock.patch.object(
        LocalEndpoint, "_wait_until_health_check_succeeds"
    ) as wait_until_health_check_succeeds_mock:
        yield wait_until_health_check_succeeds_mock


@pytest.fixture
def stop_container_if_exists_mock():
    with mock.patch.object(
        LocalEndpoint, "_stop_container_if_exists"
    ) as stop_container_if_exists_mock:
        yield stop_container_if_exists_mock


def get_requests_post_response():
    response = requests.models.Response()
    response.status_code = 200
    response._content = _TEST_PREDICT_RESPONSE_CONTENT
    return response


@pytest.fixture
def requests_post_mock():
    with mock.patch.object(requests, "post") as requests_post_mock:
        requests_post_mock.return_value = get_requests_post_response()
        yield requests_post_mock


@pytest.fixture
def requests_post_raises_exception_mock():
    with mock.patch.object(requests, "post") as requests_post_raises_exception_mock:
        requests_post_raises_exception_mock.side_effect = requests.exceptions.HTTPError(
            _TEST_HTTP_ERROR_MESSAGE
        )
        yield requests_post_raises_exception_mock


@pytest.fixture
def open_file_mock():
    with mock.patch("builtins.open") as open_file_mock:
        yield open_file_mock().__enter__()


def get_requests_get_response():
    response = requests.models.Response()
    response.status_code = 200
    response._content = _TEST_HEALTH_CHECK_RESPONSE_CONTENT
    return response


@pytest.fixture
def requests_get_mock():
    with mock.patch.object(requests, "get") as requests_get_mock:
        requests_get_mock.return_value = get_requests_get_response()
        yield requests_get_mock


@pytest.fixture
def requests_get_raises_exception_mock():
    with mock.patch.object(requests, "get") as requests_get_raises_exception_mock:
        requests_get_raises_exception_mock.side_effect = requests.exceptions.HTTPError(
            _TEST_HTTP_ERROR_MESSAGE
        )
        yield requests_get_raises_exception_mock


class TestLocalModel:
    def test_deploy_to_local_endpoint(
        self,
        local_endpoint_init_mock,
        local_endpoint_enter_mock,
        local_endpoint_exit_mock,
    ):
        container_spec = gca_model_compat.ModelContainerSpec(image_uri=_TEST_IMAGE_URI)
        local_model = LocalModel(container_spec)

        with local_model.deploy_to_local_endpoint():
            pass

        local_endpoint_init_mock.assert_called_once_with(
            serving_container_image_uri=_TEST_IMAGE_URI,
            artifact_uri=None,
            serving_container_predict_route="",
            serving_container_health_route="",
            serving_container_command=[],
            serving_container_args=[],
            serving_container_environment_variables={},
            serving_container_ports=[],
            credential_path=None,
            host_port=None,
            container_ready_timeout=None,
            container_ready_check_interval=None,
        )
        assert local_endpoint_enter_mock.called
        assert local_endpoint_exit_mock.called

    def test_deploy_to_local_endpoint_with_all_parameters(
        self,
        local_endpoint_init_mock,
        local_endpoint_enter_mock,
        local_endpoint_exit_mock,
    ):
        container_spec = gca_model_compat.ModelContainerSpec(image_uri=_TEST_IMAGE_URI)
        local_model = LocalModel(container_spec)
        artifact_uri = "gs://myproject/mymodel"
        credential_path = "key.json"
        host_port = 6666
        container_ready_timeout = 60
        container_ready_check_interval = 5

        with local_model.deploy_to_local_endpoint(
            artifact_uri=artifact_uri,
            credential_path=credential_path,
            host_port=host_port,
            container_ready_timeout=container_ready_timeout,
            container_ready_check_interval=container_ready_check_interval,
        ):
            pass

        local_endpoint_init_mock.assert_called_once_with(
            serving_container_image_uri=_TEST_IMAGE_URI,
            artifact_uri=artifact_uri,
            serving_container_predict_route="",
            serving_container_health_route="",
            serving_container_command=[],
            serving_container_args=[],
            serving_container_environment_variables={},
            serving_container_ports=[],
            credential_path=credential_path,
            host_port=host_port,
            container_ready_timeout=container_ready_timeout,
            container_ready_check_interval=container_ready_check_interval,
        )
        assert local_endpoint_enter_mock.called
        assert local_endpoint_exit_mock.called


class TestLocalEndpoint:
    def test_init(
        self,
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
    ):
        with LocalEndpoint(_TEST_IMAGE_URI):
            pass

        run_prediction_container_mock.assert_called_once_with(
            _TEST_IMAGE_URI,
            artifact_uri=None,
            serving_container_predict_route=prediction.DEFAULT_LOCAL_PREDICT_ROUTE,
            serving_container_health_route=prediction.DEFAULT_LOCAL_HEALTH_ROUTE,
            serving_container_command=None,
            serving_container_args=None,
            serving_container_environment_variables=None,
            serving_container_ports=None,
            credential_path=None,
            host_port=None,
        )
        wait_until_container_runs_mock.assert_called_once_with()
        wait_until_health_check_succeeds_mock.assert_called_once_with()
        stop_container_if_exists_mock.assert_called_once_with()

    def test_init_with_all_parameters(
        self,
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
    ):
        artifact_uri = "gs://myproject/mymodel"
        serving_container_predict_route = "/custom_predict"
        serving_container_health_route = "/custom_health"
        serving_container_command = ["echo", "hello"]
        serving_container_args = [">", "tmp.log"]
        serving_container_environment_variables = {"custom_key": "custom_value"}
        serving_container_ports = [5555]
        credential_path = "key.json"
        host_port = 6666
        container_ready_timeout = 60
        container_ready_check_interval = 5

        with LocalEndpoint(
            _TEST_IMAGE_URI,
            artifact_uri=artifact_uri,
            serving_container_predict_route=serving_container_predict_route,
            serving_container_health_route=serving_container_health_route,
            serving_container_command=serving_container_command,
            serving_container_args=serving_container_args,
            serving_container_environment_variables=serving_container_environment_variables,
            serving_container_ports=serving_container_ports,
            credential_path=credential_path,
            host_port=host_port,
            container_ready_timeout=container_ready_timeout,
            container_ready_check_interval=container_ready_check_interval,
        ):
            pass

        run_prediction_container_mock.assert_called_once_with(
            _TEST_IMAGE_URI,
            artifact_uri=artifact_uri,
            serving_container_predict_route=serving_container_predict_route,
            serving_container_health_route=serving_container_health_route,
            serving_container_command=serving_container_command,
            serving_container_args=serving_container_args,
            serving_container_environment_variables=serving_container_environment_variables,
            serving_container_ports=serving_container_ports,
            credential_path=credential_path,
            host_port=host_port,
        )
        wait_until_container_runs_mock.assert_called_once_with()
        wait_until_health_check_succeeds_mock.assert_called_once_with()
        stop_container_if_exists_mock.assert_called_once_with()

    def test_predict_request(
        self,
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
        requests_post_mock,
    ):
        serving_container_predict_route = "/custom_predict"
        host_port = 8080
        url = f"http://localhost:{host_port}{serving_container_predict_route}"
        request = '{"instances": [{"x": [[1.1, 2.2, 3.3, 5.5]]}]}'

        with LocalEndpoint(
            _TEST_IMAGE_URI,
            serving_container_predict_route=serving_container_predict_route,
            host_port=host_port,
        ) as endpoint:
            response = endpoint.predict(request=request)

        requests_post_mock.assert_called_once_with(url, data=request, headers=None)
        assert response.status_code == get_requests_post_response().status_code
        assert response._content == get_requests_post_response()._content

    def test_predict_request_with_headers(
        self,
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
        requests_post_mock,
    ):
        serving_container_predict_route = "/custom_predict"
        host_port = 8080
        url = f"http://localhost:{host_port}{serving_container_predict_route}"
        request = '{"instances": [{"x": [[1.1, 2.2, 3.3, 5.5]]}]}'
        headers = {"Custom-header": "Custom-value"}

        with LocalEndpoint(
            _TEST_IMAGE_URI,
            serving_container_predict_route=serving_container_predict_route,
            host_port=host_port,
        ) as endpoint:
            response = endpoint.predict(request=request, headers=headers)

        requests_post_mock.assert_called_once_with(url, data=request, headers=headers)
        assert response.status_code == get_requests_post_response().status_code
        assert response._content == get_requests_post_response()._content

    def test_predict_request_file(
        self,
        tmp_path,
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
        requests_post_mock,
        open_file_mock,
    ):
        serving_container_predict_route = "/custom_predict"
        host_port = 8080
        url = f"http://localhost:{host_port}{serving_container_predict_route}"
        request = '{"instances": [{"x": [[1.1, 2.2, 3.3, 5.5]]}]}'
        request_file = tmp_path / "input.json"
        request_file.write_text(request)

        with LocalEndpoint(
            _TEST_IMAGE_URI,
            serving_container_predict_route=serving_container_predict_route,
            host_port=host_port,
        ) as endpoint:
            response = endpoint.predict(request_file=request_file)

        requests_post_mock.assert_called_once_with(
            url, data=open_file_mock, headers=None
        )
        assert response.status_code == get_requests_post_response().status_code
        assert response._content == get_requests_post_response()._content

    def test_predict_request_file_with_headers(
        self,
        tmp_path,
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
        requests_post_mock,
        open_file_mock,
    ):
        serving_container_predict_route = "/custom_predict"
        host_port = 8080
        url = f"http://localhost:{host_port}{serving_container_predict_route}"
        request = '{"instances": [{"x": [[1.1, 2.2, 3.3, 5.5]]}]}'
        request_file = tmp_path / "input.json"
        request_file.write_text(request)
        headers = {"Custom-header": "Custom-value"}

        with LocalEndpoint(
            _TEST_IMAGE_URI,
            serving_container_predict_route=serving_container_predict_route,
            host_port=host_port,
        ) as endpoint:
            response = endpoint.predict(request_file=request_file, headers=headers)

        requests_post_mock.assert_called_once_with(
            url, data=open_file_mock, headers=headers
        )
        assert response.status_code == get_requests_post_response().status_code
        assert response._content == get_requests_post_response()._content

    def test_predict_both_request_and_request_file_specified_raises_exception(
        self,
        tmp_path,
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
    ):
        serving_container_predict_route = "/custom_predict"
        host_port = 8080
        request = '{"instances": [{"x": [[1.1, 2.2, 3.3, 5.5]]}]}'
        request_file = tmp_path / "input.json"
        request_file.write_text(request)
        expected_message = (
            "request and request_file can not be specified at the same time."
        )

        with pytest.raises(ValueError) as exception:
            with LocalEndpoint(
                _TEST_IMAGE_URI,
                serving_container_predict_route=serving_container_predict_route,
                host_port=host_port,
            ) as endpoint:
                endpoint.predict(request=request, request_file=request_file)

        assert str(exception.value) == expected_message

    def test_predict_none_of_request_and_request_file_specified_raises_exception(
        self,
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
    ):
        serving_container_predict_route = "/custom_predict"
        host_port = 8080
        expected_message = "One of request and request_file needs to be specified."

        with pytest.raises(ValueError) as exception:
            with LocalEndpoint(
                _TEST_IMAGE_URI,
                serving_container_predict_route=serving_container_predict_route,
                host_port=host_port,
            ) as endpoint:
                endpoint.predict()

        assert str(exception.value) == expected_message

    def test_predict_request_file_not_exists_raises_exception(
        self,
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
    ):
        serving_container_predict_route = "/custom_predict"
        host_port = 8080
        request_file = "non_existing_input.json"
        expected_message = f"request_file does not exist: {request_file}."

        with pytest.raises(ValueError) as exception:
            with LocalEndpoint(
                _TEST_IMAGE_URI,
                serving_container_predict_route=serving_container_predict_route,
                host_port=host_port,
            ) as endpoint:
                endpoint.predict(request_file=request_file)

        assert str(exception.value) == expected_message

    def test_predict_raises_exception(
        self,
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
        requests_post_raises_exception_mock,
    ):
        serving_container_predict_route = "/custom_predict"
        host_port = 8080
        url = f"http://localhost:{host_port}{serving_container_predict_route}"
        request = '{"instances": [{"x": [[1.1, 2.2, 3.3, 5.5]]}]}'

        with pytest.raises(requests.exceptions.RequestException) as exception:
            with LocalEndpoint(
                _TEST_IMAGE_URI,
                serving_container_predict_route=serving_container_predict_route,
                host_port=host_port,
            ) as endpoint:
                endpoint.predict(request=request)

        requests_post_raises_exception_mock.assert_called_once_with(
            url, data=request, headers=None
        )
        assert str(exception.value) == _TEST_HTTP_ERROR_MESSAGE

    def test_run_health_check(
        self,
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
        requests_get_mock,
    ):
        serving_container_health_route = "/custom_health"
        host_port = 8080
        url = f"http://localhost:{host_port}{serving_container_health_route}"

        with LocalEndpoint(
            _TEST_IMAGE_URI,
            serving_container_health_route=serving_container_health_route,
            host_port=host_port,
        ) as endpoint:
            response = endpoint.run_health_check()

        requests_get_mock.assert_called_once_with(url)
        assert response.status_code == get_requests_get_response().status_code
        assert response._content == get_requests_get_response()._content

    def test_run_health_check_raises_exception(
        self,
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
        requests_get_raises_exception_mock,
    ):
        serving_container_health_route = "/custom_health"
        host_port = 8080
        url = f"http://localhost:{host_port}{serving_container_health_route}"

        with pytest.raises(requests.exceptions.RequestException) as exception:
            with LocalEndpoint(
                _TEST_IMAGE_URI,
                serving_container_health_route=serving_container_health_route,
                host_port=host_port,
            ) as endpoint:
                endpoint.run_health_check()

        requests_get_raises_exception_mock.assert_called_once_with(url)
        assert str(exception.value) == _TEST_HTTP_ERROR_MESSAGE

    def test_print_container_logs(
        self,
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
        run_print_container_logs_mock,
    ):
        with LocalEndpoint(_TEST_IMAGE_URI) as endpoint:
            endpoint.print_container_logs()

        run_print_container_logs_mock.assert_called_once_with(
            run_prediction_container_mock(), start_index=0
        )

    def test_print_container_logs_show_all(
        self,
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
        run_print_container_logs_mock,
    ):
        with LocalEndpoint(_TEST_IMAGE_URI) as endpoint:
            endpoint.print_container_logs(show_all=True)

        run_print_container_logs_mock.assert_called_once_with(
            run_prediction_container_mock(), start_index=None
        )

    def test_print_container_logs_if_container_is_not_running_container_running(
        self,
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
        get_container_status_running_mock,
        local_endpoint_print_container_logs_mock,
    ):
        with LocalEndpoint(_TEST_IMAGE_URI) as endpoint:
            endpoint.print_container_logs_if_container_is_not_running()

        assert get_container_status_running_mock.called
        assert not local_endpoint_print_container_logs_mock.called

    def test_print_container_logs_if_container_is_not_running_container_exited(
        self,
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
        get_container_status_exited_mock,
        local_endpoint_print_container_logs_mock,
    ):
        with LocalEndpoint(_TEST_IMAGE_URI) as endpoint:
            endpoint.print_container_logs_if_container_is_not_running()

        assert get_container_status_exited_mock.called
        local_endpoint_print_container_logs_mock.assert_called_once_with(show_all=False)

    def test_print_container_logs_if_container_is_not_running_container_exited_show_all(
        self,
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
        get_container_status_exited_mock,
        local_endpoint_print_container_logs_mock,
    ):
        with LocalEndpoint(_TEST_IMAGE_URI) as endpoint:
            endpoint.print_container_logs_if_container_is_not_running(show_all=True)

        assert get_container_status_exited_mock.called
        local_endpoint_print_container_logs_mock.assert_called_once_with(show_all=True)

    def test_get_container_status(
        self,
        run_prediction_container_with_running_status_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
    ):
        with LocalEndpoint(_TEST_IMAGE_URI) as endpoint:
            status = endpoint.get_container_status()

        assert run_prediction_container_with_running_status_mock().reload.called
        assert status == _CONTAINER_RUNNING_STATUS
