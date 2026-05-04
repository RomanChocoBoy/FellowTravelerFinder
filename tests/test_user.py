from tests.base_test_case import BaseDBTestCase


class TestUser(BaseDBTestCase):
    def test_create_user(self):
        user = self.db.create_user("Ivan", "ivan@test.local", "+70000000001", "passenger")
        self.assertIsNotNone(user.id)
        self.assertEqual(user.name, "Ivan")
        self.assertEqual(user.status, "active")

    def test_get_all_users(self):
        self.db.create_user("User1", "user1@test.local", "+70000000011", "passenger")
        self.db.create_user("User2", "user2@test.local", "+70000000012", "reader")

        users = self.db.get_all_users()
        self.assertEqual(len(users), 2)

    def test_block_and_unblock_user(self):
        user = self.db.create_user("Temp", "temp@test.local", "+70000000021", "passenger")

        blocked = self.db.block_user(user.id)
        self.assertTrue(blocked)
        users = self.db.get_all_users()
        self.assertEqual(users[0].status, "blocked")

        unblocked = self.db.unblock_user(user.id)
        self.assertTrue(unblocked)
        users = self.db.get_all_users()
        self.assertEqual(users[0].status, "active")
