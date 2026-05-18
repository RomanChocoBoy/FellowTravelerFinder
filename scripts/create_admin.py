
from backend.facade_db import Facade_DB

db = Facade_DB()
user = db.register_user("Админ", "admin@tripfinder.com", "+70000000000", "admin", "admin123")
print(f"Админ создан: {user.email} / пароль admin123")
db.close()
