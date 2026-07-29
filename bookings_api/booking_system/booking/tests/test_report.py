"""Room-utilization report: math, no-bookings, and partial-overlap edges."""
import pytest

from booking.constants import BOOKING_STATUS_CANCELLED, BOOKING_STATUS_CONFIRMED
from booking.models import Booking
from room.models import Room
from core.time_helpers import iso, qdt, utc

pytestmark = pytest.mark.django_db


def confirmed(room, start, end):
    return Booking.objects.create(
        room=room,
        title="Meeting",
        organizer_email="rajesh@gmail.com",
        start_time=start,
        end_time=end,
        status=BOOKING_STATUS_CONFIRMED,
    )


def report(api, frm, to):
    resp = api.get(f"/reports/room-utilization?from={qdt(frm)}&to={qdt(to)}")
    assert resp.status_code == 200
    return {row["roomId"]: row for row in resp.json()}


def test_requires_from_and_to(api, room):
    assert api.get("/reports/room-utilization").status_code == 400
    assert api.get(f"/reports/room-utilization?from={iso(utc(2026,7,20))}").status_code == 400


def test_no_bookings_is_zero(api, room):
    rows = report(api, utc(2026, 7, 20), utc(2026, 7, 21))
    assert rows[room.id]["totalBookingHours"] == 0.0
    assert rows[room.id]["utilizationPercent"] == 0.0


def test_simple_utilization(api, room):
    confirmed(room, utc(2026, 7, 20, 9), utc(2026, 7, 20, 12))
    rows = report(api, utc(2026, 7, 20), utc(2026, 7, 21))
    assert rows[room.id]["totalBookingHours"] == 3.0
    assert rows[room.id]["utilizationPercent"] == 0.25


def test_partial_overlap_before_from(api, room):
    confirmed(room, utc(2026, 7, 20, 9), utc(2026, 7, 20, 12))
    rows = report(api, utc(2026, 7, 20, 10), utc(2026, 7, 20, 20))
    assert rows[room.id]["totalBookingHours"] == 2.0
    assert rows[room.id]["utilizationPercent"] == 0.2


def test_partial_overlap_after_to(api, room):
    confirmed(room, utc(2026, 7, 20, 18), utc(2026, 7, 20, 20))
    rows = report(api, utc(2026, 7, 20, 8), utc(2026, 7, 20, 19))
    assert rows[room.id]["totalBookingHours"] == 1.0
    assert rows[room.id]["utilizationPercent"] == round(1.0 / 11.0, 4)


def test_cancelled_excluded_from_report(api, room):
    Booking.objects.create(
        room=room, title="X", organizer_email="a@b.com",
        start_time=utc(2026, 7, 20, 9), end_time=utc(2026, 7, 20, 12),
        status=BOOKING_STATUS_CANCELLED,
    )
    rows = report(api, utc(2026, 7, 20), utc(2026, 7, 21))
    assert rows[room.id]["totalBookingHours"] == 0.0


def test_multiple_rooms_reported_independently(api, room):
    other = Room.objects.create(name="Nimbus", capacity=5, floor=1, timezone="UTC")
    confirmed(room, utc(2026, 7, 20, 9), utc(2026, 7, 20, 12))
    rows = report(api, utc(2026, 7, 20), utc(2026, 7, 21))
    assert rows[room.id]["totalBookingHours"] == 3.0
    assert rows[other.id]["totalBookingHours"] == 0.0
