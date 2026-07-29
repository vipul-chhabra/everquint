from django.urls import path

from room.views import RoomsView

urlpatterns = [
    path('rooms', RoomsView.as_view(), name='rooms'),
]
