from tests.base_test_case import BaseDBTestCase


class TestBooking(BaseDBTestCase):
    def test_create_booking(self):
        trip = self.create_trip()
        passenger = self.create_passenger()

        booking = self.db.create_booking(trip.id, passenger.id)
        self.assertIsNotNone(booking.id)
        self.assertEqual(booking.status, "pending")

    def test_approve_booking(self):
        trip = self.create_trip()
        passenger = self.create_passenger()
        booking = self.db.create_booking(trip.id, passenger.id)

        approved = self.db.approve_booking(booking.id)
        self.assertTrue(approved)

        updated_trip = self.db.search_trips("Krasnoyarsk", "Novosibirsk", "2026-05-10")[0]
        self.assertEqual(updated_trip.available_seats, 2)

    def test_cancel_reservation(self):
        trip = self.create_trip()
        passenger = self.create_passenger()
        booking = self.db.create_booking(trip.id, passenger.id)
        self.db.approve_booking(booking.id)

        cancelled = self.db.cancel_reservation(booking.id)
        self.assertTrue(cancelled)

        updated_trip = self.db.search_trips("Krasnoyarsk", "Novosibirsk", "2026-05-10")[0]
        self.assertEqual(updated_trip.available_seats, 3)

    def test_get_reservations(self):
        trip = self.create_trip()
        passenger = self.create_passenger()
        self.db.create_booking(trip.id, passenger.id)

        reservations = self.db.get_reservations(passenger.id)
        self.assertEqual(len(reservations), 1)
