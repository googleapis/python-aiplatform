#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2020 Google LLC
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
        'batch_migrate_resources': ('parent', 'migrate_resource_requests', ),
        'cancel_batch_prediction_job': ('name', ),
        'cancel_custom_job': ('name', ),
        'cancel_data_labeling_job': ('name', ),
        'cancel_hyperparameter_tuning_job': ('name', ),
        'cancel_pipeline_job': ('name', ),
        'cancel_training_pipeline': ('name', ),
        'create_batch_prediction_job': ('parent', 'batch_prediction_job', ),
        'create_custom_job': ('parent', 'custom_job', ),
        'create_data_labeling_job': ('parent', 'data_labeling_job', ),
        'create_dataset': ('parent', 'dataset', ),
        'create_endpoint': ('parent', 'endpoint', ),
        'create_hyperparameter_tuning_job': ('parent', 'hyperparameter_tuning_job', ),
        'create_index': ('parent', 'index', ),
        'create_index_endpoint': ('parent', 'index_endpoint', ),
        'create_model_deployment_monitoring_job': ('parent', 'model_deployment_monitoring_job', ),
        'create_pipeline_job': ('parent', 'pipeline_job', 'pipeline_job_id', ),
        'create_specialist_pool': ('parent', 'specialist_pool', ),
        'create_training_pipeline': ('parent', 'training_pipeline', ),
        'delete_batch_prediction_job': ('name', ),
        'delete_custom_job': ('name', ),
        'delete_data_labeling_job': ('name', ),
        'delete_dataset': ('name', ),
        'delete_endpoint': ('name', ),
        'delete_hyperparameter_tuning_job': ('name', ),
        'delete_index': ('name', ),
        'delete_index_endpoint': ('name', ),
        'delete_model': ('name', ),
        'delete_model_deployment_monitoring_job': ('name', ),
        'delete_pipeline_job': ('name', ),
        'delete_specialist_pool': ('name', 'force', ),
        'delete_training_pipeline': ('name', ),
        'deploy_index': ('index_endpoint', 'deployed_index', ),
        'deploy_model': ('endpoint', 'deployed_model', 'traffic_split', ),
        'explain': ('endpoint', 'instances', 'parameters', 'explanation_spec_override', 'deployed_model_id', ),
        'export_data': ('name', 'export_config', ),
        'export_model': ('name', 'output_config', ),
        'get_annotation_spec': ('name', 'read_mask', ),
        'get_batch_prediction_job': ('name', ),
        'get_custom_job': ('name', ),
        'get_data_labeling_job': ('name', ),
        'get_dataset': ('name', 'read_mask', ),
        'get_endpoint': ('name', ),
        'get_hyperparameter_tuning_job': ('name', ),
        'get_index': ('name', ),
        'get_index_endpoint': ('name', ),
        'get_model': ('name', ),
        'get_model_deployment_monitoring_job': ('name', ),
        'get_model_evaluation': ('name', ),
        'get_model_evaluation_slice': ('name', ),
        'get_pipeline_job': ('name', ),
        'get_specialist_pool': ('name', ),
        'get_training_pipeline': ('name', ),
        'import_data': ('name', 'import_configs', ),
        'list_annotations': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', 'order_by', ),
        'list_batch_prediction_jobs': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', ),
        'list_custom_jobs': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', ),
        'list_data_items': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', 'order_by', ),
        'list_data_labeling_jobs': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', 'order_by', ),
        'list_datasets': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', 'order_by', ),
        'list_endpoints': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', 'order_by', ),
        'list_hyperparameter_tuning_jobs': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', ),
        'list_index_endpoints': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', ),
        'list_indexes': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', ),
        'list_model_deployment_monitoring_jobs': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', ),
        'list_model_evaluations': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', ),
        'list_model_evaluation_slices': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', ),
        'list_models': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', 'order_by', ),
        'list_pipeline_jobs': ('parent', 'filter', 'page_size', 'page_token', ),
        'list_specialist_pools': ('parent', 'page_size', 'page_token', 'read_mask', ),
        'list_training_pipelines': ('parent', 'filter', 'page_size', 'page_token', 'read_mask', ),
        'pause_model_deployment_monitoring_job': ('name', ),
        'predict': ('endpoint', 'instances', 'parameters', ),
        'raw_predict': ('endpoint', 'http_body', ),
        'resume_model_deployment_monitoring_job': ('name', ),
        'search_migratable_resources': ('parent', 'page_size', 'page_token', 'filter', ),
        'search_model_deployment_monitoring_stats_anomalies': ('model_deployment_monitoring_job', 'deployed_model_id', 'objectives', 'feature_display_name', 'page_size', 'page_token', 'start_time', 'end_time', ),
        'undeploy_index': ('index_endpoint', 'deployed_index_id', ),
        'undeploy_model': ('endpoint', 'deployed_model_id', 'traffic_split', ),
        'update_dataset': ('dataset', 'update_mask', ),
        'update_endpoint': ('endpoint', 'update_mask', ),
        'update_index': ('index', 'update_mask', ),
        'update_index_endpoint': ('index_endpoint', 'update_mask', ),
        'update_model': ('model', 'update_mask', ),
        'update_model_deployment_monitoring_job': ('model_deployment_monitoring_job', 'update_mask', ),
        'update_specialist_pool': ('specialist_pool', 'update_mask', ),
        'upload_model': ('parent', 'model', ),
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
