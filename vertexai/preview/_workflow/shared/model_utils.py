# -*- coding: utf-8 -*-

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

"""Model utils.

Push trained model from local to Model Registry, and pull Model Registry model
to local for uptraining.
"""

import os
from typing import Any, Optional, Union

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import utils
from google.cloud.aiplatform import jobs as aiplatform_jobs
import vertexai
from vertexai.preview._workflow import driver
from vertexai.preview._workflow.serialization_engine import (
    any_serializer,
    serializers_base,
)
from vertexai.preview._workflow.executor import training
from google.cloud.aiplatform.compat.types import job_state as gca_job_state


_SKLEARN_FILE_NAME = "model.pkl"
_TF_DIR_NAME = "saved_model"
_PYTORCH_FILE_NAME = "model.mar"
_REWRAPPER_NAME = "rewrapper"

_CUSTOM_JOB_DIR = "custom_job"
_INPUT_DIR = "input"
_OUTPUT_DIR = "output"
_OUTPUT_ESTIMATOR_DIR = "output_estimator"
_OUTPUT_PREDICTIONS_DIR = "output_predictions"


_LOGGER = base.Logger("vertexai.remote_execution")


def _get_model_file_from_image_uri(container_image_uri: str) -> str:
    """Gets the model file from the container image URI.

    Args:
        container_image_uri (str):
          The image URI of the container from the training job.

    Returns:
        str:
          The model file name.
    """

    # sklearn, TF, PyTorch model extensions for retraining.
    # PyTorch serv will need model.mar
    if "tf" in container_image_uri:
        return ""
    elif "sklearn" in container_image_uri:
        return _SKLEARN_FILE_NAME
    elif "pytorch" in container_image_uri:
        # Assume the pretrained model will be pulled for uptraining.
        return _PYTORCH_FILE_NAME
    else:
        raise ValueError("Support loading PyTorch, scikit-learn and TensorFlow only.")


def _verify_custom_job(job: aiplatform.CustomJob) -> None:
    """Verifies the provided CustomJob was created with SDK 2.0.

    Args:
        job (aiplatform.CustomJob):
          The CustomJob resource

    Raises:
        If the provided job wasn't created with SDK 2.0.
    """

    if (
        not job.labels.get("trained_by_vertex_ai")
        or job.labels.get("trained_by_vertex_ai") != "true"
    ):
        raise ValueError(
            "This job wasn't created with SDK remote training, or it was created with a Vertex SDK version <= 1.32.0"
        )


def _generate_remote_job_output_path(base_gcs_dir: str) -> str:
    """Generates the GCS output path of the remote training job.

    Args:
        base_gcs_dir (str):
          The base GCS directory for the remote training job.
    """
    return os.path.join(base_gcs_dir, _OUTPUT_DIR)


def _get_model_from_successful_custom_job(
    job_dir: str,
) -> Union["sklearn.base.BaseEstimator", "tf.Module", "torch.nn.Module"]:

    serializer = any_serializer.AnySerializer()

    model = serializer.deserialize(
        os.path.join(_generate_remote_job_output_path(job_dir), _OUTPUT_ESTIMATOR_DIR)
    )
    rewrapper = serializer.deserialize(
        os.path.join(_generate_remote_job_output_path(job_dir), _REWRAPPER_NAME)
    )
    rewrapper(model)
    return model


def _register_sklearn_model(
    model: "sklearn.base.BaseEstimator",  # noqa: F821
    serializer: serializers_base.Serializer,
    staging_bucket: str,
    rewrapper: Any,
) -> aiplatform.Model:
    """Register sklearn model."""
    unique_model_name = (
        f"vertex-ai-registered-sklearn-model-{utils.timestamped_unique_name()}"
    )
    gcs_dir = os.path.join(staging_bucket, unique_model_name)
    # serialize rewrapper
    file_path = os.path.join(gcs_dir, _REWRAPPER_NAME)
    serializer.serialize(rewrapper, file_path)
    # serialize model
    file_path = os.path.join(gcs_dir, _SKLEARN_FILE_NAME)
    serializer.serialize(model, file_path)

    container_image_uri = aiplatform.helpers.get_prebuilt_prediction_container_uri(
        framework="sklearn",
        framework_version="1.0",
    )

    vertex_model = aiplatform.Model.upload(
        display_name=unique_model_name,
        artifact_uri=gcs_dir,
        serving_container_image_uri=container_image_uri,
        labels={"registered_by_vertex_ai": "true"},
        sync=True,
    )

    return vertex_model


