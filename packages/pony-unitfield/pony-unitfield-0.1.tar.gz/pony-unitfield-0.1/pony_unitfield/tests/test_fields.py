from django.test import TestCase
from pony_unitfield.tests.testproject import models


class GetDisplayTestCase(TestCase):
    def test_default(self):
        obj = models.Obj(default=42)
        display = obj.get_default_display()
        self.assertEqual(display, '42.000 foo')

    def test_no_decimal(self):
        obj = models.Obj(no_decimal=42)
        display = obj.get_no_decimal_display()
        self.assertEqual(display, '42 bar')

    def test_one_decimal(self):
        obj = models.Obj(one_decimal=42)
        display = obj.get_one_decimal_display()
        self.assertEqual(display, '42.0 ham')

    def test_non_spaced(self):
        obj = models.Obj(non_spaced=42)
        display = obj.get_non_spaced_display()
        self.assertEqual(display, '42.000bone')
