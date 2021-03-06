import time
from django.test import TransactionTestCase
from booking.booking import Booking
from booking.models import Venue, Event, Section, Row, Seat, Book


class TestBooking(TransactionTestCase):
    """ test that booking is working like expected """

    def setUp(self):
        """ create tests data """
        self.venue = Venue.objects.create(name="a venue")
        self.event1 = Event.objects.create(venue=self.venue, name="first event")
        self.event2 = Event.objects.create(venue=self.venue, name="second event")

        self.sections = [];
        self.sections.append(Section.objects.create(venue=self.venue, label="east", rank=3))
        self.sections.append(Section.objects.create(venue=self.venue, label="north", rank=3))
        self.sections.append(Section.objects.create(venue=self.venue, label="VIP", rank=1))
        self.sections.append(Section.objects.create(venue=self.venue, label="south", rank=3))
        self.sections.append(Section.objects.create(venue=self.venue, label="first class", rank=2))
        self.sections.append(Section.objects.create(venue=self.venue, label="west", rank=3))

        self.rows = {}
        for section_index in range(len(self.sections)):
            section = self.sections[section_index]
            self.rows[section.label] = []
            for i in range(5):
                row = Row.objects.create(section=section, label=i, rank=i)
                self.rows[section.label].append(row)
                for s in range(5):
                    seat = Seat.objects.create(row=row, number=s)
                    if section_index == 2:
                        Book.objects.create(event=self.event1, seat=seat, booked=True, booked_for="the queen")
                    elif section_index == 4 and i == 0:
                        Book.objects.create(event=self.event1, seat=seat, booked=True, booked_for="some first class fan")
                    elif section_index == 0 and s == 2:
                        Book.objects.create(event=self.event1, seat=seat, booked=True, booked_for="middle watcher")
                    else:
                        Book.objects.create(event=self.event1, seat=seat, booked=False, booked_for="")

    def test_singleton(self):
        """ make sure booking is a singleton """
        booking1 = Booking.Instance()
        booking2 = Booking.Instance()
        self.assertTrue(booking1 is booking2)

    def test_get_event(self):
        """ make sure you get the event you want and that asking for a wrong primary key raise an error """
        booking_event = Booking.Instance().get_event(self.event1.pk)
        self.assertEqual(booking_event.event, self.event1)
        error = False
        try:
            Booking.Instance().get_event(-1)
        except:
            error = True
        self.assertTrue(error)

    def test_booking_tree(self):
        """ make sure the booking tree is correctly constructed with correct data """
        tree = Booking.Instance().get_event(self.event1.pk).sections
        self.assertEqual(len(tree), 6)
        self.assertEqual(tree[0]["name"], "VIP")
        self.assertEqual(tree[0]["seats_available"], 0)
        self.assertEqual(tree[0]["max_adjacent_seat"], 0)

        self.assertEqual(tree[1]["name"], "first class")
        self.assertEqual(tree[1]["seats_available"], 20)
        self.assertEqual(tree[1]["max_adjacent_seat"], 5)
        self.assertEqual(tree[1]["rows"][0]["max_adjacent_seat"], 0)

        self.assertEqual(tree[2]["name"], "east")
        self.assertEqual(tree[2]["seats_available"], 20)
        self.assertEqual(tree[2]["max_adjacent_seat"], 2)

        self.assertEqual(tree[3]["seats_available"], 25)
        self.assertEqual(tree[3]["max_adjacent_seat"], 5)

    def test_book_specific_seat(self):
        """ make sure the function 'book specific seat' is correctly working """
        booking_event = Booking.Instance().get_event(self.event1.pk)
        tree = booking_event.sections
        self.assertEqual(booking_event.book_specific_seat("VIP", [(0,0),(0,1)], "some vip"), False)
        self.assertEqual(booking_event.book_specific_seat("west", [(0,0),(0,1)], "some guy"), True)
        self.assertEqual(tree[5]["seats_available"], 23)
        self.assertEqual(tree[5]["max_adjacent_seat"], 5)

        self.assertEqual(booking_event.book_specific_seat("west", [(1,2)], "some guy"), True)
        self.assertEqual(booking_event.book_specific_seat("west", [(2,2)], "some guy"), True)
        self.assertEqual(booking_event.book_specific_seat("west", [(3,2)], "some guy"), True)
        self.assertEqual(booking_event.book_specific_seat("west", [(4,2)], "some guy"), True)
        self.assertEqual(tree[5]["seats_available"], 19)
        self.assertEqual(tree[5]["max_adjacent_seat"], 3)


        self.assertEqual(booking_event.book_specific_seat("west", [(0,0),(0,1)], "some other guy"), False)

    def test_book_best_seats(self):
        """ test the three function for booking the best adjacent seats """
        booking_event = Booking.Instance().get_event(self.event1.pk)
        tree = booking_event.sections

        self.assertEqual(booking_event.book_best_adjacent_in_section("first class", 3, "three in a row"), [('1',0),('1',1),('1',2)])
        self.assertEqual(booking_event.book_best_adjacent_in_section("first class", 4, "three in a row"), [('2',0),('2',1),('2',2),('2',3)])
        self.assertEqual(booking_event.book_best_adjacent_in_section("first class", 2, "two in a row"), [('1',3),('1',4)])
        booking_event.book_best_adjacent_in_section("first class", 4, "three in a row")
        booking_event.book_best_adjacent_in_section("first class", 4, "three in a row")
        self.assertEqual(booking_event.book_best_adjacent_in_section("first class", 2, "no more seats in first class"), False)
        self.assertEqual(booking_event.book_best_adjacent(2, "two in a row"), ("east", [('0',0),('0',1)]))
