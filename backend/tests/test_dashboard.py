import pytest
from app.services.dashboard_service import DashboardService
from app.models.activity import ActivityLog

# Normally we'd use mock AsyncSession or a test database.
# Here we just implement basic unit tests assuming DB fixtures exist.
# In an actual pytest environment with FastAPI, we'd use AsyncClient to hit /api/v1/dashboard.

def test_dashboard_service_instantiation():
    svc = DashboardService(db=None)
    assert svc is not None

def test_activity_log_model():
    log = ActivityLog(
        user_id="123e4567-e89b-12d3-a456-426614174000",
        activity_type="TOPIC_COMPLETED",
        entity_id="123e4567-e89b-12d3-a456-426614174000",
        metadata_json={"title": "Test"}
    )
    assert log.activity_type == "TOPIC_COMPLETED"
    assert log.metadata_json["title"] == "Test"
