"""
Unit tests for the correlation engine.
Run: pytest tests/test_correlation.py -v
"""
import pytest
from unittest.mock import patch, MagicMock
from backend.services.correlation_service import correlate_events


def _make_pred(risk="LOW", health=85.0):
    m = MagicMock()
    m.risk_level  = risk
    m.health_score = health
    return m


def _make_safety(overall="NORMAL", proximity="NORMAL"):
    m = MagicMock()
    m.overall_risk  = overall
    m.proximity_risk = proximity
    return m


def _make_sec(risk="LOW"):
    m = MagicMock()
    m.risk_level = risk
    return m


def _make_energy(efficiency=90.0):
    m = MagicMock()
    m.efficiency_score = efficiency
    return m


def _make_tel(temp=60.0, vib=0.20):
    m = MagicMock()
    m.temperature = temp
    m.vibration   = vib
    return m


@patch("backend.services.correlation_service.get_latest_prediction")
@patch("backend.services.correlation_service.get_latest_safety")
@patch("backend.services.correlation_service.get_security_status")
@patch("backend.services.correlation_service.get_latest_energy")
@patch("backend.services.correlation_service.get_transaction_risks", return_value=[])
@patch("backend.services.correlation_service.get_latest_telemetry")
class TestCorrelation:
    def test_no_correlation_when_all_normal(
        self, mock_tel, mock_tx, mock_energy, mock_sec, mock_safety, mock_pred
    ):
        mock_pred.return_value   = _make_pred("LOW")
        mock_safety.return_value = _make_safety("NORMAL", "NORMAL")
        mock_sec.return_value    = _make_sec("LOW")
        mock_energy.return_value = _make_energy(92.0)
        mock_tel.return_value    = _make_tel(60.0, 0.20)
        result = correlate_events()
        assert result == []

    def test_machine_high_and_prox_triggers_correlation(
        self, mock_tel, mock_tx, mock_energy, mock_sec, mock_safety, mock_pred
    ):
        mock_pred.return_value   = _make_pred("HIGH")
        mock_safety.return_value = _make_safety("HIGH", "HIGH")
        mock_sec.return_value    = _make_sec("LOW")
        mock_energy.return_value = _make_energy(90.0)
        mock_tel.return_value    = _make_tel(60.0, 0.20)
        result = correlate_events()
        assert any("proximity" in c.lower() for c in result)

    def test_security_and_tx_triggers_correlation(
        self, mock_tel, mock_tx, mock_energy, mock_sec, mock_safety, mock_pred
    ):
        mock_pred.return_value   = _make_pred("LOW")
        mock_safety.return_value = _make_safety("NORMAL", "NORMAL")
        mock_sec.return_value    = _make_sec("HIGH")
        mock_energy.return_value = _make_energy(90.0)
        mock_tel.return_value    = _make_tel(60.0, 0.20)
        # Inject a suspicious transaction
        tx = MagicMock()
        tx.is_suspicious = True
        mock_tx.return_value = [tx]
        result = correlate_events()
        assert any("transaction" in c.lower() or "security" in c.lower() for c in result)

    def test_multi_risk_produces_multiple_correlations(
        self, mock_tel, mock_tx, mock_energy, mock_sec, mock_safety, mock_pred
    ):
        mock_pred.return_value   = _make_pred("CRITICAL", 22.0)
        mock_safety.return_value = _make_safety("HIGH", "HIGH")
        mock_sec.return_value    = _make_sec("HIGH")
        mock_energy.return_value = _make_energy(42.0)
        mock_tel.return_value    = _make_tel(96.0, 0.90)
        tx = MagicMock(); tx.is_suspicious = True
        mock_tx.return_value = [tx]
        result = correlate_events()
        assert len(result) >= 2