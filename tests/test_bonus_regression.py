"""Additional automated coverage for PDF bonus features and timezone support."""
import pytest

from test_api import event_payload


def _add(client, title, event_date):
    response = client.post("/events", json=event_payload(title=title, event_date=event_date))
    assert response.status_code == 201, response.text
    return response.json()


def test_pagination_first_second_and_empty_pages(client):
    for title in ("A", "B", "C", "D", "E"):
        _add(client, title, "2026-11-20T10:00:00")
    first = client.get("/events?skip=0&limit=2")
    second = client.get("/events?skip=2&limit=2")
    third = client.get("/events?skip=4&limit=2")
    empty = client.get("/events?skip=5&limit=2")
    assert [r.status_code for r in (first,second,third,empty)] == [200]*4
    assert [[e["title"] for e in r.json()] for r in (first,second,third,empty)] == [["A","B"],["C","D"],["E"],[]]


def test_title_filter_case_insensitive(client):
    _add(client,"Python Workshop","2026-11-20T10:00:00")
    _add(client,"JAVA Conference","2026-11-20T10:00:00")
    _add(client,"Python Training","2026-11-21T10:00:00")
    response=client.get("/events?title=python")
    assert response.status_code==200
    assert [e["title"] for e in response.json()]==["Python Workshop","Python Training"]


def test_date_filter_returns_exact_calendar_day(client):
    _add(client,"Morning","2026-11-20T00:00:00")
    _add(client,"Evening","2026-11-20T23:59:59")
    _add(client,"Next day","2026-11-21T00:00:00")
    response=client.get("/events?date=2026-11-20")
    assert response.status_code==200
    assert [e["title"] for e in response.json()]==["Morning","Evening"]


def test_combined_title_date_and_limit(client):
    _add(client,"Python A","2026-11-20T10:00:00")
    _add(client,"Python B","2026-11-20T12:00:00")
    _add(client,"Python C","2026-11-21T10:00:00")
    _add(client,"Java D","2026-11-20T10:00:00")
    response=client.get("/events?title=Python&date=2026-11-20&skip=1&limit=1")
    assert response.status_code==200
    assert [e["title"] for e in response.json()]==["Python B"]


@pytest.mark.parametrize("query",["skip=-1","limit=0","limit=101","date=not-a-date"])
def test_invalid_pagination_or_date_returns_422(client,query):
    assert client.get("/events?"+query).status_code==422


def test_utc_z_input_saved_as_naive_utc(client):
    event=_add(client,"UTC timestamp","2026-11-20T10:00:00Z")
    assert event["event_date"].startswith("2026-11-20T10:00:00")
    assert event["event_date"].endswith("00:00")
    assert not event["event_date"].endswith("Z")


def test_timezone_offset_is_normalized_to_utc(client):
    event=_add(client,"PKT timestamp","2026-11-20T15:00:00+05:00")
    assert event["event_date"]=="2026-11-20T10:00:00"


def test_timezone_normalization_on_update(client):
    event=_add(client,"Before","2026-11-20T10:00:00")
    response=client.put(f"/events/{event['id']}",json=event_payload(title="After",event_date="2026-11-21T15:00:00+05:00"))
    assert response.status_code==200,response.text
    assert response.json()["event_date"]=="2026-11-21T10:00:00"
