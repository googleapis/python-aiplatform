# Copyright 2023 Google LLC
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

import dataclasses
import functools
import inspect
import os
import tempfile
from typing import Any, Callable, Dict, Optional, Union

from google.cloud import aiplatform
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.private_preview import vertex_ai
from google.cloud.aiplatform.private_preview.vertex_ai._workflow.serialization_engine import (
    cloud_pickle_serializer,
)


# TODO(b/271855597) Serialize all input args
PASS_THROUGH_ARG_TYPES = [str, int, float, bool]

# Move it once the sdk_private_releases bucket is created
VERTEX_AI_DEPENDENCY_PATH = "google-cloud-aiplatform @ git+https://github.com/nayaknishant/python-aiplatform.git@nn-vertex-predict#egg=google-cloud-aiplatform"


@dataclasses.dataclass
class TrainingConfig:
    """A class that holds the configuration for CustomJob."""

    # TODO(b/271612108) Add more training options
    display_name: Optional[str] = None
    staging_bucket: Optional[str] = None
    container_uri: Optional[str] = None
    replica_count: Optional[int] = None
    machine_type: Optional[str] = None


# TODO(b/271855073) Define the training script statically in the executor
def _make_training_script(
    input_path: str,
    output_path: str,
    serialized_args: Dict[str, Any],
    pass_through_args: Dict[str, Union[str, int, float]],
    method_name: str,
) -> str:
    """Helper method to make the training script for CustomJob."""
    # script to import modules
    script = "\n".join(
        [
            "# import modules...",
            "import os",
            "from google.cloud.aiplatform.private_preview.vertex_ai._workflow"
            + ".serialization_engine import cloud_pickle_serializer",
            "\n",
        ]
    )
    # script to retrieve the estimator
    script += "\n".join(
        [
            "# retrieve the estimator...",
            "estimator = cloud_pickle_serializer._cpkl_deserializer"
            + f"('input_estimator', '{input_path}')",
            "\n",
        ]
    )
    # script to retrieve serialized_args
    script += "\n".join(
        ["# retrieve serialized arguments..."]
        + [
            f"{arg_name} = cloud_pickle_serializer._cpkl_deserializer"
            + f"('{arg_name}', '{input_path}')"
            for arg_name in serialized_args.keys()
        ]
        + ["\n"]
    )
    # script to execute the method
    kwargs = []
    for arg_name in serialized_args.keys():
        kwargs.append(f"{arg_name}={arg_name}")
    for arg_name, arg_value in pass_through_args.items():
        if isinstance(arg_value, str):
            kwargs.append(f"{arg_name}='{arg_value}'")
        else:
            kwargs.append(f"{arg_name}={arg_value}")

    script += "\n".join(
        [
            "# execute the method...",
            f"output = estimator.{method_name}({', '.join(kwargs)})",
            "\n",
        ]
    )
    # script to serialize the output
    script += "\n".join(
        [
            "# serialize the output...",
            f"os.makedirs('{output_path}', exist_ok=True)\n",
        ]
    )
    if method_name in ["fit", "fit_transform"]:
        script += (
            "cloud_pickle_serializer._cpkl_serializer"
            + f"('output_estimator', estimator, '{output_path}')\n"
        )
    if method_name in ["transform", "fit_transform"]:
        script += (
            "cloud_pickle_serializer._cpkl_serializer"
            + f"('output_data', output, '{output_path}')\n"
        )

    return script


def remote_training(method: Callable[..., Any]):
    """Wrapper function that makes a method executable by Vertex CustomJob."""

    @functools.wraps(method)
    def f(*args, **kwargs):
        # Local mode
        if not vertex_ai.global_config.remote:
            return method(*args, **kwargs)

        # Remote mode
        bound_args = inspect.signature(method).bind(*args, **kwargs)
        self = bound_args.arguments.pop("self")
        method_name = method.__name__

        # TODO(b/271613128)
        # TODO(b/271613171)

        pass_through_args = {}
        serialized_args = {}

        for arg_name, arg_value in bound_args.arguments.items():
            if type(arg_value) in PASS_THROUGH_ARG_TYPES:
                pass_through_args[arg_name] = arg_value
            else:
                serialized_args[arg_name] = arg_value

        # set base gcs path for the remote job
        staging_bucket = (
            self.TrainingConfig.staging_bucket or vertex_ai.global_config.staging_bucket
        )
        if not staging_bucket:
            raise ValueError(
                "No default staging bucket set. "
                "Please call `vertex_ai.init(staging_bucket='gs://my-bucket')."
            )
        remote_job = f"remote-job-{utils.timestamped_unique_name()}"
        remote_job_base_path = os.path.join(staging_bucket, remote_job)
        remote_job_input_path = os.path.join(remote_job_base_path, "input")
        remote_job_output_path = os.path.join(remote_job_base_path, "output")

        # serialize the estimator by cloudpickle
        # TODO(b/271613454) Remove wrapper from estimators before serializing
        cloud_pickle_serializer._cpkl_serializer(
            "input_estimator", self, remote_job_input_path
        )
        # serialize args by cloudpickle
        for arg_name, arg_value in serialized_args.items():
            cloud_pickle_serializer._cpkl_serializer(
                arg_name, arg_value, remote_job_input_path
            )

        # execute the method in CustomJob
        with tempfile.TemporaryDirectory() as temp_dir:
            # make the training script
            script_path = os.path.join(temp_dir, "training_script.py")
            script = _make_training_script(
                input_path=remote_job_input_path.replace("gs://", "/gcs/", 1),
                output_path=remote_job_output_path.replace("gs://", "/gcs/", 1),
                serialized_args=serialized_args,
                pass_through_args=pass_through_args,
                method_name=method_name,
            )
            with open(script_path, "w") as f:
                f.write(script)

            # set training configuration
            display_name = self.TrainingConfig.display_name or remote_job
            # only support sklearn in PoC
            # TODO(b/271613128) update default settings after we support more frameworks
            container_uri = self.TrainingConfig.container_uri or "python:3.8"
            machine_type = self.TrainingConfig.machine_type or "n1-standard-4"
            replica_count = self.TrainingConfig.replica_count or 1

            # only need sklearn and pandas for PoC
            # TODO(b/271613128) update requirements after we support more frameworks
            try:
                import sklearn

                sklearn_version = sklearn.__version__
            except ImportError:
                sklearn_version = "1.0"

            requirements = [
                VERTEX_AI_DEPENDENCY_PATH,
                f"scikit-learn=={sklearn_version}",
                "pandas",
            ]

            # create & run the CustomJob

            # TODO(b/271613912) Disable CustomJob logs
            job = aiplatform.CustomJob.from_local_script(
                display_name=display_name,
                script_path=script_path,
                container_uri=container_uri,
                requirements=requirements,
                machine_type=machine_type,
                replica_count=replica_count,
                staging_bucket=remote_job_base_path,
            )

        job.run()

        # retrieve the result from gcs to local

        # for sklearn `fit` and `fit_transform`, update all the estimated attributes
        # TODO(b/271867453) centralize these method names in constant
        if method_name in ["fit", "fit_transform"]:
            estimator = cloud_pickle_serializer._cpkl_deserializer(
                "output_estimator", remote_job_output_path
            )
            # TODO(b/271857515) update objects in place
            for attr_name, attr_value in estimator.__dict__.items():
                if attr_name.endswith("_") and not attr_name.startswith("__"):
                    setattr(self, attr_name, attr_value)

        if method_name in ["transform", "fit_transform"]:
            data = cloud_pickle_serializer._cpkl_deserializer(
                "output_data", remote_job_output_path
            )
            return data

        return self

    return f