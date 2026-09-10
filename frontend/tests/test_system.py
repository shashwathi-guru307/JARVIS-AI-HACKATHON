"""
Day 10 — Backend system integration tests.
Run: pytest tests/test_system.py -v
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


# ── Health ────────────────────────────────────────────────────────────────────
class TestHealth:
    def test_health_returns_200(self):
        r = client.get("/health")
        assert r.status_code == 200

    def test_health_has_required_fields(self):
        data = client.get("/health").json()
        assert data["status"] == "online"
        assert "version" in data
        assert "demo_mode" in data

    def test_system_status_returns_200(self):
        r = client.get("/system/status")
        assert r.status_code == 200

    def test_system_status_has_risk_fields(self):
        data = client.get("/system/status").json()
        assert "system_risk"  in data
        assert "system_score" in data
        assert "system_status" in data
        assert "active_alerts" in data
        assert "modules"       in data

    def test_system_health_returns_200(self):
        r = client.get("/system/health")
        assert r.status_code == 200

    def test_system_score_in_range(self):
        score = client.get("/system/status").json()["system_score"]
        assert 0.0 <= score <= 100.0


# ── Risk engine ───────────────────────────────────────────────────────────────
class TestRiskEngine:
    def test_risk_level_is_valid(self):
        data  = client.get("/system/status").json()
        valid = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        assert data["system_risk"] in valid

    def test_domain_risks_present(self):
        data = client.get("/system/status").json()
        assert "domain_risks" in data

    def test_modules_all_present(self):
        mods = client.get("/system/health").json()["modules"]
        for key in ("telemetry", "maintenance", "energy", "safety", "security", "ai"):
            assert key in mods


# ── Demo controller ───────────────────────────────────────────────────────────
class TestDemoController:
    def test_demo_status_returns_200(self):
        r = client.get("/demo/status")
        assert r.status_code == 200

    def test_demo_status_has_scenarios(self):
        data = client.get("/demo/status").json()
        if data.get("demo_mode"):
            assert "available_scenarios" in data
            assert len(data["available_scenarios"]) > 0


# ── Agent analyze ─────────────────────────────────────────────────────────────
class TestAgentAnalyze:
    def test_analyze_rejects_empty_message(self):
        r = client.post("/agent/analyze", json={"message": ""})
        # Should return a structured error, not a 500
        assert r.status_code in (200, 422)
        if r.status_code == 200:
            data = r.json()
            assert data.get("status") == "error" or data.get("http_status") == 422

    def test_analyze_valid_message_returns_fields(self):
        r = client.post("/agent/analyze", json={"message": "Temperature 65°C, vibration 0.30g. System check."})
        assert r.status_code == 200
        data = r.json()
        # Either success with full schema or a known error shape
        if data.get("status") == "success":
            for field in ("risk_level", "summary", "confidence", "narrative_answer"):
                assert field in data, f"Missing field: {field}"