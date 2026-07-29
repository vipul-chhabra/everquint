from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from booking.constants import DEFAULT_PAGE_LIMIT, MAX_PAGE_LIMIT
from core.exceptions import InvalidQueryParameterException
from booking.serializers import BookingInputSerializer, BookingOutputSerializer
from booking.services.booking_service import BookingService
from booking.services.report_service import ReportService
from core.utils import parse_datetime, parse_int

# Create your views here.


class BookingsView(APIView):

    def post(self, request):
        serializer = BookingInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        idempotency_key = request.headers.get('Idempotency-Key')

        booking, replayed = BookingService.create_booking(
            room_id=data['roomId'],
            title=data['title'],
            organizer_email=data['organizerEmail'],
            start_time=data['startTime'],
            end_time=data['endTime'],
            idempotency_key=idempotency_key,
        )
        status_code = status.HTTP_200_OK if replayed else status.HTTP_201_CREATED
        return Response(BookingOutputSerializer(booking).data, status=status_code)

    def get(self, request):
        params = request.query_params
        room_id = parse_int(params.get('roomId'), 'roomId')
        time_from = parse_datetime(params.get('from'), 'from')
        time_to = parse_datetime(params.get('to'), 'to')
        limit = parse_int(params.get('limit'), 'limit')
        offset = parse_int(params.get('offset'), 'offset')
        limit = DEFAULT_PAGE_LIMIT if limit is None else limit
        offset = 0 if offset is None else offset
        if limit < 0 or offset < 0:
            raise InvalidQueryParameterException('limit and offset must be non-negative.')
        limit = min(limit, MAX_PAGE_LIMIT)
        items, total = BookingService.list_bookings(
            room_id=room_id,
            time_from=time_from,
            time_to=time_to,
            limit=limit,
            offset=offset,
        )
        return Response({
            'items': BookingOutputSerializer(items, many=True).data,
            'total': total,
            'limit': limit,
            'offset': offset,
        })


class BookingCancelView(APIView):

    def post(self, request, booking_id):
        booking = BookingService.cancel_booking(booking_id=booking_id)
        return Response(BookingOutputSerializer(booking).data)


class RoomUtilizationView(APIView):

    def get(self, request):
        raw_from = request.query_params.get('from')
        raw_to = request.query_params.get('to')
        if not raw_from or not raw_to:
            raise InvalidQueryParameterException("Both from and to query parameters are required.")
        time_from = parse_datetime(raw_from, 'from')
        time_to = parse_datetime(raw_to, 'to')
        if time_to <= time_from:
            raise InvalidQueryParameterException("from must be before to.")
        report = ReportService.room_utilization(time_from=time_from, time_to=time_to)
        return Response(report)