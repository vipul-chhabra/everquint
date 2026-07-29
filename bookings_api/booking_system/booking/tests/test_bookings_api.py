
import pytest

from core.time_helpers import iso, qdt, utc

pytestmark = pytest.mark.django_db


def booking_payload(room, start, end, **overrides):
    payload = {
        "roomId": room.id,
        "title": "Meeting",
        "organizerEmail": "rajesh@gmail.com",
        "startTime": iso(start),
        "endTime": iso(end),
    }
    payload.update(overrides)
    return payload


def test_create_booking_happy_path(api, room):
    resp = api.post(
        "/bookings",
        booking_payload(room, utc(2026, 7, 20, 10), utc(2026, 7, 20, 11)),
        format="json",
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "confirmed"
    assert body["roomId"] == room.id
    assert body["id"] > 0


def test_roomid_accepts_string(api, room):
    resp = api.post(
        "/bookings",
        booking_payload(room, utc(2026, 7, 20, 10), utc(2026, 7, 20, 11), roomId=str(room.id)),
        format="json",
    )
    assert resp.status_code == 201


def test_unknown_room_returns_404(api, room):
    resp = api.post(
        "/bookings",
        booking_payload(room, utc(2026, 7, 20, 10), utc(2026, 7, 20, 11), roomId=999999),
        format="json",
    )
    assert resp.status_code == 404
    assert resp.json()["error"] == "NotFound"


def test_overlapping_booking_returns_409(api, room):
    first = api.post(
        "/bookings",
        booking_payload(room, utc(2026, 7, 20, 10), utc(2026, 7, 20, 12)),
        format="json",
    )
    assert first.status_code == 201

    conflict = api.post(
        "/bookings",
        booking_payload(room, utc(2026, 7, 20, 11), utc(2026, 7, 20, 13)),
        format="json",
    )
    assert conflict.status_code == 409
    assert conflict.json()["error"] == "Conflict"


def test_adjacent_bookings_allowed(api, room):
    a = api.post(
        "/bookings",
        booking_payload(room, utc(2026, 7, 20, 10), utc(2026, 7, 20, 11)),
        format="json",
    )
    b = api.post(
        "/bookings",
        booking_payload(room, utc(2026, 7, 20, 11), utc(2026, 7, 20, 12)),
        format="json",
    )
    assert a.status_code == 201 and b.status_code == 201


def test_start_after_end_returns_400(api, room):
    resp = api.post(
        "/bookings",
        booking_payload(room, utc(2026, 7, 20, 12), utc(2026, 7, 20, 11)),
        format="json",
    )
    assert resp.status_code == 400
    assert "before" in resp.json()["message"]


def test_too_short_returns_400(api, room):
    resp = api.post(
        "/bookings",
        booking_payload(room, utc(2026, 7, 20, 10), utc(2026, 7, 20, 10, 5)),
        format="json",
    )
    assert resp.status_code == 400


def test_too_long_returns_400(api, room):
    resp = api.post(
        "/bookings",
        booking_payload(room, utc(2026, 7, 20, 10), utc(2026, 7, 20, 15)),
        format="json",
    )
    assert resp.status_code == 400


def test_weekend_returns_400(api, room):
    resp = api.post(
        "/bookings",
        booking_payload(room, utc(2026, 7, 25, 10), utc(2026, 7, 25, 11)),
        format="json",
    )
    assert resp.status_code == 400


def test_outside_hours_returns_400(api, room):
    resp = api.post(
        "/bookings",
        booking_payload(room, utc(2026, 7, 20, 7), utc(2026, 7, 20, 8)),
        format="json",
    )
    assert resp.status_code == 400


def test_list_bookings_pagination_and_filters(api, room):
    for hour in (10, 12, 14, 16):
        api.post(
            "/bookings",
            booking_payload(room, utc(2026, 7, 20, hour), utc(2026, 7, 20, hour + 1)),
            format="json",
        )

    page = api.get("/bookings?limit=2&offset=0").json()
    assert page["total"] == 4
    assert page["limit"] == 2
    assert page["offset"] == 0
    assert len(page["items"]) == 2
    ranged = api.get(f"/bookings?from={qdt(utc(2026,7,20,13))}&to={qdt(utc(2026,7,20,17))}").json()
    starts = {item["startTime"] for item in ranged["items"]}
    assert ranged["total"] == 2
    assert len(starts) == 2
