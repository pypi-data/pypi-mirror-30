# Django Enumerify #

## Installation ##

```
pip install django-enumerify
```

## Usage ##

```
#!python

# .../app/enums.py

from django.utils.translation import gettext as _

from enumerify.enum import Enum

class GroupKind(Enum):
    PUBLIC = 0
    PRIVATE = 1

    i18n = (
        _('Public'),
        _('Private'),
    )

# .../app/models.py

from django.db import models

from enumerify import fields

from .enums import GroupKind

class Group(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.TextField()
    kind = fields.SelectIntegerField(blueprint=GroupKind, default=GroupKind.PUBLIC)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __unicode__(self):
        return u"Group: %s" % self.title
    
```

## Tests ##

```
#!python
$ python testapp/tests/runtests.py
```