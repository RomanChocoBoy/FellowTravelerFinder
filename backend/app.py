import os
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS

from backend.facade_db import Facade_DB

app = Flask(__name__)
CORS(app)

db = Facade_DB(
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    dbname=os.getenv("DB_NAME", "PIS"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "123456"),
)


def user_to_dict(u):
    return {
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "phone": u.phone,
        "role": u.role,
        "rating": u.rating,
        "status": u.status,
    }


def trip_to_dict(t):
    return {
        "id": t.id,
        "driver_id": t.driver_id,
        "from_place": t.from_place,
        "to_place": t.to_place,
        "date": t.date.isoformat() if isinstance(t.date, datetime) else str(t.date),
        "price": t.price,
        "seats": t.seats,
        "available_seats": t.available_seats,
        "status": t.status,
    }


def booking_to_dict(b):
    return {
        "id": b.id,
        "trip_id": b.trip_id,
        "passenger_id": b.passenger_id,
        "booking_date": b.booking_date.isoformat() if isinstance(b.booking_date, datetime) else str(b.booking_date),
        "status": b.status,
    }


def message_to_dict(m):
    return {
        "id": m.id,
        "trip_id": m.trip_id,
        "sender_id": m.sender_id,
        "recipient_id": m.recipient_id,
        "text": m.text,
        "datetime": m.datetime.isoformat() if isinstance(m.datetime, datetime) else str(m.datetime),
        "is_read": m.is_read,
    }


def complaint_to_dict(c):
    return {
        "id": c.id,
        "sender_id": c.sender_id,
        "recipient_id": c.recipient_id,
        "reason": c.reason,
        "description": c.description,
        "date": c.date.isoformat() if isinstance(c.date, datetime) else str(c.date),
        "status": c.status,
    }


