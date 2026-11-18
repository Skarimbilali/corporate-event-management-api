"""Coverage of mandatory Corporate Event Management API requirements."""
import logging

import pytest


def event_payload(**overrides):
    data = {
        "title": "Python Workshop",
        "description": "Internal training",
        "event_date": "2026-11-20T11:00:00",
        "location": "Karachi",
        "capacity": 2,
    }
    data.update(overrides)
    return data


def registration_payload(email="employee@example.com", name="Employee"):
    return {"employee_name": name, "employee_email": email}


def create_event(client, **overrides):
    response = client.post("/events", json=event_payload(**overrides))
    assert response.status_code == 201, response.text
    return response.json()


def test_home_and_documentation(client):
    assert client.get("/").status_code == 200
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_create_event_returns_201_and_fields(client):
    response = client.post("/events", json=event_payload())
    assert response.status_code == 201
    assert response.json()["id"] > 0
    assert response.json()["title"] == "Python Workshop"


def test_list_events_and_get_by_id(client):
    assert client.get("/events").json() == []
    event = create_event(client)
    assert len(client.get("/events").json()) == 1
    assert client.get(f"/events/{event['id']}").json()["id"] == event["id"]


def test_update_event(client):
    event = create_event(client)
    response = client.put(f"/events/{event['id']}", json=event_payload(title="Updated"))
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"


def test_delete_event_and_missing_afterwards(client):
    event = create_event(client)
    response = client.delete(f"/events/{event['id']}")
    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/events/{event['id']}").status_code == 404


@pytest.mark.parametrize("method,path", [
    ("get", "/events/99999"),
    ("delete", "/events/99999"),
    ("get", "/events/99999/registrations"),
    ("delete", "/registrations/99999"),
])
def test_missing_resources_return_404(client, method, path):
    assert getattr(client, method)(path).status_code == 404


def test_update_missing_event_returns_404(client):
    assert client.put("/events/99999", json=event_payload()).status_code == 404


@pytest.mark.parametrize("override", [
    {"title": ""},
    {"capacity": 0},
    {"capacity": -1},
    {"event_date": "not-a-date"},
    {"location": None},
])
def test_invalid_event_returns_422(client, override):
    assert client.post("/events", json=event_payload(**override)).status_code == 422


def test_missing_required_fields_returns_422(client):
    assert client.post("/events", json={"title": "Incomplete"}).status_code == 422


def test_registration_create_and_list(client):
    event = create_event(client)
    path = f"/events/{event['id']}/registrations"
    response = client.post(path, json=registration_payload())
    assert response.status_code == 201
    assert response.json()["event_id"] == event["id"]
    assert len(client.get(path).json()) == 1


def test_registration_for_missing_event_returns_404(client):
    response = client.post("/events/99999/registrations", json=registration_payload())
    assert response.status_code == 404


def test_duplicate_registration_returns_409(client):
    event = create_event(client)
    path = f"/events/{event['id']}/registrations"
    assert client.post(path, json=registration_payload()).status_code == 201
    assert client.post(path, json=registration_payload()).status_code == 409


def test_capacity_limit_returns_409(client):
    event = create_event(client, capacity=1)
    path = f"/events/{event['id']}/registrations"
    assert client.post(path, json=registration_payload()).status_code == 201
    assert client.post(path, json=registration_payload("other@example.com")).status_code == 409


@pytest.mark.parametrize("payload", [
    {"employee_name": "", "employee_email": "a@example.com"},
    {"employee_name": "Employee", "employee_email": "invalid-email"},
    {"employee_name": "Employee"},
])
def test_invalid_registrations_return_422(client, payload):
    event = create_event(client)
    assert client.post(f"/events/{event['id']}/registrations", json=payload).status_code == 422


def test_delete_registration_and_register_again(client):
    event = create_event(client, capacity=1)
    path = f"/events/{event['id']}/registrations"
    registration = client.post(path, json=registration_payload()).json()
    assert client.delete(f"/registrations/{registration['id']}").status_code == 204
    assert client.get(path).json() == []
    assert client.post(path, json=registration_payload()).status_code == 201


def test_delete_event_with_registrations(client):
    event = create_event(client)
    path = f"/events/{event['id']}/registrations"
    registration = client.post(path, json=registration_payload()).json()

    # Active registrations must be cancelled before an event can be deleted.
    response = client.delete(f"/events/{event['id']}")
    assert response.status_code == 409
    assert response.json() == {
        "detail": "Cannot delete event because it has active registrations"
    }
    assert client.get(f"/events/{event['id']}").status_code == 200
    assert len(client.get(path).json()) == 1

    assert client.delete(f"/registrations/{registration['id']}").status_code == 204
    assert client.delete(f"/events/{event['id']}").status_code == 204
    assert client.get(f"/events/{event['id']}").status_code == 404


def test_http_logging_for_success(client):
    records = []

    class RecordHandler(logging.Handler):
        def emit(self, record):
            records.append(record.getMessage())

    logger = logging.getLogger("app.main")
    handler = RecordHandler()
    logger.addHandler(handler)
    try:
        response = client.get("/events")
    finally:
        logger.removeHandler(handler)
    assert response.status_code == 200
    assert any("method=GET path=/events status=200" in m for m in records)


def test_whitespace_only_title_should_be_rejected(client):
    """Assignment expects nonempty titles; flags current validation gap."""
    response = client.post("/events", json=event_payload(title="   "))
    assert response.status_code == 422


def test_whitespace_only_employee_name_rejected(client):
    event = create_event(client)
    response = client.post(
        f"/events/{event['id']}/registrations",
        json=registration_payload(name="   "),
    )
    assert response.status_code == 422


def test_whitespace_only_update_title_rejected(client):
    event = create_event(client)
    response = client.put(
        f"/events/{event['id']}", json=event_payload(title="  ")
    )
    assert response.status_code == 422


def test_db_check_executes_query(client):
    response = client.get("/db-check")
    assert response.status_code == 200
    assert response.json()["message"] == "Database session received successfully"
