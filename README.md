# A2A-Healthcare

#Problem Statement:
Hospitals have many medical devices, but they don’t talk to each other, making it hard to monitor patients in real time and respond quickly to emergencies.

How A2A Protocol Solves It:
The A2A protocol lets all devices (agents) register, discover each other, and communicate instantly using a standard format. This enables real-time data sharing and alerts across all devices.


Agents Used:
Patient Monitor Agent: Sends patient vitals and alerts if something is wrong.
Dashboard Agent: Shows all devices and alerts in real time on a central dashboard.
Project Folder Structure:
app/core/a2a_protocol.py: The protocol logic (register, discover, message passing)
app/devices/patient_monitor.py: The patient monitor agent
app/main.py: The FastAPI backend and dashboard logic
app/templates/dashboard.html: The web dashboard UI
In short:
With A2A, all devices work together, and staff get instant alerts and a live overview—making patient care safer and faster.
