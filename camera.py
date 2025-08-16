import cv2
import torch
import os
import numpy as np
import threading
import time
import json
from datetime import datetime
from pymongo import MongoClient
import base64
import requests
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

RTSP_URL = os.getenv("RTSP_URL")
MONGO_URI = os.getenv("MONGO_URI")
OLLAMA_API = os.getenv("OLLAMA_API")
SAVE_PATH = os.getenv("SAVE_PATH", "public/images")  # default if not in .env

class VideoCamera:
    def __init__(self, socketio=None):
        print("[INFO] Loading YOLOv5...")
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', trust_repo=True)
        self.model.eval()

        self.video = self._open_stream()
        self.SAVE_PATH = SAVE_PATH
        os.makedirs(self.SAVE_PATH, exist_ok=True)

        self.mongo_client = MongoClient(MONGO_URI)
        self.db = self.mongo_client["intrusion_db"]
        self.collection = self.db["detections"]

        self.frame_count = 0
        self.roi_coords = (50, 100, 700, 500)
        self.socketio = socketio

        self.lock = threading.Lock()

    def _open_stream(self):
        cap = cv2.VideoCapture(RTSP_URL)
        if not cap.isOpened():
            print("[ERROR] Could not open RTSP stream.")
        return cap

    def _reconnect_stream(self):
        print("[INFO] Reconnecting to RTSP stream...")
        if self.video.isOpened():
            self.video.release()
        time.sleep(1)
        self.video = self._open_stream()

    def handle_detection_async(self, full_frame, x1, y1, x2, y2, label, conf):
        def worker():
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{label}_{timestamp}.jpg"
                filepath = os.path.join(self.SAVE_PATH, filename)

                # Annotate and save frame
                annotated_frame = full_frame.copy()
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(annotated_frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                cv2.imwrite(filepath, annotated_frame)

                # Generate description using Ollama
                description = "⚠️ Description not available."
                try:
                    with open(filepath, "rb") as img_file:
                        img_base64 = base64.b64encode(img_file.read()).decode('utf-8')

                    ollama_response = requests.post(
                        OLLAMA_API,
                        json={
                            "model": "llava",
                            "prompt": "Describe the image briefly",
                            "images": [img_base64]
                        },
                        timeout=30  # short timeout to avoid blocking forever
                    )

                    if ollama_response.ok:
                        try:
                            data = ollama_response.json()
                            description = data.get("response", "⚠️ No description.")
                        except Exception:
                            description = "⚠️ Failed to parse response."
                    else:
                        description = "⚠️ Description service failed."

                except Exception as e:
                    print("[ERROR] Ollama API call failed:", str(e))

                # Save to MongoDB
                record = {
                    "label": label,
                    "confidence": float(conf),
                    "timestamp": timestamp,
                    "image": f"/images/{filename}",
                    "msg": description
                }
                self.collection.insert_one(record)
                print(f"[INFO] Detection saved and emitted: {record}")

                if self.socketio:
                    self.socketio.emit('new_detection', record)

            except Exception as e:
                print("[ERROR] Detection worker error:", e)

        threading.Thread(target=worker, daemon=True).start()

    def person_inside_roi(self, x1, y1, x2, y2):
        roi_x1, roi_y1, roi_x2, roi_y2 = self.roi_coords
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        return (roi_x1 <= cx <= roi_x2) and (roi_y1 <= cy <= roi_y2)

    def get_frame(self):
        success, frame = self.video.read()
        if not success or frame is None:
            self._reconnect_stream()
            return None

        annotated = frame.copy()
        roi_x1, roi_y1, roi_x2, roi_y2 = self.roi_coords
        cv2.rectangle(annotated, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 255), 2)
        cv2.putText(annotated, "ROI Area", (roi_x1, roi_y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        if self.frame_count % 10 == 0:
            with torch.no_grad():  # prevents memory leak
                results = self.model(frame)
            detections = results.xyxy[0]

            for det in detections:
                cls_id = int(det[5])
                conf = float(det[4])
                if conf > 0.5:
                    label = self.model.names[cls_id]
                    x1, y1, x2, y2 = map(int, det[:4])

                    if label == "person" and self.person_inside_roi(x1, y1, x2, y2):
                        print(f"[ALERT] {label} in ROI ({conf:.2f})")
                        self.handle_detection_async(frame, x1, y1, x2, y2, label, conf)

            annotated = results.render()[0]

        self.frame_count += 1
        ret, jpeg = cv2.imencode('.jpg', annotated)
        time.sleep(0.01)  # prevent CPU spike
        return jpeg.tobytes() if ret else None

    def __del__(self):
        print("[INFO] Releasing video stream...")
        if self.video.isOpened():
            self.video.release()

