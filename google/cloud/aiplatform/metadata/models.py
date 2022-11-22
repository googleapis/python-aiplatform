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

import datetime
import pickle
import tempfile
from typing import Dict, Optional, Sequence, Union

from google.auth import credentials as auth_credentials
from google.cloud.aiplatform import base
from google.cloud.aiplatform import explain
from google.cloud.aiplatform import helpers
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import models
from google.cloud.aiplatform.metadata.schema import utils as schema_utils
from google.cloud.aiplatform.metadata.schema.google import (
    artifact_schema as google_artifact_schema,
)
from google.cloud.aiplatform.utils import gcs_utils


_LOGGER = base.Logger(__name__)

PICKLE_PROTOCOL = 4
MAX_INPUT_EXAMPLE_ROW = 5


def save_model(
    model: Union[
        "sklearn.base.BaseEstimator", "tf.Module", "xgb.Booster"  # noqa: F821
    ],
    artifact_id: Optional[str] = None,
    *,
    uri: Optional[str] = None,
    input_example: Union[list, dict, "pd.DataFrame", "np.ndarray"] = None,  # noqa: F821
    display_name: Optional[str] = None,
) -> google_artifact_schema.ExperimentModel:
    """Saves a ML model into a MLMD artifact.

    Supported model frameworks: sklearn, TensorFlow, XGBoost.

    Example usage:
        aiplatform.init(project="my-project", location="my-location", staging_bucket="gs://my-bucket")
        model = LinearRegression()
        model.fit(X, y)
        aiplatform.save_model(model, "my-sklearn-model")

    Args:
        model (Union[sklearn.base.BaseEstimator, tf.Module, xgb.Booster]):
            Requred. A machine learning model.
        artifact_id (str):
            Optional. The resource id of the artifact. This id must be globally unique
            in a metadataStore. It may be up to 63 characters, and valid characters
            are `[a-z0-9_-]`. The first character cannot be a number or hyphen.
        uri (str):
            Optional. A gcs directory to save the model file.
            If not set, make sure to set "staging_bucket" when init aiplatform.
            Default uri is "gs://default-staging-bucket/ml-framework-model-timestamp/".
        input_example (Union[list, dict, pd.DataFrame, np.ndarray]):
            Optional. An example of a valid model input. Will be stored as a yaml file
            in the gcs uri. A list, dict, or pd.DataFrame will be recognized as a
            column-based input and saved by the Pandas split-oriented format.
            A np.ndarray will be recognized as atensor-based input.
        display_name (str):
            Optional. The display name of the artifact.

    Returns:
        An ExperimentModel instance.

    Raises:
        ValueError: if model type is not supported.
                    or if both "uri" and default staging bucket are not set.
    """
    try:
        import sklearn
    except ImportError:
        pass
    else:
        if isinstance(model, sklearn.base.BaseEstimator):
            return _save_sklearn_model(
                model=model,
                artifact_id=artifact_id,
                uri=uri,
                input_example=input_example,
                display_name=display_name,
            )

    try:
        import tensorflow as tf
    except ImportError:
        pass
    else:
        if isinstance(model, tf.Module):
            return None

    try:
        import xgboost as xgb
    except ImportError:
        pass
    else:
        if isinstance(model, xgb.Booster):
            return None

    raise ValueError(f"Model type {model.__class__.__name__} not supported.")


