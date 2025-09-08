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

import collections
import explainable_ai_sdk
import os
import pandas as pd
import pytest
import sys
import tensorflow as tf

from google.auth import credentials as auth_credentials
from google.cloud import aiplatform
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.compat.types import (
    endpoint as gca_endpoint,
    prediction_service as gca_prediction_service,
    explanation as gca_explanation,
)

# TODO (b/301592787): update testing_extra_require deps to numpy >= 1.22.0 when it doesn't cause conflicts
try:
    from lit_nlp import notebook  # noqa: F401
except ImportError:
    pytest.skip(
        "Skipping test_explain_list due to dependency conflict with numpy",
        allow_module_level=True,
    )

from google.cloud.aiplatform.explain.lit import (  # noqa: E402
    create_lit_dataset,
    create_lit_model,
    create_lit_model_from_endpoint,
    open_lit,
    set_up_and_open_lit,
)
from google.cloud.aiplatform.compat.services import (  # noqa: E402
    endpoint_service_client,
    prediction_service_client,
)
from importlib import reload  # noqa: E402
from lit_nlp.api import types as lit_types  # noqa: E402
from lit_nlp import notebook  # noqa: E402, F811
from unittest import mock  # noqa: E402

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_ID = "1028944691210842416"
_TEST_ID_2 = "4366591682456584192"
_TEST_ID_3 = "5820582938582924817"
_TEST_DISPLAY_NAME = "test-display-name"
_TEST_DISPLAY_NAME_2 = "test-display-name-2"
_TEST_DISPLAY_NAME_3 = "test-display-name-3"
_TEST_ENDPOINT_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/endpoints/{_TEST_ID}"
)
_TEST_CREDENTIALS = mock.Mock(spec=auth_credentials.AnonymousCredentials())
_TEST_EXPLANATION_METADATA = aiplatform.explain.ExplanationMetadata(
    inputs={
        "features": {
            "input_tensor_name": "dense_input",
            "encoding": "BAG_OF_FEATURES",
            "modality": "numeric",
            "index_feature_mapping": ["abc", "def", "ghj"],
        }
    },
    outputs={"medv": {"output_tensor_name": "dense_2"}},
)
_TEST_EXPLANATION_PARAMETERS = aiplatform.explain.ExplanationParameters(
    {"sampled_shapley_attribution": {"path_count": 10}}
)
_TEST_DEPLOYED_MODELS = [
    gca_endpoint.DeployedModel(id=_TEST_ID, display_name=_TEST_DISPLAY_NAME),
    gca_endpoint.DeployedModel(id=_TEST_ID_2, display_name=_TEST_DISPLAY_NAME_2),
    gca_endpoint.DeployedModel(id=_TEST_ID_3, display_name=_TEST_DISPLAY_NAME_3),
]
_TEST_DEPLOYED_MODELS_WITH_EXPLANATION = [
    gca_endpoint.DeployedModel(
        id=_TEST_ID,
        display_name=_TEST_DISPLAY_NAME,
        explanation_spec=gca_explanation.ExplanationSpec(
            metadata=_TEST_EXPLANATION_METADATA,
            parameters=_TEST_EXPLANATION_PARAMETERS,
        ),
    ),
    gca_endpoint.DeployedModel(
        id=_TEST_ID_2,
        display_name=_TEST_DISPLAY_NAME_2,
        explanation_spec=gca_explanation.ExplanationSpec(
            metadata=_TEST_EXPLANATION_METADATA,
            parameters=_TEST_EXPLANATION_PARAMETERS,
        ),
    ),
    gca_endpoint.DeployedModel(
        id=_TEST_ID_3,
        display_name=_TEST_DISPLAY_NAME_3,
        explanation_spec=gca_explanation.ExplanationSpec(
            metadata=_TEST_EXPLANATION_METADATA,
            parameters=_TEST_EXPLANATION_PARAMETERS,
        ),
    ),
]
_TEST_TRAFFIC_SPLIT = {_TEST_ID: 0, _TEST_ID_2: 100, _TEST_ID_3: 0}
_TEST_DICT_PREDICTION = [{"label": 1.0}]
_TEST_LIST_PREDICTION = [[1.0]]
_TEST_EXPLANATIONS = [gca_prediction_service.explanation.Explanation(attributions=[])]
_TEST_ATTRIBUTIONS = [
    gca_prediction_service.explanation.Attribution(
        baseline_output_value=1.0,
        instance_output_value=2.0,
        feature_attributions={"feature_1": 3.0, "feature_2": 2.0},
        output_index=[1, 2, 3],
        output_display_name="abc",
        approximation_error=6.0,
        output_name="xyz",
    )
]


