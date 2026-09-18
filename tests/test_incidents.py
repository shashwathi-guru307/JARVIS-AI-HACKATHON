from datetime import datetime, timezone

import pytest

from backend.models.telemetry_models import TelemetryData
from backend.services import incident_service
from backend.services.demo_controller import set_scenario
from backend.services.predictive_service import run_prediction
from backend.services.telemetry_storage import save_telemetry


def setup_function():
    incident_service._incidents.clear()
    set_scenario("AI01_MACHINE_INCIDENT")


def test_complete_resolution_requires_approval_and_resolves():
    incident = incident_service.run_resolution()
    assert incident.status == "AWAITING_APPROVAL"
    with pytest.raises(PermissionError):
        incident_service.execute_incident(incident, "operator")

    incident_service.approve_incident(incident, "operator")
    incident_service.execute_incident(incident, "operator")
    resolved = incident_service.verify_incident(incident)
    assert resolved.status == "RESOLVED"
    assert len(resolved.source_event_ids) >= 2
    assert len(resolved.audit_event_ids) >= 8


def test_rejected_remediation_cannot_execute():
    incident = incident_service.run_resolution()
    incident_service.reject_incident(incident, "operator")
    assert incident.status == "REJECTED"
    with pytest.raises(PermissionError):
        incident_service.execute_incident(incident, "operator")


def test_detection_uses_real_telemetry_correlation():
    set_scenario("NORMAL")
    save_telemetry(TelemetryData(
        device_id="MACHINE_01", timestamp=datetime.now(timezone.utc),
        temperature=94, humidity=52, pressure=1010, vibration=.85, rpm=2300, battery=71,
    ))
    run_prediction()
    incident = incident_service.create_incident()
    assert "elevated temperature" in incident.correlated_conditions
    assert "elevated vibration" in incident.correlated_conditions