from django.core.exceptions import ObjectDoesNotExist
from booking.utils.singleton import Singleton
from booking.models import Venue, Event, Section, Row, Seat


@Singleton
class Booking:
    """ serve the BookingEvent corresponding to the event we want to book for """
    def __init__(self):
        self.events = {}

    def get_event(self, event_pk):
        """ return the Booking event object we are looking for or create it and add it to the events dict """
        if event_pk in self.events:
            return self.events[event_pk]
        else:
            event = _BookingEvent(event_pk)
            self.events[event_pk] = event
            return event


class _BookingEvent:
    """ represent an event and contain all method to book ticket for this event """
    def __init__(self, event_pk):
        try:
            self.event = Event.objects.get(pk=event_pk)
        except:
            raise Exception("No Event for this primary key in the database")
