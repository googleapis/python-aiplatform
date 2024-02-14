#! /usr/bin/env python3
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
import argparse
import os
import libcst as cst
import pathlib
import sys
from typing import (Any, Callable, Dict, List, Sequence, Tuple)


def partition(
    predicate: Callable[[Any], bool],
    iterator: Sequence[Any]
) -> Tuple[List[Any], List[Any]]:
    """A stable, out-of-place partition."""
    results = ([], [])

    for i in iterator:
        results[int(predicate(i))].append(i)

    # Returns trueList, falseList
    return results[1], results[0]


class aiplatformCallTransformer(cst.CSTTransformer):
    CTRL_PARAMS: Tuple[str] = ('retry', 'timeout', 'metadata')
    METHOD_TO_PARAMS: Dict[str, Tuple[str]] = {
        'add_context_artifacts_and_executions': ('context', 'artifacts', 'executions', ),
        'add_context_children': ('context', 'child_contexts', ),
        'add_execution_events': ('execution', 'events', ),
        'add_trial_measurement': ('trial_name', 'measurement', ),
        'batch_cancel_pipeline_jobs': ('parent', 'names', ),
        'batch_create_features': ('parent', 'requests', ),
        'batch_create_tensorboard_runs': ('parent', 'requests', ),
        'batch_create_tensorboard_time_series': ('parent', 'requests', ),
        'batch_delete_pipeline_jobs': ('parent', 'names', ),
        'batch_import_evaluated_annotations': ('parent', 'evaluated_annotations', ),
        'batch_import_model_evaluation_slices': ('parent', 'model_evaluation_slices', ),
        'batch_migrate_resources': ('parent', 'migrate_resource_requests', ),
        'batch_read_feature_values': ('featurestore', 'destination', 'entity_type_specs', 'csv_read_instances', 'bigquery_read_instances', 'pass_through_fields', 'start_time', ),
        'batch_read_tensorboard_time_series_data': ('tensorboard', 'time_series', ),
        'cancel_batch_prediction_job': ('name', ),
        'cancel_custom_job': ('name', ),
        'cancel_data_labeling_job': ('name', ),
        'cancel_hyperparameter_tuning_job': ('name', ),
        'cancel_nas_job': ('name', ),
        'cancel_pipeline_job': ('name', ),
        'cancel_training_pipeline': ('name', ),
        'check_trial_early_stopping_state': ('trial_name', ),
        'complete_trial': ('name', 'final_measurement', 'trial_infeasible', 'infeasible_reason', ),
        'compute_tokens': ('endpoint', 'instances', ),
        'copy_model': ('parent', 'source_model', 'model_id', 'parent_model', 'encryption_spec', ),
        'count_tokens': ('endpoint', 'model', 'instances', 'contents', ),
        'create_artifact': ('parent', 'artifact', 'artifact_id', ),
        'create_batch_prediction_job': ('parent', 'batch_prediction_job', ),
        'create_context': ('parent', 'context', 'context_id', ),
        'create_custom_job': ('parent', 'custom_job', ),
        'create_data_labeling_job': ('parent', 'data_labeling_job', ),
        'create_dataset': ('parent', 'dataset', ),
        'create_dataset_version': ('parent', 'dataset_version', ),
        'create_deployment_resource_pool': ('parent', 'deployment_resource_pool', 'deployment_resource_pool_id', ),
        'create_endpoint': ('parent', 'endpoint', 'endpoint_id', ),
        'create_entity_type': ('parent', 'entity_type_id', 'entity_type', ),
        'create_execution': ('parent', 'execution', 'execution_id', ),
        'create_feature': ('parent', 'feature', 'feature_id', ),
        'create_feature_group': ('parent', 'feature_group', 'feature_group_id', ),
        'create_feature_online_store': ('parent', 'feature_online_store', 'feature_online_store_id', ),
        'create_featurestore': ('parent', 'featurestore', 'featurestore_id', ),
        'create_feature_view': ('parent', 'feature_view', 'feature_view_id', 'run_sync_immediately', ),
        'create_hyperparameter_tuning_job': ('parent', 'hyperparameter_tuning_job', ),
        'create_index': ('parent', 'index', ),
        'create_index_endpoint': ('parent', 'index_endpoint', ),
        'create_metadata_schema': ('parent', 'metadata_schema', 'metadata_schema_id', ),
        'create_metadata_store': ('parent', 'metadata_store', 'metadata_store_id', ),
        'create_model_deployment_monitoring_job': ('parent', 'model_deployment_monitoring_job', ),
        'create_nas_job': ('parent', 'nas_job', ),
        'create_persistent_resource': ('parent', 'persistent_resource', 'persistent_resource_id', ),
        'create_pipeline_job': ('parent', 'pipeline_job', 'pipeline_job_id', 'preflight_validations', ),
        'create_schedule': ('parent', 'schedule', ),
        'create_specialist_pool': ('parent', 'specialist_pool', ),
        'create_study': ('parent', 'study', ),
        'create_tensorboard': ('parent', 'tensorboard', ),
        'create_tensorboard_experiment': ('parent', 'tensorboard_experiment_id', 'tensorboard_experiment', ),
        'create_tensorboard_run': ('parent', 'tensorboard_run', 'tensorboard_run_id', ),
        'create_tensorboard_time_series': ('parent', 'tensorboard_time_series', 'tensorboard_time_series_id', ),
        'create_training_pipeline': ('parent', 'training_pipeline', ),
        'create_trial': ('parent', 'trial', ),
        'delete_artifact': ('name', 'etag', ),
        'delete_batch_prediction_job': ('name', ),
        'delete_context': ('name', 'force', 'etag', ),
        'delete_custom_job': ('name', ),
        'delete_data_labeling_job': ('name', ),
        'delete_dataset': ('name', ),
        'delete_dataset_version': ('name', ),
        'delete_deployment_resource_pool': ('name', ),
        'delete_endpoint': ('name', ),
        'delete_entity_type': ('name', 'force', ),
        'delete_execution': ('name', 'etag', ),
        'delete_feature': ('name', ),
        'delete_feature_group': ('name', 'force', ),
        'delete_feature_online_store': ('name', 'force', ),
        'delete_featurestore': ('name', 'force', ),
        'delete_feature_values': ('entity_type', 'select_entity', 'select_time_range_and_feature', ),
        'delete_feature_view': ('name', ),
        'delete_hyperparameter_tuning_job': ('name', ),
        'delete_index': ('name', ),
        'delete_index_endpoint': ('name', ),
        'delete_metadata_store': ('name', 'force', ),
        'delete_model': ('name', ),
        'delete_model_deployment_monitoring_job': ('name', ),
        'delete_model_version': ('name', ),
        'delete_nas_job': ('name', ),
        'delete_persistent_resource': ('name', ),
        'delete_pipeline_job': ('name', ),
        'delete_saved_query': ('name', ),
        'delete_schedule': ('name', ),
        'delete_specialist_pool': ('name', 'force', ),
        'delete_study': ('name', ),
        'delete_tensorboard': ('name', ),
        'delete_tensorboard_experiment': ('name', ),
        'delete_tensorboard_run': ('name', ),
        'delete_tensorboard_time_series': ('name', ),
        'delete_training_pipeline': ('name', ),
        'delete_trial': ('name', ),
        'deploy_index': ('index_endpoint', 'deployed_index', ),
        'deploy_model': ('endpoint', 'deployed_model', 'traffic_split', ),
        'direct_predict': ('endpoint', 'inputs', 'parameters', ),
        'direct_raw_predict': ('endpoint', 'method_name', 'input', ),
        'explain': ('endpoint', 'instances', 'parameters', 'explanation_spec_override', 'concurrent_explanation_spec_override', 'deployed_model_id', ),
        'export_data': ('name', 'export_config', ),
        'export_feature_values': ('entity_type', 'destination', 'feature_selector', 'snapshot_export', 'full_export', 'settings', ),
        'export_model': ('name', 'output_config', ),
        'export_tensorboard_time_series_data': ('tensorboard_time_series', 'filter', 'page_size', 'page_token', 'order_by', ),
        'fetch_feature_values': ('feature_view', 'id', 'data_key', 'data_format', 'format_', ),
        'find_neighbors': ('index_endpoint', 'deployed_index_id', 'queries', 'return_full_datapoint', ),
        'generate_content': ('model', 'contents', 'tools', 'safety_settings', 'generation_config', ),
        'get_annotation_spec': ('name', 'read_mask', ),
        'get_artifact': ('name', ),
        'get_batch_prediction_job': ('name', ),
        'get_context': ('name', ),
        'get_custom_job': ('name', ),
        'get_data_labeling_job': ('name', ),
        'get_dataset': ('name', 'read_mask', ),
        'get_dataset_version': ('name', 'read_mask', ),
        'get_deployment_resource_pool': ('name', ),
        'get_endpoint': ('name', ),
        'get_entity_type': ('name', ),
        'get_execution': ('name', ),
        'get_feature': ('name', ),
        'get_feature_group': ('name', ),
        'get_feature_online_store': ('name', ),
        'get_featurestore': ('name', ),
        'get_feature_view': ('name', ),
        'get_feature_view_sync': ('name', ),
        'get_hyperparameter_tuning_job': ('name', ),
        'get_index': ('name', ),
        'get_index_endpoint': ('name', ),
        'get_metadata_schema': ('name', ),
        'get_metadata_store': ('name', ),
        'get_model': ('name', ),
        'get_model_deployment_monitoring_job': ('name', ),
        'get_model_evaluation': ('name', ),
        'get_model_evaluation_slice': ('name', ),
        'get_nas_job': ('name', ),
        'get_nas_trial_detail': ('name', ),
        'get_persistent_resource': ('name', ),
        'get_pipeline_job': ('name', ),
        'get_publisher_model': ('name', 'language_code', 'view', ),
        'get_schedule': ('name', ),
        'get_specialist_pool': ('name', ),
        'get_study': ('name', ),
        'get_tensorboard': ('name', ),
        'get_tensorboard_experiment': ('name', ),
        'get_tensorboard_run': ('name', ),
        'get_tensorboard_time_series': ('name', ),
        'get_training_pipeline': ('name', ),
        'get_trial': ('name', ),
        'import_data': ('name', 'import_configs', ),
        'import_feature_values': ('entity_type', 'feature_specs', 'avro_source', 'bigquery_source', 'csv_source', 'feature_time_field', 'feature_time', 'entity_id_field', 'disable_online_serving', 'worker_count', 'disable_ingestion_analysis', ),
        'import_model_evaluation': ('parent', 'model_evaluation', ),
        'list_annotations': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', 'order_by', ),
        'list_artifacts': ('parent', 'page_size', 'page_token', 'filter', 'order_by', ),
        'list_batch_prediction_jobs': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', ),
        'list_contexts': ('parent', 'page_size', 'page_token', 'filter', 'order_by', ),
        'list_custom_jobs': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', ),
        'list_data_items': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', 'order_by', ),
        'list_data_labeling_jobs': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', 'order_by', ),
        'list_datasets': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', 'order_by', ),
        'list_dataset_versions': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', 'order_by', ),
        'list_deployment_resource_pools': ('parent', 'page_size', 'page_token', ),
        'list_endpoints': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', ),
        'list_entity_types': ('parent', 'filter', 'page_size', 'page_token', 'order_by', 'read_mask', ),
        'list_executions': ('parent', 'page_size', 'page_token', 'filter', 'order_by', ),
        'list_feature_groups': ('parent', 'filter', 'page_size', 'page_token', 'order_by', ),
        'list_feature_online_stores': ('parent', 'filter', 'page_size', 'page_token', 'order_by', ),
        'list_features': ('parent', 'filter', 'page_size', 'page_token', 'order_by', 'read_mask', 'latest_stats_count', ),
        'list_featurestores': ('parent', 'filter', 'page_size', 'page_token', 'order_by', 'read_mask', ),
        'list_feature_views': ('parent', 'filter', 'page_size', 'page_token', 'order_by', ),
        'list_feature_view_syncs': ('parent', 'filter', 'page_size', 'page_token', 'order_by', ),
        'list_hyperparameter_tuning_jobs': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', ),
        'list_index_endpoints': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', ),
        'list_indexes': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', ),
        'list_metadata_schemas': ('parent', 'page_size', 'page_token', 'filter', ),
        'list_metadata_stores': ('parent', 'page_size', 'page_token', ),
        'list_model_deployment_monitoring_jobs': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', ),
        'list_model_evaluations': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', ),
        'list_model_evaluation_slices': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', ),
        'list_models': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', ),
        'list_model_versions': ('name', 'page_size', 'page_token', 'filter', 'read_mask', 'order_by', ),
        'list_nas_jobs': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', ),
        'list_nas_trial_details': ('parent', 'page_size', 'page_token', ),
        'list_optimal_trials': ('parent', ),
        'list_persistent_resources': ('parent', 'page_size', 'page_token', ),
        'list_pipeline_jobs': ('parent', 'filter', 'page_size', 'page_token', 'order_by', 'read_mask', ),
        'list_publisher_models': ('parent', 'filter', 'page_size', 'page_token', 'view', 'order_by', 'language_code', ),
        'list_saved_queries': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', 'order_by', ),
        'list_schedules': ('parent', 'filter', 'page_size', 'page_token', 'order_by', ),
        'list_specialist_pools': ('parent', 'page_size', 'page_token', 'read_mask', ),
        'list_studies': ('parent', 'page_token', 'page_size', ),
        'list_tensorboard_experiments': ('parent', 'filter', 'page_size', 'page_token', 'order_by', 'read_mask', ),
        'list_tensorboard_runs': ('parent', 'filter', 'page_size', 'page_token', 'order_by', 'read_mask', ),
        'list_tensorboards': ('parent', 'filter', 'page_size', 'page_token', 'order_by', 'read_mask', ),
        'list_tensorboard_time_series': ('parent', 'filter', 'page_size', 'page_token', 'order_by', 'read_mask', ),
        'list_training_pipelines': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', ),
        'list_trials': ('parent', 'page_token', 'page_size', ),
        'lookup_study': ('parent', 'display_name', ),
        'merge_version_aliases': ('name', 'version_aliases', ),
        'mutate_deployed_index': ('index_endpoint', 'deployed_index', ),
        'mutate_deployed_model': ('endpoint', 'deployed_model', 'update_mask', ),
        'pause_model_deployment_monitoring_job': ('name', ),
        'pause_schedule': ('name', ),
        'predict': ('endpoint', 'instances', 'parameters', ),
        'purge_artifacts': ('parent', 'filter', 'force', ),
        'purge_contexts': ('parent', 'filter', 'force', ),
        'purge_executions': ('parent', 'filter', 'force', ),
        'query_artifact_lineage_subgraph': ('artifact', 'max_hops', 'filter', ),
        'query_context_lineage_subgraph': ('context', ),
        'query_deployed_models': ('deployment_resource_pool', 'page_size', 'page_token', ),
        'query_execution_inputs_and_outputs': ('execution', ),
        'raw_predict': ('endpoint', 'http_body', ),
        'read_feature_values': ('entity_type', 'entity_id', 'feature_selector', ),
        'read_index_datapoints': ('index_endpoint', 'deployed_index_id', 'ids', ),
        'read_tensorboard_blob_data': ('time_series', 'blob_ids', ),
        'read_tensorboard_size': ('tensorboard', ),
        'read_tensorboard_time_series_data': ('tensorboard_time_series', 'max_data_points', 'filter', ),
        'read_tensorboard_usage': ('tensorboard', ),
        'remove_context_children': ('context', 'child_contexts', ),
        'remove_datapoints': ('index', 'datapoint_ids', ),
        'restore_dataset_version': ('name', ),
        'resume_model_deployment_monitoring_job': ('name', ),
        'resume_schedule': ('name', 'catch_up', ),
        'search_data_items': ('dataset', 'order_by_data_item', 'order_by_annotation', 'saved_query', 'data_labeling_job', 'data_item_filter', 'annotations_filter', 'annotation_filters', 'field_mask', 'annotations_limit', 'page_size', 'order_by', 'page_token', ),
        'search_features': ('location', 'query', 'page_size', 'page_token', ),
        'search_migratable_resources': ('parent', 'page_size', 'page_token', 'filter', ),
        'search_model_deployment_monitoring_stats_anomalies': ('model_deployment_monitoring_job', 'deployed_model_id', 'objectives', 'feature_display_name', 'page_size', 'page_token', 'start_time', 'end_time', ),
        'search_nearest_entities': ('feature_view', 'query', 'return_full_entity', ),
        'server_streaming_predict': ('endpoint', 'inputs', 'parameters', ),
        'stop_trial': ('name', ),
        'stream_direct_predict': ('endpoint', 'inputs', 'parameters', ),
        'stream_direct_raw_predict': ('endpoint', 'method_name', 'input', ),
        'stream_generate_content': ('model', 'contents', 'tools', 'safety_settings', 'generation_config', ),
        'streaming_predict': ('endpoint', 'inputs', 'parameters', ),
        'streaming_raw_predict': ('endpoint', 'method_name', 'input', ),
        'streaming_read_feature_values': ('entity_type', 'entity_ids', 'feature_selector', ),
        'suggest_trials': ('parent', 'suggestion_count', 'client_id', 'contexts', ),
        'sync_feature_view': ('feature_view', ),
        'undeploy_index': ('index_endpoint', 'deployed_index_id', ),
        'undeploy_model': ('endpoint', 'deployed_model_id', 'traffic_split', ),
        'update_artifact': ('artifact', 'update_mask', 'allow_missing', ),
        'update_context': ('context', 'update_mask', 'allow_missing', ),
        'update_dataset': ('dataset', 'update_mask', ),
        'update_endpoint': ('endpoint', 'update_mask', ),
        'update_entity_type': ('entity_type', 'update_mask', ),
        'update_execution': ('execution', 'update_mask', 'allow_missing', ),
        'update_explanation_dataset': ('model', 'examples', ),
        'update_feature': ('feature', 'update_mask', ),
        'update_feature_group': ('feature_group', 'update_mask', ),
        'update_feature_online_store': ('feature_online_store', 'update_mask', ),
        'update_featurestore': ('featurestore', 'update_mask', ),
        'update_feature_view': ('feature_view', 'update_mask', ),
        'update_index': ('index', 'update_mask', ),
        'update_index_endpoint': ('index_endpoint', 'update_mask', ),
        'update_model': ('model', 'update_mask', ),
        'update_model_deployment_monitoring_job': ('model_deployment_monitoring_job', 'update_mask', ),
        'update_persistent_resource': ('persistent_resource', 'update_mask', ),
        'update_schedule': ('schedule', 'update_mask', ),
        'update_specialist_pool': ('specialist_pool', 'update_mask', ),
        'update_tensorboard': ('update_mask', 'tensorboard', ),
        'update_tensorboard_experiment': ('update_mask', 'tensorboard_experiment', ),
        'update_tensorboard_run': ('update_mask', 'tensorboard_run', ),
        'update_tensorboard_time_series': ('update_mask', 'tensorboard_time_series', ),
        'upload_model': ('parent', 'model', 'parent_model', 'model_id', 'service_account', ),
        'upsert_datapoints': ('index', 'datapoints', 'update_mask', ),
        'write_feature_values': ('entity_type', 'payloads', ),
        'write_tensorboard_experiment_data': ('tensorboard_experiment', 'write_run_data_requests', ),
        'write_tensorboard_run_data': ('tensorboard_run', 'time_series_data', ),
    }

    def leave_Call(self, original: cst.Call, updated: cst.Call) -> cst.CSTNode:
        try:
            key = original.func.attr.value
            kword_params = self.METHOD_TO_PARAMS[key]
        except (AttributeError, KeyError):
            # Either not a method from the API or too convoluted to be sure.
            return updated

        # If the existing code is valid, keyword args come after positional args.
        # Therefore, all positional args must map to the first parameters.
        args, kwargs = partition(lambda a: not bool(a.keyword), updated.args)
        if any(k.keyword.value == "request" for k in kwargs):
            # We've already fixed this file, don't fix it again.
            return updated

        kwargs, ctrl_kwargs = partition(
            lambda a: a.keyword.value not in self.CTRL_PARAMS,
            kwargs
        )

        args, ctrl_args = args[:len(kword_params)], args[len(kword_params):]
        ctrl_kwargs.extend(cst.Arg(value=a.value, keyword=cst.Name(value=ctrl))
                           for a, ctrl in zip(ctrl_args, self.CTRL_PARAMS))

        request_arg = cst.Arg(
            value=cst.Dict([
                cst.DictElement(
                    cst.SimpleString("'{}'".format(name)),
cst.Element(value=arg.value)
                )
                # Note: the args + kwargs looks silly, but keep in mind that
                # the control parameters had to be stripped out, and that
                # those could have been passed positionally or by keyword.
                for name, arg in zip(kword_params, args + kwargs)]),
            keyword=cst.Name("request")
        )

        return updated.with_changes(
            args=[request_arg] + ctrl_kwargs
        )


