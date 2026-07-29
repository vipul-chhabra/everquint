
import pytest

from booking.constants import IDEMPOTENCY_IN_PROGRESS
from booking.exceptions import IdempotencyInProgressException
from booking.models import Booking, IdempotencyKey
from booking.services.booking_service import BookingService
from core.time_helpers import iso, utc

pytestmark = pytest.mark.django_db


def payload(room, organizer="rajesh@gmail.com"):
    return {
        "roomId": room.id,
        "title": "Standup",
        "organizerEmail": organizer,
        "startTime": iso(utc(2026, 7, 20, 10)),
        "endTime": iso(utc(2026, 7, 20, 11)),
    }


def test_same_key_returns_same_booking_no_duplicate(api, room):
    first = api.post("/bookings", payload(room), format="json", HTTP_IDEMPOTENCY_KEY="key-1")
    assert first.status_code == 201
    booking_id = first.json()["id"]
    second = api.post("/bookings", payload(room), format="json", HTTP_IDEMPOTENCY_KEY="key-1")
    assert second.status_code == 200
    assert second.json()["id"] == booking_id
    assert Booking.objects.count() == 1


def test_without_key_second_identical_request_conflicts(api, room):
    first = api.post("/bookings", payload(room), format="json")
    assert first.status_code == 201
    second = api.post("/bookings", payload(room), format="json")
    assert second.status_code == 409


def test_same_key_different_organizer_is_independent(api, room):
    a = api.post(
        "/bookings",
        payload(room, organizer="rajesh@gmail.com"),
        format="json",
        HTTP_IDEMPOTENCY_KEY="shared-key",
    )
    bpayload = payload(room, organizer="ramesh@gmail.com")
    bpayload["startTime"] = iso(utc(2026, 7, 20, 12))
    bpayload["endTime"] = iso(utc(2026, 7, 20, 13))
    b = api.post("/bookings", bpayload, format="json", HTTP_IDEMPOTENCY_KEY="shared-key")

    assert a.status_code == 201
    assert b.status_code == 201
    assert a.json()["id"] != b.json()["id"]
    assert Booking.objects.count() == 2


def test_in_progress_key_returns_409(room):
    IdempotencyKey.objects.create(
        key="pending", organizer_email="rajesh@gmail.com", status=IDEMPOTENCY_IN_PROGRESS
    )
    with pytest.raises(IdempotencyInProgressException):
        BookingService.create_booking(
            room_id=room.id,
            title="Standup",
            organizer_email="rajesh@gmail.com",
            start_time=utc(2026, 7, 20, 10),
            end_time=utc(2026, 7, 20, 11),
            idempotency_key="pending",
        )
    assert Booking.objects.count() == 0
