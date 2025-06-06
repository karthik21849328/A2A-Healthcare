from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

class DeviceInfo(BaseModel):
    device_id: str
    device_type: str
    status: str
    last_heartbeat: datetime
    capabilities: List[str]
    metadata: Dict[str, str]

class A2AMessage(BaseModel):
    message_id: str
    sender_id: str
    receiver_id: Optional[str]
    message_type: str
    timestamp: datetime
    payload: Dict
    priority: int = 0

class A2AProtocol:
    def __init__(self):
        self.registered_devices: Dict[str, DeviceInfo] = {}
        self.message_queue: List[A2AMessage] = []

    def register_device(self, device_info: DeviceInfo) -> bool:
        """Register a new device in the A2A network."""
        if device_info.device_id in self.registered_devices:
            return False
        self.registered_devices[device_info.device_id] = device_info
        return True

    def unregister_device(self, device_id: str) -> bool:
        """Unregister a device from the A2A network."""
        if device_id not in self.registered_devices:
            return False
        del self.registered_devices[device_id]
        return True

    def discover_devices(self, device_type: Optional[str] = None) -> List[DeviceInfo]:
        """Discover devices in the network, optionally filtered by type."""
        if device_type:
            return [device for device in self.registered_devices.values() 
                   if device.device_type == device_type]
        return list(self.registered_devices.values())

    def send_message(self, message: A2AMessage) -> bool:
        """Send a message through the A2A network."""
        if message.sender_id not in self.registered_devices:
            return False
        if message.receiver_id and message.receiver_id not in self.registered_devices:
            return False
        
        message.message_id = str(uuid.uuid4())
        message.timestamp = datetime.utcnow()
        self.message_queue.append(message)
        return True

    def receive_messages(self, device_id: str) -> List[A2AMessage]:
        """Receive messages for a specific device."""
        return [msg for msg in self.message_queue 
                if msg.receiver_id == device_id or msg.receiver_id is None]

    def update_device_status(self, device_id: str, status: str) -> bool:
        """Update the status of a registered device."""
        if device_id not in self.registered_devices:
            return False
        self.registered_devices[device_id].status = status
        self.registered_devices[device_id].last_heartbeat = datetime.utcnow()
        return True 