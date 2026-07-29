

from booking.utils import business_hours_in_range, overlap_hours
from booking.constants import BOOKING_STATUS_CONFIRMED
from booking.models import Booking, Room




class ReportService(object):
    """Report for room utilization."""

    @staticmethod
    def room_utilization(time_from, time_to):
        """
        utilization per room over given time range.
        """
        report = []
        rooms = Room.objects.all().order_by('id')

        for room in rooms:
            bookings = Booking.objects.filter(
                room=room,
                status=BOOKING_STATUS_CONFIRMED,
                start_time__lt=time_to,
                end_time__gt=time_from,
            )

            total_booked = sum(
                overlap_hours(booking.start_time, booking.end_time, time_from, time_to)
                for booking in bookings
            )
            business_hours = business_hours_in_range(time_from, time_to, room.timezone)
            utilization = (total_booked / business_hours) if business_hours > 0 else 0.0

            report.append({
                'roomId': room.id,
                'roomName': room.name,
                'totalBookingHours': round(total_booked, 4),
                'utilizationPercent': round(utilization, 4),
            })
        return report
