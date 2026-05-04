from tests.base_test_case import BaseDBTestCase


class TestTrip(BaseDBTestCase):
    def test_publish_trip(self):
        driver = self.create_driver()
        trip = self.db.publish_trip(
            driver_id=driver.id,
            from_city="A",
            to_city="B",
            date="2026-05-10",
            time="12:00",
            price=500.0,
            seats=2,
        )
        self.assertIsNotNone(trip.id)
        self.assertEqual(trip.available_seats, 2)

    def test_search_trips(self):
        trip = self.create_trip()
        found = self.db.search_trips("Krasnoyarsk", "Novosibirsk", "2026-05-10")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].id, trip.id)

    def test_get_my_trips(self):
        driver = self.create_driver()
        self.db.publish_trip(driver.id, "A", "B", "2026-05-10", "12:00", 500, 2)
        self.db.publish_trip(driver.id, "A", "C", "2026-05-11", "13:00", 600, 3)

        trips = self.db.get_my_trips(driver.id)
        self.assertEqual(len(trips), 2)