@app.post("/api/auth/register")
def register():
    data = request.get_json() or {}
    try:
        user = db.register_user(
            name=data["name"],
            email=data["email"],
            phone=data.get("phone", ""),
            role=data["role"],
            password=data["password"],
        )
        return jsonify(user_to_dict(user)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.post("/api/auth/login")
def login():
    data = request.get_json() or {}
    user = db.login(data.get("email", ""), data.get("password", ""))
    if not user:
        return jsonify({"error": "Неверный email или пароль, либо аккаунт заблокирован"}), 401
    return jsonify(user_to_dict(user))


@app.get("/api/users")
def list_users():
    users = db.get_all_users()
    return jsonify([user_to_dict(u) for u in users])


@app.get("/api/users/trip-contacts")
def list_trip_contacts():
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return jsonify({"error": "Нужен user_id"}), 400
    return jsonify(db.get_trip_contacts(user_id))


@app.get("/api/chat/threads")
def chat_threads():
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return jsonify({"error": "Нужен user_id"}), 400
    return jsonify(db.get_chat_threads(user_id))


@app.get("/api/trips/search")
def search_trips():
    from_city = request.args.get("from", "")
    to_city = request.args.get("to", "")
    if not from_city or not to_city:
        return jsonify({"error": "Укажите города отправления и назначения"}), 400
    return jsonify(db.search_trips(from_city, to_city))


@app.get("/api/trips/my")
def my_trips():
    driver_id = request.args.get("driver_id", type=int)
    if not driver_id:
        return jsonify({"error": "Нужен driver_id"}), 400
    trips = db.get_my_trips(driver_id)
    return jsonify([trip_to_dict(t) for t in trips])


@app.post("/api/trips")
def publish_trip():
    data = request.get_json() or {}
    try:
        trip = db.publish_trip(
            driver_id=data["driver_id"],
            from_city=data["from_place"],
            to_city=data["to_place"],
            date=data["date"],
            time=data["time"],
            price=float(data["price"]),
            seats=int(data["seats"]),
        )
        return jsonify(trip_to_dict(trip)), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.delete("/api/trips/<int:trip_id>")
def delete_trip(trip_id):
    driver_id = request.args.get("driver_id", type=int)
    if not driver_id:
        return jsonify({"error": "Нужен driver_id"}), 400
    if db.delete_trip(trip_id, driver_id):
        return jsonify({"ok": True})
    return jsonify({"error": "Не удалось удалить поездку"}), 400


@app.get("/api/bookings")
def reservations():
    passenger_id = request.args.get("passenger_id", type=int)
    detailed = request.args.get("detailed", "0") == "1"
    if not passenger_id:
        return jsonify({"error": "Нужен passenger_id"}), 400
    if detailed:
        return jsonify(db.get_reservations_detailed(passenger_id))
    bookings = db.get_reservations(passenger_id)
    return jsonify([booking_to_dict(b) for b in bookings])


@app.get("/api/bookings/pending")
def pending_bookings():
    driver_id = request.args.get("driver_id", type=int)
    if not driver_id:
        return jsonify({"error": "Нужен driver_id"}), 400
    items = db.get_pending_bookings_for_driver(driver_id)
    return jsonify(
        [
            {
                "id": p.id,
                "trip_id": p.trip_id,
                "passenger_id": p.passenger_id,
                "passenger_name": p.passenger_name,
                "booking_date": p.booking_date.isoformat(),
                "status": p.status,
                "from_place": p.from_place,
                "to_place": p.to_place,
            }
            for p in items
        ]
    )


@app.get("/api/bookings/reviewable")
def reviewable_trips():
    passenger_id = request.args.get("passenger_id", type=int)
    if not passenger_id:
        return jsonify({"error": "Нужен passenger_id"}), 400
    return jsonify(db.get_approved_bookings_for_passenger(passenger_id))


@app.post("/api/bookings")
def create_booking():
    data = request.get_json() or {}
    try:
        booking = db.create_booking(int(data["trip_id"]), int(data["passenger_id"]))
        return jsonify(booking_to_dict(booking)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.post("/api/bookings/<int:booking_id>/approve")
def approve_booking(booking_id):
    if db.approve_booking(booking_id):
        return jsonify({"ok": True})
    return jsonify({"error": "Не удалось подтвердить"}), 400


@app.post("/api/bookings/<int:booking_id>/cancel")
def cancel_booking(booking_id):
    if db.cancel_reservation(booking_id):
        return jsonify({"ok": True})
    return jsonify({"error": "Не удалось отменить"}), 400


@app.get("/api/messages")
def get_messages():
    user_id = request.args.get("user_id", type=int)
    other_id = request.args.get("other_id", type=int)
    trip_id = request.args.get("trip_id", type=int)
    if not user_id or not other_id:
        return jsonify({"error": "Нужны user_id и other_id"}), 400
    messages = db.get_messages(user_id, other_id, trip_id)
    return jsonify([message_to_dict(m) for m in messages])


@app.post("/api/messages")
def send_message():
    data = request.get_json() or {}
    trip_id = data.get("trip_id")
    if not trip_id:
        return jsonify({"error": "Сообщение можно отправить только в рамках поездки"}), 400
    ok = db.send_message(
        int(trip_id),
        int(data["sender_id"]),
        int(data["recipient_id"]),
        data["text"],
    )
    if ok:
        return jsonify({"ok": True}), 201
    return jsonify({"error": "Нет общей поездки с этим пользователем"}), 400


@app.post("/api/reviews")
def create_review():
    data = request.get_json() or {}
    ok = db.create_review(
        int(data["trip_id"]),
        int(data["author_id"]),
        int(data["rating"]),
        data.get("comment", ""),
    )
    if ok:
        return jsonify({"ok": True}), 201
    return jsonify({"error": "Отзыв можно оставить только после подтверждённой поездки"}), 400


@app.get("/api/complaints")
def list_complaints():
    detailed = request.args.get("detailed", "1") == "1"
    if detailed:
        return jsonify(db.get_all_complaints_detailed())
    complaints = db.get_all_complaints()
    return jsonify([complaint_to_dict(c) for c in complaints])


@app.post("/api/complaints")
def create_complaint():
    data = request.get_json() or {}
    trip_id = data.get("trip_id")
    c = db.create_complaint(
        int(data["sender_id"]),
        int(data["recipient_id"]),
        data["reason"],
        data.get("description", ""),
        int(trip_id) if trip_id else None,
    )
    if c:
        return jsonify(complaint_to_dict(c)), 201
    return jsonify({"error": "Жалобу можно подать только на участника общей поездки"}), 400


@app.post("/api/complaints/<int:complaint_id>/approve")
def approve_complaint(complaint_id):
    if db.approve_complaint(complaint_id):
        return jsonify({"ok": True})
    return jsonify({"error": "Ошибка"}), 400


@app.post("/api/complaints/<int:complaint_id>/reject")
def reject_complaint(complaint_id):
    if db.reject_complaint(complaint_id):
        return jsonify({"ok": True})
    return jsonify({"error": "Ошибка"}), 400


@app.post("/api/users/<int:user_id>/block")
def block_user(user_id):
    if db.block_user(user_id):
        return jsonify({"ok": True})
    return jsonify({"error": "Ошибка"}), 400


@app.post("/api/users/<int:user_id>/unblock")
def unblock_user(user_id):
    if db.unblock_user(user_id):
        return jsonify({"ok": True})
    return jsonify({"error": "Ошибка"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
