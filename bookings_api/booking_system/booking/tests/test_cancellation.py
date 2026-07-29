
from datetime import timedelta

import pytest
from django.utils import timezone as dj_timezone

from booking.constants import BOOKING_STATUS_CANCELLED, BOOKING_STATUS_CONFIRMED
from booking.models import Booking
from core.time_helpers import iso, utc

pytestmark = pytest.mark.django_db


def make_booking(room, start, end, status=BOOKING_STATUS_CONFIRMED):
    return Booking.objects.create(
        room=room,
        title="Meeting",
        organizer_email="rajesh@gmail.com",
        start_time=start,
        end_time=end,
        status=status,
    )


def test_cancel_more_than_one_hour_before_succeeds(api, room):
    now = dj_timezone.now()
    booking = make_booking(room, now + timedelta(hours=2), now + timedelta(hours=3))

    resp = api.post(f"/bookings/{booking.id}/cancel")
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"
    assert resp.json()["cancelledAt"] is not None


def test_cancel_inside_cutoff_returns_400(api, room):
    now = dj_timezone.now()
    booking = make_booking(room, now + timedelta(minutes=30), now + timedelta(minutes=90))

    resp = api.post(f"/bookings/{booking.id}/cancel")
    assert resp.status_code == 400
    assert "1 hour" in resp.json()["message"]

    booking.refresh_from_db()
    assert booking.status == BOOKING_STATUS_CONFIRMED


def test_cancel_already_cancelled_is_noop(api, room):
    now = dj_timezone.now()
    booking = make_booking(
        room, now + timedelta(hours=2), now + timedelta(hours=3),
        status=BOOKING_STATUS_CANCELLED,
    )
    resp = api.post(f"/bookings/{booking.id}/cancel")
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"
    assert resp.json()["id"] == booking.id


def test_cancel_unknown_booking_returns_404(api, room):
    resp = api.post("/bookings/655757/cancel")
    assert resp.status_code == 404


def test_cancelled_booking_does_not_block_new_booking(api, room):
    make_booking(
        room, utc(2026, 7, 20, 10), utc(2026, 7, 20, 12),
        status=BOOKING_STATUS_CANCELLED,
    )
    resp = api.post(
        "/bookings",
        {
            "roomId": room.id,
            "title": "New meeting",
            "organizerEmail": "ramesh@gmail.com",
            "startTime": iso(utc(2026, 7, 20, 10, 30)),
            "endTime": iso(utc(2026, 7, 20, 11, 30)),
        },
        format="json",
    )
    assert resp.status_code == 201
