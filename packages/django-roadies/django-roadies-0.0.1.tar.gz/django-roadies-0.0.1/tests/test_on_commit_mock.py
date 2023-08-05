from __future__ import absolute_import, print_function, unicode_literals


from django.test import TestCase
from django_roadies.test import mock, OnCommitMock

from .models import do_it_later


class TestOnCommitMock(TestCase):

    def test_self_is_returned_on_enter(self):
        with OnCommitMock('tests.models.transaction') as on_commit:
            self.assertIsInstance(on_commit, OnCommitMock)

    def test_add_a_function(self):
        func = mock.MagicMock()
        with OnCommitMock('tests.models.transaction') as on_commit:
            do_it_later(func)
            self.assertTrue(func in on_commit.functions)

    def test_function_called_on_exit(self):
        func = mock.MagicMock()
        with OnCommitMock('tests.models.transaction'):
            do_it_later(func)
            self.assertFalse(func.called)
        self.assertTrue(func.called)

    def test_trigger_idempotence(self):
        func = mock.MagicMock()
        with OnCommitMock('tests.models.transaction') as on_commit:
            do_it_later(func)
            self.assertFalse(func.called)
            on_commit.trigger()
            self.assertTrue(func.called)
            self.assertEqual(func.call_count, 1)
            on_commit.trigger()
            self.assertEqual(func.call_count, 1)

    def test_raises_on_incorrect_target(self):
        self.assertRaises(TypeError, OnCommitMock, 1)
