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

import abc
from typing import Dict, List, Optional, Sequence, Tuple, Union

import proto

from google.cloud.aiplatform.compat.types import study as gca_study_compat

_SCALE_TYPE_MAP = {
    "linear": gca_study_compat.StudySpec.ParameterSpec.ScaleType.UNIT_LINEAR_SCALE,
    "log": gca_study_compat.StudySpec.ParameterSpec.ScaleType.UNIT_LOG_SCALE,
    "reverse_log": gca_study_compat.StudySpec.ParameterSpec.ScaleType.UNIT_REVERSE_LOG_SCALE,
    "unspecified": gca_study_compat.StudySpec.ParameterSpec.ScaleType.SCALE_TYPE_UNSPECIFIED,
}


class _ParameterSpec(metaclass=abc.ABCMeta):
    """Base class represents a single parameter to optimize."""

    def __init__(
        self,
        conditional_parameter_spec: Optional[Dict[str, "_ParameterSpec"]] = None,
        parent_values: Optional[List[Union[float, int, str]]] = None,
    ):

        self.conditional_parameter_spec = conditional_parameter_spec
        self.parent_values = parent_values

    @property
    @classmethod
    @abc.abstractmethod
    def _proto_parameter_value_class(self) -> proto.Message:
        """The proto representation of this parameter."""
        pass

    @property
    @classmethod
    @abc.abstractmethod
    def _parameter_value_map(self) -> Tuple[Tuple[str, str]]:
        """A Tuple map of parameter key to underlying proto key."""
        pass

    @property
    @classmethod
    @abc.abstractmethod
    def _parameter_spec_value_key(self) -> Tuple[Tuple[str, str]]:
        """The ParameterSpec key this parameter should be assigned."""
        pass

    @property
    def _proto_parameter_value_spec(self) -> proto.Message:
        """Converts this parameter to it's parameter value representation."""
        proto_parameter_value_spec = self._proto_parameter_value_class()
        for self_attr_key, proto_attr_key in self._parameter_value_map:
            setattr(
                proto_parameter_value_spec, proto_attr_key, getattr(self, self_attr_key)
            )
        return proto_parameter_value_spec

    def _to_parameter_spec(
        self, parameter_id: str
    ) -> gca_study_compat.StudySpec.ParameterSpec:
        """Converts this parameter to ParameterSpec."""
        # TODO: Conditional parameters
        parameter_spec = gca_study_compat.StudySpec.ParameterSpec(
            parameter_id=parameter_id,
            scale_type=_SCALE_TYPE_MAP.get(getattr(self, "scale", "unspecified")),
        )

        setattr(
            parameter_spec,
            self._parameter_spec_value_key,
            self._proto_parameter_value_spec,
        )

        return parameter_spec


class DoubleParameterSpec(_ParameterSpec):

    _proto_parameter_value_class = (
        gca_study_compat.StudySpec.ParameterSpec.DoubleValueSpec
    )
    _parameter_value_map = (("min", "min_value"), ("max", "max_value"))
    _parameter_spec_value_key = "double_value_spec"

    def __init__(
        self, min: float, max: float, scale: str,
    ):
        """
        Value specification for a parameter in ``DOUBLE`` type.

        Args:
            min (float):
                Required. Inclusive minimum value of the
                parameter.
            max (float):
                Required. Inclusive maximum value of the
                parameter.
            scale (str):
                Required. The type of scaling that should be applied to this parameter.

                Accepts: 'linear', 'log', 'reverse_log'
        """

        super().__init__()

        self.min = min
        self.max = max
        self.scale = scale


class IntegerParameterSpec(_ParameterSpec):

    _proto_parameter_value_class = (
        gca_study_compat.StudySpec.ParameterSpec.IntegerValueSpec
    )
    _parameter_value_map = (("min", "min_value"), ("max", "max_value"))
    _parameter_spec_value_key = "integer_value_spec"

    def __init__(
        self, min: int, max: int, scale: str,
    ):
        """
        Value specification for a parameter in ``INTEGER`` type.

        Args:
            min (float):
                Required. Inclusive minimum value of the
                parameter.
            max (float):
                Required. Inclusive maximum value of the
                parameter.
            scale (str):
                Required. The type of scaling that should be applied to this parameter.

                Accepts: 'linear', 'log', 'reverse_log'
        """

        super().__init__()

        self.min = min
        self.max = max
        self.scale = scale


class CategoricalParameterSpec(_ParameterSpec):

    _proto_parameter_value_class = (
        gca_study_compat.StudySpec.ParameterSpec.CategoricalValueSpec
    )
    _parameter_value_map = (("values", "values"),)
    _parameter_spec_value_key = "categorical_value_spec"

    def __init__(
        self, values: Sequence[str],
    ):
        """Value specification for a parameter in ``CATEGORICAL`` type.

        Args:
            values (Sequence[str]):
                Required. The list of possible categories.
        """

        super().__init__()

        self.values = values


class DiscreteParameterSpec(_ParameterSpec):

    _proto_parameter_value_class = (
        gca_study_compat.StudySpec.ParameterSpec.DiscreteValueSpec
    )
    _parameter_value_map = (("values", "values"),)
    _parameter_spec_value_key = "discrete_value_spec"

    def __init__(
        self, values: Sequence[float], scale: str,
    ):
        """Value specification for a parameter in ``DISCRETE`` type.

        values (Sequence[float]):
            Required. A list of possible values.
            The list should be in increasing order and at
            least 1e-10 apart. For instance, this parameter
            might have possible settings of 1.5, 2.5, and
            4.0. This list should not contain more than
            1,000 values.
        scale (str):
            Required. The type of scaling that should be applied to this parameter.

            Accepts: 'linear', 'log', 'reverse_log'
        """

        super().__init__()

        self.values = values
        self.scale = scale
