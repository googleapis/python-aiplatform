from google.cloud import aiplatform

#  [START aiplatform_sdk_image_dataset_import_data_sample]
def image_dataset_import_data_sample(
    project: str, location: str, src_uris: list, import_schema_uri: str, dataset_id: str
):
    aiplatform.init(project=project, location=location)

    ds = aiplatform.ImageDataset(dataset_id)

    ds = ds.import_data(
        gcs_source=src_uris, import_schema_uri=import_schema_uri, sync=True
    )

    print(ds.display_name)
    print(ds.name)
    print(ds.resource_name)
    return ds


#  [END aiplatform_sdk_image_dataset_import_data_sample]
