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

"""A plugin to handle remote tensoflow profiler sessions for Vertex AI."""

import argparse
from collections import namedtuple
import importlib.util
import json
import logging
from tensorboard.plugins.base_plugin import TBContext
from typing import Optional
from urllib import parse
from werkzeug import Response

from google.cloud.aiplatform.training_utils import environment_variables
from google.cloud.aiplatform.training_utils.cloud_profiler.plugins import base_plugin
from google.cloud.aiplatform.training_utils.cloud_profiler.plugins.tensorflow import (
    tensorboard_api,
)


# TF verison information.
Version = namedtuple("Version", ["major", "minor", "patch"])

logger = logging.Logger("tf-profiler")


def _tf_installed() -> bool:
    """Helper function to determine if tensorflow is installed.

    Returns:
        Bool indicating whether tensorflow is installed.
    """
    return importlib.util.find_spec("tensorflow")


def _get_tf_versioning() -> Optional[Version]:
    """Convert version string to a Version namedtuple for ease of parsing.

    Returns:
        A version object if finding the version was successful, None otherwise.
    """
    import tensorflow as tf

    version = tf.__version__

    versioning = version.split(".")
    if len(versioning) != 3:
        return

    return Version(int(versioning[0]), int(versioning[1]), int(versioning[2]))


def _is_compatible_version(version: Version) -> bool:
    """Check if version is compatible with tf profiling.

    Profiling plugin is available to be used for version >= 2.2.0.
    Source: https://www.tensorflow.org/guide/profiler

    Args:
        version (Version):
            Required. `Verison` of tensorflow.

    Returns:
        Bool indicating wheter version is compatible with profiler.
    """
    return version.major >= 2 and version.minor >= 2


def _check_tf() -> bool:
    """Check whether all the tensorflow prereqs are met.

    Returns:
        True if all requirements met, False otherwise.
    """
    # Check tf is installed
    if not _tf_installed():
        logger.warning("Tensorflow not installed, cannot initialize profiling plugin")
        return False

    # Check tensorflow version, introduced 2.2 >=
    version = _get_tf_versioning()
    if not version:
        logger.warning(
            "Could not find major, minor, and patch versions of tensorflow. Version found: %s",
            version,
        )
        return False

    if not _is_compatible_version(version):
        logger.warning(
            "Version %s is incompatible with tf profiler."
            "To use the profiler, choose a version >= 2.2.0",
            "%s.%s.%s" % (version.major, version.minor, version.patch),
        )
        return False

    # Check for the tf profiler plugin
    if not importlib.util.find_spec("tensorboard_plugin_profile"):
        logger.warning(
            "Could not import tensorboard_plugin_profile, will not run tf profiling service"
        )
        return False

    return True


def _create_profiling_context() -> TBContext:
    """Creates the base context needed for TB Profiler.

    Returns:
        An initialized `TBContext`.
    """

    context_flags = argparse.Namespace(master_tpu_unsecure_channel=None)

    context = TBContext(
        logdir=environment_variables.tensorboard_log_dir,
        multiplexer=None,
        flags=context_flags,
    )

    return context


def _host_to_grpc(hostname: str) -> str:
    """Format a hostname to a grpc address.

    Args:
        hostname (str):
            Required. Address in form: `{hostname}:{port}`

    Returns:
        Address in form of: 'grpc://{hostname}:{port}'
    """
    return (
        "grpc://"
        + "".join(hostname.split(":")[:-1])
        + ":"
        + environment_variables.tf_profiler_port
    )


def _get_hostnames() -> Optional[str]:
    """Get the hostnames for all servers running.

    Returns:
        A host formatted by `_host_to_grpc` if obtaining the cluster spec
        is successful, None otherwise.
    """
    cluster_spec = environment_variables.cluster_spec
    if not cluster_spec:
        return

    cluster = cluster_spec.get("cluster", "")
    if not cluster:
        return

    hostnames = []
    for value in cluster.values():
        hostnames.extend(value)

    return ",".join([_host_to_grpc(x) for x in hostnames])


def _update_environ(environ) -> bool:
    """Add parameters to the query that are retrieved from training side.

    Args:
        environ (WSGIEnvironment):
            Required. The WSGI Environment.

    Returns:
        Whether the environment was successfully updated.
    """
    hosts = _get_hostnames()

    if not hosts:
        return False

    query_dict = {}
    query_dict["service_addr"] = hosts

    # Update service address and worker list
    # Use parse_qsl and then convert list to dictionary so we can update
    # attributes
    prev_query_string = dict(parse.parse_qsl(environ["QUERY_STRING"]))
    prev_query_string.update(query_dict)

    environ["QUERY_STRING"] = parse.urlencode(prev_query_string)

    return True


def _check_env_vars() -> bool:
    """Determine whether the correct environment variables are set.

    Returns:
        bool indicating all necessary variables are set.
    """
    if not environment_variables.tf_profiler_port:
        logger.warning(
            '"%s" environment variable not set, cannot enable profiling.',
            "AIP_TF_PROFILER_PORT",
        )
        return False

    if not environment_variables.tensorboard_log_dir:
        logger.warning(
            "Must set a tensorboard log directory, "
            "run training with tensorboard enabled."
        )
        return False

    if not environment_variables.tensorboard_api_uri:
        logger.warning("Must set the tensorboard API uri.")
        return False

    if not environment_variables.tensorboard_resource_name:
        logger.warning("Must set the tensorboard resource name.")
        return False

    cluster_spec = environment_variables.cluster_spec
    if not cluster_spec:
        logger.warning('Environment variable "CLUSTER_SPEC" is not set')
        return False

    if not environment_variables.cloud_ml_job_id:
        logger.warning("Job ID must be set")
        return False

    return True


class TFProfiler(base_plugin.BasePlugin):
    """Handler for Tensorflow Profiling."""

    PLUGIN_NAME = "profile"

    def __init__(self):
        """Build a TFProfiler object."""
        from tensorboard_plugin_profile.profile_plugin import ProfilePlugin

        context = _create_profiling_context()
        self._profile_request_sender = tensorboard_api.create_profile_request_sender()
        self._profile_plugin = ProfilePlugin(context)

    def get_routes(self):
        """List of routes to serve."""
        return {"/capture_profile": self.capture_profile_wrapper}

    # Define routes below
    def capture_profile_wrapper(self, environ, start_response) -> Response:
        """Take a request from tensorboard.gcp and run the profiling for the available servers."""
        # The service address (localhost) and worker list are populated locally
        if not _update_environ(environ):
            err = {"error": "Could not parse the environ: %s"}
            return Response(
                json.dumps(err), content_type="application/json", status=500
            )

        response = self._profile_plugin.capture_route(environ, start_response)

        self._profile_request_sender.send_request("")

        return response

    # End routes

    @staticmethod
    def setup() -> None:
        import tensorflow as tf

        tf.profiler.experimental.server.start(
            int(environment_variables.tf_profiler_port)
        )

    @staticmethod
    def post_setup_check() -> bool:
        """Only chief and task 0 should run the webserver."""
        cluster_spec = environment_variables.cluster_spec
        task_type = cluster_spec.get("task", {}).get("type", "")
        task_index = cluster_spec.get("task", {}).get("index", -1)

        return task_type in {"workerpool0", "chief"} and task_index == 0

    @staticmethod
    def can_initialize() -> bool:
        """Check that we can use the TF Profiler plugin.

        This function checks a number of dependencies for the plugin to ensure we have the
        right packages installed, the necessary versions, and the correct environment variables set.

        Returns:
            True if can initialize, False otherwise.
        """

        return _check_env_vars() and _check_tf()
