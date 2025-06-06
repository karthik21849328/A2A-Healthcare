from typing import Dict, List
import logging
from app.devices.base_device import BaseMedicalDevice

logger = logging.getLogger(__name__)

class PatientMonitor(BaseMedicalDevice):
    def __init__(self, patient_id: str):
        capabilities = [
            "heart_rate_monitoring",
            "blood_pressure_monitoring",
            "oxygen_saturation_monitoring",
            "temperature_monitoring",
            "alert_generation"
        ]
        metadata = {
            "patient_id": patient_id,
            "manufacturer": "Healthcare A2A",
            "model": "PM-2024"
        }
        super().__init__("patient_monitor", capabilities, metadata)
        self.vitals = {
            "heart_rate": 0,
            "systolic_bp": 0,
            "diastolic_bp": 0,
            "oxygen_saturation": 0,
            "temperature": 0
        }
        self.thresholds = {
            "heart_rate": {"min": 60, "max": 100},
            "systolic_bp": {"min": 90, "max": 140},
            "diastolic_bp": {"min": 60, "max": 90},
            "oxygen_saturation": {"min": 95, "max": 100},
            "temperature": {"min": 36.1, "max": 37.2}
        }
        logger.info(f"Initialized PatientMonitor for patient {patient_id}")

    def update_vitals(self, vitals: Dict[str, float]):
        """Update patient vitals and check for abnormal values."""
        logger.info(f"Updating vitals: {vitals}")
        self.vitals.update(vitals)
        self._check_thresholds()
        self.send_data({
            "type": "vitals_update",
            "patient_id": self.metadata["patient_id"],
            "vitals": self.vitals
        })

    def _check_thresholds(self):
        """Check if any vital signs are outside normal ranges."""
        logger.info("Checking vital thresholds")
        for vital, value in self.vitals.items():
            if vital in self.thresholds:
                threshold = self.thresholds[vital]
                logger.info(f"Checking {vital}: value={value}, threshold={threshold}")
                if value < threshold["min"]:
                    logger.info(f"Generating low alert for {vital}: {value}")
                    self.send_alert(
                        "low_vital",
                        f"Low {vital}: {value} (Normal range: {threshold['min']}-{threshold['max']})",
                        priority=1
                    )
                elif value > threshold["max"]:
                    logger.info(f"Generating high alert for {vital}: {value}")
                    self.send_alert(
                        "high_vital",
                        f"High {vital}: {value} (Normal range: {threshold['min']}-{threshold['max']})",
                        priority=1
                    )

    def get_vitals(self) -> Dict[str, float]:
        """Get current vital signs."""
        return self.vitals

    def set_thresholds(self, vital: str, min_value: float, max_value: float):
        """Set custom thresholds for a vital sign."""
        if vital in self.thresholds:
            self.thresholds[vital] = {"min": min_value, "max": max_value}
            logger.info(f"Updated thresholds for {vital}: min={min_value}, max={max_value}")
            self._check_thresholds()  # Recheck with new thresholds 