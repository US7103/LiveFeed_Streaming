# LiveFeed_Streaming

## Overview

**LiveFeed_Streaming** is a real-time video analytics and intrusion detection dashboard. It allows users to monitor live camera feeds, set detection regions, and receive instant notifications of detected intrusions (e.g., person detected within a specified ROI) using deep learning (YOLOv5) and a friendly web-based interface.

- **Languages:** HTML, Python, JavaScript, CSS
- **Backend:** Flask + Flask-SocketIO
- **Frontend:** Responsive web dashboard (HTML/CSS/JS)
- **Detection:** YOLOv5 (PyTorch)
- **Database:** MongoDB (for detection records)
- **Live Streaming:** MJPEG via Flask
- **Realtime Updates:** WebSocket (Socket.IO)
- **Cloud Vision (Optional):** Uses Ollama API for auto-generated image descriptions

## Features

- 📺 **Live Video Feed:** Watch real-time camera streams in your browser.
- 🚨 **Intrusion Detection:** Detects and highlights intrusions (e.g., people) using YOLOv5.
- 🟨 **Region of Interest (ROI):** Set a custom detection zone on the video stream.
- 💬 **Realtime Alerts:** Instant updates and event cards on the dashboard when intrusions detected.
- 🗃️ **Detection History:** View past detections with image, label, confidence, and timestamp.
- 🛠️ **Settings Panel:** Configure ROI and other dashboard options.
- 🤖 **AI Descriptions:** Integrates with Ollama API to generate brief descriptions of detection images.

## Quick Start

### Requirements

- Python 3.7+
- MongoDB (running locally or remote)
- [YOLOv5](https://github.com/ultralytics/yolov5) (automatically downloaded via PyTorch Hub)
- [Ollama API](https://ollama.com/) (optional for image descriptions)
- RTSP-compatible camera or video stream

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/US7103/LiveFeed_Streaming.git
   cd LiveFeed_Streaming
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   - Create a `.env` file in the root directory:
     ```
     RTSP_URL=rtsp://your_camera_stream
     MONGO_URI=mongodb://localhost:27017/
     SAVE_PATH=public/images
     OLLAMA_API=http://localhost:11435/api/generate    # Optional
     ```

4. **Start MongoDB** (ensure it is running on your configured host/port).

5. **Run the app:**
   ```bash
   python main.py
   ```
   The dashboard will be available at [http://localhost:5000](http://localhost:5000).

## Usage

- **Live View:** Home page shows the live camera feed and recent detections.
- **All Detections:** View all recent detection events as cards, each with image, label, confidence, timestamp, and AI-generated description (if enabled).
- **Settings:** Set or update the ROI (Region of Interest) as comma-separated coordinates (e.g., `50,100,700,500`).
- **Camera Configuration:** (If implemented) Set camera RTSP stream URL.

## Project Structure

```
.
├── main.py              # Flask app entry point
├── camera.py            # Video capture and detection logic (YOLOv5)
├── requirements.txt
├── static/
│   ├── js/
│   │   └── script.js    # Frontend Socket.IO & detection rendering
│   └── css/
│       └── style.css    # Custom styles
├── templates/
│   ├── base.html        # Base template
│   ├── index.html       # Live feed dashboard UI
│   ├── settings.html    # ROI and dashboard settings
│   └── detections.html  # (All) detection history
├── public/images/       # Saved detection images
└── .env                 # Environment variables
```

## Core Technologies

- **Flask**: Serves web interface, REST API, and MJPEG video streaming.
- **Flask-SocketIO**: Enables real-time communication for new detections.
- **PyTorch & YOLOv5**: Runs object detection on video frames.
- **MongoDB**: Stores detection logs with images and metadata.
- **Socket.IO (JS)**: Receives real-time detection updates on frontend.
- **Ollama API**: (Optional) Provides AI-generated image summaries.

## API Endpoints

- `/video_feed` : MJPEG stream of annotated video.
- `/detections` : JSON of recent detections.
- `/update_roi` : POST endpoint to update ROI coordinates.
- `/settings`, `/all_detections`, `/cameras`: Web UI routes.

## Environment Variables

| Variable     | Description                        |
|--------------|------------------------------------|
| RTSP_URL     | Camera video stream URL (RTSP)     |
| MONGO_URI    | MongoDB connection URI             |
| SAVE_PATH    | Path to save detection images      |
| OLLAMA_API   | (Optional) Ollama API endpoint     |

## Screenshots

<!-- Optionally add screenshots/gifs of the dashboard here. -->

## Contributing

Contributions are welcome! Please open issues or pull requests.

## License

[MIT License](LICENSE)  <!-- Update if your repo uses a different license -->

---

> _Built for real-time, AI-powered security monitoring. 🚦_
