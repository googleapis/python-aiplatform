import abc
from typing import Dict, List, Optional, Tuple, Union

import proto

from google.cloud.aiplatform.compat.types import study as gca_study_compat

_scale_type_map = {
    'linear': gca_study_compat.StudySpec.ParameterSpec.ScaleType.UNIT_LINEAR_SCALE,
    'log': gca_study_compat.StudySpec.ParameterSpec.ScaleType.UNIT_LOG_SCALE,
    'reverse_log': gca_study_compat.StudySpec.ParameterSpec.ScaleType.UNIT_REVERSE_LOG_SCALE,
}


class _ParameterSpec(metaclass=abc.ABCMeta):

    def __init__(
        self,
        conditional_parameter_spec: Optional[Dict[str, '_Parameter']] = None,
        parent_values: Optional[List[Union[float, int, str]]] = None):

        self.conditional_parameter_spec = conditional_parameter_spec
        self.parent_values = parent_values

    @property
    @classmethod
    @abc.abstractmethod
    def _proto_parameter_value_class(self) -> proto.Message:
        pass

    @property
    @classmethod
    @abc.abstractmethod
    def _parameter_value_map(self) -> Tuple[Tuple[str, str]]:
        pass

    @property
    @classmethod
    @abc.abstractmethod
    def _parameter_spec_value_key(self) -> Tuple[Tuple[str, str]]:
        pass
    

    @property 
    def _proto_parameter_value_spec(self) -> proto.Message:
        proto_parameter_value_spec = self._proto_parameter_value_class()
        for self_attr_key, proto_attr_key in self._parameter_value_map:
            setattr(proto_parameter_value_spec, proto_attr_key, getattr(self, self_attr_key))
        return proto_parameter_value_spec


    def _to_parameter_spec(self, parameter_id: str) -> gca_study_compat.StudySpec.ParameterSpec:
        # TODO: Conditional parameters
        parameter_spec = gca_study_compat.StudySpec.ParameterSpec(
                parameter_id=parameter_id,
                scale_type=_scale_type_map.get(getattr(self, 'scale'))
            )

        setattr(parameter_spec, self._parameter_spec_value_key, self._proto_parameter_value_spec)

        return parameter_spec


class DoubleParameterSpec(_ParameterSpec):

    _proto_parameter_value_class = gca_study_compat.StudySpec.ParameterSpec.DoubleValueSpec
    _parameter_value_map = (('min', 'min_value'), ('max', 'max_value'))
    _parameter_spec_value_key = 'double_value_spec'
    
    def __init__(
        self,
        min: float,
        max: float,
        scale: str,
        conditional_parameter_spec: Optional[Dict[str, '_Parameter']] = None,
        parent_values: Optional[List[Union[float, int, str]]] = None
        ):

        super().__init__(
            conditional_parameter_spec=conditional_parameter_spec,
            parent_values=parent_values)

        self.min = min
        self.max = max
        self.scale=scale


class IntegerParameterSpec(_ParameterSpec):
   
    _proto_parameter_value_class = gca_study_compat.StudySpec.ParameterSpec.IntegerValueSpec
    _parameter_value_map = (('min', 'min_value'), ('max', 'max_value'))
    _parameter_spec_value_key = 'integer_value_spec'

    def __init__(
        self,
        min: int,
        max: int,
        scale: str,
        conditional_parameter_spec: Optional[Dict[str, '_Parameter']] = None,
        parent_values: Optional[List[Union[float, int, str]]] = None
        ):

        super().__init__(
            conditional_parameter_spec=conditional_parameter_spec,
            parent_value=parent_values)

        self.min = min
        self.max = max,
        self.scale=scale

class CategoricalValueSpec(_ParameterSpec):

    _proto_parameter_value_class = gca_study_compat.StudySpec.ParameterSpec.CategoricalValueSpec
    _parameter_value_map = (('values', 'values'))
    _parameter_spec_value_key = 'categorical_value_spec'
    
    def __init__(
        self,
        values: List[str],
        conditional_parameter_spec: Optional[Dict[str, '_Parameter']] = None,
        parent_values: Optional[List[Union[float, int, str]]] = None
        ):

        super().__init__(
            conditional_parameter_spec=conditional_parameter_spec,
            parent_value=parent_values)

        self.values = values


class DiscreteValueSpec(_ParameterSpec):

    _proto_parameter_value_class = gca_study_compat.StudySpec.ParameterSpec.DiscreteValueSpec
    _parameter_value_map = (('values', 'values'))
    _parameter_spec_value_key = 'discrete_value_spec'
    
    def __init__(
        self,
        values: List[float],
        scale: str,
        conditional_parameter_spec: Optional[Dict[str, '_Parameter']] = None,
        parent_values: Optional[List[Union[float, int, str]]] = None
        ):

        super().__init__(
            conditional_parameter_spec=conditional_parameter_spec,
            parent_value=parent_values)

        self.values = values
        self.scale = scale


