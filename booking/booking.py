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
        self.venue = self.event.venue

        # construct tree of sections/rows/seats to access information faster
        self.sections = []

        for section in self.venue.section_set.all().order_by("rank"):
            section_data = {"name":section.label, "rank":section.rank, "max_adjacent_seat":0, "seats_available": 0, "rows": []}
            self.sections.append(section_data)

            for row in section.row_set.all().order_by("rank"):
                row_data = {"name":row.label, "rank":row.rank, "max_adjacent_seat":0, "seats_available": 0}
                section_data["rows"].append(row_data)

                # we count how many seats and adjacent seats are available
                seats_available = row.seat_set.all().filter(booked=False).order_by("number")
                row_data["seats_available"] = seats_available.count()
                section_data["seats_available"] += row_data["seats_available"]

                counter = 0 # count adjacent seat
                last_number = -1 # seat number of the previous iteration
                for seat in seats_available:
                    if seat.number > last_number + 1:
                        if counter > row_data["max_adjacent_seat"]:
                            row_data["max_adjacent_seat"] = counter
                        counter = 0
                    last_number = seat.number
                    counter += 1

                if counter > row_data["max_adjacent_seat"]:
                    row_data["max_adjacent_seat"] = counter

                if row_data["max_adjacent_seat"] > section_data["max_adjacent_seat"]:
                    section_data["max_adjacent_seat"] = row_data["max_adjacent_seat"]
