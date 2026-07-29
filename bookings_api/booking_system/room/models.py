from django.db import models
from django.db.models.functions import Lower



class Room(models.Model):
    name = models.CharField(max_length=200)
    capacity = models.PositiveIntegerField()
    floor = models.PositiveSmallIntegerField()
    timezone = models.CharField(max_length=64, default="UTC")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(Lower("name"), name="unique_room_name"),
        ]


class Amenity(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='amenities')
    name = models.CharField(max_length=100, db_index=True)

    class Meta:
        unique_together = ('room', 'name')

