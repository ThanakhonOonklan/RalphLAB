from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.auth import CurrentUser, get_current_user
from app.db.session import get_db
from app.main import app
from app.services import assessment_service


def test_paused_qsar_rejects_new_jobs_before_validation_or_dispatch(monkeypatch):
    monkeypatch.setattr(settings, "ASSESSMENT_EXECUTION_MODE", "disabled")
    create = Mock(side_effect=AssertionError("paused requests must not create jobs"))
    monkeypatch.setattr(assessment_service, "create_assessment", create)
    with TestClient(app) as client:
        assert client.get("/api/assessments/availability").json() == {"enabled": False}
        response = client.post("/api/assessments/", json={"formula": [], "region": "face"})
    assert response.status_code == 503
    assert "paused" in response.json()["detail"]
    create.assert_not_called()


def test_inline_mode_schedules_local_inference_without_redis(monkeypatch):
    fake_db = Mock()

    def override_db():
        yield fake_db

    enqueue = Mock(side_effect=AssertionError("Redis must not be used in inline mode"))
    process_inline = Mock()
    monkeypatch.setattr(settings, "ASSESSMENT_EXECUTION_MODE", "inline")
    monkeypatch.setattr(assessment_service, "enqueue_assessment", enqueue)
    monkeypatch.setattr(assessment_service, "process_assessment_inline", process_inline)
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(id="google-user-1")
    try:
        response = TestClient(app).post(
            "/api/assessments/",
            json={
                "formula": [
                    {"smiles": "CCO", "name": "Ethanol", "concentration": 10.0}
                ],
                "region": "forearm",
            },
        )
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 202
    enqueue.assert_not_called()
    process_inline.assert_called_once_with(response.json()["job_id"])
