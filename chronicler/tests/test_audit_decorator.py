''' Tests for chronicler.decorators.audits '''
from mock import Mock

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from chronicler.models import AuditItem
from chronicler.decorators import audits

from chronicler.tests import TestCase
from chronicler.tests.models import Person, Group

@audits(Person, ['group_set'], 'pk', 'person_pk', 'POST')
def fake_view_post(request):
    pass


@audits(Person, ['group_set'], 'pk', 'person_pk', 'GET')
def fake_view_get(request):
    pass


@audits(Person, ['group_set'], 'pk', 'person_pk')
def fake_view(request, person_pk):
    pass


@audits(Person, ['group_set'], 'pk', 'person_pk', force=True)
def fake_view_force(request, person_pk):
    pass


class TestCreateAuditEntry(TestCase):

    def setUp(self):
        super(TestCreateAuditEntry, self).setUp()
        self.user, _ = User.objects.get_or_create(username='analyte')
        self.content_type = ContentType.objects.get_for_model(Person)
        self.person = Person.objects.create(name='Tester')

    def test_create_post_key(self):
        ''' Test that asserts we can get our object from the POST variables
        when necessary
        '''
        assert not AuditItem.objects.all()
        request = Mock(POST={'person_pk': self.person.pk}, user=self.user)
        fake_view_post(request)
        assert AuditItem.objects.filter(
            content_type=self.content_type,
            object_id=self.person.pk)

    def test_create_get_key(self):
        ''' Test that asserts we can get our object from the GET variables
        when necessary
        '''
        assert not AuditItem.objects.all()
        request = Mock(GET={'person_pk': self.person.pk}, user=self.user)
        fake_view_get(request)
        assert AuditItem.objects.filter(
            content_type=self.content_type,
            object_id=self.person.pk)

    def test_create_simple_view(self):
        ''' Test that proves that we can grab our necessary data to get an
        object from the request path
        '''
        assert not AuditItem.objects.all()
        request = Mock(user=self.user)
        fake_view(request, person_pk=self.person.pk)
        assert AuditItem.objects.filter(
            content_type=self.content_type,
            object_id=self.person.pk)

    def test_prevent_audit_dupes(self):
        ''' Test that asserts that when nothing changes, we don't create
        another audit item with identical changes
        '''
        assert not AuditItem.objects.all()
        request = Mock(user=self.user)
        fake_view(request, person_pk=self.person.pk)
        assert AuditItem.objects.filter(
            content_type=self.content_type,
            object_id=self.person.pk)

        fake_view(request, person_pk=self.person.pk)
        audit_items = AuditItem.objects.filter(
            content_type=self.content_type,
            object_id=self.person.pk)
        self.assertEqual(audit_items.count(), 1)

    def test_audits_force_create_dupes(self):
        ''' Test that asserts that even when we find nothing changes,
        that we will create a dupe if force is set to True
        '''
        assert not AuditItem.objects.all()
        request = Mock(user=self.user)
        fake_view(request, person_pk=self.person.pk)
        assert AuditItem.objects.filter(
            content_type=self.content_type,
            object_id=self.person.pk)

        fake_view_force(request, person_pk=self.person.pk)
        audit_items = AuditItem.objects.filter(
            content_type=self.content_type,
            object_id=self.person.pk)
        self.assertEqual(audit_items.count(), 2)
