from booking.utils.singleton import Singleton
from booking.models import Venue, Event, Section, Row, Seat


@Singleton
class Booking:
    """ serve the BookingEvent corresponding to the event we want to book for """
    def __init__(self):
        self.events = {}

    def get_event(self, event_pk):
        if event_pk in self.events:
            return self.events[event_pk]
        else:
            event = BookingEvent(event_pk)
            self.events[event_pk] = event
            return event

    class BookingEvent:
        def __init__(self, event_pk):
            self.event_pk = event_pk
