"""
Run a rest API exposing the yolov5s object detection model
"""
import argparse
import io
from PIL import Image

import torch
from flask import Flask, request
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)
DETECTION_URL = "/v1/object-detection/yolov5"


@app.route(DETECTION_URL, methods=["POST"])
def predict():
    if not request.method == "POST":
        return

    if request.files.get("image"):
        image_file = request.files["image"]
        user_settings = "15"
        image_bytes = image_file.read()
        img = Image.open(io.BytesIO(image_bytes))
        results = model(img, size=640) # reduce size=320 for faster inference
        df = results.pandas().xyxy[0]
        # 'userSettings'라는 새로운 열을 추가하고 값을 설정합니다.
        # 이 예제에서는 'userSettings'의 값으로 'your_value'를 설정합니다.
        df['filter'] = user_settings
        # DataFrame을 JSON으로 변환합니다.
        json_data = df.to_json(orient="records")
        returnJson = request_to_spring(json_data)
        return returnJson

def request_to_spring(json_data):
    print(json_data)
    url = 'http://192.168.0.7:8080/api/test2'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json_data)
    return response.text

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flask api exposing yolov5 model")
    parser.add_argument("--port", default=5000, type=int, help="port number")
    parser.add_argument('--model', default='yolov5s', help='model to run, i.e. --model yolov5s')
    args = parser.parse_args()

    #model = torch.hub.load('ultralytics/yolov5', args.model)
    model = torch.hub.load('ultralytics/yolov5', 'custom', path='C:/yolov5-master/best_test_drink.pt', force_reload=True,
                           skip_validation=True)  # local model
    app.run(host="0.0.0.0", port=args.port)  # debug=True causes Restarting with stat
