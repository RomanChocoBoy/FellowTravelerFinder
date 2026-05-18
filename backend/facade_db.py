import os

os.environ.setdefault("PGCLIENTENCODING", "UTF8")

from dataclasses import dataclass
from datetime import date as dt_date
from datetime import datetime

import psycopg
from werkzeug.security import check_password_hash, generate_password_hash


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
class PendingBooking:
    id: int
    trip_id: int
    passenger_id: int
    passenger_name: str
    booking_date: datetime
    status: str
    from_place: str
    to_place: str


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


def normalize_city(city: str) -> str:
    """Единый вид города: без лишних пробелов, с заглавной буквы."""
    return " ".join(part.capitalize() for part in city.strip().split())


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

    def register_user(self, name: str, email: str, phone: str, role: str, password: str) -> User:
        pwd_hash = generate_password_hash(password)
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO "User" (name, email, phone, role, password_hash)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, name, email, phone, role, rating, status;
                """,
                (name, email, phone, role, pwd_hash),
            )
            return self._map_user(cur.fetchone())

    def create_user(self, name: str, email: str, phone: str, role: str, password: str = "password") -> User:
        """Для тестов и совместимости со старым кодом."""
        return self.register_user(name, email, phone, role, password)

    def login(self, email: str, password: str) -> User | None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, email, phone, role, rating, status, password_hash
                FROM "User"
                WHERE email = %s;
                """,
                (email,),
            )
            row = cur.fetchone()
            if not row or not row[7]:
                return None
            if not check_password_hash(row[7], password):
                return None
            user = self._map_user(row[:7])
            if user.status == "blocked":
                return None
            return user

    def get_user_by_id(self, user_id: int) -> User | None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, email, phone, role, rating, status
                FROM "User"
                WHERE id = %s;
                """,
                (user_id,),
            )
            row = cur.fetchone()
            return self._map_user(row) if row else None

    def get_all_users(self) -> list[User]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, email, phone, role, rating, status
                FROM "User"
                ORDER BY id;
                """
            )
            return [self._map_user(row) for row in cur.fetchall()]

    def get_trip_contacts(self, user_id: int) -> list[dict]:
        """Пользователи, с которыми есть общая поездка (бронь pending или approved)."""
        user = self.get_user_by_id(user_id)
        if not user:
            return []

        with self.conn.cursor() as cur:
            if user.role == "passenger":
                cur.execute(
                    """
                    SELECT DISTINCT u.id, u.name, u.role, u.rating,
                           t.id, t.from_location, t.to_location, t.date
                    FROM Booking b
                    JOIN Trip t ON b.trip_id = t.id
                    JOIN "User" u ON t.driver_id = u.id
                    WHERE b.passenger_id = %s
                      AND b.status IN ('pending', 'approved')
                      AND t.status = 'active'
                    ORDER BY t.date DESC;
                    """,
                    (user_id,),
                )
            elif user.role == "reader":
                cur.execute(
                    """
                    SELECT DISTINCT u.id, u.name, u.role, u.rating,
                           t.id, t.from_location, t.to_location, t.date
                    FROM Booking b
                    JOIN Trip t ON b.trip_id = t.id
                    JOIN "User" u ON b.passenger_id = u.id
                    WHERE t.driver_id = %s
                      AND b.status IN ('pending', 'approved')
                      AND t.status = 'active'
                    ORDER BY t.date DESC;
                    """,
                    (user_id,),
                )
            else:
                return []

            return [
                {
                    "user_id": row[0],
                    "user_name": row[1],
                    "user_role": row[2],
                    "user_rating": float(row[3]),
                    "trip_id": row[4],
                    "from_place": row[5],
                    "to_place": row[6],
                    "date": row[7].isoformat() if row[7] else None,
                }
                for row in cur.fetchall()
            ]

    def users_share_trip(self, user_id: int, other_id: int, trip_id: int | None = None) -> bool:
        contacts = self.get_trip_contacts(user_id)
        for c in contacts:
            if c["user_id"] == other_id and (trip_id is None or c["trip_id"] == trip_id):
                return True
        return False

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
        trip_day = datetime.strptime(date, "%Y-%m-%d").date()
        if trip_day < dt_date.today():
            raise ValueError("Дата поездки не может быть раньше сегодняшнего дня")

        from_city = normalize_city(from_city)
        to_city = normalize_city(to_city)
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

    def search_trips(self, from_city: str, to_city: str) -> list[dict]:
        from_city = normalize_city(from_city)
        to_city = normalize_city(to_city)

        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT t.id, t.driver_id, t.from_location, t.to_location, t.date,
                       t.price, t.seats, t.available_seats, t.status,
                       u.name, u.rating
                FROM Trip t
                JOIN "User" u ON t.driver_id = u.id
                WHERE LOWER(TRIM(t.from_location)) = LOWER(%s)
                  AND LOWER(TRIM(t.to_location)) = LOWER(%s)
                  AND t.status = 'active'
                  AND t.available_seats > 0
                  AND t.date >= CURRENT_DATE
                ORDER BY t.date;
                """,
                (from_city, to_city),
            )
            return [
                {
                    "id": row[0],
                    "driver_id": row[1],
                    "from_place": row[2],
                    "to_place": row[3],
                    "date": row[4].isoformat() if row[4] else None,
                    "price": float(row[5]),
                    "seats": row[6],
                    "available_seats": row[7],
                    "status": row[8],
                    "driver_name": row[9],
                    "driver_rating": float(row[10]),
                }
                for row in cur.fetchall()
            ]

    def delete_trip(self, trip_id: int, driver_id: int) -> bool:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                UPDATE Trip SET status = 'cancelled'
                WHERE id = %s AND driver_id = %s AND status = 'active';
                """,
                (trip_id, driver_id),
            )
            if cur.rowcount == 0:
                return False
            cur.execute(
                """
                UPDATE Booking SET status = 'cancelled'
                WHERE trip_id = %s AND status IN ('pending', 'approved');
                """,
                (trip_id,),
            )
            return True

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
            return [self._map_trip(row) for row in cur.fetchall()]

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
            cur.execute("SELECT status, trip_id FROM Booking WHERE id = %s;", (booking_id,))
            row = cur.fetchone()
            if not row or row[0] != "pending":
                return False
            cur.execute('UPDATE Booking SET status = %s WHERE id = %s;', ("approved", booking_id))
            cur.execute(
                """
                UPDATE Trip
                SET available_seats = available_seats - 1
                WHERE id = %s;
                """,
                (row[1],),
            )
            return True

    def cancel_reservation(self, booking_id: int) -> bool:
        with self.conn.cursor() as cur:
            cur.execute("SELECT status, trip_id FROM Booking WHERE id = %s;", (booking_id,))
            row = cur.fetchone()
            if not row:
                return False
            was_approved = row[0] == "approved"
            cur.execute('UPDATE Booking SET status = %s WHERE id = %s;', ("cancelled", booking_id))
            if was_approved:
                cur.execute(
                    """
                    UPDATE Trip
                    SET available_seats = available_seats + 1
                    WHERE id = %s;
                    """,
                    (row[1],),
                )
            return True

    def get_reservations(self, passenger_id: int) -> list[Booking]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, trip_id, passenger_id, booking_date, status
                FROM Booking
                WHERE passenger_id = %s
                ORDER BY booking_date DESC;
                """,
                (passenger_id,),
            )
            return [self._map_booking(row) for row in cur.fetchall()]

    def get_reservations_detailed(self, passenger_id: int) -> list[dict]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT b.id, b.trip_id, b.status, b.booking_date,
                       t.from_location, t.to_location, t.date, t.price,
                       u.name, u.rating
                FROM Booking b
                JOIN Trip t ON b.trip_id = t.id
                JOIN "User" u ON t.driver_id = u.id
                WHERE b.passenger_id = %s
                ORDER BY b.booking_date DESC;
                """,
                (passenger_id,),
            )
            return [
                {
                    "id": row[0],
                    "trip_id": row[1],
                    "status": row[2],
                    "booking_date": row[3].isoformat() if row[3] else None,
                    "from_place": row[4],
                    "to_place": row[5],
                    "trip_date": row[6].isoformat() if row[6] else None,
                    "price": float(row[7]),
                    "driver_name": row[8],
                    "driver_rating": float(row[9]),
                }
                for row in cur.fetchall()
            ]

    def get_pending_bookings_for_driver(self, driver_id: int) -> list[PendingBooking]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT b.id, b.trip_id, b.passenger_id, u.name, b.booking_date, b.status,
                       t.from_location, t.to_location
                FROM Booking b
                JOIN Trip t ON b.trip_id = t.id
                JOIN "User" u ON b.passenger_id = u.id
                WHERE t.driver_id = %s AND b.status = 'pending'
                ORDER BY b.booking_date;
                """,
                (driver_id,),
            )
            return [
                PendingBooking(
                    id=row[0],
                    trip_id=row[1],
                    passenger_id=row[2],
                    passenger_name=row[3],
                    booking_date=row[4],
                    status=row[5],
                    from_place=row[6],
                    to_place=row[7],
                )
                for row in cur.fetchall()
            ]

    def get_approved_bookings_for_passenger(self, passenger_id: int) -> list[dict]:
        """Поездки с подтверждённым бронированием — для отзывов."""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT DISTINCT ON (b.trip_id)
                       b.trip_id, t.from_location, t.to_location, t.date, t.driver_id
                FROM Booking b
                JOIN Trip t ON b.trip_id = t.id
                WHERE b.passenger_id = %s AND b.status = 'approved'
                ORDER BY b.trip_id, t.date DESC;
                """,
                (passenger_id,),
            )
            return [
                {
                    "trip_id": row[0],
                    "from_place": row[1],
                    "to_place": row[2],
                    "date": row[3].isoformat() if row[3] else None,
                    "driver_id": row[4],
                }
                for row in cur.fetchall()
            ]

    def send_message(self, trip_id: int | None, sender_id: int, recipient_id: int, text: str) -> bool:
        if not trip_id or not self.users_share_trip(sender_id, recipient_id, trip_id):
            return False
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
            return [self._map_message(row) for row in cur.fetchall()]

    def create_review(self, trip_id: int, author_id: int, rating: int, comment: str) -> bool:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT 1 FROM Booking
                WHERE trip_id = %s AND passenger_id = %s AND status = 'approved'
                LIMIT 1;
                """,
                (trip_id, author_id),
            )
            if not cur.fetchone():
                return False

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

    def create_complaint(
        self, sender_id: int, recipient_id: int, reason: str, description: str, trip_id: int | None = None
    ) -> Complaint | None:
        if not self.users_share_trip(sender_id, recipient_id, trip_id):
            return None
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
            return [self._map_complaint(row) for row in cur.fetchall()]

    def get_all_complaints_detailed(self) -> list[dict]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT c.id, c.sender_id, c.recipient_id, c.reason, c.description, c.date, c.status,
                       s.name, s.email, r.name, r.email
                FROM Complaint c
                JOIN "User" s ON c.sender_id = s.id
                JOIN "User" r ON c.recipient_id = r.id
                ORDER BY c.date DESC;
                """
            )
            return [
                {
                    "id": row[0],
                    "sender_id": row[1],
                    "recipient_id": row[2],
                    "reason": row[3],
                    "description": row[4],
                    "date": row[5].isoformat() if row[5] else None,
                    "status": row[6],
                    "sender_name": row[7],
                    "sender_email": row[8],
                    "recipient_name": row[9],
                    "recipient_email": row[10],
                }
                for row in cur.fetchall()
            ]

    def get_chat_threads(self, user_id: int) -> list[dict]:
        contacts = self.get_trip_contacts(user_id)
        threads = []
        for c in contacts:
            messages = self.get_messages(user_id, c["user_id"], c["trip_id"])
            last = messages[-1] if messages else None
            threads.append(
                {
                    **c,
                    "last_message": last.text if last else None,
                    "last_time": last.datetime.isoformat() if last else None,
                }
            )
        return threads

    def approve_complaint(self, complaint_id: int) -> bool:
        with self.conn.cursor() as cur:
            cur.execute('UPDATE Complaint SET status = %s WHERE id = %s;', ("approved", complaint_id))
            return cur.rowcount > 0

    def reject_complaint(self, complaint_id: int) -> bool:
        with self.conn.cursor() as cur:
            cur.execute('UPDATE Complaint SET status = %s WHERE id = %s;', ("rejected", complaint_id))
            return cur.rowcount > 0
