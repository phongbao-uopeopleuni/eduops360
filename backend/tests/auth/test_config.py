import unittest

from app.core.config import Settings


class LocalCookieConfigTest(unittest.TestCase):
    def test_local_environment_disables_secure_cookie(self):
        settings = Settings(environment="local")
        self.assertFalse(settings.session_cookie_secure)

    def test_test_environment_disables_secure_cookie(self):
        settings = Settings(environment="test")
        self.assertFalse(settings.session_cookie_secure)

    def test_local_environment_preserves_explicit_secure_cookie(self):
        settings = Settings(environment="local", session_cookie_secure=True)
        self.assertTrue(settings.session_cookie_secure)


if __name__ == "__main__":
    unittest.main()
