from google.cloud import aiplatform

#  [START aiplatform_sdk_automl_image_classification_training_job_sample]
def automl_image_classification_training_job_sample(project : str,
                                                    location: str,
                                                    display_name : str,
                                                    dataset  : aiplatform.datasets.image_dataset.ImageDataset):
    aiplatform.init(project=project, location=location)
    
    job = aiplatform.AutoMLImageTrainingJob(
        display_name=display_name,
        prediction_type='classification',
        multi_label=False,
        model_type="CLOUD",
        base_model=None
    )

    model = job.run(
        dataset=dataset,
        model_display_name=display_name,     
        training_fraction_split=0.6,
        validation_fraction_split=0.2,
        test_fraction_split=0.2,
        budget_milli_node_hours=8000,
        disable_early_stopping=False
    )
    
    print(model.display_name)
    print(model.name)
    print(model.resource_name)
    print(model.description)
    print(model.uri)
    
    return model
#  [END aiplatform_sdk_automl_image_classification_training_job_sample]
