"""Test utils for Prediction Tests.
"""

import numpy as np
import sklearn
from sklearn import linear_model
import tensorflow as tf
import torch
import xgboost


def create_tf_model() -> tf.keras.Model:
    """Create toy neural network : 1-layer."""
    model = tf.keras.Sequential(
        [tf.keras.layers.Dense(1, activation="linear", input_shape=(4,))]
    )
    model.compile(optimizer="Adam", loss="mean_squared_error", metrics=["mse"])
    return model


def train_tf_model(model: tf.keras.Model) -> None:
    """Trains a Keras Model."""
    n = 1
    train_x = np.random.normal(0, 1, size=(n, 4))
    train_y = np.random.uniform(0, 1, size=(n, 1))
    model.fit(train_x, train_y, epochs=1)


def get_tensorflow_trained_model() -> tf.keras.Model:
    """Returns a tensorflow trained model."""
    model = create_tf_model()
    train_tf_model(model)
    return model


def get_sklearn_estimator() -> sklearn.base.BaseEstimator:
    """Returns a sklearn estimator."""
    estimator = linear_model.LinearRegression()
    x = [[1, 2], [3, 4], [5, 6]]
    y = [7, 8, 9]
    estimator.fit(x, y)
    return estimator


def get_xgboost_model() -> xgboost.XGBClassifier:
    train_x = np.array([[1, 2], [3, 4]])
    train_y = np.array([0, 1])
    return xgboost.XGBClassifier().fit(train_x, train_y)


input_size = 1
layer_size = 1
output_size = 1
num_epochs = 1


class TorchModel(torch.nn.Module):
    def __init__(self):
        super(TorchModel, self).__init__()
        self.layer1 = torch.nn.Linear(input_size, layer_size)
        self.relu = torch.nn.ReLU()
        self.layer2 = torch.nn.Linear(layer_size, output_size)

    def forward(self, input_data):
        return self.layer2(self.relu(self.layer1(input_data)))


def get_pytorch_trained_model() -> torch.nn.Module:
    """Returns a pytorch trained model."""
    return TorchModel()
