"""Демо-сценарий без веб-интерфейса. Для UI запустите backend и frontend (см. README)."""
from backend.facade_db import Facade_DB

db = Facade_DB()

passenger = db.register_user("Иван Петров", "ivan1@mail.ru", "+79991234567", "passenger", "pass123")
driver = db.register_user("Сергей Водитель", "sergey1@mail.ru", "+79997654321", "reader", "pass123")
print(f"Созданы: {passenger.name}, {driver.name}")

trip = db.publish_trip(
    driver_id=driver.id,
    from_city="Красноярск",
    to_city="Новосибирск",
    date="2026-04-15",
    time="10:00",
    price=1500.0,
    seats=3,
)
print(f"Поездка: {trip.from_place} → {trip.to_place}")

trips = db.search_trips("Красноярск", "Новосибирск", "2026-04-15")
print(f"Найдено: {len(trips)}")

booking = db.create_booking(trip.id, passenger.id)
db.approve_booking(booking.id)
print("Бронирование подтверждено")

db.send_message(trip.id, passenger.id, driver.id, "Здравствуйте!")
db.create_review(trip.id, passenger.id, 5, "Отличная поездка!")

driver = db.get_user_by_id(driver.id)
print(f"Рейтинг водителя: {driver.rating}")

db.close()
