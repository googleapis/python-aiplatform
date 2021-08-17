# How to get model URI?

app = FastAPI()
gcs_client = storage.Client()

if obj._model is None:
    my_model = model._deserialize_remote_model(output_dir)
else:
    output_dir = obj._model._gca_resource.artifact_uri
    model_uri = pathlib.Path(output_dir) / ("my_" + obj.training_mode + "_model.pth")
    my_model = model._deserialize_remote_model(str(model_uri))


@app.post(os.environ["AIP_PREDICT_ROUTE"])
async def predict(request: Request):
    body = await request.json()

    instances = body["instances"]
    inputs = np.asarray(instances)
    outputs = my_model.predict(inputs)

    return {"predictions": [_class_names[class_num] for class_num in outputs]}