def _save_input_example(
    input_example: Union[list, dict, "pd.DataFrame", "np.ndarray"],  # noqa: F821
    path: str,
):
    """Saves an input example into a yaml file in the given path.

    Supports column-based inputs(list, dict, or pd.DataFrame) and tensor-based
    inputs(np.ndarray or dict of np.ndarray).

    Args:
        input_example (Union[list, dict, np.ndarray, pd.DataFrame]):
            Required. An input example to save. A list, dict, or pd.DataFrame
            will be recognized as a column-based input and saved by the Pandas
            split-oriented format. A np.ndarray will be recognized as a
            tensor-based input.
        path (str):
            Required. The directory that the example is saved to.
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError(
            "numpy is not installed and is required for saving input examples."
        ) from None

    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is not installed and is required for saving input examples."
        ) from None

    try:
        import yaml
    except ImportError:
        raise ImportError(
            "PyYAML is not installed and is required for saving input examples."
        ) from None

    if isinstance(input_example, np.ndarray):
        example = {
            f"example {i+1}": input_example[i]
            for i in range(len(input_example))
            if i < MAX_INPUT_EXAMPLE_ROW
        }
    elif isinstance(input_example, list):
        if all(np.isscalar(x) for x in input_example):
            example = pd.DataFrame([input_example])
        else:
            example = pd.DataFrame(input_example)
    elif isinstance(input_example, dict):
        if all(np.isscalar(x) for x in input_example.values()):
            example = pd.DataFrame([input_example])
        else:
            example = pd.DataFrame(input_example)
    else:
        raise ValueError(f"Input example type '{type(input_example)}' not supported.")

    if isinstance(example, pd.DataFrame):
        example = example.to_dict(orient="split")
        example.pop("index", None)

    example_file = "/".join([path, "instance.yaml"])
    with open(example_file, "w") as file:
        yaml.dump({"example": example}, file, default_flow_style=False)


def _save_sklearn_model(
    model: "sklearn.base.BaseEstimator",  # noqa: F821
    artifact_id: Optional[str] = None,
    uri: Optional[str] = None,
    input_example: Union[list, dict, "pd.DataFrame", "np.ndarray"] = None,  # noqa: F821
    display_name: Optional[str] = None,
) -> google_artifact_schema.ExperimentModel:
    """Saves a sklearn model into a MLMD artifact.

    Args:
        model (sklearn.base.BaseEstimator):
            Requred. A sklearn model.
        artifact_id (str):
            Optional. The resource id of the artifact. This id must be globally unique
            in a metadataStore. It may be up to 63 characters, and valid characters
            are `[a-z0-9_-]`. The first character cannot be a number or hyphen.
        uri (str):
            Optional. A gcs directory to save the model file.
            If not set, make sure to set "staging_bucket" when init aiplatform.
            Default uri is "gs://default-staging-bucket/ml-framework-model-timestamp/".
        input_example (Union[list, dict, pd.DataFrame, np.ndarray]):
            Optional. An example of a valid model input. Will be stored as a yaml file
            in the gcs uri. A list, dict, or pd.DataFrame will be recognized as a
            column-based input and saved by the Pandas split-oriented format.
            A np.ndarray will be recognized as atensor-based input.
        display_name (str):
            Optional. The display name of the artifact.

    Returns:
        An ExperimentModel instance.

    Raises:
        ImportError: if sklearn is not installed.
        ValueError: if model type is not sklearn.
                    or if both "uri" and default staging bucket are not set.
    """
    try:
        import sklearn
    except ImportError:
        raise ImportError("sklearn is not installed and is required for saving models.")

    if not isinstance(model, sklearn.base.BaseEstimator):
        raise ValueError(
            f"Must be a sklearn model. Got {model.__class__.__name__} model."
        )

    if not uri:
        staging_bucket = initializer.global_config.staging_bucket
        if not staging_bucket:
            raise ValueError(
                "No staging bucket set. Make sure to call "
                "aiplatform.init(staging_bucket='gs://my-bucket') "
                "or specify the 'uri' when saving the model. "
            )
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        uri = f"{staging_bucket}/sklearn-model-{timestamp}"

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_model_file = "/".join([temp_dir, "model.pkl"])
        with open(temp_model_file, "wb") as model_file:
            pickle.dump(model, model_file, protocol=PICKLE_PROTOCOL)

        if input_example is not None:
            _save_input_example(input_example, temp_dir)
            predict_schemata = schema_utils.PredictSchemata(
                instance_schema_uri="/".join([uri, "instance.yaml"])
            )
        else:
            predict_schemata = None
        gcs_utils.upload_to_gcs(temp_dir, uri)

    model_artifact = google_artifact_schema.ExperimentModel(
        framework_name="sklearn",
        framework_version=sklearn.__version__,
        model_file="model.pkl",
        model_class=model.__class__.__name__,
        predict_schemata=predict_schemata,
        artifact_id=artifact_id,
        uri=uri,
        display_name=display_name,
    )
    model_artifact.create()
    return model_artifact


def load_model(
    model: Union[str, google_artifact_schema.ExperimentModel]
) -> Union["sklearn.base.BaseEstimator", "tf.Module", "xgb.Booster"]:  # noqa: F821
    """Retrieves the original ML model from an ExperimentModel resource.

    Example usage:
        model = aiplatform.load("my-sklearn-model")
        pred_y = model.predict(test_X)

    Args:
        model (Union[str, google_artifact_schema.ExperimentModel]):
            Required. The id or ExperimentModel instance for the model.

    Returns:
        The original ML model.

    Raises:
        ValueError: if model type is not supported.
    """
    if isinstance(model, str):
        model = google_artifact_schema.ExperimentModel.get(model)
    if model.framework_name == "sklearn":
        return _load_sklearn_model(model)
    elif model.framework_name == "xgboost":
        return None
    elif model.framework_name.startswith("tensorflow"):
        return None
    else:
        raise ValueError(f"Model type {model.framwork_name} not supported.")


def _load_sklearn_model(
    model: google_artifact_schema.ExperimentModel,
) -> "sklearn.base.BaseEstimator":  # noqa: F821
    """Retrieves the sklearn model instance from the model saved in Vertex.

    Args:
        model (google_artifact_schema.ExperimentModel):
            Required. An ExperimentModel instance that saves a sklearn model.

    Returns:
        The sklearn model instance.

    Raises:
        ValueError: if the ExperimentModel instance saves a model for another framework.
        ImportError: if sklearn is not installed.
    """
    if model.framework_name != "sklearn":
        raise ValueError(
            f"The ExperimentModel instance must save a sklearn model. "
            f"Got an instance that saves a {model.framework_name} model."
        )
    try:
        import sklearn
    except ImportError:
        raise ImportError(
            "sklearn is not installed and is required for loading models."
        ) from None

    if sklearn.__version__ < model.framework_version:
        _LOGGER.warning(
            f"The original model was saved via sklearn {model.framework_version}. "
            f"You are using sklearn {sklearn.__version__}."
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        source_file_uri = "/".join([model.uri, "model.pkl"])
        destination_file_path = "/".join([temp_dir, "model.pkl"])
        gcs_utils.download_from_gcs(source_file_uri, destination_file_path)
        with open(destination_file_path, "rb") as model_file:
            sk_model = pickle.load(model_file)

    return sk_model


def register_model(
    model: Union[str, google_artifact_schema.ExperimentModel],
    *,
    model_id: Optional[str] = None,
    parent_model: Optional[str] = None,
    use_gpu: bool = False,
    is_default_version: bool = True,
    version_aliases: Optional[Sequence[str]] = None,
    version_description: Optional[str] = None,
    display_name: Optional[str] = None,
    description: Optional[str] = None,
    labels: Optional[Dict[str, str]] = None,
    serving_container_image_uri: Optional[str] = None,
    serving_container_predict_route: Optional[str] = None,
    serving_container_health_route: Optional[str] = None,
    serving_container_command: Optional[Sequence[str]] = None,
    serving_container_args: Optional[Sequence[str]] = None,
    serving_container_environment_variables: Optional[Dict[str, str]] = None,
    serving_container_ports: Optional[Sequence[int]] = None,
    instance_schema_uri: Optional[str] = None,
    parameters_schema_uri: Optional[str] = None,
    prediction_schema_uri: Optional[str] = None,
    explanation_metadata: Optional[explain.ExplanationMetadata] = None,
    explanation_parameters: Optional[explain.ExplanationParameters] = None,
    project: Optional[str] = None,
    location: Optional[str] = None,
    credentials: Optional[auth_credentials.Credentials] = None,
    encryption_spec_key_name: Optional[str] = None,
    staging_bucket: Optional[str] = None,
    sync: Optional[bool] = True,
    upload_request_timeout: Optional[float] = None,
) -> models.Model:
    """Register an ExperimentModel to Model Registry and returns a Model representing the registered Model resource.

    Example usage:
        registered_model = aiplatform.register_model("my-sklearn-model")
        registered_model.deploy(endpoint=my_endpoint)

    Args:
        model (Union[str, google_artifact_schema.ExperimentModel]):
            Required. The id or ExperimentModel instance for the model.
        model_id (str):
            Optional. The ID to use for the registered Model, which will
            become the final component of the model resource name.
            This value may be up to 63 characters, and valid characters
            are `[a-z0-9_-]`. The first character cannot be a number or hyphen.
        parent_model (str):
            Optional. The resource name or model ID of an existing model that the
            newly-registered model will be a version of.
            Only set this field when uploading a new version of an existing model.
        use_gpu (str):
            Optional. Whether or not to use GPUs for the serving container. Only
            specify this argument when registering a Tensorflow model and
            'serving_container_image_uri' is not specified.
        is_default_version (bool):
            Optional. When set to True, the newly registered model version will
            automatically have alias "default" included. Subsequent uses of
            this model without a version specified will use this "default" version.

            When set to False, the "default" alias will not be moved.
            Actions targeting the newly-registered model version will need
            to specifically reference this version by ID or alias.

            New model uploads, i.e. version 1, will always be "default" aliased.
        version_aliases (Sequence[str]):
            Optional. User provided version aliases so that a model version
            can be referenced via alias instead of auto-generated version ID.
            A default version alias will be created for the first version of the model.

            The format is [a-z][a-zA-Z0-9-]{0,126}[a-z0-9]
        version_description (str):
            Optional. The description of the model version being uploaded.
        display_name (str):
            Optional. The display name of the Model. The name can be up to 128
            characters long and can be consist of any UTF-8 characters.
        description (str):
            Optional. The description of the model.
        labels (Dict[str, str]):
            Optional. The labels with user-defined metadata to
            organize your Models.
            Label keys and values can be no longer than 64
            characters (Unicode codepoints), can only
            contain lowercase letters, numeric characters,
            underscores and dashes. International characters
            are allowed.
            See https://goo.gl/xmQnxf for more information
            and examples of labels.
        serving_container_image_uri (str):
            Optional. The URI of the Model serving container. A pre-built container
            <https://cloud.google.com/vertex-ai/docs/predictions/pre-built-containers>
            is automatically chosen based on the model's framwork. Set this field to
            override the default pre-built container.
        serving_container_predict_route (str):
            Optional. An HTTP path to send prediction requests to the container, and
            which must be supported by it. If not specified a default HTTP path will
            be used by Vertex AI.
        serving_container_health_route (str):
            Optional. An HTTP path to send health check requests to the container, and which
            must be supported by it. If not specified a standard HTTP path will be
            used by Vertex AI.
        serving_container_command (Sequence[str]):
            Optional. The command with which the container is run. Not executed within a
            shell. The Docker image's ENTRYPOINT is used if this is not provided.
            Variable references $(VAR_NAME) are expanded using the container's
            environment. If a variable cannot be resolved, the reference in the
            input string will be unchanged. The $(VAR_NAME) syntax can be escaped
            with a double $$, ie: $$(VAR_NAME). Escaped references will never be
            expanded, regardless of whether the variable exists or not.
        serving_container_args (Sequence[str]):
            Optional. The arguments to the command. The Docker image's CMD is used if this is
            not provided. Variable references $(VAR_NAME) are expanded using the
            container's environment. If a variable cannot be resolved, the reference
            in the input string will be unchanged. The $(VAR_NAME) syntax can be
            escaped with a double $$, ie: $$(VAR_NAME). Escaped references will
            never be expanded, regardless of whether the variable exists or not.
        serving_container_environment_variables (Dict[str, str]):
            Optional. The environment variables that are to be present in the container.
            Should be a dictionary where keys are environment variable names
            and values are environment variable values for those names.
        serving_container_ports (Sequence[int]):
            Optional. Declaration of ports that are exposed by the container. This field is
            primarily informational, it gives Vertex AI information about the
            network connections the container uses. Listing or not a port here has
            no impact on whether the port is actually exposed, any port listening on
            the default "0.0.0.0" address inside a container will be accessible from
            the network.
        instance_schema_uri (str):
            Optional. Points to a YAML file stored on Google Cloud
            Storage describing the format of a single instance, which
            are used in
            ``PredictRequest.instances``,
            ``ExplainRequest.instances``
            and
            ``BatchPredictionJob.input_config``.
            The schema is defined as an OpenAPI 3.0.2 `Schema
            Object <https://tinyurl.com/y538mdwt#schema-object>`__.
            AutoML Models always have this field populated by AI
            Platform. Note: The URI given on output will be immutable
            and probably different, including the URI scheme, than the
            one given on input. The output URI will point to a location
            where the user only has a read access.
        parameters_schema_uri (str):
            Optional. Points to a YAML file stored on Google Cloud
            Storage describing the parameters of prediction and
            explanation via
            ``PredictRequest.parameters``,
            ``ExplainRequest.parameters``
            and
            ``BatchPredictionJob.model_parameters``.
            The schema is defined as an OpenAPI 3.0.2 `Schema
            Object <https://tinyurl.com/y538mdwt#schema-object>`__.
            AutoML Models always have this field populated by AI
            Platform, if no parameters are supported it is set to an
            empty string. Note: The URI given on output will be
            immutable and probably different, including the URI scheme,
            than the one given on input. The output URI will point to a
            location where the user only has a read access.
        prediction_schema_uri (str):
            Optional. Points to a YAML file stored on Google Cloud
            Storage describing the format of a single prediction
            produced by this Model, which are returned via
            ``PredictResponse.predictions``,
            ``ExplainResponse.explanations``,
            and
            ``BatchPredictionJob.output_config``.
            The schema is defined as an OpenAPI 3.0.2 `Schema
            Object <https://tinyurl.com/y538mdwt#schema-object>`__.
            AutoML Models always have this field populated by AI
            Platform. Note: The URI given on output will be immutable
            and probably different, including the URI scheme, than the
            one given on input. The output URI will point to a location
            where the user only has a read access.
        explanation_metadata (aiplatform.explain.ExplanationMetadata):
            Optional. Metadata describing the Model's input and output for explanation.
            `explanation_metadata` is optional while `explanation_parameters` must be
            specified when used.
            For more details, see `Ref docs <http://tinyurl.com/1igh60kt>`
        explanation_parameters (aiplatform.explain.ExplanationParameters):
            Optional. Parameters to configure explaining for Model's predictions.
            For more details, see `Ref docs <http://tinyurl.com/1an4zake>`
        project: Optional[str]=None,
            Project to upload this model to. Overrides project set in
            aiplatform.init.
        location: Optional[str]=None,
            Location to upload this model to. Overrides location set in
            aiplatform.init.
        credentials: Optional[auth_credentials.Credentials]=None,
            Custom credentials to use to upload this model. Overrides credentials
            set in aiplatform.init.
        encryption_spec_key_name (Optional[str]):
            Optional. The Cloud KMS resource identifier of the customer
            managed encryption key used to protect the model. Has the
            form
            ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
            The key needs to be in the same region as where the compute
            resource is created.

            If set, this Model and all sub-resources of this Model will be secured by this key.

            Overrides encryption_spec_key_name set in aiplatform.init.
        staging_bucket (str):
            Optional. Bucket to stage local model artifacts. Overrides
            staging_bucket set in aiplatform.init.
        sync (bool):
            Optional. Whether to execute this method synchronously. If False,
            this method will unblock and it will be executed in a concurrent Future.
        upload_request_timeout (float):
            Optional. The timeout for the upload request in seconds.

    Returns:
        model (aiplatform.Model):
            Instantiated representation of the registered model resource.

    Raises:
        ValueError: If the model doesn't have a pre-built container that is
                    suitable for its framework and 'serving_container_image_uri'
                    is not set.
    """
    if isinstance(model, str):
        model = google_artifact_schema.ExperimentModel.get(model)
    artifact_uri = model.uri
    framework = model.framework_name.split(".")[0]
    framework_version = model.framework_version

    if not serving_container_image_uri:
        if framework == "tensorflow" and use_gpu:
            accelerator = "gpu"
        else:
            accelerator = "cpu"
        serving_container_image_uri = helpers.get_closest_match_prebuilt_container_uri(
            framework=framework,
            framework_version=framework_version,
            region=location,
            accelerator=accelerator,
        )

    return models.Model.upload(
        serving_container_image_uri=serving_container_image_uri,
        artifact_uri=artifact_uri,
        model_id=model_id,
        parent_model=parent_model,
        is_default_version=is_default_version,
        version_aliases=version_aliases,
        version_description=version_description,
        display_name=display_name,
        description=description,
        labels=labels,
        serving_container_predict_route=serving_container_predict_route,
        serving_container_health_route=serving_container_health_route,
        serving_container_command=serving_container_command,
        serving_container_args=serving_container_args,
        serving_container_environment_variables=serving_container_environment_variables,
        serving_container_ports=serving_container_ports,
        instance_schema_uri=instance_schema_uri,
        parameters_schema_uri=parameters_schema_uri,
        prediction_schema_uri=prediction_schema_uri,
        explanation_metadata=explanation_metadata,
        explanation_parameters=explanation_parameters,
        project=project,
        location=location,
        credentials=credentials,
        encryption_spec_key_name=encryption_spec_key_name,
        staging_bucket=staging_bucket,
        sync=sync,
        upload_request_timeout=upload_request_timeout,
    )
