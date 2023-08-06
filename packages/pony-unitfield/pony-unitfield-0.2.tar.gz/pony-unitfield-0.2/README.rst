Pony UnitField
==============

This project aims to add helpers for FloatField with:

- Specify unit (meters, feet, bytes) as field's metadata
- Specify a number of decimal (without ``DecimalField``)
- Add ``get_FIELD_display`` method on model


Example
-------

::

    from django.db import models
    from pony_unitfield.fields import UnitField
    
    class MyModel(models.Model):
        default = UnitField(unit='foo', null=True)

        no_decimal = UnitField(unit='bar', decimal=0, null=True)
        one_decimal = UnitField(unit='ham', decimal=1, null=True)

        non_spaced = UnitField(unit='bone', spaced_display=False, null=True)
