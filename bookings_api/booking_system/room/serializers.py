from rest_framework import serializers

from room.constants import DEFAULT_ROOM_TIMEZONE
from room.models import  Room



class RoomInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200, trim_whitespace=True)
    capacity = serializers.IntegerField(min_value=1)
    floor = serializers.IntegerField()
    amenities = serializers.ListField(
        child=serializers.CharField(max_length=100), required=False, default=list
    )
    timezone = serializers.CharField(max_length=64, required=False, default=DEFAULT_ROOM_TIMEZONE)



class RoomOutputSerializer(serializers.ModelSerializer):
    amenities = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'name', 'capacity', 'floor', 'amenities', 'timezone', 'createdAt']

    def get_amenities(self, room):
        return [amenity.name for amenity in room.amenities.all()]