def _register_tf_model(
    model: "tensorflow.Module",  # noqa: F821
    serializer: serializers_base.Serializer,
    staging_bucket: str,
    rewrapper: Any,
    use_gpu: bool = False,
) -> aiplatform.Model:
    """Register TensorFlow model."""
    unique_model_name = (
        f"vertex-ai-registered-tensorflow-model-{utils.timestamped_unique_name()}"
    )
    gcs_dir = os.path.join(staging_bucket, unique_model_name)
    # serialize rewrapper
    file_path = os.path.join(gcs_dir, _TF_DIR_NAME + "/" + _REWRAPPER_NAME)
    serializer.serialize(rewrapper, file_path)
    # serialize model
    file_path = os.path.join(gcs_dir, _TF_DIR_NAME)
    # The default serialization format for keras models is "keras", but this
    # format is not yet supported by the model upload (eventually prediction
    # services). See the code here:
    # https://source.corp.google.com/piper///depot/google3/third_party/py/google/cloud/aiplatform/aiplatform/models.py;rcl=561677645;l=3141
    serializer.serialize(model, file_path, save_format="tf")

    container_image_uri = aiplatform.helpers.get_prebuilt_prediction_container_uri(
        framework="tensorflow",
        framework_version="2.11",
        accelerator="gpu" if use_gpu else "cpu",
    )

    vertex_model = aiplatform.Model.upload(
        display_name=unique_model_name,
        artifact_uri=file_path,
        serving_container_image_uri=container_image_uri,
        labels={"registered_by_vertex_ai": "true"},
        sync=True,
    )

    return vertex_model


def _register_pytorch_model(
    model: "torch.nn.Module",  # noqa: F821
    serializer: serializers_base.Serializer,
    staging_bucket: str,
    rewrapper: Any,
    use_gpu: bool = False,
) -> aiplatform.Model:
    """Register PyTorch model."""
    unique_model_name = (
        f"vertex-ai-registered-pytorch-model-{utils.timestamped_unique_name()}"
    )
    gcs_dir = os.path.join(staging_bucket, unique_model_name)

    # serialize rewrapper
    file_path = os.path.join(gcs_dir, _REWRAPPER_NAME)
    serializer.serialize(rewrapper, file_path)

    # This archive model is required for using prediction pre-built container
    archive_file_path = os.path.join(gcs_dir, _PYTORCH_FILE_NAME)
    serializer.serialize(model, archive_file_path)

    container_image_uri = aiplatform.helpers.get_prebuilt_prediction_container_uri(
        framework="pytorch",
        framework_version="1.12",
        accelerator="gpu" if use_gpu else "cpu",
    )

    vertex_model = aiplatform.Model.upload(
        display_name=unique_model_name,
        artifact_uri=gcs_dir,
        serving_container_image_uri=container_image_uri,
        labels={"registered_by_vertex_ai": "true"},
        sync=True,
    )

    return vertex_model


