from google.cloud import aiplatform

#  [START aiplatform_sdk_image_dataset_create_sample]
def image_dataset_create_sample(project: str, 
                                location: str, 
                                display_name: str
                               ):
    aiplatform.init(project=project, location=location)

    ds = aiplatform.ImageDataset.create(display_name=display_name)

    print(ds.display_name)
    print(ds.name)
    print(ds.resource_name)
    return ds


#  [END aiplatform_sdk_image_dataset_create_sample]
