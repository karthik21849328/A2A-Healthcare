from fastapi import FastAPI, WebSocket, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Dict
import asyncio
import json
import logging
from app.devices.patient_monitor import PatientMonitor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Healthcare A2A System")

# Templates setup
templates = Jinja2Templates(directory="app/templates")

# Store active devices
active_devices: Dict[str, PatientMonitor] = {}

# Store active dashboard connections
dashboard_connections: List[WebSocket] = []

@app.get("/")
async def dashboard(request: Request):
    """Render the dashboard page."""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.post("/devices/patient-monitor/{patient_id}")
async def create_patient_monitor(patient_id: str):
    """Create a new patient monitor device."""
    monitor = PatientMonitor(patient_id)
    active_devices[monitor.device_id] = monitor
    logger.info(f"Created new patient monitor: {monitor.device_id}")
    # Notify all dashboard connections about the new device
    await broadcast_device_update(monitor)
    return {"device_id": monitor.device_id, "status": "created"}

@app.get("/devices/{device_id}/vitals")
async def get_vitals(device_id: str):
    """Get current vitals for a patient monitor."""
    if device_id not in active_devices:
        return {"error": "Device not found"}
    return active_devices[device_id].get_vitals()

@app.post("/devices/{device_id}/vitals")
async def update_vitals(device_id: str, vitals: Dict[str, float]):
    """Update vitals for a patient monitor."""
    if device_id not in active_devices:
        return {"error": "Device not found"}
    logger.info(f"Updating vitals for device {device_id}: {vitals}")
    device = active_devices[device_id]
    device.update_vitals(vitals)
    
    # Get any alerts that were generated
    messages = device.receive_messages()
    for message in messages:
        if message.message_type == "alert":
            await broadcast_alert(message.dict())
    
    # Notify all dashboard connections about the update
    await broadcast_device_update(device)
    return {"status": "updated"}

async def broadcast_device_update(device: PatientMonitor):
    """Broadcast device updates to all dashboard connections."""
    device_data = {
        "type": "device_update",
        "device": {
            "device_id": device.device_id,
            "device_type": device.device_type,
            "status": device.status,
            "vitals": device.vitals,
            "metadata": device.metadata
        }
    }
    logger.info(f"Broadcasting device update: {device_data}")
    for connection in dashboard_connections:
        try:
            await connection.send_json(device_data)
        except Exception as e:
            logger.error(f"Error broadcasting to dashboard: {e}")
            dashboard_connections.remove(connection)

async def broadcast_alert(alert_data: Dict):
    """Broadcast alerts to all dashboard connections."""
    logger.info(f"Broadcasting alert: {alert_data}")
    for connection in dashboard_connections:
        try:
            await connection.send_json({
                "type": "alert",
                "alert_type": alert_data["payload"]["alert_type"],
                "message": alert_data["payload"]["message"],
                "device_id": alert_data["sender_id"],
                "priority": alert_data["priority"]
            })
        except Exception as e:
            logger.error(f"Error broadcasting alert: {e}")
            dashboard_connections.remove(connection)

@app.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    """WebSocket endpoint for dashboard updates."""
    await websocket.accept()
    dashboard_connections.append(websocket)
    logger.info("New dashboard connection established")
    
    try:
        # Send initial state of all devices
        for device in active_devices.values():
            await websocket.send_json({
                "type": "device_update",
                "device": {
                    "device_id": device.device_id,
                    "device_type": device.device_type,
                    "status": device.status,
                    "vitals": device.vitals,
                    "metadata": device.metadata
                }
            })
        
        # Keep connection alive and handle messages
        while True:
            await websocket.receive_text()
    except Exception as e:
        logger.error(f"Dashboard WebSocket error: {e}")
        dashboard_connections.remove(websocket)
    finally:
        await websocket.close()

@app.websocket("/ws/{device_id}")
async def device_websocket(websocket: WebSocket, device_id: str):
    """WebSocket endpoint for device communication."""
    await websocket.accept()
    
    if device_id not in active_devices:
        await websocket.close(code=1000, reason="Device not found")
        return

    device = active_devices[device_id]
    
    try:
        while True:
            # Send any new messages to the client
            messages = device.receive_messages()
            for message in messages:
                await websocket.send_json(message.dict())
                # If it's an alert, broadcast to dashboard
                if message.message_type == "alert":
                    logger.info(f"Device {device_id} generated alert: {message.dict()}")
                    await broadcast_alert(message.dict())
            
            # Wait for a short time before checking for new messages
            await asyncio.sleep(0.1)
    except Exception as e:
        logger.error(f"Device WebSocket error: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 