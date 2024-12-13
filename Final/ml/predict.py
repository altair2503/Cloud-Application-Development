from google.cloud import aiplatform

def predict():
    # Create a Prediction Service Client
    client = aiplatform.gapic.PredictionServiceClient()

    # Replace 'your-project', 'your-region', and 'your-endpoint-id' with your actual values
    endpoint = client.endpoint_path(
        project='cloudappdevassignment3-ak', 
        location='us-central1', 
        endpoint='projects/1059330099607/locations/us-central1'
    )

    # Replace with the actual input data for your model
    instance = {'input': [1.0, 2.0, 3.0]}  # Example input for a model expecting a list of floats  # Ensure your data matches the model's input format

    # Make the prediction
    response = client.predict(endpoint=endpoint, instances=[instance])
    
    # Print the predictions
    print(response.predictions)

if __name__ == '__main__':
    predict()