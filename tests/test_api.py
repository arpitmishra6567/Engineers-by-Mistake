"""Integration tests for the Forge Command FastAPI backend."""

import pytest
from fastapi.testclient import TestClient
from web_api.main import app

client = TestClient(app)


def test_api_health():
    """Verify health endpoint returns ok and correct version."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app_name"] == "Forge Command"
    assert data["project"] == "RepairForge AI"


def test_dashboard_summary():
    """Verify dashboard summary metrics are derived from real reports."""
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_repairs" in data
    assert "verified_repairs" in data
    assert "recent_repairs" in data
    assert "recent_reports" in data
    assert data["configured_provider"] == "mock"
    assert data["execution_mode"] == "SAFE_FIXTURE"


def test_evaluations_list_and_detail():
    """Verify evaluation records include Kaggle benchmark data."""
    response = client.get("/api/evaluations")
    assert response.status_code == 200
    evals = response.json()
    assert len(evals) >= 1

    # Check for primary Kaggle experiment
    kaggle_item = next((e for e in evals if "kaggle" in e["id"]), None)
    assert kaggle_item is not None
    assert kaggle_item["model"] == "Qwen/Qwen2.5-Coder-1.5B-Instruct"
    assert kaggle_item["inference_time_seconds"] == 7.281
    assert kaggle_item["baseline_tests_passed"] == 2
    assert kaggle_item["patched_tests_passed"] == 3
    assert kaggle_item["repair_status"] == "VERIFIED"

    # Detail endpoint
    detail_res = client.get(f"/api/evaluations/{kaggle_item['id']}")
    assert detail_res.status_code == 200
    assert detail_res.json()["id"] == kaggle_item["id"]


def test_repository_inspection_and_security():
    """Verify repository inspection and path traversal prevention."""
    # Permitted path
    resp = client.get("/api/repositories/inspect?path=.")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_files"] > 0
    assert "Python" in data["languages"]

    # Traversal outside workspace should be rejected with 403 Forbidden
    resp_bad = client.get("/api/repositories/inspect?path=../../")
    assert resp_bad.status_code == 403
    assert "Access denied" in resp_bad.json()["detail"]


def test_models_endpoint_security():
    """Verify models endpoint returns provider list without leaking secrets."""
    resp = client.get("/api/models")
    assert resp.status_code == 200
    models = resp.json()
    assert len(models) >= 2
    mock_model = next(m for m in models if m["id"] == "mock")
    assert mock_model["is_deterministic"] is True
    # Ensure no API key field exists
    for m in models:
        assert "api_key" not in m


def test_skill_endpoint_and_validation():
    """Verify skills inspection and live validation."""
    resp = client.get("/api/skills")
    assert resp.status_code == 200
    skill = resp.json()
    assert skill["name"] == "bugrepro"
    assert skill["valid"] is True
    assert len(skill["phases"]) == 7

    # Validate endpoint
    val_resp = client.post("/api/skills/validate")
    assert val_resp.status_code == 200
    assert val_resp.json()["valid"] is True


def test_repairs_workflow_api():
    """Verify creating a repair task via API executes through the orchestrator."""
    payload = {
        "repo_path": "examples/buggy_average",
        "title": "API Test Repair",
        "description": "ZeroDivisionError test",
        "expected_behavior": "Raise ValueError",
        "actual_behavior": "Raises ZeroDivisionError",
        "test_command": "python -m pytest test_average.py",
        "provider_type": "mock",
        "isolate_workspace": True,
        "auto_approve": True,
    }
    resp = client.post("/api/repairs", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    task_id = data["task_id"]
    assert task_id.startswith("rf-")

    # Get task detail
    get_res = client.get(f"/api/repairs/{task_id}")
    assert get_res.status_code == 200
    assert get_res.json()["task_id"] == task_id

    # Get logs
    log_res = client.get(f"/api/repairs/{task_id}/logs")
    assert log_res.status_code == 200
    assert "logs" in log_res.json()


def test_platform_health_alias():
    """Verify /health alias works at root level for Railway health checks."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_vercel_cors_origin_allowed():
    """Verify Vercel preview/production domains pass CORS preflight."""
    headers = {
        "Origin": "https://repairforge-frontend.vercel.app",
        "Access-Control-Request-Method": "GET",
    }
    response = client.options("/api/health", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "https://repairforge-frontend.vercel.app"


