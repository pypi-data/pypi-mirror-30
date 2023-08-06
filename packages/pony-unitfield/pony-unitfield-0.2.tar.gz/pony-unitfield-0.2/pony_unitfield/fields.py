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
    template += '{:d}' if field.decimals == 0 else '{:.%sf}' % field.decimals
    template += ' ' if field.spaced_display else ''
    template += '{!s:s}'
    return template.format(value, field.unit)


class UnitFieldMixin(object):
    """
    Mixin adding all needed behaviors.
    """
    decimals = None

    def __init__(self, unit, decimals=3, spaced_display=True, *args, **kwargs):
        super(UnitFieldMixin, self).__init__(*args, **kwargs)
        self.unit = unit
        self.decimals = self.decimals if self.decimals is not None else decimals
        self.spaced_display = spaced_display

    def deconstruct(self):
        name, path, args, kwargs = super(UnitFieldMixin, self).deconstruct()
        args.extend(('unit',))
        kwargs.update(decimals=3, spaced_display=True)
        return name, path, args, kwargs

    def contribute_to_class(self, cls, name, private_only=False):
        super(UnitFieldMixin, self).contribute_to_class(cls, name, private_only)
        setattr(cls, 'get_%s_display' % self.name,
                partialmethod(_get_FIELD_display, field=self))


class UnitField(UnitFieldMixin, fields.FloatField):
    """FloatField with unit."""


class IntegerUnitField(UnitFieldMixin, fields.IntegerField):
    """IntegerField with unit."""
    decimals = 0

    def deconstruct(self):
        name, path, args, kwargs = super(IntegerUnitField, self).deconstruct()
        kwargs.pop('decimals')
        return name, path, args, kwargs
