try:
    from functools import partialmethod
except ImportError:
    from django.utils.functional import curry as partialmethod

from django.db.models import fields


def _get_FIELD_display(self, field):
    value = getattr(self, field.attname)
    if value is None:
        return
    template = ''
    template += '{:d}' if field.decimal == 0 else '{:.%sf}' % field.decimal
    template += ' ' if field.spaced_display else ''
    template += '{!s:s}'
    return template.format(value, field.unit)


class UnitField(fields.FloatField):
    def __init__(self, unit, decimal=3, spaced_display=True, *args, **kwargs):
        super(UnitField, self).__init__(*args, **kwargs)
        self.unit = unit
        self.decimal = decimal
        self.spaced_display = spaced_display

    def deconstruct(self):
        name, path, args, kwargs = super(UnitField, self).deconstruct()
        args.extend(('unit',))
        kwargs.update(decimal=3, spaced_display=True)
        return name, path, args, kwargs

    def contribute_to_class(self, cls, name, private_only=False):
        super(UnitField, self).contribute_to_class(cls, name, private_only)
        setattr(cls, 'get_%s_display' % self.name,
                partialmethod(_get_FIELD_display, field=self))
