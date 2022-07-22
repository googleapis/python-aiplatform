import pytest

from google.api_core import exceptions
from google.cloud import aiplatform
from google.cloud.aiplatform.vizier import Study
from google.cloud.aiplatform.vizier import Trial
from tests.system.aiplatform import e2e_base
from google.cloud.aiplatform.vizier import pyvizier

_TEST_STUDY_ID = 123


@pytest.mark.usefixtures("tear_down_resources")
class TestVizier(e2e_base.TestEndToEnd):
    _temp_prefix = "temp_vertex_sdk_e2e_vizier_test"

    def test_vizier_lifecycle(self, shared_state):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )
        sc = pyvizier.StudyConfig()
        sc.algorithm = pyvizier.Algorithm.RANDOM_SEARCH
        sc.metric_information.append(
            pyvizier.MetricInformation(
                name="pr-auc", goal=pyvizier.ObjectiveMetricGoal.MAXIMIZE
            )
        )
        root = sc.search_space.select_root()
        root.add_float_param(
            "learning_rate", 0.00001, 1.0, scale_type=pyvizier.ScaleType.LINEAR
        )
        root.add_categorical_param("optimizer", ["adagrad", "adam", "experimental"])
        sc.automated_stopping_config = (
            pyvizier.AutomatedStoppingConfig.decay_curve_stopping_config(use_steps=True)
        )

        study = Study.create_or_load(display_name=self._temp_prefix, problem=sc)
        shared_state["resources"] = [study]
        trials = study.suggest(count=3, worker="halio_test_worker")
        for trial in trials:
            if not trial.should_stop():
                measurement = pyvizier.Measurement()
                measurement.metrics["pr-auc"] = 0.4
                trial.add_measurement(measurement=measurement)
                trial.complete(measurement=measurement)
        optimal_trials = study.optimal_trials()

        for trial in study.trials():
            assert trial.status == pyvizier.TrialStatus.COMPLETED
        assert optimal_trials[0].status == pyvizier.TrialStatus.COMPLETED

    def test_vizier_study_deletion(self, shared_state):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )
        sc = pyvizier.StudyConfig()
        sc.algorithm = pyvizier.Algorithm.RANDOM_SEARCH
        sc.metric_information.append(
            pyvizier.MetricInformation(
                name="pr-auc", goal=pyvizier.ObjectiveMetricGoal.MAXIMIZE
            )
        )
        root = sc.search_space.select_root()
        root.add_float_param(
            "learning_rate", 0.00001, 1.0, scale_type=pyvizier.ScaleType.LINEAR
        )
        root.add_categorical_param("optimizer", ["adagrad", "adam", "experimental"])
        sc.automated_stopping_config = (
            pyvizier.AutomatedStoppingConfig.decay_curve_stopping_config(use_steps=True)
        )

        study = Study.create_or_load(display_name=self._temp_prefix, problem=sc)
        study.delete()

        with pytest.raises(exceptions.NotFound):
            study = Study(study_id=study.name)

    def test_vizier_trial_deletion(self, shared_state):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )
        sc = pyvizier.StudyConfig()
        sc.algorithm = pyvizier.Algorithm.RANDOM_SEARCH
        sc.metric_information.append(
            pyvizier.MetricInformation(
                name="pr-auc", goal=pyvizier.ObjectiveMetricGoal.MAXIMIZE
            )
        )
        root = sc.search_space.select_root()
        root.add_float_param(
            "learning_rate", 0.00001, 1.0, scale_type=pyvizier.ScaleType.LINEAR
        )
        root.add_categorical_param("optimizer", ["adagrad", "adam", "experimental"])
        sc.automated_stopping_config = (
            pyvizier.AutomatedStoppingConfig.decay_curve_stopping_config(use_steps=True)
        )

        study = Study.create_or_load(display_name=self._temp_prefix, problem=sc)
        trials = study.suggest(count=1, worker="halio_test_worker")
        trials[0].delete()

        with pytest.raises(exceptions.NotFound):
            study = Trial(study_id=study.name, trial_name=trials[0].name)
