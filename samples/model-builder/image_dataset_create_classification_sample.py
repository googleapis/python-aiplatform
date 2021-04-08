from google.cloud import aiplatform

#  [START aiplatform_sdk_image_dataset_create_classification_sample]
def image_dataset_create_classification_sample(
    project: str, location: str, display_name: str, src_uris: list
):
    aiplatform.init(project=project, location=location)

    ds = aiplatform.ImageDataset.create(
        display_name=display_name,
        gcs_source=src_uris,
        import_schema_uri=aiplatform.schema.dataset.ioformat.image.single_label_classification,
    )

    print(ds.display_name)
    print(ds.name)
    print(ds.resource_name)
    print(ds.metadata_schema_uri)
    return ds


#  [END aiplatform_sdk_image_dataset_create_classification_sample]
