load("//third_party/bazel_rules/rules_python/python:proto.bzl", "py_proto_library")

package(
    default_applicable_licenses = ["//devtools/compliance/licenses:no_external_contributions"],
    default_visibility = ["//third_party/py/google/cloud/aiplatform:__subpackages__"],
)

proto_library(
    name = "server_info",
    srcs = ["server_info.proto"],
    features = ["-proto_dynamic_mode_static_link"],
)

py_proto_library(
    name = "server_info_py_pb2",
    api_version = 2,
    deps = [":server_info"],
)
