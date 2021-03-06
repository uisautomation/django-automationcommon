import datetime
import logging

import mock

from django.contrib.auth.models import User, AnonymousUser
from testfixtures import LogCapture

from automationcommon.models import (
    set_local_user, Audit, ModelChangeMixin, clear_local_user, LOCAL_USER_WARNING
)
from automationcommon.tests.utils import UnitTestCase


class FakeModel:
    pk = 1

    def save(self, *args, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        pass


class FakeMeta:
    def __init__(self):
        self.fields = {
            'id': 1,
            'name': 'the round window',
            'description': "it's round",
            'other': True
        }

    def get_field(self, name):
        return self.fields[name]


class FakeState:
    adding = False


class TestModel(ModelChangeMixin, FakeModel):

    def __init__(self, *args, **kwargs):
        self._meta = FakeMeta()
        self._state = FakeState()
        super(TestModel, self).__init__(*args, **kwargs)

    @property
    def _dict(self):
        return self._meta.fields.copy()

    def audit_compare(self, field, old, new):
        if isinstance(field, bool):
            return False
        return super(TestModel, self).audit_compare(field, old, new)


class ModelsTests(UnitTestCase):

    @classmethod
    def setUpTestData(cls):
        with mock.patch('ucamlookup.utils.PersonMethods') as mocked_pm:
            mocked_pm.return_value.getPerson.return_value = None
            cls.user = User.objects.create(username="it123")

    def setUp(self):
        set_local_user(self.user)
        self.test_model = TestModel()

    def test_audit_no_user(self):

        clear_local_user()

        with LogCapture(level=logging.INFO) as log_capture:

            # test
            self.test_model._meta.fields.update({'description': "it's a round window"})
            self.test_model.save()

            # check
            self.assertEqual(0, Audit.objects.count())
            log_capture.check((
                'automationcommon', 'WARNING',
                "Don't know who made this change: (model=TestModel:1, field=description, "
                "old='it's round', new='it's a round window')"
            ), (
                'automationcommon', 'WARNING', LOCAL_USER_WARNING
            ))

    def test_audit_single_change(self):

        start = datetime.datetime.now()

        # test
        self.test_model._meta.fields.update({'description': "it's a round window"})
        self.test_model.save()

        # check
        self.assertEqual(1, Audit.objects.count())
        audit = Audit.objects.all().first()
        self.assertLessEqual(start, audit.when)
        self.assertEqual(self.user, audit.who)
        self.assertEqual('TestModel', audit.model)
        self.assertEqual('1', audit.model_pk)
        self.assertEqual('description', audit.field)
        self.assertEqual("it's round", audit.old)
        self.assertEqual("it's a round window", audit.new)

    def test_audit_anonymous_user(self):

        set_local_user(AnonymousUser())

        # test
        self.test_model._meta.fields.update({'description': "it's a round window"})
        self.test_model.save()

        # check
        self.assertEqual(1, Audit.objects.count())
        self.assertIsNone(Audit.objects.all().first().who)

    def test_audit_multiple_change(self):

        # test
        self.test_model._meta.fields.update({
            'name': 'the square window',
            'description': "no wait, it's actually square!",
        })
        self.test_model.save()

        # check
        self.assertEqual(2, Audit.objects.count())
        audits = Audit.objects.all().order_by('field')
        self.assertEqual('description', audits[0].field)
        self.assertEqual("it's round", audits[0].old)
        self.assertEqual("no wait, it's actually square!", audits[0].new)
        self.assertEqual('name', audits[1].field)
        self.assertEqual("the round window", audits[1].old)
        self.assertEqual("the square window", audits[1].new)

    def test_audit_delete(self):

        # test
        self.test_model.delete()

        # check
        self.assertEqual(4, Audit.objects.count())
        audits = Audit.objects.all().order_by('field')
        self.assertEqual('description', audits[0].field)
        self.assertEqual("it's round", audits[0].old)
        self.assertIsNone(audits[0].new)
        self.assertEqual('id', audits[1].field)
        self.assertEqual("1", audits[1].old)
        self.assertIsNone(audits[1].new)
        self.assertEqual('name', audits[2].field)
        self.assertEqual("the round window", audits[2].old)
        self.assertIsNone(audits[2].new)
        self.assertEqual('other', audits[3].field)
        self.assertTrue(audits[3].old)
        self.assertIsNone(audits[3].new)


    def test_audit_compare_override(self):
        """check that any changes to the 'other' field are ignored because of audit_compare()"""

        # test
        self.test_model._meta.fields.update({'other': False})
        self.test_model.save()

        # check
        self.assertEqual(0, Audit.objects.count())

    def tearDown(self):
        clear_local_user()
