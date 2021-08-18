# -*- coding: utf-8 -*-

# Copyright 2021 Google LLC
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

import abc
import datetime
import functools
import inspect
import joblib
import json
import numpy as np
import os
import pathlib
import pickle
import tempfile
from typing import Any
from typing import Callable

from fastapi import FastAPI, Request

from google.cloud import aiplatform
from google.cloud import storage
from google.cloud.aiplatform import base
from google.cloud.aiplatform.experimental.vertex_model.serializers import pandas
from google.cloud.aiplatform.experimental.vertex_model.serializers import pytorch
from google.cloud.aiplatform.experimental.vertex_model.serializers import model
from google.cloud.aiplatform.experimental.vertex_model.utils import source_utils


try:
    import pandas as pd
except ImportError:
    raise ImportError(
        "Pandas is not installed. Please install pandas to use VertexModel"
    )

try:
    import torch
except ImportError:
    raise ImportError(
        "PyTorch is not installed. Please install torch to use VertexModel"
    )


REGION = "us-central1"  # @param {type:"string"}
MODEL_ARTIFACT_DIR = "custom-container-prediction-model"  # @param {type:"string"}
REPOSITORY = "custom-container-prediction"  # @param {type:"string"}
IMAGE = "sklearn-fastapi-server"  # @param {type:"string"}
MODEL_DISPLAY_NAME = "sklearn-custom-container"  # @param {type:"string"}

_LOGGER = base.Logger(__name__)


def vertex_fit_function_wrapper(method: Callable[..., Any]):
    """Adapts code in the user-written child class for cloud training

    If the user wishes to conduct local development, will return the original function.
    If not, converts the child class to an executable inner script and calls the Vertex
    AI SDK using the custom training job interface.

    Args:
        method (Callable[..., Any]): the method to be wrapped.

    Returns:
        A function that will complete local or cloud training based off of the user's
        implementation of the VertexModel class. The training mode is determined by the
        user-designated training_mode variable.

    Raises:
        RuntimeError: An error occurred trying to access the staging bucket.
    """

    @functools.wraps(method)
    def f(*args, **kwargs):
        if method.__self__.training_mode == "local":
            return method(*args, **kwargs)

        obj = method.__self__
        cls_name = obj.__class__.__name__

        training_source = source_utils._make_class_source(obj)
        bound_args = inspect.signature(method).bind(*args, **kwargs)

        pass_through_params = {}
        serialized_params = {}

        for parameter_name, parameter in bound_args.arguments.items():
            parameter_type = type(parameter)
            valid_types = [int, float, str] + list(
                obj._data_serialization_mapping.keys()
            )
            if parameter_type not in valid_types:
                raise RuntimeError(
                    f"{parameter_type} not supported. parameter_name = {parameter_name}. The only supported types are {valid_types}"
                )

            if parameter_type in obj._data_serialization_mapping.keys():
                serialized_params[parameter_name] = parameter
            else:  # assume primitive
                pass_through_params[parameter_name] = parameter

        staging_bucket = aiplatform.initializer.global_config.staging_bucket
        if staging_bucket is None:
            raise RuntimeError(
                "Staging bucket must be set to run training in cloud mode: `aiplatform.init(staging_bucket='gs://my/staging/bucket')`"
            )

        timestamp = datetime.datetime.now().isoformat(sep="-", timespec="milliseconds")
        vertex_model_root_folder = "/".join(
            [staging_bucket, f"vertex_model_run_{timestamp}"]
        )

        param_name_to_serialized_info = {}
        serialized_inputs_artifacts_folder = "/".join(
            [vertex_model_root_folder, "serialized_input_parameters"]
        )

        for parameter_name, parameter in serialized_params.items():
            parameter_type = type(parameter)

            serializer = obj._data_serialization_mapping[parameter_type][1]
            parameter_uri = serializer(
                serialized_inputs_artifacts_folder, parameter, parameter_name
            )

            # namedtuple
            param_name_to_serialized_info[parameter_name] = (
                parameter_uri,
                parameter_type,
            )  # "pd.DataFrame"

            _LOGGER.info(
                f"{parameter_name} of type {parameter_type} was serialized to {parameter_uri}"
            )

        with tempfile.TemporaryDirectory() as tmpdirname:
            script_path = pathlib.Path(tmpdirname) / "training_script.py"

            source = source_utils._make_source(
                cls_source=training_source,
                cls_name=cls_name,
                instance_method=method.__name__,
                pass_through_params=pass_through_params,
                param_name_to_serialized_info=param_name_to_serialized_info,
                obj=obj,
            )

            with open(script_path, "w") as f:
                f.write(source)

            obj._training_job = aiplatform.CustomTrainingJob(
                display_name="my_training_job",
                script_path=str(script_path),
                requirements=obj._dependencies,
                container_uri="us-docker.pkg.dev/vertex-ai/training/scikit-learn-cpu.0-23:latest",
                model_serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-5:latest",
            )

            obj._model = obj._training_job.run(
                model_display_name="my_model", replica_count=1,
            )

    return f


