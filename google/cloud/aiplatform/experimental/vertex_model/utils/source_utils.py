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

import ast
import inspect
import tempfile
from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple

import google.cloud.aiplatform.experimental.vertex_model.serializers as serializers


try:
    # Available in a colab environment.
    from google.colab import _message  # pylint: disable=g-import-not-at-top
except ImportError:
    _message = None


def jupyter_notebook_to_file(json_notebook: Optional[str]) -> str:
    """ Retrieves the source code of a Python notebook and writes it to a file.

    Args:
        json_notebook (Optional[str]): JSON representation of a Python notebook.

    Returns:
        A string representing the file name where the Python notebook source code
        has been written.
    """

    if json_notebook is None:
        response = _message.blocking_request("get_ipynb", request="", timeout_sec=200)
        cells = response["ipynb"]["cells"]

        if response is None:
            raise RuntimeError("Unable to get the notebook contents.")
    else:
        response = json_notebook
        cells = response["cells"]
    
    py_content = []
    script_lines = []

    for cell in cells:
        if cell["cell_type"] == "code":
            # Add newline char to the last line of a code cell.
            cell["source"][-1] += "\n"

            # Combine all code cells.
            py_content.extend(cell["source"])

    for line in py_content:
        if line.strip().startswith("%"):
            raise RuntimeError("Magic commands '%' are not supported.")

        elif line.strip().startswith("!"):
            commands_list = line.strip()[1:].split(" ")
            script_lines.extend(
                [
                    "import sys\n",
                    "import subprocess\n",
                    f"print(subprocess.run({commands_list}",
                    ",capture_output=True, text=True).stdout)\n",
                ]
            )

        elif not (line.strip().startswith("get_ipython().system(")):
            script_lines.append(line)

    # Create a tmp wrapped entry point script file.
    file_descriptor, output_file = tempfile.mkstemp(suffix=".py")
    with open(output_file, "w") as f:
        f.writelines(script_lines)

    return output_file


def get_import_lines(path):
    """Given the path to a python file, retrieves the imports in the file
       and returns a list of strings representing each import, with aliases
       included.

    Args:
        path (str): A path representing a python file whose imports will be
                    retrieved.

    Returns:
        Several strings representing each of the import lines in the provided
        Python file.
    """

    with open(path) as f:
        root = ast.parse(f.read(), path)

    for node in ast.iter_child_nodes(root):
        line = ""

        if isinstance(node, ast.ImportFrom):
            line += f"from {node.module} "

        if isinstance(node, (ast.Import, ast.ImportFrom)):
            line += "import "

            for i, name in enumerate(node.names):
                line += f"{name.name}"

                if name.asname:
                    line += f" as {name.asname}"

                if len(node.names) > 0 and i < len(node.names) - 1:
                    line += ", "

        yield line


def import_try_except(obj: Any):
    """Given an object defined in either a local file or a Colab notebook,
       retrieves the imports in its class definition.

    Args:
        obj (Any): An object defined within the same workflow where this
                   method is called.

    Returns:
        Several strings representing the import lines necessary for the
        objects class definition to compile in the user workflow.
    """

    try:
        module = inspect.getmodule(obj.__class__)
        import_lines = "\n".join(get_import_lines(module.__file__))
        return import_lines

    except AttributeError:
        import_lines = "\n".join(get_import_lines(jupyter_notebook_to_file(None)))
        return import_lines


class SourceMaker:
    def __init__(self, obj_cls: Any):
        parent_classes = []

        for base_class in obj_cls.__bases__:
            if (
                base_class.__name__ != obj_cls.__name__
                and base_class.__name__ != "VertexModel"
            ):
                module = base_class.__module__
                name = base_class.__qualname__

                if module is not None and module != "__builtin__":
                    name = module + "." + name

                parent_classes.append(name)

        parent_classes.append("base.VertexModel")

        self.source = [
            "class {}({}):".format(obj_cls.__name__, ", ".join(parent_classes))
        ]

    def add_method(self, method_str: str):
        self.source.extend(method_str.split("\n"))


