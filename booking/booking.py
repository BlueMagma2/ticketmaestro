from booking.utils.singleton import Singleton
from booking.models import Venue, Event, Section, Row, Seat


@Singleton
class Booking:
    def __init__(self):
        print('booking created')
