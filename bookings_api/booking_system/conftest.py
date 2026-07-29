import pytest
from rest_framework.test import APIClient

from room.models import Amenity, Room


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def room(db):
    instance = Room.objects.create(name="Teaching Room", capacity=10, floor=3, timezone="UTC")
    Amenity.objects.bulk_create([
        Amenity(room=instance, name="Projector"),
        Amenity(room=instance, name="Whiteboard"),
    ])
    return instance