def _make_class_source(obj: Any) -> str:
    """Retrieves the source code for the class obj represents, usually an extension
       of VertexModel.

    Args:
        obj (Any): An instantiation of a user-written class
    """
    source_maker = SourceMaker(obj.__class__)

    for key, value in inspect.getmembers(obj):
        if (inspect.ismethod(value) or inspect.isfunction(value)) and value.__repr__()[
            len("<bound method ") :
        ].startswith(obj.__class__.__name__):
            source_maker.add_method(inspect.getsource(value))

    source_maker.add_method(inspect.getsource(obj.fit))
    source_maker.add_method(inspect.getsource(obj.predict))

    return "\n".join(source_maker.source)


def _make_source(
    cls_source: str,
    cls_name: str,
    instance_method: str,
    pass_through_params: Dict[str, str],
    param_name_to_serialized_info: Dict[str, Tuple[str, type]],
    obj: Any,
) -> str:
    """Converts a class source to a string including necessary imports.

    Args:
        cls_source (str): A string representing the source code of a user-written class.
        cls_name (str): The name of the class cls_source represents.
        instance_method (str): The method within the class that should be called from __main__
        pass_through_params (dict[str, Any]): A dictionary mapping primitive parameter names to their values
        param_name_to_serialize_info (dict[str, A]): A dictionary mapping a parameter that needed
                                                     to be serialized to its URI and value type.
        obj (Any): the object whose source is being generated

    Returns:
        A string representing a user-written class that can be written to a file in
        order to yield an inner script for the ModelBuilder SDK. The only difference
        between the user-written code and the string returned by this method is that
        the user has the option to specify a method to call from __main__.
    """

    src = import_try_except(obj)

    # Hard-coded specific files as imports because (for now) all data serialization methods
    # come from one of two files and we do not retrieve the modules for the methods at this
    # moment.
    src = src + "\n".join(
        [
            "import os",
            "try:",
            "\tfrom google.cloud.aiplatform.experimental.vertex_model.serializers.pandas import _deserialize_dataframe",
            "except ImportError:",
            "\tpass",
            "try:",
            "\tfrom google.cloud.aiplatform.experimental.vertex_model.serializers.pytorch import _deserialize_dataloader",
            "except ImportError:",
            "\tpass",
            cls_source,
        ]
    )

    # Then, instantiate model
    # First, grab args and kwargs using the _constructor_arguments variable in VertexModel
    class_args = inspect.signature(obj.__class__.__init__).bind(
        obj, *obj._constructor_arguments[0], **obj._constructor_arguments[1]
    )

    # need to index pass the first arg to avoid the call to self.
    src = src + f"my_model = {cls_name}({','.join(map(str, class_args.args[1:]))})\n"

    if instance_method is not None:
        # Start function call
        src = src + f"my_model.{instance_method}("

        default_serialization = serializers.build_map_safe()
        all_serialization = default_serialization.copy()
        all_serialization.update(obj._data_serialization_mapping)

        # Iterate through parameters.
        for (
            parameter_name,
            (parameter_uri, parameter_type),
        ) in param_name_to_serialized_info.items():
            deserializer = all_serialization[parameter_type][0]

            if deserializer.__name__ not in [
                "_deserialize_dataframe",
                "_deserialize_dataloader",
            ]:
                src = (
                    src
                    + f"{parameter_name}=my_model.{deserializer.__name__}('{parameter_uri}'), "
                )
            else:
                src = (
                    src
                    + f"{parameter_name}={deserializer.__name__}('{parameter_uri}'), "
                )

        for parameter_name, parameter_value in pass_through_params.items():
            if type(parameter_value) is str:
                src = src + f"{parameter_name}='{parameter_value}', "
            else:
                src = src + f"{parameter_name}={parameter_value}, "

        src = src + ")\n"

    # Workaround for bug in training that writes to models/ instead of model/
    src = src + "model_dir = os.getenv('AIP_MODEL_DIR')\n"
    src = src + "if model_dir.endswith('models'):\n"
    src = src + "\tmodel_dir = model_dir[:-1]\n"
    src = src + "if model_dir.endswith('models/'):\n"
    src = src + "\tmodel_dir = model_dir[:-2] + '/'\n"

    src = src + "my_model.serialize_model(model_dir, my_model, 'local')"

    return src
