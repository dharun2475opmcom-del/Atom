"""
Unit tests for AquaGuard authentication and database integration.
"""

import os
import unittest
from pathlib import Path
from src.database import (
    init_db,
    create_user,
    authenticate_user,
    get_user_stats,
    hash_password,
    verify_password
)

TEST_DB_PATH = Path(__file__).resolve().parent / "data" / "test_auth.db"


class TestAquaGuardAuth(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if TEST_DB_PATH.exists():
            os.remove(TEST_DB_PATH)
        init_db(TEST_DB_PATH)

    @classmethod
    def tearDownClass(cls):
        if TEST_DB_PATH.exists():
            os.remove(TEST_DB_PATH)

    def test_default_admin_created(self):
        """Ensure initial seed created the default admin account."""
        success, user, msg = authenticate_user("admin", "Aquaguard@2026", db_path=TEST_DB_PATH)
        self.assertTrue(success)
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "admin")
        self.assertEqual(user["role"], "admin")

    def test_create_new_user_success(self):
        """Ensure a new user can sign up properly."""
        success, msg = create_user(
            username="john_doe",
            email="john@domain.com",
            password="SecurePassword123",
            full_name="John Doe",
            role="operator",
            db_path=TEST_DB_PATH
        )
        self.assertTrue(success, msg)

        # Authenticate with username
        auth_ok, user_info, _ = authenticate_user("john_doe", "SecurePassword123", db_path=TEST_DB_PATH)
        self.assertTrue(auth_ok)
        self.assertEqual(user_info["full_name"], "John Doe")

        # Authenticate with email (case insensitive)
        auth_ok2, user_info2, _ = authenticate_user("JOHN@DOMAIN.COM", "SecurePassword123", db_path=TEST_DB_PATH)
        self.assertTrue(auth_ok2)
        self.assertEqual(user_info2["username"], "john_doe")

    def test_prevent_duplicate_username_and_email(self):
        """Ensure registration rejects duplicate username and email."""
        # Duplicate username
        s1, m1 = create_user("john_doe", "other@domain.com", "Password123", db_path=TEST_DB_PATH)
        self.assertFalse(s1)
        self.assertIn("already taken", m1)

        # Duplicate email
        s2, m2 = create_user("new_user", "john@domain.com", "Password123", db_path=TEST_DB_PATH)
        self.assertFalse(s2)
        self.assertIn("already registered", m2)

    def test_invalid_credentials(self):
        """Ensure authentication fails with wrong credentials."""
        ok, user, msg = authenticate_user("john_doe", "WrongPassword", db_path=TEST_DB_PATH)
        self.assertFalse(ok)
        self.assertIsNone(user)

        ok2, user2, msg2 = authenticate_user("nonexistent_user", "AnyPassword", db_path=TEST_DB_PATH)
        self.assertFalse(ok2)

    def test_validation_rules(self):
        """Test username, email, and password validation checks."""
        # Short password
        ok, msg = create_user("valid_user", "valid@email.com", "123", db_path=TEST_DB_PATH)
        self.assertFalse(ok)
        self.assertIn("at least 6 characters", msg)

        # Invalid email
        ok2, msg2 = create_user("valid_user", "not-an-email", "Password123", db_path=TEST_DB_PATH)
        self.assertFalse(ok2)
        self.assertIn("Invalid email", msg2)

        # Short username
        ok3, msg3 = create_user("ab", "valid2@email.com", "Password123", db_path=TEST_DB_PATH)
        self.assertFalse(ok3)
        self.assertIn("between 3 and 30 characters", msg3)

    def test_user_stats_and_audit(self):
        """Verify user stats and activity audit logging."""
        stats = get_user_stats(db_path=TEST_DB_PATH)
        self.assertGreaterEqual(stats["total_users"], 2)
        self.assertGreaterEqual(len(stats["recent_activity"]), 1)


if __name__ == "__main__":
    unittest.main()