@pytest.fixture()
def lit_widget_mock():
    widget_mock = mock.MagicMock(notebook.LitWidget)
    yield widget_mock


@pytest.fixture()
def init_lit_widget_mock(lit_widget_mock):
    with mock.patch.object(notebook, "LitWidget") as widget_init_mock:
        widget_init_mock.return_value = lit_widget_mock
        yield widget_init_mock


@pytest.fixture
def widget_render_mock(lit_widget_mock):
    with mock.patch.object(lit_widget_mock, "render") as render_mock:
        yield render_mock


@pytest.fixture
def sampled_shapley_explainer_mock():
    with mock.patch.object(
        explainable_ai_sdk, "SampledShapleyConfig", create=True
    ) as config_mock:
        yield config_mock


@pytest.fixture
def load_model_from_local_path_mock():
    with mock.patch.object(
        explainable_ai_sdk, "load_model_from_local_path", autospec=True
    ) as explainer_mock:
        model_mock = mock.Mock()
        explanation_mock = mock.Mock()
        explanation_mock.feature_importance.return_value = {
            "feature_1": 0.01,
            "feature_2": 0.1,
        }
        model_mock.explain.return_value = [explanation_mock]
        explainer_mock.return_value = model_mock
        yield explainer_mock


@pytest.fixture
def feature_types():
    yield collections.OrderedDict(
        [("feature_1", lit_types.Scalar()), ("feature_2", lit_types.Scalar())]
    )


@pytest.fixture
def label_types():
    yield collections.OrderedDict([("label", lit_types.RegressionScore())])


@pytest.fixture
def set_up_sequential(tmpdir, feature_types, label_types):
    # Set up a sequential model
    seq_model = tf.keras.models.Sequential()
    seq_model.add(tf.keras.layers.Dense(32, activation="relu", input_shape=(2,)))
    seq_model.add(tf.keras.layers.Dense(32, activation="relu"))
    seq_model.add(tf.keras.layers.Dense(1, activation="sigmoid"))
    saved_model_path = str(tmpdir.mkdir("tmp"))
    tf.saved_model.save(seq_model, saved_model_path)
    yield feature_types, label_types, saved_model_path


@pytest.fixture
def set_up_pandas_dataframe_and_columns():
    dataframe = pd.DataFrame.from_dict(
        {"feature_1": [1.0], "feature_2": [3.0], "label": [1.0]}
    )
    columns = collections.OrderedDict(
        [
            ("feature_1", lit_types.Scalar()),
            ("feature_2", lit_types.Scalar()),
            ("label", lit_types.RegressionScore()),
        ]
    )
    yield dataframe, columns


@pytest.fixture
def get_endpoint_with_models_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "get_endpoint"
    ) as get_endpoint_mock:
        get_endpoint_mock.return_value = gca_endpoint.Endpoint(
            display_name=_TEST_DISPLAY_NAME,
            name=_TEST_ENDPOINT_NAME,
            deployed_models=_TEST_DEPLOYED_MODELS,
            traffic_split=_TEST_TRAFFIC_SPLIT,
        )
        yield get_endpoint_mock


