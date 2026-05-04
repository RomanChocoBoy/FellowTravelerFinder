from tests.base_test_case import BaseDBTestCase


class TestReview(BaseDBTestCase):
    def test_create_review(self):
        trip = self.create_trip()
        passenger = self.create_passenger()

        created = self.db.create_review(trip.id, passenger.id, 5, "Great trip")
        self.assertTrue(created)

        users = self.db.get_all_users()
        driver = [u for u in users if u.id == trip.driver_id][0]
        self.assertEqual(driver.rating, 5.0)