def fix_files(
    in_dir: pathlib.Path,
    out_dir: pathlib.Path,
    *,
    transformer=aiplatformCallTransformer(),
):
    """Duplicate the input dir to the output dir, fixing file method calls.

    Preconditions:
    * in_dir is a real directory
    * out_dir is a real, empty directory
    """
    pyfile_gen = (
        pathlib.Path(os.path.join(root, f))
        for root, _, files in os.walk(in_dir)
        for f in files if os.path.splitext(f)[1] == ".py"
    )

    for fpath in pyfile_gen:
        with open(fpath, 'r') as f:
            src = f.read()

        # Parse the code and insert method call fixes.
        tree = cst.parse_module(src)
        updated = tree.visit(transformer)

        # Create the path and directory structure for the new file.
        updated_path = out_dir.joinpath(fpath.relative_to(in_dir))
        updated_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate the updated source file at the corresponding path.
        with open(updated_path, 'w') as f:
            f.write(updated.code)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""Fix up source that uses the aiplatform client library.

The existing sources are NOT overwritten but are copied to output_dir with changes made.

Note: This tool operates at a best-effort level at converting positional
      parameters in client method calls to keyword based parameters.
      Cases where it WILL FAIL include
      A) * or ** expansion in a method call.
      B) Calls via function or method alias (includes free function calls)
      C) Indirect or dispatched calls (e.g. the method is looked up dynamically)

      These all constitute false negatives. The tool will also detect false
      positives when an API method shares a name with another method.
""")
    parser.add_argument(
        '-d',
        '--input-directory',
        required=True,
        dest='input_dir',
        help='the input directory to walk for python files to fix up',
    )
    parser.add_argument(
        '-o',
        '--output-directory',
        required=True,
        dest='output_dir',
        help='the directory to output files fixed via un-flattening',
    )
    args = parser.parse_args()
    input_dir = pathlib.Path(args.input_dir)
    output_dir = pathlib.Path(args.output_dir)
    if not input_dir.is_dir():
        print(
            f"input directory '{input_dir}' does not exist or is not a directory",
            file=sys.stderr,
        )
        sys.exit(-1)

    if not output_dir.is_dir():
        print(
            f"output directory '{output_dir}' does not exist or is not a directory",
            file=sys.stderr,
        )
        sys.exit(-1)

    if os.listdir(output_dir):
        print(
            f"output directory '{output_dir}' is not empty",
            file=sys.stderr,
        )
        sys.exit(-1)

    fix_files(input_dir, output_dir)