@pytest.fixture
def get_endpoint_with_models_with_explanation_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "get_endpoint"
    ) as get_endpoint_mock:
        get_endpoint_mock.return_value = gca_endpoint.Endpoint(
            display_name=_TEST_DISPLAY_NAME,
            name=_TEST_ENDPOINT_NAME,
            deployed_models=_TEST_DEPLOYED_MODELS_WITH_EXPLANATION,
            traffic_split=_TEST_TRAFFIC_SPLIT,
        )
        yield get_endpoint_mock


@pytest.fixture
def predict_client_predict_dict_mock():
    with mock.patch.object(
        prediction_service_client.PredictionServiceClient, "predict"
    ) as predict_mock:
        predict_mock.return_value = gca_prediction_service.PredictResponse(
            deployed_model_id=_TEST_ID
        )
        predict_mock.return_value.predictions.extend(_TEST_DICT_PREDICTION)
        yield predict_mock


@pytest.fixture
def predict_client_explain_dict_mock():
    with mock.patch.object(
        prediction_service_client.PredictionServiceClient, "explain"
    ) as predict_mock:
        predict_mock.return_value = gca_prediction_service.ExplainResponse(
            deployed_model_id=_TEST_ID,
        )
        predict_mock.return_value.predictions.extend(_TEST_DICT_PREDICTION)
        predict_mock.return_value.explanations.extend(_TEST_EXPLANATIONS)
        predict_mock.return_value.explanations[0].attributions.extend(
            _TEST_ATTRIBUTIONS
        )
        yield predict_mock


@pytest.fixture
def predict_client_predict_list_mock():
    with mock.patch.object(
        prediction_service_client.PredictionServiceClient, "predict"
    ) as predict_mock:
        predict_mock.return_value = gca_prediction_service.PredictResponse(
            deployed_model_id=_TEST_ID
        )
        predict_mock.return_value.predictions.extend(_TEST_LIST_PREDICTION)
        yield predict_mock


@pytest.fixture
def predict_client_explain_list_mock():
    with mock.patch.object(
        prediction_service_client.PredictionServiceClient, "explain"
    ) as predict_mock:
        predict_mock.return_value = gca_prediction_service.ExplainResponse(
            deployed_model_id=_TEST_ID,
        )
        predict_mock.return_value.predictions.extend(_TEST_LIST_PREDICTION)
        predict_mock.return_value.explanations.extend(_TEST_EXPLANATIONS)
        predict_mock.return_value.explanations[0].attributions.extend(
            _TEST_ATTRIBUTIONS
        )
        yield predict_mock


