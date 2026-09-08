# Ambulance traffic priority

The standard `yolov8n.pt` model is used only to count vehicles. It does not
contain an ambulance class (`bus` is COCO class 5), so it cannot safely drive
emergency pre-emption.

To enable ambulance detection, add a YOLO model trained with an `ambulance`
label at `Backend/models/ambulance.pt`, then start the backend. Alternatively,
set `EMERGENCY_MODEL_PATH` to the weights file. If its label is named
differently, set `EMERGENCY_CLASS_NAMES` to the comma-separated label name(s).

This project includes an ambulance-capable model at that path. Its default
confidence threshold is `0.45`, calibrated against the bundled compressed lane
videos; override it with `EMERGENCY_CONFIDENCE` when using a different camera.

The controller opens only the lane where the emergency model detects an
ambulance, then holds priority briefly through missed frames. Ordinary buses
will not turn a signal green.

## Run the backend

From the project root in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
cd .\Backend
python .\app.py
```

The first launch may pause while PyTorch loads. Do not press `Ctrl+C`; a
successful launch ends with `Running on http://127.0.0.1:5000`.
