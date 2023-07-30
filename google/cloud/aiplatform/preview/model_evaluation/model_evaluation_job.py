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

from typing import Optional, List, Union

from google.protobuf import json_format
from google.auth import credentials as auth_credentials

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform._pipeline_based_service import (
    pipeline_based_service,
)
from google.cloud.aiplatform.preview import model_evaluation
from google.cloud.aiplatform import pipeline_jobs

from google.cloud.aiplatform.compat.types import (
    pipeline_state_v1 as gca_pipeline_state_v1,
    pipeline_job_v1 as gca_pipeline_job_v1,
    execution_v1 as gca_execution_v1,
    model_evaluation_slice as gca_model_evaluation_slice_compat,
)

import json

_LOGGER = base.Logger(__name__)

# First 2 are for automl tabular models, the next 2 are for automl vision models
# and the others are for everything else
_MODEL_EVAL_PIPELINE_TEMPLATES = {
    "automl_tabular_without_feature_attribution": "gs://vertex-evaluation-templates/20230315_1700/evaluation_automl_tabular_pipeline.json",
    "automl_tabular_with_feature_attribution": "gs://vertex-evaluation-templates/20230315_1700/evaluation_automl_tabular_feature_attribution_pipeline.json",
    "automl_vision_with_error_analysis": "gs://vertex-evaluation-pipeline-templates/20230523_1711/vision_error_analysis_pipeline.json",
    "automl_vision_with_evaluated_annotations": "gs://vertex-evaluation-pipeline-templates/20230523_1711/evaluated_annotation_pipeline.json",
    "other_without_feature_attribution": "gs://vertex-evaluation-templates/20230315_1700/evaluation_pipeline.json",
    "other_with_feature_attribution": "gs://vertex-evaluation-templates/20230315_1700/evaluation_feature_attribution_pipeline.json",
}


