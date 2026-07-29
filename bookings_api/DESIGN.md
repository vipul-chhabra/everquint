# DESIGN 

A room-booking REST API built with Django and Django REST Framework and db used is
SQLite.

## Code Structure
The code is split into two apps plus a shared, core app so business logic never lives in the routing layer and the 
two apps have different functionalities:


core/                 # shared, between the two .

room/                 # app for functionality of room

booking/              # app for functionality of booking 


## Data Model 
" can check models in each app(room, booking) in models.py "

**Room**
- name (charfield) #for adding name used charfield
- capacity (PositiveIntegerField) # as capacity is min > 1
- floor(PositiveSmallIntegerField) # floor cannot be large number and integer
- timezone (CharField)  # by default utc, room local time zone
- created_at (DateTimeField) # it automatically gets added when room is created

#added a unique constraint so that there could be case-insensitive name uniqueness

**Amenity**
- room (ForeignKey(Room)) #on room deletion amentities are also deleted for that room
- name (CharField)

#choose a new model over adding key to room model so querying amenties becomes easy 

**Booking**
- room (ForeignKey(Room))
- title (CharField)
- organizer_email (EmailField)
- start_time (DateTimeField)
- end_time (DateTimeField)
- status = (PositiveSmallIntegerField) # used enum option status choices of confirmed or cancelled
- created_at (DateTimeField) #automatically gets added when booking is created
- cancelled_at (DateTimeField)

#Index on (room, status, start_time, end_time) to serve the overlap query.

**IdempotencyKey**
- key (CharField) #idempotency key
- organizer_email (EmailField)
- status (PositiveSmallIntegerField) # used enum option status choices of in progress and completed
- booking (ForeignKey(Booking)) # on booking deletion it will not get deleted instead will be set to null
- created_at (DateTimeField)  #automatically gets added when booking is created

#added a unique constraint on (key, organizer_email)

## Enforcing No Overlaps 

1) An interval [start, end) is treated as half-open, so bookings that just touches the end 
(eg. 10:00–11:00 and 11:00–12:00) do not conflict.

2) Two confirmed bookings on the same room overlap if:
existing.start_time < new.end_time AND existing.end_time > new.start_time

3) Cancelled bookings never block a new bookings as query filters on status='confirmed' , so a cancelled slot is 
available for re-booking .

## Error handling strategy

1) Every custom error inherits from custom BaseApiException, which carries a status_code, error_name and error detail . 
Generic exceptions live in core app and each app defines its own exceptions.

2) Custom_exception_handler is wired via REST_FRAMEWORK["EXCEPTION_HANDLER"] which renders every error custom or drf 
exceptions in the format:
{ "error": "ValidationError", "message": "startTime must be before endTime." }

3) There is exception if None of the defined error is there in that case a http 500 error is raised.


## How idempotency is implemented

Clients send an 'Idempotency-Key' in headers and db has unique constraints (key, organizer_email):

1) On first request of and 'IdempotencyKey' insert an 'IdempotencyKey' row as 'in_progress', create
the booking, then mark the row as 'completed' with a link to the booking. All of this is enclosed in one transaction,
so if booking creation fails, the idempotency row is rolled back too and the client can retry.
2) On a later request with the same key due to unique constraint no new entry is created and it finds the completed 
record, and returns the same booking with 200 response in case of a new entry creation function returns 201.
3) On second request arriving while the first is still 'in_progress' finds the record and returns 409 'already in progress' 
rather than creating a second booking.

As the record lives in a DB table, idempotency survives process restarts.

## How concurrency is handled

1) For same room double booking 'select_for_update()' it lock the row for any insertion so while a booking is in 
progress it locks the room so that another booking cant be made after the transaction lock is released for the another 
booking and while in transaction it checks for overlaps if exist transaction is rolled back with error raised if no 
overlaps booking is created
2) In case of Idempotency the unique constraint (key, organizer_email) constraint is the arbiter which allows exactly 
one concurrent insertion wins; the loser catches IntegrityError and either gives the same completed booking or returns 409.


## How utilization is calculated


For each room:

totalBookingHours  = sum of overlap_hours(booking, [from, to])   # confirmed only
businessHours      = business hours (Mon–Fri 08:00–20:00, room-local) in [from, to]
utilizationPercent = totalBookingHours / businessHours       # 0 if businessHours == 0

Points to be noted
- a booking that starts before from or ends after to contributes only the portion inside the range.
- Cancelled bookings are excluded.
- Business hours are computed every day in the room's timezone, summing the intersection of each weekday's 08:00–20:00 
window. A full weekday contributes 12h and weekends contribute 0.
- utilizationPercent is a ratio in from 0-1 eg. 0.45, rounded to 4 decimal places.

### Assumptions
- Business hours are fixed at Mon–Fri 08:00–20:00, as per room-local timezone.
- Overlapping confirmed bookings can't exist , so booked hours never double-count.
- Since bookings are constrained to business hours at creation, booked hours are
a subset of business hours for any given range for those bookings.