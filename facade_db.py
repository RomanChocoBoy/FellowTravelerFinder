import os

# Для совместимости с сервером; драйвер psycopg (v3) на Windows обычно ведёт себя стабильнее, чем psycopg2.
os.environ.setdefault("PGCLIENTENCODING", "UTF8")

from dataclasses import dataclass
from datetime import datetime

import psycopg


@dataclass
class User:
    id: int
    name: str
    email: str
    phone: str
    role: str
    rating: float
    status: str


@dataclass
class Trip:
    id: int
    driver_id: int
    from_place: str
    to_place: str
    date: datetime
    price: float
    seats: int
    available_seats: int
    status: str


@dataclass
class Booking:
    id: int
    trip_id: int
    passenger_id: int
    booking_date: datetime
    status: str


@dataclass
class Message:
    id: int
    trip_id: int | None
    sender_id: int
    recipient_id: int
    text: str
    datetime: datetime
    is_read: bool


@dataclass
class Complaint:
    id: int
    sender_id: int
    recipient_id: int
    reason: str
    description: str | None
    date: datetime
    status: str


class Facade_DB:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        dbname: str = "PIS",
        user: str = "postgres",
        password: str = "123456",
    ):
        self.conn = psycopg.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
            autocommit=True,
        )

    def close(self) -> None:
        self.conn.close()


    @staticmethod
    def _map_user(row) -> User:
        return User(
            id=row[0],
            name=row[1],
            email=row[2],
            phone=row[3],
            role=row[4],
            rating=float(row[5]),
            status=row[6],
        )

    @staticmethod
    def _map_trip(row) -> Trip:
        return Trip(
            id=row[0],
            driver_id=row[1],
            from_place=row[2],
            to_place=row[3],
            date=row[4],
            price=float(row[5]),
            seats=row[6],
            available_seats=row[7],
            status=row[8],
        )

    @staticmethod
    def _map_booking(row) -> Booking:
        return Booking(*row)

    @staticmethod
    def _map_message(row) -> Message:
        return Message(*row)

    @staticmethod
    def _map_complaint(row) -> Complaint:
        return Complaint(*row)


    def create_user(self, name: str, email: str, phone: str, role: str) -> User:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO "User" (name, email, phone, role)
                VALUES (%s, %s, %s, %s)
                RETURNING id, name, email, phone, role, rating, status;
                """,
                (name, email, phone, role),
            )
            return self._map_user(cur.fetchone())

    def get_all_users(self) -> list[User]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, email, phone, role, rating, status
                FROM "User"
                ORDER BY id;
                """
            )
            rows = cur.fetchall()
            return [self._map_user(row) for row in rows]

    def block_user(self, user_id: int) -> bool:
        with self.conn.cursor() as cur:
            cur.execute('UPDATE "User" SET status = %s WHERE id = %s;', ("blocked", user_id))
            return cur.rowcount > 0

    def unblock_user(self, user_id: int) -> bool:
        with self.conn.cursor() as cur:
            cur.execute('UPDATE "User" SET status = %s WHERE id = %s;', ("active", user_id))
            return cur.rowcount > 0


    def publish_trip(
        self,
        driver_id: int,
        from_city: str,
        to_city: str,
        date: str,
        time: str,
        price: float,
        seats: int,
        description: str = "",
    ) -> Trip:
        trip_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")

        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO Trip (driver_id, from_location, to_location, date, price, seats, available_seats, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'active')
                RETURNING id, driver_id, from_location, to_location, date, price, seats, available_seats, status;
                """,
                (driver_id, from_city, to_city, trip_datetime, price, seats, seats),
            )
            return self._map_trip(cur.fetchone())

    def search_trips(self, from_city: str, to_city: str, date: str) -> list[Trip]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, driver_id, from_location, to_location, date, price, seats, available_seats, status
                FROM Trip
                WHERE from_location = %s
                  AND to_location = %s
                  AND DATE(date) = %s
                  AND status = 'active'
                  AND available_seats > 0
                ORDER BY date;
                """,
                (from_city, to_city, date),
            )
            rows = cur.fetchall()
            return [self._map_trip(row) for row in rows]

    def get_my_trips(self, driver_id: int) -> list[Trip]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, driver_id, from_location, to_location, date, price, seats, available_seats, status
                FROM Trip
                WHERE driver_id = %s
                ORDER BY date;
                """,
                (driver_id,),
            )
            rows = cur.fetchall()
            return [self._map_trip(row) for row in rows]


    def create_booking(self, trip_id: int, passenger_id: int) -> Booking:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO Booking (trip_id, passenger_id, status)
                VALUES (%s, %s, 'pending')
                RETURNING id, trip_id, passenger_id, booking_date, status;
                """,
                (trip_id, passenger_id),
            )
            return self._map_booking(cur.fetchone())

    def approve_booking(self, booking_id: int) -> bool:
        with self.conn.cursor() as cur:
            cur.execute('UPDATE Booking SET status = %s WHERE id = %s;', ("approved", booking_id))
            if cur.rowcount == 0:
                return False

            cur.execute(
                """
                UPDATE Trip
                SET available_seats = available_seats - 1
                WHERE id = (SELECT trip_id FROM Booking WHERE id = %s);
                """,
                (booking_id,),
            )
            return True

    def cancel_reservation(self, booking_id: int) -> bool:
        with self.conn.cursor() as cur:
            cur.execute('UPDATE Booking SET status = %s WHERE id = %s;', ("cancelled", booking_id))
            if cur.rowcount == 0:
                return False

            cur.execute(
                """
                UPDATE Trip
                SET available_seats = available_seats + 1
                WHERE id = (SELECT trip_id FROM Booking WHERE id = %s);
                """,
                (booking_id,),
            )
            return True

    def get_reservations(self, passenger_id: int) -> list[Booking]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, trip_id, passenger_id, booking_date, status
                FROM Booking
                WHERE passenger_id = %s
                ORDER BY booking_date;
                """,
                (passenger_id,),
            )
            rows = cur.fetchall()
            return [self._map_booking(row) for row in rows]


    def send_message(self, trip_id: int | None, sender_id: int, recipient_id: int, text: str) -> bool:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO Message (trip_id, sender_id, recipient_id, text)
                VALUES (%s, %s, %s, %s);
                """,
                (trip_id, sender_id, recipient_id, text),
            )
            return True

    def get_messages(self, user_id: int, other_user_id: int, trip_id: int | None = None) -> list[Message]:
        with self.conn.cursor() as cur:
            if trip_id is None:
                cur.execute(
                    """
                    SELECT id, trip_id, sender_id, recipient_id, text, datetime, is_read
                    FROM Message
                    WHERE (sender_id = %s AND recipient_id = %s)
                       OR (sender_id = %s AND recipient_id = %s)
                    ORDER BY datetime;
                    """,
                    (user_id, other_user_id, other_user_id, user_id),
                )
            else:
                cur.execute(
                    """
                    SELECT id, trip_id, sender_id, recipient_id, text, datetime, is_read
                    FROM Message
                    WHERE trip_id = %s
                      AND (
                            (sender_id = %s AND recipient_id = %s)
                         OR (sender_id = %s AND recipient_id = %s)
                      )
                    ORDER BY datetime;
                    """,
                    (trip_id, user_id, other_user_id, other_user_id, user_id),
                )
            rows = cur.fetchall()
            return [self._map_message(row) for row in rows]


    def create_review(self, trip_id: int, author_id: int, rating: int, comment: str) -> bool:
        with self.conn.cursor() as cur:
            cur.execute("SELECT driver_id FROM Trip WHERE id = %s;", (trip_id,))
            trip_row = cur.fetchone()
            if not trip_row:
                return False

            recipient_id = trip_row[0]
            cur.execute(
                """
                INSERT INTO Review (trip_id, author_id, recipient_id, rating, comment)
                VALUES (%s, %s, %s, %s, %s);
                """,
                (trip_id, author_id, recipient_id, rating, comment),
            )

            cur.execute(
                """
                UPDATE "User"
                SET rating = (
                    SELECT ROUND(AVG(rating)::numeric, 2)
                    FROM Review
                    WHERE recipient_id = %s
                )
                WHERE id = %s;
                """,
                (recipient_id, recipient_id),
            )
            return True


    def create_complaint(self, sender_id: int, recipient_id: int, reason: str, description: str) -> Complaint:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO Complaint (sender_id, recipient_id, reason, description)
                VALUES (%s, %s, %s, %s)
                RETURNING id, sender_id, recipient_id, reason, description, date, status;
                """,
                (sender_id, recipient_id, reason, description),
            )
            return self._map_complaint(cur.fetchone())

    def get_all_complaints(self) -> list[Complaint]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, sender_id, recipient_id, reason, description, date, status
                FROM Complaint
                ORDER BY date DESC;
                """
            )
            rows = cur.fetchall()
            return [self._map_complaint(row) for row in rows]

    def approve_complaint(self, complaint_id: int) -> bool:
        with self.conn.cursor() as cur:
            cur.execute('UPDATE Complaint SET status = %s WHERE id = %s;', ("approved", complaint_id))
            return cur.rowcount > 0

    def reject_complaint(self, complaint_id: int) -> bool:
        with self.conn.cursor() as cur:
            cur.execute('UPDATE Complaint SET status = %s WHERE id = %s;', ("rejected", complaint_id))
            return cur.rowcount > 0