from facade_db import Facade_DB


db = Facade_DB()


passenger = db.create_user("Иван Петров", "ivan1@mail.ru", "+79991234567", "passenger")
driver = db.create_user("Сергей Водитель", "sergey1@mail.ru", "+79997654321", "reader")
admin = db.create_user("Админ", "admin1@tripfinder.com", "", "admin")

print(f"Созданы пользователи: {passenger.name}, {driver.name}, {admin.name}")


trip = db.publish_trip(
    driver_id=driver.id,
    from_city="Красноярск",
    to_city="Новосибирск",
    date="2026-04-15",
    time="10:00",
    price=1500.0,
    seats=3
)
print(f"Поездка опубликована: {trip.from_place} → {trip.to_place}")


trips = db.search_trips("Красноярск", "Новосибирск", "2026-04-15")
print(f"Найдено поездок: {len(trips)}")


booking = db.create_booking(trip.id, passenger.id)
print(f"Бронирование создано, статус: {booking.status}")


db.approve_booking(booking.id)
print(f"Бронирование подтверждено")


db.send_message(trip.id, passenger.id, driver.id, "Здравствуйте! Когда выезжаем?")
print("Сообщение отправлено")


messages = db.get_messages(passenger.id, driver.id)
print(f"Сообщений в чате: {len(messages)}")


db.create_review(trip.id, passenger.id, 5, "Отличная поездка!")
print("Отзыв оставлен")


print(f"Рейтинг водителя: {driver.rating}")


all_users = db.get_all_users()
print(f"Всего пользователей: {len(all_users)}")

db.close()