from django import forms
from django.db import models
from django.core.exceptions import ValidationError

from .enum import Enum


class SelectIntegerField(models.fields.IntegerField):

    description = "An extended IntegerField that validates an Enum"

    def __init__(self, *args, **kwargs):
        self.blueprint = kwargs.pop('blueprint', None)
        if self.blueprint and not isinstance(self.blueprint(), Enum):
            raise TypeError("Blueprint instance must be of type {}.".format(Enum.__name__))
        if self.blueprint is not None:
            kwargs['choices'] = self.blueprint.choices()
            kwargs['db_index'] = kwargs.pop('db_index', True)
            kwargs['default'] = kwargs.pop('default', self.blueprint.DEFAULT)
        super(SelectIntegerField, self).__init__(*args, **kwargs)

    def validate_input(self, value):
        if not self.blueprint.is_in_values(value):
            raise ValidationError("Input for field '{}' is invalid.".format(self.attname))

    @staticmethod
    def validate_fields(meta_fields, dict_fields):
        fields = [field for field in meta_fields if isinstance(field, SelectIntegerField)]
        for field in fields:
            value = dict_fields.get(field.name)
            field.validate_input(value)


# Introspection rules for South
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([
        (
            [], # Class(es) these apply to
            [], # Positional arguments (not used)
                {   # Keyword argument
                    "blueprint": ["blueprint", {"default": None}],
                },
            ),
    ], ["^enumerify\.fields\.SelectIntegerField"])
except:
    pass
