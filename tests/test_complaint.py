from tests.base_test_case import BaseDBTestCase


class TestComplaint(BaseDBTestCase):
    def _linked_users(self):
        trip = self.create_trip()
        sender = self.create_passenger()
        self.db.create_booking(trip.id, sender.id)
        return sender, trip

    def test_create_and_get_all_complaints(self):
        sender, trip = self._linked_users()
        recipient = self.db.get_user_by_id(trip.driver_id)

        complaint = self.db.create_complaint(sender.id, recipient.id, "Spam", "Too many messages", trip.id)
        self.assertIsNotNone(complaint)
        self.assertIsNotNone(complaint.id)

        complaints = self.db.get_all_complaints()
        self.assertEqual(len(complaints), 1)

    def test_approve_complaint(self):
        sender, trip = self._linked_users()
        recipient = self.db.get_user_by_id(trip.driver_id)
        complaint = self.db.create_complaint(sender.id, recipient.id, "Abuse", "Bad behavior", trip.id)

        approved = self.db.approve_complaint(complaint.id)
        self.assertTrue(approved)

        complaints = self.db.get_all_complaints()
        self.assertEqual(complaints[0].status, "approved")

    def test_reject_complaint(self):
        sender, trip = self._linked_users()
        recipient = self.db.get_user_by_id(trip.driver_id)
        complaint = self.db.create_complaint(sender.id, recipient.id, "Fake", "Not true", trip.id)

        rejected = self.db.reject_complaint(complaint.id)
        self.assertTrue(rejected)

        complaints = self.db.get_all_complaints()
        self.assertEqual(complaints[0].status, "rejected")
