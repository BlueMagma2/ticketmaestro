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
