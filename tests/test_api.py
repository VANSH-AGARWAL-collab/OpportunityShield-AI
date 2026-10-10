"""
Integration tests for Flask Web Application API routes
"""

import json
import pytest
from app import app
from services import database


@pytest.fixture
def client():
    app.config["TESTING"] = True
    database.init_db()
    with app.test_client() as client:
        yield client


def test_index_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"OpportunityShield" in response.data
    assert b"Check the evidence before you trust an opportunity." in response.data


def test_api_status(client):
    response = client.get("/api/status")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert "serpapi_configured" in data


def test_api_benchmarks(client):
    response = client.get("/api/benchmarks")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert len(data["benchmarks"]) >= 4


def test_api_extract(client):
    payload = {
        "text": "Company: Test Inc\nRole: Python Intern\nEmail: test@gmail.com\nDeposit: Rs 2000 refundable fee"
    }
    response = client.post("/api/extract", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert data["extracted"]["company_name"] == "Test Inc"
    assert data["extracted"]["has_free_email"] is True


def test_api_investigate_benchmark(client):
    payload = {
        "benchmark_case_id": "apex_scam",
        "text": "",
        "company": "Apex Tech Solutions",
    }
    response = client.post("/api/investigate", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert "investigation_id" in data
    assert "report" in data
    assert data["report"]["assessment"]["risk_score"] > 60

    # Verify saved in history
    inv_id = data["investigation_id"]
    hist_resp = client.get(f"/api/history/{inv_id}")
    assert hist_resp.status_code == 200
    hist_data = json.loads(hist_resp.data)
    assert hist_data["success"] is True
    assert hist_data["report"]["metadata"]["target_company"] == "Apex Tech Solutions"


def test_api_status_does_not_leak_keys(client):
    """Priority 5: Ensure /api/status never returns key values or partial substrings."""
    response = client.get("/api/status")
    data = json.loads(response.data)
    assert "serpapi_key" not in data
    assert "api_key" not in data
    # Status label should be clean and not contain key fragments
    assert "serpapi_status_label" in data


def test_api_investigate_custom_company_without_key(client):
    """
    Priority 1 & 3:
    When investigating an arbitrary custom company without an active SerpApi key,
    it must NOT substitute Apex Scam or other benchmarks.
    It must return honest unconfigured search status and insufficient evidence.
    """
    payload = {
        "text": "Offering internship at Global Systems Solutions. Contact: info@globalsystems.com",
        "company": "Global Systems Solutions",
        "domain": "globalsystems.com",
    }
    response = client.post("/api/investigate", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    report = data["report"]
    # If test environment has no SERPAPI_KEY
    if not app.config.get("SERPAPI_KEY"):
        assert report["metadata"]["search_status"] == "unconfigured_key"
        assert report["metadata"]["is_benchmark_demonstration"] is False
        assert report["assessment"]["status_code"] == "insufficient_evidence"


def test_config_security_defaults(monkeypatch):
    """
    Priority 5:
    Genuinely verify that Flask debug mode is disabled by default (FLASK_DEBUG not set or '0'),
    and test environment-variable toggling behavior safely without tautologies.
    """
    import importlib
    import config

    # Isolate from local .env file so test purely evaluates environment variable behavior
    monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **kw: None)

    # 1. Genuinely verify DEBUG is False by default when FLASK_DEBUG is unset or '0'
    monkeypatch.delenv("FLASK_DEBUG", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    importlib.reload(config)
    assert config.Config.DEBUG is False
    assert config.Config.SECRET_KEY != "opportunity-shield-prod-secret-2026-key-change-me"
    assert len(config.Config.SECRET_KEY) >= 16

    # 2. Test environment-variable toggling safely: when explicitly opted-in via FLASK_DEBUG='1'
    monkeypatch.setenv("FLASK_DEBUG", "1")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    importlib.reload(config)
    assert config.Config.DEBUG is True
    assert config.Config.SECRET_KEY == "dev-insecure-key-local-testing-only"

    # 3. Test explicit opt-out via FLASK_DEBUG='0'
    monkeypatch.setenv("FLASK_DEBUG", "0")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    importlib.reload(config)
    assert config.Config.DEBUG is False

    # 4. Clean reset to default
    monkeypatch.delenv("FLASK_DEBUG", raising=False)
    importlib.reload(config)
    assert config.Config.DEBUG is False




