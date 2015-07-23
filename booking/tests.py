from django.test import TestCase
from booking.booking import Booking


class TestBooking(TestCase):
    """ test that booking is working like expected """

    def test_singleton(self):
        """ make sure booking is a singleton """
        booking1 = Booking.Instance()
        booking2 = Booking.Instance()
        self.assertEqual(booking1 is booking2, True)
