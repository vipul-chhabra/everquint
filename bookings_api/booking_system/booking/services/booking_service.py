from datetime import timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone

from booking.utils import validate_business_hours,validate_duration,validate_time_order
from booking.constants import BOOKING_STATUS_CANCELLED, BOOKING_STATUS_CONFIRMED, IDEMPOTENCY_COMPLETED,IDEMPOTENCY_IN_PROGRESS
from booking.constants import CANCELLATION_CUTOFF_HOURS, DEFAULT_PAGE_LIMIT
from booking.exceptions import BookingNotFoundException, BookingOverlapException, CancellationWindowClosedException, IdempotencyInProgressException
from room.exceptions import RoomNotFoundException
from booking.models import Booking, IdempotencyKey, Room



class BookingService(object):
    """Business operations for creating, cancelling and listing of bookings."""

    @staticmethod
    def create_booking(room_id, title, organizer_email, start_time, end_time, idempotency_key=None):
        """
        Validate and create a confirmed booking.
        """
        room = BookingService.get_room(room_id)
        validate_time_order(start_time, end_time)
        validate_duration(start_time, end_time)
        validate_business_hours(start_time, end_time, room.timezone)
        if not idempotency_key:
            booking = BookingService.create_confirmed_booking(
                room, title, organizer_email, start_time, end_time
            )
            return booking, False
        return BookingService.create_with_idempotency(
            room, title, organizer_email, start_time, end_time, idempotency_key
        )

    @staticmethod
    def get_room(room_id):
        try:
            pk = int(room_id)
        except (TypeError, ValueError):
            raise RoomNotFoundException("Room '{0}' not found.".format(room_id))
        room = Room.objects.filter(pk=pk).first()
        if room is None:
            raise RoomNotFoundException("Room '{0}' not found.".format(room_id))
        return room

    @staticmethod
    def has_overlap(room, start_time, end_time):
        """
        Check if any confirmed booking on this room overlaps
        """
        return Booking.objects.filter(
            room=room,
            status=BOOKING_STATUS_CONFIRMED,
            start_time__lt=end_time,
            end_time__gt=start_time,
        ).exists()

    @staticmethod
    def create_confirmed_booking(room, title, organizer_email, start_time, end_time):
        """
        Create a confirmed booking, also guarding against overlaps .
        """
        with transaction.atomic():
            Room.objects.select_for_update().get(pk=room.pk)

            if BookingService.has_overlap(room, start_time, end_time):
                raise BookingOverlapException()

            return Booking.objects.create(
                room=room,
                title=title,
                organizer_email=organizer_email,
                start_time=start_time,
                end_time=end_time,
                status=BOOKING_STATUS_CONFIRMED,
            )

    @staticmethod
    def create_with_idempotency(room, title, organizer_email, start_time, end_time, idempotency_key):
        """
        Create a booking idempotently, with key and organizer_email.
        """
        try:
            with transaction.atomic():
                record = IdempotencyKey.objects.create(
                    key=idempotency_key,
                    organizer_email=organizer_email,
                    status=IDEMPOTENCY_IN_PROGRESS,
                )
                booking = BookingService.create_confirmed_booking(
                    room, title, organizer_email, start_time, end_time
                )
                record.booking = booking
                record.status = IDEMPOTENCY_COMPLETED
                record.save(update_fields=['booking', 'status'])
                return booking, False
        except IntegrityError:
            record = IdempotencyKey.objects.filter(
                key=idempotency_key, organizer_email=organizer_email
            ).first()
            if record and record.status == IDEMPOTENCY_COMPLETED and record.booking_id:
                return record.booking, True
            raise IdempotencyInProgressException()

    @staticmethod
    def cancel_booking(booking_id):
        """
        Cancel a booking up to cancellation hour before its start time.
        """
        with transaction.atomic():
            booking = Booking.objects.select_for_update().filter(pk=booking_id).first()
            if booking is None:
                raise BookingNotFoundException("Booking '{0}' not found.".format(booking_id))

            if booking.status == BOOKING_STATUS_CANCELLED:
                return booking

            cutoff = booking.start_time - timedelta(hours=CANCELLATION_CUTOFF_HOURS)
            if timezone.now() > cutoff:
                raise CancellationWindowClosedException()

            booking.status = BOOKING_STATUS_CANCELLED
            booking.cancelled_at = timezone.now()
            booking.save(update_fields=['status', 'cancelled_at'])
            return booking

    @staticmethod
    def list_bookings(room_id=None, time_from=None, time_to=None, limit=DEFAULT_PAGE_LIMIT, offset=0):
        """
        list room bookings
        """
        booking_data = Booking.objects.all().order_by('start_time', 'id')

        if room_id is not None:
            booking_data = booking_data.filter(room_id=room_id)
        if time_from is not None:
            booking_data = booking_data.filter(end_time__gt=time_from)
        if time_to is not None:
            booking_data = booking_data.filter(start_time__lt=time_to)

        total = booking_data.count()
        items = list(booking_data[offset:offset + limit])
        return items, total
