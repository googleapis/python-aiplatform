from google.cloud import aiplatform

#  [START aiplatform_sdk_custom_training_job_sample]
def custom_training_job_sample(project,
                               location,
                               bucket,
                               display_name,
                               script_path,
                               script_args,
                               train_image,
                               deploy_image,
                               requirements,
                               replica_count):
    aiplatform.init(project=project, location=location, staging_bucket=bucket)

    job = aiplatform.CustomTrainingJob(display_name=display_name, 
                                       script_path=script_path,
                                       container_uri=train_image,
                                       requirements=requirements,
                                       model_serving_container_image_uri=deploy_image)

    model = job.run(args=script_args,
                replica_count=replica_count, 
                model_display_name=display_name)
    
    return model
#  [END aiplatform_sdk_custom_training_job_sample]