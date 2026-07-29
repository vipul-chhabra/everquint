
from rest_framework import serializers

from booking.constants import BOOKING_STATUS_LABELS
from booking.models import Booking


class BookingInputSerializer(serializers.Serializer):
    roomId = serializers.CharField()
    title = serializers.CharField(max_length=300, trim_whitespace=True)
    organizerEmail = serializers.EmailField()
    startTime = serializers.DateTimeField()
    endTime = serializers.DateTimeField()



class BookingOutputSerializer(serializers.ModelSerializer):
    roomId = serializers.IntegerField(source='room_id', read_only=True)
    organizerEmail = serializers.EmailField(source='organizer_email', read_only=True)
    startTime = serializers.DateTimeField(source='start_time', read_only=True)
    endTime = serializers.DateTimeField(source='end_time', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    cancelledAt = serializers.DateTimeField(source='cancelled_at', read_only=True)
    status = serializers.SerializerMethodField()

    def get_status(self, booking):
        return BOOKING_STATUS_LABELS.get(booking.status)

    class Meta:
        model = Booking
        fields = [
            'id', 'roomId', 'title', 'organizerEmail', 'startTime', 'endTime', 'status', 'createdAt', 'cancelledAt',
        ]
