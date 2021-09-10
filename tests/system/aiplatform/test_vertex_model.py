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

import pandas as pd
import torch

from google.cloud.aiplatform.experimental.vertex_model import base


class LinearRegression(base.VertexModel, torch.nn.Module):
    def __init__(self, input_size: int, output_size: int):
        base.VertexModel.__init__(self, input_size=input_size, output_size=output_size)
        torch.nn.Module.__init__(self)
        self.linear = torch.nn.Linear(input_size, output_size)

    def forward(self, x):
        return self.linear(x)

    def train_loop(self, dataloader, loss_fn, optimizer):
        for batch, (X, y) in enumerate(dataloader):
            pred = self.predict(X.float())
            loss = loss_fn(pred.float(), y.float())

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    def fit(
        self, data: pd.DataFrame, target_column: str, epochs: int, learning_rate: float
    ):
        feature_columns = list(data.columns)
        feature_columns.remove(target_column)

        features = torch.tensor(data[feature_columns].values)
        target = torch.tensor(data[target_column].values)

        dataloader = torch.utils.data.DataLoader(
            torch.utils.data.TensorDataset(features, target),
            batch_size=10,
            shuffle=True,
        )

        loss_fn = torch.nn.MSELoss()
        optimizer = torch.optim.SGD(self.parameters(), lr=learning_rate)

        for t in range(epochs):
            self.train_loop(dataloader, loss_fn, optimizer)

    def predict(self, data):
        return self.forward(data)

    # Implementation of predict_payload_to_predict_input(), which converts a predict_payload object to predict() inputs
    def predict_payload_to_predict_input(self, instances):
        feature_columns = ["feat_1", "feat_2"]
        data = pd.DataFrame(instances, columns=feature_columns)
        torch_tensor = torch.tensor(data[feature_columns].values).type(
            torch.FloatTensor
        )
        return torch_tensor

    # Implementation of predict_input_to_predict_payload(), which converts predict() inputs to a predict_payload object
    def predict_input_to_predict_payload(self, parameter):
        return parameter.tolist()

    # Implementation of predict_output_to_predict_payload(), which converts the predict() output to a predict_payload object
    def predict_output_to_predict_payload(self, output):
        return output.tolist()

    # Implementation of predict_payload_to_predict_output, which takes a predict_payload object containing predictions and
    # converts it to the type of output expected by the user-written class.
    def predict_payload_to_predict_output(self, predictions):
        data = pd.DataFrame(predictions)
        torch_tensor = torch.tensor(data.values).type(torch.FloatTensor)
        return torch_tensor
