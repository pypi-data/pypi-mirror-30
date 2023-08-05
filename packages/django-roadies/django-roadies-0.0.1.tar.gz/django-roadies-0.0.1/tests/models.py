from __future__ import absolute_import, print_function, unicode_literals

from django.db import models, transaction
from django_roadies.test import TempModel


class ThingWithName(models.Model):
    """A contrived abstract model."""

    name = models.CharField(max_length=16)

    class Meta:
        abstract = True


class Person(TempModel, ThingWithName):
    pass


class Place(TempModel, ThingWithName):

    latitude = models.FloatField()
    longitude = models.FloatField()


def do_it_later(func):
    transaction.on_commit(func)
