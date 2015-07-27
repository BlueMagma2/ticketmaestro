import uuid
import time
import queue
from threading import Thread
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

    def update_booking_tree(self, rows):
        if rows:
            section = rows[0].section
            section_data = {}
            for data in self.sections:
                if data["pk"] == section.pk:
                    section_data = data
                    break
            if not section_data:
                raise Exception("booking tree error")
            for row in rows:
                row_data = {}
                for data in section_data["rows"]:
                    if data["pk"] == row.pk:
                        row_data = data
                        break
                if not row_data:
                    raise Exception("booking tree error")
                seat_available = row_data["seats_available"]
                self.update_row_data(row, row_data)
                if seat_available > row_data["seats_available"]:
                    section_data["seats_available"] -= seat_available - row_data["seats_available"]
            section_data["max_adjacent_seat"] = 0
            for row_data in section_data["rows"]:
                if row_data["max_adjacent_seat"] > section_data["max_adjacent_seat"]:
                    section_data["max_adjacent_seat"] = row_data["max_adjacent_seat"]


    def unqueue(self):
        while not self.queue.empty():
            if not self.queue.empty():
                seats_set = self.queue.get()
                seats = self.get_seats_from_labels(seats_set[0], seats_set[1])
                book_for = seats_set[2]
                request_id = seats_set[3]
                seat_already_booked = False
                if not seats:
                    self.requests[request_id] = False
                    self.queue.task_done()
                    continue
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

                rows  = []
                for b in book:
                    b.booked = True
                    b.booked_for = book_for
                    b.save()
                    if not b.seat.row in rows:
                        rows.append(b.seat.row)

                self.update_booking_tree(rows)

                self.requests[request_id] = True
                self.queue.task_done()

    def get_seats_from_labels(self, section_label, row_seat_set):
        seats = []

        try:
            section = Section.objects.get(venue=self.venue, label=section_label)
            for row_seat in row_seat_set:
                row = section.row_set.get(label=row_seat[0])
                seat = row.seat_set.get(number=row_seat[1])
                seats.append(seat.id)
        except:
            print("impossible de trouver les object")
            return []

        return seats


    def book_specific_seat(self, section_label, row_seat_set, book_for):
        """ add seats to the queue """
        request_id = uuid.uuid1()
        self.queue.put((section_label, row_seat_set, book_for, request_id))
        if not self.thread.isAlive():
            self.thread = Thread(target=self.unqueue)
            self.thread.start()
        while request_id not in self.requests:
            time.sleep(1) # IDEA : could be dependant of queue size to avoid reloading too often

        result = self.requests[request_id]
        print(result)
        self.requests.pop(request_id)
        return result

    def _book_best_adjacent_in_section(self, section, seat_count, book_for):
        """ internal fonction : book best availalble seat with section_data as a parameter instead section_label """
        seat_refused = False
        while True: # make sure we try again if our best seat are taken just before we take them
            if section["max_adjacent_seat"] < seat_count:
                return False
            for row in section["rows"]:
                if row["max_adjacent_seat"] >= seat_count:
                    row_seat_set = []
                    for seat in Seat.objects.filter(row__pk=row["pk"]):
                        booked = Book.objects.filter(event=self.event).filter(seat=seat).filter(booked=True).count() == 1
                        if not booked:
                            row_seat_set.append((row["name"], seat.number))
                        else:
                            row_seat_seat = []
                        if len(row_seat_set) == seat_count:
                            result = self.book_specific_seat(section_label, row_seat_set, book_for)
                            if result:
                                return row_seat_set
                            else:
                                seat_refused = True
                                break
            if seat_refused:
                break

    def book_best_adjacent_in_section(self, section_label, seat_count, book_for):
        """ book the best available seat_count adjacent seat for the section """
        for section in self.sections:
            if section["name"] == section_label:
                return self._book_best_adjacent_in_section(section, seat_count, book_for)
        return False

    def book_best_adjacent(self, seat_count, book_for):
        """ book the best available seat_count adjacent seat for the event """
        result = False
        for section in self.sections:
            if section["max_adjacent_seat"] < seat_count:
                result = self._book_best_adjacent_in_section(section, seat_count, book_for)
                if result:
                    break
        return result
