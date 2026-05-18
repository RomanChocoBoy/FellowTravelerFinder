import os
import unittest
from datetime import timedelta

from datetime import date as dt_date

from facade_db import Facade_DB


class BaseDBTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = Facade_DB(
            host=os.getenv("TEST_DB_HOST", "localhost"),
            port=int(os.getenv("TEST_DB_PORT", "5432")),
            dbname=os.getenv("TEST_DB_NAME", "PIS"),
            user=os.getenv("TEST_DB_USER", "postgres"),
            password=os.getenv("TEST_DB_PASSWORD", "123456"),
        )

    @classmethod
    def tearDownClass(cls):
        cls._cleanup_tables()
        cls.db.close()

    @classmethod
    def _cleanup_tables(cls):
        with cls.db.conn.cursor() as cur:
            cur.execute(
                'TRUNCATE TABLE message, review, booking, complaint, trip, "User" RESTART IDENTITY CASCADE;'
            )

    def setUp(self):
        self._cleanup_tables()

    def create_driver(self):
        return self.db.create_user("Driver", "driver@test.local", "+79000000001", "reader")

    def create_passenger(self):
        return self.db.create_user("Passenger", "passenger@test.local", "+79000000002", "passenger")

    def future_date(self, days=30):
        return (dt_date.today() + timedelta(days=days)).isoformat()

    def create_trip(self):
        driver = self.create_driver()
        return self.db.publish_trip(
            driver_id=driver.id,
            from_city="Krasnoyarsk",
            to_city="Novosibirsk",
            date=self.future_date(),
            time="10:00",
            price=1200.0,
            seats=3,
        )
