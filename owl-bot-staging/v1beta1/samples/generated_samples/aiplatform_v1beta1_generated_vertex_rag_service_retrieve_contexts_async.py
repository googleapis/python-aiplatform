# -*- coding: utf-8 -*-
# Copyright 2024 Google LLC
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
# Generated code. DO NOT EDIT!
#
# Snippet for RetrieveContexts
# NOTE: This snippet has been automatically generated for illustrative purposes only.
# It may require modifications to work in your environment.

# To install the latest published package dependency, execute the following:
#   python3 -m pip install google-cloud-aiplatform


# [START aiplatform_v1beta1_generated_VertexRagService_RetrieveContexts_async]
# This snippet has been automatically generated and should be regarded as a
# code template only.
# It will require modifications to work:
# - It may require correct/in-range values for request initialization.
# - It may require specifying regional endpoints when creating the service
#   client as shown in:
#   https://googleapis.dev/python/google-api-core/latest/client_options.html
from google.cloud import aiplatform_v1beta1


async def sample_retrieve_contexts():
    # Create a client
    client = aiplatform_v1beta1.VertexRagServiceAsyncClient()

    # Initialize request argument(s)
    vertex_rag_store = aiplatform_v1beta1.VertexRagStore()
    vertex_rag_store.rag_corpora = ['rag_corpora_value1', 'rag_corpora_value2']

    query = aiplatform_v1beta1.RagQuery()
    query.text = "text_value"

    request = aiplatform_v1beta1.RetrieveContextsRequest(
        vertex_rag_store=vertex_rag_store,
        parent="parent_value",
        query=query,
    )

    # Make the request
    response = await client.retrieve_contexts(request=request)

    # Handle the response
    print(response)

# [END aiplatform_v1beta1_generated_VertexRagService_RetrieveContexts_async]
