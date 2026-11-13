# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Check installed provider and native editable namespace package coexistence."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile


def run(arguments, **kwargs):
    result = subprocess.run(arguments, capture_output=True, text=True, **kwargs)
    if result.returncode:
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
        result.check_returncode()
    return result


def check(provider_wheel, directory, install_order):
    sibling = directory / "sibling"
    package = sibling / "src" / "google" / "namespace_install_probe"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text(
        '"""A native editable namespace sibling."""\nVALUE = "editable sibling"\n'
    )
    (sibling / "pyproject.toml").write_text(
        '[build-system]\nrequires = ["flit_core>=3.12,<4"]\n'
        'build-backend = "flit_core.buildapi"\n'
        '[project]\nname = "google-namespace-install-probe"\nversion = "0.0.0"\n'
        'description = "Namespace installation control"\n'
        '[tool.flit.module]\nname = "google.namespace_install_probe"\n'
    )
    editable_output = directory / "editable-wheel"
    editable_output.mkdir()
    run(
        [
            sys.executable,
            "-I",
            "-B",
            "-c",
            "import sys; from flit_core.buildapi import build_editable; "
            "print(build_editable(sys.argv[1]))",
            str(editable_output),
        ],
        cwd=sibling,
    )
    editable_wheels = list(editable_output.glob("*.whl"))
    assert len(editable_wheels) == 1, editable_wheels
    editable_wheel = editable_wheels[0]
    environment = directory / "environment"
    run([sys.executable, "-I", "-B", "-m", "venv", str(environment)])
    python = environment / (
        "Scripts/python.exe" if sys.platform == "win32" else "bin/python"
    )
    wheels = {"provider": provider_wheel, "sibling": editable_wheel}
    for selected in install_order:
        run(
            [
                str(python),
                "-I",
                "-B",
                "-m",
                "pip",
                "install",
                "--no-deps",
                str(wheels[selected]),
            ]
        )
    expected = {}
    with zipfile.ZipFile(provider_wheel) as archive:
        for name in archive.namelist():
            if name.endswith((".py", ".pth")):
                assert not name.startswith("/") and ".." not in Path(name).parts
                expected[name] = hashlib.sha256(archive.read(name)).hexdigest()
    run(
        [
            str(python),
            "-I",
            "-B",
            "-c",
            """
import hashlib, importlib.metadata, json, sys
from pathlib import Path
distribution = importlib.metadata.distribution("google-cloud-aiplatform")
expected = json.load(sys.stdin)
for name, digest in expected.items():
    path = Path(distribution.locate_file(name))
    assert path.is_file() and not path.is_symlink(), name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, name
""",
        ],
        input=json.dumps(expected),
    )
    probe = """
import importlib.util, json
import google.namespace_install_probe as sibling
assert sibling.VALUE == "editable sibling"
provider = importlib.util.find_spec("google.cloud.aiplatform")
assert provider is not None and provider.origin is not None
print(json.dumps({"sibling": sibling.__file__, "provider": provider.origin}))
"""
    normal = run([str(python), "-B", "-c", probe], cwd=directory)
    isolated = run([str(python), "-I", "-B", "-c", probe], cwd=directory)
    normal_result = json.loads(normal.stdout)
    isolated_result = json.loads(isolated.stdout)
    for result in [normal_result, isolated_result]:
        assert Path(result["sibling"]).resolve() == (package / "__init__.py").resolve()
        assert Path(result["provider"]).resolve().is_relative_to(environment.resolve())
    return {
        "installOrder": install_order,
        "normalImport": normal_result,
        "isolatedImport": isolated_result,
        "providerRuntimeAndStartupFilesVerified": len(expected),
        "editableWheelSHA256": hashlib.sha256(editable_wheel.read_bytes()).hexdigest(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("provider_wheel", type=Path)
    arguments = parser.parse_args()
    provider_wheel = arguments.provider_wheel.resolve(strict=True)
    if not provider_wheel.name.endswith("-py3-none-any.whl"):
        raise ValueError(
            f"Wheel filename does not declare Python 3: {provider_wheel.name}"
        )
    with zipfile.ZipFile(provider_wheel) as archive:
        wheel_metadata = [
            name for name in archive.namelist() if name.endswith(".dist-info/WHEEL")
        ]
        if len(wheel_metadata) != 1:
            raise ValueError(f"Expected one WHEEL metadata member: {wheel_metadata}")
        tags = [
            line.removeprefix("Tag: ")
            for line in archive.read(wheel_metadata[0]).decode().splitlines()
            if line.startswith("Tag: ")
        ]
        if tags != ["py3-none-any"]:
            raise ValueError(f"Wheel metadata does not declare only Python 3: {tags}")
    results = []
    with tempfile.TemporaryDirectory(prefix="namespace-install-") as temporary:
        for index, order in enumerate(
            [("provider", "sibling"), ("sibling", "provider")]
        ):
            directory = Path(temporary) / str(index)
            directory.mkdir()
            results.append(check(provider_wheel, directory, order))
    print(
        json.dumps(
            {
                "python": sys.version,
                "providerWheel": provider_wheel.name,
                "providerWheelSHA256": hashlib.sha256(
                    provider_wheel.read_bytes()
                ).hexdigest(),
                "results": results,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
