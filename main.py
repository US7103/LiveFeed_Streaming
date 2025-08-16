import eventlet
eventlet.monkey_patch()
from flask import Flask, render_template, Response, jsonify, request
from flask_socketio import SocketIO
from camera import VideoCamera
from pymongo import MongoClient

app = Flask(__name__, static_url_path='/images', static_folder='public/images')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")
camera = VideoCamera(socketio=socketio)

client = MongoClient("mongodb://localhost:27017/")
db = client["intrusion_db"]
collection = db["detections"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/cameras')
def cameras():
    return render_template('cameras.html')

@app.route('/all_detections')
def all_detections():
    return render_template('detections.html')

@app.route('/video_feed')
def video_feed():
    def gen(camera):
        while True:
            frame = camera.get_frame()
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    return Response(gen(camera), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detections')
def get_detections():
    docs = collection.find().sort("timestamp", -1).limit(20)
    data = []
    for doc in docs:
        data.append({
            "label": doc.get("label", ""),
            "confidence": doc.get("confidence", 0),
            "timestamp": doc.get("timestamp", ""),
            "image": doc.get("image", ""),
            "msg": doc.get("msg", "No description")
        })
    return jsonify(data)

@app.route('/update_roi', methods=['POST'])
def update_roi():
    data = request.get_json()
    roi_str = data.get("roi", "")
    try:
        coords = tuple(map(int, roi_str.split(",")))
        if len(coords) != 4:
            raise ValueError("Invalid number of coordinates.")
        camera.roi_coords = coords
        return jsonify({"success": True, "message": f"ROI updated to {coords}"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 400


if __name__ == '__main__':
    socketio.run(app, debug=True)