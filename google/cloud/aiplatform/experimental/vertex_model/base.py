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
import os
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


COMMAND_STRING_CLI = """sh
-c
python3 -m pip install --user --disable-pip-version-check --force-reinstall --upgrade 'fastapi' 'torch' 'pandas' 'google-cloud-aiplatform @ git+https://github.com/googleapis/python-aiplatform@refs/pull/628/head#egg=google-cloud-aiplatform' && \"$0\" \"$@\"
sh
-ec
program_path=$(mktemp)\nprintf \"%s\" \"$0\" > \"$program_path\"\npython3 -u \"$program_path\" \"$@\"\n
|"""

COMMAND_STRING_CODE_SETUP = """
from fastapi import FastAPI, Request
from google.cloud.aiplatform.experimental.vertex_model.serializers import model

"""

COMMAND_STRING_CODE_APIS = """

app = FastAPI()
my_model = model._deserialize_remote_model(os.environ['AIP_STORAGE_URI'] + '/my_local_model.pth')

@app.get(os.environ['AIP_HEALTH_ROUTE'], status_code=200)
def health():
    return {}


@app.post(os.environ['AIP_PREDICT_ROUTE'])
async def predict(request: Request):
    body = await request.json()

    instances = body["instances"]

    data = pd.DataFrame(instances, columns=['feat_1', 'feat_2'])
    torch_tensor = torch.tensor(data[feature_columns].values).type(torch.FloatTensor)

    my_model.predict = functools.partial(original_model.__class__.predict, my_model)
    outputs = my_model.predict(torch_tensor)

    return {"predictions": outputs.tolist()}
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
        if not method.__self__.remote:
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

            import_lines = ""
            try:
                module = inspect.getmodule(obj.__class__)
                import_lines = "\n".join(source_utils.get_import_lines(module.__file__))

            except AttributeError:
                import_lines = "\n".join(
                    source_utils.get_import_lines(
                        source_utils.jupyter_notebook_to_file()
                    )
                )

            class_args = inspect.signature(obj.__class__.__init__).bind(
                obj, *obj._constructor_arguments[0], **obj._constructor_arguments[1]
            )

            class_creation = f"original_model = {cls_name}({','.join(map(str, class_args.args[1:]))})\n"
            command_str = (
                COMMAND_STRING_CLI
                + import_lines
                + COMMAND_STRING_CODE_SETUP
                + training_source
                + class_creation
                + COMMAND_STRING_CODE_APIS
            )

            if (
                "google-cloud-aiplatform @ git+https://github.com/googleapis/python-aiplatform@refs/pull/628/head#egg=google-cloud-aiplatform"
                not in obj._dependencies
            ):
                obj._dependencies.append(
                    "google-cloud-aiplatform @ git+https://github.com/googleapis/python-aiplatform@refs/pull/628/head#egg=google-cloud-aiplatform"
                )

            obj._training_job = aiplatform.CustomTrainingJob(
                display_name="my_training_job",
                script_path=str(script_path),
                requirements=obj._dependencies,
                container_uri="us-docker.pkg.dev/vertex-ai/training/scikit-learn-cpu.0-23:latest",
                model_serving_container_image_uri="gcr.io/google-appengine/python",
                model_serving_container_command=command_str.split("\n"),
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
            model_uri = model._serialize_local_model(
                os.environ["AIP_STORAGE_URI"], obj, "local"
            )

            # Upload model w/ command
            import_lines = ""
            try:
                module = inspect.getmodule(obj.__class__)
                import_lines = "\n".join(source_utils.get_import_lines(module.__file__))

            except AttributeError:
                import_lines = "\n".join(
                    source_utils.get_import_lines(
                        source_utils.jupyter_notebook_to_file()
                    )
                )

            training_source = source_utils._make_class_source(obj)
            class_args = inspect.signature(obj.__class__.__init__).bind(
                obj, *obj._constructor_arguments[0], **obj._constructor_arguments[1]
            )

            class_creation = f"original_model = {obj.__class__.__name__}({','.join(map(str, class_args.args[1:]))})\n"
            command_str = (
                COMMAND_STRING_CLI
                + import_lines
                + COMMAND_STRING_CODE_SETUP
                + training_source
                + class_creation
                + COMMAND_STRING_CODE_APIS
            )

            obj._model = aiplatform.Model.upload(
                display_name="serving-test",
                artifact_uri=model_uri,
                serving_container_image_uri="gcr.io/google-appengine/python",
                serving_container_command=command_str.split("\n"),
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
            # TODO: cleanup model resource after endpoint is created
            endpoint = obj._model.deploy(machine_type="n1-standard-4")
            return endpoint.predict(*args, **kwargs)

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
            "google-cloud-aiplatform @ git+https://github.com/googleapis/python-aiplatform@refs/pull/628/head#egg=google-cloud-aiplatform",
        ]

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

    def batch_predict(self):
        """Make predictions on training data."""
        raise NotImplementedError("batch_predict is currently not implemented.")

    def eval(self):
        """Evaluate model."""
        raise NotImplementedError("eval is currently not implemented.")
