from unittest import TestCase
from tesolib import teso_function


class TestHelloWorld(TestCase):
    def test_get_message(self):
        assert "Tesodev" == teso_function()
