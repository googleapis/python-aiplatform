# -*- coding: utf-8 -*-

# Copyright 2021 Google LLC
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
#

import logging
import threading
from werkzeug import serving

from google.cloud.aiplatform.training_utils.cloud_profiler import base_plugin
from google.cloud.aiplatform.training_utils.cloud_profiler import webserver
from google.cloud.aiplatform.training_utils.cloud_profiler.plugins import tf_profiler


_AVAILABLE_PLUGINS = {"tensorflow": tf_profiler.TFProfiler}
_HOST_PORT = 6010


def _build_plugin(plugin: base_plugin):
    """Builds the plugin given the object."""
    if not plugin.can_initialize():
        logging.warning("Cannot initialize the plugin")
        return

    plugin.setup()

    if not plugin.post_setup_check():
        return

    return plugin()


def _build_profiler_webserver(plugin: base_plugin):
    app = webserver.create_web_server([plugin])
    return app


def _run_webserver(app):
    serving.run_simple("0.0.0.0", _HOST_PORT, app)


def _run_app_thread(server) -> None:
    """Run the cloud_training_tools web server in a separate thread."""
    daemon = threading.Thread(
        name="profile_server", target=_run_webserver, args=(server,)
    )
    daemon.setDaemon(True)
    daemon.start()


def initializer(plugin: str = "tensorflow"):
    """Initializes the profiling SDK.

    Args:
        plugin: A string name of the plugin to initialize.

    Raises:
        ValueError: The plugin does not exist.
    """

    plugin_obj = _AVAILABLE_PLUGINS.get(plugin)

    if not plugin_obj:
        raise ValueError(
            "Plugin {} not available, must choose from {}".format(
                plugin, _AVAILABLE_PLUGINS.keys()
            )
        )

    prof_plugin = _build_plugin(plugin_obj)

    if not prof_plugin:
        return

    server = webserver.WebServer([prof_plugin])
    _run_app_thread(server)
