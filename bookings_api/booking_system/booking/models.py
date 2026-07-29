from django.db import models
from room.models import Room
from booking.constants import BOOKING_STATUS_CHOICES, BOOKING_STATUS_CONFIRMED , IDEMPOTENCY_IN_PROGRESS , IDEMPOTENCY_STATUS_CHOICES
# Create your models here.


class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings', db_index=True)
    title = models.CharField(max_length=300)
    organizer_email = models.EmailField()
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField(db_index=True)
    status = models.PositiveSmallIntegerField(
        choices=BOOKING_STATUS_CHOICES, default=BOOKING_STATUS_CONFIRMED
    )
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)




class IdempotencyKey(models.Model):
    key = models.CharField(max_length=255)
    organizer_email = models.EmailField()
    status = models.PositiveSmallIntegerField(
        choices=IDEMPOTENCY_STATUS_CHOICES, default=IDEMPOTENCY_IN_PROGRESS
    )
    booking = models.ForeignKey(
        Booking, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['key', 'organizer_email'], name='unique_idempotency_key_organizer'
            ),
        ]
