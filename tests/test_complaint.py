from tests.base_test_case import BaseDBTestCase


class TestComplaint(BaseDBTestCase):
    def test_create_and_get_all_complaints(self):
        sender = self.create_passenger()
        recipient = self.create_driver()

        complaint = self.db.create_complaint(sender.id, recipient.id, "Spam", "Too many messages")
        self.assertIsNotNone(complaint.id)

        complaints = self.db.get_all_complaints()
        self.assertEqual(len(complaints), 1)

    def test_approve_complaint(self):
        sender = self.create_passenger()
        recipient = self.create_driver()
        complaint = self.db.create_complaint(sender.id, recipient.id, "Abuse", "Bad behavior")

        approved = self.db.approve_complaint(complaint.id)
        self.assertTrue(approved)

        complaints = self.db.get_all_complaints()
        self.assertEqual(complaints[0].status, "approved")

    def test_reject_complaint(self):
        sender = self.create_passenger()
        recipient = self.create_driver()
        complaint = self.db.create_complaint(sender.id, recipient.id, "Fake", "Not true")

        rejected = self.db.reject_complaint(complaint.id)
        self.assertTrue(rejected)

        complaints = self.db.get_all_complaints()
        self.assertEqual(complaints[0].status, "rejected")
