from fastapi.testclient import TestClient
from ekklesia_notify.main import app
from ekklesia_notify.models import FreeformMessage

client = TestClient(app)


def test_api_info():
    response = client.get("/")
    assert response.status_code == 200
    assert "info" in response.json()


def test_freeform_message():
    response = client.post("/freeform_message", json=FreeformMessage.Config.schema_extra['example'])
    assert response.status_code == 200
    assert "msgid" in response.json()
