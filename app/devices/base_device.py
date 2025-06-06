from datetime import datetime
from typing import Dict, List, Optional
from app.core.a2a_protocol import A2AProtocol, DeviceInfo, A2AMessage

class BaseMedicalDevice:
    def __init__(self, device_type: str, capabilities: List[str], metadata: Dict[str, str]):
        self.device_id = f"{device_type}_{datetime.utcnow().timestamp()}"
        self.device_type = device_type
        self.capabilities = capabilities
        self.metadata = metadata
        self.status = "initializing"
        self.a2a_protocol = A2AProtocol()
        self._register_device()

    def _register_device(self):
        """Register the device with the A2A protocol."""
        device_info = DeviceInfo(
            device_id=self.device_id,
            device_type=self.device_type,
            status=self.status,
            last_heartbeat=datetime.utcnow(),
            capabilities=self.capabilities,
            metadata=self.metadata
        )
        self.a2a_protocol.register_device(device_info)

    def send_alert(self, alert_type: str, message: str, priority: int = 0):
        """Send an alert to all devices in the network."""
        alert_message = A2AMessage(
            message_id="",  # Will be set by the protocol
            sender_id=self.device_id,
            receiver_id=None,  # Broadcast to all devices
            message_type="alert",
            timestamp=datetime.utcnow(),
            payload={
                "alert_type": alert_type,
                "message": message,
                "device_id": self.device_id,
                "device_type": self.device_type
            },
            priority=priority
        )
        self.a2a_protocol.send_message(alert_message)

    def send_data(self, data: Dict, receiver_id: Optional[str] = None):
        """Send data to a specific device or broadcast to all devices."""
        data_message = A2AMessage(
            message_id="",  # Will be set by the protocol
            sender_id=self.device_id,
            receiver_id=receiver_id,
            message_type="data",
            timestamp=datetime.utcnow(),
            payload=data,
            priority=0
        )
        self.a2a_protocol.send_message(data_message)

    def receive_messages(self) -> List[A2AMessage]:
        """Receive messages for this device."""
        return self.a2a_protocol.receive_messages(self.device_id)

    def discover_devices(self, device_type: Optional[str] = None) -> List[DeviceInfo]:
        """Discover other devices in the network."""
        return self.a2a_protocol.discover_devices(device_type)

    def update_status(self, status: str):
        """Update the device status."""
        self.status = status
        self.a2a_protocol.update_device_status(self.device_id, status)

    def cleanup(self):
        """Clean up resources and unregister the device."""
        self.a2a_protocol.unregister_device(self.device_id) 