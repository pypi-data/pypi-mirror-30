from unittest import TestCase


from ..client import start_session

class TestImport(TestCase):
    def test_client_import(self):
        self.assertIsNotNone(start_session)
