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
"""Launches Tensorboard Uploader for TB.GCP."""
import re

from absl import app
from absl import flags
import grpc
from tensorboard.plugins.scalar import metadata as scalar_metadata
from tensorboard.plugins.distribution import metadata as distribution_metadata
from tensorboard.plugins.histogram import metadata as histogram_metadata
from tensorboard.plugins.text import metadata as text_metadata
from tensorboard.plugins.hparams import metadata as hparams_metadata
from tensorboard.plugins.image import metadata as images_metadata
from tensorboard.plugins.graph import metadata as graphs_metadata

from google.cloud import storage
from google import auth as google_auth
from google.auth.transport import grpc as google_auth_transport_grpc
from google.auth.transport import requests as google_auth_transport_requests
from google.cloud.aiplatform.tensorboard import uploader
from google.cloud.aiplatform_v1beta1.services.tensorboard_service import (
    TensorboardServiceClient,
)
from google.cloud.aiplatform_v1beta1.services.tensorboard_service.transports import (
    grpc as transports_grpc,
)

_AUTH_SCOPE = "https://www.googleapis.com/auth/cloud-platform"
_TB_GCP_RESOURCE_NAME = "projects/{}/locations/{}"
_ENV_SPECIFIC_CONFIGS = {
    "autopush": {
        "api_server_hostname": "autopush-aiplatform.sandbox.googleapis.com",
        "web_server_hostname": "tensorboard-gcp-dev.wm.r.appspot.com",
    },
    "staging": {
        "api_server_hostname": "staging-aiplatform.sandbox.googleapis.com",
        "web_server_hostname": "tensorboard-gcp-staging.uc.r.appspot.com",
    },
    "prod": {
        "api_server_hostname": "aiplatform.googleapis.com",
        "web_server_hostname": "tensorboard-gcp-prod.uc.r.appspot.com",
    },
}

FLAGS = flags.FLAGS
flags.DEFINE_string("experiment_name", None, "The name of the Cloud AI Experiment.")
flags.DEFINE_string(
    "experiment_display_name", None, "The display name of the Cloud AI Experiment."
)
flags.DEFINE_string("logdir", None, "Tensorboard log directory to upload")
flags.DEFINE_bool("one_shot", False, "Iterate through logdir once to upload.")
flags.DEFINE_string("api_uri", None, "DEPRECATED - API uri.")
flags.DEFINE_string("env", "prod", "Environment which this tensorboard belongs to.")
flags.DEFINE_string(
    "tensorboard_resource_name",
    None,
    "Tensorboard resource to create this experiment in. ",
)
flags.DEFINE_integer(
    "event_file_inactive_secs",
    None,
    "Age in seconds of last write after which an event file is considered " "inactive.",
)
flags.DEFINE_string(
    "run_name_prefix",
    None,
    "If present, all runs created by this invocation will have their name "
    "prefixed by this value.",
)

flags.DEFINE_multi_string(
    "allowed_plugins",
    [
        scalar_metadata.PLUGIN_NAME,
        histogram_metadata.PLUGIN_NAME,
        distribution_metadata.PLUGIN_NAME,
        text_metadata.PLUGIN_NAME,
        hparams_metadata.PLUGIN_NAME,
        images_metadata.PLUGIN_NAME,
        graphs_metadata.PLUGIN_NAME,
    ],
    "Plugins allowed by the Uploader.",
)

flags.mark_flags_as_required(["experiment_name", "logdir", "tensorboard_resource_name"])


def main(argv):
    if len(argv) > 1:
        raise app.UsageError("Too many command-line arguments.")

    scope = _AUTH_SCOPE
    credentials, _ = google_auth.default(scopes=(scope,))
    request = google_auth_transport_requests.Request()
    m = re.match(
        "projects/(.*)/locations/(.*)/tensorboards/.*", FLAGS.tensorboard_resource_name
    )
    project_id = m[1]
    region = m[2]

    web_server_hostname = None
    if FLAGS.api_uri:
        api_server_hostname = FLAGS.api_uri
        for env, config in _ENV_SPECIFIC_CONFIGS.items():
            if config["api_server_hostname"] in FLAGS.api_uri:
                web_server_hostname = config["web_server_hostname"]
                break
    else:
        api_server_hostname = "{}-{}".format(
            region, _ENV_SPECIFIC_CONFIGS[FLAGS.env]["api_server_hostname"]
        )
        web_server_hostname = _ENV_SPECIFIC_CONFIGS[FLAGS.env]["web_server_hostname"]

    channel = google_auth_transport_grpc.secure_authorized_channel(
        credentials, request, api_server_hostname
    )
    api_client = TensorboardServiceClient(
        transport=transports_grpc.TensorboardServiceGrpcTransport(channel=channel)
    )

    try:
        tensorboard = api_client.get_tensorboard(name=FLAGS.tensorboard_resource_name)
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            raise app.UsageError(
                "Tensorboard resource %s not found" % FLAGS.tensorboard_resource_name,
                exitcode=0,
            )
        raise

    blob_storage_bucket = None
    blob_storage_folder = None
    if tensorboard.blob_storage_path_prefix:
        path_prefix = tensorboard.blob_storage_path_prefix + "/"
        first_slash_index = path_prefix.find("/")
        bucket_name = path_prefix[:first_slash_index]
        blob_storage_bucket = storage.Client(project=project_id).bucket(bucket_name)
        blob_storage_folder = path_prefix[first_slash_index + 1 :]
    else:
        raise app.UsageError(
            "Tensorboard resource {} is obsolete. Please create a new one.".format(
                FLAGS.tensorboard_resource_name
            ),
            exitcode=0,
        )

    tb_uploader = uploader.TensorBoardUploader(
        experiment_name=FLAGS.experiment_name,
        experiment_display_name=FLAGS.experiment_display_name,
        tensorboard_resource_name=tensorboard.name,
        blob_storage_bucket=blob_storage_bucket,
        blob_storage_folder=blob_storage_folder,
        allowed_plugins=FLAGS.allowed_plugins,
        writer_client=api_client,
        logdir=FLAGS.logdir,
        one_shot=FLAGS.one_shot,
        event_file_inactive_secs=FLAGS.event_file_inactive_secs,
        run_name_prefix=FLAGS.run_name_prefix,
    )

    tb_uploader.create_experiment()

    print(
        "View your Tensorboard at https://{}/experiment/{}".format(
            web_server_hostname,
            tb_uploader.get_experiment_resource_name().replace("/", "+"),
        )
    )
    if FLAGS.one_shot:
        tb_uploader._upload_once()  # pylint: disable=protected-access
    else:
        tb_uploader.start_uploading()


def run_main():
    app.run(main)


if __name__ == "__main__":
    run_main()
