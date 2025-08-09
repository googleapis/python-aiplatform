# Description:
#   Public preview version of subset of Vertex AI SDK.

load("//third_party/bazel_rules/rules_python/python:py_library.bzl", "py_library")

package(
    default_applicable_licenses = ["//devtools/compliance/licenses:no_external_contributions"],
)

py_library(
    name = "model_garden",
    srcs = ["model_garden.py"],
    # TODO(b/429261909): Remove the visibility once the public API is ready.
    visibility = [
        "//cloud/ai/platform/llm/tests/managed_oss_tuning:__subpackages__",
    ],
    deps = [
    ],
)

py_library(
    name = "tuning",
    srcs = glob(
        [
            "tuning/*.py",
        ],
    ),
    # TODO(atyfto): Remove the visibility once the public API is ready.
    visibility = [
        "//cloud/ai/platform/llm/tests/managed_oss_tuning:__subpackages__",
    ],
    deps = [
    ],
)
