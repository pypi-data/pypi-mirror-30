from django.db import models
from pony_unitfield.fields import UnitField, IntegerUnitField


class Obj(models.Model):
    default = UnitField(unit='foo', null=True)

    no_decimal = UnitField(unit='bar', decimals=0, null=True)
    one_decimal = UnitField(unit='ham', decimals=1, null=True)

    non_spaced = UnitField(unit='bone', spaced_display=False, null=True)

    integer = IntegerUnitField(unit='CFA', null=True)