def register(
    model: Union[
        "sklearn.base.BaseEstimator", "tf.Module", "torch.nn.Module"  # noqa: F821
    ],
    use_gpu: bool = False,
) -> aiplatform.Model:
    """Registers a model and returns a Model representing the registered Model resource.

    Args:
        model (Union["sklearn.base.BaseEstimator", "tensorflow.Module", "torch.nn.Module"]):
            Required. An OSS model. Supported frameworks: sklearn, tensorflow, pytorch.
        use_gpu (bool):
            Optional. Whether to use GPU for model serving. Default to False.

    Returns:
        vertex_model (aiplatform.Model):
            Instantiated representation of the registered model resource.

    Raises:
        ValueError: if default staging bucket is not set
                    or if the framework is not supported.
    """
    staging_bucket = vertexai.preview.global_config.staging_bucket
    if not staging_bucket:
        raise ValueError(
            "A default staging bucket is required to upload the model file. "
            "Please call `vertexai.init(staging_bucket='gs://my-bucket')."
        )

    # Unwrap VertexRemoteFunctor before upload to Model Registry.
    rewrapper = driver._unwrapper(model)

    serializer = any_serializer.AnySerializer()
    try:
        if model.__module__.startswith("sklearn"):
            return _register_sklearn_model(model, serializer, staging_bucket, rewrapper)

        elif model.__module__.startswith("keras") or (
            hasattr(model, "_tracking_metadata")
        ):  # pylint: disable=protected-access
            return _register_tf_model(
                model, serializer, staging_bucket, rewrapper, use_gpu
            )

        elif "torch" in model.__module__ or (hasattr(model, "state_dict")):
            return _register_pytorch_model(
                model, serializer, staging_bucket, rewrapper, use_gpu
            )

        else:
            raise ValueError(
                "Support uploading PyTorch, scikit-learn and TensorFlow only."
            )
    except Exception as e:
        raise e
    finally:
        rewrapper(model)


def from_pretrained(
    *,
    model_name: Optional[str] = None,
    custom_job_name: Optional[str] = None,
) -> Union["sklearn.base.BaseEstimator", "tf.Module", "torch.nn.Module"]:  # noqa: F821
    """Pulls a model from Model Registry or from a CustomJob ID for retraining.

    The returned model is wrapped with a Vertex wrapper for running remote jobs on Vertex,
    unless an unwrapped model was registered to Model Registry.

    Args:
        model_name (str):
            Optional. The resource ID or fully qualified resource name of a registered model.
            Format: "12345678910" or
            "projects/123/locations/us-central1/models/12345678910@1". One of `model_name` or
            `custom_job_name` is required.
        custom_job_name (str):
            Optional. The resource ID or fully qualified resource name of a CustomJob created
            with Vertex SDK remote training. If the job has completed successfully, this will load
            the trained model created in the CustomJob. One of `model_name` or
            `custom_job_name` is required.

    Returns:
        model: local model for uptraining.

    Raises:
        ValueError:
            If registered model is not registered through `vertexai.preview.register`
            If custom job was not created with Vertex SDK remote training
            If both or neither model_name or custom_job_name are provided
    """
    if not model_name and not custom_job_name or (model_name and custom_job_name):
        raise ValueError("Exactly one of `model` or `custom_job` should be provided.")

    project = vertexai.preview.global_config.project
    location = vertexai.preview.global_config.location
    credentials = vertexai.preview.global_config.credentials

    if model_name:

        vertex_model = aiplatform.Model(
            model_name, project=project, location=location, credentials=credentials
        )
        if vertex_model.labels.get("registered_by_vertex_ai") != "true":
            raise ValueError(
                f"The model {model_name} is not registered through `vertex_ai.register`."
            )

        artifact_uri = vertex_model.uri
        model_file = _get_model_file_from_image_uri(
            vertex_model.container_spec.image_uri
        )

        serializer = any_serializer.AnySerializer()
        model = serializer.deserialize(os.path.join(artifact_uri, model_file))

        rewrapper = serializer.deserialize(os.path.join(artifact_uri, _REWRAPPER_NAME))

        # Rewrap model (in-place) for following remote training.
        rewrapper(model)
        return model

    if custom_job_name:
        job = aiplatform.CustomJob.get(
            custom_job_name, project=project, location=location, credentials=credentials
        )
        job_state = job.state

        _verify_custom_job(job)
        job_dir = job.job_spec.base_output_directory.output_uri_prefix

        if job_state in aiplatform_jobs._JOB_PENDING_STATES:
            _LOGGER.info(
                f"The CustomJob {job.name} is still running. When the job has completed successfully, your model will be returned."
            )
            training._get_remote_logs_until_complete(job)
            # Get the new job state after it has completed
            job_state = job.state

        if job_state == gca_job_state.JobState.JOB_STATE_SUCCEEDED:
            return _get_model_from_successful_custom_job(job_dir)
        else:
            raise ValueError(
                "The provided job did not complete successfully. Please provide a pending or successful customJob ID."
            )
