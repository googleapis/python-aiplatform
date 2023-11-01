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

import os
from unittest import mock

from google.cloud import aiplatform
import vertexai
from tests.system.aiplatform import e2e_base
from vertexai.preview._workflow.executor import training
from vertexai.preview._workflow.serialization_engine import (
    serializers,
)
import pytest
from sklearn.datasets import load_iris
import torch
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


@mock.patch.object(
    training,
    "VERTEX_AI_DEPENDENCY_PATH",
    "google-cloud-aiplatform[preview] @ git+https://github.com/googleapis/"
    f"python-aiplatform.git@{os.environ['KOKORO_GIT_COMMIT']}"
    if os.environ.get("KOKORO_GIT_COMMIT")
    else "google-cloud-aiplatform[preview] @ git+https://github.com/googleapis/python-aiplatform.git@main",
)
@mock.patch.object(
    training,
    "VERTEX_AI_DEPENDENCY_PATH_AUTOLOGGING",
    "google-cloud-aiplatform[preview,autologging] @ git+https://github.com/googleapis/"
    f"python-aiplatform.git@{os.environ['KOKORO_GIT_COMMIT']}"
    if os.environ.get("KOKORO_GIT_COMMIT")
    else "google-cloud-aiplatform[preview,autologging] @ git+https://github.com/googleapis/python-aiplatform.git@main",
)
# To avoid flaky test due to autolog enabled in parallel tests
@mock.patch.object(vertexai.preview.initializer._Config, "autolog", False)
@pytest.mark.usefixtures(
    "prepare_staging_bucket", "delete_staging_bucket", "tear_down_resources"
)
class TestRemoteExecutionPytorch(e2e_base.TestEndToEnd):

    _temp_prefix = "temp-vertexai-remote-execution"

    def test_remote_execution_pytorch(self, shared_state):
        # Define the pytorch custom model
        class TorchLogisticRegression(vertexai.preview.VertexModel, torch.nn.Module):
            def __init__(self, input_size: int, output_size: int):
                torch.nn.Module.__init__(self)
                vertexai.preview.VertexModel.__init__(self)
                self.linear = torch.nn.Linear(input_size, output_size)
                self.softmax = torch.nn.Softmax(dim=1)

            def forward(self, x):
                return self.softmax(self.linear(x))

            @vertexai.preview.developer.mark.train()
            def train(self, dataloader, num_epochs, lr):
                criterion = torch.nn.CrossEntropyLoss()
                optimizer = torch.optim.SGD(self.parameters(), lr=lr)

                for t in range(num_epochs):
                    for idx, batch in enumerate(dataloader):
                        # move data to the same device as model
                        device = next(self.parameters()).device
                        x, y = batch[0].to(device), batch[1].to(device)

                        optimizer.zero_grad()
                        pred = self(x)
                        loss = criterion(pred, y)
                        loss.backward()
                        optimizer.step()

            @vertexai.preview.developer.mark.predict()
            def predict(self, X):
                X = torch.tensor(X).to(torch.float32)
                with torch.no_grad():
                    pred = torch.argmax(self(X), dim=1)
                return pred

        # Initialize vertexai
        vertexai.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            staging_bucket=f"gs://{shared_state['staging_bucket_name']}",
        )

        # Prepare dataset
        dataset = load_iris()

        X, X_retrain, y, y_retrain = train_test_split(
            dataset.data, dataset.target, test_size=0.60, random_state=42
        )
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=42
        )

        transformer = StandardScaler()
        X_train = transformer.fit_transform(X_train)
        X_test = transformer.transform(X_test)
        X_retrain = transformer.transform(X_retrain)

        train_loader = torch.utils.data.DataLoader(
            torch.utils.data.TensorDataset(
                torch.tensor(X_train).to(torch.float32),
                torch.tensor(y_train),
            ),
            batch_size=10,
            shuffle=True,
        )

        retrain_loader = torch.utils.data.DataLoader(
            torch.utils.data.TensorDataset(
                torch.tensor(X_retrain).to(torch.float32),
                torch.tensor(y_retrain),
            ),
            batch_size=10,
            shuffle=True,
        )

        # Remote CPU training on Torch custom model
        vertexai.preview.init(remote=True)

        model = TorchLogisticRegression(4, 3)
        model.train.vertex.remote_config.display_name = self._make_display_name(
            "pytorch-cpu-training"
        )
        model.train(train_loader, num_epochs=100, lr=0.05)

        # Assert the right serializer is being used
        remote_job = aiplatform.CustomJob.list(
            filter=f'display_name="{model.train.vertex.remote_config.display_name}"'
        )[0]
        base_path = remote_job.job_spec.base_output_directory.output_uri_prefix

        input_estimator_metadata = serializers._get_metadata(
            os.path.join(base_path, "input/input_estimator")
        )
        assert input_estimator_metadata["serializer"] == "TorchModelSerializer"

        output_estimator_metadata = serializers._get_metadata(
            os.path.join(base_path, "output/output_estimator")
        )
        assert output_estimator_metadata["serializer"] == "TorchModelSerializer"

        train_loader_metadata = serializers._get_metadata(
            os.path.join(base_path, "input/dataloader")
        )
        assert train_loader_metadata["serializer"] == "TorchDataLoaderSerializer"

        shared_state["resources"] = [remote_job]

        # Remote prediction on Torch custom model
        model.predict.vertex.remote_config.display_name = self._make_display_name(
            "pytorch-prediction"
        )
        model.predict(X_test)

        # Add prediction job to teardown resource
        remote_job = aiplatform.CustomJob.list(
            filter=f'display_name="{model.predict.vertex.remote_config.display_name}"'
        )[0]
        shared_state["resources"].append(remote_job)

        # Register trained model
        registered_model = vertexai.preview.register(model)
        shared_state["resources"].append(registered_model)

        # Load the registered model
        pulled_model = vertexai.preview.from_pretrained(
            model_name=registered_model.resource_name
        )

        # Uptrain the pretrained model on CPU
        pulled_model.train.vertex.remote_config.display_name = self._make_display_name(
            "pytorch-cpu-uptraining"
        )
        pulled_model.train(retrain_loader, num_epochs=100, lr=0.05)

        # Assert the right serializer is being used
        remote_job = aiplatform.CustomJob.list(
            filter=f'display_name="{pulled_model.train.vertex.remote_config.display_name}"'
        )[0]
        base_path = remote_job.job_spec.base_output_directory.output_uri_prefix

        input_estimator_metadata = serializers._get_metadata(
            os.path.join(base_path, "input/input_estimator")
        )
        assert input_estimator_metadata["serializer"] == "TorchModelSerializer"

        output_estimator_metadata = serializers._get_metadata(
            os.path.join(base_path, "output/output_estimator")
        )
        assert output_estimator_metadata["serializer"] == "TorchModelSerializer"

        train_loader_metadata = serializers._get_metadata(
            os.path.join(base_path, "input/dataloader")
        )
        assert train_loader_metadata["serializer"] == "TorchDataLoaderSerializer"

        shared_state["resources"].append(remote_job)
