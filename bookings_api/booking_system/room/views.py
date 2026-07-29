from core.utils import parse_int

from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from room.serializers import RoomInputSerializer, RoomOutputSerializer
from room.services.room_service import RoomService

# Create your views here.

class RoomsView(APIView):
    def post(self, request):
        serializer = RoomInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        room = RoomService.create_room(
            name=data['name'],
            capacity=data['capacity'],
            floor=data['floor'],
            amenities=data['amenities'],
            timezone_name=data['timezone'],
        )
        return Response(RoomOutputSerializer(room).data, status=status.HTTP_201_CREATED)

    def get(self, request):
        min_capacity = parse_int(request.query_params.get("minCapacity"), "minCapacity")
        amenity = request.query_params.get("amenity")
        rooms = RoomService.list_rooms(min_capacity=min_capacity, amenity=amenity)
        return Response(RoomOutputSerializer(rooms, many=True).data)