"""
Unit tests for the unified risk engine and correlation service.
Run: pytest tests/test_risk_engine.py -v
"""
import pytest
from unittest.mock import patch, MagicMock
from backend.services.risk_engine import (
    _level_to_score, _score_to_level, _max_level, calculate_system_risk
)


class TestHelpers:
    def test_critical_score(self):
        assert _level_to_score("CRITICAL") >= 75

    def test_low_score(self):
        assert _level_to_score("LOW") < 25

    def test_score_to_critical(self):
        assert _score_to_level(80) == "CRITICAL"

    def test_score_to_low(self):
        assert _score_to_level(10) == "LOW"

    def test_max_level_picks_highest(self):
        assert _max_level("LOW", "HIGH", "MEDIUM") == "HIGH"

    def test_max_level_critical_wins(self):
        assert _max_level("CRITICAL", "HIGH", "LOW") == "CRITICAL"


class TestCalculateSystemRisk:
    @patch("backend.services.risk_engine.get_latest_prediction", return_value=None)
    @patch("backend.services.risk_engine.get_latest_energy",     return_value=None)
    @patch("backend.services.risk_engine.get_latest_safety",     return_value=None)
    @patch("backend.services.risk_engine.get_transaction_risks", return_value=[])
    @patch("backend.services.risk_engine.get_security_status")
    def test_all_low_gives_low_or_medium_risk(
        self, mock_sec, mock_tx, mock_safety, mock_energy, mock_pred
    ):
        sec = MagicMock()
        sec.risk_level = "LOW"
        sec.active_alerts = 0
        sec.security_status = "PROTECTED"
        mock_sec.return_value = sec

        result = calculate_system_risk()
        assert result["system_risk"] in ("LOW", "MEDIUM")
        assert 0 <= result["system_score"] <= 100
        assert "recommendation" in result

    @patch("backend.services.risk_engine.get_latest_prediction")
    @patch("backend.services.risk_engine.get_latest_energy",     return_value=None)
    @patch("backend.services.risk_engine.get_latest_safety",     return_value=None)
    @patch("backend.services.risk_engine.get_transaction_risks", return_value=[])
    @patch("backend.services.risk_engine.get_security_status")
    def test_critical_machine_raises_risk(
        self, mock_sec, mock_tx, mock_safety, mock_energy, mock_pred
    ):
        pred = MagicMock()
        pred.risk_level  = "CRITICAL"
        pred.health_score = 22.0
        mock_pred.return_value = pred

        sec = MagicMock()
        sec.risk_level = "LOW"
        sec.active_alerts = 0
        sec.security_status = "PROTECTED"
        mock_sec.return_value = sec

        result = calculate_system_risk()
        assert result["system_risk"] in ("HIGH", "CRITICAL")
        assert len(result["contributing"]) > 0