"""Regsiter XGBoost for Ray on Vertex AI."""

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

import logging
import os
import pickle
import tempfile
from typing import Optional, TYPE_CHECKING

from google.cloud import aiplatform
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.utils import gcs_utils
from google.cloud.aiplatform.preview.vertex_ray.predict.util import constants
from google.cloud.aiplatform.preview.vertex_ray.predict.util import (
    predict_utils,
)


try:
    from ray.train import xgboost as ray_xgboost

    if TYPE_CHECKING:
        import xgboost

except ModuleNotFoundError as mnfe:
    raise ModuleNotFoundError("XGBoost isn't installed.") from mnfe


def register_xgboost(
    checkpoint: "ray_xgboost.XGBoostCheckpoint",
    artifact_uri: Optional[str] = None,
    display_name: Optional[str] = None,
    **kwargs,
) -> aiplatform.Model:
    """Uploads a Ray XGBoost Checkpoint as XGBoost Model to Model Registry.

    Example usage:
        from vertex_ray.predict import xgboost
        from ray.train.xgboost import XGBoostCheckpoint

        trainer = XGBoostTrainer(...)
        result = trainer.fit()
        xgboost_checkpoint = XGBoostCheckpoint.from_checkpoint(result.checkpoint)

        my_model = xgboost.register_xgboost(
            checkpoint=xgboost_checkpoint,
            artifact_uri="gs://{gcs-bucket-name}/path/to/store",
            display_name="my-ray-on-vertex-xgboost-model",
        )


    Args:
        checkpoint: XGBoostCheckpoint instance.
        artifact_uri (str):
            The path to the directory where Model Artifacts will be saved. If
            not set, will use staging bucket set in aiplatform.init().
        display_name (str):
            Optional. The display name of the Model. The name can be up to 128
            characters long and can be consist of any UTF-8 characters.
        **kwargs:
            Any kwargs will be passed to aiplatform.Model registration.

    Returns:
        model (aiplatform.Model):
                Instantiated representation of the uploaded model resource.

    Raises:
        ValueError: Invalid Argument.
    """
    artifact_uri = artifact_uri or initializer.global_config.staging_bucket
    predict_utils.validate_artifact_uri(artifact_uri)
    display_model_name = (
        (f"ray-on-vertex-registered-xgboost-model-{utils.timestamped_unique_name()}")
        if display_name is None
        else display_name
    )
    model = _get_xgboost_model_from(checkpoint)

    model_dir = os.path.join(artifact_uri, display_model_name)
    file_path = os.path.join(model_dir, constants._PICKLE_FILE_NAME)

    with tempfile.NamedTemporaryFile(suffix=constants._PICKLE_EXTENTION) as temp_file:
        pickle.dump(model, temp_file)
        gcs_utils.upload_to_gcs(temp_file.name, file_path)
        return aiplatform.Model.upload_xgboost_model_file(
            model_file_path=temp_file.name,
            display_name=display_model_name,
            xgboost_version=constants._XGBOOST_VERSION,
            **kwargs,
        )


def _get_xgboost_model_from(
    checkpoint: "ray_xgboost.XGBoostCheckpoint",
) -> "xgboost.Booster":
    """Converts a XGBoostCheckpoint to XGBoost model.

    Args:
        checkpoint: XGBoostCheckpoint instance.

    Returns:
        A XGBoost core Booster

    Raises:
        ValueError: Invalid Argument.
    """
    if not isinstance(checkpoint, ray_xgboost.XGBoostCheckpoint):
        raise ValueError(
            "[Ray on Vertex AI]: arg checkpoint should be a"
            " ray.train.xgboost.XGBoostCheckpoint instance"
        )
    if checkpoint.get_preprocessor() is not None:
        logging.warning(
            "Checkpoint contains preprocessor. However, converting from a Ray"
            " Checkpoint to framework specific model does NOT support"
            " preprocessing. The model will be exported without preprocessors."
        )
    return checkpoint.get_model()
