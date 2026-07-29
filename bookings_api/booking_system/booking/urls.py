from django.urls import path

from booking.views import BookingCancelView, BookingsView, RoomUtilizationView

urlpatterns = [
    path('bookings', BookingsView.as_view(), name='bookings'),
    path('bookings/<int:booking_id>/cancel', BookingCancelView.as_view(), name='booking-cancel'),
    path('reports/room-utilization', RoomUtilizationView.as_view(), name='room-utilization'),
]
