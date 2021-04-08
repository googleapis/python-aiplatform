import google.cloud.aiplatform as aip
import test_constants as constants
        
import endpoint_predict_sample

def test_endpoint_predict_sample(
    mock_sdk_init, mock_endpoint_predict, mock_init_endpoint
):
    endpoint = aip.Endpoint(constants.DATASET_NAME)
    endpoint_predict_sample.endpoint_predict_sample(
        project=constants.PROJECT, 
        location=constants.LOCATION, 
        instances=[],
        endpoint=endpoint                                 
    )
              
    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT,
        location=constants.LOCATION
    )
    mock_endpoint_predict.assert_called_once_with(
        instances=[]
    )     
    
