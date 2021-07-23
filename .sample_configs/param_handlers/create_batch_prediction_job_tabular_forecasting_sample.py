def make_parent(parent: str) -> str:
    parent = parent

    return parent


def make_batch_prediction_job(
    display_name: str,
    model_name: str,
    gcs_source_uri: str,
    gcs_destination_output_uri_prefix: str,
    predictions_format: str,
) -> google.cloud.aiplatform_v1beta1.types.batch_prediction_job.BatchPredictionJob:
    batch_prediction_job = {
        "display_name": display_name,
        # Format: 'projects/{project}/locations/{location}/models/{model_id}'
        "model": model_name,
        "input_config": {
            "instances_format": predictions_format,
            "gcs_source": {"uris": [gcs_source_uri]},
        },
        "output_config": {
            "predictions_format": predictions_format,
            "gcs_destination": {"output_uri_prefix": gcs_destination_output_uri_prefix},
        },
    }
    return batch_prediction_job