class TestExplainLit:

    def setup_method(self):
        reload(initializer)
        reload(aiplatform)
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_create_lit_dataset_from_pandas_returns_dataset(
        self,
        set_up_pandas_dataframe_and_columns,
    ):
        pd_dataset, lit_columns = set_up_pandas_dataframe_and_columns
        lit_dataset = create_lit_dataset(pd_dataset, lit_columns)
        expected_examples = [
            {"feature_1": 1.0, "feature_2": 3.0, "label": 1.0},
        ]

        assert lit_dataset.spec() == dict(lit_columns)
        assert expected_examples == lit_dataset._examples

    def test_create_lit_model_from_tensorflow_returns_model(self, set_up_sequential):
        feature_types, label_types, saved_model_path = set_up_sequential
        lit_model = create_lit_model(saved_model_path, feature_types, label_types)
        test_inputs = [
            {"feature_1": 1.0, "feature_2": 2.0},
        ]
        outputs = lit_model.predict_minibatch(test_inputs)

        assert lit_model.input_spec() == dict(feature_types)
        assert lit_model.output_spec() == dict(label_types)
        assert len(outputs) == 1
        for item in outputs:
            assert item.keys() == {"label"}
            assert len(item.values()) == 1

    @pytest.mark.skipif(
        sys.version_info < (3, 11),
        reason=("temporarily skipped due to failures in python 3.9 and 3.10"),
    )
    @mock.patch.dict(os.environ, {"LIT_PROXY_URL": "auto"})
    @pytest.mark.usefixtures(
        "sampled_shapley_explainer_mock", "load_model_from_local_path_mock"
    )
    def test_create_lit_model_from_tensorflow_with_xai_returns_model(
        self, set_up_sequential
    ):
        feature_types, label_types, saved_model_path = set_up_sequential
        lit_model = create_lit_model(saved_model_path, feature_types, label_types)
        test_inputs = [
            {"feature_1": 1.0, "feature_2": 2.0},
        ]
        outputs = lit_model.predict_minibatch(test_inputs)

        assert lit_model.input_spec() == dict(feature_types)
        assert lit_model.output_spec() == dict(
            {
                **label_types,
                "feature_attribution": lit_types.FeatureSalience(signed=True),
            }
        )
        assert len(outputs) == 1
        for item in outputs:
            assert item.keys() == {"label", "feature_attribution"}
            assert len(item.values()) == 2

    @pytest.mark.usefixtures(
        "predict_client_predict_dict_mock", "get_endpoint_with_models_mock"
    )
    @pytest.mark.parametrize("model_id", [None, _TEST_ID])
    def test_create_lit_model_from_dict_endpoint_returns_model(
        self, feature_types, label_types, model_id
    ):
        endpoint = aiplatform.Endpoint(_TEST_ENDPOINT_NAME)
        lit_model = create_lit_model_from_endpoint(
            endpoint, feature_types, label_types, model_id
        )
        test_inputs = [
            {"feature_1": 1.0, "feature_2": 2.0},
        ]
        outputs = lit_model.predict_minibatch(test_inputs)

        assert lit_model.input_spec() == dict(feature_types)
        assert lit_model.output_spec() == dict(label_types)
        assert len(outputs) == 1
        for item in outputs:
            assert item.keys() == {"label"}
            assert len(item.values()) == 1

    @pytest.mark.usefixtures(
        "predict_client_explain_dict_mock",
        "get_endpoint_with_models_with_explanation_mock",
    )
    @pytest.mark.parametrize("model_id", [None, _TEST_ID])
    def test_create_lit_model_from_dict_endpoint_with_xai_returns_model(
        self, feature_types, label_types, model_id
    ):
        endpoint = aiplatform.Endpoint(_TEST_ENDPOINT_NAME)
        lit_model = create_lit_model_from_endpoint(
            endpoint, feature_types, label_types, model_id
        )
        test_inputs = [
            {"feature_1": 1.0, "feature_2": 2.0},
        ]
        outputs = lit_model.predict_minibatch(test_inputs)

        assert lit_model.input_spec() == dict(feature_types)
        assert lit_model.output_spec() == dict(
            {
                **label_types,
                "feature_attribution": lit_types.FeatureSalience(signed=True),
            }
        )
        assert len(outputs) == 1
        for item in outputs:
            assert item.keys() == {"label", "feature_attribution"}
            assert len(item.values()) == 2

    @pytest.mark.usefixtures(
        "predict_client_predict_dict_mock", "get_endpoint_with_models_mock"
    )
    @pytest.mark.parametrize("model_id", [None, _TEST_ID])
    def test_create_lit_model_from_dict_endpoint_name_returns_model(
        self, feature_types, label_types, model_id
    ):
        lit_model = create_lit_model_from_endpoint(
            _TEST_ENDPOINT_NAME, feature_types, label_types, model_id
        )
        test_inputs = [
            {"feature_1": 1.0, "feature_2": 2.0},
        ]
        outputs = lit_model.predict_minibatch(test_inputs)

        assert lit_model.input_spec() == dict(feature_types)
        assert lit_model.output_spec() == dict(label_types)
        assert len(outputs) == 1
        for item in outputs:
            assert item.keys() == {"label"}
            assert len(item.values()) == 1

    @pytest.mark.usefixtures(
        "predict_client_explain_dict_mock",
        "get_endpoint_with_models_with_explanation_mock",
    )
    @pytest.mark.parametrize("model_id", [None, _TEST_ID])
    def test_create_lit_model_from_dict_endpoint_name_with_xai_returns_model(
        self, feature_types, label_types, model_id
    ):
        lit_model = create_lit_model_from_endpoint(
            _TEST_ENDPOINT_NAME, feature_types, label_types, model_id
        )
        test_inputs = [
            {"feature_1": 1.0, "feature_2": 2.0},
        ]
        outputs = lit_model.predict_minibatch(test_inputs)

        assert lit_model.input_spec() == dict(feature_types)
        assert lit_model.output_spec() == dict(
            {
                **label_types,
                "feature_attribution": lit_types.FeatureSalience(signed=True),
            }
        )
        assert len(outputs) == 1
        for item in outputs:
            assert item.keys() == {"label", "feature_attribution"}
            assert len(item.values()) == 2

    @pytest.mark.usefixtures(
        "predict_client_predict_list_mock", "get_endpoint_with_models_mock"
    )
    @pytest.mark.parametrize("model_id", [None, _TEST_ID])
    def test_create_lit_model_from_list_endpoint_returns_model(
        self, feature_types, label_types, model_id
    ):
        endpoint = aiplatform.Endpoint(_TEST_ENDPOINT_NAME)
        lit_model = create_lit_model_from_endpoint(
            endpoint, feature_types, label_types, model_id
        )
        test_inputs = [
            {"feature_1": 1.0, "feature_2": 2.0},
        ]
        outputs = lit_model.predict_minibatch(test_inputs)

        assert lit_model.input_spec() == dict(feature_types)
        assert lit_model.output_spec() == dict(label_types)
        assert len(outputs) == 1
        for item in outputs:
            assert item.keys() == {"label"}
            assert len(item.values()) == 1

    @pytest.mark.usefixtures(
        "predict_client_explain_list_mock",
        "get_endpoint_with_models_with_explanation_mock",
    )
    @pytest.mark.parametrize("model_id", [None, _TEST_ID])
    def test_create_lit_model_from_list_endpoint_with_xai_returns_model(
        self, feature_types, label_types, model_id
    ):
        endpoint = aiplatform.Endpoint(_TEST_ENDPOINT_NAME)
        lit_model = create_lit_model_from_endpoint(
            endpoint, feature_types, label_types, model_id
        )
        test_inputs = [
            {"feature_1": 1.0, "feature_2": 2.0},
        ]
        outputs = lit_model.predict_minibatch(test_inputs)

        assert lit_model.input_spec() == dict(feature_types)
        assert lit_model.output_spec() == dict(
            {
                **label_types,
                "feature_attribution": lit_types.FeatureSalience(signed=True),
            }
        )
        assert len(outputs) == 1
        for item in outputs:
            assert item.keys() == {"label", "feature_attribution"}
            assert len(item.values()) == 2

    @pytest.mark.usefixtures(
        "predict_client_predict_list_mock", "get_endpoint_with_models_mock"
    )
    @pytest.mark.parametrize("model_id", [None, _TEST_ID])
    def test_create_lit_model_from_list_endpoint_name_returns_model(
        self, feature_types, label_types, model_id
    ):
        lit_model = create_lit_model_from_endpoint(
            _TEST_ENDPOINT_NAME, feature_types, label_types, model_id
        )
        test_inputs = [
            {"feature_1": 1.0, "feature_2": 2.0},
        ]
        outputs = lit_model.predict_minibatch(test_inputs)

        assert lit_model.input_spec() == dict(feature_types)
        assert lit_model.output_spec() == dict(label_types)
        assert len(outputs) == 1
        for item in outputs:
            assert item.keys() == {"label"}
            assert len(item.values()) == 1

    @pytest.mark.usefixtures(
        "predict_client_explain_list_mock",
        "get_endpoint_with_models_with_explanation_mock",
    )
    @pytest.mark.parametrize("model_id", [None, _TEST_ID])
    def test_create_lit_model_from_list_endpoint_name_with_xai_returns_model(
        self, feature_types, label_types, model_id
    ):
        lit_model = create_lit_model_from_endpoint(
            _TEST_ENDPOINT_NAME, feature_types, label_types, model_id
        )
        test_inputs = [
            {"feature_1": 1.0, "feature_2": 2.0},
        ]
        outputs = lit_model.predict_minibatch(test_inputs)

        assert lit_model.input_spec() == dict(feature_types)
        assert lit_model.output_spec() == dict(
            {
                **label_types,
                "feature_attribution": lit_types.FeatureSalience(signed=True),
            }
        )
        assert len(outputs) == 1
        for item in outputs:
            assert item.keys() == {"label", "feature_attribution"}
            assert len(item.values()) == 2

    @pytest.mark.usefixtures("init_lit_widget_mock")
    def test_open_lit(
        self,
        set_up_sequential,
        set_up_pandas_dataframe_and_columns,
        widget_render_mock,
    ):
        pd_dataset, lit_columns = set_up_pandas_dataframe_and_columns
        lit_dataset = create_lit_dataset(pd_dataset, lit_columns)
        feature_types, label_types, saved_model_path = set_up_sequential
        lit_model = create_lit_model(saved_model_path, feature_types, label_types)

        open_lit({"model": lit_model}, {"dataset": lit_dataset})
        widget_render_mock.assert_called_once()

    @pytest.mark.usefixtures("init_lit_widget_mock")
    def test_set_up_and_open_lit(
        self,
        set_up_sequential,
        set_up_pandas_dataframe_and_columns,
        widget_render_mock,
    ):
        pd_dataset, lit_columns = set_up_pandas_dataframe_and_columns
        feature_types, label_types, saved_model_path = set_up_sequential
        lit_dataset, lit_model = set_up_and_open_lit(
            pd_dataset, lit_columns, saved_model_path, feature_types, label_types
        )

        expected_examples = [
            {"feature_1": 1.0, "feature_2": 3.0, "label": 1.0},
        ]
        test_inputs = [
            {"feature_1": 1.0, "feature_2": 2.0},
        ]
        outputs = lit_model.predict_minibatch(test_inputs)

        assert lit_dataset.spec() == dict(lit_columns)
        assert expected_examples == lit_dataset._examples

        assert lit_model.input_spec() == dict(feature_types)
        assert lit_model.output_spec() == dict(label_types)
        assert len(outputs) == 1
        for item in outputs:
            assert item.keys() == {"label"}
            assert len(item.values()) == 1

        widget_render_mock.assert_called_once()

    @pytest.mark.skipif(
        sys.version_info < (3, 11),
        reason=("temporarily skipped due to failures in python 3.9 and 3.10"),
    )
    @pytest.mark.usefixtures("init_lit_widget_mock")
    @mock.patch.dict(os.environ, {"LIT_PROXY_URL": "auto"})
    @pytest.mark.usefixtures(
        "sampled_shapley_explainer_mock", "load_model_from_local_path_mock"
    )
    def test_set_up_and_open_lit_with_xai(
        self,
        set_up_sequential,
        set_up_pandas_dataframe_and_columns,
        widget_render_mock,
    ):
        pd_dataset, lit_columns = set_up_pandas_dataframe_and_columns
        feature_types, label_types, saved_model_path = set_up_sequential
        lit_dataset, lit_model = set_up_and_open_lit(
            pd_dataset, lit_columns, saved_model_path, feature_types, label_types
        )

        expected_examples = [
            {"feature_1": 1.0, "feature_2": 3.0, "label": 1.0},
        ]
        test_inputs = [
            {"feature_1": 1.0, "feature_2": 2.0},
        ]
        outputs = lit_model.predict_minibatch(test_inputs)

        assert lit_dataset.spec() == dict(lit_columns)
        assert expected_examples == lit_dataset._examples

        assert lit_model.input_spec() == dict(feature_types)
        assert lit_model.output_spec() == dict(
            {
                **label_types,
                "feature_attribution": lit_types.FeatureSalience(signed=True),
            }
        )
        assert len(outputs) == 1
        for item in outputs:
            assert item.keys() == {"label", "feature_attribution"}
            assert len(item.values()) == 2

        widget_render_mock.assert_called_once()
