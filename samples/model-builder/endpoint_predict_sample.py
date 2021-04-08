from google.cloud import aiplatform

#  [START aiplatform_sdk_endpoint_predict_sample]
def endpoint_predict_sample(project, location, instances, endpoint):
    aiplatform.init(project=project, location=location)

    prediction = endpoint.predict(instances=instances)
    print(prediction)
    return prediction


#  [END aiplatform_sdk_endpoint_predict_sample]
