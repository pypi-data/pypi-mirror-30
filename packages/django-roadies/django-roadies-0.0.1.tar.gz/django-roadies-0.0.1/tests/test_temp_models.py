from __future__ import absolute_import, print_function, unicode_literals

from django.db.utils import OperationalError
from django_roadies.test import TempModel, TestCase

from .models import Person, Place, ThingWithName


class TestTempModels(TestCase):

    TEST_MODELS = (Person, Place, Person)

    def test_model_inheritance(self):
        self.assertIsInstance(Person(), ThingWithName)
        self.assertIsInstance(Person(), TempModel)

    def test_model_save(self):
        person = Person(name='bob')
        self.assertIsNone(person.pk)
        person.save()
        self.assertIsNotNone(person.pk)


class TestTempModelsRepeated(TestCase):

    TEST_MODELS = (Place, )

    def test_place_save(self):
        place = Place(name='bob', latitude=0, longitude=0)
        self.assertIsNone(place.pk)
        place.save()
        self.assertIsNotNone(place.pk)

    def test_person_save_raises(self):
        # Person is not defined within the TestCase and is therefore out of scope
        person = Person(name='bob')
        self.assertRaises(OperationalError, person.save)


class TestBackwardsCompatibility(TestCase):

    def test_success(self):
        self.assertTrue(True)
