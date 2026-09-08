# RoutePulse AI

> **From Emergency to Impact — Verify. Coordinate. Save Lives.**

RoutePulse AI is a safety-first emergency-corridor coordination platform built for the **iQOO Hackathon — Chennai Battle**. It addresses a simple but consequential problem: an ambulance loses time when traffic signals, pedestrians, and destination hospitals act independently rather than as one verified system.

This repository contains the working computer-vision and intersection-control prototype. It detects traffic and ambulances from lane feeds, publishes a live dashboard, and applies deterministic lane-priority logic. The larger RoutePulse vision extends this into a verified, multi-intersection corridor from emergency activation to hospital handoff.

## The problem

Emergency response is fragmented:

- A signal can react at one intersection without coordinating the route ahead.
- A blanket “green everything” response can create pedestrian and gridlock risk.
- A single mistaken vehicle classification must not be able to trigger a corridor.

RoutePulse AI replaces isolated pre-emption with a coordinated, verified, and safety-gated response.

## Product vision: one verified corridor

```text
Emergency → Verification → Routing → Signals → Hospital handoff → Recovery
```

1. **Emergency:** receive camera, siren, GPS, or dispatch evidence.
2. **Verification:** confirm the request through trusted signals before any plan is created.
3. **Routing:** balance ambulance ETA with cross-traffic impact.
4. **Signals:** reserve a staged corridor rather than issuing a blanket green.
5. **Handoff:** select a hospital using capability and capacity information.
6. **Recovery:** close the corridor and restore normal coordination.

## Safety principles

- **AI observes; a deterministic safety engine decides what is allowed.**
- **Human operators retain override.**
- **Emergency identity must be verified before priority is granted.**
- **Pedestrian and conflict-zone checks must gate signal changes.**
- **Every action should be auditable and safely abortable.**

## What this prototype implements

- Live MJPEG streams for four simulated traffic lanes
- YOLOv8 vehicle counting (`car`, `motorcycle`, `bus`, and `truck`)
- Ambulance-specific detection; ordinary buses never trigger emergency priority
- Automatic lane selection based on observed traffic volume
- Ambulance lane pre-emption with a short hold period for missed frames
- React dashboard with lane state, vehicle counts, alerts, and charts
- REST APIs for status monitoring and manual signal-control testing

## Current prototype architecture

```text
Lane video → vehicle + ambulance models → deterministic lane policy → Flask API → React dashboard
```

The backend is the source of truth for signal decisions. In normal operation, it opens the busiest lane. When the ambulance model confirms an allowed emergency label, that lane receives priority for 30 seconds after the last detection. The frontend displays controller state; it does not decide signals.

## Roadmap

The presentation describes capabilities beyond this repository’s current prototype: multi-modal verification (siren, GPS, and dispatch), multi-intersection corridor reservation, pedestrian safety gates, routing, hospital readiness scoring, formal operator workflows, and citywide coordination. These are planned product directions, not claimed as implemented by the current codebase.

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
- This is a hackathon prototype for simulation and demonstration—not a production traffic-control system. Live deployment requires certified signal interfaces, privacy and security controls, safety validation, and operator procedures.

## Illustrative impact

The hackathon presentation models a corridor-delay reduction from **160 seconds to 58 seconds**—**102 seconds avoided**—while safely handling one pedestrian conflict and recording no unsafe transitions. These are illustrative simulation results from the pitch, not a benchmark reproduced by this repository.

## Team

**Team S2V**

- Sudarsana M
- Subhikshath S K
- Vignesh S