class _ModelEvaluationJob(pipeline_based_service._VertexAiPipelineBasedService):
    """Creates a Model Evaluation PipelineJob using _VertexAiPipelineBasedService."""

    _template_ref = _MODEL_EVAL_PIPELINE_TEMPLATES

    _creation_log_message = "Created PipelineJob for your Model Evaluation."

    _component_identifier = "fpc-model-evaluation"

    _template_name_identifier = None

    @property
    def _metadata_output_artifact(self) -> Optional[str]:
        """The resource uri for the ML Metadata output artifact from the evaluation component of the Model Evaluation pipeline."""
        if self.state == gca_pipeline_state_v1.PipelineState.PIPELINE_STATE_SUCCEEDED:
            for task in self.backing_pipeline_job._gca_resource.job_detail.task_details:
                if (
                    task.task_name.startswith("model-evaluation")
                    and "evaluation_metrics" in task.outputs
                ):
                    return task.outputs["evaluation_metrics"].artifacts[0].name

    def __init__(
        self,
        evaluation_pipeline_run_name: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves a ModelEvaluationJob and instantiates its representation.

        Example Usage:
            my_evaluation = aiplatform.ModelEvaluationJob(
                pipeline_job_name =
                "projects/123/locations/us-central1/pipelineJobs/456"
            )
            my_evaluation = aiplatform.ModelEvaluationJob(
                pipeline_job_name = "456"
            )
        Args:
            evaluation_pipeline_run_name (str): Required. A fully-qualified pipeline
              job run ID.
                Example: "projects/123/locations/us-central1/pipelineJobs/456" or
                  "456" when project and location are initialized or passed.
            project (str): Optional. Project to retrieve pipeline job from. If not
              set, project set in aiplatform.init will be used.
            location (str): Optional. Location to retrieve pipeline job from. If not
              set, location set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials): Optional. Custom credentials
              to use to retrieve this pipeline job. Overrides credentials set in
              aiplatform.init.
        """
        super().__init__(
            pipeline_job_name=evaluation_pipeline_run_name,
            project=project,
            location=location,
            credentials=credentials,
        )

    @staticmethod
    def _get_template_url(
        model_type: str,
        feature_attributions: bool,
        error_analysis: bool,
    ) -> str:
        """Gets the pipeline template URL for this model evaluation job given the type of data used to train the model and whether feature attributions should be generated.

        Args:
            data_type (str): Required. The type of data used to train the model.
            feature_attributions (bool): Required. Whether this evaluation job
              should generate feature attributions.
            error_analysis (bool): Required. Whether this evaluation job should
              generate error analysis or evaluated annotations.

        Returns:
            (str): The pipeline template URL to use for this model evaluation job.
        """
        if model_type == "automl_vision" and feature_attributions:
            model_type = "other"

        template_type = model_type

        if model_type == "automl_vision":
            if error_analysis:
                template_type += "_with_error_analysis"
            else:
                template_type += "_with_evaluated_annotations"
        else:
            if feature_attributions:
                template_type += "_with_feature_attribution"
            else:
                template_type += "_without_feature_attribution"
        print(f"Triggered {template_type} Pipeline.")
        return _ModelEvaluationJob._template_ref[template_type]

    @staticmethod
    def _slice_proto_to_json_str(
        slice_spec_proto: List[
            gca_model_evaluation_slice_compat.ModelEvaluationSlice.Slice.SliceSpec
        ],
    ) -> List[str]:
        """Converts the Model Evaluation SliceSpec protos into a list of JSON strings.

        KFP pipeline components can't take a proto as input so we need to convert
        it.
        """
        slicing_spec_list = []
        for single_slice_spec in slice_spec_proto:
            slicing_spec_json = json_format.MessageToJson(single_slice_spec._pb)
            slicing_spec_list.append(slicing_spec_json)
        return slicing_spec_list

    @classmethod
    def submit(
        cls,
        model_name: Union[str, "aiplatform.Model"],
        prediction_type: str,
        target_field_name: str,
        pipeline_root: str,
        model_type: str,
        gcs_source_uris: Optional[List[str]] = None,
        bigquery_source_uri: Optional[str] = None,
        batch_predict_bigquery_destination_output_uri: Optional[str] = None,
        class_labels: Optional[List[str]] = None,
        prediction_label_column: Optional[str] = None,
        prediction_score_column: Optional[str] = None,
        sliced_metrics_config: Optional[
            gca_model_evaluation_slice_compat.ModelEvaluationSlice.Slice.SliceSpec
        ] = None,
        generate_feature_attributions: Optional[bool] = False,
        instances_format: Optional[str] = "jsonl",
        evaluation_pipeline_display_name: Optional[str] = None,
        evaluation_metrics_display_name: Optional[str] = None,
        job_id: Optional[str] = None,
        service_account: Optional[str] = None,
        network: Optional[str] = None,
        encryption_spec_key_name: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        experiment: Optional[Union[str, "aiplatform.Experiment"]] = None,
        enable_error_analysis: Optional[bool] = False,
        test_dataset_resource_name: Optional[str] = None,
        test_dataset_annotation_set_name: Optional[str] = None,
        training_dataset_resource_name: Optional[str] = None,
        training_dataset_annotation_set_name: Optional[str] = None,
        test_dataset_storage_source_uris: Optional[str] = None,
        training_dataset_storage_source_uris: Optional[str] = None,
        batch_predict_predictions_format: str = "jsonl",
        batch_predict_machine_type: str = "n1-standard-32",
        batch_predict_starting_replica_count: int = 5,
        batch_predict_max_replica_count: int = 10,
        batch_predict_accelerator_type: str = "",
        batch_predict_accelerator_count: int = 0,
        dataflow_machine_type: str = "n1-standard-8",
        dataflow_max_num_workers: int = 5,
        dataflow_disk_size_gb: int = 50,
        dataflow_service_account: str = "",
        dataflow_subnetwork: str = "",
        dataflow_use_public_ips: bool = True,
    ) -> "_ModelEvaluationJob":
        """Submits a Model Evaluation Job using aiplatform.PipelineJob and returns the ModelEvaluationJob resource.

        Example usage:
        my_evaluation = _ModelEvaluationJob.submit(
            model="projects/123/locations/us-central1/models/456",
            prediction_type="classification",
            pipeline_root="gs://my-pipeline-bucket/runpath",
            gcs_source_uris=["gs://test-prediction-data"],
            target_field_name=["prediction_class"],
            instances_format="jsonl",
        )

        my_evaluation = _ModelEvaluationJob.submit(
            model="projects/123/locations/us-central1/models/456",
            prediction_type="regression",
            pipeline_root="gs://my-pipeline-bucket/runpath",
            gcs_source_uris=["gs://test-prediction-data"],
            target_field_name=["price"],
            instances_format="jsonl",
        )
        Args:
            model_name (Union[str, "aiplatform.Model"]): Required. An instance of
              aiplatform.Model or a fully-qualified model resource name or model ID
              to run the evaluation job on. Example:
              "projects/123/locations/us-central1/models/456" or "456" when project
              and location are initialized or passed.
            prediction_type (str): Required. The type of prediction performed by the
              Model. One of "classification" or "regression".
            target_field_name (str): Required. The name of your prediction column.
            pipeline_root (str): Required. The GCS directory to store output from
              the model evaluation PipelineJob.
            gcs_source_uris (List[str]): Optional. A list of Cloud Storage data
              files containing the ground truth data to use for this evaluation job.
              These files should contain your model's prediction column. Currently
              only Google Cloud Storage urls are supported, for example:
              "gs://path/to/your/data.csv". The provided data files must be either
              CSV or JSONL. One of `gcs_source_uris` or `bigquery_source_uri` is
              required.
            model_type (str): Required. One of "automl_tabular", "automl_vision" or
              "other". This determines the Model Evaluation template used by this
              PipelineJob.
            gcs_source_uris (List[str]): Optional. A list of Cloud Storage data
              files containing the ground truth data to use for this evaluation job.
              These files should contain your model's prediction column. Currently
              only Google Cloud Storage urls are supported, for example:
              "gs://path/to/your/data.csv". The provided data files must be either
              CSV or JSONL. One of `gcs_source_uris` or `bigquery_source_uri` is
              required.
            bigquery_source_uri (str): Optional. A bigquery table URI containing the
              ground truth data to use for this evaluation job. This uri should be
              in the format 'bq://my-project-id.dataset.table'. One of
              `gcs_source_uris` or `bigquery_source_uri` is required.
            bigquery_destination_output_uri (str): Optional. A bigquery table URI
              where the Batch Prediction job associated with your Model Evaluation
              will write prediction output. This can be a BigQuery URI to a project
              ('bq://my-project'), a dataset ('bq://my-project.my-dataset'), or a
              table ('bq://my-project.my-dataset.my-table'). Required if
              `bigquery_source_uri` is provided.
            class_labels (List[str]): Optional. For custom (non-AutoML)
              classification models, a list of possible class names, in the same
              order that predictions are generated. This argument is required when
              prediction_type is 'classification'. For example, in a classification
              model with 3 possible classes that are outputted in the format: [0.97,
              0.02, 0.01] with the class names "cat", "dog", and "fish", the value
              of `class_labels` should be `["cat", "dog", "fish"]` where the class
              "cat" corresponds with 0.97 in the example above.
            prediction_label_column (str): Optional. The column name of the field
              containing classes the model is scoring. Formatted to be able to find
              nested columns, delimeted by `.`. If not set, defaulted to
              `prediction.classes` for classification.
            prediction_score_column (str): Optional. The column name of the field
              containing batch prediction scores. Formatted to be able to find
              nested columns, delimeted by `.`. If not set, defaulted to
              `prediction.scores` for a `classification` problem_type,
              `prediction.value` for a `regression` problem_type.
            generate_feature_attributions (boolean): Optional. Whether the model
              evaluation job should generate feature attributions. Defaults to False
              if not specified.
            instances_format (str): The format in which instances are given, must be
              one of the Model's supportedInputStorageFormats. If not set, defaults
              to "jsonl".
            evaluation_pipeline_display_name (str) Optional. The
              user-defined name of the PipelineJob created by this Pipeline Based
              Service. evaluation_metrics_display_name (str) Optional. The
              user-defined name of the evaluation metrics resource uploaded to
              Vertex in the evaluation pipeline job.
            job_id (str): Optional. The unique ID of the job run. If not specified,
              pipeline name + timestamp will be used.
            service_account (str): Specifies the service account for workload run-as
              account for this Model Evaluation PipelineJob. Users submitting jobs
              must have act-as permission on this run-as account. The service
              account running this Model Evaluation job needs the following
              permissions: Dataflow Worker, Storage Admin, Vertex AI User.
            network (str): The full name of the Compute Engine network to which the
              job should be peered. For example,
              projects/12345/global/networks/myVPC. Private services access must
              already be configured for the network. If left unspecified, the job is
              not peered with any network.
            encryption_spec_key_name (str): Optional. The Cloud KMS resource
              identifier of the customer managed encryption key used to protect the
              job. Has the form:
              ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``
              The key needs to be in the same region as where the compute resource
              is created. If this is set, then allresources created by the
              PipelineJob for this Model Evaluation will be encrypted with the
              provided encryption key. If not specified, encryption_spec of original
              PipelineJob will be used.
            project (str): Optional. The project to run this PipelineJob in. If not
              set, the project set in aiplatform.init will be used.
            location (str): Optional. Location to create PipelineJob. If not set,
              location set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials): Optional. Custom credentials
              to use to create the PipelineJob. Overrides credentials set in
              aiplatform.init.
            experiment (Union[str, experiments_resource.Experiment]): Optional. The
              Vertex AI experiment name or instance to associate to the PipelineJob
              executingthis model evaluation job.
            enable_error_analysis (boolean): Optional. Whether the model evaluation
              job should generate error analysis. Defaults to False if not
              specified.
            test_dataset_resource_name (str): Optional.  A google.VertexDataset
              artifact of the test dataset. If `test_dataset_storage_source_uris` is
              also provided, this Vertex Dataset argument will override the GCS
              source.
            test_dataset_annotation_set_name (str): Optional. A string of the
              annotation_set resource name containing the ground truth of the test
              dataset used for evaluation.
            training_dataset_resource_name (str): Optional. A google.VertexDataset
              artifact of the training dataset. If
              `training_dataset_storage_source_uris` is also provided, this Vertex
              Dataset argument will override the GCS source.
            training_dataset_annotation_set_name (str): Optional. A string of the
              annotation_set resource name containing the ground truth of the test
              dataset used for evaluation.
            test_dataset_storage_source_uris (str): Optional. Google Cloud Storage
              URI(-s) to unmanaged test datasets. `jsonl` is currently the only
              allowed format. If `test_dataset` is also provided, this field will be
              overriden by the provided Vertex Dataset.
              training_dataset_storage_source_uris(str): Optional. Google Cloud
              Storage URI(-s) to unmanaged test datasets. `jsonl` is currently the
              only allowed format. If `training_dataset` is also provided, this
              field will be overriden by the provided Vertex Dataset.
            batch_predict_predictions_format(str): Optional. The format in
                which Vertex AI gives the predictions. Must be one of the Model's
                supportedOutputStorageFormats. Ifnot set, default to "jsonl". If
                not set, default to "jsonl". For more details about this output
                config, see
                https://cloud.google.com/vertex-ai/docs/reference/rest/v1/projects.locations.batchPredictionJobs#OutputConfig.
            batch_predict_machine_type(str): Optional. The type of machine for
                running batch prediction on dedicated resources. If the Model
                supports DEDICATED_RESOURCES this config may be provided (and the
                job will use these resources). If the Model doesn't support
                AUTOMATIC_RESOURCES, this config must be provided. If not set,
                defaulted to `n1-standard-32`. For more details about the
                BatchDedicatedResources, see
                    https://cloud.google.com/vertex-ai/docs/reference/rest/v1/projects.locations.batchPredictionJobs#BatchDedicatedResources.
                For more details about the machine spec, see
                https://cloud.google.com/vertex-ai/docs/reference/rest/v1/MachineSpec
            batch_predict_starting_replica_count(int): Optional. The number of
                machine replicas used at the start of the batch operation. If not
                set, Vertex AI decides starting number, not greater than
                `max_replica_count`. Only used if `machine_type` is set.
            batch_predict_max_replica_count(int): Optional. The maximum number
                of machine replicas the batch operation may be scaled to. Only
                used if `machine_type` is set. Default is 10.
            batch_predict_accelerator_type(str): Optional. The type of
                accelerator(s) that may be attached to the machine as per
                `batch_predict_accelerator_count`. Only used if
                `batch_predict_machine_type` is set. For more details about the
                machine spec, see
                https://cloud.google.com/vertex-ai/docs/reference/rest/v1/MachineSpec
            batch_predict_accelerator_count: The number of accelerators to
                attach to the `batch_predict_machine_type`. Only used if
                `batch_predict_machine_type` is set.
            dataflow_machine_type(str):
                Optional. The dataflow machine type for evaluation components.
            dataflow_max_num_workers(int): Optional. The max number of
                Dataflow workers for evaluation components.
            dataflow_disk_size_gb(int): Optional. Dataflow worker's disk size
                in GB for evaluation components.
            dataflow_service_account(str):
                Optional. Custom service account to run dataflow jobs.
            dataflow_subnetwork(str): Optional. Dataflow's fully qualified
                subnetwork name, when empty the default subnetwork will be used.
                Example:
                https://cloud.google.com/dataflow/docs/guides/specifying-networks#example_network_and_subnetwork_specifications
            dataflow_use_public_ips(bool): Optional. Specifies whether
                Dataflow workers use public IPaddresses.

        Returns:
            (ModelEvaluationJob): Instantiated represnetation of the model
            evaluation job.
        """

        if isinstance(model_name, aiplatform.Model):
            model_resource_name = model_name.versioned_resource_name
        else:
            model_resource_name = aiplatform.Model(
                model_name=model_name
            ).versioned_resource_name

        if not evaluation_pipeline_display_name:
            evaluation_pipeline_display_name = cls._generate_display_name()

        if model_type == "automl_vision" and enable_error_analysis is True:
            template_params = {
                "project": project or initializer.global_config.project,
                "location": location or initializer.global_config.location,
                "batch_predict_gcs_destination_output_uri": pipeline_root,
                "model_name": model_resource_name,
                "test_dataset_resource_name": test_dataset_resource_name,
                "test_dataset_annotation_set_name": test_dataset_annotation_set_name,
                "training_dataset_resource_name": training_dataset_resource_name,
                "training_dataset_annotation_set_name": training_dataset_annotation_set_name,
                "test_dataset_storage_source_uris": test_dataset_storage_source_uris,
                "training_dataset_storage_source_uris": training_dataset_storage_source_uris,
                "batch_predict_instances_format": instances_format,
                "batch_predict_predictions_format": batch_predict_predictions_format,
                "batch_predict_machine_type": batch_predict_machine_type,
                "batch_predict_starting_replica_count": batch_predict_starting_replica_count,
                "batch_predict_max_replica_count": batch_predict_max_replica_count,
                "batch_predict_accelerator_type": batch_predict_accelerator_type,
                "batch_predict_accelerator_count": batch_predict_accelerator_count,
                "evaluation_display_name": evaluation_metrics_display_name,
                "dataflow_machine_type": dataflow_machine_type,
                "dataflow_max_num_workers": dataflow_max_num_workers,
                "dataflow_disk_size_gb": dataflow_disk_size_gb,
                "dataflow_service_account": dataflow_service_account,
                "dataflow_subnetwork": dataflow_subnetwork,
                "dataflow_use_public_ips": dataflow_use_public_ips,
                "encryption_spec_key_name": encryption_spec_key_name,
            }
        elif (
            model_type == "automl_vision"
            and enable_error_analysis is False
            and generate_feature_attributions is False
        ):
            template_params = {
                "project": project or initializer.global_config.project,
                "location": location or initializer.global_config.location,
                "batch_predict_gcs_destination_output_uri": pipeline_root,
                "model_name": model_resource_name,
                "test_dataset_resource_name": test_dataset_resource_name,
                "test_dataset_annotation_set_name": test_dataset_annotation_set_name,
                "test_dataset_storage_source_uris": test_dataset_storage_source_uris,
                "batch_predict_instances_format": instances_format,
                "batch_predict_predictions_format": batch_predict_predictions_format,
                "batch_predict_machine_type": batch_predict_machine_type,
                "batch_predict_starting_replica_count": batch_predict_starting_replica_count,
                "batch_predict_max_replica_count": batch_predict_max_replica_count,
                "batch_predict_accelerator_type": batch_predict_accelerator_type,
                "batch_predict_accelerator_count": batch_predict_accelerator_count,
                "evaluation_display_name": evaluation_metrics_display_name,
                "dataflow_machine_type": dataflow_machine_type,
                "dataflow_max_num_workers": dataflow_max_num_workers,
                "dataflow_disk_size_gb": dataflow_disk_size_gb,
                "dataflow_service_account": dataflow_service_account,
                "dataflow_subnetwork": dataflow_subnetwork,
                "dataflow_use_public_ips": dataflow_use_public_ips,
                "encryption_spec_key_name": encryption_spec_key_name,
            }
        else:
            template_params = {
                "batch_predict_instances_format": instances_format,
                "model_name": model_resource_name,
                "prediction_type": prediction_type,
                "evaluation_display_name": evaluation_metrics_display_name,
                "project": project or initializer.global_config.project,
                "location": location or initializer.global_config.location,
                "root_dir": pipeline_root,
                "target_field_name": target_field_name,
            }

        if bigquery_source_uri:
            template_params["batch_predict_predictions_format"] = "bigquery"
            template_params["batch_predict_bigquery_source_uri"] = bigquery_source_uri
            template_params[
                "batch_predict_bigquery_destination_output_uri"
            ] = batch_predict_bigquery_destination_output_uri
        elif gcs_source_uris:
            template_params["batch_predict_gcs_source_uris"] = gcs_source_uris

        if (
            prediction_type == "classification"
            and model_type == "other"
            and class_labels is not None
        ):
            template_params["evaluation_class_labels"] = class_labels

        if prediction_label_column:
            template_params[
                "evaluation_prediction_label_column"
            ] = prediction_label_column

        if prediction_score_column:
            template_params[
                "evaluation_prediction_score_column"
            ] = prediction_score_column

        # If the user provides a SA, use it for the Dataflow job as well
        if service_account is not None:
            template_params["dataflow_service_account"] = service_account

        if sliced_metrics_config:
            sliced_metrics_protos_to_str = cls._slice_proto_to_json_str(
                sliced_metrics_config
            )
            template_params["slicing_specs"] = sliced_metrics_protos_to_str

        template_url = cls._get_template_url(
            model_type,
            generate_feature_attributions,
            enable_error_analysis,
        )

        eval_pipeline_run = cls._create_and_submit_pipeline_job(
            template_params=template_params,
            template_path=template_url,
            pipeline_root=pipeline_root,
            display_name=evaluation_pipeline_display_name,
            job_id=job_id,
            service_account=service_account,
            network=network,
            encryption_spec_key_name=encryption_spec_key_name,
            project=project,
            location=location,
            credentials=credentials,
            experiment=experiment,
        )

        _LOGGER.info(
            f"{_ModelEvaluationJob._creation_log_message} View it in the console:"
            f" {eval_pipeline_run.pipeline_console_uri}"
        )

        return eval_pipeline_run

    def get_model_evaluation(
        self,
    ) -> Optional["model_evaluation.ModelEvaluation"]:
        """Gets the ModelEvaluation created by this ModelEvlauationJob.

        Returns:
            aiplatform.ModelEvaluation: Instantiated representation of the
            ModelEvaluation resource.
        Raises:
            RuntimeError: If the ModelEvaluationJob pipeline failed.
        """
        eval_job_state = self.backing_pipeline_job.state

        if eval_job_state in pipeline_jobs._PIPELINE_ERROR_STATES:
            raise RuntimeError(
                "Evaluation job failed. For more details see the logs:"
                f" {self.pipeline_console_uri}"
            )
        elif eval_job_state not in pipeline_jobs._PIPELINE_COMPLETE_STATES:
            _LOGGER.info(
                "Your evaluation job is still in progress. For more details see the"
                f" logs {self.pipeline_console_uri}"
            )
        else:
            for component in self.backing_pipeline_job.task_details:
                if (
                    component.task_name.startswith("model-evaluation-import")
                    and "output:gcp_resources" in component.execution.metadata
                ):
                    for metadata_key in component.execution.metadata:
                        if metadata_key == "output:gcp_resources" and (
                            component.state
                            == gca_pipeline_job_v1.PipelineTaskDetail.State.SUCCEEDED
                            or (
                                component.state
                                == gca_pipeline_job_v1.PipelineTaskDetail.State.SKIPPED
                                and component.execution.state
                                == gca_execution_v1.Execution.State.CACHED
                            )
                        ):
                            resource_metadata = json.loads(
                                (component.execution.metadata[metadata_key])
                            )["resources"]
                            for entry in resource_metadata:
                                if entry["resourceType"] == "ModelEvaluation":
                                    eval_resource_uri = entry["resourceUri"]
                                    eval_resource_name = eval_resource_uri.split("v1/")[
                                        1
                                    ]
                                    eval_resource = model_evaluation.ModelEvaluation(
                                        evaluation_name=eval_resource_name
                                    )
                                    eval_resource._gca_resource = (
                                        eval_resource._get_gca_resource(
                                            resource_name=eval_resource_name
                                        )
                                    )

                            return eval_resource
