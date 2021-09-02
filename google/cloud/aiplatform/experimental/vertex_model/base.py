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

# import json
import pathlib
import tempfile
from typing import Any
from typing import Callable

from google.cloud import aiplatform
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

GITHUB_DEPENDENCY = "google-cloud-aiplatform @ git+https://github.com/googleapis/python-aiplatform@refs/pull/659/head#egg=google-cloud-aiplatform"

SERVING_COMMAND_STRING_CLI = [
    "sh",
    "-c",
    "python3 -m pip install --user --disable-pip-version-check 'uvicorn' 'fastapi' 'torch' 'pandas' 'google-cloud-aiplatform @ git+https://github.com/googleapis/python-aiplatform@refs/pull/659/head#egg=google-cloud-aiplatform' && \"$0\" \"$@\"",
    "sh",
    "-ec",
    'program_path=$(mktemp)\nprintf "%s" "$0" > "$program_path"\npython3 -u "$program_path" "$@"\n',
]

SERVING_COMMAND_STRING_CODE_SETUP = """import os
from fastapi import FastAPI, Request
import uvicorn
import functools
import inspect

from google.cloud.aiplatform.experimental.vertex_model.serializers import model

"""

SERVING_COMMAND_STRING_CODE_APIS = """

class ModelWrapper:

  def __init__(self, vertex_model_instance, deserialized_model):
     self._vertex_model_instance = vertex_model_instance
     self._deserialized_model = deserialized_model

  def __getattr__(self, name):
    if hasattr(self._deserialized_model, name):
        return getattr(self._deserialized_model, name)

    else:
        attribute = getattr(self._vertex_model_instance, name)

        if inspect.ismethod(attribute):
            # wrap vertex_model method
            return functools.partial(getattr(self._vertex_model_instance.__class__, name), mw)
        else:
            return attribute

app = FastAPI()
my_model = model._deserialize_remote_model(os.environ['AIP_STORAGE_URI'] + '/my_local_model.pth')
wrapped_model = ModelWrapper(original_model, my_model)


@app.get(os.environ['AIP_HEALTH_ROUTE'], status_code=200)
def health():
    return {}


@app.post(os.environ['AIP_PREDICT_ROUTE'])
async def predict(request: Request):
    body = await request.json()
    instances = body["instances"]
    input_data = original_model.predict_payload_to_predict_input(instances)

    my_model.predict = wrapped_model.predict
    outputs = my_model.predict(input_data)

    return {"predictions": original_model.predict_output_to_predict_payload(outputs)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=os.environ['AIP_HTTP_PORT'])
"""

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
        user-designated remote variable.

    Raises:
        RuntimeError: An error occurred trying to access the staging bucket.
    """

    @functools.wraps(method)
    def f(*args, **kwargs):
        obj = method.__self__
        cls_name = obj.__class__.__name__

        obj._model = None
        obj._endpoint = None

        if not method.__self__.remote:
            return method(*args, **kwargs)

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

            import_lines = source_utils.import_try_except(obj)

            class_args = inspect.signature(obj.__class__.__init__).bind(
                obj, *obj._constructor_arguments[0], **obj._constructor_arguments[1]
            )

            class_creation = f"original_model = {cls_name}({','.join(map(str, class_args.args[1:]))})\n"
            command_str = (
                import_lines
                + SERVING_COMMAND_STRING_CODE_SETUP
                + training_source
                + class_creation
                + SERVING_COMMAND_STRING_CODE_APIS
            )

            if GITHUB_DEPENDENCY not in obj.dependencies:
                obj.dependencies.append(GITHUB_DEPENDENCY)

            obj._training_job = aiplatform.CustomTrainingJob(
                display_name="my_training_job",
                script_path=str(script_path),
                requirements=obj.dependencies,
                container_uri="us-docker.pkg.dev/vertex-ai/training/scikit-learn-cpu.0-23:latest",
                model_serving_container_image_uri="gcr.io/google-appengine/python",
                model_serving_container_command=SERVING_COMMAND_STRING_CLI
                + [command_str],
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

        # Local training to local prediction: return original method
        if not method.__self__.remote and obj._model is None:
            return method(*args, **kwargs)

        # Local training to cloud prediction CUJ: serialize to cloud location
        if method.__self__.remote and obj._model is None:
            # Serialize model
            staging_bucket = aiplatform.initializer.global_config.staging_bucket

            if staging_bucket is None:
                raise RuntimeError(
                    "Staging bucket must be set to run training in cloud mode: `aiplatform.init(staging_bucket='gs://my/staging/bucket')`"
                )

            timestamp = datetime.datetime.now().isoformat(
                sep="-", timespec="milliseconds"
            )
            vertex_model_root_folder = "/".join(
                [staging_bucket, f"vertex_model_run_{timestamp}"]
            )
            vertex_model_model_folder = "/".join(
                [vertex_model_root_folder, "serialized_model"]
            )

            model_uri = model._serialize_local_model(
                vertex_model_model_folder, obj, "local"
            )

            # Upload model w/ command
            import_lines = source_utils.import_try_except(obj)

            training_source = source_utils._make_class_source(obj)
            class_args = inspect.signature(obj.__class__.__init__).bind(
                obj, *obj._constructor_arguments[0], **obj._constructor_arguments[1]
            )

            class_creation = f"original_model = {obj.__class__.__name__}({','.join(map(str, class_args.args[1:]))})\n"
            command_str = (
                import_lines
                + SERVING_COMMAND_STRING_CODE_SETUP
                + training_source
                + class_creation
                + SERVING_COMMAND_STRING_CODE_APIS
            )

            obj._model = aiplatform.Model.upload(
                display_name="serving-test",
                artifact_uri=vertex_model_model_folder,
                serving_container_image_uri="gcr.io/google-appengine/python",
                serving_container_command=SERVING_COMMAND_STRING_CLI + [command_str],
            )

        # Cloud training to local prediction: deserialize from cloud URI
        if not method.__self__.remote:
            output_dir = obj._model._gca_resource.artifact_uri
            model_uri = output_dir + "/" + "my_" + "local" + "_model.pth"

            my_model = model._deserialize_remote_model(model_uri)

            try:
                my_model.predict(*args, **kwargs)
            except AttributeError:
                my_model.predict = functools.partial(obj.__class__.predict, my_model)

            return my_model.predict(*args, **kwargs)

        # Make remote predictions, regardless of training: create custom container
        if method.__self__.remote:
            # Convert the predict input to a predict_payload input for the Endpoint resource
            data = []
            bound_args = inspect.signature(method).bind(*args, **kwargs)

            for parameter_name, parameter in bound_args.arguments.items():
                if parameter_name == "data":
                    data = obj.predict_input_to_predict_payload(parameter)
                    break

            # TODO: cleanup model resource after endpoint is created
            if obj._endpoint is None:
                _LOGGER.info(
                    "Model is not deployed for remote prediction. Deploying model to an endpoint."
                )
                obj._endpoint = obj._model.deploy(machine_type=obj.machine_type)

            endpoint_output = obj._endpoint.predict(instances=data)
            return obj.predict_payload_to_predict_output(endpoint_output.predictions)

    return p


class VertexModel(metaclass=abc.ABCMeta):
    """ Parent class that users can extend to use the Vertex AI SDK """

    _data_serialization_mapping = {
        pd.DataFrame: (pandas._deserialize_dataframe, pandas._serialize_dataframe),
        torch.utils.data.DataLoader: (
            pytorch._deserialize_dataloader,
            pytorch._serialize_dataloader,
        ),
    }

    dependencies = [
        "pandas>=1.3",
        "torch>=1.7",
        "google-cloud-aiplatform @ git+https://github.com/googleapis/python-aiplatform@refs/pull/659/head#egg=google-cloud-aiplatform",
    ]

    machine_type = "n1-standard-4"

    def __init__(self, *args, **kwargs):
        """Initializes child class. All constructor arguments must be passed to the
           VertexModel constructor as well."""
        # Default to local training on creation, at least for this prototype.
        self._training_job = None
        self._model = None
        self._endpoint = None

        self._constructor_arguments = (args, kwargs)

        self.remote = False

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

    @abc.abstractmethod
    def predict_input_to_predict_payload(self, instances: Any) -> List:
        pass

    @abc.abstractmethod
    def predict_payload_to_predict_input(self, predict_payload: List) -> Any:
        pass

    @abc.abstractmethod
    def predict_output_to_predict_payload(self):
        pass

    @abc.abstractmethod
    def predict_payload_to_predict_output(self):
        pass

    def batch_predict(self):
        """Make predictions on training data."""
        raise NotImplementedError("batch_predict is currently not implemented.")

    def eval(self):
        """Evaluate model."""
        raise NotImplementedError("eval is currently not implemented.")
