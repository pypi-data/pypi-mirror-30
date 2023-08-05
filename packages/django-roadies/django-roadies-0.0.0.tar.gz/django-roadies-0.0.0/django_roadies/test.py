from __future__ import absolute_import, print_function, unicode_literals

try:
    from unittest import mock
except ImportError:  # pragma: no cover
    import mock

from django.db import connection, models
from django.utils import six
from django.test import TestCase as DjangoTestCase


class TempModel(models.Model):
    """Abstract base model intended to support the testing of other abstract models.

    Usage:
        # in a models.py module
        class MyAbstractModel(models.Model):
            # fields
            ...

            class Meta:
                abstract = True

        # in tests
        from django_roadies.test import TempModel, TestCase
        from myapp.models import MyAbstractModel

        class MyConcreteTestModel(TempModel, MyAbstractModel):
            # N.B. the TempModel must be first in the set of parents.
            # proceed with the concrete implementation
            ...

        class TestMyAbstractModel(TestCase):

            TEST_MODELS = (MyConcreteTestModel, )

            def test_filtering(self):
                MyConcreteTestModel.objects.filter(...)
    """

    class Meta:
        abstract = True
        app_label = 'django_roadies'


class TestCase(DjangoTestCase):
    """Override the django.test.TestCase to setup test models.

    Add a class attribute called TEST_MODELS to the TestCase subclass.
    Usage:

        class MyTests(TestCase):

            TEST_MODELS = [TestOnlyModel,]

    This is useful when testing abstract base classes.
    """

    @classmethod
    def setUpClass(cls, *args, **kwargs):
        """Override setUpClass to created necessary tables."""
        super(TestCase, cls).setUpClass(*args, **kwargs)
        setup_test_models(*cls.TEST_MODELS)


def setup_test_models(*models):
    """Use this method to create new tables in the test db for test models.

    Must be used in the setUpClass part of the django.test.TestCase subclass.
    :param models:
    :return:
    """
    with connection.schema_editor(atomic=True) as schema_editor:
        for model in set(models):
            schema_editor.create_model(model)


class OnCommitMock(object):
    """ContextManager needed to avoid using TransactionTestCase.

    TransactionTestCase significantly slows down the execution of the tests.

    Usage:

        target = 'reelio.conversation.receivers.transaction'
        with EagerOnCommit(target):
            ...execute some method that hits the target...

        # upon exiting any functions that were added to the target via on_commit
        # will be executed.

    Alternate Usage:

        target = 'reelio.conversation.receivers.transaction'
        with EagerOnCommit(target) as transaction:
            ...execute some method that hits the target...

            # manually trigger the the execution of any functions added to the
            # target via on_commit
            transaction.trigger()

        # once the eager on commit context has exitted the trigger method will do
        # nothing.
    """

    def __init__(self, target):
        self.functions = []
        self.results = []
        self.called = False
        self.triggered = False
        if not isinstance(target, six.string_types):
            raise TypeError(
                'target should be a dotpath pointing to a transaction object.'
            )
        self.target = target

    def add(self, func):
        """Add the given function to the context's functions list.

        Should only be used to replace the transaction's on_commit
        method. This then allows greater control of when to trigger those added
        functions.
        """
        self.called = True
        self.functions.append(func)

    def trigger(self):
        """Trigger the execution of all functions listed in self.functions.

        Once triggered the functions will not be executed when calling this method
        again i.e. this method is idempotent.
        """
        if not self.triggered:
            for func in self.functions:
                result = func()
                self.add_result(result)
            self.triggered = True

    def add_result(self, result):
        """Override this method to check the result and then add it to self.results."""
        self.results.append(result)

    def __enter__(self):
        """Patch the target and set it's on_commit method to self.add."""
        self.transaction_patch = mock.patch(self.target)
        transaction_mock = self.transaction_patch.start()
        transaction_mock.on_commit = self.add
        return self

    def __exit__(self, *args, **kwargs):
        """Trigger the functions and ensure the patch has been stopped."""
        self.trigger()
        self.transaction_patch.stop()
