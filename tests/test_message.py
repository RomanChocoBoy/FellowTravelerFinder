from tests.base_test_case import BaseDBTestCase


class TestMessage(BaseDBTestCase):
    def test_send_and_get_messages(self):
        trip = self.create_trip()
        passenger = self.create_passenger()
        self.db.create_booking(trip.id, passenger.id)

        sent = self.db.send_message(trip.id, passenger.id, trip.driver_id, "Hello")
        self.assertTrue(sent)

        messages = self.db.get_messages(passenger.id, trip.driver_id)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].text, "Hello")
