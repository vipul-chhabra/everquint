from django.db import IntegrityError, transaction

from core.time_utils import resolve_timezone
from room.constants import DEFAULT_ROOM_TIMEZONE
from room.exceptions import RoomNameAlreadyExistsException

from room.models import Room , Amenity


class RoomService(object):
    """Business operations for rooms and their amenities."""

    @staticmethod
    def create_room(name, capacity, floor, amenities=None, timezone_name=DEFAULT_ROOM_TIMEZONE):
        """
        Create a room and its amenities.
        """
        resolve_timezone(timezone_name)
        try:
            with transaction.atomic():
                room = Room.objects.create(
                    name=name,
                    capacity=capacity,
                    floor=floor,
                    timezone=timezone_name,
                )
                RoomService.create_amenities(room, amenities)
        except IntegrityError:
            raise RoomNameAlreadyExistsException(
                "A room named '{0}' already exists (case-insensitive).".format(name)
            )
        return room

    @staticmethod
    def create_amenities(room, amenities):
        """
        create a room amenities.
        """
        rows = []
        seen = set()
        for raw in amenities or []:
            name = str(raw).strip()
            key = name.lower()
            if name and key not in seen:
                seen.add(key)
                rows.append(Amenity(room=room, name=name))
        if rows:
            Amenity.objects.bulk_create(rows)

    @staticmethod
    def list_rooms(min_capacity=None, amenity=None):
        """
        List rooms filtered by minimum capacity and amenity membership.
        """
        room_data = Room.objects.all().prefetch_related('amenities').order_by('id')
        if min_capacity is not None:
            room_data = room_data.filter(capacity__gte=min_capacity)
        if amenity:
            room_data = room_data.filter(amenities__name__iexact=amenity.strip()).distinct()
        return room_data
