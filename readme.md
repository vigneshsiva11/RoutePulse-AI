# TRAFFIX — Smart Traffic Control with Ambulance Priority

TRAFFIX is a four-lane traffic-management prototype that uses computer vision to count vehicles, stream annotated camera footage, and select the lane that receives a green signal. When a custom ambulance detector confirms an emergency vehicle, the controller immediately prioritizes that lane and holds the route open briefly to tolerate missed video frames.

## Highlights

- Live MJPEG video streams for four traffic lanes
- Vehicle counting with YOLOv8 (`car`, `motorcycle`, `bus`, and `truck`)
- Ambulance-specific emergency detection—ordinary buses never trigger priority
- Automatic signal selection based on traffic volume, overridden by ambulance priority
- Web dashboard with lane state, vehicle counts, emergency alerts, and traffic charts
- REST endpoints for status checks and manual signal-control testing

## How it works

```text
Lane video → vehicle detector + ambulance detector → traffic controller → Flask API → React dashboard
```

The backend is the single source of truth for signal decisions. In normal operation, it opens the busiest lane. If the ambulance model detects an allowed emergency label, that lane receives priority for 30 seconds after the last detection. The frontend only displays the controller state; it does not make signal decisions.

## Tech stack

- **Frontend:** React, Vite, Tailwind CSS, Recharts
- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-CORS
- **Computer vision:** Ultralytics YOLOv8 and OpenCV
- **Storage:** SQLite

## Repository layout

```text
Backend/
  app.py                       Flask application entry point
  routes/                      Traffic, control, and emergency APIs
  services/traffic_analyzer.py Detection pipeline and signal policy
  services/emv_detector.py     Ambulance-model integration
  models/                      Place ambulance model here (not committed)
  videos/                      Place four lane videos here (not committed)
Frontend/
  src/pages/Dashboard.jsx      Live traffic dashboard
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm
- A YOLOv8 vehicle model at `Backend/yolov8n.pt` (included in this project checkout)

For the **full ambulance-priority demo**, also obtain the following project assets from the team or event submission package. They are excluded from Git because they are large binary files.

```text
Backend/models/ambulance.pt
Backend/videos/lane1.mp4
Backend/videos/lane2.mp4
Backend/videos/lane3.mp4
Backend/videos/lane4.mp4
```

Without the ambulance model, the backend still runs vehicle counting, but emergency priority is disabled. Without lane videos, the dashboard loads but has no camera frames to process.

## Run locally

### 1. Clone the repository

```powershell
git clone <your-repository-url>
cd traffic_updated
```

### 2. Set up and start the backend

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r .\Backend\requirements.txt
cd .\Backend
python .\app.py
```

The API starts at `http://127.0.0.1:5000`. The first start can take a moment while the YOLO models load.

### 3. Set up and start the frontend

Open a second terminal from the repository root:

```powershell
cd .\Frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal (typically `http://localhost:5173`). Keep the backend running while using the dashboard.

## Configuration

The ambulance detector uses these optional environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `EMERGENCY_MODEL_PATH` | `Backend/models/ambulance.pt` | Path to the custom ambulance YOLO model |
| `EMERGENCY_CLASS_NAMES` | `ambulance`, `emergency vehicle`, `emergency_vehicle` | Comma-separated model label names treated as emergency vehicles |
| `EMERGENCY_CONFIDENCE` | `0.45` | Minimum ambulance-detection confidence |

Example:

```powershell
$env:EMERGENCY_MODEL_PATH = 'D:\models\ambulance.pt'
$env:EMERGENCY_CONFIDENCE = '0.50'
python .\app.py
```

## API

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/traffic/status` | Lane states, vehicle counts, timers, and emergency status |
| `GET` | `/traffic/stream/<lane>` | MJPEG stream for `lane1`–`lane4` |
| `GET` | `/control/status` | Current controller status |
| `POST` | `/control/change-light` | Manually set a lane light; disables smart control |
| `POST` | `/control/stc-toggle` | Enable or disable smart traffic control |
| `GET` | `/emv/emv-status` | Whether an ambulance is detected and the affected lanes |
| `POST` | `/emv/clear-emv` | Apply the current emergency-priority policy |

Example manual-control request:

```powershell
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:5000/control/change-light' `
  -ContentType 'application/json' `
  -Body '{"lane":"lane1","state":"green"}'
```

## Important notes

- The standard COCO YOLOv8 model has no ambulance class; its `bus` class is **not** used to trigger an emergency signal.
- Demo videos and custom model weights are intentionally listed in `.gitignore`. Share them separately with judges or host them in a release/cloud drive, then provide the download link here.
- This is a hackathon prototype for simulation and demonstration—not a production traffic-control system.

## Team

Built for the hackathon by the TRAFFIX team.