def vertex_predict_function_wrapper(method: Callable[..., Any]):
    """Adapts code in the user-written child class for prediction

    If the user wishes to conduct local prediction, will deserialize a remote model if necessary
    and return the local object's predict function. If the user wishes to conduct cloud prediction,
    this method creates a custom container that an Endpoint resource can use to make
    remote predictions.

    Args:
        method (Callable[..., Any]): the predict() method to be wrapped.

    Returns:
        A function that will complete local or cloud prediction based off of the user's
        implementation of the VertexModel class. The prediction mode is determined by the
        user-designated training_mode variable.
    """

    @functools.wraps(method)
    def p(*args, **kwargs):
        obj = method.__self__
        output_dir = ""

        # Local training to local prediction: return original method
        if method.__self__.training_mode == "local" and obj._model is None:
            return method(*args, **kwargs)

        # Local training to cloud prediction CUJ: serialize to cloud location
        if method.__self__.training_mode == "cloud" and obj._model is None:
            output_dir = model._serialize_local_model(
                os.getenv("AIP_MODEL_DIR"), obj, obj.training_mode
            )

        # Cloud training to local prediction: deserialize from cloud URI
        if method.__self__.training_mode == "local":
            output_dir = obj._model._gca_resource.artifact_uri
            model_uri = pathlib.Path(output_dir) / (
                "my_" + obj.training_mode + "_model.pth"
            )

            my_model = model._deserialize_remote_model(str(model_uri))
            return my_model.predict(*args, **kwargs)

        # Make remote predictions, regardless of training: create custom container
        if method.__self__.training_mode == "cloud":
            app = FastAPI()
            gcs_client = storage.Client()

            if obj._model is None:
                my_model = model._deserialize_remote_model(output_dir)
            else:
                output_dir = obj._model._gca_resource.artifact_uri
                model_uri = pathlib.Path(output_dir) / (
                    "my_" + obj.training_mode + "_model.pth"
                )
                my_model = model._deserialize_remote_model(str(model_uri))

            @app.post(os.environ["AIP_PREDICT_ROUTE"])
            async def predict(request: Request):
                body = await request.json()

                instances = body["instances"]
                inputs = np.asarray(instances)
                outputs = my_model.predict(inputs)

                return {
                    "predictions": [_class_names[class_num] for class_num in outputs]
                }

            # Deploy model

            my_model = aiplatform.Model.upload(
                display_name=MODEL_DISPLAY_NAME,
                artifact_uri=output_dir,
                serving_container_image_uri=f"{REGION}-docker.pkg.dev/{PROJECT_ID}/{REPOSITORY}/{IMAGE}",
            )

            endpoint = my_model.deploy(machine_type="n1-standard-4")
            return endpoint.predict(*args, **kwargs)

            # Pass in full script to container:
            """
            component_spec.implementation=ContainerImplementation(
                    container=ContainerSpec(
                        image=base_image,
                        command=packages_to_install_command + [
                            'sh',
                            '-ec',
                            textwrap.dedent('''\
                                program_path=$(mktemp -d)
                                printf "%s" "$0" > "$program_path/ephemeral_component.py"
                                python3 -m kfp.components.executor_main \
                                    --component_module_path \
                                    "$program_path/ephemeral_component.py" \
                                    "$@"
                            '''),
                            source,
                        ],
                        args=[
                            "--executor_input",
                            ExecutorInputPlaceholder(),
                            "--function_to_execute", func.__name__,
                            ]
                    )
                )
            """

    return p


class VertexModel(metaclass=abc.ABCMeta):

    _data_serialization_mapping = {
        pd.DataFrame: (pandas._deserialize_dataframe, pandas._serialize_dataframe),
        torch.utils.data.DataLoader: (
            pytorch._deserialize_dataloader,
            pytorch._serialize_dataloader,
        ),
    }

    """ Parent class that users can extend to use the Vertex AI SDK """

    def __init__(self, *args, **kwargs):
        """Initializes child class. All constructor arguments must be passed to the
           VertexModel constructor as well."""
        # Default to local training on creation, at least for this prototype.
        self._training_job = None
        self._model = None
        self._constructor_arguments = (args, kwargs)
        self._dependencies = [
            "pandas>=1.3",
            "torch>=1.7",
            "google-cloud-aiplatform @ git+https://github.com/googleapis/python-aiplatform@refs/pull/603/head#egg=google-cloud-aiplatform",
        ]

        self.training_mode = "local"

        self.fit = vertex_fit_function_wrapper(self.fit)
        self.predict = vertex_predict_function_wrapper(self.predict)

    @abc.abstractmethod
    def fit(self):
        """Train model."""
        pass

    @abc.abstractmethod
    def predict(self):
        """Make predictions on training data."""
        pass

    def batch_predict(self):
        """Make predictions on training data."""
        raise NotImplementedError("batch_predict is currently not implemented.")

    def eval(self):
        """Evaluate model."""
        raise NotImplementedError("eval is currently not implemented.")
