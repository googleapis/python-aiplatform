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

import copy
from typing import Any, Dict, Mapping, Optional, Union


class PipelineRuntimeConfigBuilder(object):
    """Pipeline RuntimeConfig builder.

    Constructs a RuntimeConfig spec with pipeline_root and parameter overrides.
    """

    def __init__(
        self,
        pipeline_root: str,
        parameter_types: Mapping[str, str],
        parameter_values: Optional[Dict[str, Any]] = None,
    ):
        """Creates a PipelineRuntimeConfigBuilder object.

        Args:
          pipeline_root (str):
              Required. The root of the pipeline outputs.
          parameter_types (Mapping[str, str]):
              Required. The mapping from pipeline parameter name to its type.
          parameter_values (Dict[str, Any]):
              Optional. The mapping from runtime parameter name to its value.
        """
        self._pipeline_root = pipeline_root
        self._parameter_types = parameter_types
        self._parameter_values = copy.deepcopy(parameter_values or {})

    @classmethod
    def from_job_spec_json(
        cls, job_spec: Mapping[str, Any],
    ) -> "PipelineRuntimeConfigBuilder":
        """Creates a PipelineRuntimeConfigBuilder object from PipelineJob json spec.

        Args:
          job_spec (Mapping[str, Any]):
              Required. The PipelineJob spec.

        Returns:
          A PipelineRuntimeConfigBuilder object.
        """
        runtime_config_spec = job_spec["runtimeConfig"]
        parameter_input_definitions = (
            job_spec["pipelineSpec"]["root"]
            .get("inputDefinitions", {})
            .get("parameters", {})
        )
        parameter_types = {k: v["type"] for k, v in parameter_input_definitions.items()}

        pipeline_root = runtime_config_spec.get("gcs_output_directory")
        parameter_values = _parse_runtime_parameters(runtime_config_spec)
        return cls(pipeline_root, parameter_types, parameter_values)

    def update_pipeline_root(self, pipeline_root: Optional[str]) -> None:
        """Updates pipeline_root value.

        Args:
          pipeline_root (str):
              Optional. The root of the pipeline outputs.
        """
        if pipeline_root:
            self._pipeline_root = pipeline_root

    def update_runtime_parameters(
        self, parameter_values: Optional[Mapping[str, Any]] = None
    ) -> None:
        """Merges runtime parameter values.

        Args:
          parameter_values (Mapping[str, Any]):
              Optional. The mapping from runtime parameter names to its values.
        """
        if parameter_values:
            self._parameter_values.update(parameter_values)

    def build(self) -> Dict[str, Any]:
        """Build a RuntimeConfig proto.

        Raises:
          ValueError: if the pipeline root is not specified.
        """
        if not self._pipeline_root:
            raise ValueError(
                "Pipeline root must be specified, either during "
                "compile time, or when calling the service."
            )
        return {
            "gcs_output_directory": self._pipeline_root,
            "parameters": {
                k: self._get_vertex_value(k, v)
                for k, v in self._parameter_values.items()
                if v is not None
            },
        }

    def _get_vertex_value(
        self, name: str, value: Union[int, float, str]
    ) -> Dict[str, Any]:
        """Converts primitive values into Vertex pipeline Value proto message.

        Args:
          name (str):
              Required. The name of the pipeline parameter.
          value (Union[int, float, str]):
              Required. The value of the pipeline parameter.

        Returns:
          A dictionary represents the Vertex pipeline Value proto message.

        Raises:
          ValueError: if the parameter name is not found in pipeline root
          inputs, or value is none.
        """
        if not value:
            raise ValueError("None values should be filterd out.")

        if name not in self._parameter_types:
            raise ValueError(
                "The pipeline parameter {} is not found in the "
                "pipeline job input definitions.".format(name)
            )

        result = {}
        if self._parameter_types[name] == "INT":
            result["intValue"] = value
        elif self._parameter_types[name] == "DOUBLE":
            result["doubleValue"] = value
        elif self._parameter_types[name] == "STRING":
            result["stringValue"] = value
        else:
            raise TypeError("Got unknown type of value: {}".format(value))

        return result


def _parse_runtime_parameters(
    runtime_config_spec: Mapping[str, Any]
) -> Optional[Dict[str, Any]]:
    """Extracts runtime parameters from runtime config json spec.

    Raises:
        TypeError: if the parameter type is not one of 'INT', 'DOUBLE', 'STRING'.
    """
    runtime_parameters = runtime_config_spec.get("parameters")
    if not runtime_parameters:
        return None

    result = {}
    for name, value in runtime_parameters.items():
        if "intValue" in value:
            result[name] = int(value["intValue"])
        elif "doubleValue" in value:
            result[name] = float(value["doubleValue"])
        elif "stringValue" in value:
            result[name] = value["stringValue"]
        else:
            raise TypeError("Got unknown type of value: {}".format(value))

    return result
