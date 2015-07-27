import uuid
import time
import queue
from threading import Thread
from django.db import connection
from booking.utils.singleton import Singleton
from booking.models import Venue, Event, Section, Row, Seat, Book


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
        self.queue = queue.Queue()
        self.requests = {}
        self.thread = Thread(target=self.unqueue)

        # construct tree of sections/rows/seats to access information faster
        self.sections = []

        for section in self.venue.section_set.all().order_by("rank"):
            section_data = {"pk":section.pk, "name":section.label, "rank":section.rank, "max_adjacent_seat":0, "seats_available": 0, "rows": []}
            self.sections.append(section_data)

            for row in section.row_set.all().order_by("rank"):
                row_data = {"pk":row.pk, "name":row.label, "rank":row.rank, "max_adjacent_seat":0, "seats_available": 0}
                section_data["rows"].append(row_data)

                # we count how many seats and adjacent seats are available
                self.update_row_data(row, row_data)
                section_data["seats_available"] += row_data["seats_available"]
                if row_data["max_adjacent_seat"] > section_data["max_adjacent_seat"]:
                    section_data["max_adjacent_seat"] = row_data["max_adjacent_seat"]

    def update_row_data(self, row, row_data):
        """ update row_data with row data """
        already_booked_pks = Book.objects.filter(event=self.event).filter(booked=True).values_list("seat", flat=True)
        seats_available = row.seat_set.order_by("number").exclude(id__in=already_booked_pks)
        row_data["seats_available"] = seats_available.count()
        row_data["max_adjacent_seat"] = 0

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

    def unqueue(self):
        while not self.queue.empty():
            if not self.queue.empty():
                seats_set = self.queue.get()
                seats = seats_set[0]
                book_for = seats_set[1]
                request_id = seats_set[2]
                seat_already_booked = False
                book = []
                for seat in seats:
                    booked = Book.objects.filter(event=self.event).filter(seat=seat).filter(booked=True).count() == 1
                    if booked:
                        print("already booked")
                        self.requests[request_id] = False
                        self.queue.task_done()
                        seat_already_booked = True
                        break
                    else:
                        if Book.objects.filter(event=self.event).filter(seat=seat).filter(booked=False).count() != 0:
                            book.append(Book.objects.get(event=self.event, seat=seat, booked=False))
                        else:
                            book.append(Book.objects.create(event=self.event, seat=seat, booked=False))
                if seat_already_booked:
                    continue
                rows = []
                for b in book:
                    b.booked = True
                    b.booked_for = book_for
                    b.save()
                    if not seat.row in rows:
                        rows.append(seat.row)
                # TODO : update tree

                self.requests[request_id] = True
                self.queue.task_done()
