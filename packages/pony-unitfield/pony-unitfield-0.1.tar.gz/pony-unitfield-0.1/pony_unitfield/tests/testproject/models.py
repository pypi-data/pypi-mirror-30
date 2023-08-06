from django.db import models
from pony_unitfield.fields import UnitField


class Obj(models.Model):
    default = UnitField(unit='foo', null=True)

    no_decimal = UnitField(unit='bar', decimal=0, null=True)
    one_decimal = UnitField(unit='ham', decimal=1, null=True)

    non_spaced = UnitField(unit='bone', spaced_display=False, null=True)
