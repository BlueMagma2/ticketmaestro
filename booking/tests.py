from django.test import TestCase
from booking.booking import Booking
from booking.models import Venue, Event, Section, Row, Seat


class TestBooking(TestCase):
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
                row = Row.objects.create(section=section, label="east", rank=i)
                self.rows[section.label].append(row)
                for s in range(5):
                    if section_index == 2:
                        Seat.objects.create(row=row, number=s, booked=True, booked_for="the queen")
                    elif section_index == 4 and i == 0:
                        Seat.objects.create(row=row, number=s, booked=True, booked_for="some first class fan")
                    elif section_index == 0 and s == 2:
                        Seat.objects.create(row=row, number=s, booked=True, booked_for="middle watcher")
                    else:
                        Seat.objects.create(row=row, number=s, booked=False, booked_for="")

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
